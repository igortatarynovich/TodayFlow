/**
 * Derived slot index for Grammar §9. Not meaning SoT.
 * SoT: PROFILE_DISPLAY_INVENTORY_V1 · TODAY_DISPLAY_INVENTORY_V1
 */

import type {
  DisplaySurface,
  FeTransform,
  InventorySlotRecord,
  SemanticOrigin,
  TextClass,
} from "@/lib/displayGrammar/types";

const T1_NO: SemanticOrigin[] = [
  "natal",
  "ce",
  "personal_day",
  "ritual_identity",
  "card",
  "number",
  "goals",
  "behavior",
];
const T3_NO: SemanticOrigin[] = ["ce", "card", "number", "goals", "global"];
const CE_OK: SemanticOrigin[] = ["ce", "chrome", "product"];
const GLOBAL_OK: SemanticOrigin[] = ["global", "chrome", "product"];
const CLIP: FeTransform[] = ["clip"];
const MAP: FeTransform[] = ["map_label"];
const HIDE: FeTransform[] = ["hide_by_gate"];
const CLIP_HIDE: FeTransform[] = ["clip", "hide_by_gate"];
const MAP_HIDE: FeTransform[] = ["map_label", "hide_by_gate"];
const NONE: FeTransform[] = ["none"];

function slot(
  slot_id: string,
  surface: DisplaySurface,
  text_class: TextClass,
  anti_dupe_groups: string[],
  allowed_origins: SemanticOrigin[],
  forbidden_origins: SemanticOrigin[],
  may_fe_transform: FeTransform[],
  extra: Partial<Pick<InventorySlotRecord, "budget_chars" | "budget_count" | "empty_behavior" | "inputs_lock">> = {},
): InventorySlotRecord {
  const generated = text_class === "generated" || text_class === "projected";
  return {
    slot_id,
    surface,
    text_class,
    anti_dupe_groups,
    allowed_origins,
    forbidden_origins,
    may_fe_transform,
    empty_behavior: extra.empty_behavior ?? "omit",
    inputs_lock: extra.inputs_lock ?? generated,
    budget_chars: extra.budget_chars,
    budget_count: extra.budget_count,
  };
}

const CHROME_OK: SemanticOrigin[] = ["chrome", "product"];
const CHROME_NO: SemanticOrigin[] = [
  "global",
  "personal_day",
  "natal",
  "ce",
  "ritual_identity",
  "card",
  "number",
  "goals",
  "behavior",
];

function chrome(id: string, surface: DisplaySurface, groups: string[] = []): InventorySlotRecord {
  return slot(id, surface, "chrome", groups, CHROME_OK, CHROME_NO, NONE, {
    inputs_lock: false,
    empty_behavior: "omit",
  });
}

export const INVENTORY_SLOTS: InventorySlotRecord[] = [
  chrome("TF.no_connection", "chrome-shared", ["failure"]),
  chrome("TF.unavailable", "chrome-shared", ["failure"]),
  chrome("SF.next.*", "chrome-shared"),

  chrome("T1-date.eyebrow", "today"),
  slot("T1-date.title", "today", "calc", [], GLOBAL_OK, T1_NO, NONE),
  slot("T1-hero.moon", "today", "calc", ["global_sky"], GLOBAL_OK, T1_NO, NONE),
  chrome("T1-hero.eyebrow", "today", ["day_kind"]),
  slot("T1-hero.energy_word", "today", "calc", ["day_kind"], GLOBAL_OK, T1_NO, MAP),
  slot("T1-hero.energy_pct", "today", "calc", ["day_kind"], GLOBAL_OK, T1_NO, NONE),
  slot("T1-hero.mood", "today", "calc", ["day_kind"], GLOBAL_OK, T1_NO, MAP),
  slot("T1-hero.human_line", "today", "generated", ["day_kind", "global_vs_personal"], GLOBAL_OK, T1_NO, CLIP, {
    budget_chars: 160,
  }),
  slot("T1-hero.sheet", "today", "projected", ["day_kind"], GLOBAL_OK, T1_NO, CLIP, { budget_chars: 320 }),
  chrome("T1-clock.label", "today", ["global_sky"]),
  slot("T1-clock.range", "today", "calc", ["global_sky"], GLOBAL_OK, T1_NO, NONE),
  slot("T1-clock.spectrum", "today", "calc", ["global_sky"], GLOBAL_OK, T1_NO, NONE),
  slot("T1-clock.transit", "today", "calc", ["global_sky"], GLOBAL_OK, T1_NO, CLIP, {
    budget_chars: 120,
    budget_count: 3,
  }),
  slot("T1-clock.sheet", "today", "calc", ["global_sky"], GLOBAL_OK, T1_NO, CLIP),
  chrome("T1-strength.label", "today", ["do_layers"]),
  slot("T1-strength.chip", "today", "calc", ["do_layers"], GLOBAL_OK, T1_NO, MAP, { budget_count: 4 }),
  slot("T1-strength.sheet", "today", "generated", ["do_layers"], GLOBAL_OK, T1_NO, CLIP),
  chrome("T1-risk.label", "today", ["risk_layers"]),
  slot("T1-risk.chip", "today", "calc", ["risk_layers"], GLOBAL_OK, T1_NO, MAP, { budget_count: 3 }),
  slot("T1-risk.sheet", "today", "generated", ["risk_layers"], GLOBAL_OK, T1_NO, CLIP),

  chrome("T2-gate.card_*", "ritual"),
  chrome("T2-gate.number_*", "ritual"),
  slot("T2.card_face", "ritual", "calc", ["symbol_layers"], ["ritual_identity", "catalog"], T1_NO.filter((o) => o !== "ritual_identity"), NONE),
  slot("T2.number_glyph", "ritual", "calc", ["symbol_layers"], ["ritual_identity", "number", "catalog"], T1_NO.filter((o) => o !== "ritual_identity" && o !== "number"), NONE),
  slot("T2.catalog_card", "ritual", "catalog", ["symbol_layers"], ["catalog", "card"], ["personal_day", "ce", "global"], NONE),
  slot("T2.catalog_number", "ritual", "catalog", ["symbol_layers"], ["catalog", "number"], ["personal_day", "ce", "global"], NONE),
  slot("T2.lens_card", "ritual", "generated", ["symbol_layers"], ["personal_day", "card", "catalog"], ["ce", "global"], CLIP_HIDE),
  slot("T2.lens_number", "ritual", "generated", ["symbol_layers"], ["personal_day", "number", "catalog"], ["ce", "global"], CLIP_HIDE),

  chrome("T3.unavailable", "my_day", ["failure"]),
  slot("T3.headline", "my_day", "generated", ["personal_split", "global_vs_personal"], ["personal_day", "natal"], T3_NO, CLIP, {
    budget_chars: 180,
  }),
  chrome("T3.focus_label", "my_day", ["personal_split"]),
  slot("T3.focus_title", "my_day", "projected", ["personal_split"], ["natal", "personal_day"], T3_NO, MAP, {
    budget_chars: 72,
  }),
  slot("T3.focus_body", "my_day", "generated", ["personal_split", "focus_vs_priority"], ["personal_day", "natal"], T3_NO.concat(["ce"]), CLIP, {
    budget_chars: 220,
  }),
  chrome("T3.priority_label", "my_day", ["do_layers"]),
  slot("T3.priority", "my_day", "generated", ["do_layers", "focus_vs_priority", "tasks_not_priority"], ["personal_day"], T3_NO, CLIP, {
    budget_chars: 200,
    budget_count: 3,
  }),
  chrome("T3.caution_label", "my_day", ["risk_layers"]),
  slot("T3.caution", "my_day", "generated", ["risk_layers"], ["personal_day"], T3_NO, CLIP, {
    budget_chars: 180,
    budget_count: 2,
  }),
  chrome("T3.rhythm_label", "my_day"),
  slot("T3.rhythm_row", "my_day", "calc", [], ["personal_day", "natal", "global"], ["ce", "card", "number"], HIDE),
  slot("T3.color.*", "my_day", "catalog", [], ["catalog"], ["ce"], NONE),
  slot("T3.practice", "my_day", "catalog", ["do_layers"], ["catalog", "personal_day"], ["global"], NONE),
  slot("T3.affirmation", "my_day", "generated", ["do_layers"], ["personal_day"], T3_NO, CLIP),
  slot("T3.tracker", "my_day", "user", ["tasks_not_priority"], ["user"], ["personal_day", "global"], NONE),
  chrome("T3.tasks_empty", "my_day", ["tasks_not_priority"]),
  slot("T3.depth", "my_day", "generated", [], ["personal_day"], T3_NO, CLIP_HIDE),

  chrome("T4.title", "evening"),
  chrome("T4.lead", "evening"),
  chrome("T4.category", "evening"),
  slot("T4.text", "evening", "user", [], ["user"], T1_NO, NONE),
  chrome("T4.save_*", "evening"),

  chrome("P-forming.message", "profile"),
  chrome("P-data.cta_text", "profile"),
  chrome("P-data.button", "profile"),
  slot("P1.visual", "profile", "catalog", [], ["catalog", "ce"], ["personal_day"], NONE),
  slot("P1.recognition_name", "profile", "calc", [], CE_OK, ["personal_day", "global"], MAP),
  slot("P1.recognition_line", "profile", "generated", ["path_new_value", "identity_axis"], CE_OK, ["personal_day", "global"], CLIP, {
    budget_chars: 120,
  }),
  chrome("P1.signal", "profile", ["identity_axis"]),
  slot("P1.identity_core", "profile", "generated", ["identity_axis"], CE_OK, ["personal_day"], CLIP),
  chrome("P2.step_title", "profile"),
  chrome("P2.selected_section", "profile", ["why_not_hero"]),
  slot("P2.selected_life_path", "profile", "calc", ["why_not_hero"], ["ce", "product"], ["personal_day"], NONE),
  chrome("P2.influenced_section", "profile", ["why_not_hero"]),
  slot("P2.anchor.sun", "profile", "calc", ["why_not_hero"], ["natal", "ce"], ["personal_day"], NONE),
  slot("P2.anchor.element", "profile", "calc", ["why_not_hero"], ["natal", "ce"], ["personal_day"], NONE),
  slot("P2.anchor.rhythm", "profile", "calc", ["why_not_hero"], ["ce"], ["personal_day"], NONE),
  slot("P2.anchor.moon", "profile", "calc", ["why_not_hero"], ["natal", "ce"], ["personal_day"], NONE),
  slot("P2.anchor.asc", "profile", "calc", ["why_not_hero"], ["natal", "ce"], ["personal_day"], NONE),
  slot("P2.anchor.mc", "profile", "calc", ["why_not_hero"], ["natal", "ce"], ["personal_day"], NONE),
  chrome("P2.honesty_no_time", "profile"),
  chrome("P2.expand_hint", "profile"),
  chrome("P3.step_title", "profile"),
  chrome("P3.eyebrow", "profile"),
  slot("P3.node_title", "profile", "generated", ["node_heading"], CE_OK, ["personal_day"], CLIP),
  slot("P3.insight", "profile", "generated", ["path_new_value", "node_heading", "node_help"], CE_OK, ["personal_day"], CLIP),
  chrome("P3.grounded_label", "profile"),
  slot("P3.grounded_on", "profile", "calc", [], ["natal", "ce"], ["personal_day"], NONE),
  chrome("P3.help_label", "profile", ["node_help"]),
  slot("P3.help", "profile", "generated", ["node_help"], CE_OK, ["personal_day"], CLIP),
  chrome("P3.living_label", "profile"),
  chrome("P3.living_note", "profile"),
  slot("P3.living_evidence", "profile", "user", [], ["user"], ["personal_day"], NONE),
  chrome("P4.step_title", "profile"),
  chrome("P4.lead", "profile"),
  slot("P4.effort_vector", "profile", "projected", ["path_new_value", "effort_not_mission", "bridge_not_effort", "effort_where"], CE_OK, ["personal_day"], CLIP),
  chrome("P4.sphere.title", "profile", ["effort_where"]),
  slot("P4.sphere.teaser", "profile", "generated", ["effort_where"], CE_OK, ["personal_day"], CLIP, { budget_count: 2 }),
  slot("P4.sphere.expand", "profile", "generated", ["effort_where"], CE_OK, ["personal_day"], CLIP),
  chrome("P5.step_title", "profile"),
  slot("P5.bridge_line", "profile", "projected", ["path_new_value", "bridge_not_effort"], CE_OK, ["personal_day"], CLIP),
  chrome("P5.cta", "profile"),
  chrome("P6.title", "explore"),
  slot("P6.wheel", "explore", "calc", ["node_not_warehouse"], ["natal"], ["personal_day"], NONE),
  slot("P6.numbers", "explore", "calc", ["node_not_warehouse"], ["ce"], ["personal_day"], NONE),
  slot("P6.detail", "explore", "generated", ["node_not_warehouse"], CE_OK, ["personal_day"], CLIP),
  slot("P6.style.*", "explore", "generated", ["node_not_warehouse"], CE_OK, ["personal_day"], CLIP),
  slot("P6.natal_decode", "explore", "generated", ["decode"], ["natal", "ce"], ["personal_day"], CLIP_HIDE),
];

const BY_ID = new Map(INVENTORY_SLOTS.map((row) => [row.slot_id, row]));

export function matchInventorySlot(slot_id: string): InventorySlotRecord | undefined {
  const exact = BY_ID.get(slot_id);
  if (exact) return exact;
  for (const row of INVENTORY_SLOTS) {
    const id = row.slot_id;
    if (id.endsWith(".*") && slot_id.startsWith(id.slice(0, -2))) return row;
    if (id.endsWith("_*") && slot_id.startsWith(id.slice(0, -1))) return row;
  }
  return undefined;
}

export function inventorySlotIds(): string[] {
  return INVENTORY_SLOTS.map((row) => row.slot_id);
}

const ALLOWED_CLASSES = new Set<string>(["chrome", "calc", "generated", "projected", "catalog", "user"]);

export function isKnownTextClass(value: string | undefined): boolean {
  return Boolean(value && ALLOWED_CLASSES.has(value));
}
