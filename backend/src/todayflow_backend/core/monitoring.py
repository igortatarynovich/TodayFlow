"""Monitoring and observability configuration."""

from __future__ import annotations

import logging
from typing import Any

from todayflow_backend.core.config import settings

logger = logging.getLogger(__name__)

try:
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    from sentry_sdk.integrations.logging import LoggingIntegration
    from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
except Exception:  # pragma: no cover - optional dependency
    sentry_sdk = None
    FastApiIntegration = None
    LoggingIntegration = None
    SqlalchemyIntegration = None


def _filter_sensitive_data(event: dict[str, Any], hint: dict[str, Any]) -> dict[str, Any] | None:
    """Redact sensitive request data before sending events."""
    request_data = event.get("request", {})
    headers = request_data.get("headers", {})
    for key in ("authorization", "cookie", "x-api-key"):
        headers.pop(key, None)

    cookies = request_data.get("cookies", {})
    for key in ("session", "token", "auth"):
        cookies.pop(key, None)
    return event


def init_monitoring() -> None:
    """Initialize Sentry if configured."""
    if not settings.sentry_dsn:
        logger.info("Sentry disabled: SENTRY_DSN is not set")
        return

    if sentry_sdk is None:
        logger.warning("Sentry DSN is set, but sentry-sdk is not installed")
        return

    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        environment=settings.environment,
        release=settings.narrative_model_version,
        traces_sample_rate=settings.sentry_traces_sample_rate,
        profiles_sample_rate=settings.sentry_profiles_sample_rate,
        integrations=[
            FastApiIntegration(),
            SqlalchemyIntegration(),
            LoggingIntegration(level=logging.INFO, event_level=logging.ERROR),
        ],
        before_send=_filter_sensitive_data,
    )
    logger.info("Sentry monitoring initialized")


def capture_exception(error: Exception, context: dict[str, Any] | None = None) -> None:
    """Capture exception with optional context."""
    logger.error("Exception captured: %s", error, exc_info=True, extra=context or {})
    if sentry_sdk is not None:
        with sentry_sdk.push_scope() as scope:
            for key, value in (context or {}).items():
                scope.set_extra(key, value)
            sentry_sdk.capture_exception(error)


def capture_message(message: str, level: str = "info", context: dict[str, Any] | None = None) -> None:
    """Capture message in logs and Sentry."""
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.log(log_level, message, extra=context or {})
    if sentry_sdk is not None:
        with sentry_sdk.push_scope() as scope:
            for key, value in (context or {}).items():
                scope.set_extra(key, value)
            sentry_sdk.capture_message(message, level=level)


def set_user(user_id: str, email: str | None = None, **kwargs: Any) -> None:
    """Set user context in Sentry."""
    logger.info("User context set: %s", user_id, extra={"user_id": user_id, "email": email, **kwargs})
    if sentry_sdk is not None:
        sentry_sdk.set_user({"id": user_id, "email": email, **kwargs})


def clear_user() -> None:
    """Clear user context in Sentry."""
    logger.info("User context cleared")
    if sentry_sdk is not None:
        sentry_sdk.set_user(None)
