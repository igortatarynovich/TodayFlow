/** Человекочитаемые подписи тел и стихий в UI профиля (внутренние ключи API могут оставаться на английском). */

export const NATAL_BODY_LABEL_RU: Record<string, string> = {
  Sun: "Солнце",
  Moon: "Луна",
  Mercury: "Меркурий",
  Venus: "Венера",
  Mars: "Марс",
  Jupiter: "Юпитер",
  Saturn: "Сатурн",
  Uranus: "Уран",
  Neptune: "Нептун",
  Pluto: "Плутон",
  Rising: "Асцендент",
};

const ELEMENT_RU: Record<string, string> = {
  air: "воздух",
  fire: "огонь",
  earth: "земля",
  water: "вода",
};

export function natalBodyLabelRu(key: string): string {
  return NATAL_BODY_LABEL_RU[key] ?? key;
}

export function sunElementLabelRu(raw: string | null | undefined): string | null {
  if (!raw?.trim()) return null;
  const k = raw.trim().toLowerCase();
  return ELEMENT_RU[k] ?? raw.trim();
}
