"""Profile Information Contract v1 — closed N=18 as a code gate.

SoT: docs/profile/PROFILE_INFORMATION_CONTRACT_V1.md

Any Profile meaning producer must name PIC_K + dependent PIC_F.
Chrome / transport failure are exempt.
"""

from __future__ import annotations

from typing import Final

PIC_KNOWLEDGE_IDS: Final[tuple[str, ...]] = tuple(f"K{i:02d}" for i in range(1, 19))
PIC_FACT_IDS: Final[tuple[str, ...]] = tuple(f"F{i:02d}" for i in range(1, 14))

# Meaning producers that may emit Profile content. Chrome/errors omitted.
# slot_id None = derived material, not a first-paint slot.
PROFILE_MEANING_PRODUCERS: Final[tuple[dict[str, object], ...]] = (
    {
        "module": "character_engine_stage1_evidence_v0",
        "pic_k": ("K01", "K02"),
        "pic_f": ("F03", "F06"),
        "slot_id": None,
    },
    {
        "module": "character_engine_stage2_identity_v0",
        "pic_k": ("K01", "K02"),
        "pic_f": ("F03", "F06"),
        "slot_id": "P1.recognition_line",
    },
    {
        "module": "character_engine_stage3_internal_v0",
        "pic_k": ("K04", "K05", "K06"),
        "pic_f": ("F03", "F04", "F07", "F08"),
        "slot_id": "P3.insight",
    },
    {
        "module": "character_engine_stage4_life_v0",
        "pic_k": ("K07", "K08", "K09"),
        "pic_f": ("F06",),
        "slot_id": "P4.sphere.teaser",
    },
    {
        "module": "character_engine_stage5_assembly_v0",
        "pic_k": ("K10", "K11"),
        "pic_f": ("F13",),
        "slot_id": "P4.effort_vector",
    },
    {
        "module": "character_engine_profile_consumption_v0",
        "pic_k": ("K01", "K02", "K04", "K10"),
        "pic_f": ("F03", "F06"),
        "slot_id": "P1.identity_core",
    },
    {
        "module": "profile_header_knowledge_v0",
        "pic_k": ("K14",),
        "pic_f": ("F12",),
        "slot_id": "P2.correspondence",
    },
    {
        "module": "profile_matrix_adapter_v0",
        "pic_k": ("K13", "K14"),
        "pic_f": ("F10", "F12"),
        "slot_id": "P2.name_numerology",
    },
)

KNOWLEDGE_TO_SLOT: Final[dict[str, tuple[str, ...]]] = {
    "K01": ("P1.recognition_line", "P1.identity_core"),
    "K02": ("P2.anchor.sun", "P2.anchor.moon", "P2.anchor.asc", "P2.anchor.mc", "P2.anchor.element"),
    "K13": ("P2.name_numerology",),
    "K14": ("P2.correspondence",),
}

CHROME_EXEMPT_PREFIXES: Final[tuple[str, ...]] = (
    "P-forming",
    "P-data",
    "TF.",
    "SF.",
)
