"""Stage 5 assembly shadow — Compass + adapters; diagnostics only; never PUBLISH_READY."""

from __future__ import annotations

import logging
from typing import Any

from todayflow_backend.core.config import settings
from todayflow_backend.services.character_engine_stage2_shadow_v0 import (
    character_engine_publish_ready_enabled,
)
from todayflow_backend.services.character_engine_stage4_shadow_v0 import (
    maybe_attach_stage4_shadow,
)
from todayflow_backend.services.character_engine_stage5_assembly_v0 import (
    STAGE5_VERSION,
    build_character_engine_assembly_v0,
)

logger = logging.getLogger(__name__)


def character_engine_stage5_should_run() -> bool:
    return bool(
        getattr(settings, "character_engine_stage5_shadow", False)
        or getattr(settings, "character_engine_stage5_enabled", False)
        or getattr(settings, "character_engine_profile_consumption", False)
    )


def run_character_engine_stage5_shadow_v0(
    *,
    profile_fingerprint: str,
    swiss_chart: dict[str, Any] | None = None,
    numerology: dict[str, Any] | None = None,
    catalog_facts: dict[str, Any] | None = None,
    natal_facts_bridge: dict[str, Any] | None = None,
    capability: dict[str, Any] | None = None,
    birth_date: Any = None,
    stage2_artifact: dict[str, Any] | None = None,
    stage3_artifact: dict[str, Any] | None = None,
    stage4_artifact: dict[str, Any] | None = None,
    locale: str = "ru",
) -> dict[str, Any]:
    if not isinstance(stage4_artifact, dict) or not isinstance(stage4_artifact.get("stage4"), dict):
        # Rebuild via stage4 runner (pulls 2–3 as needed).
        from todayflow_backend.services.character_engine_stage4_shadow_v0 import (
            run_character_engine_stage4_shadow_v0,
        )

        stage4_artifact = run_character_engine_stage4_shadow_v0(
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
        )

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
        )

    if not isinstance(stage3_artifact, dict) or not isinstance(stage3_artifact.get("stage3"), dict):
        from todayflow_backend.services.character_engine_stage3_shadow_v0 import (
            run_character_engine_stage3_shadow_v0,
        )

        stage3_artifact = run_character_engine_stage3_shadow_v0(
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

    identity = stage2_artifact.get("stage2") if isinstance(stage2_artifact, dict) else {}
    stage3 = stage3_artifact.get("stage3") if isinstance(stage3_artifact, dict) else {}
    stage4 = stage4_artifact.get("stage4") if isinstance(stage4_artifact, dict) else {}

    assembly = build_character_engine_assembly_v0(
        identity=identity if isinstance(identity, dict) else {},
        stage3=stage3 if isinstance(stage3, dict) else {},
        stage4=stage4 if isinstance(stage4, dict) else {},
    )
    validation = assembly.get("validation") or {}
    ok = assembly.get("status") in {"grounded", "insufficient_assembly"} and bool(
        validation.get("deterministic", True)
    )

    return {
        "artifact_version": STAGE5_VERSION,
        "publish_mode": "diagnostics_only",
        "character_engine_ready_published": False,
        "character_engine_publish_ready_flag": character_engine_publish_ready_enabled(),
        "identity_thesis": assembly.get("identity_thesis"),
        "stage2_status": (identity or {}).get("status") if isinstance(identity, dict) else None,
        "stage3_status": (stage3 or {}).get("status") if isinstance(stage3, dict) else None,
        "stage4_status": (stage4 or {}).get("status") if isinstance(stage4, dict) else None,
        "stage5": assembly,
        "ok": ok,
        "note": (
            "Stage 5 deterministic Compass + legacy adapters from Stage 2–4. "
            "No LLM. PUBLISH_READY stays off — does not write character_engine_v1 ready."
        ),
    }


def maybe_attach_stage5_shadow(
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
    if not character_engine_stage5_should_run():
        return profile_payload
    diagnostics = profile_payload.get("diagnostics")
    if isinstance(diagnostics, dict):
        existing = diagnostics.get("character_engine_stage5")
        if isinstance(existing, dict) and isinstance(existing.get("stage5"), dict):
            return profile_payload
    if character_engine_publish_ready_enabled():
        logger.warning(
            "CHARACTER_ENGINE_PUBLISH_READY set but Stage 5 path remains diagnostics-only until cutover wiring"
        )

    if not isinstance(diagnostics, dict):
        diagnostics = {}

    stage2_artifact = diagnostics.get("character_engine_stage2")
    stage3_artifact = diagnostics.get("character_engine_stage3")
    stage4_artifact = diagnostics.get("character_engine_stage4")
    if not isinstance(stage4_artifact, dict):
        profile_payload = maybe_attach_stage4_shadow(
            profile_payload,
            profile_fingerprint=profile_fingerprint,
            swiss_chart=swiss_chart,
            numerology=numerology,
            catalog_facts=catalog_facts,
            natal_facts_bridge=natal_facts_bridge,
            capability=capability,
            birth_date=birth_date,
            locale=locale,
        )
        diagnostics = profile_payload.get("diagnostics")
        if not isinstance(diagnostics, dict):
            diagnostics = {}
        stage2_artifact = diagnostics.get("character_engine_stage2")
        stage3_artifact = diagnostics.get("character_engine_stage3")
        stage4_artifact = diagnostics.get("character_engine_stage4")

    try:
        artifact = run_character_engine_stage5_shadow_v0(
            profile_fingerprint=profile_fingerprint,
            swiss_chart=swiss_chart,
            numerology=numerology,
            catalog_facts=catalog_facts,
            natal_facts_bridge=natal_facts_bridge,
            capability=capability,
            birth_date=birth_date,
            stage2_artifact=stage2_artifact if isinstance(stage2_artifact, dict) else None,
            stage3_artifact=stage3_artifact if isinstance(stage3_artifact, dict) else None,
            stage4_artifact=stage4_artifact if isinstance(stage4_artifact, dict) else None,
            locale=locale,
        )
    except Exception:
        logger.exception("character_engine_stage5_shadow failed")
        artifact = {
            "artifact_version": STAGE5_VERSION,
            "publish_mode": "diagnostics_only",
            "character_engine_ready_published": False,
            "ok": False,
            "error": "stage5_shadow_exception",
        }

    diagnostics = {**diagnostics, "character_engine_stage5": artifact}
    profile_payload["diagnostics"] = diagnostics
    if "character_engine_v1" in profile_payload and not character_engine_publish_ready_enabled():
        ce = profile_payload.get("character_engine_v1")
        if isinstance(ce, dict) and ce.get("status") == "ready":
            if not ce.get("cascade"):
                profile_payload.pop("character_engine_v1", None)
    return profile_payload
