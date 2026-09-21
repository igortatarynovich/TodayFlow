"""Today Information Contract v1 — closed N=20 as a code gate.

SoT: docs/today/TODAY_INFORMATION_CONTRACT_V1.md

Any new Today meaning producer must name TIC_K + dependent TIC_F.
Chrome / transport failure are exempt.
TIC-K* is not PIC-K*. Character Engine prose is not Today N.
"""

from __future__ import annotations

from typing import Final

TIC_KNOWLEDGE_IDS: Final[tuple[str, ...]] = tuple(f"K{i:02d}" for i in range(1, 21))
TIC_FACT_IDS: Final[tuple[str, ...]] = tuple(f"F{i:02d}" for i in range(1, 17))

# Display slots for each knowledge id. Empty = honesty/chrome-adjacent or omit-only.
KNOWLEDGE_TO_SLOT: Final[dict[str, tuple[str, ...]]] = {
    "K01": (
        "T1-hero.energy_word",
        "T1-hero.energy_pct",
        "T1-hero.mood",
        "T1-hero.human_line",
        "T1-hero.sheet",
    ),
    "K02": ("T1-clock.transit", "T1-clock.sheet"),
    "K03": ("T1-strength.chip", "T1-strength.sheet"),
    "K04": ("T1-risk.chip", "T1-risk.sheet"),
    "K05": ("T1-clock.range", "T1-clock.spectrum", "T3.rhythm_row"),
    "K06": ("T3.headline",),
    "K07": ("T3.focus_title",),
    "K08": ("T3.focus_body",),
    "K09": ("T3.priority",),
    "K10": ("T3.caution",),
    "K11": ("T2.catalog_card", "T2.card_face"),
    "K12": ("T2.catalog_number", "T2.number_glyph"),
    "K13": ("T2.lens_card",),
    "K14": ("T2.lens_number",),
    "K15": ("T3.color.name", "T3.color.hex", "T3.color.lines"),
    "K16": ("T3.practice",),
    "K17": ("T3.affirmation",),
    "K18": ("T3.depth",),
    "K19": ("T1.continuity",),
    "K20": ("T3.unavailable",),
}

# Live-path census after coverage audit. Cite stamps on these modules = later K hops.
TODAY_MEANING_PRODUCERS: Final[tuple[dict[str, object], ...]] = (
    {
        "module": "global_day_engine_v1",
        "tic_k": ("K01", "K02", "K03", "K04", "K05", "K07"),
        "tic_f": ("F01", "F02", "F03", "F04", "F05", "F06", "F07", "F09", "F10"),
        "slot_id": "T1-hero.energy_word",
    },
    {
        "module": "day_personal_v1",
        "tic_k": ("K06",),
        "tic_f": ("F08", "F09"),
        "slot_id": "T3.headline",
    },
    {
        "module": "today_natal_activations_v1",
        "tic_k": ("K05", "K07", "K08"),
        "tic_f": ("F08", "F09", "F10"),
        "slot_id": "T3.focus_title",
    },
    {
        "module": "today_domain_verdicts_v1",
        "tic_k": ("K07",),
        "tic_f": ("F09", "F10"),
        "slot_id": "T3.focus_title",
    },
    {
        "module": "day_scenario_project_v1",
        "tic_k": ("K09", "K10", "K17"),
        "tic_f": ("F09",),
        "slot_id": "T3.priority",
    },
    {
        "module": "day_symbol_state_v1",
        "tic_k": ("K11", "K12", "K13", "K14"),
        "tic_f": ("F11", "F12", "F13"),
        "slot_id": "T2.catalog_card",
    },
    {
        "module": "hook_reveal_v1",
        "tic_k": ("K11", "K12", "K13", "K14"),
        "tic_f": ("F11", "F12", "F13"),
        "slot_id": "T2.lens_card",
    },
    {
        "module": "day_scenario_v1",
        "tic_k": ("K15", "K17"),
        "tic_f": ("F14",),
        "slot_id": "T3.color.name",
    },
    {
        "module": "content_library_selection_v1",
        "tic_k": ("K16",),
        "tic_f": ("F05",),
        "slot_id": "T3.practice",
    },
    {
        "module": "today_depth_layer_v1",
        "tic_k": ("K18",),
        "tic_f": ("F08", "F09"),
        "slot_id": "T3.depth",
    },
)

COVERAGE_STATUSES: Final[frozenset[str]] = frozenset(
    {"COMPLETE", "PARTIAL", "MISSING", "OMIT-BY-DESIGN"}
)

# Executable coverage — SoT table: TODAY_INFORMATION_CONTRACT_V1 §11.
TIC_COVERAGE: Final[tuple[dict[str, object], ...]] = (
    {"tic_k": "K01", "status": "COMPLETE", "slot_id": ("T1-hero.energy_word", "T1-hero.human_line")},
    {"tic_k": "K02", "status": "COMPLETE", "slot_id": ("T1-clock.transit",)},
    {"tic_k": "K03", "status": "COMPLETE", "slot_id": ("T1-strength.chip",)},
    {"tic_k": "K04", "status": "COMPLETE", "slot_id": ("T1-risk.chip",)},
    {"tic_k": "K05", "status": "COMPLETE", "slot_id": ("T1-clock.range", "T3.rhythm_row")},
    {"tic_k": "K06", "status": "COMPLETE", "slot_id": ("T3.headline",)},
    {"tic_k": "K07", "status": "COMPLETE", "slot_id": ("T3.focus_title",)},
    {"tic_k": "K08", "status": "COMPLETE", "slot_id": ("T3.focus_body",)},
    {"tic_k": "K09", "status": "COMPLETE", "slot_id": ("T3.priority",)},
    {"tic_k": "K10", "status": "COMPLETE", "slot_id": ("T3.caution",)},
    {"tic_k": "K11", "status": "COMPLETE", "slot_id": ("T2.catalog_card", "T2.card_face")},
    {"tic_k": "K12", "status": "COMPLETE", "slot_id": ("T2.catalog_number", "T2.number_glyph")},
    {"tic_k": "K13", "status": "PARTIAL", "slot_id": ("T2.lens_card",)},
    {"tic_k": "K14", "status": "PARTIAL", "slot_id": ("T2.lens_number",)},
    {"tic_k": "K15", "status": "PARTIAL", "slot_id": ("T3.color.name", "T3.color.hex", "T3.color.lines")},
    {"tic_k": "K16", "status": "PARTIAL", "slot_id": ("T3.practice",)},
    {"tic_k": "K17", "status": "PARTIAL", "slot_id": ("T3.affirmation",)},
    {"tic_k": "K18", "status": "COMPLETE", "slot_id": ("T3.depth",)},
    {"tic_k": "K19", "status": "COMPLETE", "slot_id": ("T1.continuity",)},
    {"tic_k": "K20", "status": "PARTIAL", "slot_id": ("T3.unavailable",)},
)

TIC_DEFECT_QUEUE: Final[tuple[str, ...]] = tuple(
    str(row["tic_k"])
    for row in TIC_COVERAGE
    if row["status"] in {"PARTIAL", "MISSING"}
)

CHROME_EXEMPT_PREFIXES: Final[tuple[str, ...]] = (
    "T1-date.",
    "T1-hero.eyebrow",
    "T1-clock.label",
    "T1-strength.label",
    "T1-risk.label",
    "T2-gate.",
    "T3.focus_label",
    "T3.priority_label",
    "T3.caution_label",
    "T3.rhythm_label",
    "T3.tasks_empty",
    "T4.",
    "TF.",
    "SF.",
)

# Guard: Today N must not map onto Profile Identity Core slots.
PIC_IDENTITY_SLOTS_FORBIDDEN: Final[frozenset[str]] = frozenset(
    {"P1.recognition_line", "P1.identity_core"}
)
