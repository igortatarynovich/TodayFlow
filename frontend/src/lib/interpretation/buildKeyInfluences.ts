import { chineseZodiacFromIsoDate } from "@/lib/chineseZodiacFromDate";
import type { GuestProfileDraft } from "@/lib/guestProfileDraft";
import { sunSignFromIsoDate } from "@/lib/sunSignFromDate";
import { elementNames, getElement, type Element } from "@/lib/zodiac-utils";
import { getLifePathEntry, getZodiacEntry, resolveZodiacSignId } from "@/lib/zodiacKnowledge";
import { lifePathHeroCaption } from "@/lib/visualIdentity/lifePathTitles";

export type KeyInfluenceKind = "sun" | "life_path" | "chinese" | "element" | "archetype";

export type KeyInfluenceTile = {
  id: KeyInfluenceKind;
  label: string;
  value: string;
  traits: string[];
};

const ELEMENT_TRAITS: Record<Element, string[]> = {
  Fire: ["Импульс", "Смелость", "Драйв"],
  Earth: ["Стабильность", "Практичность", "Опора"],
  Air: ["Идеи", "Связи", "Свобода"],
  Water: ["Чувствительность", "Глубина", "Интуиция"],
};

const ARCHETYPE_SHORT: Record<number, string> = {
  1: "Лидер",
  2: "Союзник",
  3: "Творец",
  4: "Строитель",
  5: "Исследователь",
  6: "Хранитель",
  7: "Исследователь",
  8: "Стратег",
  9: "Наставник",
  11: "Визионер",
  22: "Мастер",
  33: "Наставник",
};

function capitalizeTrait(value: string): string {
  const t = value.trim();
  if (!t) return t;
  return t.charAt(0).toUpperCase() + t.slice(1);
}

export function buildKeyInfluences(draft: GuestProfileDraft): KeyInfluenceTile[] {
  const sunSign = draft.sun_sign || sunSignFromIsoDate(draft.birth_date);
  const signId = sunSign ? resolveZodiacSignId(sunSign, null) : null;
  const signEntry = signId ? getZodiacEntry(signId) : undefined;
  const lpEntry = getLifePathEntry(draft.life_path ?? undefined);
  const chinese = chineseZodiacFromIsoDate(draft.birth_date);
  const element = sunSign ? getElement(sunSign) : null;

  const tiles: KeyInfluenceTile[] = [];

  if (signEntry) {
    tiles.push({
      id: "sun",
      label: "Солнечный знак",
      value: signEntry.ruName,
      traits: (signEntry.plusSide ?? signEntry.strengths ?? signEntry.themes)
        .slice(0, 3)
        .map(capitalizeTrait),
    });
  }

  if (draft.life_path != null && lpEntry) {
    tiles.push({
      id: "life_path",
      label: "Число пути",
      value: String(draft.life_path),
      traits: (lpEntry.strengths ?? lpEntry.plus_side ?? []).slice(0, 3).map(capitalizeTrait),
    });
  }

  if (chinese) {
    tiles.push({
      id: "chinese",
      label: "Восточный знак",
      value: chinese.animalRu,
      traits: chinese.traits,
    });
  }

  if (element) {
    tiles.push({
      id: "element",
      label: "Стихия",
      value: elementNames[element],
      traits: ELEMENT_TRAITS[element],
    });
  }

  if (draft.life_path != null) {
    const archetype =
      ARCHETYPE_SHORT[draft.life_path] ??
      lifePathHeroCaption(draft.life_path).split(" ")[0] ??
      "Архетип";
    tiles.push({
      id: "archetype",
      label: "Доминирующая энергия",
      value: archetype,
      traits: (lpEntry?.plus_side ?? lpEntry?.strengths ?? ["Глубина", "Смысл", "Фокус"])
        .slice(0, 3)
        .map(capitalizeTrait),
    });
  }

  return tiles.slice(0, 5);
}
