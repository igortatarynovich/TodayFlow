import type { TodayContractV1 } from "@/lib/todayContract";
import { TODAY_NO_CONNECTION_COPY } from "@/lib/todaySlotAvailability";

export const TODAY_CONTRACT_FALLBACK_GENERATION_ID = "fallback-today-contract-v1";

export function isTodayContractFallback(contract: TodayContractV1 | null | undefined): boolean {
  return (contract?.generation_id || "").trim() === TODAY_CONTRACT_FALLBACK_GENERATION_ID;
}

/** Показываем только при сбое сети/API — не при LLM-fallback на сервере. */
export function shouldShowTodayServiceUnavailableNotice(input: {
  contract: TodayContractV1 | null | undefined;
  narrativeRequestFailed?: boolean;
}): boolean {
  return isTodayContractFallback(input.contract) || Boolean(input.narrativeRequestFailed);
}

/** Honest transport failure — never invent day/sphere content in its place. */
export const TODAY_SERVICE_UNAVAILABLE_MESSAGE = TODAY_NO_CONNECTION_COPY;
