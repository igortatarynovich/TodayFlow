"""Stage 4 life_bundle shadow — diagnostics; expand-only; never publishes CE ready."""

from __future__ import annotations

import logging
from typing import Any

from todayflow_backend.core.config import settings
from todayflow_backend.services.character_engine_stage2_shadow_v0 import (
    character_engine_publish_ready_enabled,
)
from todayflow_backend.services.character_engine_stage3_shadow_v0 import (
    maybe_attach_stage3_shadow,
    run_character_engine_stage3_shadow_v0,
)
from todayflow_backend.services.character_engine_stage4_life_v0 import (
    STAGE4_VERSION,
    build_character_engine_life_bundle_v0,
)

logger = logging.getLogger(__name__)


def character_engine_stage4_should_run() -> bool:
    return bool(
        getattr(settings, "character_engine_stage4_shadow", False)
        or getattr(settings, "character_engine_stage4_enabled", False)
        or getattr(settings, "character_engine_profile_consumption", False)
        or getattr(settings, "character_engine_stage5_shadow", False)
        or getattr(settings, "character_engine_stage5_enabled", False)
    )


def run_character_engine_stage4_shadow_v0(
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
    stage3_artifact: dict[str, Any] | None = None,
    locale: str = "ru",
    deterministic_only: bool = False,
) -> dict[str, Any]:
    if not isinstance(stage3_artifact, dict) or not isinstance(stage3_artifact.get("stage3"), dict):
        stage3_artifact = run_character_engine_stage3_shadow_v0(
            profile_fingerprint=profile_fingerprint,
            swiss_chart=swiss_chart,
            numerology=numerology,
            catalog_facts=catalog_facts,
            natal_facts_bridge=natal_facts_bridge,
            capability=capability,
            birth_date=birth_date,
            input_fingerprint=input_fingerprint,
            stage2_artifact=stage2_artifact,
            locale=locale,
            deterministic_only=deterministic_only,
        )

    if not isinstance(stage3_artifact, dict):
        return {
            "artifact_version": STAGE4_VERSION,
            "publish_mode": "diagnostics_only",
            "character_engine_ready_published": False,
            "character_engine_publish_ready_flag": character_engine_publish_ready_enabled(),
            "stage4": None,
            "ok": False,
            "error": "stage3_artifact_missing",
        }

    # Prefer nested stage2 from diagnostics if caller passed it; else rebuild from stage3 run.
    if not isinstance(stage2_artifact, dict):
        # Stage3 runner may have rebuilt stage2 internally without returning it —
        # reconstruct via stage3 prerequisites only when needed below.
        stage2_artifact = None

    # Stage3 artifact doesn't embed stage0/1/2 — need stage2 artifact for packs.
    if not isinstance(stage2_artifact, dict) or not isinstance(stage2_artifact.get("stage2"), dict):
        from todayflow_backend.services.character_engine_stage2_shadow_v0 import (
            run_character_engine_stage2_shadow_v0,
        )

        stage2_artifact = run_character_engine_stage2_shadow_v0(
            profile_fingerprint=profile_fingerprint,
            swiss_chart=swiss_chart,
            numerology=numerology,
            catalog_facts=catalog_facts,
            natal_facts_bridge=natal_facts_bridge,
            capability=capability,
            birth_date=birth_date,
            input_fingerprint=input_fingerprint,
            deterministic_only=deterministic_only,
        )

    facts_pack = stage2_artifact.get("stage0") if isinstance(stage2_artifact.get("stage0"), dict) else {}
    evidence = stage2_artifact.get("stage1") if isinstance(stage2_artifact.get("stage1"), dict) else {}
    identity = stage2_artifact.get("stage2") if isinstance(stage2_artifact.get("stage2"), dict) else {}
    stage3 = stage3_artifact.get("stage3") if isinstance(stage3_artifact.get("stage3"), dict) else {}

    life = build_character_engine_life_bundle_v0(
        facts_pack=facts_pack,
        evidence=evidence,
        identity=identity,
        stage3=stage3,
        locale=locale,
        deterministic_only=deterministic_only,
    )
    validation = life.get("validation") or {}
    ok = life.get("status") in {"grounded", "insufficient_life_bundle"} and bool(
        validation.get("no_core_rewrite", True)
    )

    return {
        "artifact_version": STAGE4_VERSION,
        "publish_mode": "diagnostics_only",
        "character_engine_ready_published": False,
        "character_engine_publish_ready_flag": character_engine_publish_ready_enabled(),
        "identity_thesis": life.get("identity_thesis"),
        "stage2_status": identity.get("status"),
        "stage3_status": stage3.get("status"),
        "stage4": life,
        "ok": ok,
        "note": (
            "Stage 4 life_bundle expands Identity Core + Internal Engine + tension "
            "(prompt profile.character_engine.stage4.v1). Code forbids core rewrite and "
            "career/love/money encyclopedia roots. PUBLISH_READY stays off."
        ),
    }


def maybe_attach_stage4_shadow(
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
    deterministic_only: bool = False,
) -> dict[str, Any]:
    if not character_engine_stage4_should_run():
        return profile_payload
    diagnostics = profile_payload.get("diagnostics")
    if isinstance(diagnostics, dict):
        existing = diagnostics.get("character_engine_stage4")
        if isinstance(existing, dict) and isinstance(existing.get("stage4"), dict):
            return profile_payload
    if character_engine_publish_ready_enabled():
        logger.warning(
            "CHARACTER_ENGINE_PUBLISH_READY set but Stage 4 path remains diagnostics-only until cutover"
        )

    if not isinstance(diagnostics, dict):
        diagnostics = {}

    stage2_artifact = diagnostics.get("character_engine_stage2")
    if not isinstance(stage2_artifact, dict):
        stage2_artifact = None

    stage3_artifact = diagnostics.get("character_engine_stage3")
    if not isinstance(stage3_artifact, dict):
        profile_payload = maybe_attach_stage3_shadow(
            profile_payload,
            profile_fingerprint=profile_fingerprint,
            swiss_chart=swiss_chart,
            numerology=numerology,
            catalog_facts=catalog_facts,
            natal_facts_bridge=natal_facts_bridge,
            capability=capability,
            birth_date=birth_date,
            locale=locale,
            deterministic_only=deterministic_only,
        )
        diagnostics = profile_payload.get("diagnostics")
        if not isinstance(diagnostics, dict):
            diagnostics = {}
        stage3_artifact = diagnostics.get("character_engine_stage3")
        stage2_artifact = diagnostics.get("character_engine_stage2")
    if not isinstance(stage3_artifact, dict):
        stage3_artifact = None
    if not isinstance(stage2_artifact, dict):
        stage2_artifact = None

    try:
        artifact = run_character_engine_stage4_shadow_v0(
            profile_fingerprint=profile_fingerprint,
            swiss_chart=swiss_chart,
            numerology=numerology,
            catalog_facts=catalog_facts,
            natal_facts_bridge=natal_facts_bridge,
            capability=capability,
            birth_date=birth_date,
            stage2_artifact=stage2_artifact,
            stage3_artifact=stage3_artifact,
            locale=locale,
            deterministic_only=deterministic_only,
        )
    except Exception:
        logger.exception("character_engine_stage4_shadow failed")
        artifact = {
            "artifact_version": STAGE4_VERSION,
            "publish_mode": "diagnostics_only",
            "character_engine_ready_published": False,
            "ok": False,
            "error": "stage4_shadow_exception",
        }

    diagnostics = {**diagnostics, "character_engine_stage4": artifact}
    profile_payload["diagnostics"] = diagnostics
    if "character_engine_v1" in profile_payload and not character_engine_publish_ready_enabled():
        ce = profile_payload.get("character_engine_v1")
        if isinstance(ce, dict) and ce.get("status") == "ready":
            if not ce.get("cascade"):
                profile_payload.pop("character_engine_v1", None)
    return profile_payload
