import json

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    HOST: str = "127.0.0.1"
    PORT: int = 8000
    ENV: str = "development"
    GROQ_API_KEY: str = ""
    CORS_ORIGINS: str = '["*"]'

    @property
    def cors_origins_list(self) -> list[str]:
        try:
            origins = json.loads(self.CORS_ORIGINS)
            if isinstance(origins, list):
                return origins
            return ["*"]
        except Exception:
            return ["*"]


settings = Settings()
