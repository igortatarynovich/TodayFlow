"use client";

import type { ReactNode } from "react";
import { useMemo } from "react";
import { ProductPageScreen } from "@/components/product-ui/ProductPageScreen";
import { compatibilityWebChromeBundle } from "@/components/product-ui/compatibilityWebChrome";
import type { FlowPracticesChromeLocale } from "@/components/today/flowPracticesMainTabChrome";
import { getLocale } from "@/lib/i18n";
import type { CoreProfile } from "@/lib/types";
import pl from "@/design-system/layouts/productPageLayout.module.css";

export type CompatibilityWebScreenProps = {
  displayName?: string | null;
  profileMeta?: string | null;
  coreProfile?: CoreProfile | null;
  locale?: FlowPracticesChromeLocale;
  title?: string;
  subtitle?: string;
  /** Real context rail only — omit when empty (PR-2). */
  rail?: ReactNode;
  hideHeader?: boolean;
  contentClassName?: string;
  children: ReactNode;
};

export function CompatibilityWebScreen({
  displayName,
  profileMeta,
  coreProfile,
  locale,
  title,
  subtitle,
  rail,
  hideHeader = false,
  contentClassName,
  children,
}: CompatibilityWebScreenProps) {
  const resolvedLocale: FlowPracticesChromeLocale =
    locale ?? (getLocale() === "ru" ? "ru" : "en");
  const chrome = useMemo(() => compatibilityWebChromeBundle(resolvedLocale), [resolvedLocale]);
  const resolvedTitle = title ?? chrome.pageTitle;
  const resolvedSubtitle = subtitle ?? chrome.pageSubtitle;

  return (
    <ProductPageScreen
      testId="compatibility-web-screen"
      title={resolvedTitle}
      subtitle={resolvedSubtitle}
      displayName={displayName}
      profileMeta={profileMeta}
      coreProfile={coreProfile}
      locale={resolvedLocale}
      rail={rail}
      hideHeader={hideHeader}
      contentClassName={contentClassName ?? pl.content}
    >
      {children}
    </ProductPageScreen>
  );
}
