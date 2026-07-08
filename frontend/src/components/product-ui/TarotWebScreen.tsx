"use client";

import Link from "next/link";
import type { ReactNode } from "react";
import { useMemo } from "react";
import { ProductWebShellConfigBridge, type ProductWebShellConfig } from "@/components/product-ui/productWebShellConfig";
import { productWebShellChromeBundle } from "@/components/product-ui/productWebShellChrome";
import type { FlowPracticesChromeLocale } from "@/components/today/flowPracticesMainTabChrome";
import { getLocale } from "@/lib/i18n";
import type { CoreProfile } from "@/lib/types";
import v2 from "@/design-system/layouts/productV2Surface.module.css";
import l from "@/design-system/layouts/dsLayouts.module.css";
import pl from "@/design-system/layouts/productPageLayout.module.css";

export type TarotWebScreenProps = {
  displayName?: string | null;
  profileMeta?: string | null;
  coreProfile?: CoreProfile | null;
  locale?: FlowPracticesChromeLocale;
  backHref?: string;
  backLabel?: string;
  topicLabel?: string;
  theme?: "light" | "dark";
  rail?: ReactNode;
  children: ReactNode;
};

export function TarotWebScreen({
  displayName,
  profileMeta,
  coreProfile,
  locale,
  backHref = "/tarot",
  backLabel,
  topicLabel,
  theme = "light",
  rail,
  children,
}: TarotWebScreenProps) {
  const resolvedLocale: FlowPracticesChromeLocale =
    locale ?? (getLocale() === "ru" ? "ru" : "en");
  const shell = useMemo(() => productWebShellChromeBundle(resolvedLocale), [resolvedLocale]);
  const resolvedBackLabel = backLabel ?? shell.tarotBackLabel;

  const shellConfig = useMemo((): ProductWebShellConfig => {
    return {
      testId: "tarot-web-screen",
      theme,
      mainWide: theme === "light",
      displayName,
      profileMeta,
      coreProfile,
      rail,
    };
  }, [coreProfile, displayName, profileMeta, rail, theme]);

  return (
    <>
      <ProductWebShellConfigBridge config={shellConfig} />
      {theme === "light" ? (
        <div className={l.productWebContentV2}>
          <div className={`${v2.pageRoot} ${pl.subPageRoot}`}>
            <Link href={backHref} className={pl.textLink}>
              ← {resolvedBackLabel}
              {topicLabel ? ` · ${topicLabel}` : ""}
            </Link>
            {children}
          </div>
        </div>
      ) : (
        <div className={pl.subPageRoot}>
          <Link href={backHref} className={pl.textLink}>
            ← {resolvedBackLabel}
            {topicLabel ? ` · ${topicLabel}` : ""}
          </Link>
          {children}
        </div>
      )}
    </>
  );
}
