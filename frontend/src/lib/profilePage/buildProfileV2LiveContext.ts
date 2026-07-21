import type { MorningRitualData } from "@/components/today/todayPageUtils";
import { formatDelta30dLabel } from "@/lib/profileCumInsights";
import type { CompactUserModel, CoreProfile } from "@/lib/types";
import { elementRuName } from "@/lib/zodiacKnowledge";
import { filterProfileCopyList } from "@/lib/profilePage/profileCopySafety";
import { getLocale } from "@/lib/i18n";

export type ObservationAccuracyLevel = "initial" | "forming" | "stable";

export type ProfileV2DailyAnchors = {
  stoneName: string | null;
  stoneStory: string | null;
  colorName: string | null;
  totemName: string | null;
  totemEmoji: string | null;
  planetName: string | null;
  line: string;
};

export type ProfileV2LiveContext = {
  /** Qualitative maturity of personal observations — never a fabricated precise %. */
  observationAccuracyLevel: ObservationAccuracyLevel;
  observationAccuracyLabel: string;
  /** Only when CUM confidence.overall is present; otherwise null. */
  awarenessPercent: number | null;
  awarenessDeltaLabel: string | null;
  updatedAtIso: string | null;
  /** Empty when no real generated_at — never browser "now". */
  updatedLabel: string;
  hasStoneCard: boolean;
  hasSupportsCard: boolean;
  dailyAnchors: ProfileV2DailyAnchors;
  stoneCardTitle: string;
  stoneCardBody: string;
  supportsCardTitle: string;
  supportsCardBody: string;
  helps: string[];
  elementLabel: string | null;
};

const ACCURACY_LABELS: Record<ObservationAccuracyLevel, string> = {
  initial: "начальная",
  forming: "формируется",
  stable: "устойчивая",
};

function uniqueStrings(items: Array<string | null | undefined>, max: number): string[] {
  const seen = new Set<string>();
  const out: string[] = [];
  for (const item of items) {
    const trimmed = item?.trim();
    if (!trimmed) continue;
    const key = trimmed.toLowerCase();
    if (seen.has(key)) continue;
    seen.add(key);
    out.push(trimmed);
    if (out.length >= max) break;
  }
  return out;
}

function resolvePlanetName(morningRitual: MorningRitualData | null): string | null {
  return morningRitual?.celestial_events?.personal_transits?.[0]?.title?.trim() ?? null;
}

export function buildProfileV2DailyAnchors(morningRitual: MorningRitualData | null): ProfileV2DailyAnchors {
  const symbols = morningRitual?.celestial_events?.daily_symbols;
  const stoneName = symbols?.stone?.name?.trim() ?? null;
  const stoneStory = symbols?.stone?.story_ru?.trim() ?? null;
  const colorName = symbols?.color?.name?.trim() ?? null;
  const totemName = symbols?.totem?.name?.trim() ?? null;
  const totemEmoji = symbols?.totem?.emoji?.trim() ?? null;
  const planetName = resolvePlanetName(morningRitual);

  const parts = uniqueStrings(
    [
      stoneName,
      colorName,
      totemEmoji && totemName ? `${totemEmoji} ${totemName}` : totemName,
      planetName,
    ],
    4,
  );

  return {
    stoneName,
    stoneStory,
    colorName,
    totemName,
    totemEmoji,
    planetName,
    line: parts.length ? parts.join(" · ") : "",
  };
}

/** @deprecated Prefer resolveObservationAccuracy — kept for callers that need a 0–100 from real confidence only. */
export function resolveProfileV2AwarenessPercent(input: {
  cum: CompactUserModel | null;
  coreProfile: CoreProfile | null;
  localClosedDays?: number;
}): number | null {
  const overall = input.cum?.confidence?.overall;
  if (typeof overall === "number" && !Number.isNaN(overall)) {
    return Math.round(Math.max(0, Math.min(1, overall)) * 100);
  }
  return null;
}

export function resolveObservationAccuracy(input: {
  cum: CompactUserModel | null;
  coreProfile: CoreProfile | null;
  localClosedDays?: number;
}): { level: ObservationAccuracyLevel; label: string; percent: number | null } {
  const overall = input.cum?.confidence?.overall;
  if (typeof overall === "number" && !Number.isNaN(overall)) {
    const clamped = Math.max(0, Math.min(1, overall));
    const percent = Math.round(clamped * 100);
    const level: ObservationAccuracyLevel =
      clamped >= 0.6 ? "stable" : clamped >= 0.3 ? "forming" : "initial";
    return { level, label: ACCURACY_LABELS[level], percent };
  }

  const signalsDays = input.coreProfile?.living?.signal_profile?.signals_days;
  const filled = input.localClosedDays ?? 0;
  const evidence =
    (typeof signalsDays === "number" && signalsDays > 0 ? signalsDays : 0) + filled;

  let level: ObservationAccuracyLevel = "initial";
  if (evidence >= 10) level = "stable";
  else if (evidence >= 3) level = "forming";

  return { level, label: ACCURACY_LABELS[level], percent: null };
}

function formatUpdatedLabel(iso: string | null | undefined): { updatedAtIso: string | null; updatedLabel: string } {
  if (!iso) {
    return { updatedAtIso: null, updatedLabel: "" };
  }

  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) {
    return { updatedAtIso: null, updatedLabel: "" };
  }

  const todayIso = new Date().toISOString().split("T")[0];
  const dateIso = date.toISOString().split("T")[0];
  const time = new Intl.DateTimeFormat("ru-RU", { hour: "2-digit", minute: "2-digit" }).format(date);

  if (dateIso === todayIso) {
    return { updatedAtIso: iso, updatedLabel: `обновлено сегодня, ${time}` };
  }

  const dayMonth = new Intl.DateTimeFormat("ru-RU", { day: "numeric", month: "short" }).format(date);
  return { updatedAtIso: iso, updatedLabel: `обновлено ${dayMonth}, ${time}` };
}

function buildHelps(
  cum: CompactUserModel | null,
  thriveAreas: string[],
  contractHelps: string[] = [],
): string[] {
  return filterProfileCopyList(
    [
      ...contractHelps,
      cum?.recommendations?.primary?.text,
      ...(cum?.behavioral_patterns?.hints ?? []),
      ...(cum?.behavioral_patterns?.works ?? []),
      ...(cum?.recommendations?.alternates?.map((alt) => alt.text) ?? []),
      ...thriveAreas,
    ],
    4,
    getLocale(),
  );
}

function buildElementLabel(coreProfile: CoreProfile | null): string | null {
  const element = elementRuName(coreProfile?.astro?.sun_element?.trim());
  const moonElement = coreProfile?.baseline?.element_focus?.trim() ?? "";
  if (element && moonElement && element !== moonElement) {
    return `Стихия: ${element} + ${moonElement}`;
  }
  if (element) return `Стихия: ${element}`;
  if (moonElement) return `Стихия: ${moonElement}`;
  return null;
}

export function buildProfileV2LiveContext(input: {
  coreProfile: CoreProfile | null;
  cum: CompactUserModel | null;
  morningRitual: MorningRitualData | null;
  thriveAreas?: string[];
  decisionStyle?: string | null;
  identitySummary?: string | null;
  localClosedDays?: number;
}): ProfileV2LiveContext {
  const dailyAnchors = buildProfileV2DailyAnchors(input.morningRitual);
  const accuracy = resolveObservationAccuracy(input);
  const awarenessDeltaLabel = formatDelta30dLabel(input.cum?.confidence?.delta_30d);

  // Only real timestamps — never fabricate "now" from log id presence.
  const updatedSource = input.cum?.generated_at ?? input.coreProfile?.generated_at ?? null;
  const { updatedAtIso, updatedLabel } = formatUpdatedLabel(updatedSource);

  const hasStoneCard = Boolean(dailyAnchors.stoneName && dailyAnchors.stoneStory);
  const stoneCardTitle = hasStoneCard
    ? `Камень дня · ${dailyAnchors.stoneName!.toLowerCase()}`
    : "";
  const stoneCardBody = hasStoneCard ? dailyAnchors.stoneStory! : "";

  const supportParts = uniqueStrings(
    [dailyAnchors.colorName, dailyAnchors.totemName, dailyAnchors.planetName],
    3,
  );
  const hasSupportsCard = supportParts.length > 0;
  const supportsCardTitle = hasSupportsCard
    ? `Опоры · ${supportParts.join(" · ").toLowerCase()}`
    : "";
  const supportsCardBody = hasSupportsCard ? supportParts.join(" · ") : "";

  const contractHelps = input.coreProfile?.profile_contract_v1?.helps ?? [];

  return {
    observationAccuracyLevel: accuracy.level,
    observationAccuracyLabel: accuracy.label,
    awarenessPercent: accuracy.percent,
    awarenessDeltaLabel,
    updatedAtIso,
    updatedLabel,
    hasStoneCard,
    hasSupportsCard,
    dailyAnchors,
    stoneCardTitle,
    stoneCardBody,
    supportsCardTitle,
    supportsCardBody,
    helps: buildHelps(input.cum, input.thriveAreas ?? [], contractHelps),
    elementLabel: buildElementLabel(input.coreProfile),
  };
}
