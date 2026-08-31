"""Deterministic selection of Content Items from the canonical practice library.

No LLM. No randomness. A product need (purpose/direction/state/context) is matched
against the retrieval tags of active items; the best match is returned with a short
reason string. This is the runtime bridge between Meaning (which emits a need) and
the Content Library (which holds the expression of an accepted technique).

Canon: docs/practices/CONTENT_LIBRARY_SELECTION_V1.md
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from todayflow_backend.data.reference_machine_loader import DATA_ROOT

_PRACTICE_REF = DATA_ROOT / "reference" / "practice"
LIBRARY_PATH = _PRACTICE_REF / "content_library_v1.json"
TECHNIQUE_PATH = _PRACTICE_REF / "technique_canon_v1.json"


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


def load_content_library(path: Path | None = None) -> dict[str, Any]:
    """Load the canonical content library JSON."""
    with open(path or LIBRARY_PATH, encoding="utf-8") as f:
        return json.load(f)


def load_technique_canon(path: Path | None = None) -> dict[str, Any]:
    """Load the canonical technique registry JSON."""
    with open(path or TECHNIQUE_PATH, encoding="utf-8") as f:
        return json.load(f)


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
