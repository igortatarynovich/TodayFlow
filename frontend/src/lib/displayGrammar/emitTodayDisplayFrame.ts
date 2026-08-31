/**
 * Live Today projection frame — the same slots production UI paints.
 * Not a new composition. Scanner input only.
 * Canon: DISPLAY_CONSTRUCTION_GRAMMAR_V1 §9 · TODAY_DISPLAY_INVENTORY_V1
 */

import { TODAY_COMPOSITION_COPY as copy } from "@/components/today/composition/todayCompositionCopy";
import { pickRitualPersonalLens } from "@/lib/ritualRevealCopy";
import {
  buildTodayDayBriefModel,
  clipCompassProse,
  type TodayDayBriefModel,
} from "@/lib/todayDayBrief";
import {
  contractHasDeterministicPersonalDayForMyDay,
  contractHasPersistedPersonalDay,
  isTodayInterpretationUnavailable,
  type TodayContractV1,
} from "@/lib/todayContract";
import { omitIfOverlapsHeadline, pickInstructionPersonalBridge } from "@/lib/todayInstructionBridge";
import { pickMyDayPriorityLines } from "@/lib/todayMyDayPriority";
import { pickPersonalFocusAxisLabel } from "@/lib/todayPersonalFocusAxis";
import {
  TODAY_SCREEN_FLOW_CAPABILITY,
  todayAllowsRitualLens,
  type TodayCapabilityDepth,
} from "@/lib/todayScreenFlowCapability";
import { TODAY_UNAVAILABLE_COPY } from "@/lib/todaySlotAvailability";
import type {
  DisplayAtom,
  DisplayScanInput,
  DisplaySurface,
  ExposedVmField,
  FeTransform,
  SemanticOrigin,
  TextClass,
} from "@/lib/displayGrammar/types";

export type TodayRitualHook = {
  bridge_to_day?: string | null;
  personal_angle?: string | null;
  base?: { meaning?: string | null } | null;
} | null | undefined;

export type EmitTodayRitualInput = {
  cardCatalog?: string | null;
  cardHook?: TodayRitualHook;
  numberCatalog?: string | null;
  numberHook?: TodayRitualHook;
  numberGlyph?: string | null;
};

export type EmitTodayDisplayFrameInput = {
  contract: TodayContractV1;
  capability: TodayCapabilityDepth;
  dateLabel?: string;
  headline?: string | null;
  eveningInScroll?: boolean;
  eveningTimeOk?: boolean;
  ritual?: EmitTodayRitualInput;
  gratitudeText?: string | null;
  glancePrioritize?: string | null;
};

function trim(value: unknown): string {
  return String(value ?? "").trim();
}

function pushAtom(
  atoms: DisplayAtom[],
  partial: {
    slot_id: string;
    surface: DisplaySurface;
    text?: string | null;
    origins: SemanticOrigin[];
    text_class: TextClass;
    fe_transform?: FeTransform;
    json_field?: string;
    copy_key?: string;
    transit_kind?: "moon" | "driver";
  },
): void {
  const text = trim(partial.text);
  if (!text) return;
  atoms.push({
    slot_id: partial.slot_id,
    surface: partial.surface,
    text,
    origins: partial.origins,
    text_class: partial.text_class,
    fe_transform: partial.fe_transform ?? "none",
    json_field: partial.json_field,
    copy_key: partial.copy_key,
    transit_kind: partial.transit_kind,
  });
}

function vm(
  fields: ExposedVmField[],
  field: string,
  value: unknown,
  slot_id?: string,
  would_render?: boolean,
): void {
  const filled = Array.isArray(value)
    ? value.length > 0
    : value != null && trim(value) !== "" && value !== false;
  fields.push({
    field,
    filled,
    slot_id,
    would_render: would_render ?? Boolean(filled && slot_id),
  });
}

function emitTodaySurface(model: TodayDayBriefModel, atoms: DisplayAtom[]): string | null {
  pushAtom(atoms, {
    slot_id: "T1-date.title",
    surface: "today",
    text: model.dateLabel,
    origins: ["global"],
    text_class: "calc",
  });

  const energyWord = model.modeLabel;
  const humanLine = clipCompassProse(model.atmosphereLine ?? model.vibe ?? model.expect, 160);
  if (energyWord) {
    pushAtom(atoms, {
      slot_id: "T1-hero.energy_word",
      surface: "today",
      text: energyWord,
      origins: ["global"],
      text_class: "calc",
      fe_transform: "map_label",
      json_field: "global_day.primary_energy",
    });
  } else {
    pushAtom(atoms, {
      slot_id: "T1-date.eyebrow",
      surface: "today",
      text: "Сегодня",
      origins: ["chrome"],
      text_class: "chrome",
      copy_key: "dateEyebrow",
    });
  }

  pushAtom(atoms, {
    slot_id: "T1-hero.human_line",
    surface: "today",
    text: humanLine,
    origins: ["global"],
    text_class: "generated",
    fe_transform: "clip",
    json_field: model.atmosphereLine ? "global_context.period" : "day_story.expect",
  });

  const sheetBits = [model.atmosphereNote, model.energyCause].map(trim).filter(Boolean);
  if (model.expect && humanLine && trim(model.expect) !== humanLine) {
    sheetBits.unshift(trim(model.expect));
  }
  const sheet = sheetBits.join("\n\n");
  if (sheet && trim(sheet) !== humanLine) {
    pushAtom(atoms, {
      slot_id: "T1-hero.sheet",
      surface: "today",
      text: clipCompassProse(sheet, 320) || sheet,
      origins: ["global"],
      text_class: "projected",
      fe_transform: "clip",
    });
  }

  if (typeof model.moonPhase === "number" && Number.isFinite(model.moonPhase)) {
    pushAtom(atoms, {
      slot_id: "T1-hero.moon",
      surface: "today",
      text: String(model.moonPhase),
      origins: ["global"],
      text_class: "calc",
    });
  }

  if (model.energyPct != null) {
    pushAtom(atoms, {
      slot_id: "T1-hero.energy_pct",
      surface: "today",
      text: `${model.energyPct}%`,
      origins: ["global"],
      text_class: "calc",
      json_field: "global_day.energy_scores",
    });
  }

  // Mood only when distinct from energy_word (Inventory: no substitution).
  if (model.modeLabel && energyWord && model.modeLabel !== energyWord) {
    pushAtom(atoms, {
      slot_id: "T1-hero.mood",
      surface: "today",
      text: model.modeLabel,
      origins: ["global"],
      text_class: "calc",
      fe_transform: "map_label",
    });
  }

  if (model.dayWindow?.start && model.dayWindow?.end) {
    pushAtom(atoms, {
      slot_id: "T1-clock.range",
      surface: "today",
      text: `${model.dayWindow.start}–${model.dayWindow.end}`,
      origins: ["global"],
      text_class: "calc",
      json_field: "global_day.windows",
    });
  }

  for (const row of model.transits ?? []) {
    const isMoon = row.id === "moon";
    pushAtom(atoms, {
      slot_id: "T1-clock.transit",
      surface: "today",
      text: row.title,
      origins: ["global"],
      text_class: "calc",
      fe_transform: "clip",
      json_field: isMoon ? undefined : "global_day.drivers",
      transit_kind: isMoon ? "moon" : "driver",
    });
  }

  for (const chip of model.strengthChips ?? []) {
    pushAtom(atoms, {
      slot_id: "T1-strength.chip",
      surface: "today",
      text: chip.label,
      origins: ["global"],
      text_class: "calc",
      fe_transform: "map_label",
      json_field: "global_day.strength",
    });
  }
  for (const chip of model.riskChips ?? []) {
    pushAtom(atoms, {
      slot_id: "T1-risk.chip",
      surface: "today",
      text: chip.label,
      origins: ["global"],
      text_class: "calc",
      fe_transform: "map_label",
      json_field: "global_day.risk",
    });
  }

  return humanLine;
}

function emitRitual(
  input: EmitTodayDisplayFrameInput,
  atoms: DisplayAtom[],
): { cardLens: string | null; numberLens: string | null } {
  const allowLens = todayAllowsRitualLens(input.capability, input.contract);
  const ritual = input.ritual;
  const cardCatalog =
    trim(ritual?.cardCatalog) || trim(ritual?.cardHook?.base?.meaning) || null;
  const numberCatalog =
    trim(ritual?.numberCatalog) || trim(ritual?.numberHook?.base?.meaning) || null;
  const cardLens = pickRitualPersonalLens(ritual?.cardHook, allowLens);
  const numberLens = pickRitualPersonalLens(ritual?.numberHook, allowLens);

  pushAtom(atoms, {
    slot_id: "T2.catalog_card",
    surface: "ritual",
    text: cardCatalog,
    origins: ["catalog"],
    text_class: "catalog",
    json_field: "ritual.card.catalog",
  });
  pushAtom(atoms, {
    slot_id: "T2.catalog_number",
    surface: "ritual",
    text: numberCatalog,
    origins: ["catalog"],
    text_class: "catalog",
    json_field: "ritual.number.catalog",
  });
  if (trim(ritual?.numberGlyph)) {
    pushAtom(atoms, {
      slot_id: "T2.number_glyph",
      surface: "ritual",
      text: ritual?.numberGlyph,
      origins: ["ritual_identity"],
      text_class: "calc",
    });
  }
  pushAtom(atoms, {
    slot_id: "T2.lens_card",
    surface: "ritual",
    text: cardLens,
    origins: ["personal_day", "card"],
    text_class: "generated",
    fe_transform: "clip",
    json_field: "ritual.card.lens",
  });
  pushAtom(atoms, {
    slot_id: "T2.lens_number",
    surface: "ritual",
    text: numberLens,
    origins: ["personal_day", "number"],
    text_class: "generated",
    fe_transform: "clip",
    json_field: "ritual.number.lens",
  });
  return { cardLens, numberLens };
}

function emitMyDay(
  input: EmitTodayDisplayFrameInput,
  model: TodayDayBriefModel,
  atoms: DisplayAtom[],
): {
  headline: string | null;
  focusTitle: string | null;
  focusBody: string | null;
  priorities: string[];
} {
  const showMyDay = TODAY_SCREEN_FLOW_CAPABILITY[input.capability].myDay;
  if (!showMyDay) {
    return { headline: null, focusTitle: null, focusBody: null, priorities: [] };
  }

  const unavailable =
    isTodayInterpretationUnavailable(input.contract) &&
    !contractHasDeterministicPersonalDayForMyDay(input.contract);
  if (unavailable) {
    pushAtom(atoms, {
      slot_id: "T3.unavailable",
      surface: "my_day",
      text: TODAY_UNAVAILABLE_COPY,
      origins: ["chrome"],
      text_class: "chrome",
      copy_key: "unavailable",
    });
    return { headline: null, focusTitle: null, focusBody: null, priorities: [] };
  }

  const headline = model.personalLine;
  const focusTitle = pickPersonalFocusAxisLabel(input.contract);
  const focusBody = omitIfOverlapsHeadline(
    pickInstructionPersonalBridge(input.contract),
    headline,
  );
  const priorities = pickMyDayPriorityLines({
    contract: input.contract,
    doItems: model.doItems,
    glancePrioritize: input.glancePrioritize,
  });
  const cautions = model.avoidItems
    .filter((line) => !priorities.includes(line))
    .slice(0, 2);

  pushAtom(atoms, {
    slot_id: "T3.headline",
    surface: "my_day",
    text: headline,
    origins: ["personal_day"],
    text_class: "generated",
    fe_transform: "clip",
    json_field: "day_story.day_personal.summary_ru",
  });
  if (focusTitle || focusBody) {
    pushAtom(atoms, {
      slot_id: "T3.focus_label",
      surface: "my_day",
      text: copy.myDayFocusLabel,
      origins: ["chrome"],
      text_class: "chrome",
      copy_key: "myDayFocusLabel",
    });
  }
  pushAtom(atoms, {
    slot_id: "T3.focus_title",
    surface: "my_day",
    text: focusTitle,
    origins: ["natal"],
    text_class: "projected",
    fe_transform: "map_label",
    json_field: "personal_day.natal_overlay",
  });
  pushAtom(atoms, {
    slot_id: "T3.focus_body",
    surface: "my_day",
    text: focusBody,
    origins: ["personal_day"],
    text_class: "generated",
    fe_transform: "clip",
    json_field: "day_story.day_scenario.conflict.why_personal",
  });
  if (priorities.length) {
    pushAtom(atoms, {
      slot_id: "T3.priority_label",
      surface: "my_day",
      text: copy.myDayPriorityLabel,
      origins: ["chrome"],
      text_class: "chrome",
      copy_key: "myDayPriorityLabel",
    });
  }
  for (const line of priorities) {
    pushAtom(atoms, {
      slot_id: "T3.priority",
      surface: "my_day",
      text: line,
      origins: ["personal_day"],
      text_class: "generated",
      fe_transform: "clip",
      json_field: "day_story.do",
    });
  }
  if (cautions.length) {
    pushAtom(atoms, {
      slot_id: "T3.caution_label",
      surface: "my_day",
      text: copy.myDayCautionLabel,
      origins: ["chrome"],
      text_class: "chrome",
      copy_key: "myDayCautionLabel",
    });
  }
  for (const line of cautions) {
    pushAtom(atoms, {
      slot_id: "T3.caution",
      surface: "my_day",
      text: line,
      origins: ["personal_day"],
      text_class: "generated",
      fe_transform: "clip",
      json_field: "day_story.avoid",
    });
  }

  return { headline, focusTitle, focusBody, priorities };
}

function emitEvening(input: EmitTodayDisplayFrameInput, atoms: DisplayAtom[]): void {
  if (!input.eveningInScroll) return;
  pushAtom(atoms, {
    slot_id: "T4.title",
    surface: "evening",
    text: copy.eveningGratitudeTitle,
    origins: ["chrome"],
    text_class: "chrome",
    copy_key: "eveningGratitudeTitle",
  });
  pushAtom(atoms, {
    slot_id: "T4.text",
    surface: "evening",
    text: input.gratitudeText,
    origins: ["user"],
    text_class: "user",
    json_field: "gratitude.text",
  });
}

/**
 * Project the production Today path into a Grammar §9 scan frame.
 * Calls the same pickers the UI uses. Does not invent meaning.
 */
export function emitTodayDisplayFrame(input: EmitTodayDisplayFrameInput): DisplayScanInput {
  const persisted = contractHasPersistedPersonalDay(input.contract);
  const model = buildTodayDayBriefModel({
    contract: input.contract,
    dateLabel: input.dateLabel || "сегодня",
    salutation: "",
    headline: input.headline,
  });

  const atoms: DisplayAtom[] = [];
  const vm_fields: ExposedVmField[] = [];

  const humanLine = emitTodaySurface(model, atoms);
  const { cardLens, numberLens } = emitRitual(input, atoms);
  const myDay = emitMyDay(input, model, atoms);
  emitEvening(input, atoms);

  vm(vm_fields, "global_context.period", input.contract.global_context?.period, "T1-hero.human_line", Boolean(humanLine));
  vm(vm_fields, "global_day.primary_energy", input.contract.global_day?.primary_energy, "T1-hero.energy_word", Boolean(model.modeLabel));
  vm(vm_fields, "day_story.day_personal.summary_ru", input.contract.day_story?.day_personal?.summary_ru, "T3.headline", Boolean(myDay.headline));
  vm(
    vm_fields,
    "day_story.day_scenario.conflict.why_personal",
    input.contract.day_story?.day_scenario?.conflict?.why_personal,
    "T3.focus_body",
    Boolean(myDay.focusBody),
  );
  vm(vm_fields, "personal_day.natal_overlay", input.contract.personal_day?.natal_overlay, "T3.focus_title", Boolean(myDay.focusTitle));
  vm(vm_fields, "day_story.do", input.contract.day_story?.do, "T3.priority", myDay.priorities.length > 0);
  vm(vm_fields, "personal_growth.development_point", input.contract.personal_growth?.development_point, undefined, false);
  vm(vm_fields, "primary_action", input.contract.primary_action, undefined, false);

  const showMyDay = TODAY_SCREEN_FLOW_CAPABILITY[input.capability].myDay;
  const todaySentence = Boolean(model.modeLabel || humanLine);
  const myDaySentence = Boolean(myDay.headline);
  const ritualSentence = Boolean(trim(input.ritual?.cardCatalog) || trim(input.ritual?.numberCatalog) || trim(input.ritual?.cardHook?.base?.meaning));

  let journey: DisplayScanInput["journey"];
  if (showMyDay && (myDaySentence || isTodayInterpretationUnavailable(input.contract))) {
    journey = { surface: "my_day", can_finish_sentence: myDaySentence || isTodayInterpretationUnavailable(input.contract) };
  } else if (ritualSentence && !todaySentence) {
    journey = { surface: "ritual", can_finish_sentence: true };
  } else {
    journey = { surface: "today", can_finish_sentence: todaySentence };
  }

  return {
    atoms,
    vm_fields,
    capability: input.capability,
    personal_day_persisted: persisted,
    evening_in_scroll: Boolean(input.eveningInScroll),
    evening_time_ok: input.eveningTimeOk,
    journey,
    today_lock: {
      lensText: cardLens || numberLens,
      headline: myDay.headline,
      focusTitle: myDay.focusTitle,
      primaryAction: input.contract.primary_action,
      priorities: myDay.priorities,
      emptyTasksChrome: false,
      inventedTexts: [humanLine, myDay.headline, myDay.focusBody, ...myDay.priorities],
    },
  };
}
