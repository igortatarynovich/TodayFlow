"""Shared OpenAPI / REST contracts for PIM learning surfaces (attachment, ILR, meaning events)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

COMPATIBILITY_ATTACHMENT_REFERENCE_V0_CONTRACT = "compatibility_attachment_reference_v0"
COMPAT_DEEP_BLOCK_KEYS = ("emotions", "communication", "conflicts", "sexuality", "long_term")


class AttachmentStyleHintResponse(BaseModel):
    """Reference CD hint — hypothesis only, not user diagnosis."""

    code: str = Field(..., description="Attachment style code from attachment_style_registry_v1")
    label: str = Field(..., description="Localized display label")
    summary: str = Field(..., max_length=240, description="Short hypothesis copy for confirm chip")
    score: float | None = Field(None, description="Engine ranking score (reference bias × echo)")
    evidence_blocks: list[str] = Field(
        default_factory=list,
        description="Deep block keys that contributed (communication, conflicts, emotions)",
    )
    confirmation_required: bool = True
    knowledge_type: Literal["hypothesis"] = "hypothesis"
    source: str = Field(
        default=COMPATIBILITY_ATTACHMENT_REFERENCE_V0_CONTRACT,
        description="Reference contract id",
    )


class CompatibilityAttachmentReferenceV0(BaseModel):
    """Compatibility dynamics attachment lens slice (CD → engine, learning-aware)."""

    contract_version: Literal["compatibility_attachment_reference_v0"] = (
        COMPATIBILITY_ATTACHMENT_REFERENCE_V0_CONTRACT
    )
    deep_block_order: list[str] = Field(
        default_factory=list,
        description="Ordered deep block keys after attachment bias",
    )
    attachment_style_hints: list[AttachmentStyleHintResponse] = Field(
        default_factory=list,
        max_length=3,
        description="Top attachment style hypotheses for confirm chip",
    )
    trigger_blocks: list[str] = Field(
        default_factory=list,
        description="Deep blocks with user echo feedback in this session",
    )
    reference_status: str = Field(
        default="active",
        description="attachment_style_registry_v1 container status at build time",
    )


class CompactUserModelInterpretationInstance(BaseModel):
    """ILR instance read slice for confirm chips (Profile, Compatibility)."""

    instance_id: str | None = Field(None, max_length=80)
    interpretation_ref_id: str | None = Field(
        None,
        max_length=80,
        description="ILR rule id, e.g. beh.compat_echo_yes.v1",
    )
    level: str | None = Field(None, max_length=16, description="Interpretation level L2–L4")
    summary: str | None = Field(None, max_length=200, description="Dominant summary for UI chip")
    dominant_meaning: str | None = Field(None, max_length=120)
    confirmation_required: bool | None = True
    evidence_count: int | None = Field(None, ge=0)
    user_verdict: Literal["confirm", "partial", "reject"] | None = Field(
        None,
        description="Set after interpretation_instance_confirm; hidden from pending chips",
    )


class CompatibilityAttachmentConfirmPayload(BaseModel):
    """POST /meaning/events payload when event_type=compatibility_attachment_confirm."""

    surface: str = Field(..., description="UI surface, e.g. analyze_dynamics, compatibility_exploration")
    attachment_style_code: str
    label: str
    summary: str
    echo: Literal["yes", "partial", "no"]
    verdict: Literal["confirm", "partial", "reject"]
    knowledge_id: str | None = Field(
        None,
        description="Target hypothesis id, e.g. inf-attachment-lens-anxious",
    )
    scenario_id: str | None = None


class InterpretationInstanceConfirmPayload(BaseModel):
    """POST /meaning/events payload when event_type=interpretation_instance_confirm."""

    surface: str = Field(..., description="e.g. analyze_dynamics, profile_quick_map, compatibility_exploration")
    instance_id: str
    interpretation_ref_id: str | None = None
    correction: Literal["confirm", "partial", "reject"]
    verdict: Literal["confirm", "partial", "reject"]
    summary: str | None = None
    scenario_id: str | None = None


class ProfileAtomCorrectionPayload(BaseModel):
    """POST /meaning/events payload when event_type=profile_atom_correction (incl. attachment promote)."""

    knowledge_id: str
    correction: Literal["confirm", "partial", "reject"]
    claim_summary: str | None = None
    surface: str | None = None
    attachment_style_code: str | None = None
