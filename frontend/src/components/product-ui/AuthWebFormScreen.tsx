"use client";

import Link from "next/link";
import type { ReactNode } from "react";
import { IconOrbitalGlyph } from "@/design-system";
import { LoadingSpinner } from "@/components/orbit";
import s from "@/components/product-ui/productWebScreens.module.css";

export type AuthWebFormScreenProps = {
  title: string;
  lead?: string;
  backHref?: string;
  backLabel?: string;
  loading?: boolean;
  visible?: boolean;
  children?: ReactNode;
};

export function AuthWebFormScreen({
  title,
  lead,
  backHref,
  backLabel = "← Назад",
  loading = false,
  visible = true,
  children,
}: AuthWebFormScreenProps) {
  if (loading) {
    return (
      <div className={s.authWebFrame} data-testid="auth-web-form-screen">
        <div className={s.authWebLoading}>
          <LoadingSpinner size="lg" />
        </div>
      </div>
    );
  }

  return (
    <div className={s.authWebFrame} data-testid="auth-web-form-screen">
      <Link href="/" className={s.onboardingWebLogo}>
        <IconOrbitalGlyph />
        TodayFlow
      </Link>

      <div className={`${s.authWebFormLayout} ${visible ? s.authWebGridVisible : ""}`}>
        {backHref ? (
          <Link href={backHref} className={s.practiceSessionBack}>
            {backLabel}
          </Link>
        ) : null}
        <header className={s.authWebFormHeader}>
          <h1 className={s.authWebTitle}>{title}</h1>
          {lead ? <p className={s.authWebLead}>{lead}</p> : null}
        </header>
        <div className={s.authWebPanel}>{children}</div>
      </div>
    </div>
  );
}
