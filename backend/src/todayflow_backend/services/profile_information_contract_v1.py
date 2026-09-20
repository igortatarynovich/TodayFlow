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
        "pic_k": ("K01", "K02", "K05"),
        "pic_f": ("F03", "F06", "F07"),
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
        "pic_k": ("K01", "K02", "K04", "K05", "K07", "K09", "K10", "K12"),
        "pic_f": ("F01", "F03", "F04", "F05", "F06", "F07", "F08", "F09"),
        "slot_id": "P1.identity_core",
    },
    {
        "module": "profile_portrait_why_projection_v0",
        "pic_k": ("K12",),
        "pic_f": ("F09",),
        "slot_id": "P2.selected_life_path",
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
    "K03": ("P2.anchor.asc", "P2.anchor.mc"),
    "K04": ("P3.insight", "P3.help"),
    "K05": ("P3.insight",),
    "K06": (),
    "K07": ("P4.sphere.title", "P4.sphere.teaser", "P4.sphere.expand"),
    "K08": ("P4.effort_vector",),
    "K09": ("P3.insight", "P3.help"),
    "K10": ("P3.help", "P4.effort_vector"),
    "K11": ("P5.bridge_line",),
    "K12": ("P2.selected_life_path",),
    "K13": ("P2.name_numerology",),
    "K14": ("P2.correspondence",),
    "K15": ("P6.natal_decode",),
    "K16": (),
    "K17": ("P-data.cta_text", "P-forming.message"),
    "K18": ("P3.living_evidence",),
}

COVERAGE_STATUSES: Final[frozenset[str]] = frozenset(
    {"COMPLETE", "PARTIAL", "MISSING", "OMIT-BY-DESIGN"}
)

# Executable coverage — SoT table: PROFILE_INFORMATION_CONTRACT_V1 §11.
PIC_COVERAGE: Final[tuple[dict[str, object], ...]] = (
    {"pic_k": "K01", "status": "PARTIAL", "slot_id": ("P1.recognition_line", "P1.identity_core")},
    {"pic_k": "K02", "status": "COMPLETE", "slot_id": ("P2.anchor.sun", "P2.anchor.moon", "P2.anchor.asc")},
    {"pic_k": "K03", "status": "PARTIAL", "slot_id": ("P2.anchor.asc", "P2.anchor.mc")},
    {"pic_k": "K04", "status": "COMPLETE", "slot_id": ("P3.insight", "P3.help")},
    {"pic_k": "K05", "status": "COMPLETE", "slot_id": ("P3.insight",)},
    {"pic_k": "K06", "status": "MISSING", "slot_id": ()},
    {"pic_k": "K07", "status": "COMPLETE", "slot_id": ("P4.sphere.title", "P4.sphere.teaser", "P4.sphere.expand")},
    {"pic_k": "K08", "status": "COMPLETE", "slot_id": ("P4.effort_vector",)},
    {"pic_k": "K09", "status": "COMPLETE", "slot_id": ("P3.insight", "P3.help")},
    {"pic_k": "K10", "status": "PARTIAL", "slot_id": ("P3.help", "P4.effort_vector")},
    {"pic_k": "K11", "status": "COMPLETE", "slot_id": ("P5.bridge_line",)},
    {"pic_k": "K12", "status": "COMPLETE", "slot_id": ("P2.selected_life_path",)},
    {"pic_k": "K13", "status": "COMPLETE", "slot_id": ("P2.name_numerology",)},
    {"pic_k": "K14", "status": "COMPLETE", "slot_id": ("P2.correspondence",)},
    {"pic_k": "K15", "status": "PARTIAL", "slot_id": ("P6.natal_decode",)},
    {"pic_k": "K16", "status": "PARTIAL", "slot_id": ()},
    {"pic_k": "K17", "status": "COMPLETE", "slot_id": ("P-data.cta_text", "P-forming.message")},
    {"pic_k": "K18", "status": "COMPLETE", "slot_id": ("P3.living_evidence",)},
)

CHROME_EXEMPT_PREFIXES: Final[tuple[str, ...]] = (
    "P-forming",
    "P-data",
    "TF.",
    "SF.",
)
