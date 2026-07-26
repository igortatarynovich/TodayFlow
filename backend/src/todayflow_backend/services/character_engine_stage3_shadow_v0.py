"""Stage 3 Internal Engine shadow — diagnostics; expand-only; never publishes CE ready."""

from __future__ import annotations

import logging
from typing import Any

from todayflow_backend.core.config import settings
from todayflow_backend.services.character_engine_stage2_shadow_v0 import (
    character_engine_publish_ready_enabled,
    character_engine_stage2_should_run,
    run_character_engine_stage2_shadow_v0,
)
from todayflow_backend.services.character_engine_stage3_internal_v0 import (
    STAGE3_VERSION,
    build_character_engine_internal_engine_v0,
)

logger = logging.getLogger(__name__)


def character_engine_stage3_should_run() -> bool:
    return bool(
        getattr(settings, "character_engine_stage3_shadow", False)
        or getattr(settings, "character_engine_stage3_enabled", False)
        or getattr(settings, "character_engine_profile_consumption", False)
        or getattr(settings, "character_engine_stage4_shadow", False)
        or getattr(settings, "character_engine_stage4_enabled", False)
        or getattr(settings, "character_engine_stage5_shadow", False)
        or getattr(settings, "character_engine_stage5_enabled", False)
    )


def run_character_engine_stage3_shadow_v0(
    *,
    profile_fingerprint: str,
    swiss_chart: dict[str, Any] | None = None,
    numerology: dict[str, Any] | None = None,
    catalog_facts: dict[str, Any] | None = None,
    natal_facts_bridge: dict[str, Any] | None = None,
    capability: dict[str, Any] | None = None,
    birth_date: Any = None,
    input_fingerprint: str | None = None,
    stage2_artifact: dict[str, Any] | None = None,
    locale: str = "ru",
) -> dict[str, Any]:
    if not isinstance(stage2_artifact, dict) or not isinstance(stage2_artifact.get("stage2"), dict):
        if not character_engine_stage2_should_run() and not character_engine_stage3_should_run():
            stage2_artifact = None
        else:
            stage2_artifact = run_character_engine_stage2_shadow_v0(
                profile_fingerprint=profile_fingerprint,
                swiss_chart=swiss_chart,
                numerology=numerology,
                catalog_facts=catalog_facts,
                natal_facts_bridge=natal_facts_bridge,
                capability=capability,
                birth_date=birth_date,
                input_fingerprint=input_fingerprint,
            )

    if not isinstance(stage2_artifact, dict):
        return {
            "artifact_version": STAGE3_VERSION,
            "publish_mode": "diagnostics_only",
            "character_engine_ready_published": False,
            "character_engine_publish_ready_flag": character_engine_publish_ready_enabled(),
            "stage3": None,
            "ok": False,
            "error": "stage2_artifact_missing",
        }

    facts_pack = stage2_artifact.get("stage0") if isinstance(stage2_artifact.get("stage0"), dict) else {}
    evidence = stage2_artifact.get("stage1") if isinstance(stage2_artifact.get("stage1"), dict) else {}
    identity = stage2_artifact.get("stage2") if isinstance(stage2_artifact.get("stage2"), dict) else {}

    internal = build_character_engine_internal_engine_v0(
        facts_pack=facts_pack,
        evidence=evidence,
        identity=identity,
        locale=locale,
    )
    validation = internal.get("validation") or {}
    ok = internal.get("status") in {"grounded", "insufficient_internal_engine"} and bool(
        validation.get("no_core_rewrite", True)
    )

    return {
        "artifact_version": STAGE3_VERSION,
        "publish_mode": "diagnostics_only",
        "character_engine_ready_published": False,
        "character_engine_publish_ready_flag": character_engine_publish_ready_enabled(),
        "identity_thesis": internal.get("identity_thesis"),
        "stage2_status": identity.get("status"),
        "stage3": internal,
        "ok": ok,
        "note": (
            "Stage 3 Internal Engine expands Identity Core only (prompt "
            "profile.character_engine.stage3.v1). Code forbids core rewrite. "
            "Flags = diagnostics; CHARACTER_ENGINE_PUBLISH_READY stays off."
        ),
    }


def maybe_attach_stage3_shadow(
    profile_payload: dict[str, Any],
    *,
    profile_fingerprint: str,
    swiss_chart: dict[str, Any] | None = None,
    numerology: dict[str, Any] | None = None,
    catalog_facts: dict[str, Any] | None = None,
    natal_facts_bridge: dict[str, Any] | None = None,
    capability: dict[str, Any] | None = None,
    birth_date: Any = None,
    locale: str = "ru",
) -> dict[str, Any]:
    if not character_engine_stage3_should_run():
        return profile_payload
    diagnostics = profile_payload.get("diagnostics")
    if isinstance(diagnostics, dict):
        existing = diagnostics.get("character_engine_stage3")
        if isinstance(existing, dict) and isinstance(existing.get("stage3"), dict):
            return profile_payload
    if character_engine_publish_ready_enabled():
        logger.warning(
            "CHARACTER_ENGINE_PUBLISH_READY set but Stage 3 path remains diagnostics-only until cutover"
        )

    if not isinstance(diagnostics, dict):
        diagnostics = {}
    stage2_artifact = diagnostics.get("character_engine_stage2")
    if not isinstance(stage2_artifact, dict):
        from todayflow_backend.services.character_engine_stage2_shadow_v0 import (
            maybe_attach_stage2_shadow,
        )

        profile_payload = maybe_attach_stage2_shadow(
            profile_payload,
            profile_fingerprint=profile_fingerprint,
            swiss_chart=swiss_chart,
            numerology=numerology,
            catalog_facts=catalog_facts,
            natal_facts_bridge=natal_facts_bridge,
            capability=capability,
            birth_date=birth_date,
        )
        diagnostics = profile_payload.get("diagnostics")
        if not isinstance(diagnostics, dict):
            diagnostics = {}
        stage2_artifact = diagnostics.get("character_engine_stage2")
    if not isinstance(stage2_artifact, dict):
        stage2_artifact = None

    try:
        artifact = run_character_engine_stage3_shadow_v0(
            profile_fingerprint=profile_fingerprint,
            swiss_chart=swiss_chart,
            numerology=numerology,
            catalog_facts=catalog_facts,
            natal_facts_bridge=natal_facts_bridge,
            capability=capability,
            birth_date=birth_date,
            stage2_artifact=stage2_artifact,
            locale=locale,
        )
    except Exception:
        logger.exception("character_engine_stage3_shadow failed")
        artifact = {
            "artifact_version": STAGE3_VERSION,
            "publish_mode": "diagnostics_only",
            "character_engine_ready_published": False,
            "ok": False,
            "error": "stage3_shadow_exception",
        }

    diagnostics = {**diagnostics, "character_engine_stage3": artifact}
    profile_payload["diagnostics"] = diagnostics
    if "character_engine_v1" in profile_payload and not character_engine_publish_ready_enabled():
        ce = profile_payload.get("character_engine_v1")
        if isinstance(ce, dict) and ce.get("status") == "ready":
            if not ce.get("cascade"):
                profile_payload.pop("character_engine_v1", None)
    return profile_payload
