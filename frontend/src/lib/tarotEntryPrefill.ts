import { consumeGuidanceCompatibilityPrefill } from "@/lib/guidanceCompatibilityPrefill";
import {
  getSpreadOffer,
  type TarotConcernDomain,
} from "@/lib/tarotQuestionFlowCanon";
import type { TarotQuestionSession } from "@/lib/tarotQuestionSession";

const TOPIC_TO_CONCERN: Record<string, TarotConcernDomain> = {
  relationships: "relationships",
  money: "money",
  work: "work",
};

/** Entry prefill from deep links (`?from=compatibility`, `?topic=…`) into question-first session. */
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

  const topic = searchParams.get("topic");
  const concern = topic ? TOPIC_TO_CONCERN[topic] : undefined;
  if (!concern) return session;

  return {
    ...session,
    concernDomain: concern,
    refinementId: null,
    step: "refine",
  };
}
