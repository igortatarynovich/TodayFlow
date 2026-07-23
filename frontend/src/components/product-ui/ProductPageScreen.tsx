"use client";

/**
 * Product Page Standard v1 — единая обёртка для всех in-app экранов.
 *
 * Anatomy:
 *   ProductWebShellLayout (sidebar + identity)
 *     └─ productWebContentV2 (max-width canvas)
 *         └─ pageRoot
 *             ├─ pageHeader — title, subtitle, date chip (optional)
 *             └─ content — screen-specific blocks
 *
 * PR-2: context rail only when `rail` or (`railTitle` + real `railHint`) is set.
 * Never echo title/subtitle into an empty rail for layout symmetry.
 *
 * Do NOT: orbit-page, custom hero images, per-page font sizes, DsPageHeader on product routes.
 * DO: productV2Surface tokens + productPageLayout grids + DsButton/DsRailPanel.
 */
import type { ReactNode } from "react";
import { useMemo } from "react";
import { DsBody, DsButton, DsRailPanel, IconCalendar } from "@/design-system";
import { ProductWebShellConfigBridge, type ProductWebShellConfig } from "@/components/product-ui/productWebShellConfig";
import {
  ProductShellEmpty,
  ProductShellError,
  ProductShellLoading,
} from "@/components/product-ui/ProductShellStates";
import type { FlowPracticesChromeLocale } from "@/components/today/flowPracticesMainTabChrome";
import { getLocale } from "@/lib/i18n";
import { useProductDayNightTheme } from "@/lib/useProductDayNightTheme";
import type { CoreProfile } from "@/lib/types";
import v2 from "@/design-system/layouts/productV2Surface.module.css";
import pl from "@/design-system/layouts/productPageLayout.module.css";
import l from "@/design-system/layouts/dsLayouts.module.css";

export type ProductPageGuestState = {
  message: string;
  ctaHref?: string;
  ctaLabel?: string;
};

export type ProductPageErrorState = {
  message: string;
  retryLabel?: string;
  onRetry?: () => void;
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
  /** Real context rail only — omit when empty. */
  rail?: ReactNode;
  /** Optional titled rail panel; requires non-empty railHint (no title-only filler). */
  railTitle?: string;
  railHint?: string;
  hideHeader?: boolean;
  hideDatePill?: boolean;
  mainWide?: boolean;
  contentClassName?: string;
  loading?: boolean;
  loadingLabel?: string;
  guest?: ProductPageGuestState;
  error?: ProductPageErrorState;
  empty?: { message: string; action?: ReactNode };
  children?: ReactNode;
};

function resolveOptionalRail(
  rail: ReactNode | undefined,
  railTitle: string | undefined,
  railHint: string | undefined,
): ReactNode | undefined {
  if (rail != null) return rail;
  const hint = typeof railHint === "string" ? railHint.trim() : "";
  if (railTitle && hint) {
    return (
      <DsRailPanel title={railTitle}>
        <DsBody size="sm" muted>
          {hint}
        </DsBody>
      </DsRailPanel>
    );
  }
  return undefined;
}

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
  error,
  empty,
  children,
}: ProductPageScreenProps) {
  const resolvedLocale: FlowPracticesChromeLocale =
    locale ?? (getLocale() === "ru" ? "ru" : "en");
  const theme = useProductDayNightTheme();

  const todayLabel = new Intl.DateTimeFormat(resolvedLocale === "ru" ? "ru-RU" : "en-US", {
    weekday: "long",
    day: "numeric",
    month: "long",
  }).format(new Date());

  const resolvedRail = resolveOptionalRail(rail, railTitle, railHint);

  const shellConfig = useMemo((): ProductWebShellConfig => {
    return {
      testId,
      mainWide,
      displayName,
      profileMeta,
      coreProfile,
      theme,
      rail: resolvedRail,
    };
  }, [coreProfile, displayName, mainWide, profileMeta, resolvedRail, testId, theme]);

  const body = (() => {
    if (loading) {
      return <ProductShellLoading label={loadingLabel} />;
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

    if (error) {
      return (
        <ProductShellError
          message={error.message}
          retryLabel={error.retryLabel}
          onRetry={error.onRetry}
        />
      );
    }

    if (empty) {
      return <ProductShellEmpty message={empty.message} action={empty.action} />;
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
