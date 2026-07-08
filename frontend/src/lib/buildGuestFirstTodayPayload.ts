import type { MorningRitualData, TodayCycleData } from "@/components/today/todayPageUtils";
import type { GuestProfileDraft } from "@/lib/guestProfileDraft";
import { buildFirstTodayPackage } from "@/lib/firstTodayPackage";
import { TODAY_CONTRACT_V1, type TodayContractV1 } from "@/lib/todayContract";
import type { CoreProfile } from "@/lib/types";
import { readOnboardingContext } from "@/lib/onboardingContext";

function todayIsoDate(): string {
  const d = new Date();
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
}

function formatDisplayDate(iso: string): string {
  const d = new Date(`${iso}T12:00:00`);
  if (Number.isNaN(d.getTime())) return iso;
  return d.toLocaleDateString("ru-RU", { weekday: "long", day: "numeric", month: "long" });
}

function pseudoCoreFromDraft(draft: GuestProfileDraft): CoreProfile {
  return {
    is_ready: false,
    person: {
      first_name: draft.first_name.trim(),
      display_name: draft.first_name.trim(),
    },
    astro: {
      sun_sign: draft.sun_sign,
    },
    numerology: {
      life_path: draft.life_path,
    },
  } as CoreProfile;
}

function contractFromPackage(
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
    generation_id: "guest-first-today-v1",
  };
}

export type GuestFirstTodayPayload = {
  dateISO: string;
  displayDate: string;
  todayData: TodayCycleData;
  contract: TodayContractV1;
  guideNarrativePayload: Record<string, unknown>;
  cardName: string;
  cardMeaning: string | null;
  numerologyValue: string;
  numerologyMeaning: string | null;
  coreProfile: CoreProfile;
};

export function buildGuestFirstTodayPayload(draft: GuestProfileDraft): GuestFirstTodayPayload {
  const ctx = readOnboardingContext();
  const coreProfile = pseudoCoreFromDraft(draft);
  const pkg = buildFirstTodayPackage({
    coreProfile,
    intentTheme: ctx.intent_theme,
    realityState: ctx.reality_state,
  });
  const contract = contractFromPackage(pkg);
  const dateISO = todayIsoDate();

  const todayData: TodayCycleData = {
    date: dateISO,
    morning: null,
    morning_completed: false,
    day_connection: null,
    day_trackers: [],
    day_journal_entries: [],
    day_completed: false,
    evening: null,
    evening_completed: false,
    morning_available: true,
    day_available: true,
    evening_available: true,
    core_profile: coreProfile,
  };

  const guideNarrativePayload: Record<string, unknown> = {
    daily_theme_headline: pkg.theme.headline,
    daily_theme_body: pkg.theme.body,
    primary_action: pkg.action.primary,
    day_model_brief: {
      oneFocus: pkg.action.primary,
      vectorSummary: pkg.theme.body,
      tempoLabel: "steady",
    },
  };

  return {
    dateISO,
    displayDate: formatDisplayDate(dateISO),
    todayData,
    contract,
    guideNarrativePayload,
    cardName: "—",
    cardMeaning: null,
    numerologyValue: draft.life_path != null ? String(draft.life_path) : "—",
    numerologyMeaning: pkg.symbolic.number,
    coreProfile,
  };
}

export function emptyMorningRitualData(): MorningRitualData | null {
  return null;
}
