import { consumeGuidanceCompatibilityPrefill } from "@/lib/guidanceCompatibilityPrefill";
import {
  getSpreadOffer,
  TAROT_REFINEMENTS,
  type TarotConcernDomain,
} from "@/lib/tarotQuestionFlowCanon";
import type { TarotQuestionSession } from "@/lib/tarotQuestionSession";

const TOPIC_TO_CONCERN: Record<string, TarotConcernDomain> = {
  relationships: "relationships",
  money: "money",
  work: "work",
  family: "family",
  growth: "growth",
  decision: "decision",
  conflict: "conflict",
  inner_state: "inner_state",
  other: "other",
};

const CONCERN_IDS = new Set<string>(Object.keys(TOPIC_TO_CONCERN));

/** Entry prefill from deep links (`?from=compatibility`, `?topic=…`, deepen) into question-first session. */
export function applyTarotEntryPrefill(
  session: TarotQuestionSession,
  searchParams: URLSearchParams | null,
): TarotQuestionSession {
  if (!searchParams) return session;

  if (searchParams.get("from") === "compatibility") {
    const stored = consumeGuidanceCompatibilityPrefill();
    if (!stored) return session;
    const spreadId =
      stored.spread_id && getSpreadOffer(stored.spread_id)
        ? stored.spread_id
        : session.spreadId;
    return {
      ...session,
      concernDomain: "relationships",
      customQuestion: stored.suggested_question,
      spreadId,
      refinementId: null,
      step: "spread",
    };
  }

  const concernRaw = (searchParams.get("concern") || searchParams.get("topic") || "").trim();
  const concern = CONCERN_IDS.has(concernRaw) ? (concernRaw as TarotConcernDomain) : undefined;
  if (!concern) return session;

  const refineRaw = (searchParams.get("refine") || "").trim();
  const refineOk =
    Boolean(refineRaw) &&
    (TAROT_REFINEMENTS[concern] || []).some((r) => r.id === refineRaw);
  const question = (searchParams.get("question") || "").trim();
  const fromDeepen = searchParams.get("source") === "deepen";

  // Signed-in deepen: skip to spread with a ready question when possible.
  if (fromDeepen && question) {
    return {
      ...session,
      concernDomain: concern,
      refinementId: refineOk ? refineRaw : null,
      customQuestion: question,
      spreadId: null,
      step: "spread",
    };
  }

  return {
    ...session,
    concernDomain: concern,
    refinementId: refineOk ? refineRaw : null,
    customQuestion: question || session.customQuestion,
    step: refineOk || concern === "other" ? "spread" : "refine",
  };
}
