import type { AccountProfile, InsightDepthTier, SubscriptionBillingLevel } from "@/lib/types";

export type { InsightDepthTier };

/** Дублирует маппинг бэкенда billing_to_insight_depth — только для старых ответов /auth/me без полей. */
export function insightDepthFromBilling(level: SubscriptionBillingLevel | undefined): InsightDepthTier {
  if (level === "pro") return "premium";
  if (level === "lite") return "pro";
  return "free";
}

/**
 * Глубина инсайта для UI: только из данных API (insight_depth_tier или subscription_level).
 * Не смешиваем с отчётами (has_full_report) — иначе расходится с /today/narrative.
 */
export function insightDepthFromProfile(profile: AccountProfile | null): InsightDepthTier {
  const t = profile?.insight_depth_tier;
  if (t === "free" || t === "pro" || t === "premium") return t;
  return insightDepthFromBilling(profile?.subscription_level);
}

/**
 * Paid / trial depth access (lite|pro, legacy is_paid, active|trialing).
 * Canon: trial = full depth experience; subscription unlocks deepen layers.
 */
export function hasPaidSubscriptionAccess(profile: AccountProfile | null | undefined): boolean {
  if (!profile) return false;
  if (profile.subscription_level === "lite" || profile.subscription_level === "pro") return true;
  if (profile.is_paid) return true;
  const status = (profile.subscription_status || "").toLowerCase();
  if (status === "active" || status === "trialing") return true;
  return insightDepthFromProfile(profile) !== "free";
}

/** Примеры для paywall / превью: один день, разная глубина. */
export const INSIGHT_PAYWALL_COPY = {
  headline: "Платишь за ощущение, что тебя понимают",
  sub: "Тариф — не «набор функций», а насколько глубоко мы раскрываем смысл твоего дня.",
  freeSample: "Сегодня не перегружай себя — и закрой хотя бы одну задачу.",
  plusTeaser: "Ты перегружаешь себя сильнее, когда не видишь ощутимого результата — сегодня важен один завершённый шаг.",
  plusLabel: "Plus — объяснение и паттерны",
  proTeaser: "Долгие процессы без отдачи тебя выжимают: тебе ближе движение с понятным смыслом, чем бесконечная рутина.",
  proLabel: "Pro — жизненные сценарии и глубина",
  ctaHref: "/pricing",
  ctaLabel: "Сравнить глубину",
} as const;

/**
 * Типы инсайтов по ступеням прогрессии (контент-матрица; подписка открывает 2–4 в тексте).
 * order 1 = всегда доступно на free как поведенческий слой.
 */
export const INSIGHT_PROGRESSION_STAGES = [
  { order: 1, id: "behavior", title: "Поведение", description: "Что сделать сегодня, чего избегать." },
  { order: 2, id: "patterns", title: "Паттерны", description: "Почему так, причины, повторяющиеся реакции." },
  { order: 3, id: "scenarios", title: "Сценарии", description: "Как темы дня стыкуются с типичными ситуациями." },
  { order: 4, id: "life_strategy", title: "Стратегии жизни", description: "Какой формат жизни тебе подходит и где теряется энергия." },
] as const;
