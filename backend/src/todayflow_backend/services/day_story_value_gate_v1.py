"""Hard value gate for day_story slots — hide / scrub garbage before UI.

Person-not-system: never ship internal pipeline language, truncated quotes,
address mix, raw topic keys, or near-duplicate claim dumps.
Does NOT score cinematic quality (TL-1 remains blocked).
"""

from __future__ import annotations

import re
from typing import Any

# Internal / design / pipeline language that must never reach the user.
SYSTEM_LEAK_PHRASES_RU: tuple[str, ...] = (
    "слой собран",
    "собран слабо",
    "профиль видит",
    "профиль в основном опирается",
    "общий фон дня",
    "при твоём стиле",
    "при твоем стиле",
    "при вашем стиле",
    "портрет звучит",
    "опоры портрета",
    "узнавание в одном",
    "почему портрет",
    "один узел — не",
    "повтор уже назван",
    "всплывает тема",
    "тема «общий",
    'тема "общий',
    "generation_gate",
    "source_depth",
    "eligibility",
    "block_eligibility",
    "kitchen",
    "пайплайн",
    "мы рассчитали",
    "система видит",
    "система знает",
    "недостаточно данных",
    "нам не хватает",
    # Kitchen day_model / profile baseline catalogs — never ship as day_story Focus copy
    "источники в основном согласованы",
    "мышление и ясные формулировки",
    "инициатива и действие",
    "структура и устойчивость",
    "эмпатия и внутренняя глубина",
)

# Textbook astrology without personal conclusion — for Profile house blurbs.
TEXTBOOK_HOUSE_PHRASES_RU: tuple[str, ...] = (
    "первый дом отвечает",
    "второй дом отвечает",
    "третий дом отвечает",
    "четвёртый дом отвечает",
    "четвертый дом отвечает",
    "пятый дом отвечает",
    "шестой дом отвечает",
    "седьмой дом отвечает",
    "восьмой дом отвечает",
    "девятый дом отвечает",
    "десятый дом отвечает",
    "одиннадцатый дом отвечает",
    "двенадцатый дом отвечает",
    "дом отвечает за",
    "в астрологии этот дом",
)

# Kitchen / ephemeris mechanism — evidence for models, never ambassador prose.
# Canon: EXPLAIN_MEANING_NOT_MECHANISM · TODAY_SCREEN_SCENARIO_V3 §0 (конкретность / no kitchen).
MECHANISM_ASTRO_LEAK_RE = re.compile(
    r"профекц|"
    r"секундарн\w*\s+прогресс|"
    r"прогресс\.?\s*солнц|"
    r"прогресс\.?\s*лун|"
    r"solar\s*return|"
    r"лунарн\w*\s+возврат|"
    r"возврат\s+солнц|"
    r"управител|"
    r"нет\s+(?:времени|ASC)|"
    r"нет\s+времени/места\s+для\s+ASC|"
    r"активных\s+личных\s+транзит|"
    r"firdaria|"
    r"vimshottari|"
    r"\bzr\s*(?:fortune|spirit)\b|"
    r"time[_\s-]?lords|"
    r"\d+(?:[.,]\d+)?°|"  # raw ecliptic degrees
    r"возраст\s+\d+(?:[.,]\d+)?\s*лет|"
    r"дата\s+19\d{2}-\d{2}-\d{2}|"
    r"дата\s+20\d{2}-\d{2}-\d{2}",
    re.IGNORECASE,
)

_RAW_KEY_RE = re.compile(
    r"(?:тема\s+[`«\"']([a-z][a-z0-9_]{1,32})[`»\"'])|(?:`([a-z][a-z0-9_]{2,32})`)",
    re.IGNORECASE,
)
_TRUNCATED_QUOTE_RE = re.compile(r"[«\"'].{8,160}(?:\.\.\.|…)\s*$")
_TY_RE = re.compile(
    r"\b(ты|тебе|тебя|тобой|твой|твоя|твоё|твое|твои|твоих|твоим)\b",
    re.IGNORECASE,
)
_VY_RE = re.compile(
    r"\b(вы|вам|вас|вами|ваш|ваша|ваше|ваши|ваших|вашим)\b",
    re.IGNORECASE,
)

_SLOT_KEYS = (
    "theme",
    "headline_anchor",
    "primary_conflict",
    "events_lead",
    "expect",
    "trap",
    "direction",
    "story",
    "advantage",
    "abstain",
    "today_move",
    "vibe_closing",
    "global_period",
    "development_point",
    "primary_action",
    "evening_closure",
    "symbolic_note",
    "supports_story",
)


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip())


def _low(text: str) -> str:
    return _norm(text).lower().replace("ё", "е")


def is_kitchen_mechanism_prose(text: str | None) -> bool:
    """True when text is ephemeris/kitchen dump, not person-facing meaning."""
    raw = _norm(text or "")
    if not raw:
        return False
    return bool(MECHANISM_ASTRO_LEAK_RE.search(raw))


def find_value_gate_hits(text: str, *, allow_textbook: bool = False) -> list[str]:
    """Return reasons why user-facing text must be hidden."""
    raw = _norm(text)
    if not raw:
        return []
    low = _low(raw)
    hits: list[str] = []

    for phrase in SYSTEM_LEAK_PHRASES_RU:
        if _low(phrase) in low:
            hits.append(f"system_leak:{phrase}")

    if not allow_textbook:
        for phrase in TEXTBOOK_HOUSE_PHRASES_RU:
            if _low(phrase) in low:
                hits.append(f"textbook:{phrase}")

    if is_kitchen_mechanism_prose(raw):
        hits.append("kitchen_mechanism")

    if _RAW_KEY_RE.search(raw):
        hits.append("raw_topic_key")

    if _TRUNCATED_QUOTE_RE.search(raw) or (
        ("…" in raw or "..." in raw) and ("«" in raw or '"' in raw or "'" in raw)
    ):
        # Truncated mid-thought with quote/ellipsis — editorial garbage.
        if re.search(r"[«\"'].{0,40}(?:\.\.\.|…)", raw) or raw.rstrip().endswith(("…", "...")):
            if len(raw) < 220 and ("стиль" in low or "тема" in low or "фон" in low):
                hits.append("truncated_quote")

    if _TY_RE.search(raw) and _VY_RE.search(raw):
        hits.append("address_mix_ty_vy")

    return hits


def _near_duplicate(a: str, b: str) -> bool:
    x, y = _low(a), _low(b)
    if not x or not y:
        return False
    if x == y:
        return True
    if len(x) >= 24 and (x in y or y in x):
        return True
    ax = {w for w in re.findall(r"[a-zа-яё0-9]{4,}", x) }
    by = [w for w in re.findall(r"[a-zа-яё0-9]{4,}", y)]
    if not ax or not by:
        return False
    overlap = sum(1 for w in by if w in ax)
    return overlap >= max(3, int(len(by) * 0.55))


def scrub_user_facing_text(text: str | None, *, allow_textbook: bool = False) -> str | None:
    raw = _norm(text or "")
    if not raw:
        return None
    if find_value_gate_hits(raw, allow_textbook=allow_textbook):
        return None
    return raw


def apply_day_story_value_gate(story: dict[str, Any]) -> dict[str, Any]:
    """Null failing slots and collapse near-duplicate claims into one place."""
    out = dict(story)

    for key in _SLOT_KEYS:
        val = out.get(key)
        if not isinstance(val, str):
            continue
        cleaned = scrub_user_facing_text(val, allow_textbook=True)
        out[key] = cleaned or ""

    for list_key in ("do", "avoid", "vibe_strokes"):
        items = out.get(list_key)
        if not isinstance(items, list):
            continue
        cleaned_items: list[str] = []
        for item in items:
            c = scrub_user_facing_text(str(item or ""), allow_textbook=True)
            if c and not any(_near_duplicate(c, prev) for prev in cleaned_items):
                cleaned_items.append(c)
        out[list_key] = cleaned_items

    thesis = out.get("day_thesis")
    if isinstance(thesis, dict):
        thesis_out = dict(thesis)
        for lab_key in ("label_ru", "label"):
            lab = scrub_user_facing_text(str(thesis_out.get(lab_key) or ""), allow_textbook=True)
            if lab is None:
                thesis_out[lab_key] = ""
            elif lab:
                thesis_out[lab_key] = lab
        out["day_thesis"] = thesis_out

    # day_personal.summary_ru is a kitchen mash (profections/progressions/SR) — never ambassador copy.
    personal = out.get("day_personal")
    if isinstance(personal, dict):
        personal_out = dict(personal)
        summary = scrub_user_facing_text(str(personal_out.get("summary_ru") or ""), allow_textbook=True)
        personal_out["summary_ru"] = summary or ""
        out["day_personal"] = personal_out

    # Plot why_arose must stay meaning — not ruler/degree dumps.
    scenario = out.get("day_scenario")
    if isinstance(scenario, dict):
        scenario_out = dict(scenario)
        conflict = scenario_out.get("conflict")
        if isinstance(conflict, dict):
            conflict_out = dict(conflict)
            for key in ("why_arose", "why_personal", "named_factor"):
                cleaned = scrub_user_facing_text(str(conflict_out.get(key) or ""), allow_textbook=True)
                conflict_out[key] = cleaned or ""
            scenario_out["conflict"] = conflict_out
        out["day_scenario"] = scenario_out

    # One claim → one slot: story must not reprint expect+trap+do soup.
    expect = _norm(str(out.get("expect") or ""))
    trap = _norm(str(out.get("trap") or ""))
    story_body = _norm(str(out.get("story") or ""))
    events = _norm(str(out.get("events_lead") or ""))
    thesis_label = ""
    if isinstance(out.get("day_thesis"), dict):
        thesis_label = _norm(
            str(out["day_thesis"].get("label_ru") or out["day_thesis"].get("label") or "")
        )
    conflict = _norm(str(out.get("primary_conflict") or "")) or thesis_label

    if story_body:
        if expect and _near_duplicate(story_body, expect):
            out["story"] = ""
        elif trap and _near_duplicate(story_body, trap):
            out["story"] = ""
        elif conflict and _near_duplicate(story_body, conflict):
            out["story"] = ""
        elif expect and trap and _low(expect) in _low(story_body) and _low(trap) in _low(story_body):
            # Concat dump of slots — clear; slots remain authoritative.
            out["story"] = ""

    # Prefer events_lead as the prose bridge when story was cleared as a dump.
    if not _norm(str(out.get("story") or "")) and events:
        out["story"] = events

    if events and expect and _near_duplicate(events, expect):
        # Keep events_lead only when it still looks like sky evidence.
        skyish = any(
            token in _low(events)
            for token in (
                "меркури",
                "венери",
                "марс",
                "юпитер",
                "сатурн",
                "уран",
                "нептун",
                "плутон",
                "луна",
                "солнц",
                "аспект",
                "квадрат",
                "тригон",
                "соединен",
                "ретро",
                "ингресс",
            )
        )
        if not skyish:
            out["events_lead"] = ""
            if _near_duplicate(str(out.get("story") or ""), events):
                out["story"] = ""

    if conflict and expect and _near_duplicate(conflict, expect):
        # Thesis label stays; expect must be a scene, not the thesis again.
        out["expect"] = ""

    domains = out.get("domains")
    if isinstance(domains, dict):
        dom_out: dict[str, Any] = {}
        for did, lens in domains.items():
            if not isinstance(lens, dict):
                dom_out[did] = lens
                continue
            lens_out = dict(lens)
            for slot in ("status", "opportunity", "risk", "action"):
                c = scrub_user_facing_text(str(lens_out.get(slot) or ""), allow_textbook=True)
                lens_out[slot] = c or ""
            dom_out[did] = lens_out
        out["domains"] = dom_out

    return out


def day_story_passes_value_gate(story: dict[str, Any]) -> tuple[bool, list[str]]:
    """True when remaining user-facing slots are clean enough to show."""
    hits: list[str] = []
    for key in ("events_lead", "expect", "trap", "today_move", "vibe_closing", "story"):
        val = str(story.get(key) or "").strip()
        if not val:
            continue
        for h in find_value_gate_hits(val, allow_textbook=True):
            hits.append(f"{key}:{h}")
    for list_key in ("do", "avoid"):
        items = story.get(list_key)
        if not isinstance(items, list):
            continue
        for i, item in enumerate(items):
            for h in find_value_gate_hits(str(item or ""), allow_textbook=True):
                hits.append(f"{list_key}[{i}]:{h}")
    # Soft: need at least expect or trap with events OR do — otherwise hollow.
    has_expect = bool(str(story.get("expect") or "").strip())
    has_trap = bool(str(story.get("trap") or story.get("abstain") or "").strip())
    has_move = bool(str(story.get("today_move") or "").strip()) or (
        isinstance(story.get("do"), list) and any(str(x).strip() for x in story["do"])
    )
    if not (has_expect or has_trap) and not has_move:
        hits.append("structure:no_valuable_slots")
    return (len(hits) == 0, hits)
