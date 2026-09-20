"""Subscriber deep themes (L3) — practical tips derived from grounded K07 spheres.

PIC: K16 → P6.practical_tips (Explore / Trial+). Child of selected K07 theme.
Does not mint personality meaning. Does not rewrite how/need/risk.

Product lock:
- Tips only for an already grounded K07 sphere matching the selected theme.
- Derived from that sphere's how/need/risk — not identity-thesis / Stage4/5 / generic self-help.
- Max 1–2 tips. Missing K07 row → omit.
- Base life_spheres how/need/risk/turns_* never rewritten.
- Paid/Trial reveal practical_tips for selected themes only.
- Catalog: sex · money · love · work · body
- Caps: lite/Plus=1 · pro=2 · free=0 (CTA only)
- Change cadence: at most one selection change per rolling 7 days.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Literal

from sqlalchemy.orm import Session

from todayflow_backend.db import models as db_models
from todayflow_backend.services.prose_clip_v1 import clip_prose
from todayflow_backend.services.subscription_level import BillingLevel, get_subscription_snapshot

PIC_K = ("K16",)
PIC_F = ("F06",)

PROJECTION_VERSION = "character_engine_deep_themes_v0.3"
_MAX_TIPS = 2
_TIP_NEED = "Один проверяемый шаг в этой зоне: "
_TIP_HOW = "Сделай это так: "
_TIP_RISK = "Не пускай сюда: "

DEEP_THEME_CATALOG: tuple[str, ...] = ("sex", "money", "love", "work", "body")

DEEP_THEME_LABELS_RU: dict[str, str] = {
    "sex": "Секс",
    "money": "Деньги",
    "love": "Любовь",
    "work": "Работа",
    "body": "Тело",
}

CHANGE_WINDOW = timedelta(days=7)

BillingCap = Literal[0, 1, 2]


def _clip_tip(value: Any, limit: int) -> str:
    return clip_prose(" ".join(str(value or "").split()).strip(), limit)


def _same_line(a: str, b: str) -> bool:
    return a.strip().lower() == b.strip().lower()


def _tokens_overlap(left: str, *parts: str) -> bool:
    hay = " ".join(parts).lower()
    tokens = [tok for tok in left.lower().replace("—", " ").replace("–", " ").split() if len(tok) >= 4]
    if not tokens:
        return False
    hits = sum(1 for tok in tokens if tok in hay)
    return hits >= max(2, len(tokens) // 2)


def _k07_sphere_for_theme(
    life_spheres: dict[str, Any] | None,
    theme_id: str,
) -> dict[str, Any] | None:
    if not isinstance(life_spheres, dict):
        return None
    row = life_spheres.get(theme_id)
    if not isinstance(row, dict):
        return None
    how = _clip_tip(row.get("how"), 220)
    need = _clip_tip(row.get("need"), 120)
    if not how and not need:
        return None
    return row


def derive_practical_tips_from_k07_sphere(sphere: dict[str, Any] | None) -> list[str]:
    """1–2 do-lines from grounded K07 how/need/risk. Chrome wrap only — no new meaning."""
    if not isinstance(sphere, dict):
        return []
    how = _clip_tip(sphere.get("how"), 180)
    need = _clip_tip(sphere.get("need"), 120)
    risk = _clip_tip(sphere.get("risk"), 180)
    tips: list[str] = []
    if how:
        tips.append(_clip_tip(f"{_TIP_HOW}{how}", 280))
    if need and not _same_line(need, how) and not (how and need in how):
        if len(tips) < _MAX_TIPS:
            tips.append(_clip_tip(f"{_TIP_NEED}{need}", 220))
    if len(tips) < _MAX_TIPS and risk and not _tokens_overlap(risk, how, need):
        tips.append(_clip_tip(f"{_TIP_RISK}{risk}", 280))
    if not tips and need:
        tips.append(_clip_tip(f"{_TIP_NEED}{need}", 220))
    return tips[:_MAX_TIPS]


def build_tips_by_theme(
    selected: list[str],
    life_spheres: dict[str, Any] | None,
) -> dict[str, dict[str, list[str]]]:
    out: dict[str, dict[str, list[str]]] = {}
    for tid in selected:
        if tid not in DEEP_THEME_CATALOG:
            continue
        sphere = _k07_sphere_for_theme(life_spheres, tid)
        tips = derive_practical_tips_from_k07_sphere(sphere)
        if tips:
            out[tid] = {"tips": tips}
    return out


def theme_cap_for_billing(level: BillingLevel | str) -> int:
    b = (level or "free").strip().lower()
    if b == "pro":
        return 2
    if b in ("lite", "plus"):
        return 1
    return 0


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _parse_ts(raw: Any) -> datetime | None:
    if raw is None:
        return None
    if isinstance(raw, datetime):
        dt = raw
    else:
        s = str(raw).strip()
        if not s:
            return None
        try:
            dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
        except ValueError:
            return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _normalize_selected(raw: Any) -> list[str]:
    if not isinstance(raw, list):
        return []
    out: list[str] = []
    for item in raw:
        tid = str(item or "").strip().lower()
        if tid in DEEP_THEME_CATALOG and tid not in out:
            out.append(tid)
    return out


def read_preference_blob(settings: db_models.UserSettings | None) -> dict[str, Any]:
    if settings is None:
        return {"selected": [], "updated_at": None}
    blob = getattr(settings, "profile_deep_themes", None)
    if not isinstance(blob, dict):
        return {"selected": [], "updated_at": None}
    return {
        "selected": _normalize_selected(blob.get("selected")),
        "updated_at": blob.get("updated_at"),
    }


def next_change_at(updated_at: datetime | None, *, now: datetime | None = None) -> datetime | None:
    if updated_at is None:
        return None
    now = now or _utc_now()
    unlock = updated_at + CHANGE_WINDOW
    return unlock if unlock > now else None


def can_change_selection(
    *,
    previous: list[str],
    previous_updated_at: datetime | None,
    new_selected: list[str],
    now: datetime | None = None,
) -> tuple[bool, str | None]:
    """Allow no-op or first set; block material change inside window."""
    now = now or _utc_now()
    if previous == new_selected:
        return True, None
    if not previous:
        return True, None
    unlock = next_change_at(previous_updated_at, now=now)
    if unlock is not None:
        return False, unlock.isoformat()
    return True, None


def preference_payload(
    *,
    settings: db_models.UserSettings | None,
    billing_level: BillingLevel | str,
    access_allows_reveal: bool,
) -> dict[str, Any]:
    blob = read_preference_blob(settings)
    selected = blob["selected"]
    updated = _parse_ts(blob["updated_at"])
    cap = theme_cap_for_billing(billing_level)
    # Clamp stored selection to current cap for response honesty.
    selected_view = selected[:cap] if cap else []
    unlock = next_change_at(updated)
    return {
        "catalog": [
            {"id": tid, "label": DEEP_THEME_LABELS_RU[tid]} for tid in DEEP_THEME_CATALOG
        ],
        "selected": selected_view,
        "cap": cap,
        "billing_level": billing_level,
        "gated": not access_allows_reveal or cap == 0,
        "change_window_days": CHANGE_WINDOW.days,
        "updated_at": updated.isoformat() if updated else None,
        "next_change_at": unlock.isoformat() if unlock else None,
        "can_change": unlock is None,
    }


def set_preference(
    db: Session,
    settings: db_models.UserSettings,
    *,
    selected: list[str],
    billing_level: BillingLevel | str,
    now: datetime | None = None,
) -> dict[str, Any]:
    now = now or _utc_now()
    cap = theme_cap_for_billing(billing_level)
    if cap <= 0:
        raise PermissionError("deep_themes_require_paid")
    raw_ids = [str(x).strip().lower() for x in (selected or []) if str(x).strip()]
    for tid in raw_ids:
        if tid not in DEEP_THEME_CATALOG:
            raise ValueError(f"deep_themes_unknown:{tid}")
    if len(set(raw_ids)) > cap:
        raise ValueError(f"deep_themes_cap_exceeded:{cap}")
    new_selected = _normalize_selected(raw_ids)[:cap]

    blob = read_preference_blob(settings)
    prev = blob["selected"]
    prev_at = _parse_ts(blob["updated_at"])
    ok, unlock_iso = can_change_selection(
        previous=prev,
        previous_updated_at=prev_at,
        new_selected=new_selected,
        now=now,
    )
    if not ok:
        raise PermissionError(f"deep_themes_change_locked:{unlock_iso}")

    # Only bump timestamp on material change.
    updated_at = now if new_selected != prev else (prev_at or now)
    settings.profile_deep_themes = {
        "selected": new_selected,
        "updated_at": updated_at.isoformat(),
    }
    db.add(settings)
    db.commit()
    db.refresh(settings)
    return preference_payload(
        settings=settings,
        billing_level=billing_level,
        access_allows_reveal=True,
    )


def apply_deep_themes_to_payload(
    payload: dict[str, Any],
    *,
    settings: db_models.UserSettings | None,
    billing_level: BillingLevel | str,
    access_allows_reveal: bool,
    identity_thesis: str | None = None,
) -> dict[str, Any]:
    """Attach character_engine_deep_themes_v0. Never mutates life_spheres."""
    pref = preference_payload(
        settings=settings,
        billing_level=billing_level,
        access_allows_reveal=access_allows_reveal,
    )
    thesis = (identity_thesis or "").strip()
    if not thesis:
        cons = payload.get("character_engine_consumption_v0")
        if isinstance(cons, dict):
            thesis = str(cons.get("identity_thesis") or "").strip()
    selected = list(pref["selected"]) if access_allows_reveal and not pref["gated"] else []
    contract = payload.get("profile_contract_v1")
    spheres_before = None
    life_spheres: dict[str, Any] | None = None
    if isinstance(contract, dict):
        spheres_before = contract.get("life_spheres")
        if isinstance(spheres_before, dict):
            life_spheres = spheres_before
    tips_by_theme = build_tips_by_theme(selected, life_spheres) if selected else {}
    k16_source = "k07_how_need_risk" if tips_by_theme else "omitted_no_grounded_k07"

    payload["character_engine_deep_themes_v0"] = {
        "projection_version": PROJECTION_VERSION,
        "identity_thesis": thesis or None,
        "catalog": pref["catalog"],
        "selected": selected,
        "cap": pref["cap"],
        "gated": pref["gated"],
        "billing_level": pref["billing_level"],
        "change_window_days": pref["change_window_days"],
        "updated_at": pref["updated_at"],
        "next_change_at": pref["next_change_at"],
        "can_change": pref["can_change"],
        "tips_by_theme": tips_by_theme,
        "k16_source": k16_source,
        "note": "L3 practical tips from grounded K07 how/need/risk; base life_spheres remain immutable.",
    }
    # Guard: never rewrite spheres
    if isinstance(contract, dict) and spheres_before is not None:
        contract["life_spheres"] = spheres_before
        payload["profile_contract_v1"] = contract
    return payload


def resolve_identity_thesis_from_payload(payload: dict[str, Any]) -> str | None:
    cons = payload.get("character_engine_consumption_v0")
    if isinstance(cons, dict) and cons.get("identity_thesis"):
        return str(cons["identity_thesis"])
    diagnostics = payload.get("diagnostics")
    if isinstance(diagnostics, dict):
        art = diagnostics.get("character_engine_stage2")
        if isinstance(art, dict):
            stage2 = art.get("stage2") if isinstance(art.get("stage2"), dict) else art
            if isinstance(stage2, dict):
                core = stage2.get("identity_core")
                if isinstance(core, dict) and core.get("thesis_key"):
                    return str(core["thesis_key"])
    return None


def attach_for_user(
    db: Session,
    payload: dict[str, Any],
    *,
    user: db_models.User,
    access_allows_reveal: bool,
) -> dict[str, Any]:
    settings = (
        db.query(db_models.UserSettings)
        .filter(db_models.UserSettings.user_id == user.id)
        .first()
    )
    snap = get_subscription_snapshot(user, db)
    thesis = resolve_identity_thesis_from_payload(payload)
    return apply_deep_themes_to_payload(
        payload,
        settings=settings,
        billing_level=snap.level,
        access_allows_reveal=access_allows_reveal,
        identity_thesis=thesis,
    )
