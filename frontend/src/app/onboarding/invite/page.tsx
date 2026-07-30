"use client";

import Link from "next/link";
import { DsButton } from "@/design-system";
import { VALUE_FIRST_PATHS } from "@/lib/guestProfileDraft";
import { ValueFirstOnboardingShell } from "@/components/onboarding/valueFirst/ValueFirstOnboardingShell";
import styles from "@/components/onboarding/valueFirst/valueFirstOnboarding.module.css";

const INVITE_COPY = {
  title: "Today становится точным, когда система знает тебя",
  lead:
    "Это не гороскоп по знаку — это твоя карта. Дата (и по возможности время и место) рождения даёт картину, которая не меняется день ото дня. Собирается один раз — дальше работает на Today, Совместимость и Таро.",
  body:
    "Следующий шаг — коротко: имя и дата рождения. Если точного времени нет — можно продолжить; потеряется часть точности, а не весь путь.",
  cta: "Построить мой Profile",
  secondary: "Сначала посмотреть демо-день",
} as const;

/** Profile-invite — why Profile before collecting birth data (Guest Story Surface P0). */
export default function OnboardingInvitePage() {
  return (
    <ValueFirstOnboardingShell
      step={1}
      turnId="profile_invite"
      title={INVITE_COPY.title}
      lead={INVITE_COPY.lead}
      backHref={VALUE_FIRST_PATHS.demoToday}
    >
      <p className={styles.hint} data-testid="onboarding-invite-body">
        {INVITE_COPY.body}
      </p>
      <div className={styles.ctaRow}>
        <DsButton
          variant="primary"
          href={`${VALUE_FIRST_PATHS.welcome}?fresh=1`}
          data-testid="onboarding-invite-continue"
        >
          {INVITE_COPY.cta}
        </DsButton>
        <Link href={VALUE_FIRST_PATHS.demoToday} className={styles.textLink} data-testid="onboarding-invite-demo">
          {INVITE_COPY.secondary}
        </Link>
      </div>
    </ValueFirstOnboardingShell>
  );
}
