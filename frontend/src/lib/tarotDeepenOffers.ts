/**
 * Signed-in Tarot advantage: pick a deepen topic → same question-first flow
 * (no new pipeline). Canon: Editorial Phase — UI + prefill reuse.
 */

import type { TarotConcernDomain } from "@/lib/tarotQuestionFlowCanon";

export type TarotDeepenOffer = {
  id: string;
  label: string;
  hint: string;
  concernDomain: TarotConcernDomain;
  refinementId: string;
  questionSeed: string;
};

const OFFERS: TarotDeepenOffer[] = [
  {
    id: "money_practical",
    label: "Деньги · практический шаг",
    hint: "Один конкретный ход на этой неделе",
    concernDomain: "money",
    refinementId: "practical_week",
    questionSeed: "Какой один практический шаг по деньгам стоит сделать на этой неделе?",
  },
  {
    id: "intimacy_practical",
    label: "Близость и секс",
    hint: "Тепло, тело, без стыда и давления",
    concernDomain: "relationships",
    refinementId: "intimacy_sex",
    questionSeed: "Какие практические шаги помогут близости и сексуальной жизни без давления и стыда?",
  },
  {
    id: "work_direction",
    label: "Работа · направление",
    hint: "Куда вложить внимание",
    concernDomain: "work",
    refinementId: "direction",
    questionSeed: "Какое направление в работе сейчас заслуживает внимания?",
  },
  {
    id: "self_boundaries",
    label: "Я и границы",
    hint: "Где беречь себя",
    concernDomain: "inner_state",
    refinementId: "overwhelm",
    questionSeed: "Где мне сейчас нужны более ясные границы — и какой один шаг это укрепит?",
  },
];

/** Prefer adjacent topics, keep 3–4 choices, always include money + intimacy when relevant. */
export function pickTarotDeepenOffers(
  concernDomain: string | null | undefined,
  options?: { limit?: number },
): TarotDeepenOffer[] {
  const limit = options?.limit ?? 4;
  const domain = String(concernDomain || "").toLowerCase();
  const preferredIds: string[] = [];
  if (domain === "money" || domain === "work") {
    preferredIds.push("money_practical", "work_direction", "intimacy_practical", "self_boundaries");
  } else if (domain === "relationships" || domain === "love" || domain === "family") {
    preferredIds.push("intimacy_practical", "self_boundaries", "money_practical", "work_direction");
  } else if (domain === "inner_state" || domain === "growth") {
    preferredIds.push("self_boundaries", "intimacy_practical", "money_practical", "work_direction");
  } else {
    preferredIds.push("money_practical", "intimacy_practical", "work_direction", "self_boundaries");
  }

  const byId = new Map(OFFERS.map((o) => [o.id, o]));
  const out: TarotDeepenOffer[] = [];
  for (const id of preferredIds) {
    const offer = byId.get(id);
    if (offer && !out.some((x) => x.id === offer.id)) out.push(offer);
    if (out.length >= limit) break;
  }
  return out;
}

export function buildTarotDeepenHref(offer: TarotDeepenOffer): string {
  const params = new URLSearchParams({
    concern: offer.concernDomain,
    refine: offer.refinementId,
    question: offer.questionSeed,
    source: "deepen",
  });
  return `/tarot?${params.toString()}`;
}
