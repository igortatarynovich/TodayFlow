"use client";

/**
 * Product Page Standard v1 — единая обёртка для всех in-app экранов.
 *
 * Anatomy (always):
 *   ProductWebShellLayout (sidebar + identity)
 *     └─ productWebContentV2 (max-width canvas)
 *         └─ pageRoot (vertical gap 1.75rem)
 *             ├─ pageHeader (surfaceGlass) — title, subtitle, date chip
 *             └─ content — screen-specific blocks (panels, grids)
 *
 * Do NOT: orbit-page, custom hero images, per-page font sizes, DsPageHeader on product routes.
 * DO: productV2Surface tokens + productPageLayout grids + DsButton/DsRailPanel.
 */
import type { ReactNode } from "react";
import { useMemo } from "react";
import { DsBody, DsButton, DsRailPanel, IconCalendar } from "@/design-system";
import { LoadingSpinner } from "@/components/orbit";
import { ProductWebShellConfigBridge, type ProductWebShellConfig } from "@/components/product-ui/productWebShellConfig";
import type { FlowPracticesChromeLocale } from "@/components/today/flowPracticesMainTabChrome";
import { getLocale } from "@/lib/i18n";
import type { CoreProfile } from "@/lib/types";
import v2 from "@/design-system/layouts/productV2Surface.module.css";
import pl from "@/design-system/layouts/productPageLayout.module.css";
import l from "@/design-system/layouts/dsLayouts.module.css";

export type ProductPageGuestState = {
  message: string;
  ctaHref?: string;
  ctaLabel?: string;
};

export type ProductPageScreenProps = {
  testId?: string;
  title: string;
  subtitle?: string;
  eyebrow?: string;
  displayName?: string | null;
  profileMeta?: string | null;
  coreProfile?: CoreProfile | null;
  locale?: FlowPracticesChromeLocale;
  rail?: ReactNode;
  railTitle?: string;
  railHint?: string;
  hideHeader?: boolean;
  hideDatePill?: boolean;
  mainWide?: boolean;
  contentClassName?: string;
  loading?: boolean;
  loadingLabel?: string;
  guest?: ProductPageGuestState;
  children?: ReactNode;
};

export function ProductPageScreen({
  testId = "product-page-screen",
  title,
  subtitle,
  eyebrow,
  displayName,
  profileMeta,
  coreProfile,
  locale,
  rail,
  railTitle,
  railHint,
  hideHeader = false,
  hideDatePill = false,
  mainWide = true,
  contentClassName,
  loading = false,
  loadingLabel,
  guest,
  children,
}: ProductPageScreenProps) {
  const resolvedLocale: FlowPracticesChromeLocale =
    locale ?? (getLocale() === "ru" ? "ru" : "en");

  const todayLabel = new Intl.DateTimeFormat(resolvedLocale === "ru" ? "ru-RU" : "en-US", {
    weekday: "long",
    day: "numeric",
    month: "long",
  }).format(new Date());

  const shellConfig = useMemo((): ProductWebShellConfig => {
    return {
      testId,
      mainWide,
      displayName,
      profileMeta,
      coreProfile,
      // Always reserve the right rail column — never collapse to a 2-column product page.
      rail:
        rail ??
        (railTitle || railHint ? (
          <DsRailPanel title={railTitle ?? title}>
            {railHint ? (
              <DsBody size="sm" muted>
                {railHint}
              </DsBody>
            ) : null}
          </DsRailPanel>
        ) : (
          <DsRailPanel title={title}>
            <DsBody size="sm" muted>
              {subtitle ?? ""}
            </DsBody>
          </DsRailPanel>
        )),
    };
  }, [coreProfile, displayName, mainWide, profileMeta, rail, railHint, railTitle, subtitle, testId, title]);

  const body = (() => {
    if (loading) {
      return (
        <div className={pl.centerState}>
          <LoadingSpinner size="lg" />
          {loadingLabel ? <p className={v2.bodyLead}>{loadingLabel}</p> : null}
        </div>
      );
    }

    if (guest) {
      return (
        <div className={pl.loginGate}>
          <h1 className={v2.sectionTitle}>{title}</h1>
          <p className={v2.bodyLead}>{guest.message}</p>
          {guest.ctaHref && guest.ctaLabel ? (
            <DsButton href={guest.ctaHref}>{guest.ctaLabel}</DsButton>
          ) : null}
        </div>
      );
    }

    return (
      <>
        {hideHeader ? null : (
          <header className={pl.pageHeader}>
            <div>
              {eyebrow ? <p className={v2.eyebrow}>{eyebrow}</p> : null}
              <h1 className={v2.displayTitle}>{title}</h1>
              {subtitle ? <p className={v2.bodyLead}>{subtitle}</p> : null}
            </div>
            {hideDatePill ? null : (
              <p className={`${v2.chip} ${pl.datePill}`}>
                <IconCalendar aria-hidden />
                {todayLabel}
              </p>
            )}
          </header>
        )}
        {children ? <div className={contentClassName ?? pl.content}>{children}</div> : null}
      </>
    );
  })();

  return (
    <>
      <ProductWebShellConfigBridge config={shellConfig} />
      <div className={l.productWebContentV2}>
        <div className={v2.pageRoot}>{body}</div>
      </div>
    </>
  );
}

/** Re-export layout primitives for page content (grids, cards, forms). */
export { pl as productPageLayout };
