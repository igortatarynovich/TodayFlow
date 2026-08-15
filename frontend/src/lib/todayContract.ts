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
  work: DomainLensV1;
  money: DomainLensV1;
  relationships: DomainLensV1;
  energy: DomainLensV1;
};

export type TodayContractDomainId = keyof TodayContractDomainsV1;

/** Fixed-4 DomainLens wire order (ScreenFlow v3.1). */
export const TODAY_CONTRACT_DOMAIN_ORDER: TodayContractDomainId[] = [
  "work",
  "money",
  "relationships",
  "energy",
];

export const TODAY_CONTRACT_DOMAIN_LABEL_RU: Record<TodayContractDomainId, string> = {
  work: "Работа",
  money: "Деньги",
  relationships: "Отношения",
  energy: "Энергия",
};

const ABSENT_DOMAIN_LENS: DomainLensV1 = {
  status: "",
  opportunity: "",
  risk: "",
  action: "",
  evidence_status: "absent",
};

function isDomainLensObject(value: unknown): value is DomainLensV1 {
  return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}

/**
 * Prefer fixed-4 keys; fold legacy money_work → work+money and family → relationships
 * only when the target keys are missing. Always returns all 4 keys.
 */
export function normalizeTodayContractDomains(raw: unknown): TodayContractDomainsV1 {
  const src =
    raw && typeof raw === "object" && !Array.isArray(raw)
      ? (raw as Record<string, unknown>)
      : {};
  const out: Partial<TodayContractDomainsV1> = {};

  for (const id of TODAY_CONTRACT_DOMAIN_ORDER) {
    if (isDomainLensObject(src[id])) {
      out[id] = src[id] as DomainLensV1;
    }
  }

  const moneyWork = src.money_work;
  if (isDomainLensObject(moneyWork)) {
    if (!out.work) out.work = moneyWork;
    if (!out.money) out.money = moneyWork;
  }

  const family = src.family;
  if (isDomainLensObject(family) && !out.relationships) {
    out.relationships = family;
  }

  return {
    work: out.work ?? { ...ABSENT_DOMAIN_LENS },
    money: out.money ?? { ...ABSENT_DOMAIN_LENS },
    relationships: out.relationships ?? { ...ABSENT_DOMAIN_LENS },
    energy: out.energy ?? { ...ABSENT_DOMAIN_LENS },
  };
}

export function normalizeTodayContractV1(contract: TodayContractV1): TodayContractV1 {
  return {
    ...contract,
    domains: normalizeTodayContractDomains(contract.domains),
  };
}

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
  /** ok | unavailable — facts-only shell when interpretation could not be generated. */
  interpretation_status?: "ok" | "unavailable" | string;
  interpretation_unavailable_message?: string | null;
  theme?: string;
  /** §0.1 image-title for hero — not an astro fact label. */
  headline_anchor?: string;
  /** Single day plot (family/variant/mode). Prefer over primary_conflict. */
  day_thesis?: {
    family?: string;
    variant?: string;
    mode?: string;
    label_ru?: string;
    label?: string;
    driver_ids?: string[];
    composition_ids?: string[];
  } | null;
  /** @deprecated Use day_thesis.label_ru — kept for mid-migration UI. */
  primary_conflict?: string;
  /** Named 1–3 sky drivers paragraph. */
  events_lead?: string;
  /** What to expect today (everyday scene). */
  expect?: string;
  /** Single day trap. */
  trap?: string;
  direction?: string;
  story?: string;
  do?: string[];
  avoid?: string[];
  advantage?: string;
  abstain?: string;
  today_move?: string;
  /** §0.5 concrete sensory closing strokes (semicolon-separated). */
  vibe_closing?: string;
  /** Preferred structured strokes when present — join for display. */
  vibe_strokes?: string[];
  /** Kitchen editorial meta (exemplar + SP ids) — not primary UI copy. */
  editorial?: {
    exemplar_id?: string;
    strong_pattern_ids?: string[];
  } | null;
  evening_closure?: string;
  /** Closed day mood (same enum as day_atmosphere.visual_mode). LLM pick; optional. */
  visual_mode?: string | null;
  talisman?: {
    color?: string;
    stone?: string;
    note?: string;
    /** Scenario-derived avoid (B3+); preferred over morning catalog avoid. */
    avoid_color?: string;
    avoid_why?: string;
    origin_scene_id?: string;
  };
  practice_recommendation?: {
    kind?: string;
    text?: string;
    reason?: string;
    origin_scene_id?: string;
  };
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
      beats?: Array<{ id?: string; kind?: string; title?: string; story_ru?: string }>;
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
      profile_lines_cross?: {
        summary_ru?: string;
        depth?: string;
        profile?: {
          id?: string;
          personality_line?: number;
          design_line?: number;
          personality_role_ru?: string;
          design_role_ru?: string;
          label_ru?: string;
        };
        angle?: { id?: string; name_ru?: string };
        incarnation_cross?: {
          gates?: number[];
          label?: string;
          conscious_sun?: { gate?: number; line?: number; label?: string; theme_ru?: string | null };
          unconscious_sun?: { gate?: number; line?: number; label?: string; theme_ru?: string | null };
          named_cross?: string | null;
        };
        limitation_ru?: string;
      } | null;
      variables?: {
        summary_ru?: string;
        depth?: string;
        pattern?: string;
        digestion?: { orientation?: string; color_name_ru?: string; color?: number } | null;
        environment?: { orientation?: string; color_name_ru?: string; color?: number } | null;
        perspective?: { orientation?: string; color_name_ru?: string; color?: number } | null;
        motivation?: { orientation?: string; color_name_ru?: string; color?: number } | null;
        arrows?: Array<{
          id?: string;
          name_ru?: string;
          orientation?: string;
          orientation_ru?: string;
          color_name_ru?: string;
        }>;
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
      notes_ru?: string;
      mode?: "electional" | "horary" | string;
      verdict?: string;
      verdict_ru?: string;
      checklist?: Array<{ id?: string; status?: string; title?: string; story_ru?: string }>;
      checklist_counts?: {
        pass?: number;
        caution?: number;
        fail?: number;
        info?: number;
      };
      ascendant?: { sign_ru?: string; degree_in_sign?: number };
      moon?: {
        sign_ru?: string;
        dignity?: { id?: string; name_ru?: string; tone?: string };
        longitude_method?: string;
      };
      planetary_hour?: {
        matched?: boolean;
        ruler_planet_ru?: string;
        period?: string;
        start_local?: string;
        end_local?: string;
      } | null;
      nearest_lunar_aspect?: {
        title?: string;
        aspect?: string;
        delta_minutes?: number;
        within_3h?: boolean;
      } | null;
      moment?: { date?: string; time?: string; timezone?: string | null };
      question?: string | null;
    } | null;
    name_numbers?: {
      status?: string;
      summary_ru?: string;
      expression?: { value?: number; theme_ru?: string } | null;
      soul_urge?: { value?: number; theme_ru?: string } | null;
      personality?: { value?: number; theme_ru?: string } | null;
      school_canon?: string;
    } | null;
    source_inputs?: {
      has_personal_astrology?: boolean;
      has_human_design?: boolean;
      has_bazi?: boolean;
      has_vedic_personal?: boolean;
      has_kabbalah_letter?: boolean;
      has_electional_horary?: boolean;
      has_name_numbers?: boolean;
      electional_status?: string | null;
      ok_family_ids?: string[];
    };
  } | null;
  /** Kitchen trace — not required for display; used for honesty / future UI. */
  trace?: TodayContractDayStoryTraceV1;
  /**
   * Level-2 interpretive chorus (astro / day card / number / natal) — explains one conflict.
   * Not a second forecast.
   */
  interpretive_chorus?: {
    astrology_lead?: string | null;
    astrology_meaning?: string | null;
    day_card?: { named?: string | null; role?: string | null } | null;
    day_number?: {
      named?: string | null;
      tempo?: string | null;
      style?: string | null;
      for_conflict?: string | null;
    } | null;
    natal_lead?: string | null;
    dialogue_rule?: string | null;
    parallel_forecast_forbidden?: boolean;
  } | null;
  /**
   * Full day_scenario nest (B3+). Prefer for conflict/scenes/props when present;
   * public slots remain projections.
   */
  day_scenario?: {
    contract_version?: string;
    version?: string;
    runtime_sot?: boolean;
    ready?: boolean;
    generation_source?: string;
    conflict?: {
      short_name?: string;
      why_arose?: string;
      why_personal?: string;
      opposing_forces?: { a?: string; b?: string };
    };
    scenes?: Array<{
      scene_id?: string;
      sphere?: string;
      sphere_label_ru?: string;
      role_in_story?: string;
      /** Reading step 1 — why this sphere today (not Plot why_arose). */
      why?: string;
      what_happens?: string;
      opportunity?: string;
      trap?: string;
      recommended_action?: string;
      do_not?: string;
      domestic_example?: string;
    }>;
    props?: {
      status?: string;
      color?: {
        name?: string;
        origin_scene_id?: string;
        link_to_conflict?: string;
        where_to_use?: string;
        expected_effect_today?: string;
      };
      avoid_color?: { name?: string; why?: string; origin_scene_id?: string };
      goals?: Array<{ text?: string; origin_scene_id?: string }>;
      affirmations?: Array<{ text?: string; origin_scene_id?: string }>;
      strong_spheres?: Array<{ sphere?: string; sphere_label_ru?: string; status?: string }>;
      weak_spheres?: Array<{ sphere?: string; sphere_label_ru?: string; status?: string }>;
    };
    chorus?: Record<string, unknown>;
  } | null;
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
      id?: string;
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
    holidays?: {
      is_holiday?: boolean;
      summary_ru?: string;
      today?: Array<{
        id?: string;
        name_ru?: string;
        name_en?: string;
        kind?: string;
      }>;
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

/** C5 day clock — see docs/audits/DAY_LIFECYCLE_V1.md */
export type DayLifecycleC5 = {
  contract_version?: string;
  status?: "day_not_ready" | "assembling" | "ready" | "closed" | string;
  local_date?: string;
  target_date?: string;
  timezone?: string;
  ready_time?: string;
  ready_at?: string;
  assemble_window?: { start?: string; end?: string; active?: boolean };
  now_local?: string;
};

export type TodayDepthTopicId = "money" | "intimacy" | "love" | "career" | "family" | "full_day";

export type TodayDepthLayerMenuItemV1 = {
  topic: TodayDepthTopicId | string;
  label: string;
  value?: string;
};

/** Optional deepen offer — never hides base day (TODAY_DEPTH_LAYER_V1). */
export type TodayContractDepthLayerV1 = {
  version: string;
  can_generate: boolean;
  access: "available" | "cta" | string;
  menu: TodayDepthLayerMenuItemV1[];
  subscribe_path?: string;
};

/** Wire shape for `/today/contract.day_atmosphere` — mirrors FE DayAtmosphereContract. */
export type DayAtmosphereContractWire = {
  version?: string;
  visual_mode: string;
  intensity?: number;
  warmth?: number;
  motion?: string;
  contrast?: string;
  decor_variant?: string;
  time_phase?: string;
};

/** Wave B1 — welcome glass nest (mood / lunar reason / do chips). */
export type TodayContractWelcomeGlassV1 = {
  mood_tags: string[];
  reason: string | null;
  good_for: string[];
};

export type TodayContractProgressKind = "habit" | "ascetic" | "practice";

/** Wave B1 — unified growth rows; do not confuse with story `progress`. */
export type TodayContractTodayProgressRowV1 = {
  id: string;
  kind: TodayContractProgressKind | string;
  kind_label: string;
  name: string;
  streak_days: number;
  days_bool: boolean[];
};

export type TodayContractTodayProgressV1 = {
  rows: TodayContractTodayProgressRowV1[];
};

/** Wave B1 — color guide rows for FE (fill-empty from scenario/talisman/catalog). */
export type TodayContractColorGuideV1 = {
  name: string;
  intensity?: string | null;
  clothing?: string | null;
  accessory?: string | null;
  amount?: string | null;
  avoid?: string | null;
  avoid_why?: string | null;
};

export type TodayContractSkyBodyV1 = {
  body: string;
  body_ru: string;
  sign: string;
  sign_ru: string;
  degree?: number | null;
  retrograde?: boolean;
};

export type TodayContractSkyHeadlineV1 = {
  id: string;
  planet_a: string;
  planet_b: string;
  planet_a_ru: string;
  planet_b_ru: string;
  sign_a?: string | null;
  sign_b?: string | null;
  sign_a_ru?: string | null;
  sign_b_ru?: string | null;
  aspect: string;
  aspect_ru: string;
  title_ru: string;
  orb_delta?: number | null;
};

export type TodayContractSkyAspectV1 = {
  id: string;
  planet_a: string;
  planet_b: string;
  planet_a_ru: string;
  planet_b_ru: string;
  sign_a_ru?: string | null;
  sign_b_ru?: string | null;
  aspect: string;
  aspect_ru: string;
  title_ru: string;
  orb_delta?: number | null;
};

/** Shared sky strip + sheet. Moon every day; headline is the extra body-pair. */
export type TodayContractSkyTodayV1 = {
  contract_version?: string;
  moon?: TodayContractSkyBodyV1 | null;
  headline?: TodayContractSkyHeadlineV1 | null;
  positions?: TodayContractSkyBodyV1[];
  aspects?: TodayContractSkyAspectV1[];
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
  /** Closed Day Atmosphere config from BE (FOUNDATION_UI §11–§12). */
  day_atmosphere?: DayAtmosphereContractWire | null;
  depth_layer?: TodayContractDepthLayerV1 | null;
  welcome_glass?: TodayContractWelcomeGlassV1 | null;
  today_progress?: TodayContractTodayProgressV1 | null;
  color_guide?: TodayContractColorGuideV1 | null;
  /** Shared sky: Moon in sign every day + one headline pair. Sheet lists the rest. */
  sky_today?: TodayContractSkyTodayV1 | null;
};

export const DAY_ATMOSPHERE_ENGINE_EVENT = "todayflow:day-atmosphere";

/**
 * Publish engine day_atmosphere for DayAtmosphereBridge (same payload as contract nest).
 * Fired when Today bundle writes a contract — no second invented fetch.
 */
export function publishDayAtmosphereEngine(
  nest: DayAtmosphereContractWire | null | undefined,
): void {
  if (typeof window === "undefined") return;
  try {
    window.dispatchEvent(
      new CustomEvent(DAY_ATMOSPHERE_ENGINE_EVENT, { detail: nest ?? null }),
    );
  } catch {
    /* ignore */
  }
}

export function readDayLifecycle(contract: TodayContractV1 | null | undefined): DayLifecycleC5 | null {
  const raw = contract?.progress?.day_lifecycle;
  if (!raw || typeof raw !== "object") return null;
  return raw as DayLifecycleC5;
}

export function isDayNotReady(contract: TodayContractV1 | null | undefined): boolean {
  if ((contract?.generation_id || "").trim() === "day-not-ready-c5") return true;
  return readDayLifecycle(contract)?.status === "day_not_ready";
}

/** Past ready_at but package not served yet — show loading, never trigger assemble. */
export function isDayAssembling(contract: TodayContractV1 | null | undefined): boolean {
  if ((contract?.generation_id || "").trim() === "day-assembling-c5") return true;
  if (readDayLifecycle(contract)?.status === "assembling") return true;
  const storyStatus = String((contract?.progress as { story_status?: unknown } | undefined)?.story_status || "");
  return storyStatus === "assembling";
}

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

function lensFromLine(line: string | undefined): DomainLensV1 {
  const text = (line || "").trim();
  if (!text) return { ...ABSENT_DOMAIN_LENS };
  return {
    status: "",
    opportunity: text,
    risk: "",
    action: text,
  };
}

function contractFromFirstTodayPackage(
  pkg: ReturnType<typeof buildFirstTodayPackage>,
): TodayContractV1 {
  const byId = new Map(pkg.insight.spheres.map((s) => [s.id, s.line] as const));

  return {
    contract_version: TODAY_CONTRACT_V1,
    global_context: { period: pkg.theme.headline },
    personal_growth: { development_point: pkg.why.lines[0] || "Один честный шаг сегодня." },
    domains: {
      work: lensFromLine(byId.get("work")),
      money: lensFromLine(byId.get("money")),
      relationships: lensFromLine(byId.get("relationships")),
      energy: lensFromLine(byId.get("energy")),
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

function clientTimezone(): string {
  try {
    return Intl.DateTimeFormat().resolvedOptions().timeZone || "UTC";
  } catch {
    return "UTC";
  }
}

/** Local calendar YYYY-MM-DD (not UTC ISO date). */
export function localCalendarDateISO(d: Date = new Date()): string {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
}

export async function fetchTodayContractV1(targetDate?: string): Promise<TodayContractV1> {
  const params = new URLSearchParams();
  if (targetDate) params.set("target_date", targetDate);
  params.set("timezone", clientTimezone());
  const qs = `?${params.toString()}`;
  // Hard client budget: if contract LLM stalls, Today must paint via fallback — not hang forever.
  const controller = typeof AbortController !== "undefined" ? new AbortController() : null;
  const timer =
    controller && typeof window !== "undefined"
      ? window.setTimeout(() => {
          try {
            controller.abort(
              typeof DOMException !== "undefined"
                ? new DOMException("Request timed out.", "TimeoutError")
                : undefined,
            );
          } catch {
            controller.abort();
          }
        }, 12_000)
      : null;
  try {
    const raw = await getJson<TodayContractV1>(`/today/contract${qs}`, {
      signal: controller?.signal,
    });
    return normalizeTodayContractV1(raw);
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
  const result = await postJson<TodayStoryRefreshResult>("/today/story/refresh", {
    local_date: input?.localDate,
    timezone,
    force: Boolean(input?.force),
  });
  if (result.contract) {
    return { ...result, contract: normalizeTodayContractV1(result.contract) };
  }
  return result;
}

export function isTodayStoryStale(contract: TodayContractV1 | null | undefined): boolean {
  const p = contract?.progress || {};
  return p.story_refresh_required === true || p.story_status === "stale";
}
