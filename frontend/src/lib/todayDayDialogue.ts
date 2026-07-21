/**
 * Today Day Dialogue — explicit signals when missing/stale (learning → PIM).
 * Staleness: day-scoped capture per local_date.
 */

export type TodayMorningMood = {
  id: string;
  label: string;
  icon: string;
};

export type TodayFocusTopic = {
  id: string;
  label: string;
};

export type TodayPromiseSuggestion = {
  id: string;
  text: string;
};

export type TodayEveningHighlight = {
  id: string;
  label: string;
};

/** Indirect day check-ins — learning without test-like UX. Rotates by date. */
export type TodaySoftDayCheckIn = {
  id: string;
  question: string;
  options: Array<{ id: string; label: string }>;
};

export const TODAY_SOFT_DAY_CHECKINS: TodaySoftDayCheckIn[] = [
  {
    id: "pace",
    question: "Сейчас день скорее про темп или про паузу?",
    options: [
      { id: "tempo", label: "Темп" },
      { id: "pause", label: "Паузу" },
      { id: "mix", label: "И то, и другое" },
      { id: "unsure", label: "Пока не ясно" },
    ],
  },
  {
    id: "clarity",
    question: "Что сегодня важнее — ясность или терпение?",
    options: [
      { id: "clarity", label: "Ясность" },
      { id: "patience", label: "Терпение" },
      { id: "both", label: "Оба" },
      { id: "unsure", label: "Зависит от часа" },
    ],
  },
  {
    id: "inner",
    question: "Сейчас ближе — разобраться внутри или сделать шаг снаружи?",
    options: [
      { id: "inner", label: "Внутри" },
      { id: "outer", label: "Снаружи" },
      { id: "both", label: "По очереди" },
      { id: "unsure", label: "Пока не выбрал" },
    ],
  },
];

export function pickSoftDayCheckIn(dateISO: string): TodaySoftDayCheckIn {
  const seed = dateISO.split("-").reduce((acc, p) => acc + Number(p || 0), 0);
  return TODAY_SOFT_DAY_CHECKINS[Math.abs(seed) % TODAY_SOFT_DAY_CHECKINS.length]!;
}

export const TODAY_DAY_DIALOGUE_COPY = {
  moodTitle: "Как ты входишь в этот день?",
  moodLead: "От этого зависит, на что я сделаю акцент дальше.",
  focusTitle: "Что сейчас ближе всего к сердцу?",
  focusLead: "Проведу день через эту тему.",
} as const;

export const TODAY_MORNING_MOODS: TodayMorningMood[] = [
  { id: "calm", label: "Спокойно", icon: "😊" },
  { id: "driven", label: "Полон сил", icon: "⚡" },
  { id: "tired", label: "Устал", icon: "😴" },
  { id: "anxious", label: "Тревожно", icon: "😟" },
  { id: "overloaded", label: "Перегружен", icon: "🤯" },
  { id: "inspired", label: "Вдохновлён", icon: "❤️" },
];

export const TODAY_FOCUS_TOPICS: TodayFocusTopic[] = [
  { id: "work", label: "Работа" },
  { id: "money", label: "Деньги" },
  { id: "relations", label: "Отношения" },
  { id: "family", label: "Семья" },
  { id: "health", label: "Здоровье" },
  { id: "growth", label: "Саморазвитие" },
  { id: "decision", label: "Решение" },
  { id: "other", label: "Другое" },
];

/** Legacy static chips — do not surface in production UI (empty affirmation formulas). */
export const TODAY_PROMISE_SUGGESTIONS: TodayPromiseSuggestion[] = [];

function asSoftIntention(raw: string): string {
  const t = raw.replace(/\s+/g, " ").trim();
  if (!t) return "";
  // Keep observational; avoid forcing «Сегодня я…» affirmation template.
  if (/^сегодня/i.test(t)) return t.endsWith(".") ? t : `${t}.`;
  const sentence = t.charAt(0).toUpperCase() + t.slice(1);
  return sentence.endsWith(".") ? sentence : `${sentence}.`;
}

/**
 * Intentions only from the day's computed action — never a canned affirmation list.
 * Empty when there is nothing real to offer (user can write their own).
 */
export function buildTodayPromiseSuggestions(input: {
  primaryAction?: string | null;
  focusTopicId?: string | null;
  developmentPoint?: string | null;
}): TodayPromiseSuggestion[] {
  const out: TodayPromiseSuggestion[] = [];
  const seen = new Set<string>();

  const push = (id: string, text: string) => {
    const normalized = text.replace(/\s+/g, " ").trim();
    if (!normalized) return;
    const key = normalized.toLowerCase();
    if (seen.has(key)) return;
    seen.add(key);
    out.push({ id, text: normalized.length <= 140 ? normalized : `${normalized.slice(0, 137)}…` });
  };

  const primary = input.primaryAction?.trim();
  if (primary) push("contract_primary", asSoftIntention(primary));

  return out.slice(0, 1);
}

export const TODAY_EVENING_HIGHLIGHTS: TodayEveningHighlight[] = [
  { id: "work", label: "Работа" },
  { id: "conversation", label: "Разговор" },
  { id: "rest", label: "Отдых" },
  { id: "surprise", label: "Неожиданность" },
  { id: "mood", label: "Настроение" },
  { id: "money", label: "Деньги" },
  { id: "other", label: "Другое" },
];

const LOW_ENERGY_MOODS = new Set(["tired", "overloaded", "anxious", "heavy", "quiet_wish"]);

export function isLowEnergyMood(moodId: string | null | undefined): boolean {
  if (!moodId) return false;
  return LOW_ENERGY_MOODS.has(moodId.trim().toLowerCase());
}

export function moodLabelRu(moodId: string | null | undefined): string | null {
  if (!moodId) return null;
  return TODAY_MORNING_MOODS.find((m) => m.id === moodId)?.label ?? null;
}

/** Micro-signals are day-scoped: one mood/focus capture per calendar day. */
export function isSignalCapturedToday(
  dateISO: string,
  capturedAtMs: number | null | undefined,
): boolean {
  if (!capturedAtMs) return false;
  const d = new Date(capturedAtMs);
  const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
  return key === dateISO;
}

export function shouldAskMorningDialogue(input: {
  dateISO: string;
  morningMoodId: string | null;
  focusTopicId: string | null;
  morningMoodCapturedAtMs?: number | null;
  focusTopicCapturedAtMs?: number | null;
}): boolean {
  const moodNeeded =
    !input.morningMoodId || !isSignalCapturedToday(input.dateISO, input.morningMoodCapturedAtMs ?? null);
  const focusNeeded =
    !input.focusTopicId || !isSignalCapturedToday(input.dateISO, input.focusTopicCapturedAtMs ?? null);
  return moodNeeded || focusNeeded;
}

export function shouldAskMorningMood(input: {
  dateISO: string;
  morningMoodId: string | null;
  morningMoodCapturedAtMs?: number | null;
}): boolean {
  return (
    !input.morningMoodId || !isSignalCapturedToday(input.dateISO, input.morningMoodCapturedAtMs ?? null)
  );
}

export function shouldAskMorningFocus(input: {
  dateISO: string;
  focusTopicId: string | null;
  focusTopicCapturedAtMs?: number | null;
}): boolean {
  return (
    !input.focusTopicId || !isSignalCapturedToday(input.dateISO, input.focusTopicCapturedAtMs ?? null)
  );
}

export function focusTopicLabel(topicId: string | null): string | null {
  if (!topicId) return null;
  return TODAY_FOCUS_TOPICS.find((t) => t.id === topicId)?.label ?? null;
}

/** Narrative lens: explain card/day through user's current focus. */
export function focusLensPrefix(topicId: string | null): string {
  switch (topicId) {
    case "work":
      return "В работе";
    case "money":
      return "В деньгах и ресурсах";
    case "relations":
      return "В отношениях";
    case "family":
      return "В семье";
    case "health":
      return "В теме здоровья и энергии";
    case "growth":
      return "В саморазвитии";
    case "decision":
      return "В решении, которое сейчас важно";
    default:
      return "Сегодня";
  }
}

export function promiseOutcomeLabelRu(outcome: "done" | "partial" | "not_done"): string {
  switch (outcome) {
    case "done":
      return "Да";
    case "partial":
      return "Частично";
    case "not_done":
      return "Было непросто";
  }
}
