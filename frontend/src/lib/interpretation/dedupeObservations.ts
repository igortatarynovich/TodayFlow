import { normText, textSimilarity } from "@/lib/interpretation/formatRecognitionText";

const THEME_KEYWORDS: Record<string, string[]> = {
  thinking: ["логик", "решен", "дум", "анализ", "смысл", "поним", "концеп"],
  freedom: ["свобод", "огранич", "рамк", "контрол", "независ"],
  energy: ["энерг", "уста", "тяжел", "слабе", "выгор"],
  social: ["люди", "замеч", "общен", "контакт", "дистан"],
  growth: ["раст", "разви", "учиш"],
  depth: ["глуб", "одиноч", "наблюд"],
  environment: ["сред", "простран", "ритм", "раскры", "работ"],
  balance: ["равновес", "восстан", "опор", "тишин", "поддерж"],
};

export function inferObservationThemes(text: string): Set<string> {
  const norm = normText(text);
  const themes = new Set<string>();
  for (const [theme, keys] of Object.entries(THEME_KEYWORDS)) {
    if (keys.some((k) => norm.includes(k))) themes.add(theme);
  }
  return themes;
}

export function isTooSimilarToAny(
  candidateText: string,
  selectedTexts: string[],
  similarityThreshold = 0.38,
): boolean {
  return selectedTexts.some((selected) => textSimilarity(selected, candidateText) >= similarityThreshold);
}

export function sharesDominantTheme(candidateText: string, usedThemes: Set<string>): boolean {
  const themes = inferObservationThemes(candidateText);
  for (const theme of Array.from(themes)) {
    if (usedThemes.has(theme)) return true;
  }
  return false;
}

export function registerThemes(text: string, usedThemes: Set<string>): void {
  Array.from(inferObservationThemes(text)).forEach((t) => usedThemes.add(t));
}
