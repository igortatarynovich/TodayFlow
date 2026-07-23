"use client";

import Link from "next/link";
import type { ReactNode } from "react";
import { ProductWebGuestNav } from "@/components/product-ui/ProductWebGuestNav";
import { IconOrbitalGlyph } from "@/design-system";
import { guestSignupHref } from "@/lib/guestAccessStore";
import { t } from "@/lib/i18n";
import s from "@/components/product-ui/productWebScreens.module.css";

export type OnboardingWebScreenProps = {
  step?: number;
  totalSteps?: number;
  title: string;
  lead?: string;
  footer?: ReactNode;
  showGuestNav?: boolean;
  children: ReactNode;
};

export function OnboardingWebScreen({
  step = 1,
  totalSteps = 3,
  title,
  lead,
  footer,
  showGuestNav = true,
  children,
}: OnboardingWebScreenProps) {
  const safeTotal = Math.max(1, totalSteps);
  const safeStep = Math.min(Math.max(1, step), safeTotal);

  return (
    <div className={s.onboardingWebFrame} data-testid="onboarding-web-screen">
      {showGuestNav ? (
        <div className={s.authWebMarketingNav}>
          <ProductWebGuestNav
            ctaHref={guestSignupHref()}
            ctaLabel={t("onboarding.nav.cta", "Построить мой профиль")}
          />
        </div>
      ) : (
        <Link href="/" className={s.onboardingWebLogo}>
          <IconOrbitalGlyph />
          TodayFlow
        </Link>
      )}

      <div className={s.onboardingWebCard}>
        <div
          className={s.onboardingWebProgress}
          style={{ gridTemplateColumns: `repeat(${safeTotal}, 1fr)` }}
          aria-hidden
        >
          {Array.from({ length: safeTotal }, (_, index) => index + 1).map((index) => (
            <span
              key={index}
              className={`${s.onboardingWebProgressStep} ${index <= safeStep ? s.onboardingWebProgressStepActive : ""}`.trim()}
            />
          ))}
        </div>

        <header>
          <h1 className={s.onboardingWebTitle}>{title}</h1>
          {lead ? <p className={s.onboardingWebLead}>{lead}</p> : null}
        </header>

        {children}

        {footer ? <div className={s.onboardingWebFooter}>{footer}</div> : null}
      </div>
    </div>
  );
}
