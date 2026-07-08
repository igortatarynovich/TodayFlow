import type { TodayContractV1 } from "@/lib/todayContract";
import type { DayQuestionCard } from "@/components/today/todayPageUtils";
import { buildTodayNarrativeV1 } from "@/lib/todayNarrativeFromContract";
import { isRuUserFacingText } from "@/lib/todaySynthesisTextPolicy";

export type TodaySemanticBlocks = {
  manifestations: string[];
  question: DayQuestionCard | null;
};

export function buildTodaySemanticBlocks({
  contract,
  questionOfDay,
  synthesisParagraphs = [],
}: {
  contract: TodayContractV1;
  questionOfDay: DayQuestionCard | null;
  synthesisParagraphs?: string[];
}): TodaySemanticBlocks {
  const narrative = buildTodayNarrativeV1(contract);
  const synthLow = synthesisParagraphs.map((p) => p.toLowerCase()).join(" ");

  const manifestations = narrative.manifestations
    .map((m) => m.line.trim())
    .filter((line) => {
      if (!isRuUserFacingText(line)) return false;
      const snippet = line.toLowerCase().slice(0, 36);
      return !synthLow.includes(snippet);
    });

  return {
    manifestations,
    question: questionOfDay,
  };
}
