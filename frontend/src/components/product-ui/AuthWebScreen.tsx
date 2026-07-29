"use client";

import Link from "next/link";
import type { ReactNode } from "react";
import { ProductWebGuestNav } from "@/components/product-ui/ProductWebGuestNav";
import { IconOrbitalGlyph } from "@/design-system";
import { LoadingSpinner } from "@/components/orbit";
import s from "@/components/product-ui/productWebScreens.module.css";

export type AuthWebScreenProps = {
  mode: "login" | "signup";
  onSelectLogin: () => void;
  onSelectSignup: () => void;
  loginTabLabel: string;
  signupTabLabel: string;
  /** Login-only: hide password-signup tab; signup CTA goes to soft onboarding. */
  loginOnly?: boolean;
  /** Single-column form (no marketing sidebar column). */
  formOnly?: boolean;
  headline: string;
  lead: string;
  productLine?: string;
  guestNavCtaHref?: string;
  guestNavCtaLabel?: string;
  visible?: boolean;
  loading?: boolean;
  children?: ReactNode;
};

export function AuthWebScreen({
  mode,
  onSelectLogin,
  onSelectSignup,
  loginTabLabel,
  signupTabLabel,
  loginOnly = false,
  formOnly = false,
  headline,
  lead,
  productLine,
  guestNavCtaHref,
  guestNavCtaLabel,
  visible = true,
  loading = false,
  children,
}: AuthWebScreenProps) {
  if (loading) {
    return (
      <div className={s.authWebFrame} data-testid="auth-web-screen">
        <div className={s.authWebLoading}>
          <LoadingSpinner size="lg" />
        </div>
      </div>
    );
  }

  const header = (
    <header className={formOnly ? s.authWebFormHeader : s.authWebHeader}>
      {loginOnly ? (
        <div className={s.authWebTabs}>
          <span className={`${s.authWebTab} ${s.authWebTabActive}`}>{loginTabLabel}</span>
        </div>
      ) : (
        <div className={s.authWebTabs}>
          <button
            type="button"
            className={`${s.authWebTab} ${mode === "login" ? s.authWebTabActive : ""}`}
            onClick={onSelectLogin}
          >
            {loginTabLabel}
          </button>
          <button
            type="button"
            className={`${s.authWebTab} ${mode === "signup" ? s.authWebTabActive : ""}`}
            onClick={onSelectSignup}
          >
            {signupTabLabel}
          </button>
        </div>
      )}
      <h1 className={`${s.authWebTitle} ${visible ? s.authWebReveal : ""}`}>{headline}</h1>
      {lead ? <p className={`${s.authWebLead} ${visible ? s.authWebReveal : ""}`}>{lead}</p> : null}
      {productLine ? (
        <p className={`${s.authWebProductLine} ${visible ? s.authWebReveal : ""}`}>{productLine}</p>
      ) : null}
    </header>
  );

  return (
    <div className={s.authWebFrame} data-testid="auth-web-screen">
      {guestNavCtaHref && guestNavCtaLabel ? (
        <div className={s.authWebMarketingNav}>
          <ProductWebGuestNav ctaHref={guestNavCtaHref} ctaLabel={guestNavCtaLabel} />
        </div>
      ) : (
        <Link href="/" className={s.onboardingWebLogo}>
          <IconOrbitalGlyph />
          TodayFlow
        </Link>
      )}

      {formOnly ? (
        <div className={`${s.authWebFormLayout} ${visible ? s.authWebGridVisible : ""}`}>
          {header}
          {children}
        </div>
      ) : (
        <>
          {header}
          <div className={`${s.authWebGrid} ${visible ? s.authWebGridVisible : ""}`}>{children}</div>
        </>
      )}
    </div>
  );
}
