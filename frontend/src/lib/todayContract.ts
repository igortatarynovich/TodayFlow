import { getJson, postJson } from "@/lib/api";
import { buildFirstTodayPackage } from "@/lib/firstTodayPackage";
import { readOnboardingContext } from "@/lib/onboardingContext";
import type { CoreProfile } from "@/lib/types";

export const TODAY_CONTRACT_V1 = "today_contract_v1";

export type DomainLensV1 = {
  status: string;
  opportunity: string;
  risk: string;
  action: string;
};

export type TodayContractDomainsV1 = {
  relationships: DomainLensV1;
  money_work: DomainLensV1;
  family: DomainLensV1;
};

export type TodayContractDayStoryV1 = {
  contract_version: string;
  theme?: string;
  direction?: string;
  story?: string;
  do?: string[];
  avoid?: string[];
  advantage?: string;
  abstain?: string;
  today_move?: string;
  talisman?: { color?: string; stone?: string; note?: string };
  practice_recommendation?: { kind?: string; text?: string; reason?: string };
  symbolic_note?: string;
};

export type TodayContractV1 = {
  contract_version: typeof TODAY_CONTRACT_V1 | string;
  global_context: { period: string };
  personal_growth: { development_point: string };
  domains: TodayContractDomainsV1;
  primary_action: string;
  progress: Record<string, unknown>;
  generation_id: string;
  day_story?: TodayContractDayStoryV1 | null;
};

export type TodayContractDomainId = keyof TodayContractDomainsV1;

function contractFromFirstTodayPackage(
  pkg: ReturnType<typeof buildFirstTodayPackage>,
): TodayContractV1 {
  const [rel, money, family] = pkg.insight.spheres;
  const lens = (line: string) => ({
    status: "",
    opportunity: line,
    risk: "",
    action: line,
  });

  return {
    contract_version: TODAY_CONTRACT_V1,
    global_context: { period: pkg.theme.headline },
    personal_growth: { development_point: pkg.why.lines[0] || "Один честный шаг сегодня." },
    domains: {
      relationships: lens(rel.line),
      money_work: lens(money.line),
      family: lens(family.line),
    },
    primary_action: pkg.action.primary,
    progress: {},
    generation_id: "fallback-today-contract-v1",
  };
}

/** Deterministic contract when `/today/contract` is unavailable (offline, LLM quota, etc.). */
export function buildFallbackTodayContract(input: {
  coreProfile?: CoreProfile | null;
} = {}): TodayContractV1 {
  const ctx = readOnboardingContext();
  const pkg = buildFirstTodayPackage({
    coreProfile: input.coreProfile ?? null,
    intentTheme: ctx.intent_theme,
    realityState: ctx.reality_state,
  });
  return contractFromFirstTodayPackage(pkg);
}

export function isTodayContractFallback(contract: TodayContractV1 | null | undefined): boolean {
  return (contract?.generation_id || "").trim() === "fallback-today-contract-v1";
}

export async function fetchTodayContractV1(targetDate?: string): Promise<TodayContractV1> {
  const qs = targetDate ? `?target_date=${encodeURIComponent(targetDate)}` : "";
  return getJson<TodayContractV1>(`/today/contract${qs}`);
}

export type TodayStoryRefreshResult = {
  rebuilt: boolean;
  story_status: string;
  story_refresh_required: boolean;
  story_fingerprint?: string | null;
  generation_id?: string;
  contract?: TodayContractV1 | null;
  error?: string | null;
};

/** Rebuild day_story when fingerprint is stale after reveal/mood/goals. */
export async function refreshTodayStory(input?: {
  localDate?: string;
  timezone?: string;
  force?: boolean;
}): Promise<TodayStoryRefreshResult> {
  let timezone = input?.timezone;
  if (!timezone) {
    try {
      timezone = Intl.DateTimeFormat().resolvedOptions().timeZone || "UTC";
    } catch {
      timezone = "UTC";
    }
  }
  return postJson<TodayStoryRefreshResult>("/today/story/refresh", {
    local_date: input?.localDate,
    timezone,
    force: Boolean(input?.force),
  });
}

export function isTodayStoryStale(contract: TodayContractV1 | null | undefined): boolean {
  const p = contract?.progress || {};
  return p.story_refresh_required === true || p.story_status === "stale";
}
