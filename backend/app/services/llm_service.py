import json
import re
from typing import Type, TypeVar, Optional, Any, Dict
import httpx
from pydantic import BaseModel, ValidationError
from app.core.config import settings

T = TypeVar("T", bound=BaseModel)


class LLMService:
    """
    Model abstraction service supporting local Ollama models and external APIs.
    Guarantees structured Pydantic output validation and resilient JSON parsing.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        model_name: Optional[str] = None,
        timeout: float = 240.0,
    ):
        self.base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")
        self.model_name = model_name or settings.OLLAMA_MODEL
        self.timeout = timeout

    async def is_available(self) -> bool:
        """Check if the Ollama instance is reachable and the model exists."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                if response.status_code != 200:
                    return False
                models = response.json().get("models", [])
                model_names = [m.get("name") for m in models]
                # Check for exact name or prefix (e.g. qwen2.5-coder:7b)
                return any(
                    self.model_name in name or name in self.model_name
                    for name in model_names
                )
        except Exception:
            return False

    def _clean_json_string(self, text: str) -> str:
        """Clean markdown fences, extra whitespace, or commentary around JSON."""
        text = text.strip()
        # Remove ```json ... ``` or ``` ... ```
        fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
        if fence_match:
            text = fence_match.group(1).strip()
        # Sometimes Ollama prepends or appends non-JSON text; find first { and last }
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
        """Generate plain text from the LLM."""
        payload: Dict[str, Any] = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": temperature},
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
        Employs JSON format mode and iterative self-repair if validation fails.
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
                "options": {"temperature": temperature},
            }

            async with httpx.AsyncClient(timeout=httpx.Timeout(self.timeout, connect=15.0)) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                )
                response.raise_for_status()
                raw_output = response.json().get("response", "")

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
