import type { TarotConcernDomain } from "@/lib/tarotQuestionFlowCanon";

export function tarotFlowEventKey(sessionId: string, suffix: string): string {
  return `tarot-flow:${sessionId}:${suffix}`;
}

export type TarotFlowTrackInput = {
  sessionId: string;
  concernDomain?: TarotConcernDomain | null;
  refinementId?: string | null;
  questionText?: string | null;
  spreadId?: string | null;
};
