/**
 * Today story-deck frames — presentation polish (FOUNDATION_UI §16 / SCENARIO).
 * StoryBlockCue = within-step scroll · StoryNextAnchor = next ScreenFlow step.
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
import { scrollStoryBlockIntoStep } from "@/lib/todayStoryScroll";
import styles from "@/components/today/composition/TodayStoryDeckFrames.module.css";

function TodayStoryArtBackdrop({
  role,
  tone = "photo",
}: {
  role: TodayStoryArtRole;
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

/** Within-screen cue — scrolls to `targetId` inside the active step. Never advances ScreenFlow. */
export function StoryBlockCue({
  targetId,
  label,
}: {
  targetId: string;
  label?: string;
}) {
  return (
    <button
      type="button"
      className={styles.blockCue}
      data-testid="today-story-block-cue"
      aria-label={label ? `Дальше: ${label}` : "К следующему блоку"}
      onClick={() => {
        const target = document.querySelector<HTMLElement>(`[data-story-block="${targetId}"]`);
        if (target) scrollStoryBlockIntoStep(target);
      }}
    >
      <span className={styles.blockCueArrow} aria-hidden>
        ↓
      </span>
      {label ? <span className={styles.blockCueLabel}>{label}</span> : null}
    </button>
  );
}

/** Cross-screen foreshadow — advances ScreenFlow only. */
export function StoryNextAnchor({
  title,
  hint,
  onNext,
}: {
  title: string;
  hint?: string;
  onNext: () => void;
}) {
  return (
    <button
      type="button"
      className={styles.nextAnchor}
      data-testid="today-story-next-anchor"
      onClick={onNext}
    >
      <span className={styles.nextAnchorArrow} aria-hidden>
        ↓
      </span>
      <span className={styles.nextAnchorEyebrow}>{copy.storyNext.further}</span>
      <span className={styles.nextAnchorTitle}>{title}</span>
      {hint ? <span className={styles.nextAnchorHint}>{hint}</span> : null}
    </button>
  );
}

/** @deprecated use StoryBlockCue */
export function TodayStoryDownCue({ targetId, label }: { targetId?: string; label?: string } = {}) {
  if (targetId) return <StoryBlockCue targetId={targetId} label={label} />;
  return (
    <div className={styles.blockCue} data-testid="today-story-down-cue" aria-hidden>
      <span className={styles.blockCueArrow}>↓</span>
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
          <span className={styles.startHint}>{copy.storyNext.energy}</span>
        </button>
      </div>
    </div>
  );
}

export function TodayEnergyFlowFrame({
  energyLine,
  energyCause,
  dateISO,
  onGoNext,
  nextTitle = copy.storyNext.symbols,
  nextHint = copy.storyNext.symbolsHint,
}: {
  energyLine: string | null;
  energyCause: string | null;
  dateISO: string;
  onGoNext: () => void;
  nextTitle?: string;
  nextHint?: string;
}) {
  const energy = (energyLine || "").trim() || null;
  const cause = (energyCause || "").trim() || null;
  return (
    <div className={`${styles.frame} ${styles.frameGrow} ${styles.immersive}`} data-testid="today-frame-energy-flow">
      <TodayStoryArtBackdrop role="energy" tone="energy" />
      <div className={styles.immersiveContent}>
        <div className={styles.centerStack} data-story-block="energy-hero">
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

        <StoryBlockCue targetId="energy-flow" label={copy.storyNext.flowCue} />

        <div className={styles.flowBlock} data-story-block="energy-flow" data-testid="today-frame-day-flow">
          <p className={styles.eyebrowOnArt}>Поток дня</p>
          <div className={styles.flowOnArt}>
            <TodayGlanceTimelineSlot dateISO={dateISO} />
          </div>
        </div>

        <StoryNextAnchor title={nextTitle} hint={nextHint} onNext={onGoNext} />
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
  onGoNext,
}: {
  themeLabel: string;
  themeText: string | null;
  dailyFocus: GlanceDailyFocusModel | null;
  colorGuide: TodayDayColorGuide | null;
  moveDo: string | null;
  moveAvoid: string | null;
  onGoNext: () => void;
}) {
  const focusTitle = (dailyFocus?.title || "").trim() || null;
  const prioritize = (dailyFocus?.prioritize || "").trim() || moveDo;
  const avoid = (dailyFocus?.avoid || "").trim() || moveAvoid;
  const hasTheme = Boolean(themeText);
  const hasFocus = Boolean(focusTitle || prioritize);
  const hasAvoid = Boolean(avoid);

  return (
    <div className={`${styles.frame} ${styles.frameGrow}`} data-testid="today-frame-attributes">
      {colorGuide ? (
        <div className={styles.colorHero} data-story-block="attr-color">
          <TodayDayColorGuideSection guide={colorGuide} />
        </div>
      ) : null}

      {colorGuide && (hasTheme || hasFocus || hasAvoid) ? (
        <StoryBlockCue targetId={hasTheme ? "attr-theme" : hasFocus ? "attr-focus" : "attr-avoid"} />
      ) : null}

      {hasTheme ? (
        <div className={styles.centerStack} data-story-block="attr-theme">
          <p className={styles.eyebrow}>{themeLabel}</p>
          <h2 className={styles.themePrimary} data-testid="today-attributes-theme">
            {themeText}
          </h2>
        </div>
      ) : null}

      {hasTheme && (hasFocus || hasAvoid) ? (
        <StoryBlockCue targetId={hasFocus ? "attr-focus" : "attr-avoid"} />
      ) : null}

      {hasFocus ? (
        <div className={styles.listBlock} data-story-block="attr-focus" data-testid="today-glance-daily-focus">
          <p className={styles.eyebrow}>{copy.journey.glanceFocusLabel}</p>
          {focusTitle ? (
            <p className={styles.focusTitle} data-testid="today-glance-focus-title">
              {focusTitle}
            </p>
          ) : null}
          {prioritize ? (
            <ul className={styles.cardList}>
              <li className={styles.cardItem} data-testid="today-glance-focus-prioritize">
                <span className={styles.cardItemLabel}>
                  {copy.journey.glanceFocusPrioritize.replace(" · ", "")}
                </span>
                <span>{prioritize}</span>
              </li>
            </ul>
          ) : !focusTitle ? (
            <p className={styles.muted} data-testid="today-glance-focus-empty">
              {TODAY_NO_SHARP_FOCUS_COPY}
            </p>
          ) : null}
        </div>
      ) : null}

      {hasFocus && hasAvoid ? <StoryBlockCue targetId="attr-avoid" label={copy.storyNext.avoidLabel} /> : null}

      {hasAvoid ? (
        <div className={styles.listBlock} data-story-block="attr-avoid" data-testid="today-attributes-avoid">
          <p className={styles.eyebrow}>{copy.storyNext.avoidLabel}</p>
          <ul className={styles.cardList}>
            <li className={styles.cardItem} data-testid="today-glance-focus-avoid">
              <span className={styles.cardItemLabel}>
                {copy.journey.glanceFocusAvoid.replace(" · ", "")}
              </span>
              <span>{avoid}</span>
            </li>
          </ul>
        </div>
      ) : null}

      <StoryNextAnchor
        title={copy.storyNext.practice}
        hint={copy.storyNext.practiceHint}
        onNext={onGoNext}
      />
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
  onGoNext,
}: {
  title: string | null;
  meta: string | null;
  actionLabel: string;
  completed: boolean;
  completing?: boolean;
  onAction: () => void;
  linkSlot?: ReactNode;
  onGoNext: () => void;
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
        <StoryNextAnchor
          title={copy.storyNext.insight}
          hint={copy.storyNext.insightHint}
          onNext={onGoNext}
        />
      </div>
    </div>
  );
}

export function TodayInsightFrame({
  heroText,
  story,
  dialogue,
  onGoNext,
}: {
  /** Primary insight / вывод — hero. */
  heroText?: string | null;
  /** Short explanation / plot beats. */
  story?: ReactNode;
  dialogue?: ReactNode;
  onGoNext: () => void;
}) {
  const hero = (heroText || "").trim() || null;
  const hasStory = Boolean(story);
  const hasDialogue = Boolean(dialogue);

  return (
    <div className={`${styles.insight} ${styles.frameGrow}`} data-testid="today-frame-insight">
      <div className={styles.insightHero} data-story-block="insight-hero">
        <span className={styles.quoteMark} aria-hidden>
          “
        </span>
        <p className={styles.eyebrow}>Инсайт дня</p>
        {hero ? (
          <h2 className={styles.insightPrimary} data-testid="today-insight-hero">
            {hero}
          </h2>
        ) : null}
      </div>

      {hasStory ? (
        <>
          <StoryBlockCue targetId="insight-story" />
          <div className={styles.insightBody} data-story-block="insight-story">
            {story}
          </div>
        </>
      ) : null}

      {hasDialogue ? (
        <>
          <StoryBlockCue targetId="insight-dialogue" />
          <div className={styles.insightBody} data-story-block="insight-dialogue">
            {dialogue}
          </div>
        </>
      ) : null}

      <StoryNextAnchor
        title={copy.storyNext.close}
        hint={copy.storyNext.closeHint}
        onNext={onGoNext}
      />
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
    <div className={`${styles.frame} ${styles.frameGrow}`} data-testid="today-frame-close">
      <div className={styles.centerStack} data-story-block="close-question">
        <p className={styles.eyebrow}>Вопрос на вечер</p>
        <h2 className={styles.eveningQuestion} data-testid="today-evening-question">
          {eveningQuestion?.trim() || "Что сегодня было по-настоящему важным?"}
        </h2>
      </div>

      <StoryBlockCue targetId="close-response" />

      <div className={styles.responseWrap} data-story-block="close-response" data-testid="today-slot-tap-wrap">
        <TodayTapWidget
          contract={contract}
          dateISO={dateISO}
          initialResponse={tapResponse}
          onRecorded={onTapRecorded}
        />
      </div>

      <StoryBlockCue targetId="close-cta" label={copy.eveningCta} />

      <div data-story-block="close-cta">
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
    </div>
  );
}
