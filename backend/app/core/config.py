from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Orchestrix"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    DATABASE_URL: str = "postgresql+psycopg://postgres:indiawin@localhost:5432/orchestrix_db"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen2.5-coder:7b"
    FRONTEND_URL: str = "http://localhost:3000"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

    @property
    def cors_origins(self) -> List[str]:
        origins = [self.FRONTEND_URL, "http://localhost:3000", "http://127.0.0.1:3000"]
        return list(dict.fromkeys(origins))


settings = Settings()
