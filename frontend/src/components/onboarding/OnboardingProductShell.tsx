"use client";

import Link from "next/link";
import type { ReactNode } from "react";
import { DsButton } from "@/design-system";
import { OnboardingWebScreen } from "@/components/product-ui/OnboardingWebScreen";
import { guestSignupHref } from "@/lib/guestAccessStore";

export type OnboardingAuthGateProps = {
  title: string;
  body: string;
  loginHref: string;
  /** Ignored — registration is always the soft onboarding canon. */
  signupHref?: string;
};

/** Single registration CTA (soft Today) + login for returning users. */
export function OnboardingAuthGate({ title, body, loginHref }: OnboardingAuthGateProps) {
  return (
    <OnboardingWebScreen step={1} title={title} lead={body}>
      <div style={{ display: "grid", gap: "0.85rem", justifyItems: "center" }}>
        <Link href={guestSignupHref()}>
          <DsButton variant="primary">Создать мой Today</DsButton>
        </Link>
        <Link href={loginHref} className="orbit-body-sm" style={{ color: "#78716c", textDecoration: "underline" }}>
          Уже есть аккаунт? Войти
        </Link>
      </div>
    </OnboardingWebScreen>
  );
}

export function OnboardingProductLoading({ children }: { children: ReactNode }) {
  return (
    <OnboardingWebScreen step={1} title="Загрузка…">
      <div style={{ minHeight: "12rem", display: "grid", placeItems: "center" }}>{children}</div>
    </OnboardingWebScreen>
  );
}
