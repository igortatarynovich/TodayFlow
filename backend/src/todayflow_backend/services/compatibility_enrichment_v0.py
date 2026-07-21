"""Background enrichment runner for Compatibility dynamics (registered tier).

C2 note: registered LLM still uses the legacy pipeline by default.
When COMPATIBILITY_CONTENT_V1=1 *and* offline eval beats baseline, switch
enrichment to compatibility_content_v1.generate_content_v1 (registered tier).
Do not enable that switch casually — see docs/COMPATIBILITY_CONTENT_CANON_V1.md.
"""

from __future__ import annotations

import logging
from typing import Any

from sqlalchemy.orm import Session

from todayflow_backend.data.astrology import lookup_sign_metadata
from todayflow_backend.services.compatibility_access_v0 import (
    apply_paragraph_gate,
    resolve_compat_access_tier,
    shape_product_surface_for_tier,
)
from todayflow_backend.services.compatibility_llm import build_pair_dynamics, build_signals
from todayflow_backend.services.generation_jobs_v0 import (
    claim_job,
    complete_job_if_fresh,
    get_job,
    mark_job_failed,
    run_with_db,
)
from todayflow_backend.services.generation_orchestrator import run_compatibility_dynamics_pipeline
from todayflow_backend.services.sign_compatibility_product import (
    build_sign_product_surface,
    normalize_relationship_context,
)

logger = logging.getLogger("todayflow.compatibility.enrichment")


def _rebuild_template_surface(payload: dict[str, Any], *, locale: str):
    """Rebuild template surface from stored request bits (no LLM)."""
    from todayflow_backend.api.compatibility import (
        _build_static_sign_report,
        _localized_element_relation,
        _localized_rhythm_relation,
    )
    from todayflow_backend.i18n import localized_sign_name

    from_id = str(payload.get("from_sign") or "")
    to_id = str(payload.get("to_sign") or "")
    from_meta = lookup_sign_metadata(from_id) or {}
    to_meta = lookup_sign_metadata(to_id) or {}
    from_display = localized_sign_name(from_id, locale=locale)
    to_display = localized_sign_name(to_id, locale=locale)
    static_payload = _build_static_sign_report(
        from_sign=from_id,
        to_sign=to_id,
        from_name=from_display,
        to_name=to_display,
        from_element=from_meta.get("element", ""),
        to_element=to_meta.get("element", ""),
        from_modality=from_meta.get("modality", ""),
        to_modality=to_meta.get("modality", ""),
        locale=locale,
    )
    ctx_norm = normalize_relationship_context(payload.get("relationship_context"))
    qr = static_payload["quick_reading"]
    el_rel = _localized_element_relation(
        from_meta.get("element", ""), to_meta.get("element", ""), locale=locale
    )
    rh_rel = _localized_rhythm_relation(
        from_meta.get("modality", ""), to_meta.get("modality", ""), locale=locale
    )
    surface = build_sign_product_surface(
        from_sign=from_id,
        to_sign=to_id,
        from_name=from_display,
        to_name=to_display,
        from_element=from_meta.get("element", ""),
        to_element=to_meta.get("element", ""),
        from_modality=from_meta.get("modality", ""),
        to_modality=to_meta.get("modality", ""),
        score=static_payload["score"],
        relationship_context=ctx_norm,
        element_relation=el_rel,
        rhythm_relation=rh_rel,
        strongest=str(qr.get("strongest") or ""),
        friction=str(qr.get("friction") or ""),
        locale=locale,
    )
    return surface, static_payload, from_meta, to_meta, from_display, to_display, el_rel, rh_rel, ctx_norm


def run_compatibility_enrichment_job(job_id: int) -> None:
    def _run(db: Session) -> None:
        job = claim_job(db, job_id)
        if job is None:
            return
        payload = job.request_payload if isinstance(job.request_payload, dict) else {}
        locale = str(payload.get("locale") or "ru")
        fingerprint = job.fingerprint
        try:
            (
                template_surface,
                static_payload,
                from_meta,
                to_meta,
                from_display,
                to_display,
                el_rel,
                rh_rel,
                ctx_norm,
            ) = _rebuild_template_surface(payload, locale=locale)

            from todayflow_backend.i18n import translate

            user1 = str(payload.get("name_1") or "").strip() or translate(
                "compat.label.you", locale=locale
            )
            user2 = str(payload.get("name_2") or "").strip() or translate(
                "compat.label.partner", locale=locale
            )
            pair_dyn = build_pair_dynamics(
                user1_label=user1,
                user2_label=user2,
                from_modality=from_meta.get("modality", ""),
                to_modality=to_meta.get("modality", ""),
                from_element=from_meta.get("element", ""),
                to_element=to_meta.get("element", ""),
                locale=locale,
            )
            signals = build_signals(
                subscores=template_surface.subscores.model_dump(),
                score=int(static_payload["score"]),
            )
            from todayflow_backend.core.llm_openai_compatible import llm_operation

            with llm_operation("background"):
                product_surface, gen_src, _ = run_compatibility_dynamics_pipeline(
                    db,
                    template_surface=template_surface,
                    pair_display=f"{from_display} × {to_display}",
                    user1_label=user1,
                    user2_label=user2,
                    relationship_context=ctx_norm,
                    pair_dynamics=pair_dyn,
                    signals=signals,
                    element_relation=el_rel,
                    rhythm_relation=rh_rel,
                    block_feedback=payload.get("block_feedback")
                    if isinstance(payload.get("block_feedback"), dict)
                    else None,
                    user_id=job.user_id,
                    locale=locale,
                    base_model_layer=None,
                    scenario_tone=None,
                    scenario_context=None,
                    compatibility_learning=None,
                )
            # Re-check freshness before write.
            fresh = get_job(db, job_id)
            if fresh is None or fresh.fingerprint != fingerprint:
                if fresh is not None:
                    fresh.status = "stale"
                    db.add(fresh)
                    db.commit()
                return

            tier = "registered"
            if job.user_id is not None:
                from todayflow_backend.db.models import User

                user = db.query(User).filter(User.id == job.user_id).first()
                if user is not None:
                    tier = resolve_compat_access_tier(user, db)

            shaped, disclosure = shape_product_surface_for_tier(
                product_surface,
                tier=tier,  # type: ignore[arg-type]
                overall_score=int(static_payload["score"]),
                locale=locale,
            )
            free_p, full_p = apply_paragraph_gate(
                list(static_payload.get("paragraphs") or []),
                tier=tier,  # type: ignore[arg-type]
            )
            result = {
                "generation_source": gen_src,
                "score": int(static_payload["score"]),
                "summary": static_payload.get("summary"),
                "quick_reading": static_payload.get("quick_reading"),
                "product_surface": shaped.model_dump(),
                "pair_dynamics": pair_dyn,
                "access_disclosure": disclosure,
                "free_paragraphs": free_p,
                "full_paragraphs": full_p,
                "from_sign": from_meta.get("id") or payload.get("from_sign"),
                "to_sign": to_meta.get("id") or payload.get("to_sign"),
                "from_sign_name": from_display,
                "to_sign_name": to_display,
            }
            if gen_src == "template":
                # Provider returned empty / fell back — treat as failed enrichment so UI can retry.
                mark_job_failed(db, job, "llm_returned_template_fallback")
                # Still store last valid-ish surface for inspection.
                job.result_payload = result
                db.add(job)
                db.commit()
                return

            complete_job_if_fresh(
                db,
                job,
                expected_fingerprint=fingerprint,
                result_payload=result,
            )
        except Exception as exc:
            logger.exception("compatibility_enrichment_failed job_id=%s", job_id)
            job2 = get_job(db, job_id)
            if job2 is not None:
                if job2.attempt_count >= job2.max_attempts:
                    mark_job_failed(db, job2, str(exc)[:500])
                else:
                    job2.status = "enrichment_pending"
                    job2.locked_at = None
                    job2.error_message = str(exc)[:500]
                    db.add(job2)
                    db.commit()

    run_with_db(_run)
