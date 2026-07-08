// Утилиты для работы со знаками зодиака, стихиями и модальностями

export type ZodiacSign = 
  | "Aries" | "Taurus" | "Gemini" | "Cancer" 
  | "Leo" | "Virgo" | "Libra" | "Scorpio" 
  | "Sagittarius" | "Capricorn" | "Aquarius" | "Pisces";

export type Element = "Fire" | "Earth" | "Air" | "Water";
export type Modality = "Cardinal" | "Fixed" | "Mutable";

// Маппинг русских названий на английские (для нормализации)
const russianToEnglish: Record<string, ZodiacSign> = {
  "овен": "Aries",
  "aries": "Aries",
  "телец": "Taurus",
  "taurus": "Taurus",
  "близнецы": "Gemini",
  "gemini": "Gemini",
  "рак": "Cancer",
  "cancer": "Cancer",
  "лев": "Leo",
  "leo": "Leo",
  "дева": "Virgo",
  "virgo": "Virgo",
  "весы": "Libra",
  "libra": "Libra",
  "скорпион": "Scorpio",
  "scorpio": "Scorpio",
  "стрелец": "Sagittarius",
  "sagittarius": "Sagittarius",
  "козерог": "Capricorn",
  "capricorn": "Capricorn",
  "водолей": "Aquarius",
  "aquarius": "Aquarius",
  "рыбы": "Pisces",
  "pisces": "Pisces",
};

// Маппинг знаков на стихии
const signToElement: Record<ZodiacSign, Element> = {
  Aries: "Fire",
  Taurus: "Earth",
  Gemini: "Air",
  Cancer: "Water",
  Leo: "Fire",
  Virgo: "Earth",
  Libra: "Air",
  Scorpio: "Water",
  Sagittarius: "Fire",
  Capricorn: "Earth",
  Aquarius: "Air",
  Pisces: "Water",
};

// Маппинг знаков на модальности
const signToModality: Record<ZodiacSign, Modality> = {
  Aries: "Cardinal",
  Taurus: "Fixed",
  Gemini: "Mutable",
  Cancer: "Cardinal",
  Leo: "Fixed",
  Virgo: "Mutable",
  Libra: "Cardinal",
  Scorpio: "Fixed",
  Sagittarius: "Mutable",
  Capricorn: "Cardinal",
  Aquarius: "Fixed",
  Pisces: "Mutable",
};

// Русские названия
export const elementNames: Record<Element, string> = {
  Fire: "Огонь",
  Earth: "Земля",
  Air: "Воздух",
  Water: "Вода",
};

export const modalityNames: Record<Modality, string> = {
  Cardinal: "Кардинальная",
  Fixed: "Фиксированная",
  Mutable: "Мутабельная",
};

/**
 * Нормализует название знака к английскому формату
 * Поддерживает русские и английские названия в любом регистре
 */
/** Канонический slug знака (Aries..Pisces) из en/ru подписи API. */
export function normalizeZodiacSign(sign: string): ZodiacSign | null {
  return normalizeSign(sign);
}

function normalizeSign(sign: string): ZodiacSign | null {
  if (!sign) return null;
  
  const normalized = sign.toLowerCase().trim();
  
  // Прямое совпадение с английским названием
  if (normalized in signToElement) {
    return normalized as ZodiacSign;
  }
  
  // Поиск в маппинге русских названий
  if (normalized in russianToEnglish) {
    return russianToEnglish[normalized];
  }
  
  // Попытка найти по частичному совпадению (для случаев типа "Aries" vs "aries")
  const found = Object.keys(russianToEnglish).find(key => 
    key.toLowerCase() === normalized || 
    key.toLowerCase().includes(normalized) ||
    normalized.includes(key.toLowerCase())
  );
  
  if (found) {
    return russianToEnglish[found];
  }
  
  return null;
}

/**
 * Получить стихию знака
 * Поддерживает русские и английские названия
 */
export function getElement(sign: string): Element | null {
  const normalizedSign = normalizeSign(sign);
  if (!normalizedSign) return null;
  return signToElement[normalizedSign] || null;
}

/**
 * Получить модальность знака
 * Поддерживает русские и английские названия
 */
export function getModality(sign: string): Modality | null {
  const normalizedSign = normalizeSign(sign);
  if (!normalizedSign) return null;
  return signToModality[normalizedSign] || null;
}

/**
 * Вычислить баланс стихий из знаков
 */
export function calculateElementBalance(signs: string[]): Record<Element, number> {
  const balance: Record<Element, number> = {
    Fire: 0,
    Earth: 0,
    Air: 0,
    Water: 0,
  };

  signs.forEach((sign) => {
    const element = getElement(sign);
    if (element) {
      balance[element] += 1;
    }
  });

  // Нормализуем к относительным значениям (0-1)
  const total = signs.length || 1;
  Object.keys(balance).forEach((key) => {
    balance[key as Element] = balance[key as Element] / total;
  });

  return balance;
}

/**
 * Вычислить баланс модальностей из знаков
 */
export function calculateModalityBalance(signs: string[]): Record<Modality, number> {
  const balance: Record<Modality, number> = {
    Cardinal: 0,
    Fixed: 0,
    Mutable: 0,
  };

  signs.forEach((sign) => {
    const modality = getModality(sign);
    if (modality) {
      balance[modality] += 1;
    }
  });

  // Нормализуем к относительным значениям (0-1)
  const total = signs.length || 1;
  Object.keys(balance).forEach((key) => {
    balance[key as Modality] = balance[key as Modality] / total;
  });

  return balance;
}

