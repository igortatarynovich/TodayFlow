"""Stage 2 Identity Core shadow — diagnostics only; never publishes CE ready."""

from __future__ import annotations

import logging
from typing import Any

from todayflow_backend.core.config import settings
from todayflow_backend.services.character_engine_stage0_facts_v0 import (
    build_character_engine_facts_pack_v0,
)
from todayflow_backend.services.character_engine_stage1_evidence_v0 import (
    build_character_engine_evidence_candidates_v0,
)
from todayflow_backend.services.character_engine_stage2_identity_v0 import (
    STAGE2_VERSION,
    build_character_engine_identity_core_v0,
)

logger = logging.getLogger(__name__)


def character_engine_stage2_should_run() -> bool:
    return bool(
        getattr(settings, "character_engine_stage2_shadow", False)
        or getattr(settings, "character_engine_stage2_enabled", False)
        or getattr(settings, "character_engine_profile_consumption", False)
        or getattr(settings, "character_engine_stage3_shadow", False)
        or getattr(settings, "character_engine_stage3_enabled", False)
        or getattr(settings, "character_engine_stage4_shadow", False)
        or getattr(settings, "character_engine_stage4_enabled", False)
        or getattr(settings, "character_engine_stage5_shadow", False)
        or getattr(settings, "character_engine_stage5_enabled", False)
    )


def character_engine_publish_ready_enabled() -> bool:
    """Future SoT cutover switch — must stay false until Stage 5 + ready validation."""
    return bool(getattr(settings, "character_engine_publish_ready", False))


def run_character_engine_stage2_shadow_v0(
    *,
    profile_fingerprint: str,
    swiss_chart: dict[str, Any] | None = None,
    numerology: dict[str, Any] | None = None,
    catalog_facts: dict[str, Any] | None = None,
    natal_facts_bridge: dict[str, Any] | None = None,
    capability: dict[str, Any] | None = None,
    birth_date: Any = None,
    input_fingerprint: str | None = None,
) -> dict[str, Any]:
    facts_pack = build_character_engine_facts_pack_v0(
        profile_fingerprint=profile_fingerprint,
        swiss_chart=swiss_chart,
        numerology=numerology,
        catalog_facts=catalog_facts,
        natal_facts_bridge=natal_facts_bridge,
        capability=capability,
        birth_date=birth_date,
        input_fingerprint=input_fingerprint,
    )
    evidence = build_character_engine_evidence_candidates_v0(facts_pack)
    identity = build_character_engine_identity_core_v0(facts_pack=facts_pack, evidence=evidence)
    validation = identity.get("validation") or {}
    ok = identity.get("status") in {"grounded", "insufficient_identity_core"} and bool(
        validation.get("no_new_facts", True)
    ) and bool(validation.get("thesis_from_registry", True))

    return {
        "artifact_version": STAGE2_VERSION,
        "publish_mode": "diagnostics_only",
        "character_engine_ready_published": False,
        "character_engine_publish_ready_flag": character_engine_publish_ready_enabled(),
        "stage0": facts_pack,
        "stage1": evidence,
        "stage2": identity,
        "ok": ok,
        "note": (
            "Stage 2 Identity Core is LLM-first (prompt profile.character_engine.stage2.v1). "
            "Code validates structure/provenance only. Stage flags = diagnostics; "
            "CHARACTER_ENGINE_PUBLISH_READY (future) gates SoT cutover."
        ),
    }


def maybe_attach_stage2_shadow(
    profile_payload: dict[str, Any],
    *,
    profile_fingerprint: str,
    swiss_chart: dict[str, Any] | None = None,
    numerology: dict[str, Any] | None = None,
    catalog_facts: dict[str, Any] | None = None,
    natal_facts_bridge: dict[str, Any] | None = None,
    capability: dict[str, Any] | None = None,
    birth_date: Any = None,
) -> dict[str, Any]:
    if not character_engine_stage2_should_run():
        return profile_payload
    diagnostics = profile_payload.get("diagnostics")
    if isinstance(diagnostics, dict):
        existing = diagnostics.get("character_engine_stage2")
        if isinstance(existing, dict) and isinstance(existing.get("stage2"), dict):
            return profile_payload
    # Explicit: publish-ready must never be implied by Stage 2 enabled/shadow.
    if character_engine_publish_ready_enabled():
        logger.warning(
            "CHARACTER_ENGINE_PUBLISH_READY set but Stage 2 path remains diagnostics-only until cutover wiring exists"
        )
    try:
        artifact = run_character_engine_stage2_shadow_v0(
            profile_fingerprint=profile_fingerprint,
            swiss_chart=swiss_chart,
            numerology=numerology,
            catalog_facts=catalog_facts,
            natal_facts_bridge=natal_facts_bridge,
            capability=capability,
            birth_date=birth_date,
        )
    except Exception:
        logger.exception("character_engine_stage2_shadow failed")
        artifact = {
            "artifact_version": STAGE2_VERSION,
            "publish_mode": "diagnostics_only",
            "character_engine_ready_published": False,
            "ok": False,
            "error": "stage2_shadow_exception",
        }
    diagnostics = profile_payload.get("diagnostics")
    if not isinstance(diagnostics, dict):
        diagnostics = {}
    diagnostics = {**diagnostics, "character_engine_stage2": artifact}
    profile_payload["diagnostics"] = diagnostics
    # Never promote Stage 2 alone to CE ready SoT.
    if "character_engine_v1" in profile_payload and not character_engine_publish_ready_enabled():
        ce = profile_payload.get("character_engine_v1")
        if isinstance(ce, dict) and ce.get("status") == "ready":
            # Defensive: Stage 2 shadow must not leave a ready nest without full cascade.
            if not ce.get("cascade"):
                profile_payload.pop("character_engine_v1", None)
    return profile_payload
