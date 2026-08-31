"""Deterministic Content Library selection endpoint (no LLM, no randomness).

Canon: docs/practices/CONTENT_LIBRARY_SELECTION_V1.md
"""

from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel

from todayflow_backend.services.content_library_selection_v1 import (
    NeedQuery,
    select_content_item,
)

router = APIRouter(prefix="/practices", tags=["practices"])


class ContentItemSelectResponse(BaseModel):
    """Public response for a deterministic content library lookup."""

    item_id: Optional[str]
    content_class: Optional[str]
    type: Optional[str]
    title: str
    body: str
    outcome_label: str
    duration: Optional[int]
    duration_unit: Optional[str]
    context: List[str]
    delivery: List[str]
    reason: str
    matched: bool


@router.get("/select", response_model=ContentItemSelectResponse)
async def select_content_item_endpoint(
    purpose: str,
    direction: str,
    input_state: Optional[str] = Query(
        None, description="Comma-separated input_state tags"
    ),
    context: Optional[str] = Query(None, description="Comma-separated context tags"),
    duration: Optional[int] = Query(None, description="Preferred session duration"),
    energy_effect: Optional[str] = Query(None, description="up | down | neutral"),
    content_class: Optional[str] = Query(None, description="practice | meditation | affirmation | discipline"),
    item_type: Optional[str] = Query(None, alias="type"),
    locale: str = Query("ru", description="Locale for title/body/outcome_label"),
) -> ContentItemSelectResponse:
    """Return the best active Content Item for a product need.

    This endpoint is deterministic: the same query + same library always returns the
    same item_id. It never calls an LLM. A `matched=false` response is honest about
    why nothing was found; it does not invent a placeholder.
    """
    query = NeedQuery(
        purpose=purpose,
        direction=direction,
        input_state=[s.strip() for s in input_state.split(",") if s.strip()]
        if input_state
        else [],
        context=[s.strip() for s in context.split(",") if s.strip()]
        if context
        else [],
        duration=duration,
        energy_effect=energy_effect,
        content_class=content_class,
        item_type=item_type,
        locale=locale,
    )
    selection = select_content_item(query)
    return ContentItemSelectResponse(
        item_id=selection.item_id,
        content_class=selection.content_class,
        type=selection.item_type,
        title=selection.title,
        body=selection.body,
        outcome_label=selection.outcome_label,
        duration=selection.duration,
        duration_unit=selection.duration_unit,
        context=selection.context,
        delivery=selection.delivery,
        reason=selection.reason,
        matched=selection.matched,
    )
