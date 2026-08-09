/**
 * Handoff welcome glass — FE composition from existing day signals.
 * Canon: TODAY_SCREEN_SCENARIO_V3 presentation v3.3 (Architecture A).
 * Honest omit when signals missing — never invent lunar/activity copy.
 */

import type { DayVisualMode } from "@/lib/dayAtmosphere";

export type HandoffWelcomeGlass = {
  moodPills: string[];
  reasonLine: string | null;
  activityTags: string[];
};

/** Presentation chips keyed by Day Atmosphere visual_mode (already SoT for the day). */
const VISUAL_MOOD_PILLS: Record<DayVisualMode, [string, string]> = {
  grounded: ["Спокойная", "Устойчивая"],
  flow: ["Мягкая", "Текучая"],
  radiance: ["Светлая", "Открытая"],
  momentum: ["Живая", "Собранная"],
  clarity: ["Ясная", "Собранная"],
  tension: ["Острая", "Внимательная"],
  renewal: ["Свежая", "Мягкая"],
  depth: ["Глубокая", "Тихая"],
};

function clean(text: string | null | undefined): string {
  return (text ?? "").replace(/\s+/g, " ").trim();
}

function firstSentence(text: string): string {
  const parts = text.split(/(?<=[.!?])\s+/).map((s) => s.trim()).filter(Boolean);
  return parts[0] || text;
}

/**
 * Build welcome glass model. Empty arrays / null = omit that cluster in UI.
 */
export function buildHandoffWelcomeGlass(input: {
  visualMode?: DayVisualMode | string | null;
  lunarName?: string | null;
  lunarThemes?: string | null;
  lunarGuidance?: string | null;
  /** Short activity nouns already derived from day signals (max 3 used). */
  activityTags?: string[] | null;
}): HandoffWelcomeGlass {
  const mode = input.visualMode;
  const moodPills =
    typeof mode === "string" && mode in VISUAL_MOOD_PILLS
      ? [...VISUAL_MOOD_PILLS[mode as DayVisualMode]]
      : [];

  const lunarName = clean(input.lunarName);
  const themes = clean(input.lunarThemes);
  const guidance = clean(input.lunarGuidance);
  let reasonLine: string | null = null;
  if (lunarName && (themes || guidance)) {
    const detail = firstSentence(themes || guidance);
    reasonLine = detail.toLowerCase().includes(lunarName.toLowerCase())
      ? detail
      : `${lunarName} — ${detail}`;
  } else if (lunarName) {
    reasonLine = lunarName;
  } else if (themes || guidance) {
    reasonLine = firstSentence(themes || guidance);
  }

  const activityTags = (input.activityTags ?? [])
    .map((t) => clean(t))
    .filter(Boolean)
    .filter((t, i, arr) => arr.findIndex((x) => x.toLowerCase() === t.toLowerCase()) === i)
    .slice(0, 3);

  return { moodPills, reasonLine, activityTags };
}
