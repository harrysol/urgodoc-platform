"""Centralized application configuration.

All settings are read from environment variables (or a local ``.env`` file) via
pydantic-settings. ``get_settings()`` is cached so the ``.env`` file is parsed
exactly once per process — both the FastAPI app and the Celery worker import the
same singleton.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # ── Application ───────────────────────────────────────────────────────────
    APP_NAME: str = "UrgoDoc Fashion 3D Try-On API"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: str = "*"

    # ── Database ──────────────────────────────────────────────────────────────
    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/urgodoc"

    # ── Celery / Redis ────────────────────────────────────────────────────────
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"

    # ── Vision LLM (Anthropic Claude) ─────────────────────────────────────────
    ANTHROPIC_API_KEY: str = ""
    VISION_MODEL: str = "claude-opus-4-8"

    # ── Tripo3D ───────────────────────────────────────────────────────────────
    TRIPO3D_API_KEY: str = ""
    TRIPO3D_BASE_URL: str = "https://api.tripo3d.ai/v2/openapi"
    TRIPO3D_POLL_INTERVAL: int = 5      # seconds between status polls
    TRIPO3D_POLL_TIMEOUT: int = 600     # give up after this many seconds

    # ── Headless scraper ──────────────────────────────────────────────────────
    SCRAPER_PROXY_SERVER: str | None = None
    SCRAPER_PROXY_USERNAME: str | None = None
    SCRAPER_PROXY_PASSWORD: str | None = None
    SCRAPER_TIMEOUT_MS: int = 45000
    SCREENSHOT_DIR: str = "/tmp/urgodoc/screenshots"

    # ── Affiliate monetization ────────────────────────────────────────────────
    SKIMLINKS_PUBLISHER_ID: str | None = None
    AMAZON_ASSOCIATE_TAG: str | None = None

    @property
    def cors_origin_list(self) -> list[str]:
        """Parse the comma-separated CORS origins env var into a list."""
        if self.CORS_ORIGINS.strip() == "*":
            return ["*"]
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
