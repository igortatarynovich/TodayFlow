import type { MorningRitualData } from "@/components/today/todayPageUtils";
import { formatDelta30dLabel } from "@/lib/profileCumInsights";
import type { CompactUserModel, CoreProfile } from "@/lib/types";
import { elementRuName } from "@/lib/zodiacKnowledge";

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
  awarenessPercent: number;
  awarenessDeltaLabel: string | null;
  updatedAtIso: string | null;
  updatedLabel: string;
  dailyAnchors: ProfileV2DailyAnchors;
  stoneCardTitle: string;
  stoneCardBody: string;
  supportsCardTitle: string;
  supportsCardBody: string;
  helps: string[];
  elementLabel: string | null;
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
    line: parts.length ? parts.join(" · ") : "—",
  };
}

export function resolveProfileV2AwarenessPercent(input: {
  cum: CompactUserModel | null;
  coreProfile: CoreProfile | null;
  localClosedDays?: number;
}): number {
  const overall = input.cum?.confidence?.overall;
  if (typeof overall === "number" && !Number.isNaN(overall)) {
    return Math.round(Math.max(0, Math.min(1, overall)) * 100);
  }

  const signalsDays = input.coreProfile?.living?.signal_profile?.signals_days;
  if (typeof signalsDays === "number" && signalsDays > 0) {
    return Math.min(99, Math.max(15, Math.round((signalsDays / 14) * 100)));
  }

  const filled = input.localClosedDays ?? 0;
  return Math.min(99, Math.max(12, Math.round((filled / 21) * 100)));
}

function formatUpdatedLabel(iso: string | null | undefined): { updatedAtIso: string | null; updatedLabel: string } {
  if (!iso) {
    const time = new Intl.DateTimeFormat("ru-RU", { hour: "2-digit", minute: "2-digit" }).format(new Date());
    return { updatedAtIso: null, updatedLabel: `обновлено сегодня, ${time}` };
  }

  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) {
    const time = new Intl.DateTimeFormat("ru-RU", { hour: "2-digit", minute: "2-digit" }).format(new Date());
    return { updatedAtIso: null, updatedLabel: `обновлено сегодня, ${time}` };
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
): string[] {
  return uniqueStrings(
    [
      cum?.recommendations?.primary?.text,
      ...(cum?.behavioral_patterns?.hints ?? []),
      ...(cum?.behavioral_patterns?.works ?? []),
      ...(cum?.recommendations?.alternates?.map((alt) => alt.text) ?? []),
      ...thriveAreas,
    ],
    3,
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
  const awarenessPercent = resolveProfileV2AwarenessPercent(input);
  const awarenessDeltaLabel = formatDelta30dLabel(input.cum?.confidence?.delta_30d);

  const updatedSource =
    input.cum?.generated_at ??
    input.coreProfile?.generated_at ??
    input.morningRitual?.daily_horoscope_generation_log_id != null
      ? new Date().toISOString()
      : null;
  const { updatedAtIso, updatedLabel } = formatUpdatedLabel(updatedSource);

  const stoneCardTitle = dailyAnchors.stoneName
    ? `Камень дня · ${dailyAnchors.stoneName.toLowerCase()}`
    : "Камень дня";
  const stoneCardBody =
    dailyAnchors.stoneStory ??
    input.identitySummary ??
    input.coreProfile?.living?.summary ??
    "Помогает держать фокус без внутренней спешки.";

  const supportParts = uniqueStrings(
    [dailyAnchors.colorName, dailyAnchors.totemName, dailyAnchors.planetName],
    3,
  );
  const supportsCardTitle = supportParts.length
    ? `Опоры · ${supportParts.join(" · ").toLowerCase()}`
    : "Опоры дня";

  const supportsCardBody =
    input.cum?.recommendations?.primary?.text ??
    input.coreProfile?.living?.summary ??
    input.decisionStyle ??
    input.cum?.current_state?.day_promise_text ??
    "Медленное планирование и один сложный разговор до 14:00.";

  return {
    awarenessPercent,
    awarenessDeltaLabel,
    updatedAtIso,
    updatedLabel,
    dailyAnchors,
    stoneCardTitle,
    stoneCardBody,
    supportsCardTitle,
    supportsCardBody,
    helps: buildHelps(input.cum, input.thriveAreas ?? []),
    elementLabel: buildElementLabel(input.coreProfile),
  };
}
