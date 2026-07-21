import type { CompactUserModel, CompactUserModelConfidenceHistory } from "@/lib/types";

export type ConfidenceSparklineCell = {
  dateISO: string;
  overall: number;
  heightPct: number;
};

const UNCERTAINTY_FLAG_RU: Record<string, string> = {
  low_meaning_events: "Мало событий за период — выводы предварительные.",
  no_active_knowledge_atoms: "Пока нет подтверждённых паттернов.",
  no_explicit_state_today: "Отметь настроение в «Я сегодня» — точность вырастет.",
};

export function formatConfidencePercent(overall: number | null | undefined): string {
  if (overall == null || Number.isNaN(overall)) return "—";
  return `${Math.round(Math.max(0, Math.min(1, overall)) * 100)}%`;
}

export function formatDelta30dLabel(delta: number | null | undefined): string | null {
  if (delta == null || Number.isNaN(delta)) return null;
  const pct = Math.round(delta * 100);
  if (pct === 0) return "без изменений за 30 дн";
  const sign = pct > 0 ? "+" : "";
  return `${sign}${pct} за 30 дн`;
}

export function formatDeltaWindowLabel(delta: number | null | undefined, windowDays: number): string | null {
  if (delta == null || Number.isNaN(delta)) return null;
  const pct = Math.round(delta * 100);
  if (pct === 0) return `без изменений за ${windowDays} дн`;
  const sign = pct > 0 ? "+" : "";
  return `${sign}${pct} за ${windowDays} дн`;
}

export function uncertaintyFlagMessage(flag: string): string {
  return UNCERTAINTY_FLAG_RU[flag] ?? flag.replace(/_/g, " ");
}

export function buildConfidenceSparklineCells(
  points: CompactUserModelConfidenceHistory["points"],
): ConfidenceSparklineCell[] {
  if (!points.length) return [];
  const values = points.map((p) => p.overall);
  const min = Math.min(...values);
  const max = Math.max(...values);
  const span = Math.max(max - min, 0.08);
  return points.map((point) => ({
    dateISO: point.snapshot_date,
    overall: point.overall,
    heightPct: Math.round(((point.overall - min) / span) * 70 + 30),
  }));
}

export function shouldShowCumInsights(cum: CompactUserModel | null | undefined): boolean {
  if (!cum) return false;
  const hasConfidence = typeof cum.confidence?.overall === "number";
  const hasRec = Boolean(cum.recommendations?.primary?.text?.trim());
  return hasConfidence || hasRec;
}

export function cumDomainRows(cum: CompactUserModel): Array<{ id: string; label: string; value: number }> {
  const domains = cum.confidence?.by_domain;
  if (!domains) return [];
  const labels: Record<string, string> = {
    identity: "Идентичность",
    themes: "Темы",
    timing: "Тайминг",
    recommendations: "Рекомендации",
  };
  return Object.entries(domains)
    .filter(([, value]) => typeof value === "number")
    .map(([id, value]) => ({ id, label: labels[id] ?? id, value: value as number }))
    .sort((a, b) => b.value - a.value);
}
