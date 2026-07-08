import {
  guideCanonicalPrimaryStepLine,
  parseCoreMessageForUi,
  parseDayModelBriefFromGuide,
} from "@/components/today/todayGuideActionable";
import { RITUAL_COPY } from "@/components/today/todayRitualCopy";

function narrativeString(payload: Record<string, unknown> | null | undefined, key: string): string | null {
  if (!payload || typeof payload !== "object") return null;
  const v = payload[key];
  return typeof v === "string" && v.trim() ? v.trim() : null;
}

function shortenMetaChunk(text: string, max = 48): string {
  const t = text.trim();
  if (t.length <= max) return t;
  const cut = t.slice(0, max);
  const lastSpace = cut.lastIndexOf(" ");
  return (lastSpace > 24 ? cut.slice(0, lastSpace) : cut).trim() + "…";
}

function tempoMetaLabel(tempo: string): string {
  const key = tempo.trim().toLowerCase();
  if (key === "slow" || key === "calm" || key === "spokojnyj" || key === "спокойный") {
    return RITUAL_COPY.todayExperienceTempoCalm;
  }
  if (key === "fast" || key === "active" || key === "быстрый") {
    return RITUAL_COPY.todayExperienceTempoActive;
  }
  if (/темп/i.test(tempo)) return tempo.trim();
  return `${RITUAL_COPY.todayExperienceTempoPrefix}${tempo.trim()}`;
}

function riskMetaLabel(risk: string): string {
  const t = risk.trim();
  if (/^риск/i.test(t)) return shortenMetaChunk(t, 56);
  return `${RITUAL_COPY.todayExperienceRiskPrefix}${shortenMetaChunk(t, 40)}`;
}

export type TodayExperienceTheme = {
  headline: string;
  meta: string | null;
};

export function buildTodayExperienceTheme(
  payload: Record<string, unknown> | null | undefined,
  headlineFallback: string,
): TodayExperienceTheme {
  const core = parseCoreMessageForUi(payload);
  const headline =
    narrativeString(payload, "headline") ||
    (core?.kind === "structured" ? core.headline : undefined) ||
    parseDayModelBriefFromGuide(payload)?.oneFocus ||
    headlineFallback.trim() ||
    RITUAL_COPY.todayExperienceThemeFallback;

  const subline =
    narrativeString(payload, "subline") ||
    (core?.kind === "structured" ? core.body : core?.kind === "paragraphs" ? core.paragraphs[0] : null);

  const dm = parseDayModelBriefFromGuide(payload);
  const metaParts: string[] = [];
  if (dm?.tempoLabel) metaParts.push(tempoMetaLabel(dm.tempoLabel));
  const riskChunk =
    (core?.kind === "structured" && core.risk?.trim()) ||
    dm?.riskSummary?.trim() ||
    null;
  if (riskChunk) metaParts.push(riskMetaLabel(riskChunk));
  if (metaParts.length === 0 && subline && subline !== headline) {
    metaParts.push(shortenMetaChunk(subline, 72));
  }

  return {
    headline,
    meta: metaParts.length > 0 ? metaParts.join(" · ") : null,
  };
}

export function buildTodayExperienceActionLine(
  payload: Record<string, unknown> | null | undefined,
  actionFallback: readonly string[],
): string {
  return guideCanonicalPrimaryStepLine(payload, actionFallback, RITUAL_COPY.guidePrimaryDoFallback);
}

export type TodayExperienceProgress = {
  primary: string;
  secondary: string | null;
  active: boolean;
};

export function buildTodayExperienceProgress({
  actionDone,
  streakDays,
}: {
  actionDone: boolean;
  streakDays: number;
}): TodayExperienceProgress {
  if (actionDone) {
    const primary = RITUAL_COPY.todayExperienceProgressAfterAction;
    const secondary =
      streakDays >= 2
        ? RITUAL_COPY.todayExperienceProgressStreakLine(streakDays)
        : RITUAL_COPY.todayExperienceProgressReturnHint;
    return { primary, secondary: secondary || null, active: true };
  }
  if (streakDays >= 2) {
    return {
      primary: RITUAL_COPY.todayExperienceProgressDayStarted,
      secondary: RITUAL_COPY.todayExperienceProgressStreakLine(streakDays),
      active: false,
    };
  }
  return {
    primary: RITUAL_COPY.todayExperienceProgressDayStarted,
    secondary: RITUAL_COPY.todayExperienceProgressBeforeActionHint || null,
    active: false,
  };
}
