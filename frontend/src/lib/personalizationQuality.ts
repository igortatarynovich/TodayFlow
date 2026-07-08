import type { TodayContractV1 } from "@/lib/todayContract";

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

export const TODAY_SERVICE_UNAVAILABLE_MESSAGE =
  "Сейчас нет связи с сервером — сервис недоступен. Ниже то, что можно посмотреть без подключения.";
