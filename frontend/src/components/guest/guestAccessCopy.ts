import { GUEST_ACCESS_LIMITS } from "@/lib/guestAccessLimits";

export const GUEST_ACCESS_COPY = {
  tarotLimitTitle: "Бесплатный расклад уже использован",
  tarotLimitBody: `Без регистрации доступен ${GUEST_ACCESS_LIMITS.tarotSpreads} расклад. Создай Today — и открой полный Таро в своём ритме дня.`,
  compatLimitTitle: "Бесплатные проверки закончились",
  compatLimitBody: `Без регистрации — ${GUEST_ACCESS_LIMITS.compatibilityChecks} проверки совместимости. Создай Today, чтобы сохранять пары и возвращаться к ним.`,
  practiceLockedTitle: "Эта практика — после регистрации",
  practiceLockedBody: "Без аккаунта доступны базовые бесплатные практики. Создай Today — персональные рекомендации откроются вместе с экраном дня.",
  remainingTarot: (n: number) =>
    n === 1 ? "1 бесплатный расклад" : n === 0 ? "Бесплатный расклад использован" : `${n} бесплатных расклада`,
  remainingCompat: (n: number) =>
    n === 1 ? "1 проверка осталась" : n === 0 ? "Проверки использованы" : `${n} проверки осталось`,
} as const;
