"use client";

/**
 * Static guest demo for Compatibility hub — shows what the product creates
 * before auth (no invented personal pair; editorial example only).
 */
import { DsBody, DsButton } from "@/design-system";
import journeyStyles from "@/components/product-ui/ProductJourneyScene.module.css";
import type { FlowPracticesChromeLocale } from "@/components/today/flowPracticesMainTabChrome";

const DEMO_RU = {
  eyebrow: "Пример результата",
  pair: "Овен · Весы · любовь",
  dynamicsLabel: "Главная динамика",
  dynamics:
    "Разный темп: один ускоряет решения, другой держит ритм и смысл. Сила — в дополнении, не в споре «кто быстрее».",
  strengthLabel: "Сильная сторона",
  strength: "Легко говорить о чувствах, когда есть общее «зачем» — разговор становится опорой, а не тестом.",
  tensionLabel: "Зона напряжения",
  tension: "Решения под давлением: кто ведёт, кто ждёт. Без явной договорённости копится обида «меня не слышат».",
  tipLabel: "Практический совет",
  tip: "Перед важным разговором договоритесь о времени и цели — не о том, «кто прав».",
  note: "Это демонстрация формата. Свой расчёт — по знакам или после создания Today.",
  ctaAnalyze: "Проверить свою пару",
  ctaToday: "Создать мой Today",
} as const;

const DEMO_EN = {
  eyebrow: "Sample result",
  pair: "Aries · Libra · love",
  dynamicsLabel: "Main dynamic",
  dynamics:
    "Different pace: one speeds decisions, the other holds rhythm and meaning. Strength is complementarity — not a race.",
  strengthLabel: "Strength",
  strength: "Easy to talk about feelings when there is a shared why — conversation becomes support, not a test.",
  tensionLabel: "Tension zone",
  tension: "Decisions under pressure: who leads, who waits. Without an explicit agreement, “I’m not heard” builds up.",
  tipLabel: "Practical tip",
  tip: "Before an important talk, agree on time and purpose — not on who is right.",
  note: "This is a format demo. Your reading is by signs or after creating Today.",
  ctaAnalyze: "Check your pair",
  ctaToday: "Create my Today",
} as const;

export function CompatibilityGuestDemo({
  locale = "ru",
}: {
  locale?: FlowPracticesChromeLocale;
}) {
  const copy = locale === "ru" ? DEMO_RU : DEMO_EN;

  return (
    <div data-testid="compatibility-guest-demo" className={journeyStyles.demoPanel}>
      <p className={journeyStyles.pairSub}>{copy.eyebrow}</p>
      <p className={journeyStyles.pairTitle}>{copy.pair}</p>

      <div className={journeyStyles.demoGrid}>
        <div>
          <p className={journeyStyles.demoLabel}>{copy.dynamicsLabel}</p>
          <DsBody size="sm">{copy.dynamics}</DsBody>
        </div>
        <div>
          <p className={journeyStyles.demoLabel}>{copy.strengthLabel}</p>
          <DsBody size="sm">{copy.strength}</DsBody>
        </div>
        <div>
          <p className={journeyStyles.demoLabel}>{copy.tensionLabel}</p>
          <DsBody size="sm">{copy.tension}</DsBody>
        </div>
        <div>
          <p className={journeyStyles.demoLabel}>{copy.tipLabel}</p>
          <DsBody size="sm">{copy.tip}</DsBody>
        </div>
      </div>

      <DsBody size="sm" muted>
        {copy.note}
      </DsBody>

      <div className={journeyStyles.actionRow}>
        <DsButton href="/compatibility/analyze">{copy.ctaAnalyze}</DsButton>
        <DsButton href="/onboarding/welcome?fresh=1" variant="secondary">
          {copy.ctaToday}
        </DsButton>
      </div>
    </div>
  );
}
