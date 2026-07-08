"""Application-wide settings."""

import os
from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    environment: str = "development"
    database_url: str = "postgresql+psycopg://postgres:postgres@postgres:5432/todayflow"
    astro_service_url: str = "http://astro:8081"
    stripe_secret_key: str = "sk_test_placeholder"
    stripe_price_id: str = "price_placeholder"  # Legacy, deprecated
    stripe_webhook_secret: str = "whsec_placeholder"
    payments_mode: str = "mock"  # "mock" or "stripe"
    # Subscription plan price IDs (create these in Stripe Dashboard)
    stripe_lite_plus_price_id: str | None = None
    stripe_full_access_price_id: str | None = None
    stripe_tarot_plus_price_id: str | None = None
    google_client_id: str | None = None
    apple_client_id: str | None = None
    auth_jwt_secret: str = "supersecret"
    auth_jwt_algorithm: str = "HS256"
    frontend_app_url: str = "http://localhost:3000"
    email_from: str = "no-reply@todayflow.app"
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_use_tls: bool = True
    sentry_dsn: str | None = None
    sentry_traces_sample_rate: float = 0.1
    sentry_profiles_sample_rate: float = 0.1
    narrative_model_version: str = "1.0.0"
    content_version: str = "1.0.0"
    i18n_version: str = "1.0.0"
    paragraph_templates_path: Path = Path(os.getenv("CONTENT_DIR", Path(__file__).resolve().parents[4] / "CONTENT")) / "paragraph_templates_v1.jsonl"
    paragraph_templates_meta_path: Path = Path(os.getenv("CONTENT_DIR", Path(__file__).resolve().parents[4] / "CONTENT")) / "paragraph_templates_v1.meta.jsonl"
    allowed_origins: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    openai_api_key: str | None = None  # OPENAI_API_KEY — для генерации прогнозов через LLM

    # Push: optional cron secret for POST /internal/push/run-due (set in production)
    push_dispatch_secret: str | None = None
    # Optional FCM legacy server key for HTTP API (v1 JSON credentials preferred later)
    fcm_server_key: str | None = None

    class Config:
        env_file = ".env"


settings = Settings()
