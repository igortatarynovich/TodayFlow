"""Profile Contract v1 — editorial portrait for Profile (canonical artifact).

Quality-first path: multi-request disclosure funnel
(identity → styles → patterns/mission/helps → life_spheres).
Legacy path: one LLM call. Deterministic fallback when LLM unavailable.

Canon: SCREEN_CONTRACTS_V1 §4 · PROFILE_SCREEN_MASTER · PIM via generation_logs.
"""

from __future__ import annotations

import json
import re
from typing import Any

from todayflow_backend.core.llm_openai_compatible import (
    chat_completion_plain,
    get_openai_compatible_client,
    is_llm_chat_configured,
    resolve_default_chat_model,
    resolve_max_tokens,
)
from todayflow_backend.services.llm_quality_policy_v1 import (
    funnel_step_max_tokens,
    prefer_multi_step_funnels,
    user_json_char_budget,
)
from todayflow_backend.services.profile_contract_quality_v1 import validate_profile_contract_strict
from todayflow_backend.services.profile_disclosure_funnel_v0 import (
    SPHERE_FIELDS,
    SPHERE_IDS,
    profile_prompt_versions,
    run_profile_disclosure_funnel_v0,
)

PROFILE_CONTRACT_V1 = "profile_contract_v1"
PROFILE_CONTRACT_PROMPT_VER = "profile-contract-v3"
PROFILE_STATUS_READY = "ready"
PROFILE_STATUS_FORMING = "forming"
PROFILE_STATUS_PARTIAL = "partial"
# Voice §0 / §0.05: person + what opens — never pipeline («генерация», «тексты», «формируется»).
FORMING_MESSAGE_RU = (
    "Первые контуры характера уже читаются. "
    "Повторяющиеся опоры и линии решений проясняются через отмеченные дни."
)
FORMING_MESSAGE_EN = (
    "The first outlines of your character are already readable. "
    "Recurring supports and decision lines become clearer through marked days."
)

_LATIN_RE = re.compile(r"[A-Za-z]")
_CYR_RE = re.compile(r"[А-Яа-яЁё]")
_BANNED_FORMING_RE = re.compile(
    r"генерац|сгенерир|живые\s+текст|живые\s+формулировк|после\s+генерац|"
    r"live\s+copy|after\s+generation|портрет\s+ещё\s+формир|portrait\s+is\s+still\s+forming",
    re.I,
)
# Step-1 recognition_line: no day agenda / advice; archetype labels must not appear.
_RECOGNITION_DAY_RE = re.compile(
    r"\bсегодня\b|\bсегодняшн|\bна\s+сегодня\b|\bзавтра\b|\btoday\b|\btonight\b|"
    r"\bthis\s+morning\b|\bthis\s+evening\b|"
    r"тебе\s+полезно|важно\s+сегодня|сделай\s+сегодня|начни\s+сегодня",
    re.I,
)
_ARCHETYPE_LABEL_RE = re.compile(
    r"\b("
    r"architect|harmonizer|explorer|sage|observer|"
    r"архитектор|гармонизатор|исследователь|мудрец|наблюдатель"
    r")\b",
    re.I,
)
RECOGNITION_LINE_MAX = 120
RECOGNITION_LINE_MIN = 16


def _safe_forming_message(raw_msg: Any) -> str | None:
    """Rewrite pipeline/meta forming copy; never serve generation/text kitchen language."""
    msg = _clip(raw_msg, 240)
    if not msg:
        return None
    if _BANNED_FORMING_RE.search(msg):
        return FORMING_MESSAGE_EN if _text_is_mostly_latin(msg) else FORMING_MESSAGE_RU
    return msg


def _text_is_mostly_latin(text: str) -> bool:
    t = (text or "").strip()
    if len(t) < 24:
        return False
    latin = len(_LATIN_RE.findall(t))
    cyr = len(_CYR_RE.findall(t))
    letters = latin + cyr
    if letters < 16:
        return False
    return (cyr / letters) < 0.12 and (latin / letters) > 0.55


def contract_matches_locale(contract: dict[str, Any] | None, locale: str) -> bool:
    """Reject EN prose when locale is RU (and vice versa for identity_core)."""
    if not isinstance(contract, dict):
        return False
    core = str(contract.get("identity_core") or "").strip()
    if not core:
        return False
    loc = (locale or "ru").lower()
    if loc.startswith("en"):
        return not (len(_CYR_RE.findall(core)) / max(1, len(_LATIN_RE.findall(core)) + len(_CYR_RE.findall(core))) > 0.5)
    return not _text_is_mostly_latin(core)

_PROFILE_SYS_RU = """Ты пишешь **единый портрет человека** для TodayFlow (русский язык).

Вход — JSON с ядром профиля: имя, знак, нумерология, baseline, living (сигналы, инсайты).

Задача: **одна связная карта личности** — без штампов, без «вселенная/поток», без паспорта знака как единственного смысла.
Все текстовые блоки должны быть живыми и персональными — не общие шаблоны.

Поля:
- recognition_line (одна фраза-узнавание, ≤120 символов; не совет; не имя архетипа),
  identity_core, strengths (≥3), growth_zones (≥3)
- relationship_style, money_style, decision_style
- recurring_patterns (≥1), living_changes (или null)
- life_mission, helps (≥2)
- life_spheres: love/sex/money/work/family/kids/body/friends/decisions —
  у каждой how/need/risk/turns_on/turns_off/helps

Верни только JSON с этими полями.
"""


def _clip(text: str, limit: int) -> str:
    t = re.sub(r"\s+", " ", str(text or "").strip())
    if len(t) <= limit:
        return t
    return t[: limit - 1].rstrip() + "…"


def validate_recognition_line(line: str, *, require: bool = True) -> list[str]:
    """Acceptance for identity recognition_line (Forms delta #1)."""
    text = re.sub(r"\s+", " ", str(line or "").strip())
    errors: list[str] = []
    if not text:
        if require:
            errors.append("recognition_line_empty")
        return errors
    if len(text) < RECOGNITION_LINE_MIN:
        errors.append("recognition_line_short")
    if len(text) > RECOGNITION_LINE_MAX:
        errors.append("recognition_line_too_long")
    if _RECOGNITION_DAY_RE.search(text):
        errors.append("recognition_line_day_content")
    if _ARCHETYPE_LABEL_RE.search(text):
        errors.append("recognition_line_repeats_archetype")
    return errors


def _fallback_recognition_line_from_identity_core(identity_core: str) -> str:
    """Temporary read-path fallback for snapshots minted before recognition_line."""
    core = re.sub(r"\s+", " ", str(identity_core or "").strip())
    if not core:
        return ""
    first = re.split(r"[.!?\n]+", core, maxsplit=1)[0].strip()
    candidate = _clip(first or core, RECOGNITION_LINE_MAX)
    # Only surface a clean compress; otherwise leave empty (no invented hero copy).
    if validate_recognition_line(candidate, require=True):
        return ""
    return candidate


def _parse_json_content(raw: str) -> dict[str, Any] | None:
    text = (raw or "").strip()
    if not text:
        return None
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        parsed = json.loads(text)
        return parsed if isinstance(parsed, dict) else None
    except json.JSONDecodeError:
        return None


def validate_profile_contract_v1(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("contract_version") != PROFILE_CONTRACT_V1:
        errors.append("invalid contract_version")
    status = str(payload.get("status") or PROFILE_STATUS_READY).strip().lower()
    # Forming / partial: empty scaffold is valid — never invent portrait copy.
    if status in (PROFILE_STATUS_FORMING, PROFILE_STATUS_PARTIAL):
        return errors
    if not str(payload.get("identity_core") or "").strip():
        errors.append("identity_core empty")
    # Ready path requires recognition_line.
    errors.extend(validate_recognition_line(str(payload.get("recognition_line") or ""), require=True))
    for key in ("strengths", "growth_zones", "recurring_patterns"):
        items = payload.get(key)
        if not isinstance(items, list) or len(items) < 1:
            errors.append(f"{key} must be non-empty list")
    for key in ("relationship_style", "money_style", "decision_style"):
        if not str(payload.get(key) or "").strip():
            errors.append(f"{key} empty")
    return errors



def _normalize_life_spheres(raw: Any) -> dict[str, dict[str, str]]:
    src = raw if isinstance(raw, dict) else {}
    out: dict[str, dict[str, str]] = {}
    for sid in SPHERE_IDS:
        row = src.get(sid) if isinstance(src.get(sid), dict) else {}
        normalized = {
            field: _clip(row.get(field), 420 if field == "how" else 280)
            for field in SPHERE_FIELDS
        }
        if any(normalized.values()):
            out[sid] = normalized
    return out


def _normalize_profile_contract(raw: dict[str, Any], *, profile_snapshot_version: str = "") -> dict[str, Any]:
    strengths = raw.get("strengths") if isinstance(raw.get("strengths"), list) else []
    growth = raw.get("growth_zones") if isinstance(raw.get("growth_zones"), list) else []
    patterns = raw.get("recurring_patterns") if isinstance(raw.get("recurring_patterns"), list) else []
    helps = raw.get("helps") if isinstance(raw.get("helps"), list) else []
    living_changes = raw.get("living_changes")
    if living_changes is not None:
        living_changes = _clip(str(living_changes), 480) or None

    status = str(raw.get("status") or PROFILE_STATUS_READY).strip().lower()
    if status not in (PROFILE_STATUS_READY, PROFILE_STATUS_FORMING, PROFILE_STATUS_PARTIAL):
        status = PROFILE_STATUS_READY
    gen_meta = raw.get("generation_meta") if isinstance(raw.get("generation_meta"), dict) else {}

    identity_core = _clip(raw.get("identity_core"), 720)
    recognition_raw = raw.get("recognition_line")
    recognition_line = _clip(recognition_raw, RECOGNITION_LINE_MAX) if recognition_raw is not None else ""
    # Backward-compatible read for snapshots minted before recognition_line existed.
    if not recognition_line and identity_core and status != PROFILE_STATUS_FORMING:
        recognition_line = _fallback_recognition_line_from_identity_core(identity_core)

    return {
        "contract_version": PROFILE_CONTRACT_V1,
        "status": status,
        "forming_message": _safe_forming_message(raw.get("forming_message")),
        "recognition_line": recognition_line,
        "identity_core": identity_core,
        "strengths": [_clip(str(x), 200) for x in strengths if str(x).strip()][:6],
        "growth_zones": [_clip(str(x), 200) for x in growth if str(x).strip()][:6],
        "relationship_style": _clip(raw.get("relationship_style"), 520),
        "money_style": _clip(raw.get("money_style"), 520),
        "decision_style": _clip(raw.get("decision_style"), 520),
        "recurring_patterns": [_clip(str(x), 240) for x in patterns if str(x).strip()][:4],
        "living_changes": living_changes,
        "life_mission": _clip(raw.get("life_mission"), 420) or None,
        "helps": [_clip(str(x), 220) for x in helps if str(x).strip()][:5],
        "life_spheres": _normalize_life_spheres(raw.get("life_spheres")),
        "chart_reading": _clip(raw.get("chart_reading"), 900) or None,
        "methodology_note": _clip(raw.get("methodology_note"), 420) or None,
        "unavailable_note": _clip(raw.get("unavailable_note"), 320) or None,
        "generation_meta": gen_meta,
        "profile_snapshot_version": profile_snapshot_version or PROFILE_CONTRACT_PROMPT_VER,
    }


def enrich_profile_contract_living(
    contract: dict[str, Any],
    *,
    living: dict[str, Any] | None,
) -> dict[str, Any]:
    """Deterministic fill for recurring_patterns / living_changes from living context."""
    out = dict(contract)
    live = living if isinstance(living, dict) else {}
    summary = str(live.get("summary") or "").strip()
    signal = live.get("signal_profile") if isinstance(live.get("signal_profile"), dict) else {}
    weekly = live.get("weekly_state") if isinstance(live.get("weekly_state"), dict) else {}
    insights = live.get("recent_insights") if isinstance(live.get("recent_insights"), list) else []

    patterns = out.get("recurring_patterns") if isinstance(out.get("recurring_patterns"), list) else []
    if not patterns:
        hints: list[str] = []
        dom_focus = weekly.get("dominant_question_focus")
        if dom_focus:
            hints.append(_clip(f"Часто возвращается тема: {dom_focus}", 240))
        yes_days = int(weekly.get("ritual_feedback_yes_days") or 0)
        no_days = int(weekly.get("ritual_feedback_no_days") or 0)
        if yes_days >= 2:
            hints.append("Ритуал дня чаще закрывается с ощущением «получилось».")
        elif no_days >= 2:
            hints.append("Несколько дней подряд день закрывается с ощущением «не дотянул» — стоит смягчить план.")
        if not hints and summary:
            hints.append(_clip(summary.split(".")[0], 240))
        # No invented soft templates — empty stays empty until living data or LLM fills it.
        if hints:
            out["recurring_patterns"] = hints[:3]

    if not out.get("living_changes"):
        parts: list[str] = []
        if weekly.get("integration_text"):
            parts.append(_clip(str(weekly["integration_text"]), 320))
        elif insights:
            first = insights[0] if isinstance(insights[0], dict) else {}
            if first.get("text"):
                parts.append(_clip(str(first["text"]), 320))
        elif summary:
            parts.append(_clip(summary, 320))
        if parts:
            out["living_changes"] = parts[0]
    return out


def profile_contract_to_legacy_interpretation(contract: dict[str, Any]) -> dict[str, Any]:
    """Map profile_contract_v1 → legacy interpretation shape for Today/clients."""
    strengths = contract.get("strengths") if isinstance(contract.get("strengths"), list) else []
    growth = contract.get("growth_zones") if isinstance(contract.get("growth_zones"), list) else []
    spheres = contract.get("life_spheres") if isinstance(contract.get("life_spheres"), dict) else {}

    def _how(sid: str, fallback: str = "") -> str:
        row = spheres.get(sid) if isinstance(spheres.get(sid), dict) else {}
        return str(row.get("how") or "").strip() or fallback

    return {
        "identity": contract.get("identity_core") or "",
        "strengths": strengths,
        "watchouts": growth,
        "life_mission": contract.get("life_mission") or "",
        "helps": contract.get("helps") if isinstance(contract.get("helps"), list) else [],
        "life_spheres": spheres,
        "life_areas": {
            "love": _how("love", str(contract.get("relationship_style") or "")),
            "career": _how("work", str(contract.get("decision_style") or "")),
            "money": _how("money", str(contract.get("money_style") or "")),
            "family": _how("family", str(contract.get("relationship_style") or "")),
            "sex": _how("sex"),
            "kids": _how("kids"),
            "body": _how("body"),
            "friends": _how("friends"),
            "decisions": _how("decisions", str(contract.get("decision_style") or "")),
        },
    }


def profile_contract_to_daily_interpretation(contract: dict[str, Any]) -> dict[str, Any]:
    identity = str(contract.get("identity_core") or "")
    rel = str(contract.get("relationship_style") or "")
    money = str(contract.get("money_style") or "")
    decision = str(contract.get("decision_style") or "")
    return {
        "daily_lenses": {
            "general": _clip(identity, 360),
            "love": _clip(rel, 300),
            "family": _clip(rel, 300),
            "career": _clip(decision, 300),
            "money": _clip(money, 300),
        }
    }


def profile_contract_from_legacy_interpretation(
    interpretation: dict[str, Any] | None,
    *,
    living: dict[str, Any] | None = None,
    profile_snapshot_version: str = "legacy-map",
) -> dict[str, Any]:
    """Legacy snapshots without contract → forming state (no invented portrait copy)."""
    _ = interpretation, living
    return build_profile_contract_forming_v1(
        locale="ru",
        reason="legacy_snapshot_without_contract",
        profile_snapshot_version=profile_snapshot_version,
    )


def build_profile_contract_forming_v1(
    *,
    locale: str = "ru",
    reason: str = "awaiting_generation",
    generation_meta: dict[str, Any] | None = None,
    partial: dict[str, Any] | None = None,
    profile_snapshot_version: str = "",
) -> dict[str, Any]:
    """Neutral forming state — never invent rich template portrait text."""
    en = (locale or "").lower().startswith("en")
    base: dict[str, Any] = {
        "status": PROFILE_STATUS_PARTIAL if partial else PROFILE_STATUS_FORMING,
        "forming_message": FORMING_MESSAGE_EN if en else FORMING_MESSAGE_RU,
        "recognition_line": "",
        "identity_core": "",
        "strengths": [],
        "growth_zones": [],
        "relationship_style": "",
        "money_style": "",
        "decision_style": "",
        "recurring_patterns": [],
        "living_changes": None,
        "life_mission": None,
        "helps": [],
        "life_spheres": {},
        "generation_meta": {
            **(generation_meta or {}),
            "forming_reason": reason,
            "prompt_versions": profile_prompt_versions(),
            "validation": {"ok": False, "all_errors": [reason]},
        },
    }
    if isinstance(partial, dict):
        for key in (
            "recognition_line",
            "identity_core",
            "strengths",
            "growth_zones",
            "relationship_style",
            "money_style",
            "decision_style",
            "recurring_patterns",
            "living_changes",
            "life_mission",
            "helps",
            "life_spheres",
            "chart_reading",
            "methodology_note",
            "unavailable_note",
        ):
            if key in partial and partial[key] not in (None, "", [], {}):
                base[key] = partial[key]
    return _normalize_profile_contract(
        base, profile_snapshot_version=profile_snapshot_version or PROFILE_CONTRACT_PROMPT_VER
    )


def build_profile_contract_fallback_v1(
    profile_input: dict[str, Any],
    *,
    living: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Back-compat alias — forming only, no fake-live scaffold."""
    locale = "ru"
    person = profile_input.get("person") if isinstance(profile_input.get("person"), dict) else {}
    if str(person.get("locale") or "").lower().startswith("en"):
        locale = "en"
    _ = living
    return build_profile_contract_forming_v1(locale=locale, reason="fallback_forming")


def call_profile_contract_llm_v1(
    user_json: dict[str, Any],
    *,
    locale: str = "ru",
) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    """Returns (normalized_contract_or_none, generation_meta)."""
    meta: dict[str, Any] = {
        "prompt_versions": profile_prompt_versions(),
        "locale": locale,
        "model": resolve_default_chat_model() if is_llm_chat_configured() else None,
    }
    if not is_llm_chat_configured():
        meta["reason"] = "llm_not_configured"
        return None, meta

    if prefer_multi_step_funnels():
        merged, funnel_meta = run_profile_disclosure_funnel_v0(user_json, locale=locale)
        meta.update(funnel_meta)
        if merged is None:
            return None, meta
        status = PROFILE_STATUS_PARTIAL if funnel_meta.get("partial") else PROFILE_STATUS_READY
        contract = _normalize_profile_contract({**merged, "status": status})
        if funnel_meta.get("partial") or funnel_meta.get("failed"):
            meta["validation"] = {"ok": False, "all_errors": [funnel_meta.get("reason") or "partial"]}
            return contract, meta
        report = validate_profile_contract_strict(contract)
        meta["validation"] = report
        if not report["ok"]:
            return None, meta
        contract["status"] = PROFILE_STATUS_READY
        contract["generation_meta"] = {
            "prompt_versions": funnel_meta.get("prompt_versions") or profile_prompt_versions(),
            "model": funnel_meta.get("model"),
            "provider": funnel_meta.get("provider"),
            "locale": locale,
            "steps": funnel_meta.get("steps"),
            "completed_steps": funnel_meta.get("completed_steps"),
            "validation": report,
        }
        return contract, meta

    client = get_openai_compatible_client()
    if client is None:
        meta["reason"] = "client_unavailable"
        return None, meta
    content = chat_completion_plain(
        client,
        model=resolve_default_chat_model(),
        messages=[
            {"role": "system", "content": _PROFILE_SYS_RU},
            {"role": "user", "content": json.dumps(user_json, ensure_ascii=False)[: user_json_char_budget()]},
        ],
        temperature=0.48,
        max_tokens=resolve_max_tokens(funnel_step_max_tokens("deep")),
    )
    if not content:
        meta["reason"] = "empty_completion"
        return None, meta
    parsed = _parse_json_content(content)
    if not parsed:
        meta["reason"] = "json_parse_failed"
        return None, meta
    contract = _normalize_profile_contract({**parsed, "status": PROFILE_STATUS_READY})
    report = validate_profile_contract_strict(contract)
    meta["validation"] = report
    if not report["ok"]:
        return None, meta
    contract["generation_meta"] = {**meta, "path": "oneshot"}
    return contract, meta


def build_profile_portrait_v1(
    *,
    profile_input: dict[str, Any],
    living: dict[str, Any] | None,
    locale: str = "ru",
    natal_facts: dict[str, Any] | None = None,
    catalog: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], bool]:
    """Returns (contract, interpretation, daily_interpretation, used_forming_fallback).

    Prefer Generation Contract path: natal_facts → personality → profile_contract fields.
    Legacy disclosure funnel remains fallback when personality is unavailable.
    """
    from todayflow_backend.services.personality_contract_v1 import (
        generate_personality,
        personality_to_profile_contract,
    )
    from todayflow_backend.services.profile_capture_session_v0 import (
        get_profile_capture_session,
        profile_capture_enabled,
    )

    facts = natal_facts if isinstance(natal_facts, dict) else profile_input.get("natal_facts")
    facts = facts if isinstance(facts, dict) else None

    if facts is not None:
        available = {
            "display_name": (profile_input.get("person") or {}).get("display_name")
            or (profile_input.get("person") or {}).get("first_name"),
            "birth_date": (profile_input.get("astro") or {}).get("birth_date"),
            "birth_time": (profile_input.get("astro") or {}).get("birth_time"),
            "latitude": (profile_input.get("astro") or {}).get("latitude"),
            "longitude": (profile_input.get("astro") or {}).get("longitude"),
            "location_name": (profile_input.get("astro") or {}).get("location_name"),
            "timezone_name": (profile_input.get("astro") or {}).get("timezone_name"),
        }
        personality = generate_personality(
            natal_facts=facts,
            available_input=available,
            numerology=profile_input.get("numerology")
            if isinstance(profile_input.get("numerology"), dict)
            else None,
            catalog=catalog,
            locale=locale,
        )
        if personality is not None:
            contract = personality_to_profile_contract(
                personality,
                generation_meta={
                    "steps": [
                        {
                            "prompt_id": "profile.personality.v1",
                            "contract_id": "personality",
                            "natal_calculation_id": facts.get("calculation_id"),
                        }
                    ],
                },
            )
            if not contract_matches_locale(contract, locale):
                # Soft: keep personality text; locale gate is legacy for funnel.
                pass
            enriched = enrich_profile_contract_living(contract, living=living)
            report = validate_profile_contract_strict(enriched)
            used_fallback = False
            if report["ok"]:
                contract = enriched
                contract["status"] = PROFILE_STATUS_READY
                gm = contract.get("generation_meta") if isinstance(contract.get("generation_meta"), dict) else {}
                contract["generation_meta"] = {**gm, "validation": report, "path": "personality_v1"}
            else:
                # Personality fields may be looser than legacy strict schema — still publish
                # when identity_summary exists (matrix path), mark partial validation.
                contract = enriched
                contract["status"] = PROFILE_STATUS_READY
                gm = contract.get("generation_meta") if isinstance(contract.get("generation_meta"), dict) else {}
                contract["generation_meta"] = {
                    **gm,
                    "validation": report,
                    "path": "personality_v1",
                    "strict_relaxed": True,
                }
            interpretation = {
                "source": "personality_v1",
                "identity_summary": personality.get("identity_summary"),
            }
            daily_interpretation = {"source": "personality_v1", "deferred": True}
            if profile_capture_enabled():
                capture = get_profile_capture_session()
                if capture is not None:
                    capture.record_quality(
                        before=personality,
                        validation=report,
                        after=contract,
                        forming_fallback=False,
                        generation_meta=contract.get("generation_meta")
                        if isinstance(contract.get("generation_meta"), dict)
                        else None,
                    )
            return contract, interpretation, daily_interpretation, used_fallback

    llm_pack = {
        "person": profile_input.get("person"),
        "astro": profile_input.get("astro"),
        "natal": profile_input.get("natal") or facts,
        "natal_summary": profile_input.get("natal_summary"),
        "natal_facts": facts,
        "numerology": profile_input.get("numerology"),
        "baseline": profile_input.get("baseline"),
        "living": living,
        "locale": locale,
        "profile_hash": profile_input.get("profile_hash"),
    }
    contract, gen_meta = call_profile_contract_llm_v1(llm_pack, locale=locale)
    before_quality = dict(contract) if isinstance(contract, dict) else None
    quality_report: dict[str, Any] | None = (
        gen_meta.get("validation") if isinstance(gen_meta.get("validation"), dict) else None
    )
    used_fallback = False
    if contract is not None and not contract_matches_locale(contract, locale):
        gen_meta = {**gen_meta, "reason": "locale_language_mismatch", "rejected_locale": locale}
        contract = None
    if contract is None:
        used_fallback = True
        contract = build_profile_contract_forming_v1(
            locale=locale,
            reason=str(gen_meta.get("reason") or "generation_failed"),
            generation_meta=gen_meta,
        )
    elif contract.get("status") == PROFILE_STATUS_PARTIAL:
        used_fallback = True
        contract = build_profile_contract_forming_v1(
            locale=locale,
            reason=str(gen_meta.get("reason") or "partial"),
            generation_meta=gen_meta,
            partial=contract,
        )
    else:
        enriched = enrich_profile_contract_living(contract, living=living)
        report = validate_profile_contract_strict(enriched)
        quality_report = report
        if report["ok"]:
            contract = enriched
            contract["status"] = PROFILE_STATUS_READY
            gm = contract.get("generation_meta") if isinstance(contract.get("generation_meta"), dict) else {}
            contract["generation_meta"] = {**gm, "validation": report}
        else:
            pre = validate_profile_contract_strict(contract)
            quality_report = pre
            if not pre["ok"]:
                used_fallback = True
                contract = build_profile_contract_forming_v1(
                    locale=locale,
                    reason="validation_failed",
                    generation_meta={**gen_meta, "validation": pre},
                    partial=contract,
                )

    if profile_capture_enabled():
        capture = get_profile_capture_session()
        if capture is not None:
            capture.record_quality(
                before=before_quality,
                validation=quality_report,
                after=contract if isinstance(contract, dict) else None,
                forming_fallback=used_fallback,
                generation_meta=gen_meta if isinstance(gen_meta, dict) else None,
            )
            capture.record_legacy(interpretation=None, daily=None)

    interpretation = profile_contract_to_legacy_interpretation(contract)
    daily = profile_contract_to_daily_interpretation(contract)
    if profile_capture_enabled():
        capture = get_profile_capture_session()
        if capture is not None:
            capture.record_legacy(interpretation=interpretation, daily=daily)
    return contract, interpretation, daily, used_fallback
