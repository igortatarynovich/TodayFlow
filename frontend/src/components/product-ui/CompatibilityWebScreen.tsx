"use client";

import type { ReactNode } from "react";
import { useMemo } from "react";
import { DsBody, DsRailPanel } from "@/design-system";
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
  railHint?: string;
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
  railHint,
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
  const resolvedRailHint = railHint ?? chrome.railHint;

  const resolvedRail =
    rail ?? (
      <DsRailPanel title={chrome.railReadTitle}>
        <DsBody size="sm" muted>
          {resolvedRailHint}
        </DsBody>
      </DsRailPanel>
    );

  return (
    <ProductPageScreen
      testId="compatibility-web-screen"
      title={resolvedTitle}
      subtitle={resolvedSubtitle}
      displayName={displayName}
      profileMeta={profileMeta}
      coreProfile={coreProfile}
      locale={resolvedLocale}
      rail={resolvedRail}
      hideHeader={hideHeader}
      contentClassName={contentClassName ?? pl.content}
    >
      {children}
    </ProductPageScreen>
  );
}
