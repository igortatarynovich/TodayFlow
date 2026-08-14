"use client";

import { useCallback, useEffect, useId, useState, type ReactNode } from "react";
import { CelestialMoon } from "@/components/celestial/CelestialMoon";
import { TODAY_COMPOSITION_COPY as copy } from "@/components/today/composition/todayCompositionCopy";
import type { TodayDayBriefModel } from "@/lib/todayDayBrief";
import {
  DsActionCard,
  DsButton,
  DsCaption,
  DsCard,
  DsChip,
  DsChipCluster,
  DsContentCard,
  DsEyebrow,
  DsHeroBlock,
  DsHeroFabArrow,
  DsListPanel,
  DsListRow,
  DsMetricCard,
  DsOverlaySheet,
  DsPlanet,
  DsRadialMeter,
  DsStarDivider,
} from "@/design-system";
import layout from "@/design-system/compositions/dsCompositions.module.css";

/**
 * Block 1 — Form Kit pilot (FOUNDATION_UI §15.8).
 * Distinct kit roles: Hero · Metric · List · Content pair · Action.
 * Moon backdrop restored as atmosphere (not a card twin).
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
  body: string;
  kicker?: string;
} | null;

const BETTER_PLANET: Record<string, string> = {
  work: "mars",
  people: "venus",
  self: "sun",
};

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
    />
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
    moonPhase,
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
  const showMoon = typeof moonPhase === "number" && Number.isFinite(moonPhase);
  const energyPct = (() => {
    if (!energy) return 62;
    const m = String(energy).match(/(\d{1,3})\s*%/);
    if (m) return Math.min(100, Number(m[1]));
    return 62;
  })();

  const openHero = () =>
    openSheet({
      title: modeLabel || copy.atmosphereLabel,
      kicker: copy.atmosphereLabel,
      body:
        [heroMeta, line, expect, atmosphereNote, heroCue].filter(Boolean).join("\n\n") ||
        copy.loadingDay,
    });

  return (
    <div
      className={[layout.pilotStack, showMoon ? layout.pilotWithMoon : null].filter(Boolean).join(" ")}
      data-testid="today-day-brief"
      data-pane="atmosphere"
      data-form-kit="pilot"
      data-has-moon={showMoon ? "true" : "false"}
    >
      {showMoon ? (
        <div className={layout.moonBackdrop} aria-hidden data-testid="today-day-brief-moon">
          <CelestialMoon
            phase={moonPhase}
            size={608}
            spin={0.014}
            glow={1.35}
            animated
            textureSrc="/images/celestial/moon_lro_2k.jpg"
            className={layout.moonDisk}
          />
        </div>
      ) : null}

      <div className={layout.pilotForeground}>
        <p data-testid="today-day-brief-date">
          <DsCaption>{dateLabel}</DsCaption>
        </p>

        {/* Kit: Hero (atmosphere) + Data (metric) — different block roles */}
        <div className={layout.pilotGrid}>
          <DsHeroBlock
            testId="today-day-brief-vibe"
            tone="glass"
            eyebrow={heroMeta || copy.atmosphereLabel}
            title={loading ? copy.loadingDay : modeLabel || "Сегодня"}
            body={heroBody || undefined}
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
                onClick={openHero}
              />
            }
            onOpen={openHero}
          />

          <DsMetricCard
            testId="today-day-brief-energy-metric"
            tone="solid"
            value={`${Math.round(energyPct)}%`}
            label={copy.pulseLabel}
            meter={<DsRadialMeter value={energyPct} size={80} />}
          />
        </div>

        {/* Kit: List panel — planet rows, not a grid of twin glass cards */}
        {betterCards.length > 0 ? (
          <DsListPanel title={copy.betterTodayLabel} tone="glass" testId="today-day-brief-better">
            {betterCards.map((card) => (
              <DsListRow
                key={card.id}
                testId={`today-day-better-${card.id}`}
                leading={<DsPlanet planet={BETTER_PLANET[card.id] || "mercury"} size={36} />}
                title={card.title}
                subtitle={card.body}
                onClick={() =>
                  openSheet({
                    title: card.title,
                    kicker: copy.betterTodayLabel,
                    body: card.detail || card.body,
                  })
                }
              />
            ))}
          </DsListPanel>
        ) : null}

        {/* Kit: Content pair — support (subtle) vs trap (accent), not identical twins */}
        {(supportLine || trap) && (
          <section data-testid="today-day-brief-pair" className={layout.pairGrid}>
            {supportLine ? (
              <DsContentCard
                tone="subtle"
                as="button"
                testId="today-day-brief-do"
                eyebrow={copy.supportLabel}
                body={supportLine}
                chips={<DsChip variant="ghost">опора</DsChip>}
                onClick={() =>
                  openSheet({
                    title: copy.supportLabel,
                    body: supportDetail || supportLine,
                  })
                }
              />
            ) : null}
            {trap ? (
              <DsContentCard
                tone="accent"
                as="button"
                testId="today-day-brief-trap"
                eyebrow={copy.trapDayLabel}
                body={trap}
                chips={<DsChip variant="status">внимание</DsChip>}
                onClick={() =>
                  openSheet({
                    title: copy.trapDayLabel,
                    body: trap,
                  })
                }
              />
            ) : null}
          </section>
        )}

        {/* Kit: Action / CTA block */}
        {personalLine || onContinue ? (
          <>
            <DsStarDivider />
            <DsActionCard
              testId="today-day-brief-personal"
              tone="accent"
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
      </div>

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
        <DsContentCard tone="glass" testId="today-day-brief-expect" eyebrow={copy.expectLabel} body={expect} />
      ) : null}

      {trap ? (
        <DsContentCard tone="accent" testId="today-day-brief-trap" eyebrow={copy.trapLabel} body={trap} />
      ) : null}

      {hasCues ? (
        <section className={layout.stack} data-testid="today-day-brief-instruction">
          {doItems.length > 0 ? (
            <DsListPanel tone="subtle" testId="today-day-brief-do" title={copy.supportLabel}>
              {doItems.map((item) => (
                <DsListRow key={item} title={item} />
              ))}
            </DsListPanel>
          ) : null}
          {avoidItems.length > 0 ? (
            <DsListPanel tone="glass" testId="today-day-brief-avoid" title={copy.trapDayLabel}>
              {avoidItems.map((item) => (
                <DsListRow key={item} title={item} />
              ))}
            </DsListPanel>
          ) : null}
        </section>
      ) : null}

      {energy ? (
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
