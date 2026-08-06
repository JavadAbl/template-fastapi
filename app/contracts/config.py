from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """Application configuration loaded from environment variables / .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ── Application ──────────────────────────────────────────
    app_name: str = "Modular Monolith API"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"

    # ── Database ─────────────────────────────────────────────
    # Use APP_DATABASE_URL to avoid clash with system DATABASE_URL
    app_database_url: str = "sqlite:///./app.db"

    @property
    def database_url(self) -> str:
        return self.app_database_url

    # ── JWT / Authentication ─────────────────────────────────
    secret_key: str = "super-secret-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # ── Pagination ───────────────────────────────────────────
    default_page_size: int = 20
    max_page_size: int = 100


@lru_cache
def get_settings() -> Settings:
    """Cached settings singleton — inject via DI instead of importing directly."""
    return Settings()
