/** Post-ritual proximity choice — learning signal without test-like UX. */

export type InterpretationResonance = "yes" | "partial" | "no";

export type InterpretationConfirmTarget = "tarot_impact" | "number_impact" | "day_pulse";

export type ProximityChoiceId =
  | "wait"
  | "see_differently"
  | "first_step"
  | "unsure"
  | "pause"
  | "move"
  | "both"
  | "clarity"
  | "patience";

export const TAROT_PROXIMITY_OPTIONS: Array<{
  choiceId: ProximityChoiceId;
  resonance: InterpretationResonance;
  label: string;
}> = [
  { choiceId: "wait", resonance: "partial", label: "Подождать" },
  { choiceId: "see_differently", resonance: "yes", label: "Посмотреть иначе" },
  { choiceId: "first_step", resonance: "yes", label: "Сделать первый шаг" },
  { choiceId: "unsure", resonance: "no", label: "Пока не понимаю" },
];

export const NUMBER_PROXIMITY_OPTIONS: Array<{
  choiceId: ProximityChoiceId;
  resonance: InterpretationResonance;
  label: string;
}> = [
  { choiceId: "wait", resonance: "partial", label: "Дать дню время" },
  { choiceId: "see_differently", resonance: "yes", label: "Замечаю закономерность" },
  { choiceId: "first_step", resonance: "yes", label: "Готов действовать" },
  { choiceId: "unsure", resonance: "no", label: "Пока не понимаю" },
];

export const DAY_PULSE_PROXIMITY_OPTIONS: Array<{
  choiceId: ProximityChoiceId;
  resonance: InterpretationResonance;
  label: string;
}> = [
  { choiceId: "pause", resonance: "partial", label: "Скорее про паузу" },
  { choiceId: "move", resonance: "yes", label: "Скорее про движение" },
  { choiceId: "both", resonance: "partial", label: "И то, и другое" },
  { choiceId: "unsure", resonance: "no", label: "Пока не ясно" },
];

/** @deprecated kept for tests — use interpretationProximityQuestion */
export const INTERPRETATION_RESONANCE_OPTIONS = TAROT_PROXIMITY_OPTIONS.map((o) => ({
  id: o.resonance,
  label: o.label,
}));

export function interpretationProximityQuestion(_target: InterpretationConfirmTarget): string {
  return "Что сейчас ближе?";
}

/** @deprecated */
export function interpretationConfirmQuestion(target: InterpretationConfirmTarget): string {
  return interpretationProximityQuestion(target);
}

export function proximityOptionsForTarget(target: InterpretationConfirmTarget) {
  if (target === "number_impact") return NUMBER_PROXIMITY_OPTIONS;
  if (target === "day_pulse") return DAY_PULSE_PROXIMITY_OPTIONS;
  return TAROT_PROXIMITY_OPTIONS;
}

export function buildInterpretationConfirmPayload(input: {
  target: InterpretationConfirmTarget;
  resonance: InterpretationResonance;
  choiceId?: ProximityChoiceId;
  surface?: string;
  headline?: string | null;
}) {
  return {
    surface: input.surface ?? "today_day_story_v3",
    target: input.target,
    echo: input.resonance,
    proximity_choice: input.choiceId ?? null,
    interpretation_confirm: true,
    headline_preview: input.headline?.slice(0, 120) ?? null,
  };
}
