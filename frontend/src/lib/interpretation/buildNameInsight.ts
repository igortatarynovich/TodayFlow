import { computeNameNumbers } from "@/lib/numerology/computeNameNumbers";
import { getNameNumberEntry } from "@/lib/zodiacKnowledge";

export type NameInsightTile = {
  id: "expression" | "soul_urge" | "personality";
  label: string;
  value: string;
  meaning: string;
};

export type NameInsightModel = {
  displayName: string;
  headline: string;
  tiles: NameInsightTile[];
};

function capitalizeFirst(text: string): string {
  const t = text.trim();
  if (!t) return t;
  return t.charAt(0).toUpperCase() + t.slice(1);
}

export function buildNameInsight(firstName: string): NameInsightModel | null {
  const trimmed = firstName.trim();
  if (!trimmed) return null;

  const numbers = computeNameNumbers(trimmed);
  if (!numbers) return null;

  const expressionEntry = getNameNumberEntry(numbers.expression);
  const soulEntry = getNameNumberEntry(numbers.soulUrge);
  const personalityEntry = getNameNumberEntry(numbers.personality);

  const tiles: NameInsightTile[] = [
    {
      id: "expression",
      label: "Число имени",
      value: String(numbers.expression),
      meaning: expressionEntry?.expression
        ? capitalizeFirst(expressionEntry.expression)
        : "Как имя задаёт твой стиль проявления.",
    },
    {
      id: "soul_urge",
      label: "Число души",
      value: String(numbers.soulUrge),
      meaning: soulEntry?.soul_urge
        ? capitalizeFirst(soulEntry.soul_urge)
        : "Что для тебя важно внутри, даже если снаружи это не всегда видно.",
    },
    {
      id: "personality",
      label: "Число личности",
      value: String(numbers.personality),
      meaning: personalityEntry?.personality
        ? capitalizeFirst(personalityEntry.personality)
        : "Как тебя чаще считывают при первом контакте.",
    },
  ];

  return {
    displayName: trimmed,
    headline: `${trimmed} — имя уже несёт свой ритм и числовой оттенок.`,
    tiles,
  };
}
