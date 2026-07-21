"""Application-wide settings."""

import os
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    environment: str = "development"
    database_url: str = "postgresql+psycopg://postgres:postgres@postgres:5432/todayflow"
    # Локальный dev / pytest: тот же порт, что в compose (`8081:8081`). В контейнере backend
    # задаётся явно: `ASTRO_SERVICE_URL=http://astro:8081` (имя сервиса в docker-compose).
    astro_service_url: str = "http://127.0.0.1:8081"
    stripe_secret_key: str = "sk_test_placeholder"
    stripe_price_id: str = "price_placeholder"  # Legacy, deprecated
    stripe_webhook_secret: str = "whsec_placeholder"
    payments_mode: str = "mock"  # "mock" or "stripe"
    # Subscription plan price IDs (create these in Stripe Dashboard)
    stripe_lite_plus_price_id: str | None = None
    stripe_full_access_price_id: str | None = None
    stripe_tarot_plus_price_id: str | None = None
    google_client_id: str | None = None
    google_client_secret: str | None = None  # GOOGLE_CLIENT_SECRET — для обмена authorization code (редирект-флоу)
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
    allowed_origins: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ]

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_allowed_origins(cls, value: object) -> object:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value
    openai_api_key: str | None = None  # OPENAI_API_KEY — ключ для OpenAI-совместимого chat API
    # Свой инференс (vLLM, LiteLLM, Azure OpenAI через прокси и т.д.): тот же протокол, другой host.
    openai_base_url: str | None = None  # OPENAI_BASE_URL — базовый URL без завершающего /
    llm_chat_api_key: str | None = None  # LLM_CHAT_API_KEY — если задан, используется вместо OPENAI_API_KEY
    llm_default_model: str = "gpt-4o-mini"  # LLM_DEFAULT_MODEL — chat-модель для всех сервисов кроме Guidance
    guidance_llm_model: str = "gpt-4o-mini"  # GUIDANCE_LLM_MODEL — id модели на вашем endpoint
    guidance_llm_json_object: bool = True  # GUIDANCE_LLM_JSON_OBJECT — False, если провайдер не поддерживает json mode
    gemini_api_key: str | None = None  # GEMINI_API_KEY — Google AI Studio / Gemini API
    gemini_model: str = "gemini-2.5-flash"  # GEMINI_MODEL — chat-модель для LLM_PROVIDER=gemini
    gemini_base_url: str = "https://generativelanguage.googleapis.com/v1beta/openai/"  # GEMINI_BASE_URL
    gemini_max_tokens: int = 4096  # GEMINI_MAX_TOKENS — Gemini 2.5 резервирует budget на thinking
    # Nebius Token Factory (OpenAI-compatible): https://docs.tokenfactory.nebius.com/
    nebius_api_key: str | None = None  # NEBIUS_API_KEY
    nebius_base_url: str = "https://api.tokenfactory.nebius.com/v1/"  # NEBIUS_BASE_URL
    nebius_model: str = "deepseek-ai/DeepSeek-V4-Pro"  # NEBIUS_MODEL — id модели в Token Factory
    llm_provider: str = "openai"  # LLM_PROVIDER — openai | gemini | nebius
    # Hard HTTP timeout for OpenAI-compatible clients (Nebius/OpenAI/Gemini proxy).
    # Prevents Compatibility / Today from hanging the product UI when the provider stalls.
    # Sync/read path: short. Background jobs use llm_background_timeout_seconds.
    llm_http_timeout_seconds: float = 12.0  # LLM_HTTP_TIMEOUT_SECONDS
    llm_background_timeout_seconds: float = 45.0  # LLM_BACKGROUND_TIMEOUT_SECONDS
    # LLM_QUALITY_MODE:
    #   economize — legacy: tight max_tokens, cheap tiers, clipped context (AMLL cost control);
    #   rich — quality-first: full context, multi-step funnels, generous max_tokens, no cheap-tier preference.
    llm_quality_mode: str = "rich"
    # TODAY_NARRATIVE_QUALITY_MODE: strict — post-hoc copy gates + brief-alignment retry;
    # trust_llm — только shape/locale для UI; тон и контекст задаются промптом, без template fallback по «конкретности».
    today_narrative_quality_mode: str = "trust_llm"
    # COMPATIBILITY_CONTENT_V1 — C2 content contracts (guest finished / registered / premium).
    # Off until evaluation set beats legacy truncation + LLM baseline. Do not enable in prod early.
    compatibility_content_v1: bool = False  # COMPATIBILITY_CONTENT_V1=1 to enable

    # Push: optional cron secret for POST /internal/push/run-due (set in production)
    push_dispatch_secret: str | None = None
    # Optional FCM legacy server key for HTTP API (v1 JSON credentials preferred later)
    fcm_server_key: str | None = None

    class Config:
        env_file = ".env"


settings = Settings()
