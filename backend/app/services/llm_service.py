import asyncio
import json
import logging
import re
from typing import Type, TypeVar, Optional, Any, Dict
import httpx
from pydantic import BaseModel, ValidationError
from app.core.config import settings

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)

DEFAULT_NUM_CTX = 8192


class LLMService:
    """
    Model abstraction service supporting local Ollama models and external APIs.
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

    async def is_available(self) -> bool:
        """Check if the Ollama instance is reachable and the model exists."""
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

    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
    ) -> str:
        """Generate plain text from the LLM with configured context window."""
        payload: Dict[str, Any] = {
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

        async with httpx.AsyncClient(timeout=httpx.Timeout(self.timeout, connect=15.0)) as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            return data.get("response", "").strip()

    async def generate_json(
        self,
        user_prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.1,
        max_retries: int = 2,
    ) -> Dict[str, Any]:
        """Generate arbitrary JSON object with Ollama format=json and retry resilience."""
        payload: Dict[str, Any] = {
            "model": self.model_name,
            "prompt": user_prompt,
            "stream": False,
            "format": "json",
            "options": {
                "temperature": temperature,
                "num_ctx": self.num_ctx,
            },
        }
        if system_prompt:
            payload["system"] = system_prompt

        last_error = None
        for attempt in range(max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=httpx.Timeout(self.timeout, connect=15.0)) as client:
                    response = await client.post(
                        f"{self.base_url}/api/generate",
                        json=payload,
                    )
                    if response.status_code != 200:
                        logger.warning(
                            f"Ollama generate_json status {response.status_code} on attempt {attempt + 1}: {response.text}"
                        )
                    response.raise_for_status()
                    raw_output = response.json().get("response", "")

                cleaned_json = self._clean_json_string(raw_output)
                return json.loads(cleaned_json)
            except (httpx.HTTPStatusError, httpx.RequestError, json.JSONDecodeError) as exc:
                last_error = exc
                if attempt < max_retries:
                    wait_time = 1.5 * (attempt + 1)
                    logger.info(f"Retrying Ollama generate_json after error: {exc} (backing off {wait_time}s)...")
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
        Employs JSON format mode, 8192 context window, HTTP retry backoff, and iterative self-repair.
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
            payload: Dict[str, Any] = {
                "model": self.model_name,
                "prompt": current_prompt,
                "system": augmented_system_prompt,
                "stream": False,
                "format": "json",
                "options": {
                    "temperature": temperature,
                    "num_ctx": self.num_ctx,
                },
            }

            try:
                async with httpx.AsyncClient(timeout=httpx.Timeout(self.timeout, connect=15.0)) as client:
                    response = await client.post(
                        f"{self.base_url}/api/generate",
                        json=payload,
                    )
                    if response.status_code != 200:
                        logger.warning(
                            f"Ollama structured generation returned status {response.status_code} on attempt {attempt + 1}: {response.text}"
                        )
                    response.raise_for_status()
                    raw_output = response.json().get("response", "")
            except (httpx.HTTPStatusError, httpx.RequestError) as http_err:
                last_error = http_err
                if attempt < max_retries:
                    wait_time = 2.0 * (attempt + 1)
                    logger.warning(
                        f"Ollama HTTP error ({http_err}). Retrying attempt {attempt + 2}/{max_retries + 1} after {wait_time}s..."
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
