import { buildTarotJourneySummary } from "@/lib/buildTarotJourneySummary";
import { readTarotJourneyEntries, shouldShowTarotJourney } from "@/lib/tarotJourneyStore";
import type { MoodMapLocale } from "@/lib/moodMapModel";

export function buildTarotMapShareLine(locale: MoodMapLocale): string | null {
  if (!shouldShowTarotJourney()) return null;
  const summary = buildTarotJourneySummary(readTarotJourneyEntries());
  const theme = summary.themes[0];
  const card = summary.frequentCards[0];
  if (locale === "ru") {
    if (theme && card) {
      return `Моё таро-путешествие: тема «${theme.label}», чаще приходил ${card.name}. ${summary.periodLabel}.`;
    }
    return `Моё таро-путешествие в TodayFlow — ${summary.totalSessions} раскладов, ${summary.periodLabel}.`;
  }
  if (theme && card) {
    return `My tarot arc: theme "${theme.label}", ${card.name} showed up often. ${summary.periodLabel}.`;
  }
  return `My tarot arc in TodayFlow—${summary.totalSessions} readings, ${summary.periodLabel}.`;
}

export function buildTarotMapObservation(locale: MoodMapLocale): string | null {
  if (!shouldShowTarotJourney()) return null;
  const summary = buildTarotJourneySummary(readTarotJourneyEntries());
  if (locale === "ru") {
    const card = summary.frequentCards[0];
    if (card) return `Чаще других рядом был ${card.name} — архетипическая линия, не статистика.`;
    return `${summary.totalSessions} раскладов уже на карте — история складывается.`;
  }
  const card = summary.frequentCards[0];
  if (card) return `${card.name} showed up most often—an archetypal line, not a stat sheet.`;
  return `${summary.totalSessions} readings on the map—the story is taking shape.`;
}
