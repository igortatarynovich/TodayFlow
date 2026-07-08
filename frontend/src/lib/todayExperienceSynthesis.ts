import type { TodayContractV1 } from "@/lib/todayContract";
import { buildTodayUnifiedSynthesis, type TodayUnifiedSynthesis } from "@/lib/todayUnifiedSynthesis";

/** @deprecated Use TodayUnifiedSynthesis — kept for component prop typing */
export type TodaySynthesisModel = TodayUnifiedSynthesis;

export function buildTodaySynthesisModel({
  contract,
  guidePayload,
  tarotMainId,
  numerologyValue,
  numerologyMeaning,
  personalObservation,
  mood,
  dateISO,
  eyebrow,
}: {
  contract: TodayContractV1;
  guidePayload: Record<string, unknown> | null;
  tarotMainId: number | null;
  numerologyValue: string;
  numerologyMeaning: string;
  personalObservation?: string | null;
  mood?: string | null;
  dateISO: string;
  eyebrow: string;
}): TodayUnifiedSynthesis {
  return buildTodayUnifiedSynthesis({
    contract,
    guidePayload,
    tarotMainId,
    numerologyValue,
    numerologyMeaning,
    personalObservation,
    mood,
    dateISO,
    eyebrow,
  });
}
