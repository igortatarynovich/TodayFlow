"use client";

import { useCallback, useEffect, useId, useState, type ReactNode } from "react";
import { TODAY_COMPOSITION_COPY as copy } from "@/components/today/composition/todayCompositionCopy";
import type { TodayDayBriefModel, TodayDayTransitRow } from "@/lib/todayDayBrief";
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
  DsPlanet,
  DsRadialMeter,
  DsSectionHeader,
  DsSpectrum,
  DsWaveMeter,
  DsWindowCard,
} from "@/design-system";
import layout from "@/design-system/compositions/dsCompositions.module.css";
import { joinClass } from "@/design-system/utils/joinClass";

/**
 * TODAY dashboard — ENERGY% + mood → Global day clock → timed transits → STRENGTHS → RISKS.
 * Layout: docs/today/TODAY_PRODUCT_FLOW_V1.md · form kit only.
 * Global clock ≠ Personal Timeline (MY DAY).
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

function moodStatusTone(mode: string | null | undefined): "good" | "warn" | "risk" | "neutral" {
  if (mode === "tension") return "risk";
  if (mode === "momentum") return "warn";
  if (mode === "renewal" || mode === "flow" || mode === "grounded" || mode === "clarity") return "good";
  return "neutral";
}

function transitRowTestId(row: TodayDayTransitRow): string {
  if (row.id === "moon") return "today-day-brief-moon-row";
  return `today-day-brief-transit-${row.id}`;
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
    visualMode,
    moonPhase,
    moonCard,
    transits,
    dayWindow,
    energyPct,
    strengthChips,
    riskChips,
    energyCause,
  } = model;
  const transitRows = transits || [];

  const line = atmosphereLine ?? vibe;
  const showMoon = typeof moonPhase === "number" && Number.isFinite(moonPhase);
  const heroTitle = loading ? copy.loadingDay : modeLabel || "Сегодня";
  const heroBody = line || expect || undefined;
  const showPulse = energyPct !== null || Boolean(modeLabel);
  const firstDriverId = transitRows.find((item) => item.id !== "moon")?.id;

  const openHero = () =>
    openSheet({
      title: modeLabel || copy.pulseLabel,
      kicker: copy.pulseLabel,
      body: [line, expect, atmosphereNote, energyCause].filter(Boolean).join("\n\n") || copy.loadingDay,
    });

  const openTransit = (row: TodayDayTransitRow) => {
    openSheet({
      title: row.title,
      kicker: row.time || (row.id === "moon" ? copy.moonLabel : copy.transitsLabel),
      body: row.id === "moon" ? moonCard?.context || undefined : undefined,
      rows: row.sheetRows.length ? row.sheetRows : undefined,
    });
  };

  return (
    <div
      className={layout.dayBriefMoonStage}
      data-testid="today-day-brief"
      data-pane="atmosphere"
      data-form-kit="composition"
      data-has-moon={showMoon ? "true" : "false"}
    >
      {showMoon ? (
        <div className={layout.dayBriefMoonBackdrop} aria-hidden data-moon-crop="top-40">
          <DsCelestialMoon
            phase={moonPhase}
            size={440}
            spin={0}
            glow={0.55}
            animated={false}
            textureSrc="/images/celestial/moon_lro_2k.jpg"
            testId="today-day-brief-moon"
          />
        </div>
      ) : null}

      <div className={joinClass(layout.pilotStack, layout.dayBriefMoonForeground)}>
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

      {showPulse ? (
        <div className={layout.pairGrid} data-testid="today-day-brief-pulse">
          {energyPct !== null ? (
            <DsMetricCard
              tone="solid"
              testId="today-day-brief-energy"
              value={`${energyPct}%`}
              label={copy.pulseLabel}
              meter={
                <div className={layout.stackTight}>
                  <DsRadialMeter value={energyPct} size={72} />
                  <DsWaveMeter value={energyPct} />
                </div>
              }
            />
          ) : null}
          {modeLabel ? (
            <DsMetricCard
              tone="solid"
              testId="today-day-brief-mood"
              value={modeLabel}
              label={copy.moodLabel}
              meter={
                <DsChip variant="status" statusTone={moodStatusTone(visualMode)}>
                  {modeLabel}
                </DsChip>
              }
            />
          ) : null}
        </div>
      ) : null}

      {dayWindow ? (
        <DsWindowCard
          tone="solid"
          testId="today-day-brief-window"
          title={copy.bestWindowLabel}
          startLabel={dayWindow.start}
          endLabel={dayWindow.end}
          spectrum={
            <DsSpectrum
              value={dayWindow.mark}
              lowLabel={copy.spectrumDawn}
              highLabel={copy.spectrumNight}
              testId="today-day-brief-spectrum"
            />
          }
        />
      ) : null}

      {transitRows.length > 0 ? (
        <DsListPanel tone="glass" title={copy.transitsLabel} testId="today-day-brief-transits">
          {transitRows.map((row) => (
            <DsListRow
              key={row.id}
              testId={
                row.id === "moon"
                  ? "today-day-brief-moon-row"
                  : row.id === firstDriverId
                    ? "today-day-brief-driver-row"
                    : transitRowTestId(row)
              }
              leading={
                row.planets.length ? (
                  <span className={layout.planetPair}>
                    {row.planets.map((planet) => (
                      <DsPlanet key={planet} planet={planet} size={44} />
                    ))}
                  </span>
                ) : undefined
              }
              title={row.title}
              subtitle={row.time || (row.id === "moon" ? moonCard?.meta || undefined : undefined)}
              onClick={() => openTransit(row)}
            />
          ))}
        </DsListPanel>
      ) : null}

      {strengthChips.length > 0 ? (
        <div data-testid="today-day-brief-strengths">
          <DsEyebrow>{copy.strengthsLabel}</DsEyebrow>
          <DsChipCluster>
            {strengthChips.map((chip) => (
              <DsChip
                key={chip.id}
                variant="status"
                statusTone="good"
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
                variant="status"
                statusTone="risk"
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
