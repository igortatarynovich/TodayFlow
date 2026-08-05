"""Subscriber deep themes (L3) — selectable practical tips over immutable base spheres.

Product lock:
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
from todayflow_backend.services.subscription_level import BillingLevel, get_subscription_snapshot

PROJECTION_VERSION = "character_engine_deep_themes_v0.2"

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

# Deterministic tip banks: identity_thesis → theme → direct person tips (not abstract coaching).
_TIPS: dict[str, dict[str, list[str]]] = {
    "builds_through_autonomy": {
        "sex": [
            "Перед сексом скажи вслух одно: «медленнее», «глубже», «не трогай пока», «держи взгляд» — без оправданий.",
            "Если тело зажимается: ляг на спину, партнёр — язык/пальцы медленно по клитору или головке 3–5 минут без цели «довести».",
            "Поза, которая часто заходит при дистанции: ты сверху или сбоку — контроль темпа у тебя, партнёр не давит.",
            "Для оргазма с головой «в схеме»: выключи разговор на 10 минут, дыши животом, проси только касания — без анализа «как мы».",
        ],
        "money": [
            "Зафиксируй один денежный приоритет на месяц и один счёт/конверт под него — без идеальной таблицы.",
            "Сделай один видимый шаг: перевод, отказ от траты, договорённость о цене — вслух или письмом.",
            "Где копишь схемы вместо выбора — выпиши ответ одной строкой и сделай его.",
            "Назови одну трату или условие, которое не торгуешь — и держи его.",
        ],
        "love": [
            "В одном разговоре назови границу: что оставляешь своим, что открываешь — коротко.",
            "Дай один понятный жест близости без требования идеальных условий.",
            "Если ждёшь полной ясности вместо шага — сделай маленький контактный шаг сейчас.",
            "Спроси партнёра одно конкретное «как тебе лучше» — и услышь ответ без защиты.",
        ],
        "work": [
            "Выбери один рабочий фронт и доведи до проверяемого «сделано» — до новых идей.",
            "Сформулируй роль одним предложением: влияние без потери твоего метода.",
            "Отложи чужую повестку на час — сначала свой контур задачи.",
            "Покажи один результат видимо — не только внутреннюю схему.",
        ],
        "body": [
            "Сон, еда или прогулка — один жест заботы о теле без героизма.",
            "Поставь себе сигнал «хватит» раньше чужой нормы — заметь его в теле.",
            "Согласуй нагрузку и паузу в одном блоке дня.",
            "Перед решением проверь тело одной фразой: напряжение, голод, усталость.",
        ],
    },
    "builds_through_air_mind": {
        "sex": [
            "Выключи «разбор полётов» в постели: 10 минут только тело — рот, руки, без вопросов «а что ты имел в виду».",
            "Для возбуждения головы: партнёр говорит грязно и конкретно (что делает), ты отвечаешь одним словом — не лекцией.",
            "Куни/минет без цели: ритм медленный → быстрее → пауза; спроси только «так?» — не строй схему оргазма.",
            "Поза лицом к лицу + глазной контакт ломает уход в анализ лучше, чем «эффективные» позиции спиной.",
        ],
        "money": [
            "Один денежный шаг вместо ещё одной таблицы: перевод, счёт, отказ.",
            "Запиши, куда уходит контроль вместо выбора — одной строкой — и сделай выбор.",
            "Отдели нужду от статуса: что реально держит опору.",
            "Закрой один мелкий денежный хвост до конца дня.",
        ],
        "love": [
            "Скажи одно честное «мне важно» без схемы всей связи.",
            "Сделай жест тепла без условия «сразу идеально».",
            "Заметь отсрочку разговором и замени её одним контактом.",
            "Спроси и выслушай один ответ без защиты.",
        ],
        "work": [
            "Закрой один конкретный рабочий результат — видимый.",
            "Убери одну лишнюю задачу из списка — освободи фокус.",
            "Попроси ясность рамки там, где хаос чужой повестки.",
            "Покажи прогресс коротко — без перфекционизма схемы.",
        ],
        "body": [
            "Один жест заботы о теле: сон, еда, движение.",
            "Ложись / ешь / двигайся по своему сигналу, не по чужой норме.",
            "Заметь усталость раньше срыва — сократи нагрузку на шаг.",
            "Короткая пауза без экрана — телу, не голове.",
        ],
    },
}

_GENERIC_TIPS: dict[str, list[str]] = {
    "sex": [
        "Перед близостью назови одно желание или границу — коротко, без оправданий.",
        "3–5 минут только касания (язык/пальцы) без цели «довести» — спроси «так?» один раз.",
        "Попробуй позу, где тебе легче дышать и вести темп (сверху или сбоку).",
        "Если голова мешает телу — тишина 10 минут, только дыхание и касания.",
    ],
    "money": [
        "Один денежный шаг на эту неделю — видимый.",
        "Куда уходит контроль вместо выбора — одной строкой, потом действие.",
        "Отдели нужду от статуса: что реально держит опору.",
        "Закрой один мелкий денежный хвост.",
    ],
    "love": [
        "Одно честное «мне важно» в близкой связи.",
        "Один жест тепла без условия взаимности «сразу идеально».",
        "Заметь паттерн отсрочки и назови его себе.",
        "Спроси и выслушай один ответ без защиты.",
    ],
    "work": [
        "Один конкретный рабочий результат — доведи до «сделано».",
        "Убери одну лишнюю задачу — освободи фокус.",
        "Попроси ясность рамки там, где хаос чужой повестки.",
        "Покажи прогресс коротко — без перфекционизма.",
    ],
    "body": [
        "Один жест заботы о теле: сон, еда, движение.",
        "Свой сигнал тела важнее чужой нормы нагрузки.",
        "Усталость раньше срыва — сократи нагрузку на шаг.",
        "Короткая пауза без экрана.",
    ],
}


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


def tips_for_theme(identity_thesis: str, theme_id: str) -> list[str]:
    pack = _TIPS.get(identity_thesis) or {}
    tips = pack.get(theme_id) or _GENERIC_TIPS.get(theme_id) or []
    return [str(t).strip() for t in tips if str(t).strip()][:4]


def build_tips_by_theme(
    identity_thesis: str,
    selected: list[str],
) -> dict[str, dict[str, list[str]]]:
    out: dict[str, dict[str, list[str]]] = {}
    for tid in selected:
        tips = tips_for_theme(identity_thesis, tid)
        if tips:
            out[tid] = {"tips": tips}
    return out


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
    tips_by_theme = build_tips_by_theme(thesis, selected) if selected else {}
    # Snapshot base spheres fingerprint for tests / honesty — do not write back.
    contract = payload.get("profile_contract_v1")
    spheres_before = None
    if isinstance(contract, dict):
        spheres_before = contract.get("life_spheres")

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
        "note": "L3 practical tips only; base life_spheres remain immutable.",
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
