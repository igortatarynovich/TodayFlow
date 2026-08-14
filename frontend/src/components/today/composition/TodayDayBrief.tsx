"use client";

import { useCallback, useEffect, useId, useState, type ReactNode } from "react";
import { TODAY_COMPOSITION_COPY as copy } from "@/components/today/composition/todayCompositionCopy";
import type { TodayDayBriefModel } from "@/lib/todayDayBrief";
import {
  DsActionCard,
  DsButton,
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
  DsIconBadge,
  DsListPanel,
  DsListRow,
  DsMetricCard,
  DsOverlaySheet,
  DsQuote,
  DsRadialMeter,
  DsSectionHeader,
  DsStarDivider,
  DsWaveMeter,
} from "@/design-system";
import { TODAY_DOMAIN_ICON_MAP } from "@/design-system/icons/DsIcons";
import layout from "@/design-system/compositions/dsCompositions.module.css";

/**
 * Block 1 — Form Kit production (FOUNDATION_UI §15.8).
 * Wire only roles with real model data. UI imports: design-system/** only
 * (plus domain data/types). Planets = celestial contexts only, not life spheres.
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

/** betterCards ids → DomainKey for §16.6 linear icons (not planet photos). */
const BETTER_DOMAIN: Record<string, keyof typeof TODAY_DOMAIN_ICON_MAP> = {
  work: "work",
  people: "relationships",
  self: "energy",
};

function BetterDomainLeading({ id }: { id: string }) {
  const key = BETTER_DOMAIN[id] ?? "energy";
  const Icon = TODAY_DOMAIN_ICON_MAP[key];
  return (
    <DsIconBadge size="md">
      <Icon className={layout.domainIcon} />
    </DsIconBadge>
  );
}

/** Parse energy string → 0–100, or null when no real numeric signal. */
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
    activityTags,
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
  const energyPct = parseEnergyPct(energy);
  const showMetric = energyPct !== null;
  const statusChipLabel = modeLabel || heroCue;

  const openHero = () =>
    openSheet({
      title: modeLabel || copy.atmosphereLabel,
      kicker: copy.atmosphereLabel,
      body:
        [heroMeta, line, expect, atmosphereNote, heroCue].filter(Boolean).join("\n\n") ||
        copy.loadingDay,
    });

  /* Single moon — Hero bleed only. A second backdrop disk reads as a duplicate. */
  const moonBleed = showMoon ? (
    <DsCelestialMoon
      phase={moonPhase}
      size={300}
      spin={0.014}
      glow={1.05}
      animated
      textureSrc="/images/celestial/moon_lro_2k.jpg"
      className={layout.moonDisk}
    />
  ) : null;

  return (
    <div
      className={layout.pilotStack}
      data-testid="today-day-brief"
      data-pane="atmosphere"
      data-form-kit="pilot"
      data-has-moon={showMoon ? "true" : "false"}
    >
      <div className={layout.pilotForeground}>
        <p data-testid="today-day-brief-date">
          <DsCaption>{dateLabel}</DsCaption>
        </p>

        <div className={layout.pilotGrid}>
          <DsHeroBlock
            testId="today-day-brief-vibe"
            tone="glass"
            className={showMoon ? layout.heroWithMoon : undefined}
            eyebrow={heroMeta || copy.atmosphereLabel}
            title={loading ? copy.loadingDay : modeLabel || "Сегодня"}
            body={heroBody || undefined}
            bleed={
              showMoon ? (
                <div data-testid="today-day-brief-moon" aria-hidden>
                  {moonBleed}
                </div>
              ) : null
            }
            bleedClassName={showMoon ? layout.heroMoonBleed : undefined}
            chips={
              moodPills.length || activityTags.length || statusChipLabel ? (
                <DsChipCluster>
                  {statusChipLabel ? (
                    <DsChip
                      variant="status"
                      statusTone="neutral"
                      testId={statusChipLabel === heroCue ? "today-day-brief-mood" : "today-day-brief-status"}
                    >
                      {statusChipLabel}
                    </DsChip>
                  ) : null}
                  {(moodPills.length ? moodPills : []).slice(0, 3).map((pill) =>
                    pill === statusChipLabel ? null : (
                      <DsChip key={pill} testId={pill === heroCue ? "today-day-brief-mood" : undefined}>
                        {pill}
                      </DsChip>
                    ),
                  )}
                  {activityTags.slice(0, 2).map((tag) => (
                    <DsChip key={tag} variant="time">
                      {tag}
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

          {showMetric ? (
            <DsMetricCard
              testId="today-day-brief-energy-metric"
              tone="solid"
              value={`${Math.round(energyPct)}%`}
              label={copy.pulseLabel}
              meter={
                <div className={layout.stackTight}>
                  <DsRadialMeter value={energyPct} size={80} />
                  <DsWaveMeter value={energyPct} testId="today-day-brief-energy-wave" />
                </div>
              }
            />
          ) : null}
        </div>

        {betterCards.length > 0 ? (
          <>
            <DsSectionHeader title={copy.betterTodayLabel} withDivider={false} />
            <DsListPanel tone="solid" testId="today-day-brief-better">
              {betterCards.map((card) => (
                <DsListRow
                  key={card.id}
                  testId={`today-day-better-${card.id}`}
                  leading={<BetterDomainLeading id={card.id} />}
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
          </>
        ) : null}

        {(supportLine || trap) && (
          <section data-testid="today-day-brief-pair" className={layout.pairGrid}>
            {supportLine ? (
              <button
                type="button"
                className={layout.pairHit}
                data-testid="today-day-brief-do"
                onClick={() =>
                  openSheet({
                    title: copy.supportLabel,
                    body: supportDetail || supportLine,
                  })
                }
              >
                <DsCallout tone="help" label="help" title={copy.supportLabel}>
                  {supportLine}
                </DsCallout>
              </button>
            ) : null}
            {trap ? (
              <button
                type="button"
                className={layout.pairHit}
                data-testid="today-day-brief-trap"
                onClick={() =>
                  openSheet({
                    title: copy.trapDayLabel,
                    body: trap,
                  })
                }
              >
                <DsCallout tone="avoid" label="attention" title={copy.trapDayLabel}>
                  {trap}
                </DsCallout>
              </button>
            ) : null}
          </section>
        )}

        {personalLine ? (
          <>
            <DsStarDivider />
            <DsQuote highlight kicker={copy.personalTodayLabel} testId="today-day-brief-quote">
              {personalLine}
            </DsQuote>
          </>
        ) : null}

        {onContinue ? (
          <DsActionCard
            testId="today-day-brief-personal"
            tone="accent"
            title={copy.personalTodayLabel}
            action={
              <>
                <DsButton size="lg" data-testid="today-day-personal-cta" onClick={onContinue}>
                  {copy.personalTodayCta}
                </DsButton>
                <DsFab ariaLabel={copy.personalTodayCta} size="md" onClick={onContinue}>
                  →
                </DsFab>
              </>
            }
          />
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
  const { trap, doItems, avoidItems, energy, energyCause, expect, personalLine } = model;
  const hasCues = doItems.length > 0 || avoidItems.length > 0;
  const energyPct = parseEnergyPct(energy);
  const empty = !trap && !hasCues && !energy && !expect && !timeline && !loading;

  return (
    <div className={layout.pilotStack} data-testid="today-day-brief" data-pane="orientation">
      {expect ? (
        <DsContentCard tone="glass" testId="today-day-brief-expect" eyebrow={copy.expectLabel} body={expect} />
      ) : null}

      {personalLine ? (
        <DsQuote highlight kicker={copy.personalTodayLabel}>
          {personalLine}
        </DsQuote>
      ) : null}

      {trap ? (
        <DsCallout tone="avoid" label="attention" title={copy.trapLabel} testId="today-day-brief-trap">
          {trap}
        </DsCallout>
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
