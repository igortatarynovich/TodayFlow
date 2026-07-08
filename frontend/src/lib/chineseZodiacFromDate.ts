/** Client-side Chinese zodiac — mirrors backend `ChineseHoroscopeService` (DOB-only). */

const ANIMALS = [
  "Rat",
  "Ox",
  "Tiger",
  "Rabbit",
  "Dragon",
  "Snake",
  "Horse",
  "Goat",
  "Monkey",
  "Rooster",
  "Dog",
  "Pig",
] as const;

const ELEMENTS = ["Wood", "Fire", "Earth", "Metal", "Water"] as const;

export type ChineseZodiacAnimal = (typeof ANIMALS)[number];
export type ChineseZodiacElement = (typeof ELEMENTS)[number];

const CNY: Record<number, string> = {
  2000: "2000-02-05",
  2001: "2001-01-24",
  2002: "2002-02-12",
  2003: "2003-02-01",
  2004: "2004-01-22",
  2005: "2005-02-09",
  2006: "2006-01-29",
  2007: "2007-02-18",
  2008: "2008-02-07",
  2009: "2009-01-26",
  2010: "2010-02-14",
  2011: "2011-02-03",
  2012: "2012-01-23",
  2013: "2013-02-10",
  2014: "2014-01-31",
  2015: "2015-02-19",
  2016: "2016-02-08",
  2017: "2017-01-28",
  2018: "2018-02-16",
  2019: "2019-02-05",
  2020: "2020-01-25",
  2021: "2021-02-12",
  2022: "2022-02-01",
  2023: "2023-01-22",
  2024: "2024-02-10",
  2025: "2025-01-29",
  2026: "2026-02-17",
};

export const CHINESE_ANIMAL_RU: Record<ChineseZodiacAnimal, { name: string; traits: string[] }> = {
  Rat: { name: "Крыса", traits: ["Находчивость", "Гибкость", "Быстрота"] },
  Ox: { name: "Бык", traits: ["Упорство", "Надёжность", "Сила"] },
  Tiger: { name: "Тигр", traits: ["Смелость", "Независимость", "Решительность"] },
  Rabbit: { name: "Кролик", traits: ["Такт", "Интуиция", "Гармония"] },
  Dragon: { name: "Дракон", traits: ["Масштаб", "Харизма", "Амбиции"] },
  Snake: { name: "Змея", traits: ["Мудрость", "Глубина", "Интуиция"] },
  Horse: { name: "Лошадь", traits: ["Энергия", "Свобода", "Движение"] },
  Goat: { name: "Коза", traits: ["Творчество", "Мягкость", "Эмпатия"] },
  Monkey: { name: "Обезьяна", traits: ["Любопытство", "Остроумие", "Гибкость"] },
  Rooster: { name: "Петух", traits: ["Точность", "Наблюдательность", "Уверенность"] },
  Dog: { name: "Собака", traits: ["Верность", "Честность", "Защита"] },
  Pig: { name: "Свинья", traits: ["Щедрость", "Тепло", "Оптимизм"] },
};

export const CHINESE_ELEMENT_RU: Record<ChineseZodiacElement, string[]> = {
  Wood: ["Рост", "Гибкость", "Идеи"],
  Fire: ["Страсть", "Импульс", "Драйв"],
  Earth: ["Стабильность", "Практичность", "Опора"],
  Metal: ["Структура", "Точность", "Сила"],
  Water: ["Адаптивность", "Интуиция", "Глубина"],
};

function parseIsoDate(iso: string): Date | null {
  const m = iso.match(/^(\d{4})-(\d{2})-(\d{2})/);
  if (!m) return null;
  return new Date(Number(m[1]), Number(m[2]) - 1, Number(m[3]));
}

function chineseCalendarYear(birthDate: Date): number {
  const year = birthDate.getFullYear();
  const cny = CNY[year];
  if (cny) {
    const boundary = new Date(cny);
    if (birthDate < boundary) return year - 1;
    return year;
  }
  if (birthDate.getMonth() === 0 || (birthDate.getMonth() === 1 && birthDate.getDate() < 20)) {
    return year - 1;
  }
  return year;
}

export type ChineseZodiacProfile = {
  animal: ChineseZodiacAnimal;
  animalRu: string;
  element: ChineseZodiacElement;
  traits: string[];
  chineseYear: number;
};

export function chineseZodiacFromIsoDate(birthDateIso: string): ChineseZodiacProfile | null {
  const birthDate = parseIsoDate(birthDateIso);
  if (!birthDate) return null;

  const chineseYear = chineseCalendarYear(birthDate);
  const animal = ANIMALS[(chineseYear - 4) % 12];
  const element = ELEMENTS[Math.floor(((chineseYear - 4) % 10) / 2)];

  const animalMeta = CHINESE_ANIMAL_RU[animal];
  const elementTraits = CHINESE_ELEMENT_RU[element];
  const traits = Array.from(new Set([...animalMeta.traits.slice(0, 2), elementTraits[0]])).slice(0, 3);

  return {
    animal,
    animalRu: animalMeta.name,
    element,
    traits,
    chineseYear,
  };
}
