/**
 * FE tarot theater bank — labels + sphereBump only.
 * Meaning SoT is BE `card_base_v1` (hook_reveal / tarot_card.meaning / explainer).
 * Do not add card prose here.
 */
export type TarotSphereBump = Partial<Record<"love" | "work" | "money" | "energy", number>>;

export type TodayTarotCardRu = {
  nameRu: string;
  sphereBump?: TarotSphereBump;
};

/** Старшие арканы (id 0–21): имя + theater sphereBump. */
export const TODAY_TAROT_CARDS_RU: Record<number, TodayTarotCardRu> = {
  0: { nameRu: "Шут", sphereBump: { energy: 5, work: 4 } },
  1: { nameRu: "Маг", sphereBump: { work: 8, money: 4 } },
  2: { nameRu: "Верховная Жрица", sphereBump: { love: 6, energy: 5 } },
  3: { nameRu: "Императрица", sphereBump: { love: 8, energy: 6 } },
  4: { nameRu: "Император", sphereBump: { work: 7, money: 6 } },
  5: { nameRu: "Иерофант", sphereBump: { work: 5, love: 5 } },
  6: { nameRu: "Влюблённые", sphereBump: { love: 10, money: 3 } },
  7: { nameRu: "Колесница", sphereBump: { work: 8, energy: 6 } },
  8: { nameRu: "Сила", sphereBump: { energy: 8, love: 5 } },
  9: { nameRu: "Отшельник", sphereBump: { energy: 6, work: 4 } },
  10: { nameRu: "Колесо Фортуны", sphereBump: { money: 6, work: 5, energy: 5 } },
  11: { nameRu: "Справедливость", sphereBump: { work: 7, love: 6 } },
  12: { nameRu: "Повешенный", sphereBump: { energy: 7, love: 4 } },
  13: { nameRu: "Смерть", sphereBump: { energy: 6, work: 6 } },
  14: { nameRu: "Умеренность", sphereBump: { energy: 8, love: 6, work: 6 } },
  15: { nameRu: "Дьявол", sphereBump: { money: 8, love: 6 } },
  16: { nameRu: "Башня", sphereBump: { work: 7, energy: 7 } },
  17: { nameRu: "Звезда", sphereBump: { love: 7, energy: 7 } },
  18: { nameRu: "Луна", sphereBump: { energy: 8, love: 5 } },
  19: { nameRu: "Солнце", sphereBump: { energy: 9, love: 7 } },
  20: { nameRu: "Суд", sphereBump: { work: 6, love: 6, energy: 6 } },
  21: { nameRu: "Мир", sphereBump: { work: 6, money: 6, love: 5 } },
};

const SUIT_RU = ["жезлов", "кубков", "мечей", "пентаклей"] as const;
const RANK_RU = [
  "Туз",
  "Двойка",
  "Тройка",
  "Четвёрка",
  "Пятёрка",
  "Шестёрка",
  "Семёрка",
  "Восьмёрка",
  "Девятка",
  "Десятка",
  "Паж",
  "Рыцарь",
  "Королева",
  "Король",
] as const;

/** Младший аркан 22…77 — только имя + лёгкий theater bump. */
function minorTarotLabel(deckIndex: number): TodayTarotCardRu {
  const off = deckIndex - 22;
  const suit = SUIT_RU[Math.floor(off / 14)] ?? "масти";
  const rank = RANK_RU[off % 14]!;
  return {
    nameRu: `${rank} ${suit}`,
    sphereBump: { energy: 4, work: 3 },
  };
}

export function getTodayTarotCardRu(cardId: number): TodayTarotCardRu | undefined {
  if (cardId >= 0 && cardId <= 21) return TODAY_TAROT_CARDS_RU[cardId];
  if (cardId >= 22 && cardId <= 77) return minorTarotLabel(cardId);
  return undefined;
}

const TAROT_SPHERE_BUMP_KEYS: (keyof TarotSphereBump)[] = ["love", "work", "money", "energy"];

/** Основная карта + половина веса уточняющей — паритет с iOS. */
export function mergeTarotSphereBumps(main?: TarotSphereBump, clarifier?: TarotSphereBump): TarotSphereBump {
  const out: TarotSphereBump = {};
  TAROT_SPHERE_BUMP_KEYS.forEach((id) => {
    const v = (main?.[id] ?? 0) + (clarifier?.[id] ?? 0) * 0.5;
    const rounded = Math.round(v);
    if (rounded !== 0) out[id] = rounded;
  });
  return out;
}
