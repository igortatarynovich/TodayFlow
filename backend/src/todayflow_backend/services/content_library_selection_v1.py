"""Deterministic selection of Content Items from the canonical practice library + catalog adapter.

No LLM. No randomness. This module provides two things:

1. `select_content_item(query)` — runtime bridge between Meaning and the Content Library.
   Returns the best active Content Item for a product need.

2. `all_content_library_practices()`, `get_content_library_practice_by_id()` — catalog adapter
   that exposes active, accepted Content Library items through the `GET /practices` hub.

Canon: docs/practices/CONTENT_LIBRARY_SELECTION_V1.md · PRACTICE_LIBRARY_FILL_V1.md
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any

from todayflow_backend.data.practice_state_cycle_catalog_v1 import (
    STATE_CYCLE_FORMAT_IDS,
    STATE_CYCLE_NEED_IDS,
    rank_practices_for_need,
)
from todayflow_backend.data.reference_machine_loader import DATA_ROOT

_PRACTICE_REF = DATA_ROOT / "reference" / "practice"
LIBRARY_PATH = _PRACTICE_REF / "content_library_v1.json"
TECHNIQUE_PATH = _PRACTICE_REF / "technique_canon_v1.json"
CONTENT_LIBRARY_PATH = LIBRARY_PATH
TECHNIQUE_CANON_PATH = TECHNIQUE_PATH

LOCALE_FALLBACK = "en"


# --- selection dataclasses -----------------------------------------------------


@dataclass(frozen=True)
class NeedQuery:
    """Product-side need used to retrieve a Content Item.

    This shape is intentionally close to the `retrieval` group of a Content Item:
    purpose + direction are required; input_state/context are soft filters.
    Meaning never emits `item_id` or `technique_id`; those are resolved here.
    """

    purpose: str
    direction: str
    input_state: list[str] = field(default_factory=list)
    context: list[str] = field(default_factory=list)
    duration: int | None = None
    duration_unit: str = "minutes"
    energy_effect: str | None = None
    content_class: str | None = None
    item_type: str | None = None
    locale: str = "ru"


@dataclass(frozen=True)
class ContentSelection:
    """Result of a deterministic content library lookup."""

    item_id: str | None
    content_class: str | None
    item_type: str | None
    title: str
    body: str
    outcome_label: str
    duration: int | None
    duration_unit: str | None
    context: list[str]
    delivery: list[str]
    technique_id: str | None
    reason: str
    matched: bool


# --- canonical loaders --------------------------------------------------------


def load_content_library(path: Path | None = None) -> dict[str, Any]:
    """Load the canonical content library JSON."""
    with open(path or LIBRARY_PATH, encoding="utf-8") as f:
        return json.load(f)


def load_technique_canon(path: Path | None = None) -> dict[str, Any]:
    """Load the canonical technique registry JSON."""
    with open(path or TECHNIQUE_PATH, encoding="utf-8") as f:
        return json.load(f)


# --- selection helpers --------------------------------------------------------


def _accepted_technique_ids(techniques: dict[str, Any]) -> set[str]:
    return {
        str(t["technique_id"])
        for t in techniques.get("techniques", [])
        if t.get("status") == "accepted"
    }


def _as_set(value: Any) -> set[str]:
    if isinstance(value, list):
        return {str(v) for v in value if v is not None}
    return set()


def _is_active(item: dict[str, Any], accepted: set[str]) -> bool:
    """Active items are publishable; if they carry a technique_id it must be accepted."""
    identity = item.get("identity", {})
    if identity.get("status") != "active":
        return False
    tid = identity.get("technique_id")
    if tid is not None and str(tid) not in accepted:
        return False
    return True


def _matches_hard_tags(item: dict[str, Any], query: NeedQuery) -> tuple[bool, dict[str, Any]]:
    """Check required retrieval tags: purpose, direction, optional class/type."""
    identity = item.get("identity", {})
    retrieval = item.get("retrieval", {})
    purposes = retrieval.get("purpose") or []
    directions = retrieval.get("direction") or []
    if query.purpose not in purposes:
        return False, {}
    if query.direction not in directions:
        return False, {}
    if query.content_class is not None and query.content_class != identity.get("content_class"):
        return False, {}
    if query.item_type is not None and query.item_type != identity.get("type"):
        return False, {}
    return True, retrieval


def _score(
    item: dict[str, Any], query: NeedQuery, retrieval: dict[str, Any]
) -> tuple[int, int, int, int, str]:
    """Return a stable sort key for a candidate. Lower tuple = better match."""
    identity = item.get("identity", {})
    item_id = str(identity.get("item_id") or "")

    query_states = _as_set(query.input_state)
    item_states = _as_set(retrieval.get("input_state"))
    state_overlap = len(query_states & item_states)

    query_contexts = _as_set(query.context)
    item_contexts = _as_set(retrieval.get("context"))
    context_overlap = len(query_contexts & item_contexts)

    energy_match = int(
        bool(query.energy_effect and retrieval.get("energy_effect") == query.energy_effect)
    )

    item_duration = retrieval.get("duration")
    if query.duration is not None and isinstance(item_duration, int):
        duration_penalty = abs(query.duration - item_duration)
    elif isinstance(item_duration, int):
        # No requested duration: prefer shorter session items.
        duration_penalty = item_duration
    else:
        # Discipline items (duration_days) and malformed rows sort last.
        duration_penalty = 9999

    # Sort descending by overlap, ascending by penalty; final tie-break by item_id
    # for deterministic, reproducible ordering.
    return (-state_overlap, -context_overlap, -energy_match, duration_penalty, item_id)


def select_content_item(
    query: NeedQuery,
    *,
    library: dict[str, Any] | None = None,
    technique_canon: dict[str, Any] | None = None,
) -> ContentSelection:
    """Return the best active Content Item for a product need.

    The function is fully deterministic: same query + same library always yields the
    same item_id. If nothing matches, `matched` is False and the reason explains why.
    """
    if library is None:
        library = load_content_library()
    if technique_canon is None:
        technique_canon = load_technique_canon()

    accepted = _accepted_technique_ids(technique_canon)
    candidates: list[tuple[tuple[int, int, int, int, str], dict[str, Any], dict[str, Any]]] = []
    for item in library.get("items", []):
        ok, retrieval = _matches_hard_tags(item, query)
        if not ok:
            continue
        if not _is_active(item, accepted):
            continue
        candidates.append((_score(item, query, retrieval), item, retrieval))

    if not candidates:
        reason = (
            f"No active accepted item matches purpose={query.purpose} "
            f"direction={query.direction}"
        )
        if query.content_class:
            reason += f" content_class={query.content_class}"
        if query.item_type:
            reason += f" type={query.item_type}"
        return ContentSelection(
            item_id=None,
            content_class=None,
            item_type=None,
            title="",
            body="",
            outcome_label="",
            duration=None,
            duration_unit=None,
            context=[],
            delivery=[],
            technique_id=None,
            reason=reason,
            matched=False,
        )

    candidates.sort(key=lambda x: x[0])
    _, item, retrieval = candidates[0]
    identity = item.get("identity", {})
    payload = item.get("payload", {})
    locales = payload.get("locales", {})
    locale_payload = locales.get(query.locale) or locales.get("ru") or {}
    title = str(locale_payload.get("title") or "")
    body = str(locale_payload.get("body") or "")
    outcome_label = (
        payload.get("presentation", {})
        .get("outcome_label", {})
        .get(query.locale)
        or payload.get("presentation", {})
        .get("outcome_label", {})
        .get("ru")
        or ""
    )

    reason = f"Selected {identity.get('item_id')}: purpose={query.purpose} direction={query.direction}"
    if query.input_state:
        overlap = len(_as_set(query.input_state) & _as_set(retrieval.get("input_state")))
        reason += f" input_state_overlap={overlap}"
    if query.context:
        overlap = len(_as_set(query.context) & _as_set(retrieval.get("context")))
        reason += f" context_overlap={overlap}"
    if query.duration is not None and retrieval.get("duration") is not None:
        reason += f" duration={retrieval['duration']}"

    return ContentSelection(
        item_id=str(identity.get("item_id") or ""),
        content_class=identity.get("content_class"),
        item_type=identity.get("type"),
        title=title,
        body=body,
        outcome_label=str(outcome_label),
        duration=retrieval.get("duration"),
        duration_unit=retrieval.get("duration_unit"),
        context=list(_as_set(retrieval.get("context"))),
        delivery=list(_as_set(retrieval.get("delivery"))),
        technique_id=identity.get("technique_id"),
        reason=reason,
        matched=True,
    )


# --- public taxonomy mapping --------------------------------------------------


INTENSITY_TO_DIFFICULTY = {
    "low": "beginner",
    "medium": "intermediate",
    "high": "advanced",
}

PURPOSE_TO_NEED: dict[str, str] = {
    "calm": "calm",
    "sleep": "sleep",
    "rest": "sleep",
    "recovery": "recover",
    "body": "body",
    "focus": "focus",
    "clarity": "focus",
    "confidence": "focus",
    "motivation": "focus",
    "decision_making": "focus",
    "emotional_awareness": "understand",
    "self_connection": "understand",
    "creativity": "understand",
    "transition": "understand",
    "detachment": "calm",
    "presence": "calm",
    "simplicity": "calm",
    "reset": "recover",
    "self_control": "focus",
    "connection": "understand",
    "consistency": "focus",
    "habit_change": "focus",
    "energy": "recover",
    "discipline": "focus",
}

DIRECTION_TO_NEED: dict[str, str] = {
    "downregulate": "calm",
    "release": "calm",
    "stabilize": "focus",
    "reflect": "understand",
    "focus": "focus",
    "activate": "recover",
    "open": "understand",
    "connect": "understand",
    "recover": "recover",
    "prepare": "focus",
}

INPUT_STATE_TO_NEED: dict[str, str] = {
    "scattered": "focus",
    "stuck": "understand",
    "overstimulated": "calm",
    "disconnected": "understand",
    "uncertain": "understand",
    "restless": "calm",
    "low_energy": "recover",
    "tense": "body",
    "emotionally_heavy": "understand",
    "balanced": "calm",
}

CLASS_TO_CATEGORY: dict[str, str] = {
    "affirmation": "affirmation",
    "meditation": "meditation",
    "practice": "meditation",
    "discipline": "focus",
}

TYPE_TO_CATEGORY: dict[str, str] = {
    "extended_exhale": "breathing",
    "paced_breathing": "breathing",
    "physiological_sigh": "breathing",
    "box_breathing": "breathing",
    "energizing_breath": "breathing",
    "breath_awareness": "breathing",
    "digital_pause": "breathing",
    "mobility": "focus",
    "stretching": "focus",
    "mindful_movement": "focus",
    "body_scan": "meditation",
    "sensory_grounding": "meditation",
    "grounding": "meditation",
    "open_awareness": "meditation",
    "letting_go": "meditation",
    "mindfulness": "meditation",
    "relaxation": "meditation",
    "sleep": "meditation",
    "sleep_discipline": "meditation",
    "prompted_reflection": "reflection",
    "journaling": "reflection",
    "free_writing": "reflection",
    "reflection_meditation": "reflection",
    "self_check_in": "reflection",
    "gratitude": "gratitude",
    "creative_prompt": "reflection",
    "priority_setting": "reflection",
    "connection_action": "meditation",
    "morning_ritual": "meditation",
    "evening_ritual": "meditation",
    "transition_ritual": "meditation",
    "micro_action": "meditation",
    "capability": "affirmation",
    "agency": "affirmation",
    "relationship": "affirmation",
    "self_trust": "affirmation",
    "body_release": "meditation",
    "routine_commitment": "meditation",
    "attention_discipline": "meditation",
    "consistency_challenge": "meditation",
    "reduction": "meditation",
    "digital_limit": "meditation",
    "consumption_limit": "meditation",
    "intention_setting": "meditation",
    "environment_reset": "meditation",
    "abstinence": "meditation",
    "focused_attention": "meditation",
    "acceptance": "meditation",
}

CLASS_TO_FORMAT: dict[str, str] = {
    "affirmation": "affirmation",
    "meditation": "meditation",
    "practice": "meditation",
    "discipline": "meditation",
}

TYPE_TO_FORMAT: dict[str, str] = {
    "extended_exhale": "breath",
    "paced_breathing": "breath",
    "physiological_sigh": "breath",
    "box_breathing": "breath",
    "energizing_breath": "breath",
    "breath_awareness": "breath",
    "digital_pause": "breath",
    "mobility": "stretch",
    "stretching": "stretch",
    "mindful_movement": "stretch",
    "body_scan": "meditation",
    "sensory_grounding": "meditation",
    "grounding": "meditation",
    "open_awareness": "meditation",
    "letting_go": "meditation",
    "mindfulness": "meditation",
    "relaxation": "meditation",
    "sleep": "sleep",
    "sleep_discipline": "sleep",
    "prompted_reflection": "reflection",
    "journaling": "reflection",
    "free_writing": "reflection",
    "reflection_meditation": "reflection",
    "self_check_in": "reflection",
    "gratitude": "reflection",
    "creative_prompt": "reflection",
    "priority_setting": "reflection",
    "connection_action": "meditation",
    "morning_ritual": "meditation",
    "evening_ritual": "sleep",
    "transition_ritual": "meditation",
    "micro_action": "meditation",
    "capability": "affirmation",
    "agency": "affirmation",
    "relationship": "affirmation",
    "self_trust": "affirmation",
    "body_release": "meditation",
    "routine_commitment": "meditation",
    "attention_discipline": "meditation",
    "consistency_challenge": "meditation",
    "reduction": "meditation",
    "digital_limit": "meditation",
    "consumption_limit": "meditation",
    "intention_setting": "meditation",
    "environment_reset": "meditation",
    "abstinence": "meditation",
    "focused_attention": "meditation",
    "acceptance": "meditation",
}


# --- catalog loaders ----------------------------------------------------------


@lru_cache(maxsize=1)
def _load_content_library() -> dict[str, Any]:
    with CONTENT_LIBRARY_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def _load_technique_canon() -> dict[str, Any]:
    with TECHNIQUE_CANON_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def _accepted_technique_ids_cached() -> frozenset[str]:
    canon = _load_technique_canon()
    return frozenset(
        t["technique_id"]
        for t in canon.get("techniques", [])
        if t.get("status") == "accepted"
    )


# --- mapping helpers ----------------------------------------------------------


def _resolve_locale_text(locale: str, node: dict[str, Any]) -> dict[str, str]:
    """Return the best available locale text dict."""
    if locale in node:
        return node[locale]
    if LOCALE_FALLBACK in node:
        return node[LOCALE_FALLBACK]
    if node:
        return next(iter(node.values()))
    return {"title": "", "body": ""}


def _derive_need_ids(retrieval: dict[str, Any]) -> list[str]:
    """Map content-library retrieval tags to public STATE_CYCLE_NEED_IDS."""
    need_ids: list[str] = []
    seen: set[str] = set()

    for purpose in retrieval.get("purpose", []):
        need = PURPOSE_TO_NEED.get(purpose)
        if need and need not in seen:
            need_ids.append(need)
            seen.add(need)

    for direction in retrieval.get("direction", []):
        need = DIRECTION_TO_NEED.get(direction)
        if need and need not in seen:
            need_ids.append(need)
            seen.add(need)

    for state in retrieval.get("input_state", []):
        need = INPUT_STATE_TO_NEED.get(state)
        if need and need not in seen:
            need_ids.append(need)
            seen.add(need)

    # If no mapping produced a valid public need, default to "focus" so the item
    # is still visible in the hub and filterable.
    if not need_ids:
        need_ids = ["focus"]

    return need_ids


def _derive_tags(retrieval: dict[str, Any]) -> list[str]:
    """Build a small, stable tag list from retrieval dimensions."""
    tags: list[str] = []
    tags.extend(str(x) for x in retrieval.get("purpose", []))
    tags.extend(str(x) for x in retrieval.get("direction", []))
    tags.extend(str(x) for x in retrieval.get("input_state", []))
    return tags[:6]


def _content_item_to_practice(item: dict[str, Any], locale: str) -> dict[str, Any] | None:
    """Map a single content-library item to the PracticeResponse dict shape."""
    identity = item.get("identity", {})
    if identity.get("status") != "active":
        return None

    technique_id = identity.get("technique_id")
    if not technique_id or technique_id not in _accepted_technique_ids_cached():
        return None

    retrieval = item.get("retrieval", {})
    payload = item.get("payload", {})

    text = _resolve_locale_text(locale, payload.get("locales", {}))
    title = (text.get("title") or "").strip() or identity.get("item_id", "")
    body = (text.get("body") or "").strip()

    # Multi-line bodies carry an intro line followed by step lines. The hub
    # card / detail subtitle shows the intro; the detail page lists steps.
    body_lines = [line.strip() for line in body.splitlines() if line.strip()]
    description = body_lines[0] if body_lines else ""
    steps = body_lines[1:] if len(body_lines) > 1 else ([body] if body else [])

    presentation = payload.get("presentation", {})
    outcome_node = presentation.get("outcome_label", {})
    outcome_label = (outcome_node.get(locale) or outcome_node.get(LOCALE_FALLBACK) or "").strip() or None

    content_class = identity.get("content_class", "practice")
    item_type = identity.get("type", "")

    category = TYPE_TO_CATEGORY.get(item_type) or CLASS_TO_CATEGORY.get(content_class, "meditation")
    fmt = TYPE_TO_FORMAT.get(item_type) or CLASS_TO_FORMAT.get(content_class, "meditation")
    if fmt not in STATE_CYCLE_FORMAT_IDS:
        fmt = "meditation"

    need_ids = _derive_need_ids(retrieval)

    duration = None
    if retrieval.get("duration_unit") == "minutes":
        try:
            duration = int(retrieval["duration"])
        except (TypeError, ValueError):
            duration = None

    intensity = retrieval.get("intensity", "low")
    difficulty = INTENSITY_TO_DIFFICULTY.get(intensity, "beginner")

    return {
        "id": identity.get("item_id"),
        "title": title,
        "description": description,
        "category": category,
        "practice_type": None,
        "duration_minutes": duration,
        "difficulty": difficulty,
        "is_free": True,
        "is_personalized": False,
        "personalized_reason": None,
        "access_level": "free",
        "tags": _derive_tags(retrieval),
        "need_ids": need_ids,
        "format_id": fmt,
        "outcome_label": outcome_label,
        "instructions": steps,
        "target_axis": None,
        "target_modulator": None,
        "pattern_type": None,
        "source_domain": None,
        "target_domain": None,
        "cycle_type": None,
        "trigger_phase": None,
        "sequence_id": None,
        "step_number": None,
        "total_steps": None,
        "related_practices": [],
        "audio_url": None,
    }


# --- public catalog API -------------------------------------------------------


def all_content_library_practices(locale: str = "ru") -> list[dict[str, Any]]:
    """Return all active/accepted content-library items as practice dicts."""
    library = _load_content_library()
    practices: list[dict[str, Any]] = []
    for item in library.get("items", []):
        mapped = _content_item_to_practice(item, locale)
        if mapped is not None:
            practices.append(mapped)
    return practices


def select_content_library_practices(
    *,
    locale: str = "ru",
    need: str | None = None,
    format_id: str | None = None,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    """Ranked/filtered slice of the content-library catalog for the hub."""
    practices = all_content_library_practices(locale=locale)

    need_key = (need or "").strip().lower() or None
    if need_key and need_key in STATE_CYCLE_NEED_IDS:
        practices = [p for p in practices if need_key in [str(x).lower() for x in p.get("need_ids", [])]]
        practices = rank_practices_for_need(practices, need_key)

    format_key = (format_id or "").strip().lower() or None
    if format_key and format_key in STATE_CYCLE_FORMAT_IDS:
        practices = [p for p in practices if str(p.get("format_id") or "").lower() == format_key]

    if limit is not None and limit > 0:
        practices = practices[:limit]

    return practices


def get_content_library_practice_by_id(practice_id: str, locale: str = "ru") -> dict[str, Any] | None:
    """Return a single content-library practice by its `item_id`."""
    for practice in all_content_library_practices(locale=locale):
        if str(practice.get("id") or "") == practice_id:
            return practice
    return None
