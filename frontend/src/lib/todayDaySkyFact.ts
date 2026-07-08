import type { MorningRitualData } from "@/components/today/todayPageUtils";

export type DaySkyFact = {
  factKey: string;
  factLine: string;
};

/** R3a — факт неба/дня, не совет (themes, не guidance). */
export function pickDaySkyFact(morning: MorningRitualData | null | undefined): DaySkyFact {
  const lp = morning?.celestial_events?.lunar_phase;
  if (lp?.name && String(lp.name).trim()) {
    const name = String(lp.name).trim();
    const themes = typeof lp.themes === "string" ? lp.themes.trim() : "";
    return {
      factKey: `lunar_phase:${name}`,
      factLine: themes ? `${name}. ${themes}` : name,
    };
  }
  return {
    factKey: "day:default",
    factLine: "Сегодня новый день в твоём цикле.",
  };
}

export function timeOfDayGreetingRu(now = new Date()): string {
  const h = now.getHours();
  if (h < 12) return "Доброе утро";
  if (h < 18) return "Добрый день";
  return "Добрый вечер";
}
