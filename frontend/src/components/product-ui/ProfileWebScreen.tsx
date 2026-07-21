"use client";

import Link from "next/link";
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
  compatibilityHref?: string | null;
  /** v2: Figma profile-v2-system — hero + depth ladder inside main; hide classic header. */
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
  compatibilityHref,
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
    // Always keep the product 3-column grid (left nav · center · right rail).
    return {
      testId: "profile-web-screen",
      displayName,
      profileMeta,
      coreProfile,
      mainWide: true,
      fullMain: false,
      rail: (
        <>
          {railAnchors.length > 0 ? (
            <section className={s.profileRailPanel} aria-labelledby="profile-rail-anchors">
              <h2 id="profile-rail-anchors" className={s.profileRailTitle}>
                {chrome.railAnchorsTitle}
              </h2>
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
          ) : (
            <section className={s.profileRailPanel} aria-labelledby="profile-rail-hint">
              <h2 id="profile-rail-hint" className={s.profileRailTitle}>
                {chrome.railAnchorsTitle}
              </h2>
              <p className={s.profileRailHint}>{resolvedSubtitle}</p>
            </section>
          )}
          {compatibilityHref ? (
            <section className={s.profileRailPanel} aria-labelledby="profile-rail-links">
              <h2 id="profile-rail-links" className={s.profileRailTitle}>
                {chrome.railLinksTitle}
              </h2>
              <p className={s.profileRailHint}>{chrome.railLinksHint}</p>
              <Link href={compatibilityHref} className={l.railLink}>
                {chrome.railCompatibilityLink}
              </Link>
            </section>
          ) : null}
        </>
      ),
    };
  }, [
    chrome.railAnchorsTitle,
    chrome.railCompatibilityLink,
    chrome.railLinksHint,
    chrome.railLinksTitle,
    compatibilityHref,
    coreProfile,
    displayName,
    profileMeta,
    railAnchors,
    resolvedSubtitle,
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
            ) : !identityPills.length ? (
              <p className={s.profilePageSubtitle}>{resolvedSubtitle}</p>
            ) : null}
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
