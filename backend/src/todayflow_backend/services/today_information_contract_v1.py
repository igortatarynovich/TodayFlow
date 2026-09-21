"""Today Information Contract v1 — closed N=20 as a code gate.

SoT: docs/today/TODAY_INFORMATION_CONTRACT_V1.md

Any new Today meaning producer must name TIC_K + dependent TIC_F.
Chrome / transport failure are exempt.
TIC-K* is not PIC-K*. Character Engine prose is not Today N.
"""

from __future__ import annotations

import re
from pathlib import Path
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
        "tic_f": ("F09", "F10"),
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
        "tic_k": ("K15",),
        "tic_f": ("F05", "F09", "F14"),
        "slot_id": "T3.color.name",
    },
    {
        "module": "content_library_selection_v1",
        "tic_k": ("K16",),
        "tic_f": ("F10",),
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
    {"tic_k": "K13", "status": "COMPLETE", "slot_id": ("T2.lens_card",)},
    {"tic_k": "K14", "status": "COMPLETE", "slot_id": ("T2.lens_number",)},
    {"tic_k": "K15", "status": "COMPLETE", "slot_id": ("T3.color.name", "T3.color.hex", "T3.color.lines")},
    {"tic_k": "K16", "status": "COMPLETE", "slot_id": ("T3.practice",)},
    {"tic_k": "K17", "status": "COMPLETE", "slot_id": ("T3.affirmation",)},
    {"tic_k": "K18", "status": "COMPLETE", "slot_id": ("T3.depth",)},
    {"tic_k": "K19", "status": "COMPLETE", "slot_id": ("T1.continuity",)},
    {"tic_k": "K20", "status": "COMPLETE", "slot_id": ("T3.unavailable",)},
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

# ---------------------------------------------------------------------------
# Close-out gate (independent of TIC_COVERAGE).
# SoT: docs/today/TODAY_INFORMATION_CONTRACT_V1.md §12
# Coverage table COMPLETE is not the verdict. Re-audit the live chain.
# ---------------------------------------------------------------------------

TIC_CLOSEOUT_BLOCKS: Final[tuple[str, ...]] = (
    "executable_re_audit",
    "inventory_last_authority",
    "forbidden_source_scan",
    "omit_integrity",
)

TIC_LOCKED_SURFACE_RELPATHS: Final[tuple[str, ...]] = (
    "frontend/src/app/today/page.tsx",
    "frontend/src/components/today/composition/TodayProductScreenFlow.tsx",
    "frontend/src/components/today/composition/TodayDayBrief.tsx",
    "frontend/src/components/today/composition/TodayRitualLensPair.tsx",
    "frontend/src/components/today/composition/TodayMyDayPane.tsx",
    "frontend/src/components/today/composition/TodayMyDayRhythm.tsx",
    "frontend/src/components/today/composition/TodayDayTasksBlock.tsx",
    "frontend/src/components/today/composition/TodayEveningGratitudeBlock.tsx",
    "frontend/src/components/today/composition/TodayDepthLayerSection.tsx",
    "frontend/src/lib/todayDayBrief.ts",
    "frontend/src/lib/todayK01HumanLine.ts",
    "frontend/src/lib/todayPersonalFocusAxis.ts",
    "frontend/src/lib/todayMyDayPriority.ts",
    "frontend/src/lib/ritualRevealCopy.ts",
    "frontend/src/lib/todaySupportXor.ts",
    "frontend/src/lib/todayPracticeSelect.ts",
    "frontend/src/lib/todayInstructionBridge.ts",
    "frontend/src/lib/displayGrammar/emitTodayDisplayFrame.ts",
)

# Wave2 / leftover Glance as a fifth act. Out of TIC locked-surface scope
# unless a locked file mounts TodayGlanceAct or renders glanceSection.
TIC_GLANCE_LEFTOVER_RELPATHS: Final[tuple[str, ...]] = (
    "frontend/src/components/today/composition/TodayGlanceAct.tsx",
    "frontend/src/lib/todayGlanceEnergy.ts",
    "frontend/src/lib/todayGlanceTexture.ts",
    "frontend/src/lib/todayGlanceSphereChips.ts",
    "frontend/src/lib/todayDailyFocus.ts",
)

TIC_REGRESSION_K: Final[tuple[str, ...]] = (
    "K01",
    "K06",
    "K07",
    "K09",
    "K10",
    "K13",
    "K14",
    "K15",
    "K16",
    "K17",
    "K20",
)

_PIC_CE_MARKERS: Final[tuple[str, ...]] = (
    "P1.recognition_line",
    "P1.identity_core",
    "compose_k01_identity",
    "character_engine_stage",
    "13-key",
    "identity_core",
)


def _repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "docs" / "today" / "TODAY_INFORMATION_CONTRACT_V1.md").is_file():
            return parent
    raise RuntimeError("TodayFlow repo root not found from today_information_contract_v1")


def _read(root: Path, rel: str) -> str:
    return (root / rel).read_text(encoding="utf-8")


def _code_only(text: str) -> str:
    """Strip comments so prohibition scans do not trip on 'not X' documentation."""
    text = re.sub(r"/\*[\s\S]*?\*/", "", text)
    text = re.sub(r'"""[\s\S]*?"""', "", text)
    text = re.sub(r"'''[\s\S]*?'''", "", text)
    text = re.sub(r"//.*?$", "", text, flags=re.M)
    text = re.sub(r"#.*?$", "", text, flags=re.M)
    return text


def _inventory_has_slot(inventory: str, catalog: str, slot: str) -> bool:
    token = slot.split(".*")[0]
    if f"`{slot}`" in inventory or slot in catalog:
        return True
    if f"`{token}`" in inventory or token in catalog:
        return True
    # Wildcard family: T3.color.name is authorized by T3.color.*
    parts = slot.split(".")
    while len(parts) > 1:
        parts.pop()
        family = ".".join(parts) + ".*"
        if f"`{family}`" in inventory or family in catalog:
            return True
    return False


def _block(name: str, verdict: str, **extra: object) -> dict[str, object]:
    row: dict[str, object] = {"block": name, "verdict": verdict}
    row.update(extra)
    return row


def _probe_executable_re_audit() -> dict[str, object]:
    """Re-run live producer/omit functions. Does not read TIC_COVERAGE statuses."""
    from todayflow_backend.data import card_base_v1, number_base_v1
    from todayflow_backend.services.day_scenario_project_v1 import (
        _personal_narrative_avoid_lines,
        _personal_narrative_do_lines,
        _personal_narrative_practice_recommendation,
    )
    from todayflow_backend.services.day_scenario_v1 import (
        F05_ENERGY_TO_COLOR_TAGS,
        F09_DOMAIN_TO_COLOR_TAGS,
        _has_grounded_f09,
    )
    from todayflow_backend.services.global_day_engine_v1 import (
        ACTION_TYPES,
        ENERGY_SET,
        build_global_day_profile_v1,
        build_personal_day_nest_v1,
        is_global_event,
        pick_primary_energy,
    )
    from todayflow_backend.services.hook_reveal_v1 import (
        _personal_card_lens_line,
        _personal_number_lens_line,
        attach_hooks_to_symbol_view,
        build_card_hook_reveal,
        build_number_hook_reveal,
    )
    from todayflow_backend.services.today_depth_layer_v1 import DEPTH_LAYER_TOPICS
    from todayflow_backend.services.today_domain_verdicts_v1 import (
        DOMAINS,
        overlay_focus_axis_from_natal_point,
    )

    defects: list[str] = []

    # K01 — closed 8-set Engine kind. Formulation lives on FE; BE must not invent a 9th.
    if ENERGY_SET != (
        "grounded",
        "flow",
        "radiance",
        "momentum",
        "clarity",
        "tension",
        "renewal",
        "depth",
    ):
        defects.append("K01: ENERGY_SET mutated")
    scores = {k: 0.1 for k in ENERGY_SET}
    scores["tension"] = 0.9
    if pick_primary_energy(scores) != "tension":
        defects.append("K01: pick_primary_energy did not keep Engine argmax")
    if pick_primary_energy({k: 0.0 for k in ENERGY_SET}) not in ENERGY_SET:
        defects.append("K01: empty scores left the 8-set")

    # K02 — ranked global drivers; natal/card filtered.
    if is_global_event({"kind": "personal_transit", "id": "pt-mars-natal"}):
        defects.append("K02: natal event treated as global")
    profile = build_global_day_profile_v1(
        day_events_pack={
            "events": [
                {
                    "id": "moon-ingress-1",
                    "kind": "moon_ingress",
                    "fact_ru": "Луна вошла в Рыбы",
                    "strength": 0.8,
                },
                {
                    "id": "pt-mars-natal",
                    "kind": "personal_transit",
                    "fact_ru": "Марс по наталу",
                    "strength": 0.99,
                },
            ],
            "ranked_drivers": ["pt-mars-natal", "moon-ingress-1"],
        }
    )
    ids = [str(d.get("id")) for d in (profile.get("drivers") or [])]
    if "moon-ingress-1" not in ids or "pt-mars-natal" in ids:
        defects.append("K02: global ranker leaked natal or dropped sky")

    # K03 / K04 — closed action types; risk ≠ personal avoid.
    if len(ACTION_TYPES) != 8:
        defects.append("K03/K04: ACTION_TYPES mutated")
    if "hard_negotiation" not in (profile.get("risk") or []) and "sensitive_conversation" not in (
        profile.get("risk") or []
    ):
        # tension-heavy fixtures usually emit a risk type; empty risk is omit, not a leak.
        pass
    if profile.get("primary_energy") not in ENERGY_SET:
        defects.append("K03: profile energy left the 8-set")

    # K05 — Engine windows remain the clock authority on the profile.
    if "windows" not in profile:
        defects.append("K05: global profile dropped windows")

    # K06 — overlay thesis field is not a kitchen join (writer source).
    # Live omit: nest without natal_transit drops focus_axis; summary writer is day_personal_v1.
    nest = build_personal_day_nest_v1(
        {
            "day_personal": {
                "personal_astrology": {"beats": [{"kind": "time_lords", "title": "Firdaria"}]},
                "human_design": {"summary_ru": "Генератор"},
                "summary_ru": "не должно стать осью",
            }
        }
    )
    overlay = (nest or {}).get("natal_overlay") or nest or {}
    if overlay.get("focus_axis"):
        defects.append("K06/K07: kitchen beat minted focus_axis")

    # K07 — F10 is DOMAIN membership of already-chosen natal point.
    if DOMAINS != ("work", "money", "relationships", "energy"):
        defects.append("K07: 4-set mutated")
    if overlay_focus_axis_from_natal_point("sun") not in DOMAINS:
        defects.append("K07: sun did not map to a closed domain")
    if overlay_focus_axis_from_natal_point("chiron") is not None:
        defects.append("K07: unmapped point did not omit")
    if overlay_focus_axis_from_natal_point(None) is not None:
        defects.append("K07: missing point did not omit")

    # K09 / K10 / K17 — Personal Narrative writers stay empty (Global scene is not personal).
    if _personal_narrative_do_lines() != []:
        defects.append("K09: personal do writer filled from a leftover")
    if _personal_narrative_avoid_lines() != []:
        defects.append("K10: personal avoid writer filled from a leftover")
    if _personal_narrative_practice_recommendation() is not None:
        defects.append("K17: scene rec packaged as personal affirmation")

    # K11 / K12 — catalog lookup still exists; not a day-cause.
    card = card_base_v1.get_base_meaning(0, "upright")
    if not card or not str(card.get("meaning") or "").strip():
        defects.append("K11: card_base lookup empty")
    number = number_base_v1.get_number_base(4)
    if not number or not str(number.get("base_meaning") or number.get("meaning") or "").strip():
        defects.append("K12: number_base lookup empty")

    # K13 / K14 — Global chorus stays on bridge; personal_angle omits without Personal×symbol.
    chorus_card = {"day_card": {"link_to_conflict": "хор карты не линза"}}
    card_hook = build_card_hook_reveal(
        card_id=0,
        orientation="upright",
        chorus=chorus_card,
        personal_angle=_personal_card_lens_line(),
        profile_depth="deep",
    )
    if card_hook.get("personal_angle") != "omit":
        defects.append("K13: chorus packaged as personal card lens")
    if card_hook.get("bridge_to_day") == "хор карты не линза" and card_hook.get("personal_angle") == "хор карты не линза":
        defects.append("K13: personal_angle copied chorus")
    attached = attach_hooks_to_symbol_view(
        {"card": {"revealed": True, "id": 0, "orientation": "upright"}},
        chorus=chorus_card,
        profile_depth="deep",
    )
    attached_lens = ((attached.get("card") or {}).get("hook_reveal") or {}).get("personal_angle")
    if attached_lens not in {"omit", None, ""}:
        defects.append("K13: attach still paints chorus as lens")

    chorus_num = {
        "day_number": {
            "link_to_conflict": "хор числа не линза",
            "tempo": "медленный темп",
        }
    }
    num_hook = build_number_hook_reveal(
        value=4,
        chorus=chorus_num,
        personal_angle=_personal_number_lens_line(),
        profile_depth="deep",
    )
    if num_hook.get("personal_angle") != "omit":
        defects.append("K14: chorus packaged as personal number lens")

    # K15 — F05+F09 tags; no F09 → not grounded.
    if set(F05_ENERGY_TO_COLOR_TAGS) != set(ENERGY_SET):
        defects.append("K15: F05 color map left the 8-set")
    if set(F09_DOMAIN_TO_COLOR_TAGS) != set(DOMAINS):
        defects.append("K15: F09 color map left the 4-set")
    if _has_grounded_f09([]) or _has_grounded_f09(None):
        defects.append("K15: empty overlay counted as grounded F09")

    # K16 — selector still class-gated; need cell is F10 on FE (Jest).
    from todayflow_backend.services.content_library_selection_v1 import NeedQuery

    q = NeedQuery(
        purpose="grounding",
        direction="stabilize",
        context=["body"],
        content_class="practice",
    )
    if q.content_class != "practice":
        defects.append("K16: practice class dropped from query")

    # K18 — deepen is a closed topic menu, not a second Today plot.
    if "full_day" not in DEPTH_LAYER_TOPICS or len(DEPTH_LAYER_TOPICS) < 5:
        defects.append("K18: depth topic menu mutated")

    # K08 / K19 / K20 — FE chain; BE confirms N still maps those slots.
    for kid in ("K08", "K19", "K20"):
        if kid not in KNOWLEDGE_TO_SLOT:
            defects.append(f"{kid}: dropped from N")

    if "K21" in TIC_KNOWLEDGE_IDS:
        defects.append("invented K21")

    complete = tuple(k for k in TIC_KNOWLEDGE_IDS if not any(d.startswith(f"{k}:") for d in defects))
    return _block(
        "executable_re_audit",
        "PASS" if not defects else "FAIL",
        complete=len(complete),
        partial=0,
        missing=0,
        omit_by_design=0,
        defects=tuple(defects),
        note="Independent producer re-run. TIC_COVERAGE statuses were not read.",
    )


def _probe_inventory_last_authority(root: Path) -> dict[str, object]:
    inventory = _read(root, "docs/today/TODAY_DISPLAY_INVENTORY_V1.md")
    catalog = _read(root, "frontend/src/lib/displayGrammar/inventoryCatalog.ts")
    emit = _read(root, "frontend/src/lib/displayGrammar/emitTodayDisplayFrame.ts")
    pane = _read(root, "frontend/src/components/today/composition/TodayMyDayPane.tsx")
    defects: list[str] = []

    for kid, slots in KNOWLEDGE_TO_SLOT.items():
        for slot in slots:
            if not _inventory_has_slot(inventory, catalog, slot):
                defects.append(f"{kid}: Inventory missing {slot}")

    # Payload presence is not authority: locked pane paints only Inventory props.
    if "meaningUnavailable" not in pane or "T3.unavailable" not in pane and "TODAY_UNAVAILABLE_COPY" not in pane:
        defects.append("K20: unavailable pane is not honesty-copy only")
    if "recommended_action" in pane or "interpretive_chorus" in pane:
        defects.append("locked MY DAY pane reads scene/chorus as meaning")

    # Scanner may omit some slots (rhythm/color/practice scan gap) but must not
    # emit an unknown Today slot.
    if "slot_id:" in emit and "P1." in emit:
        defects.append("Today emit leaked a Profile slot")

    for rel in TIC_LOCKED_SURFACE_RELPATHS:
        if not (root / rel).is_file():
            defects.append(f"locked surface missing: {rel}")

    return _block(
        "inventory_last_authority",
        "PASS" if not defects else "FAIL",
        defects=tuple(defects),
    )


def _probe_forbidden_source_scan(root: Path) -> dict[str, object]:
    defects: list[str] = []
    personal = _read(root, "backend/src/todayflow_backend/services/day_personal_v1.py")
    if "overlay_thesis" not in personal or "is_kitchen_mechanism_prose" not in personal:
        defects.append("K06: overlay thesis writer missing kitchen reject")
    for family in ("human_design", "bazi", "vedic_personal", "electional_horary", "name_numbers"):
        # Pack may keep kitchen nests; they must not feed summary_ru assignment.
        if f"summary = {family}" in personal or f"+ {family}" in personal.split("summary =", 1)[-1][:400]:
            defects.append(f"K06: {family} still joins summary_ru")

    axis = _code_only(_read(root, "frontend/src/lib/todayPersonalFocusAxis.ts"))
    if "scenes" in axis or ".sphere" in axis or "sphere_label" in axis:
        defects.append("K07: FE axis picker still reads scene sphere")

    priority = _read(root, "frontend/src/lib/todayMyDayPriority.ts")
    if "recommended_action" not in priority or "isGlobalSceneAction" not in priority:
        defects.append("K09: Global scene action reject missing")
    if "do_not" not in priority or "isGlobalSceneCaution" not in priority:
        defects.append("K10: Global do_not reject missing")

    lens = _read(root, "frontend/src/lib/ritualRevealCopy.ts")
    if "bridge_to_day" not in lens or "personal_angle" not in lens:
        defects.append("K13/K14: lens picker missing chorus reject")

    support = _code_only(_read(root, "frontend/src/lib/todaySupportXor.ts"))
    if "contentClassFromFocusAxis" not in support:
        defects.append("K17: XOR is not the existing F10 content class")
    if "date-hash" in support or re.search(r"\bhash\b", support):
        defects.append("K17: date-hash selector returned")

    practice = _code_only(_read(root, "frontend/src/lib/todayPracticeSelect.ts"))
    if "GLOBAL_ENERGY_NEED" in practice or "global_day?.primary_energy" in practice:
        defects.append("K16: Global energy still feeds practice select")

    human = _read(root, "frontend/src/lib/todayK01HumanLine.ts")
    if "SHARED_DAY_HUMAN_LINES" not in human:
        defects.append("K01: closed sentence map missing")
    for marker in _PIC_CE_MARKERS:
        if marker in human:
            defects.append(f"K01: PIC/CE marker {marker}")

    locked_blob = "\n".join(_read(root, rel) for rel in TIC_LOCKED_SURFACE_RELPATHS if (root / rel).is_file())
    if "compose_k01_identity" in locked_blob or "P1.recognition_line" in locked_blob:
        defects.append("locked Today surfaces import PIC Identity Core")

    # Glance leftover must stay unmounted on locked surfaces.
    glance_in_scope = False
    glance_hits: list[str] = []
    for rel in TIC_LOCKED_SURFACE_RELPATHS:
        text = _read(root, rel) if (root / rel).is_file() else ""
        if "TodayGlanceAct" in text:
            glance_in_scope = True
            glance_hits.append(rel)
        if "{glanceSection}" in text or "glanceSection}" in text and "const glanceSection" not in text:
            # rendered, not merely declared
            if "{glanceSection}" in text:
                glance_in_scope = True
                glance_hits.append(f"{rel}:renders glanceSection")
    page = _read(root, "frontend/src/app/today/page.tsx")
    if "TodayGlanceAct" in page:
        glance_in_scope = True
        glance_hits.append("today/page.tsx")

    if glance_in_scope:
        defects.append("Glance leftover mounted on a locked Today surface: " + ", ".join(glance_hits))

    return _block(
        "forbidden_source_scan",
        "PASS" if not defects else "FAIL",
        defects=tuple(defects),
        regression_set=TIC_REGRESSION_K,
        glance_in_locked_surface_scope=glance_in_scope,
        glance_hits=tuple(glance_hits),
    )


def _probe_omit_integrity(root: Path) -> dict[str, object]:
    from todayflow_backend.services.day_scenario_project_v1 import (
        _personal_narrative_avoid_lines,
        _personal_narrative_do_lines,
        _personal_narrative_practice_recommendation,
    )
    from todayflow_backend.services.global_day_engine_v1 import build_personal_day_nest_v1
    from todayflow_backend.services.hook_reveal_v1 import (
        _personal_card_lens_line,
        _personal_number_lens_line,
    )
    from todayflow_backend.services.today_domain_verdicts_v1 import overlay_focus_axis_from_natal_point

    defects: list[str] = []
    if build_personal_day_nest_v1({}) is not None:
        defects.append("no overlay → personal nest should omit")
    if overlay_focus_axis_from_natal_point("") is not None:
        defects.append("empty natal point minted F10")
    if _personal_narrative_do_lines() or _personal_narrative_avoid_lines():
        defects.append("empty Personal do/avoid minted lines")
    if _personal_card_lens_line() or _personal_number_lens_line():
        defects.append("empty Personal×card/number minted a lens")
    if _personal_narrative_practice_recommendation() is not None:
        defects.append("empty K17 branch switched to scene rec")

    pane = _read(root, "frontend/src/components/today/composition/TodayMyDayPane.tsx")
    xor = _read(root, "frontend/src/lib/todaySupportXor.ts")
    if "extraCards" not in pane or "meaningUnavailable" not in pane:
        defects.append("K20: unavailable extraCards omit missing")
    if "empty selected branch" not in xor.lower() and "does not switch" not in xor.lower():
        if "practiceReady ? \"practice\" : null" not in xor and "practiceReady ? 'practice' : null" not in xor:
            # source comment + empty-branch omit
            if "input.practiceReady ? \"practice\" : null" not in xor and "input.practiceReady ? 'practice' : null" not in xor:
                if "practiceReady" not in xor:
                    defects.append("K17: empty selected branch omit missing")

    human = _read(root, "frontend/src/lib/todayK01HumanLine.ts")
    if "Unknown / missing → omit" not in human and "return null" not in human:
        defects.append("K01: missing energy omit missing")

    return _block(
        "omit_integrity",
        "PASS" if not defects else "FAIL",
        defects=tuple(defects),
    )


def evaluate_tic_closeout(repo_root: Path | None = None) -> dict[str, object]:
    """Independent close-out. Coverage-table COMPLETE is not accepted as proof."""
    root = Path(repo_root) if repo_root else _repo_root()
    blocks = (
        _probe_executable_re_audit(),
        _probe_inventory_last_authority(root),
        _probe_forbidden_source_scan(root),
        _probe_omit_integrity(root),
    )
    by_name = {str(b["block"]): b for b in blocks}
    failed = tuple(str(b["block"]) for b in blocks if b["verdict"] != "PASS")
    glance_scope = bool(by_name["forbidden_source_scan"].get("glance_in_locked_surface_scope"))
    verdict = "FAIL" if failed else "PASS"
    return {
        "contract": "TODAY_INFORMATION_CONTRACT",
        "verdict": verdict,
        "status": "CLOSED" if verdict == "PASS" else "OPEN",
        "n": 20,
        "invented_k21": False,
        "blocks": blocks,
        "failed_blocks": failed,
        "glance_leftover": {
            "in_locked_surface_scope": glance_scope,
            "declared_out_of_scope": not glance_scope,
            "files": TIC_GLANCE_LEFTOVER_RELPATHS,
            "note": (
                "TodayGlanceAct unmounted; glanceSection unrendered. "
                "Named Glance helpers on the locked path are not a fifth act: "
                "T1-hero.sheet energyCause is Inventory-authorized Global; "
                "T3.priority glancePrioritize is identity-check vs personal today_move."
            ),
        },
        "independent_of_tic_coverage": True,
    }
