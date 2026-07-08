import type { TodayGuideRitualContext } from "@/lib/todayNarrativeApi";

export type IntentTheme = "focus" | "energy" | "relationships" | "money" | "clarity" | "calm";

export type RealityState = "overloaded" | "stable" | "unclear" | "tired" | "motivated" | "sensitive";

export type OnboardingChipOption<T extends string> = {
  slug: T;
  label: string;
  hint?: string;
};

export const INTENT_CHIP_OPTIONS: OnboardingChipOption<IntentTheme>[] = [
  { slug: "focus", label: "Фокус", hint: "работа и концентрация" },
  { slug: "energy", label: "Энергия", hint: "темп и силы" },
  { slug: "relationships", label: "Отношения", hint: "близость и контакт" },
  { slug: "money", label: "Деньги", hint: "ресурсы и опоры" },
  { slug: "clarity", label: "Ясность", hint: "решения без шума" },
  { slug: "calm", label: "Спокойствие", hint: "мягкий ритм дня" },
];

export const REALITY_CHIP_OPTIONS: OnboardingChipOption<RealityState>[] = [
  { slug: "overloaded", label: "Перегруз", hint: "слишком много всего" },
  { slug: "stable", label: "Стабильно", hint: "ровный, нормальный день" },
  { slug: "unclear", label: "Нет ясности", hint: "не понимаю, куда идти" },
  { slug: "tired", label: "Усталость", hint: "мало сил" },
  { slug: "motivated", label: "Есть энергия", hint: "хочется двигаться" },
  { slug: "sensitive", label: "Чувствительность", hint: "эмоции на поверхности" },
];

const STORAGE_KEY = "todayflow_onboarding_context_v1";

export type OnboardingContext = {
  intent_theme?: IntentTheme;
  reality_state?: RealityState;
  day_key?: string;
};

export function todayDayKey(now = new Date()): string {
  const y = now.getFullYear();
  const m = String(now.getMonth() + 1).padStart(2, "0");
  const d = String(now.getDate()).padStart(2, "0");
  return `${y}-${m}-${d}`;
}

function isBrowser(): boolean {
  return typeof window !== "undefined";
}

export function readOnboardingContext(): OnboardingContext {
  if (!isBrowser()) return {};
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return {};
    const parsed = JSON.parse(raw) as OnboardingContext;
    return parsed && typeof parsed === "object" ? parsed : {};
  } catch {
    return {};
  }
}

function writeOnboardingContext(next: OnboardingContext): void {
  if (!isBrowser()) return;
  localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
}

export function saveIntentTheme(theme: IntentTheme, dayKey = todayDayKey()): OnboardingContext {
  const next: OnboardingContext = {
    ...readOnboardingContext(),
    intent_theme: theme,
    day_key: dayKey,
  };
  writeOnboardingContext(next);
  return next;
}

export function saveRealityState(state: RealityState, dayKey = todayDayKey()): OnboardingContext {
  const next: OnboardingContext = {
    ...readOnboardingContext(),
    reality_state: state,
    day_key: dayKey,
  };
  writeOnboardingContext(next);
  return next;
}

export function hasOnboardingIntent(ctx = readOnboardingContext(), dayKey = todayDayKey()): boolean {
  return Boolean(ctx.intent_theme && ctx.day_key === dayKey);
}

export function hasOnboardingReality(ctx = readOnboardingContext(), dayKey = todayDayKey()): boolean {
  return Boolean(ctx.reality_state && ctx.day_key === dayKey);
}

/** Intent was saved at least once — used for Profile access (not day-scoped). */
export function hasOnboardingIntentRecorded(ctx = readOnboardingContext()): boolean {
  return Boolean(ctx.intent_theme);
}

/** Reality was saved at least once — used for Profile access (not day-scoped). */
export function hasOnboardingRealityRecorded(ctx = readOnboardingContext()): boolean {
  return Boolean(ctx.reality_state);
}

/** Maps onboarding picks into ritual_context for the first Today narrative call. */
export function buildOnboardingRitualContext(ctx = readOnboardingContext()): TodayGuideRitualContext | null {
  if (!ctx.intent_theme && !ctx.reality_state) return null;
  const out: TodayGuideRitualContext = {};
  if (ctx.intent_theme) out.head_topic = ctx.intent_theme;
  if (ctx.reality_state) out.mood = ctx.reality_state;
  if (ctx.intent_theme) {
    out.day_events = [`onboarding intent: ${ctx.intent_theme}`];
    if (ctx.reality_state) out.day_events.push(`onboarding state: ${ctx.reality_state}`);
  }
  return out;
}

export function buildOnboardingEventIdempotencyKey(
  event: "onboarding_intent_selected" | "onboarding_reality_selected",
  slug: string,
  dayKey = todayDayKey(),
): string {
  return `${event}:${dayKey}:${slug}`;
}
