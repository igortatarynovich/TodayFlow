"""Admin helpers for managing paragraph templates."""

from sqlalchemy.orm import Session

from todayflow_backend.content import templates
from todayflow_backend.db import models as db_models


def list_paragraphs(db: Session):
    overrides = {ov.paragraph_id: ov for ov in db.query(db_models.ParagraphOverride).all()}
    text_overrides = {
        (txt.paragraph_id, txt.variant_id): txt
        for txt in db.query(db_models.ParagraphTextOverride).all()
    }
    result = []
    for tpl in templates.load_templates():
        override = overrides.get(tpl.paragraph_id)
        result.append(_serialize_template(tpl, override, text_overrides))
    return result


def get_paragraph(db: Session, paragraph_id: str):
    tpl = next((t for t in templates.load_templates() if t.paragraph_id == paragraph_id), None)
    if tpl is None:
        return None
    override = db.query(db_models.ParagraphOverride).filter_by(paragraph_id=paragraph_id).one_or_none()
    text_overrides = {
        (txt.paragraph_id, txt.variant_id): txt
        for txt in db.query(db_models.ParagraphTextOverride).filter_by(paragraph_id=paragraph_id).all()
    }
    return _serialize_template(tpl, override, text_overrides, include_variants=True)


def toggle_paragraph(
    db: Session,
    paragraph_id: str,
    *,
    lite_enabled: bool | None = None,
    full_enabled: bool | None = None,
    actor: str | None = None,
):
    override = db.query(db_models.ParagraphOverride).filter_by(paragraph_id=paragraph_id).one_or_none()
    created = False
    if override is None:
        override = db_models.ParagraphOverride(paragraph_id=paragraph_id)
        db.add(override)
        created = True

    before_state = {"lite_enabled": override.lite_enabled, "full_enabled": override.full_enabled}

    if lite_enabled is not None:
        override.lite_enabled = lite_enabled
    if full_enabled is not None:
        override.full_enabled = full_enabled

    db.commit()

    action = "create_override" if created else "update_override"
    if actor:
        action = f"{actor}:{action}"

    db.add(
        db_models.ParagraphAudit(
            paragraph_id=paragraph_id,
            action=action,
            before_state=before_state,
            after_state={"lite_enabled": override.lite_enabled, "full_enabled": override.full_enabled},
        )
    )
    db.commit()
    return override


def update_variant_text(
    db: Session,
    paragraph_id: str,
    variant_id: str,
    text: str,
    *,
    actor: str | None = None,
):
    cleaned = text
    override = (
        db.query(db_models.ParagraphTextOverride)
        .filter_by(paragraph_id=paragraph_id, variant_id=variant_id)
        .one_or_none()
    )
    before_text = override.text if override else None
    action = None

    if cleaned.strip() == "":
        if override:
            db.delete(override)
            action = "delete_text_override"
            override = None
    else:
        if override is None:
            override = db_models.ParagraphTextOverride(
                paragraph_id=paragraph_id,
                variant_id=variant_id,
                text=cleaned,
            )
            db.add(override)
            action = "create_text_override"
        else:
            override.text = cleaned
            action = "update_text_override"

    db.commit()

    if action:
        if actor:
            action = f"{actor}:{action}"
        db.add(
            db_models.ParagraphAudit(
                paragraph_id=paragraph_id,
                action=action,
                before_state={"text": before_text},
                after_state={"text": override.text if override else None},
            )
        )
        db.commit()

    return override


def list_audit_logs(db: Session, limit: int = 100):
    logs = (
        db.query(db_models.ParagraphAudit)
        .order_by(db_models.ParagraphAudit.created_at.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "paragraph_id": log.paragraph_id,
            "action": log.action,
            "before_state": log.before_state,
            "after_state": log.after_state,
            "created_at": log.created_at.isoformat(),
        }
        for log in logs
    ]


def _serialize_template(tpl, override, text_overrides, include_variants: bool = False):
    data = {
        "paragraph_id": tpl.paragraph_id,
        "section": tpl.section,
        "sub_block": tpl.sub_block,
        "meaning_type": tpl.meaning_type,
        "primary_axes": tpl.primary_axes,
        "secondary_axes": tpl.secondary_axes,
        "modulators": tpl.modulators,
        "lite_allowed": override.lite_enabled if override else tpl.lite_allowed,
        "full_allowed": override.full_enabled if override else True,
    }
    if include_variants:
        variants = []
        for variant in tpl.variants:
            text_override = text_overrides.get((tpl.paragraph_id, variant.variant_id))
            variants.append(
                {
                    "variant_id": variant.variant_id,
                    "text": text_override.text if text_override else variant.text,
                    "base_text": variant.text,
                    "override_text": text_override.text if text_override else None,
                }
            )
        data["variants"] = variants
    else:
        data["has_text_override"] = any(
            (tpl.paragraph_id, variant.variant_id) in text_overrides for variant in tpl.variants
        )
    return data
