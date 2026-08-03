"""Application-wide settings."""

import os
from pathlib import Path

from typing import Annotated

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

# backend/src/todayflow_backend/core/config.py → repo root TodayFlow/
_REPO_ROOT = Path(__file__).resolve().parents[4]
_ENV_CANDIDATES = (
    _REPO_ROOT / ".env",
    Path.cwd() / ".env",
    Path(".env"),
)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        # Repo-root .env first (Nebius / LLM live there); cwd .env as fallback for local overrides.
        env_file=tuple(str(p) for p in _ENV_CANDIDATES if p.is_file()) or (".env",),
        env_file_encoding="utf-8",
        extra="ignore",
    )

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
    allowed_origins: Annotated[list[str], NoDecode] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ]

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_allowed_origins(cls, value: object) -> object:
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        if isinstance(value, str):
            raw = value.strip()
            if raw.startswith("["):
                import json

                try:
                    parsed = json.loads(raw)
                    if isinstance(parsed, list):
                        return [str(item).strip() for item in parsed if str(item).strip()]
                except json.JSONDecodeError:
                    inner = raw.strip("[]")
                    return [item.strip().strip("'\"") for item in inner.split(",") if item.strip()]
            return [item.strip() for item in raw.split(",") if item.strip()]
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
    nebius_model: str = "moonshotai/Kimi-K2.6"  # NEBIUS_MODEL — Kimi voice trial (K3 TTFT ~160s+ on Nebius)
    # Empty during Kimi primary trial — do not silently hop to DeepSeek and “pass” the test.
    # Set NEBIUS_FALLBACK_MODEL=deepseek-ai/DeepSeek-V4-Pro to re-enable provider failover.
    nebius_fallback_model: str = ""  # NEBIUS_FALLBACK_MODEL
    llm_provider: str = "openai"  # LLM_PROVIDER — openai | gemini | nebius
    # Hard HTTP timeout for OpenAI-compatible clients (Nebius/OpenAI/Gemini proxy).
    # Prevents Compatibility / Today from hanging the product UI when the provider stalls.
    # Sync/read path: short. Background jobs use stream read idle (Kimi) or this wall.
    llm_http_timeout_seconds: float = 12.0  # LLM_HTTP_TIMEOUT_SECONDS
    # Legacy non-stream wall for background. Kimi uses streaming + llm_stream_read_timeout_seconds.
    llm_background_timeout_seconds: float = 180.0  # LLM_BACKGROUND_TIMEOUT_SECONDS
    # Idle between SSE chunks (httpx read). K3 on Nebius needs ≥180s TTFT; K2.6 is sub-second.
    llm_stream_read_timeout_seconds: float = 120.0  # LLM_STREAM_READ_TIMEOUT_SECONDS
    # Stream chat completions for Kimi (and when True). Avoids idle wait until full thinking finishes.
    llm_stream_completions: bool = True  # LLM_STREAM_COMPLETIONS
    # LLM_QUALITY_MODE:
    #   economize — legacy: tight max_tokens, cheap tiers, clipped context (AMLL cost control);
    #   rich — quality-first: full context, multi-step funnels, generous max_tokens, no cheap-tier preference.
    llm_quality_mode: str = "rich"
    # TODAY_NARRATIVE_QUALITY_MODE: strict — post-hoc copy gates + brief-alignment retry;
    # trust_llm — только shape/locale для UI; тон и контекст задаются промптом, без template fallback по «конкретности».
    today_narrative_quality_mode: str = "trust_llm"
    # COMPATIBILITY_CONTENT_V1 — C2 content contracts (guest finished / registered / premium).
    # Off until evaluation set beats legacy truncation + LLM baseline. Do not enable in prod early.
    # Guest+registered content v1.1 (publish_gate in enrichment). Premium not via this flag.
    compatibility_content_v1: bool = False  # COMPATIBILITY_CONTENT_V1=1 to enable

    # Character Engine stages — flags control execution, not Snapshot SoT cutover.
    # CHARACTER_ENGINE_STAGE01_SHADOW=1 — Stage 0–1 diagnostics only (recommended staging).
    # CHARACTER_ENGINE_STAGE01_ENABLED=1 — also runs Stage 0–1; still diagnostics-only.
    # CHARACTER_ENGINE_STAGE2_SHADOW / ENABLED — Stage 2 Identity Core diagnostics-only.
    # CHARACTER_ENGINE_STAGE3_SHADOW / ENABLED — Stage 3 Internal Engine diagnostics-only.
    # CHARACTER_ENGINE_STAGE4_SHADOW / ENABLED — Stage 4 life_bundle diagnostics-only.
    # CHARACTER_ENGINE_STAGE5_SHADOW / ENABLED — Stage 5 Compass+adapters diagnostics-only.
    # CHARACTER_ENGINE_PROFILE_CONSUMPTION=1 — Identity Core (+ Stage 3–5 when on) overwrites
    #   Profile journey slots.
    # CHARACTER_ENGINE_PUBLISH_READY=1 — cutover: character_engine_v1 is portrait SoT;
    #   personality / disclosure funnel / oneshot blocked on publish.
    character_engine_stage01_shadow: bool = False
    character_engine_stage01_enabled: bool = False
    character_engine_stage2_shadow: bool = False
    character_engine_stage2_enabled: bool = False
    character_engine_stage3_shadow: bool = False
    character_engine_stage3_enabled: bool = False
    character_engine_stage4_shadow: bool = False
    character_engine_stage4_enabled: bool = False
    character_engine_stage5_shadow: bool = False
    character_engine_stage5_enabled: bool = False
    character_engine_profile_consumption: bool = False
    character_engine_publish_ready: bool = False

    # Push: optional cron secret for POST /internal/push/run-due (set in production)
    push_dispatch_secret: str | None = None
    # Optional FCM legacy server key for HTTP API (v1 JSON credentials preferred later)
    fcm_server_key: str | None = None


settings = Settings()
