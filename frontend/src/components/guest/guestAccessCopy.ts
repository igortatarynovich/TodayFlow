import { GUEST_ACCESS_LIMITS } from "@/lib/guestAccessLimits";

export const GUEST_ACCESS_COPY = {
  tarotLimitTitle: "Бесплатный расклад уже использован",
  tarotLimitBody: `Без аккаунта доступен ${GUEST_ACCESS_LIMITS.tarotSpreads} расклад. Войдите или создайте Today — полный Таро откроется в вашем ритме дня.`,
  compatLimitTitle: "Бесплатные проверки закончились",
  compatLimitBody: `Без аккаунта — ${GUEST_ACCESS_LIMITS.compatibilityChecks} проверки совместимости. Войдите или создайте Today, чтобы сохранять пары и возвращаться к ним.`,
  practiceLockedTitle: "Эта практика — после регистрации",
  practiceLockedBody: "Без аккаунта доступны базовые бесплатные практики. Создайте Today — персональные рекомендации откроются вместе с экраном дня.",
  sessionEndedCta: "Войти снова",
  sessionEndedBody: (fallback: string) =>
    `Сессия завершилась. Войдите снова — ваш профиль и прогресс уже сохранены. ${fallback}`,
  remainingTarot: (n: number) =>
    n === 1 ? "1 бесплатный расклад" : n === 0 ? "Бесплатный расклад использован" : `${n} бесплатных расклада`,
  remainingCompat: (n: number) =>
    n === 1 ? "1 проверка осталась" : n === 0 ? "Проверки использованы" : `${n} проверки осталось`,
} as const;
