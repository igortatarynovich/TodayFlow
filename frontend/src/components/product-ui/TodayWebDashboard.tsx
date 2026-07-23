"use client";

import type { ReactNode } from "react";
import { useMemo } from "react";
import { DsOrbitalViz, IconCalendar, IconSun } from "@/design-system";
import v2 from "@/design-system/layouts/productV2Surface.module.css";
import l from "@/design-system/layouts/dsLayouts.module.css";
import { ProductWebShellConfigBridge, type ProductWebShellConfig } from "@/components/product-ui/productWebShellConfig";
import pl from "@/design-system/layouts/productPageLayout.module.css";
import {
  todayWebDashboardChromeBundle,
  todayWebGreeting,
} from "@/components/product-ui/todayWebDashboardChrome";
import type { FlowPracticesChromeLocale } from "@/components/today/flowPracticesMainTabChrome";
import { getLocale } from "@/lib/i18n";
import type { CoreProfile } from "@/lib/types";
import s from "@/components/product-ui/productWebScreens.module.css";

export type TodayWebPractice = {
  id: string;
  title: string;
  durationLabel?: string;
  completed?: boolean;
};

export type TodayWebTimelineEvent = {
  time: string;
  title: string;
  active?: boolean;
};

export type TodayWebDashboardLayout = "full" | "overview" | "composition" | "ritual";

export type TodayWebDashboardProps = {
  displayName: string | null;
  displayDate: string;
  greetingLine?: string;
  profileMeta?: string | null;
  themeTitle: string;
  themeTags?: string[];
  themeBody?: string;
  cardName: string;
  cardMeaning?: string | null;
  moonLine?: string | null;
  numerologyValue: string;
  numerologyMeaning?: string | null;
  practices?: TodayWebPractice[];
  timelineEvents?: TodayWebTimelineEvent[];
  weeklyActivity?: number[] | null;
  streakDays?: number;
  coreProfile?: CoreProfile | null;
  locale?: FlowPracticesChromeLocale;
  layout?: TodayWebDashboardLayout;
  children?: ReactNode;
};

function TodayWebRail({
  chrome,
  timelineEvents,
  weeklyActivity,
  streakDays,
}: {
  chrome: ReturnType<typeof todayWebDashboardChromeBundle>;
  timelineEvents: TodayWebTimelineEvent[];
  weeklyActivity: number[];
  streakDays: number;
}) {
  return (
    <>
      {streakDays > 0 ? (
        <section className={s.todayRailPanel} aria-labelledby="today-rail-streak">
          <h2 id="today-rail-streak" className={v2.eyebrow}>
            {chrome.railStreakTitle}
          </h2>
          <div className={s.todayStreakBlock}>
            <span className={s.todayStreakValue}>{streakDays}</span>
            <span className={s.todayStreakUnit}>{chrome.railStreakDays}</span>
          </div>
        </section>
      ) : null}

      {weeklyActivity.length > 0 ? (
        <section className={s.todayRailPanel} aria-labelledby="today-rail-weekly">
          <h2 id="today-rail-weekly" className={v2.eyebrow}>
            {chrome.railWeeklyTitle}
          </h2>
          <div className={s.todayWeeklyRow}>
            {chrome.weekdayLabels.map((label, index) => {
              const level = weeklyActivity[index] ?? 0;
              return (
                <div key={`${label}-${index}`} className={s.todayWeeklyCell}>
                  <span
                    className={s.todayWeeklyDot}
                    style={{ opacity: 0.35 + level * 0.65, transform: `scale(${0.85 + level * 0.35})` }}
                    aria-hidden
                  />
                  <span className={s.todayWeeklyLabel}>{label}</span>
                </div>
              );
            })}
          </div>
        </section>
      ) : null}

      {timelineEvents.length > 0 ? (
        <section className={s.todayRailPanel} aria-labelledby="today-rail-timeline">
          <h2 id="today-rail-timeline" className={v2.eyebrow}>
            {chrome.railTimelineTitle}
          </h2>
          <ol className={s.todayTimelineList}>
            {timelineEvents.map((event, index) => (
              <li key={`${event.time}-${event.title}`} className={s.todayTimelineItem}>
                <span className={s.todayTimelineTrack} aria-hidden>
                  <span className={`${s.todayTimelineDot} ${event.active ? s.todayTimelineDotActive : ""}`.trim()} />
                  {index < timelineEvents.length - 1 ? <span className={s.todayTimelineLine} /> : null}
                </span>
                <span className={s.todayTimelineContent}>
                  <span className={s.todayTimelineTitle}>{event.title}</span>
                  <span className={s.todayTimelineTime}>{event.time}</span>
                </span>
              </li>
            ))}
          </ol>
        </section>
      ) : null}
    </>
  );
}

function TodayWebOverview({
  chrome,
  themeTitle,
  themeTags,
  themeBody,
  cardName,
  cardMeaning,
  moonLine,
  numerologyValue,
  numerologyMeaning,
  practices,
}: {
  chrome: ReturnType<typeof todayWebDashboardChromeBundle>;
  themeTitle: string;
  themeTags: string[];
  themeBody?: string;
  cardName: string;
  cardMeaning?: string | null;
  moonLine?: string | null;
  numerologyValue: string;
  numerologyMeaning?: string | null;
  practices: TodayWebPractice[];
}) {
  return (
    <>
      <section className={pl.heroCard} aria-labelledby="today-theme-title">
        <div className={pl.heroOrbital} aria-hidden>
          <DsOrbitalViz
            nodes={[
              {
                id: "sun",
                label: "",
                icon: <IconSun />,
                style: { top: "38%", left: "72%" },
              },
            ]}
          />
        </div>
        <div className={pl.heroCopy}>
          <p className={v2.eyebrowOnDark}>{chrome.themeEyebrow}</p>
          <h2 id="today-theme-title" className={v2.displayTitleOnDark}>
            {themeTitle}
          </h2>
          {themeTags.length ? (
            <div className={pl.heroTags}>
              {themeTags.map((tag) => (
                <span key={tag} className={pl.heroTag}>
                  {tag}
                </span>
              ))}
            </div>
          ) : null}
          {themeBody ? <p className={v2.bodyLeadOnDark}>{themeBody}</p> : null}
        </div>
      </section>

      <section className={pl.gridInsights} aria-label={chrome.insightsAria}>
        <article className={pl.dashboardInsightCard}>
          <p className={v2.eyebrow}>{chrome.insightCardLabel}</p>
          <div className={pl.insightVisual}>
            <span className={pl.insightGlyph} aria-hidden>
              ✦
            </span>
          </div>
          <div className={pl.insightCopy}>
            <p className={pl.insightTitle}>{cardName}</p>
            {cardMeaning ? <p className={v2.bodyLead}>{cardMeaning}</p> : null}
          </div>
        </article>

        <article className={pl.dashboardInsightCard}>
          <p className={v2.eyebrow}>{chrome.insightMoonLabel}</p>
          <div className={pl.insightVisual}>
            <span className={pl.moonVisual} aria-hidden />
          </div>
          <div className={pl.insightCopy}>
            <p className={pl.insightTitle}>{moonLine ?? chrome.insightMoonFallback}</p>
          </div>
        </article>

        <article className={pl.dashboardInsightCard}>
          <p className={v2.eyebrow}>{chrome.insightNumerologyLabel}</p>
          <div className={pl.insightVisual}>
            <span className={pl.insightNumber}>{numerologyValue}</span>
          </div>
          <div className={pl.insightCopy}>
            <p className={pl.insightTitle}>{chrome.insightNumerologyTitle}</p>
            {numerologyMeaning ? <p className={v2.bodyLead}>{numerologyMeaning}</p> : null}
          </div>
        </article>
      </section>

      <section className={pl.practicesSection} aria-labelledby="today-practices-title">
        <div className={pl.practicesIntro}>
          <h2 id="today-practices-title" className={v2.sectionTitle}>
            {chrome.practicesTitle}
          </h2>
          <p className={v2.bodyLead}>{chrome.practicesLead}</p>
        </div>
        <div className={pl.practicesGrid}>
          {practices.map((practice) => (
            <article key={practice.id} className={pl.practiceCard}>
              <div className={pl.practiceTop}>
                <span
                  className={`${pl.practiceCheck} ${practice.completed ? pl.practiceCheckDone : ""}`.trim()}
                  aria-hidden
                />
                {practice.durationLabel ? (
                  <span className={pl.practiceDuration}>{practice.durationLabel}</span>
                ) : null}
              </div>
              <p className={pl.practiceName}>{practice.title}</p>
            </article>
          ))}
        </div>
      </section>
    </>
  );
}

export function TodayWebDashboard({
  displayName,
  displayDate,
  greetingLine,
  profileMeta,
  themeTitle,
  themeTags = [],
  themeBody,
  cardName,
  cardMeaning,
  moonLine,
  numerologyValue,
  numerologyMeaning,
  practices,
  timelineEvents,
  weeklyActivity,
  streakDays = 0,
  coreProfile,
  locale,
  layout = "full",
  children,
}: TodayWebDashboardProps) {
  const resolvedLocale: FlowPracticesChromeLocale =
    locale ?? (getLocale() === "ru" ? "ru" : "en");
  const chrome = useMemo(() => todayWebDashboardChromeBundle(resolvedLocale), [resolvedLocale]);

  // PR-2: never invent timeline / weekly / practices for the rail or overview.
  const resolvedTimeline = timelineEvents ?? [];
  const resolvedWeekly = weeklyActivity ?? [];
  const resolvedPractices = practices ?? [];
  const hasContextRail =
    streakDays > 0 || resolvedWeekly.length > 0 || resolvedTimeline.length > 0;

  const showOverview = layout === "full" || layout === "overview";
  const showComposition = layout === "full" || layout === "composition" || layout === "ritual";
  const slotClassName = layout === "ritual" ? pl.ritualSlot : pl.compositionSlot;

  const shellConfig = useMemo((): ProductWebShellConfig => {
    return {
      testId: "today-web-dashboard",
      displayName,
      profileMeta,
      coreProfile,
      mainWide: true,
      rail: hasContextRail ? (
        <TodayWebRail
          chrome={chrome}
          timelineEvents={resolvedTimeline}
          weeklyActivity={resolvedWeekly}
          streakDays={streakDays}
        />
      ) : undefined,
    };
  }, [
    chrome,
    coreProfile,
    displayName,
    hasContextRail,
    profileMeta,
    resolvedTimeline,
    resolvedWeekly,
    streakDays,
  ]);

  return (
    <>
      <ProductWebShellConfigBridge config={shellConfig} />
      <div className={l.productWebContentV2}>
        <div className={v2.pageRoot}>
          <header className={`${pl.pageHeader} ${layout === "composition" ? pl.pageHeaderQuiet : ""}`.trim()}>
            <div>
              {layout === "composition" ? (
                <p className={v2.eyebrow}>Сегодня</p>
              ) : null}
              <h1 className={layout === "composition" ? v2.sectionTitle : v2.displayTitle}>
                {todayWebGreeting(chrome, displayName)}
              </h1>
              {greetingLine ? <p className={v2.bodyLead}>{greetingLine}</p> : null}
            </div>
            <p className={`${v2.chip} ${pl.datePill}`}>
              <IconCalendar />
              {displayDate}
            </p>
          </header>

          {showOverview ? (
            <TodayWebOverview
              chrome={chrome}
              themeTitle={themeTitle}
              themeTags={themeTags}
              themeBody={themeBody}
              cardName={cardName}
              cardMeaning={cardMeaning}
              moonLine={moonLine}
              numerologyValue={numerologyValue}
              numerologyMeaning={numerologyMeaning}
              practices={resolvedPractices}
            />
          ) : null}

          {showComposition && children ? <div className={slotClassName}>{children}</div> : null}
        </div>
      </div>
    </>
  );
}
