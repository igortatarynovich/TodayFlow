"use client";

import type { ReactNode } from "react";
import { useMemo } from "react";
import { DsPageHeader, DsStreakRing, DsWeeklyBars, IconCalendar } from "@/design-system";
import {
  ProductWebShellConfigBridge,
  type ProductWebShellConfig,
} from "@/components/product-ui/productWebShellConfig";
import {
  practicesExperienceChromeBundle,
  type FlowPracticesChromeLocale,
} from "@/components/today/flowPracticesMainTabChrome";
import { getLocale } from "@/lib/i18n";
import type { CoreProfile } from "@/lib/types";
import l from "@/design-system/layouts/dsLayouts.module.css";
import s from "@/components/product-ui/productWebScreens.module.css";

export type PracticesWebScreenProps = {
  displayName?: string | null;
  profileMeta?: string | null;
  coreProfile?: CoreProfile | null;
  locale?: FlowPracticesChromeLocale;
  title: string;
  subtitle: string;
  streakDays?: number;
  activePractices?: number;
  bestStreakDays?: number;
  weeklyRhythm?: number[];
  /** When false, hide decorative zero-progress rail (honest empty state). */
  showProgressRail?: boolean;
  rail?: ReactNode;
  /** Figma 162:1522 — dashboard layout, wide main, no classic header/rail. */
  variant?: "default" | "v2";
  children: ReactNode;
};

export function PracticesWebScreen({
  displayName,
  profileMeta,
  coreProfile,
  locale,
  title,
  subtitle,
  streakDays = 0,
  activePractices = 0,
  bestStreakDays = 0,
  weeklyRhythm = [],
  showProgressRail = true,
  rail,
  variant = "default",
  children,
}: PracticesWebScreenProps) {
  const resolvedLocale: FlowPracticesChromeLocale =
    locale ?? (getLocale() === "ru" ? "ru" : "en");
  const pc = useMemo(() => practicesExperienceChromeBundle(resolvedLocale), [resolvedLocale]);
  const bestStreakSuffix = pc.practicesRailDaysSuffix;
  const todayLabel = new Intl.DateTimeFormat(resolvedLocale === "ru" ? "ru-RU" : "en-US", {
    weekday: "long",
    day: "numeric",
    month: "long",
  }).format(new Date());
  const isV2 = variant === "v2";

  const shellConfig = useMemo((): ProductWebShellConfig => {
    const defaultRail =
      showProgressRail && (streakDays > 0 || weeklyRhythm.length > 0) ? (
        <>
          <section className={s.practicesRailSection} aria-labelledby="practices-streak">
            <h2 id="practices-streak" className={s.practicesRailEyebrow}>
              {pc.practicesRailMyStreak}
            </h2>
            <DsStreakRing days={streakDays} label="" />
            <div className={s.practicesRailStats}>
              {activePractices > 0 ? (
                <p className={s.practicesRailStatMain}>
                  {pc.practicesRailActiveCount} {activePractices}
                </p>
              ) : null}
              {bestStreakDays > 0 ? (
                <p className={s.practicesRailStatSub}>
                  {pc.practicesRailBestStreak} {bestStreakDays} {bestStreakSuffix}
                </p>
              ) : null}
            </div>
          </section>
          {weeklyRhythm.length > 0 ? (
            <section className={s.practicesRailSection} aria-labelledby="practices-weekly">
              <h2 id="practices-weekly" className={s.practicesRailEyebrow}>
                {pc.practicesRailWeeklyRhythm}
              </h2>
              <DsWeeklyBars values={weeklyRhythm} />
            </section>
          ) : null}
        </>
      ) : undefined;

    return {
      testId: "practices-web-screen",
      displayName,
      profileMeta,
      coreProfile,
      mainWide: true,
      fullMain: false,
      rail: rail !== undefined ? rail : defaultRail,
    };
  }, [
    activePractices,
    bestStreakDays,
    bestStreakSuffix,
    coreProfile,
    displayName,
    isV2,
    pc.practicesRailActiveCount,
    pc.practicesRailBestStreak,
    pc.practicesRailMyStreak,
    pc.practicesRailWeeklyRhythm,
    profileMeta,
    rail,
    showProgressRail,
    streakDays,
    weeklyRhythm,
  ]);

  return (
    <>
      <ProductWebShellConfigBridge config={shellConfig} />
      {!isV2 ? (
        <DsPageHeader
          title={title}
          subtitle={subtitle}
          dateLabel={todayLabel}
          dateIcon={<IconCalendar />}
        />
      ) : null}
      <div className={isV2 ? `${l.practicesWebContent} ${l.practicesWebContentV2}` : s.practicesWebContent}>
        {children}
      </div>
    </>
  );
}
