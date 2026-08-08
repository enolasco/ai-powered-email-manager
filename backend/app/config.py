from pydantic_settings import BaseSettings
from functools import lru_cache
import warnings


class Settings(BaseSettings):
    openai_api_key: str = ""
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8000/auth/callback"
    frontend_url: str = "http://localhost:3000"
    secret_key: str = "changeme-in-production"
    cors_origins: list[str] = ["http://localhost:3000"]

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    settings = Settings()
    if settings.secret_key == "changeme-in-production":
        warnings.warn(
            "SECRET_KEY is set to the insecure default value. "
            "Set a strong random SECRET_KEY in your .env before deploying.",
            stacklevel=2,
        )
    return settings
