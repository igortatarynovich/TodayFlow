import type { TarotJourneyEntry } from "@/lib/tarotJourneyStore";
import { TAROT_CONCERN_OPTIONS } from "@/lib/tarotQuestionFlowCanon";
import { getTodayTarotCardRu } from "@/components/today/todayTarotCardsRu";

export type TarotJourneyTheme = {
  emoji: string;
  label: string;
  count: number;
};

export type TarotJourneyCardStat = {
  cardId: number;
  name: string;
  count: number;
};

export type TarotJourneySummary = {
  totalSessions: number;
  periodLabel: string;
  themes: TarotJourneyTheme[];
  frequentCards: TarotJourneyCardStat[];
  recentQuestions: string[];
};

const DOMAIN_THEME: Record<string, { emoji: string; label: string }> = {
  relationships: { emoji: "❤️", label: "отношения" },
  work: { emoji: "💼", label: "работа" },
  money: { emoji: "💰", label: "деньги" },
  family: { emoji: "🏡", label: "семья" },
  growth: { emoji: "🌱", label: "саморазвитие" },
  decision: { emoji: "🧭", label: "выбор" },
  conflict: { emoji: "⚡", label: "освобождение" },
  inner_state: { emoji: "🕊", label: "терпение" },
  other: { emoji: "✨", label: "личный поиск" },
};

const KEYWORD_THEMES: Array<{ match: RegExp; emoji: string; label: string }> = [
  { match: /терпен|подожд|не спеш/i, emoji: "🌙", label: "терпение" },
  { match: /выбор|решени|вариант/i, emoji: "🧭", label: "выбор" },
  { match: /отношен|партн|любов/i, emoji: "❤️", label: "отношения" },
  { match: /работ|карьер/i, emoji: "💼", label: "работа" },
  { match: /деньг|ресурс/i, emoji: "💰", label: "деньги" },
  { match: /конфликт|освобод|отпуст/i, emoji: "⚡", label: "освобождение" },
];

function cardDisplayName(cardId: number, englishFallback: string): string {
  const ru = getTodayTarotCardRu(cardId);
  return ru?.nameRu || englishFallback;
}

export function buildTarotJourneySummary(entries: TarotJourneyEntry[], windowDays = 30): TarotJourneySummary {
  const cutoff = Date.now() - windowDays * 24 * 60 * 60 * 1000;
  const recent = entries.filter((e) => new Date(e.completedAt).getTime() >= cutoff);
  const pool = recent.length ? recent : entries.slice(0, 12);

  const themeCounts = new Map<string, TarotJourneyTheme>();
  const bumpTheme = (emoji: string, label: string) => {
    const key = label.toLowerCase();
    const prev = themeCounts.get(key);
    themeCounts.set(key, { emoji, label, count: (prev?.count ?? 0) + 1 });
  };

  for (const entry of pool) {
    const domain = (entry.concernDomain || "").toLowerCase();
    if (domain && DOMAIN_THEME[domain]) {
      const t = DOMAIN_THEME[domain];
      bumpTheme(t.emoji, t.label);
    } else {
      const concern = TAROT_CONCERN_OPTIONS.find((c) => c.id === domain);
      if (concern) bumpTheme(concern.emoji, concern.label.toLowerCase());
    }
    for (const rule of KEYWORD_THEMES) {
      if (rule.match.test(entry.question)) bumpTheme(rule.emoji, rule.label);
    }
  }

  const cardCounts = new Map<number, { name: string; count: number }>();
  for (const entry of pool) {
    entry.cardIds.forEach((id, idx) => {
      const name = cardDisplayName(id, entry.cardNames[idx] || `Card ${id}`);
      const prev = cardCounts.get(id);
      cardCounts.set(id, { name, count: (prev?.count ?? 0) + 1 });
    });
  }

  const themes = Array.from(themeCounts.values()).sort((a, b) => b.count - a.count).slice(0, 4);
  const frequentCards = Array.from(cardCounts.entries())
    .map(([cardId, v]) => ({ cardId, name: v.name, count: v.count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 5);

  const recentQuestions = pool
    .map((e) => e.question.trim())
    .filter(Boolean)
    .slice(0, 5);

  return {
    totalSessions: entries.length,
    periodLabel: recent.length ? `за последние ${windowDays} дней` : "за всё время",
    themes,
    frequentCards,
    recentQuestions,
  };
}
