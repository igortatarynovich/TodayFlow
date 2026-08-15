"use client";

import { useCallback, useEffect, useId, useState, type ReactNode } from "react";
import { TODAY_COMPOSITION_COPY as copy } from "@/components/today/composition/todayCompositionCopy";
import type { TodayDayBriefModel } from "@/lib/todayDayBrief";
import {
  DsActionCard,
  DsCallout,
  DsCaption,
  DsCard,
  DsCelestialMoon,
  DsChip,
  DsChipCluster,
  DsContentCard,
  DsEyebrow,
  DsFab,
  DsHeroBlock,
  DsHeroFabArrow,
  DsListPanel,
  DsListRow,
  DsMetricCard,
  DsOverlaySheet,
  DsRadialMeter,
  DsSectionHeader,
  DsWaveMeter,
} from "@/design-system";
import layout from "@/design-system/compositions/dsCompositions.module.css";

/**
 * TODAY dashboard — ENERGY → MOON → MAIN DRIVER → STRENGTHS → RISKS.
 * Layout: docs/today/TODAY_PRODUCT_FLOW_V1.md · kit only.
 */

export type TodayDayBriefPane = "atmosphere" | "orientation";

export type TodayDayBriefProps = {
  model: TodayDayBriefModel;
  pane?: TodayDayBriefPane;
  loading?: boolean;
  timeline?: ReactNode;
  onContinue?: () => void;
};

type SheetState = {
  title: string;
  body?: string;
  kicker?: string;
  rows?: Array<{ label: string; value: string }>;
} | null;

function parseEnergyPct(energy: string | null | undefined): number | null {
  if (!energy) return null;
  const m = String(energy).match(/(\d{1,3})\s*%/);
  if (!m) return null;
  return Math.min(100, Math.max(0, Number(m[1])));
}

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
    <DsOverlaySheet
      testId="today-day-detail-sheet"
      titleId={titleId}
      title={sheet.title}
      body={sheet.body}
      kicker={sheet.kicker}
      closeLabel={copy.sheetClose}
      onClose={onClose}
    >
      {sheet.rows && sheet.rows.length > 0 ? (
        <DsListPanel tone="subtle" testId="today-day-sheet-rows">
          {sheet.rows.map((row) => (
            <DsListRow key={`${row.label}:${row.value}`} title={row.label} subtitle={row.value} />
          ))}
        </DsListPanel>
      ) : null}
    </DsOverlaySheet>
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
    atmosphereLine,
    vibe,
    atmosphereNote,
    expect,
    modeLabel,
    moonPhase,
    moonCard,
    mainDriver,
    strengthChips,
    riskChips,
  } = model;

  const line = atmosphereLine ?? vibe;
  const showMoon = typeof moonPhase === "number" && Number.isFinite(moonPhase);
  const heroTitle = loading ? copy.loadingDay : modeLabel || "Сегодня";
  const heroBody = line || expect || undefined;

  const openHero = () =>
    openSheet({
      title: modeLabel || copy.pulseLabel,
      kicker: copy.pulseLabel,
      body: [line, expect, atmosphereNote].filter(Boolean).join("\n\n") || copy.loadingDay,
    });

  const openMoon = () => {
    if (!moonCard) return;
    openSheet({
      title: moonCard.title,
      kicker: copy.moonLabel,
      body: moonCard.context || undefined,
      rows: moonCard.sheetRows,
    });
  };

  const openDriver = () => {
    if (!mainDriver) return;
    openSheet({
      title: mainDriver.title,
      kicker: copy.mainDriverLabel,
      body: undefined,
      rows: mainDriver.sheetRows.length ? mainDriver.sheetRows : undefined,
    });
  };

  return (
    <div
      className={layout.pilotStack}
      data-testid="today-day-brief"
      data-pane="atmosphere"
      data-form-kit="composition"
      data-has-moon={showMoon ? "true" : "false"}
    >
      <DsSectionHeader eyebrow={copy.storyNext.day} title={dateLabel} testId="today-day-brief-date" />

      <DsHeroBlock
        testId="today-day-brief-vibe"
        tone="none"
        size="feature"
        className={layout.heroOpen}
        eyebrow={copy.pulseLabel}
        title={heroTitle}
        body={heroBody}
        fab={
          <DsHeroFabArrow
            ariaLabel={copy.pulseLabel}
            testId="today-day-brief-hero-fab"
            onClick={openHero}
          />
        }
        onOpen={openHero}
      />

      {moonCard ? (
        <DsListPanel tone="glass" testId="today-day-brief-moon-card">
          <DsListRow
            testId="today-day-brief-moon-row"
            leading={
              showMoon ? (
                <DsCelestialMoon
                  phase={moonPhase}
                  size={56}
                  spin={0}
                  glow={0.6}
                  animated={false}
                  textureSrc="/images/celestial/moon_lro_2k.jpg"
                  testId="today-day-brief-moon"
                />
              ) : undefined
            }
            title={moonCard.title}
            subtitle={moonCard.meta || undefined}
            onClick={openMoon}
          />
        </DsListPanel>
      ) : null}

      {mainDriver ? (
        <DsContentCard
          tone="glass"
          testId="today-day-brief-driver"
          eyebrow={copy.mainDriverLabel}
          title={mainDriver.title}
          body={mainDriver.body || undefined}
          onClick={openDriver}
        />
      ) : null}

      {strengthChips.length > 0 ? (
        <div data-testid="today-day-brief-strengths">
          <DsEyebrow>{copy.strengthsLabel}</DsEyebrow>
          <DsChipCluster>
            {strengthChips.map((chip) => (
              <DsChip
                key={chip.id}
                testId={`today-day-strength-${chip.id}`}
                onClick={() =>
                  openSheet({
                    title: chip.label,
                    kicker: copy.strengthsLabel,
                    body: chip.sheetRows.length ? undefined : chip.label,
                    rows: chip.sheetRows.length ? chip.sheetRows : undefined,
                  })
                }
              >
                {chip.label}
              </DsChip>
            ))}
          </DsChipCluster>
        </div>
      ) : null}

      {riskChips.length > 0 ? (
        <div data-testid="today-day-brief-risks">
          <DsEyebrow>{copy.risksLabel}</DsEyebrow>
          <DsChipCluster>
            {riskChips.map((chip) => (
              <DsChip
                key={chip.id}
                testId={`today-day-risk-${chip.id}`}
                onClick={() =>
                  openSheet({
                    title: chip.label,
                    kicker: copy.risksLabel,
                    body: chip.sheetRows.length ? undefined : chip.label,
                    rows: chip.sheetRows.length ? chip.sheetRows : undefined,
                  })
                }
              >
                {chip.label}
              </DsChip>
            ))}
          </DsChipCluster>
        </div>
      ) : null}

      {onContinue ? (
        <section className={layout.dayBriefClose} data-testid="today-day-brief-close">
          <DsActionCard
            testId="today-day-brief-personal"
            tone="accent"
            layout="bar"
            title={copy.todayContinueCta.replace(/\s*→\s*$/, "")}
            action={
              <DsFab
                ariaLabel={copy.todayContinueCta}
                size="lg"
                onClick={onContinue}
                testId="today-day-personal-cta"
              >
                →
              </DsFab>
            }
          />
        </section>
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
  const energyPct = parseEnergyPct(energy);
  const empty = !trap && !hasCues && !energy && !expect && !timeline && !loading;

  return (
    <div className={layout.pilotStack} data-testid="today-day-brief" data-pane="orientation">
      {expect ? (
        <DsContentCard tone="glass" testId="today-day-brief-expect" eyebrow={copy.expectLabel} body={expect} />
      ) : null}

      {trap ? (
        <DsCallout tone="avoid" label="attention" title={copy.trapLabel} testId="today-day-brief-trap">
          {trap}
        </DsCallout>
      ) : null}

      {hasCues ? (
        <section className={layout.dayBriefMid} data-testid="today-day-brief-instruction">
          {doItems.length > 0 ? (
            <DsListPanel tone="subtle" testId="today-day-brief-do" title={copy.supportLabel}>
              {doItems.map((item) => (
                <DsListRow key={item} title={item} />
              ))}
            </DsListPanel>
          ) : null}
          {avoidItems.length > 0 ? (
            <DsListPanel tone="solid" testId="today-day-brief-avoid" title={copy.trapDayLabel}>
              {avoidItems.map((item) => (
                <DsListRow key={item} title={item} />
              ))}
            </DsListPanel>
          ) : null}
        </section>
      ) : null}

      {energyPct !== null ? (
        <DsMetricCard
          tone="solid"
          testId="today-day-brief-energy"
          value={`${Math.round(energyPct)}%`}
          label={energyCause || copy.pulseLabel}
          meter={
            <div className={layout.stackTight}>
              <DsRadialMeter value={energyPct} size={72} />
              <DsWaveMeter value={energyPct} />
            </div>
          }
        />
      ) : energy ? (
        <DsMetricCard
          tone="solid"
          testId="today-day-brief-energy"
          value={energy}
          label={energyCause || copy.pulseLabel}
        />
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
