import type { JTBDLane, QuestionsHubContextResponse } from "@/lib/types";

export type AdaptiveQuestionSurface = {
  title?: string;
  body?: string;
  placeholder?: string;
  quickPrompts?: readonly string[];
  scenarios?: readonly string[];
};

export function findLaneSuggestion(
  hubContext: QuestionsHubContextResponse | null,
  lane: JTBDLane,
) {
  return hubContext?.lane_suggestions?.find((item) => item.lane === lane) || null;
}

export function buildAdaptiveQuestionSurface(
  lane: JTBDLane,
  base: AdaptiveQuestionSurface,
  hubContext: QuestionsHubContextResponse | null,
): AdaptiveQuestionSurface {
  const suggestion = findLaneSuggestion(hubContext, lane);
  if (!suggestion) {
    return base;
  }

  const adaptive: AdaptiveQuestionSurface = { ...base };
  const lastQuestion = suggestion.last_question?.trim();
  const lastThesis = suggestion.last_thesis?.trim();
  const focusHint = suggestion.focus_hint?.trim();

  if (focusHint && base.body) {
    adaptive.body = `${base.body} ${focusHint}`;
  }

  if (lastQuestion && base.title) {
    adaptive.title = `${base.title} Сейчас здесь уже есть живая линия.`;
  }

  if (lastQuestion && lastQuestion.length > 12) {
    adaptive.placeholder = lastQuestion;
  }

  if (base.quickPrompts?.length) {
    const prompts = [...base.quickPrompts];
    if (lastQuestion && !prompts.includes(lastQuestion)) {
      prompts.unshift(lastQuestion);
    }
    adaptive.quickPrompts = prompts.slice(0, 4);
  }

  if (base.scenarios?.length) {
    const scenarios = [...base.scenarios];
    if (lastThesis && !scenarios.includes(lastThesis)) {
      scenarios.unshift(lastThesis);
    }
    adaptive.scenarios = scenarios.slice(0, 4);
  }

  return adaptive;
}
