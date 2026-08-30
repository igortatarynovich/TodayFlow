/**
 * Grammar §9 scanner types.
 * Inventory markdown remains SoT. This is the audit shape, not meaning SoT.
 * Canon: docs/foundation/DISPLAY_CONSTRUCTION_GRAMMAR_V1.md §9
 */

export type GrammarFindingId =
  | 1
  | 2
  | 3
  | 4
  | 5
  | 6
  | 7
  | 8
  | 9
  | 10
  | 11
  | 12
  | 13
  | 14
  | 15
  | 16
  | 17
  | 18
  | 19;

export type DisplaySurface =
  | "profile"
  | "today"
  | "ritual"
  | "my_day"
  | "evening"
  | "explore"
  | "chrome-shared";

export type TextClass = "chrome" | "calc" | "generated" | "projected" | "catalog" | "user";

export type SemanticOrigin =
  | "global"
  | "personal_day"
  | "natal"
  | "ce"
  | "ritual_identity"
  | "card"
  | "number"
  | "goals"
  | "behavior"
  | "catalog"
  | "user"
  | "chrome"
  | "product";

export type FeTransform =
  | "none"
  | "clip"
  | "map_label"
  | "hide_by_gate"
  | "invent"
  | "paraphrase"
  | "fill_empty"
  | "other";

export type InventorySlotRecord = {
  slot_id: string;
  surface: DisplaySurface;
  text_class: TextClass;
  anti_dupe_groups: string[];
  allowed_origins: SemanticOrigin[];
  forbidden_origins: SemanticOrigin[];
  may_fe_transform: FeTransform[];
  budget_chars?: number;
  budget_count?: number;
  empty_behavior: "omit" | "show_chrome" | "conditional";
  /** Finding 14 — generated/projected slots must declare inputs lock. */
  inputs_lock: boolean;
};

export type DisplayAtom = {
  slot_id?: string;
  surface: DisplaySurface;
  text?: string | null;
  text_class?: string;
  origins: SemanticOrigin[];
  json_field?: string;
  copy_key?: string;
  fe_transform?: FeTransform;
  /** Filled empty payload with neighbor/canned — finding 7. */
  empty_filled?: boolean;
  /** generated/projected without allowed_inputs+forbidden declared — finding 14. */
  inputs_lock?: boolean;
  transit_kind?: "moon" | "driver";
};

export type ExposedVmField = {
  field: string;
  filled: boolean;
  /** If set, this field is allowed to render as that slot. */
  slot_id?: string;
  /** True when UI would paint this field. Legacy JSON may exist without this. */
  would_render?: boolean;
};

export type DisplayScanInput = {
  atoms?: DisplayAtom[];
  vm_fields?: ExposedVmField[];
  capability?: "guest" | "general" | "light" | "deep";
  evening_in_scroll?: boolean;
  evening_time_ok?: boolean;
  personal_day_persisted?: boolean;
  journey?: { surface: DisplaySurface; can_finish_sentence: boolean };
  /** Regression payload for findings 7 / 12 / 15 / 17 / 18. */
  today_lock?: {
    lensText?: string | null;
    headline?: string | null;
    focusTitle?: string | null;
    primaryAction?: string | null;
    priorities?: string[];
    emptyTasksChrome?: boolean;
    developmentPoint?: string | null;
    inventedTexts?: Array<string | null | undefined>;
  };
};

export type DisplayGrammarFinding = {
  grammar: GrammarFindingId;
  code: string;
  slot_id?: string;
  detail?: string;
};
