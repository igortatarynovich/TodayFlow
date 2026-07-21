"""Production publish gate — invalid contracts never become user-facing enriched content."""

from __future__ import annotations

from typing import Any, Literal

from todayflow_backend.services.compatibility_content_v1.quality_checks import run_quality_suite

PublishDecision = Literal["publish", "reject_keep_baseline", "reject_retry"]


def evaluate_publish(
    *,
    tier: str,
    content: dict[str, Any] | None,
    known_facts: set[str] | None = None,
    attempt: int = 1,
    max_attempts: int = 2,
) -> dict[str, Any]:
    """Decide whether content may replace baseline in production.

    On reject: caller keeps last baseline and marks job enrichment_failed
    (or schedules one controlled retry if attempt < max_attempts).
    """
    if not content:
        decision: PublishDecision = "reject_retry" if attempt < max_attempts else "reject_keep_baseline"
        return {
            "publish_allowed": False,
            "decision": decision,
            "errors": ["empty_content"],
            "user_facing": None,
        }

    quality = run_quality_suite(tier=tier, content=content, known_facts=known_facts)
    if quality["ok"]:
        return {
            "publish_allowed": True,
            "decision": "publish",
            "errors": [],
            "user_facing": content,
            "quality": quality,
        }

    decision = "reject_retry" if attempt < max_attempts else "reject_keep_baseline"
    return {
        "publish_allowed": False,
        "decision": decision,
        "errors": quality.get("errors") or ["validation_failed"],
        "user_facing": None,
        "quality": quality,
    }
