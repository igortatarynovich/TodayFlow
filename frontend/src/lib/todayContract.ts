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
  /** PR-3: absent = no personal signal; do not treat empty copy as a domain claim. */
  evidence_status?: "present" | "absent" | string;
};

export type TodayContractDomainsV1 = {
  relationships: DomainLensV1;
  money_work: DomainLensV1;
  family: DomainLensV1;
};

export type TodayContractDayStoryTraceClaimV1 = {
  id?: string;
  kind?: string;
  text?: string;
  domain?: string | null;
  evidence_ids?: string[];
};

export type TodayContractDayStoryTraceV1 = {
  calculation_version?: string;
  confidence?: number;
  limitations?: string[];
  evidence?: unknown[];
  derived_claims?: TodayContractDayStoryTraceClaimV1[];
  domains_present?: string[];
  domains_absent?: string[];
  fingerprint?: string;
  used_fallback?: boolean;
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
  /** Kitchen trace — not required for display; used for honesty / future UI. */
  trace?: TodayContractDayStoryTraceV1;
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

/** PR-3: domain is showable only with present evidence and non-empty copy. */
export function isDomainLensPresent(lens: DomainLensV1 | null | undefined): boolean {
  if (!lens) return false;
  if (String(lens.evidence_status || "present") === "absent") return false;
  return Boolean(
    (lens.status || "").trim() ||
      (lens.opportunity || "").trim() ||
      (lens.risk || "").trim() ||
      (lens.action || "").trim(),
  );
}

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
  const { coordinatedFetch } = await import("@/lib/todayFetchCoordinator");
  const key = `today:contract:${targetDate || "today"}`;
  return coordinatedFetch(key, async () => {
    const qs = targetDate ? `?target_date=${encodeURIComponent(targetDate)}` : "";
    // Hard client budget: if contract LLM stalls, Today must paint via fallback — not hang forever.
    const controller = typeof AbortController !== "undefined" ? new AbortController() : null;
    const timer =
      controller && typeof window !== "undefined"
        ? window.setTimeout(() => controller.abort(), 12_000)
        : null;
    try {
      return await getJson<TodayContractV1>(`/today/contract${qs}`, {
        signal: controller?.signal,
      });
    } finally {
      if (timer != null) window.clearTimeout(timer);
    }
  });
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
