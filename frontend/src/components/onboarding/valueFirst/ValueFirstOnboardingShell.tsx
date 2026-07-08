"use client";

import Link from "next/link";
import type { ReactNode } from "react";
import { OnboardingWebScreen } from "@/components/product-ui/OnboardingWebScreen";
import s from "@/components/product-ui/productWebScreens.module.css";
import styles from "@/components/onboarding/valueFirst/valueFirstOnboarding.module.css";

const VALUE_FIRST_TOTAL_STEPS = 5;

type Props = {
  step?: number;
  turnId: string;
  title: string;
  lead?: string;
  children: ReactNode;
  backHref?: string | null;
  wide?: boolean;
  footer?: ReactNode;
  /** @deprecated deepen content — use footer or inline in children */
  deepen?: ReactNode;
  deepenLabel?: string;
};

/** Guest value-first onboarding — product shell (Figma 29:777 extended). */
export function ValueFirstOnboardingShell({
  step = 1,
  turnId,
  title,
  lead,
  children,
  backHref,
  footer,
}: Props) {
  return (
    <div data-testid={`onboarding-value-first-${turnId}`}>
      <OnboardingWebScreen step={step} totalSteps={VALUE_FIRST_TOTAL_STEPS} title={title} lead={lead} footer={footer}>
        {backHref ? (
          <Link href={backHref} className={s.practiceSessionBack}>
            ← Назад
          </Link>
        ) : null}
        <div className={styles.body}>{children}</div>
      </OnboardingWebScreen>
    </div>
  );
}
