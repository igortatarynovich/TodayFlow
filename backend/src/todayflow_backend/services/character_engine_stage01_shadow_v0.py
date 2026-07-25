"""Stage 0–1 shadow runner — build/validate without publishing Character Engine ready."""

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

logger = logging.getLogger(__name__)

SHADOW_ARTIFACT_VERSION = "character_engine_stage01_shadow_v0"


def character_engine_stage01_should_run() -> bool:
    return bool(
        getattr(settings, "character_engine_stage01_shadow", False)
        or getattr(settings, "character_engine_stage01_enabled", False)
    )


def run_character_engine_stage01_shadow_v0(
    *,
    profile_fingerprint: str,
    swiss_chart: dict[str, Any] | None = None,
    numerology: dict[str, Any] | None = None,
    catalog_facts: dict[str, Any] | None = None,
    natal_facts_bridge: dict[str, Any] | None = None,
    capability: dict[str, Any] | None = None,
    birth_date: Any = None,
) -> dict[str, Any]:
    """
    Returns diagnostics artifact only.

    Never sets character_engine_v1.status=ready.
    Never invents identity_core / compass / scenes.
    """
    facts_pack = build_character_engine_facts_pack_v0(
        profile_fingerprint=profile_fingerprint,
        swiss_chart=swiss_chart,
        numerology=numerology,
        catalog_facts=catalog_facts,
        natal_facts_bridge=natal_facts_bridge,
        capability=capability,
        birth_date=birth_date,
    )
    evidence = build_character_engine_evidence_candidates_v0(facts_pack)
    validation = (evidence.get("diagnostics") or {}).get("validation") or {}
    ok = bool(validation.get("all_supporting_facts_exist")) and bool(
        validation.get("all_edges_resolve")
    ) and bool(validation.get("forbidden_kinds_absent"))

    return {
        "artifact_version": SHADOW_ARTIFACT_VERSION,
        "publish_mode": "diagnostics_only",
        "character_engine_ready_published": False,
        "stage0": facts_pack,
        "stage1": evidence,
        "ok": ok,
        "note": "Stage 0–1 shadow only; funnel/personality remain publish SoT until Stage 2–5 cutover.",
    }


def maybe_attach_stage01_shadow(
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
    """Attach diagnostics under profile_payload['diagnostics']['character_engine_stage01']."""
    if not character_engine_stage01_should_run():
        return profile_payload
    try:
        artifact = run_character_engine_stage01_shadow_v0(
            profile_fingerprint=profile_fingerprint,
            swiss_chart=swiss_chart,
            numerology=numerology,
            catalog_facts=catalog_facts,
            natal_facts_bridge=natal_facts_bridge,
            capability=capability,
            birth_date=birth_date,
        )
    except Exception:
        logger.exception("character_engine_stage01_shadow failed")
        artifact = {
            "artifact_version": SHADOW_ARTIFACT_VERSION,
            "publish_mode": "diagnostics_only",
            "character_engine_ready_published": False,
            "ok": False,
            "error": "stage01_shadow_exception",
        }
    diagnostics = profile_payload.get("diagnostics")
    if not isinstance(diagnostics, dict):
        diagnostics = {}
    diagnostics = {**diagnostics, "character_engine_stage01": artifact}
    profile_payload["diagnostics"] = diagnostics
    # Explicit: do not publish CE ready nest from Stage 0–1 alone.
    if "character_engine_v1" in profile_payload:
        # Defensive — Stage 0–1 must not leave a ready CE from this path.
        ce = profile_payload.get("character_engine_v1")
        if isinstance(ce, dict) and ce.get("status") == "ready" and not ce.get("cascade"):
            profile_payload.pop("character_engine_v1", None)
    return profile_payload
