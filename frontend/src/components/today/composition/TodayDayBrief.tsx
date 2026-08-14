"use client";

import { useCallback, useEffect, useId, useState, type ReactNode } from "react";
import { TODAY_COMPOSITION_COPY as copy } from "@/components/today/composition/todayCompositionCopy";
import type { TodayDayBriefModel } from "@/lib/todayDayBrief";
import {
  DsActionCard,
  DsBody,
  DsButton,
  DsCaption,
  DsCard,
  DsChip,
  DsChipCluster,
  DsEyebrow,
  DsHeroBlock,
  DsHeroFabArrow,
  DsMetricCard,
  DsPlanet,
  DsRadialMeter,
  DsStarDivider,
} from "@/design-system";
import layout from "@/design-system/compositions/dsCompositions.module.css";

/**
 * Block 1 — Form Kit pilot (FOUNDATION_UI §15.8).
 * Atmosphere pane: hero + metric + celestial visual + chips — zero local visual CSS.
 * Canon: TODAY_SCREEN_SCENARIO_V3 v3.4.2
 */

export type TodayDayBriefPane = "atmosphere" | "orientation";

export type TodayDayBriefProps = {
  model: TodayDayBriefModel;
  pane?: TodayDayBriefPane;
  loading?: boolean;
  timeline?: ReactNode;
  /** Advance ScreenFlow after personal CTA (optional). */
  onContinue?: () => void;
};

type SheetState = {
  title: string;
  body: string;
  kicker?: string;
} | null;

export function TodayDayBrief({
  model,
  pane = "atmosphere",
  loading = false,
  timeline = null,
  onContinue,
}: TodayDayBriefProps) {
  if (pane === "orientation") {
    return <TodayDayOrientation model={model} loading={loading} timeline={timeline} />;
  }
  return <TodayDayDashboard model={model} loading={loading} onContinue={onContinue} />;
}

function TodayDayDetailSheet({
  sheet,
  onClose,
}: {
  sheet: SheetState;
  onClose: () => void;
}) {
  const titleId = useId();
  useEffect(() => {
    if (!sheet) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    const prev = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      window.removeEventListener("keydown", onKey);
      document.body.style.overflow = prev;
    };
  }, [sheet, onClose]);

  if (!sheet) return null;

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby={titleId}
      data-testid="today-day-detail-sheet"
      style={{
        position: "fixed",
        inset: 0,
        zIndex: 40,
        display: "flex",
        alignItems: "flex-end",
        justifyContent: "center",
        padding: "var(--tf-ds-space-4, 1rem)",
      }}
    >
      <button
        type="button"
        aria-label={copy.sheetClose}
        onClick={onClose}
        style={{
          position: "absolute",
          inset: 0,
          border: "none",
          background: "transparent",
          cursor: "pointer",
        }}
      />
      <DsCard tone="glass" size="default" className={layout.stack} testId="today-day-detail-panel">
        {sheet.kicker ? <DsEyebrow>{sheet.kicker}</DsEyebrow> : null}
        <h3 id={titleId}>
          <DsBody>{sheet.title}</DsBody>
        </h3>
        <DsBody size="sm">{sheet.body}</DsBody>
        <DsButton variant="secondary" onClick={onClose}>
          {copy.sheetClose}
        </DsButton>
      </DsCard>
    </div>
  );
}

function TodayDayDashboard({
  model,
  loading,
  onContinue,
}: {
  model: TodayDayBriefModel;
  loading: boolean;
  onContinue?: () => void;
}) {
  const [sheet, setSheet] = useState<SheetState>(null);
  const openSheet = useCallback((next: SheetState) => setSheet(next), []);
  const closeSheet = useCallback(() => setSheet(null), []);

  const {
    dateLabel,
    salutation,
    atmosphereLine,
    vibe,
    moodPills,
    atmosphereNote,
    expect,
    modeLabel,
    lunarCaption,
    betterCards,
    supportLine,
    supportDetail,
    trap,
    personalLine,
    energy,
  } = model;

  const line = atmosphereLine ?? vibe;
  const heroBody = line || expect || atmosphereNote;
  const heroCue = moodPills[0] || null;
  const heroMeta = lunarCaption || salutation;
  const energyPct = (() => {
    if (!energy) return 62;
    const m = String(energy).match(/(\d{1,3})\s*%/);
    if (m) return Math.min(100, Number(m[1]));
    return 62;
  })();

  return (
    <div
      className={layout.pilotStack}
      data-testid="today-day-brief"
      data-pane="atmosphere"
      data-form-kit="pilot"
    >
      <p data-testid="today-day-brief-date">
        <DsCaption>{dateLabel}</DsCaption>
      </p>

      <div className={layout.pilotGrid}>
        <DsHeroBlock
          testId="today-day-brief-vibe"
          eyebrow={heroMeta || copy.atmosphereLabel}
          title={loading ? copy.loadingDay : modeLabel || "Сегодня"}
          body={heroBody || undefined}
          bleed={<DsPlanet planet="moon" size={132} />}
          chips={
            heroCue || moodPills.length ? (
              <DsChipCluster>
                {(moodPills.length ? moodPills.slice(0, 3) : heroCue ? [heroCue] : []).map((pill) => (
                  <DsChip key={pill} testId={pill === heroCue ? "today-day-brief-mood" : undefined}>
                    {pill}
                  </DsChip>
                ))}
              </DsChipCluster>
            ) : undefined
          }
          fab={
            <DsHeroFabArrow
              ariaLabel={copy.atmosphereLabel}
              testId="today-day-brief-hero-fab"
              onClick={() =>
                openSheet({
                  title: modeLabel || copy.atmosphereLabel,
                  kicker: copy.atmosphereLabel,
                  body:
                    [heroMeta, line, expect, atmosphereNote, heroCue].filter(Boolean).join("\n\n") ||
                    copy.loadingDay,
                })
              }
            />
          }
          onOpen={() =>
            openSheet({
              title: modeLabel || copy.atmosphereLabel,
              kicker: copy.atmosphereLabel,
              body:
                [heroMeta, line, expect, atmosphereNote, heroCue].filter(Boolean).join("\n\n") ||
                copy.loadingDay,
            })
          }
        />

        <DsMetricCard
          testId="today-day-brief-energy-metric"
          value={`${Math.round(energyPct)}%`}
          label={copy.pulseLabel}
          meter={<DsRadialMeter value={energyPct} size={72} />}
        />
      </div>

      {betterCards.length > 0 ? (
        <section data-testid="today-day-brief-better" className={layout.stack}>
          <DsEyebrow>{copy.betterTodayLabel}</DsEyebrow>
          <div className={layout.betterGrid} data-count={Math.min(3, betterCards.length)}>
            {betterCards.map((card) => (
              <DsCard
                key={card.id}
                tone="glass"
                size="compact"
                as="button"
                onClick={() =>
                  openSheet({
                    title: card.title,
                    kicker: copy.betterTodayLabel,
                    body: card.detail || card.body,
                  })
                }
                testId={`today-day-better-${card.id}`}
              >
                <DsBody size="sm">{card.title}</DsBody>
                <DsCaption>{card.body}</DsCaption>
              </DsCard>
            ))}
          </div>
        </section>
      ) : null}

      {(supportLine || trap) && (
        <section data-testid="today-day-brief-pair" className={layout.pairGrid}>
          {supportLine ? (
            <DsCard
              tone="subtle"
              size="compact"
              as="button"
              testId="today-day-brief-do"
              onClick={() =>
                openSheet({
                  title: copy.supportLabel,
                  body: supportDetail || supportLine,
                })
              }
            >
              <DsEyebrow>{copy.supportLabel}</DsEyebrow>
              <DsBody size="sm">{supportLine}</DsBody>
            </DsCard>
          ) : null}
          {trap ? (
            <DsCard
              tone="subtle"
              size="compact"
              as="button"
              testId="today-day-brief-trap"
              onClick={() =>
                openSheet({
                  title: copy.trapDayLabel,
                  body: trap,
                })
              }
            >
              <DsEyebrow>{copy.trapDayLabel}</DsEyebrow>
              <DsBody size="sm">{trap}</DsBody>
            </DsCard>
          ) : null}
        </section>
      )}

      {personalLine || onContinue ? (
        <>
          <DsStarDivider />
          <DsActionCard
            testId="today-day-brief-personal"
            title={copy.personalTodayLabel}
            body={personalLine || undefined}
            action={
              onContinue ? (
                <DsButton data-testid="today-day-personal-cta" onClick={onContinue}>
                  {copy.personalTodayCta}
                </DsButton>
              ) : (
                <DsChip variant="ghost">·</DsChip>
              )
            }
          />
        </>
      ) : null}

      <TodayDayDetailSheet sheet={sheet} onClose={closeSheet} />
    </div>
  );
}

function TodayDayOrientation({
  model,
  loading,
  timeline,
}: {
  model: TodayDayBriefModel;
  loading: boolean;
  timeline: ReactNode;
}) {
  const { trap, doItems, avoidItems, energy, energyCause, expect } = model;
  const hasCues = doItems.length > 0 || avoidItems.length > 0;
  const empty = !trap && !hasCues && !energy && !expect && !timeline && !loading;

  return (
    <div className={layout.pilotStack} data-testid="today-day-brief" data-pane="orientation">
      {expect ? (
        <DsCard tone="glass" size="compact" testId="today-day-brief-expect">
          <DsEyebrow>{copy.expectLabel}</DsEyebrow>
          <DsBody size="sm">{expect}</DsBody>
        </DsCard>
      ) : null}

      {trap ? (
        <DsCard tone="subtle" size="compact" testId="today-day-brief-trap">
          <DsEyebrow>{copy.trapLabel}</DsEyebrow>
          <DsBody size="sm">{trap}</DsBody>
        </DsCard>
      ) : null}

      {hasCues ? (
        <section className={layout.stack} data-testid="today-day-brief-instruction">
          {doItems.length > 0 ? (
            <DsCard tone="glass" size="compact" testId="today-day-brief-do">
              <ul>
                {doItems.map((item) => (
                  <li key={item}>
                    <DsBody size="sm">{item}</DsBody>
                  </li>
                ))}
              </ul>
            </DsCard>
          ) : null}
          {avoidItems.length > 0 ? (
            <DsCard tone="subtle" size="compact" testId="today-day-brief-avoid">
              <ul>
                {avoidItems.map((item) => (
                  <li key={item}>
                    <DsBody size="sm">{item}</DsBody>
                  </li>
                ))}
              </ul>
            </DsCard>
          ) : null}
        </section>
      ) : null}

      {energy ? (
        <DsCard tone="glass" size="compact" testId="today-day-brief-energy">
          <DsEyebrow>{copy.pulseLabel}</DsEyebrow>
          <DsBody size="sm">{energy}</DsBody>
          {energyCause ? (
            <DsCaption>
              <span data-testid="today-day-brief-energy-cause">{energyCause}</span>
            </DsCaption>
          ) : null}
        </DsCard>
      ) : null}

      {timeline ? (
        <DsCard tone="none" size="compact" testId="today-day-brief-timeline">
          <DsEyebrow>{copy.timelineLabel}</DsEyebrow>
          {timeline}
        </DsCard>
      ) : null}

      {empty ? (
        <p data-testid="today-day-brief-orientation-empty">
          <DsCaption>{copy.orientationEmpty}</DsCaption>
        </p>
      ) : null}
    </div>
  );
}
