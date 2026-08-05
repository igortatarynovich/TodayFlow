/**
 * Today story-deck frames (mockup-aligned ScreenFlow cuts).
 * Content SoT unchanged — presentation regroup only (FOUNDATION_UI §16 / SCENARIO).
 */
"use client";

import { useEffect, useState, type CSSProperties, type ReactNode } from "react";
import { DsButton } from "@/design-system/primitives/DsButton";
import { DsCard } from "@/design-system/primitives/DsCard";
import { TodayDayColorGuideSection } from "@/components/today/composition/TodayDayColorGuideSection";
import { TODAY_COMPOSITION_COPY as copy } from "@/components/today/composition/todayCompositionCopy";
import { TodayGlanceTimelineSlot } from "@/components/today/composition/TodayWave2Slots";
import { TodayTapWidget } from "@/components/today/composition/TodayWave2Slots";
import type { TodayDayColorGuide } from "@/lib/todayDayColorGuide";
import type { GlanceDailyFocusModel } from "@/lib/todayDailyFocus";
import type { TodayContractV1 } from "@/lib/todayContract";
import type { TapResponseCode } from "@/lib/todayTapWidget";
import { TODAY_NO_SHARP_FOCUS_COPY } from "@/lib/todayGlanceTexture";
import {
  resolveTodayStoryFrameArt,
  type TodayStoryArtRole,
} from "@/lib/todayStoryFrameArt";
import styles from "@/components/today/composition/TodayStoryDeckFrames.module.css";

function TodayStoryArtBackdrop({
  role,
  tone = "photo",
}: {
  role: TodayStoryArtRole;
  /** photo = immersive full-bleed; theme pages omit this. */
  tone?: "photo" | "energy";
}) {
  const [src, setSrc] = useState(() => resolveTodayStoryFrameArt(role));
  useEffect(() => {
    setSrc(resolveTodayStoryFrameArt(role));
    const root = document.documentElement;
    const sync = () => setSrc(resolveTodayStoryFrameArt(role));
    const obs = new MutationObserver(sync);
    obs.observe(root, { attributes: true, attributeFilter: ["data-day-mode", "data-day-phase"] });
    return () => obs.disconnect();
  }, [role]);

  return (
    <div
      className={tone === "energy" ? styles.artEnergy : styles.artPhoto}
      style={{ "--story-art": `url("${src}")` } as CSSProperties}
      aria-hidden
      data-testid={`today-frame-art-${role}`}
    />
  );
}

/** Mockup cue between stacked blocks inside one story frame. */
export function TodayStoryDownCue() {
  return (
    <div className={styles.downCue} data-testid="today-story-down-cue" aria-hidden>
      <span className={styles.downCueArrow}>↓</span>
    </div>
  );
}

export function TodayGreetingFrame({
  salutation,
  dateLabel,
  headline,
  loading = false,
  onStart,
}: {
  salutation: string;
  dateLabel: string;
  headline: string | null;
  loading?: boolean;
  onStart: () => void;
}) {
  return (
    <div className={`${styles.greeting} ${styles.immersive}`} data-testid="today-frame-greeting">
      <TodayStoryArtBackdrop role="greeting" />
      <div className={styles.immersiveContent}>
        <p className={styles.salutation}>{salutation}</p>
        <h2 className={styles.greetingHeadline}>
          {loading ? copy.loadingDay : headline || "Сегодня — твой день"}
        </h2>
        <p className={styles.dateLine}>{dateLabel}</p>
        <button type="button" className={styles.startCta} data-testid="today-greeting-start" onClick={onStart}>
          <span className={styles.startArrow} aria-hidden>
            →
          </span>
          <span>Начать день</span>
        </button>
      </div>
    </div>
  );
}

export function TodayEnergyFlowFrame({
  energyLine,
  energyCause,
  dateISO,
}: {
  energyLine: string | null;
  energyCause: string | null;
  dateISO: string;
}) {
  const energy = (energyLine || "").trim() || null;
  const cause = (energyCause || "").trim() || null;
  return (
    <div
      className={`${styles.frame} ${styles.frameScroll} ${styles.immersive}`}
      data-testid="today-frame-energy-flow"
    >
      <TodayStoryArtBackdrop role="energy" tone="energy" />
      <div className={styles.immersiveContent}>
        <div className={styles.centerStack}>
          <p className={styles.eyebrowOnArt}>{copy.pulseLabel}</p>
          {energy ? (
            <h2 className={styles.energyPrimaryOnArt} data-testid="today-glance-energy-text">
              {energy}
            </h2>
          ) : (
            <p className={styles.mutedOnArt} data-testid="today-energy-empty">
              Энергия дня сегодня без отдельной формулировки.
            </p>
          )}
          {cause ? (
            <p className={styles.detailOnArt} data-testid="today-glance-energy-cause">
              {cause}
            </p>
          ) : null}
        </div>

        <TodayStoryDownCue />

        <div className={styles.flowBlock} data-testid="today-frame-day-flow">
          <p className={styles.eyebrowOnArt}>Поток дня</p>
          <div className={styles.flowOnArt}>
            <TodayGlanceTimelineSlot dateISO={dateISO} />
          </div>
        </div>
      </div>
    </div>
  );
}

export function TodayAttributesFrame({
  themeLabel,
  themeText,
  dailyFocus,
  colorGuide,
  moveDo,
  moveAvoid,
}: {
  themeLabel: string;
  themeText: string | null;
  dailyFocus: GlanceDailyFocusModel | null;
  colorGuide: TodayDayColorGuide | null;
  moveDo: string | null;
  moveAvoid: string | null;
}) {
  const focusTitle = (dailyFocus?.title || "").trim() || null;
  const prioritize = (dailyFocus?.prioritize || "").trim() || moveDo;
  const avoid = (dailyFocus?.avoid || "").trim() || moveAvoid;

  return (
    <div className={`${styles.frame} ${styles.frameScroll}`} data-testid="today-frame-attributes">
      {colorGuide ? (
        <>
          <div className={styles.colorAnchor}>
            <TodayDayColorGuideSection guide={colorGuide} />
          </div>
          <TodayStoryDownCue />
        </>
      ) : null}

      <div className={styles.centerStack}>
        <p className={styles.eyebrow}>{themeLabel}</p>
        {themeText ? (
          <h2 className={styles.themePrimary} data-testid="today-attributes-theme">
            {themeText}
          </h2>
        ) : null}
      </div>

      {(focusTitle || prioritize || avoid) && <TodayStoryDownCue />}

      <div className={styles.listBlock} data-testid="today-glance-daily-focus">
        <p className={styles.eyebrow}>{copy.journey.glanceFocusLabel}</p>
        {focusTitle ? (
          <p className={styles.focusTitle} data-testid="today-glance-focus-title">
            {focusTitle}
          </p>
        ) : null}
        {prioritize || avoid ? (
          <ul className={styles.cardList}>
            {prioritize ? (
              <li className={styles.cardItem} data-testid="today-glance-focus-prioritize">
                <span className={styles.cardItemLabel}>{copy.journey.glanceFocusPrioritize.replace(" · ", "")}</span>
                <span>{prioritize}</span>
              </li>
            ) : null}
            {avoid ? (
              <li className={styles.cardItem} data-testid="today-glance-focus-avoid">
                <span className={styles.cardItemLabel}>{copy.journey.glanceFocusAvoid.replace(" · ", "")}</span>
                <span>{avoid}</span>
              </li>
            ) : null}
          </ul>
        ) : (
          <p className={styles.muted} data-testid="today-glance-focus-empty">
            {TODAY_NO_SHARP_FOCUS_COPY}
          </p>
        )}
      </div>
    </div>
  );
}

export function TodayPracticeFrame({
  title,
  meta,
  actionLabel,
  completed,
  completing,
  onAction,
  linkSlot,
}: {
  title: string | null;
  meta: string | null;
  actionLabel: string;
  completed: boolean;
  completing?: boolean;
  onAction: () => void;
  linkSlot?: ReactNode;
}) {
  return (
    <div className={`${styles.practice} ${styles.immersive}`} data-testid="today-frame-practice">
      <TodayStoryArtBackdrop role="practice" />
      <div className={styles.immersiveContent}>
        <p className={styles.eyebrowOnArt}>Практика дня</p>
        {title ? (
          <h2 className={styles.practiceTitleOnArt} data-testid="today-practice-title">
            {title}
          </h2>
        ) : (
          <p className={styles.mutedOnArt}>Сегодня без отдельной практики — держи ритм дня.</p>
        )}
        {meta ? <p className={styles.detailOnArt}>{meta}</p> : null}
        {title && !completed ? (
          <DsButton
            type="button"
            variant="primary"
            className={styles.practiceCta}
            data-testid="today-tool-practice"
            disabled={completing}
            onClick={onAction}
          >
            {actionLabel}
          </DsButton>
        ) : null}
        {completed ? <p className={styles.detailOnArt}>{copy.practiceCompleted}</p> : null}
        {linkSlot ? <div className={styles.linkOnArt}>{linkSlot}</div> : null}
      </div>
    </div>
  );
}

export function TodayInsightFrame({
  plot,
  dialogue,
}: {
  plot?: ReactNode;
  dialogue?: ReactNode;
}) {
  const hasPlot = Boolean(plot);
  const hasDialogue = Boolean(dialogue);
  return (
    <div className={`${styles.insight} ${styles.frameScroll}`} data-testid="today-frame-insight">
      <span className={styles.quoteMark} aria-hidden>
        “
      </span>
      <p className={styles.eyebrow}>Инсайт дня</p>
      <div className={styles.insightBody}>
        {hasPlot ? plot : null}
        {hasPlot && hasDialogue ? <TodayStoryDownCue /> : null}
        {hasDialogue ? dialogue : null}
      </div>
    </div>
  );
}

export function TodayCloseFrame({
  eveningQuestion,
  contract,
  dateISO,
  tapResponse,
  onTapRecorded,
  onOpenEvening,
}: {
  eveningQuestion: string | null;
  contract: TodayContractV1;
  dateISO: string;
  tapResponse?: TapResponseCode | null;
  onTapRecorded?: (response: TapResponseCode) => void;
  onOpenEvening: () => void;
}) {
  return (
    <div className={`${styles.frame} ${styles.frameScroll}`} data-testid="today-frame-close">
      <div className={styles.centerStack}>
        <p className={styles.eyebrow}>Вопрос на вечер</p>
        <h2 className={styles.eveningQuestion} data-testid="today-evening-question">
          {eveningQuestion?.trim() || "Что сегодня было по-настоящему важным?"}
        </h2>
      </div>
      <TodayStoryDownCue />
      <div className={styles.responseWrap} data-testid="today-slot-tap-wrap">
        <TodayTapWidget
          contract={contract}
          dateISO={dateISO}
          initialResponse={tapResponse}
          onRecorded={onTapRecorded}
        />
      </div>
      <TodayStoryDownCue />
      <DsCard
        variant="glass"
        size="compact"
        as="button"
        className={styles.eveningCta}
        testId="today-evening-open"
        onClick={onOpenEvening}
      >
        <span className={styles.teaserLabel}>{copy.eveningCta}</span>
        <span className={styles.teaserHook}>{copy.eveningHint}</span>
      </DsCard>
    </div>
  );
}
