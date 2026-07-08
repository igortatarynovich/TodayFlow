"use client";

import Link from "next/link";
import type { ReactNode } from "react";
import { DsButton } from "@/design-system";
import { OnboardingWebScreen } from "@/components/product-ui/OnboardingWebScreen";

export type OnboardingAuthGateProps = {
  title: string;
  body: string;
  loginHref: string;
  signupHref: string;
};

export function OnboardingAuthGate({ title, body, loginHref, signupHref }: OnboardingAuthGateProps) {
  return (
    <OnboardingWebScreen step={1} title={title} lead={body}>
      <div style={{ display: "flex", gap: "0.65rem", justifyContent: "center", flexWrap: "wrap" }}>
        <Link href={signupHref}>
          <DsButton variant="primary">Создать аккаунт</DsButton>
        </Link>
        <Link href={loginHref}>
          <DsButton variant="secondary">Войти</DsButton>
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
