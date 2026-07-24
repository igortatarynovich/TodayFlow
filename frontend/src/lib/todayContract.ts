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
  /** Short «Твой ход» paragraph from LLM — empty when no support claims. */
  supports_story?: string;
  /** Objective day plot: astro + lunar layers → essence (Суть дня). */
  day_foundation?: TodayDayFoundationV1 | null;
  /** L3 personal activation — natal transits; not part of shared Foundation. */
  day_personal?: {
    contract_version?: string;
    summary_ru?: string;
    personal_astrology?: {
      depth?: string;
      summary_ru?: string;
      capability_ids?: string[];
      profections?: {
        age_years?: number;
        depth?: string;
        annual?: { house?: number; sign_ru?: string; lord_ru?: string; theme_ru?: string };
        monthly?: { house?: number; lord_ru?: string };
        summary_ru?: string;
      } | null;
      secondary_progressions?: {
        summary_ru?: string;
        progressed_date?: string;
        progressed?: { sun?: { sign_ru?: string }; moon?: { sign_ru?: string } };
      } | null;
      solar_arc?: {
        arc_degrees?: number;
        summary_ru?: string;
        bodies?: { moon?: { sign_ru?: string }; ascendant?: { sign_ru?: string } | null };
      } | null;
      solar_return?: {
        summary_ru?: string;
        period_year?: number;
        return_date?: string;
        next_return_date?: string;
        days_since_return?: number;
        days_until_next?: number;
        return_chart_soft?: {
          sun?: { sign_ru?: string };
          moon?: { sign_ru?: string };
          ascendant?: { sign_ru?: string } | null;
        };
        limitation_ru?: string;
      } | null;
      lunar_return?: {
        summary_ru?: string;
        return_date?: string;
        next_return_date?: string;
        days_since_return?: number;
        days_until_next?: number;
        return_chart_soft?: {
          sun?: { sign_ru?: string };
          moon?: { sign_ru?: string };
          ascendant?: { sign_ru?: string } | null;
        };
        limitation_ru?: string;
      } | null;
      house_rulers_chains?: {
        summary_ru?: string;
        depth?: string;
        ascendant?: { sign_ru?: string };
        houses?: Array<{ house?: number; sign_ru?: string; lord?: string; lord_ru?: string }>;
        focus?: { house?: number; lord_ru?: string; chain?: { label_ru?: string } } | null;
        limitation_ru?: string;
      } | null;
      time_lords?: {
        summary_ru?: string;
        depth?: string;
        sect?: { sect?: string; method?: string };
        firdaria?: {
          major?: { planet?: string; planet_ru?: string; start_date?: string; end_date?: string };
          sub?: { planet?: string; planet_ru?: string; start_date?: string; end_date?: string };
        };
        zodiacal_releasing?: {
          lot?: { sign_ru?: string; method?: string; lot?: string };
          level1?: { sign_ru?: string; lord_ru?: string; start_date?: string; end_date?: string };
          level2?: { sign_ru?: string; lord_ru?: string; start_date?: string; end_date?: string };
          peak_soft?: { active?: boolean; note_ru?: string | null };
        };
        zodiacal_releasing_spirit?: {
          lot?: { sign_ru?: string; method?: string; lot?: string };
          level1?: { sign_ru?: string; lord_ru?: string; start_date?: string; end_date?: string };
          level2?: { sign_ru?: string; lord_ru?: string; start_date?: string; end_date?: string };
          peak_soft?: { active?: boolean; note_ru?: string | null };
        };
        systems_available?: string[];
        limitation_ru?: string;
      } | null;
      planet_returns?: {
        summary_ru?: string;
        depth?: string;
        highlights?: Array<{
          body?: string;
          body_ru?: string;
          return_date?: string;
          next_return_date?: string;
          in_return_window?: boolean;
        }>;
        active?: Array<{ body?: string; body_ru?: string }>;
        limitation_ru?: string;
      } | null;
      beats?: Array<{ id?: string; title?: string; story_ru?: string }>;
    } | null;
    human_design?: {
      summary_ru?: string;
      capability_ids?: string[];
      transit_gates?: {
        depth?: string;
        sun?: { gate?: number; line?: number; label?: string; theme_ru?: string };
        earth?: { gate?: number; line?: number; label?: string };
        moon?: { gate?: number; line?: number; label?: string };
        planets?: Array<{ body?: string; gate?: number; line?: number; label?: string }>;
        limitation_ru?: string;
      };
      bodygraph?: {
        depth?: string;
        activations?: Array<{ id?: string; title?: string; story_ru?: string }>;
        natal_gates?: number[];
      } | null;
      channels?: {
        summary_ru?: string;
        channels?: Array<{
          id?: string;
          name_ru?: string;
          gates?: number[];
          centers?: string[];
          centers_ru?: string[];
        }>;
        natal_channels?: Array<{ id?: string; name_ru?: string; centers_ru?: string[] }>;
        defined_centers?: Array<{ id?: string; name_ru?: string; via_channels?: string[] }>;
        natal_defined_centers?: Array<{ id?: string; name_ru?: string; via_channels?: string[] }>;
        active_gates?: { transit?: number[]; natal?: number[]; combined?: number[] };
        limitation_ru?: string;
      } | null;
      type_authority?: {
        summary_ru?: string;
        depth?: string;
        type?: { id?: string; name_ru?: string };
        authority?: { id?: string; name_ru?: string };
        strategy?: { id?: string; name_ru?: string };
        defined_center_ids?: string[];
        motor_to_throat?: boolean;
        limitation_ru?: string;
      } | null;
    } | null;
    bazi?: {
      summary_ru?: string;
      depth?: string;
      beats?: Array<{ id?: string; title?: string; story_ru?: string; kind?: string }>;
      pillars?: Record<string, { label_zh?: string; branch?: { animal_ru?: string } } | null>;
    } | null;
    vedic_personal?: {
      summary_ru?: string;
      depth?: string;
      lagna?: { sign_ru?: string; sidereal_lon?: number } | null;
      gochara?: {
        transit_moon?: { house_from_natal_moon?: number; sign_ru?: string };
        summary_ru?: string;
      };
      lagna_gochara?: {
        transit_moon?: { house_from_natal?: number; sign_ru?: string };
        summary_ru?: string;
      } | null;
      dasha?: {
        mahadasha?: { lord?: string; lord_ru?: string; start?: string; end?: string };
        antardasha?: { lord?: string; lord_ru?: string } | null;
        summary_ru?: string;
      };
    } | null;
    kabbalah_letter?: {
      summary_ru?: string;
      hebrew_date?: { label_ru?: string; year?: number; month_ru?: string; day?: number };
      date_gematria?: { total?: number; reduced?: number };
      sefira?: { id?: string; name_ru?: string; theme_ru?: string };
      school_canon?: string;
    } | null;
    electional_horary?: {
      summary_ru?: string;
      mode?: "electional" | "horary" | string;
      verdict?: string;
      verdict_ru?: string;
      checklist?: Array<{ id?: string; status?: string; title?: string; story_ru?: string }>;
      ascendant?: { sign_ru?: string; degree_in_sign?: number };
      moon?: { sign_ru?: string; dignity?: { name_ru?: string } };
    } | null;
    source_inputs?: {
      has_personal_astrology?: boolean;
      has_human_design?: boolean;
      has_bazi?: boolean;
      has_vedic_personal?: boolean;
      has_kabbalah_letter?: boolean;
      has_electional_horary?: boolean;
      electional_status?: string | null;
      ok_family_ids?: string[];
    };
  } | null;
  /** Kitchen trace — not required for display; used for honesty / future UI. */
  trace?: TodayContractDayStoryTraceV1;
};

export type TodayDayFoundationBeatV1 = {
  id?: string;
  kind?: string;
  title?: string;
  story_ru?: string;
};

export type TodayDayFoundationV1 = {
  contract_version?: string;
  calculation_version?: string;
  astro?: {
    beats?: TodayDayFoundationBeatV1[];
    summary_ru?: string;
  };
  lunar?: {
    phase?: {
      name?: string;
      cycle_day?: number;
      guidance?: string;
      themes?: string;
      next_phase?: { name?: string; in_days?: number } | null;
    } | null;
    moon_sign?: { sign?: string; sign_ru?: string } | null;
    void_of_course?: {
      status?: string;
      rule_id?: string;
      in_void_of_course?: boolean;
      starts_at?: string;
      ends_at?: string;
      unavailable_reason?: string;
    } | null;
    beats?: TodayDayFoundationBeatV1[];
    summary_ru?: string;
  };
  /** Shared universal day from numerology Source Family (personal day is Personal layer). */
  numerology?: {
    universal_day?: number | null;
    personal_day?: number | null;
    summary_ru?: string;
  } | null;
  weekday?: {
    weekday?: string | null;
    ruler_planet?: string | null;
    ruler_planet_ru?: string | null;
    summary_ru?: string;
  } | null;
  seasonal?: {
    season?: string | null;
    season_ru?: string | null;
    summary_ru?: string;
    sun?: {
      sunrise_local?: string;
      sunset_local?: string;
      day_length_minutes?: number;
    } | null;
  } | null;
  planetary_hours?: {
    day_ruler_planet?: string | null;
    day_ruler_planet_ru?: string | null;
    sunrise_local?: string | null;
    sunset_local?: string | null;
    summary_ru?: string;
    hours?: Array<{
      index?: number;
      period?: string;
      ruler_planet?: string;
      ruler_planet_ru?: string;
      start_local?: string;
      end_local?: string;
    }>;
  } | null;
  panchanga?: {
    summary_ru?: string;
    tithi?: { number?: number; name_ru?: string; paksha_ru?: string } | null;
    nakshatra?: { number?: number; name_ru?: string; pada?: number } | null;
    yoga?: { number?: number; name_ru?: string } | null;
    karana?: { name_ru?: string } | null;
    vara?: { name_ru?: string; ruler_planet_ru?: string } | null;
    muhurta?: Record<string, unknown> | null;
    ayanamsha?: { id?: string; degrees?: number } | null;
  } | null;
  chinese?: {
    summary_ru?: string;
    gan_zhi_day?: {
      label_zh?: string;
      label_pinyin?: string;
      cycle_index?: number;
    } | null;
    five_elements_day?: {
      stem_element_ru?: string;
      stem_polarity_ru?: string;
      branch_element_ru?: string;
    } | null;
    jianchu_officer?: {
      id?: string;
      name_ru?: string;
      suitable_ru?: string[];
      avoid_ru?: string[];
    } | null;
    almanac_actions?: {
      suitable_ru?: string[];
      avoid_ru?: string[];
    } | null;
    solar_term?: { id?: string; name_ru?: string; zh?: string } | null;
    lucky_hours_directions?: {
      summary_ru?: string;
      directions?: Record<
        string,
        { compass?: string; name_ru?: string; role_ru?: string }
      >;
      supportive_windows?: string[];
      caution_windows?: string[];
    } | null;
  } | null;
  mayan?: {
    summary_ru?: string;
    note_ru?: string;
    tzolkin_haab?: {
      tzolkin?: { label?: string; number?: number; sign_ru?: string };
      haab?: { label?: string };
      long_count?: { label?: string };
      summary_ru?: string;
    } | null;
    dreamspell?: {
      kin?: number;
      tone?: { name_ru?: string };
      seal?: { name_ru?: string; color_ru?: string };
      summary_ru?: string;
    } | null;
  } | null;
  essence?: {
    theme?: string;
    story_ru?: string;
    evidence_ids?: string[];
  };
  source_inputs?: {
    has_astro?: boolean;
    has_lunar?: boolean;
    has_numerology?: boolean;
    has_weekday?: boolean;
    has_seasonal?: boolean;
    has_planetary_hours?: boolean;
    has_panchanga?: boolean;
    has_chinese?: boolean;
    has_mayan?: boolean;
    has_essence?: boolean;
    ok_family_ids?: string[];
  };
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
