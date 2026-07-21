"use client";

import type { ReactNode } from "react";
import { useMemo } from "react";
import { ProductWebShellConfigBridge, type ProductWebShellConfig } from "@/components/product-ui/productWebShellConfig";
import { profileWebChromeBundle } from "@/components/product-ui/profileWebChrome";
import type { FlowPracticesChromeLocale } from "@/components/today/flowPracticesMainTabChrome";
import type { ProfileRailAnchor } from "@/lib/product-ui/profileWebFigmaHelpers";
import { getLocale } from "@/lib/i18n";
import type { CoreProfile } from "@/lib/types";
import l from "@/design-system/layouts/dsLayouts.module.css";
import s from "@/components/product-ui/productWebScreens.module.css";

export type ProfileWebScreenProps = {
  displayName?: string | null;
  profileMeta?: string | null;
  coreProfile?: CoreProfile | null;
  locale?: FlowPracticesChromeLocale;
  title?: string;
  subtitle?: string;
  identityPills?: string[];
  railAnchors?: ProfileRailAnchor[];
  /** Custom right-rail content (e.g. Profile v2 depth nav). Wins over railAnchors. */
  rail?: ReactNode;
  /** @deprecated PR-2: compat link alone must not keep the rail column. Ignored. */
  compatibilityHref?: string | null;
  /** v2: Figma profile-v2-system — content in main; depth nav in shell rail. */
  variant?: "default" | "v2";
  children: ReactNode;
};

export function ProfileWebScreen({
  displayName,
  profileMeta,
  coreProfile,
  locale,
  title,
  subtitle,
  identityPills = [],
  railAnchors = [],
  rail,
  variant = "default",
  children,
}: ProfileWebScreenProps) {
  const resolvedLocale: FlowPracticesChromeLocale =
    locale ?? (getLocale() === "ru" ? "ru" : "en");
  const chrome = useMemo(() => profileWebChromeBundle(resolvedLocale), [resolvedLocale]);
  const resolvedTitle = title ?? chrome.pageTitle;
  const resolvedSubtitle = subtitle ?? chrome.pageSubtitle;

  const todayLabel = new Intl.DateTimeFormat(resolvedLocale === "ru" ? "ru-RU" : "en-US", {
    day: "numeric",
    month: "long",
  }).format(new Date());

  const isV2 = variant === "v2";

  const shellConfig = useMemo((): ProductWebShellConfig => {
    const anchorsRail =
      railAnchors.length > 0 ? (
        <section className={s.profileRailPanel} aria-labelledby="profile-rail-anchors">
          <p id="profile-rail-anchors" className={s.profileRailTitle}>
            {chrome.railAnchorsTitle}
          </p>
          <ul className={s.profileRailList}>
            {railAnchors.map((item) => (
              <li key={item.id} className={s.profileRailRow}>
                <span className={s.profileRailLeft}>
                  <span className={s.profileRailIcon}>{item.icon}</span>
                  <span className={s.profileRailLabel}>{item.label}</span>
                </span>
                <span className={s.profileRailValue}>{item.value}</span>
              </li>
            ))}
          </ul>
        </section>
      ) : undefined;

    return {
      testId: "profile-web-screen",
      displayName,
      profileMeta,
      coreProfile,
      mainWide: true,
      fullMain: false,
      // PR-2: rail only with real content — depth nav (v2) or map anchors.
      rail: rail ?? anchorsRail,
    };
  }, [
    chrome.railAnchorsTitle,
    coreProfile,
    displayName,
    profileMeta,
    rail,
    railAnchors,
  ]);

  return (
    <>
      <ProductWebShellConfigBridge config={shellConfig} />
      {!isV2 ? (
        <div className={s.pageHeader}>
          <div>
            <h1 className={s.profilePageTitle}>{resolvedTitle}</h1>
            {identityPills.length ? (
              <div className={s.identityPills}>
                {identityPills.map((pill) => (
                  <span key={pill} className={s.identityPill}>
                    {pill}
                  </span>
                ))}
              </div>
            ) : (
              <p className={s.profilePageSubtitle}>{resolvedSubtitle}</p>
            )}
          </div>
          <p className={s.profileDateLabel}>
            {chrome.todayPrefix} {todayLabel}
          </p>
        </div>
      ) : null}
      <section
        className={isV2 ? `${l.profileWebContent} ${l.profileWebContentV2}` : l.profileWebContent}
        aria-label={chrome.profileAria}
      >
        {children}
      </section>
    </>
  );
}
