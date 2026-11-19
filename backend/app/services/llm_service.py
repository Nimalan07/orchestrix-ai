import asyncio
import json
import logging
import re
from typing import Type, TypeVar, Optional, Any, Dict, List
import httpx
from pydantic import BaseModel, ValidationError
from app.core.config import settings

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)

DEFAULT_NUM_CTX = 8192
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"


class LLMService:
    """
    Model abstraction service supporting both cloud providers (GroqCloud OpenAI-compatible API)
    and local offline Ollama models.
    Guarantees structured Pydantic output validation, resilient JSON parsing,
    configured context window allocation, and exponential backoff retry.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        model_name: Optional[str] = None,
        timeout: float = 240.0,
        num_ctx: int = DEFAULT_NUM_CTX,
    ):
        self.base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")
        self.model_name = model_name or settings.OLLAMA_MODEL
        self.timeout = timeout
        self.num_ctx = num_ctx

    @property
    def is_groq(self) -> bool:
        """Check if GroqCloud API key is configured."""
        return bool(settings.GROQ_API_KEY and settings.GROQ_API_KEY.strip())

    @property
    def active_model(self) -> str:
        """Return the active model name based on provider."""
        return settings.GROQ_MODEL if self.is_groq else self.model_name

    async def is_available(self) -> bool:
        """Check if the configured LLM engine is reachable."""
        if self.is_groq:
            return True

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                if response.status_code != 200:
                    return False
                models = response.json().get("models", [])
                model_names = [m.get("name") for m in models]
                return any(
                    self.model_name in name or name in self.model_name
                    for name in model_names
                )
        except Exception:
            return False

    def _clean_json_string(self, text: str) -> str:
        """Clean markdown fences, extra whitespace, or commentary around JSON."""
        text = text.strip()
        fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
        if fence_match:
            text = fence_match.group(1).strip()
        start_idx = text.find("{")
        end_idx = text.rfind("}")
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            text = text[start_idx : end_idx + 1]
        return text

    async def _call_provider(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.1,
        json_mode: bool = False,
    ) -> str:
        """Internal unified dispatcher routing between GroqCloud and Ollama."""
        if self.is_groq:
            headers = {
                "Authorization": f"Bearer {settings.GROQ_API_KEY.strip()}",
                "Content-Type": "application/json",
            }
            messages: List[Dict[str, str]] = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            payload: Dict[str, Any] = {
                "model": settings.GROQ_MODEL,
                "messages": messages,
                "temperature": temperature,
            }
            if json_mode:
                payload["response_format"] = {"type": "json_object"}

            async with httpx.AsyncClient(timeout=httpx.Timeout(self.timeout, connect=15.0)) as client:
                response = await client.post(
                    GROQ_API_URL,
                    json=payload,
                    headers=headers,
                )
                if response.status_code != 200:
                    logger.warning(
                        f"Groq API returned status {response.status_code}: {response.text}"
                    )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"].strip()

        else:
            # Local Ollama dispatcher
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_ctx": self.num_ctx,
                },
            }
            if system_prompt:
                payload["system"] = system_prompt
            if json_mode:
                payload["format"] = "json"

            async with httpx.AsyncClient(timeout=httpx.Timeout(self.timeout, connect=15.0)) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                )
                if response.status_code != 200:
                    logger.warning(
                        f"Ollama returned status {response.status_code}: {response.text}"
                    )
                response.raise_for_status()
                data = response.json()
                return data.get("response", "").strip()

    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
    ) -> str:
        """Generate plain text from the active LLM engine."""
        return await self._call_provider(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            json_mode=False,
        )

    async def generate_json(
        self,
        user_prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.1,
        max_retries: int = 2,
    ) -> Dict[str, Any]:
        """Generate arbitrary JSON object with retry resilience."""
        last_error = None
        for attempt in range(max_retries + 1):
            try:
                raw_output = await self._call_provider(
                    prompt=user_prompt,
                    system_prompt=system_prompt,
                    temperature=temperature,
                    json_mode=True,
                )
                cleaned_json = self._clean_json_string(raw_output)
                return json.loads(cleaned_json)
            except (httpx.HTTPStatusError, httpx.RequestError, json.JSONDecodeError) as exc:
                last_error = exc
                if attempt < max_retries:
                    wait_time = 1.5 * (attempt + 1)
                    logger.info(
                        f"Retrying LLM generation after error ({exc}) in {wait_time}s..."
                    )
                    await asyncio.sleep(wait_time)
                else:
                    raise exc

        raise ValueError(f"Failed to generate JSON after {max_retries + 1} attempts. Last error: {last_error}")

    async def generate_structured(
        self,
        prompt: str,
        schema: Type[T],
        system_prompt: Optional[str] = None,
        temperature: float = 0.1,
        max_retries: int = 2,
    ) -> T:
        """
        Generate structured data strictly validated against a Pydantic schema.
        Employs JSON format mode, HTTP retry backoff, and iterative self-repair.
        """
        schema_json = json.dumps(schema.model_json_schema(), indent=2)
        augmented_system_prompt = (
            (system_prompt or "You are an expert AI software architect.")
            + "\n\nYou MUST respond with ONLY a valid JSON object matching this JSON Schema:\n"
            + schema_json
            + "\nDo NOT wrap your JSON in any conversational text. Return raw JSON only."
        )

        last_error = None
        current_prompt = prompt

        for attempt in range(max_retries + 1):
            try:
                raw_output = await self._call_provider(
                    prompt=current_prompt,
                    system_prompt=augmented_system_prompt,
                    temperature=temperature,
                    json_mode=True,
                )
            except (httpx.HTTPStatusError, httpx.RequestError) as http_err:
                last_error = http_err
                if attempt < max_retries:
                    wait_time = 2.0 * (attempt + 1)
                    logger.warning(
                        f"LLM HTTP error ({http_err}). Retrying attempt {attempt + 2}/{max_retries + 1} after {wait_time}s..."
                    )
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    raise http_err

            cleaned_json = self._clean_json_string(raw_output)

            try:
                parsed_dict = json.loads(cleaned_json)
                validated_model = schema.model_validate(parsed_dict)
                return validated_model
            except (json.JSONDecodeError, ValidationError) as e:
                last_error = e
                # Self-repair prompt for next iteration
                current_prompt = (
                    f"{prompt}\n\n"
                    f"CRITICAL ERROR in previous attempt: {str(e)}\n"
                    f"Previous malformed output:\n{cleaned_json}\n"
                    f"Please correct the JSON and strictly adhere to the schema without missing required fields."
                )

        raise ValueError(
            f"Failed to generate valid structured data after {max_retries + 1} attempts. Last error: {last_error}"
        )


llm_service = LLMService()
