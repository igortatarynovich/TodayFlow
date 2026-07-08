/** Strip technical / kitchen-sink phrasing from tarot reading copy (RU + EN). */
const BANNED_PATTERNS: RegExp[] = [
  /справочное значение[^.]*\.?\s*/gi,
  /reference meaning[^.]*\.?\s*/gi,
  /это тормоз[^.]*\.?\s*/gi,
  /use it as a brake[^.]*\.?\s*/gi,
  /профиль (?:лишь )?подстраивает[^.]*\.?\s*/gi,
  /profile only tunes[^.]*\.?\s*/gi,
  /на сервере не больше[^.]*\.?\s*/gi,
  /position_weights[^.]*\.?\s*/gi,
  /tension slot[^.]*\.?\s*/gi,
  /напряжение видно в позиции[^.]*\.?\s*/gi,
  /Сегодня ориентируйся[^.]*\.?\s*/gi,
  /Today, orient yourself[^.]*\.?\s*/gi,
  /не должен дублировать общий фон дня[^.]*\.?\s*/gi,
  /задаёт ракурс интерпретации[^.]*\.?\s*/gi,
  /только профессиональная рамка расклада[^.]*\.?\s*/gi,
  /Позиции с большим весом[^.]*\.?\s*/gi,
  /Slots like risk, obstacle[^.]*\.?\s*/gi,
  /Не делай:\s*/gi,
  /Do not:\s*/gi,
];

const POSITION_ID_LABELS_RU: Record<string, string> = {
  tension: "Где напряжение",
  attraction: "Что тебя тянет",
  pull: "Что тебя тянет",
  obstacle: "Что останавливает",
  block: "Что останавливает",
  stop: "Что останавливает",
  risk: "Где риск",
  next_step: "Следующий шаг",
  outcome: "К чему ведёт",
  past: "Откуда это",
  present: "Что сейчас",
  future: "Куда движется",
  advice: "Совет расклада",
  hidden: "Скрытый слой",
  core: "Сердце вопроса",
  challenge: "Главное препятствие",
  strength: "Твоя опора",
  weakness: "Уязвимое место",
  hope: "Надежда",
  fear: "Страх",
  environment: "Окружение",
  you: "Ты в этой истории",
  partner: "Другой человек",
  dynamic: "Динамика между вами",
  nuance: "Тонкий слой",
  illusion: "Иллюзия",
  harm: "Что может ранить",
};

const POSITION_ID_LABELS_EN: Record<string, string> = {
  tension: "Where the tension is",
  attraction: "What pulls you",
  pull: "What pulls you",
  obstacle: "What holds you back",
  block: "What holds you back",
  stop: "What holds you back",
  risk: "Where the risk is",
  next_step: "Next step",
  outcome: "Where this leads",
  past: "Where this comes from",
  present: "What's happening now",
  future: "Where it's moving",
  advice: "Spread advice",
  hidden: "Hidden layer",
  core: "Heart of the question",
  challenge: "Main obstacle",
  strength: "Your anchor",
  weakness: "Vulnerable spot",
  hope: "Hope",
  fear: "Fear",
  environment: "Environment",
  you: "You in this story",
  partner: "The other person",
  dynamic: "Dynamic between you",
  nuance: "Subtle layer",
  illusion: "Illusion",
  harm: "What could hurt",
};

export function sanitizeTarotStoryText(raw: string | null | undefined): string {
  if (!raw?.trim()) return "";
  let text = raw.trim();
  for (const pattern of BANNED_PATTERNS) {
    text = text.replace(pattern, "");
  }
  return text.replace(/\s{2,}/g, " ").replace(/\s+([,.!?])/g, "$1").trim();
}

export function humanizeTarotPositionLabel(
  position: string,
  positionId: string | null | undefined,
  positionPrompt: string | null | undefined,
  locale: "ru" | "en",
): string {
  if (positionPrompt?.trim()) return sanitizeTarotStoryText(positionPrompt);
  const id = (positionId || position || "").trim().toLowerCase();
  const map = locale === "ru" ? POSITION_ID_LABELS_RU : POSITION_ID_LABELS_EN;
  if (id && map[id]) return map[id];
  const cleaned = sanitizeTarotStoryText(
    position.replace(/^(?:position|позиция)[:\s]*/i, "").trim(),
  );
  if (/^[a-z_]+$/.test(cleaned)) {
    const fromClean = map[cleaned];
    if (fromClean) return fromClean;
    return cleaned.replace(/_/g, " ");
  }
  return cleaned || (locale === "ru" ? "Карта расклада" : "Spread card");
}

export function cleanTarotCardMeaning(raw: string | null | undefined): string {
  const text = sanitizeTarotStoryText(raw);
  return text.replace(/^Справочное значение[^:]*:\s*/i, "").replace(/^Reference meaning[^:]*:\s*/i, "");
}

export function dedupeSentences(parts: string[]): string {
  const seen = new Set<string>();
  const out: string[] = [];
  for (const part of parts) {
    const cleaned = sanitizeTarotStoryText(part);
    if (!cleaned) continue;
    const key = cleaned.toLowerCase();
    if (seen.has(key)) continue;
    seen.add(key);
    out.push(cleaned);
  }
  return out.join(" ");
}

export function formatTarotCardCount(count: number, locale: "ru" | "en"): string {
  if (locale === "en") return count === 1 ? "1 card" : `${count} cards`;
  const mod10 = count % 10;
  const mod100 = count % 100;
  if (mod10 === 1 && mod100 !== 11) return `${count} карта`;
  if (mod10 >= 2 && mod10 <= 4 && (mod100 < 12 || mod100 > 14)) return `${count} карты`;
  return `${count} карт`;
}
