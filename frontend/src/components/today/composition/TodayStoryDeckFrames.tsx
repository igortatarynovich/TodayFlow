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
import { TodayTapWidget } from "@/components/today/composition/TodayWave2Slots";
import type { TodayDayColorGuide } from "@/lib/todayDayColorGuide";
import type { GlanceDailyFocusModel } from "@/lib/todayDailyFocus";
import type { TodayContractV1 } from "@/lib/todayContract";
import type { TapResponseCode } from "@/lib/todayTapWidget";
import { TODAY_NO_SHARP_FOCUS_COPY } from "@/lib/todayGlanceTexture";
import { buildStoryDayFlow } from "@/lib/todayStoryDayFlow";
import {
  resolveTodayStoryFrameArt,
  type TodayStoryArtRole,
} from "@/lib/todayStoryFrameArt";
import { findStoryBlockInStep, scrollStoryBlockIntoStep } from "@/lib/todayStoryScroll";
import styles from "@/components/today/composition/TodayStoryDeckFrames.module.css";

type StoryArtTone = "photo" | "energy" | "practice";

/** Resolve art URL and bind it as this block's own background (not Day Atmosphere theme). */
function useStoryFrameArt(role: TodayStoryArtRole): CSSProperties {
  const [src, setSrc] = useState(() => resolveTodayStoryFrameArt(role));
  useEffect(() => {
    setSrc(resolveTodayStoryFrameArt(role));
    const root = document.documentElement;
    const sync = () => setSrc(resolveTodayStoryFrameArt(role));
    const obs = new MutationObserver(sync);
    obs.observe(root, { attributes: true, attributeFilter: ["data-day-mode", "data-day-phase"] });
    return () => obs.disconnect();
  }, [role]);
  return { "--story-art": `url("${src}")` } as CSSProperties;
}

function immersiveClass(tone: StoryArtTone, ...extra: Array<string | false | null | undefined>) {
  return [styles.immersive, tone === "energy" ? styles.immersiveEnergy : null, tone === "practice" ? styles.immersivePractice : null, ...extra]
    .filter(Boolean)
    .join(" ");
}

/** Full-bleed photo plane for the ScreenFlow step — stays pinned while content scrolls. */
function ImmersiveArtPlane({ role, testId }: { role: TodayStoryArtRole; testId: string }) {
  const artStyle = useStoryFrameArt(role);
  return (
    <div
      className={styles.immersiveArt}
      style={artStyle}
      data-testid={testId}
      data-frame-art={role}
      aria-hidden
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
      onClick={(e) => {
        const target = findStoryBlockInStep(e.currentTarget, targetId);
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
    <div
      className={immersiveClass("photo", styles.greeting)}
      data-testid="today-frame-greeting"
      data-frame-art="greeting"
    >
      <ImmersiveArtPlane role="greeting" testId="today-frame-art-greeting" />
      <div className={styles.immersiveContent}>
        <section className={`${styles.storyPane} ${styles.storyPaneLift}`} data-story-block="greeting-hero">
          <div className={styles.storyPaneBody}>
            <p className={styles.salutation}>{salutation}</p>
            <h2 className={styles.greetingHeadline}>
              {loading ? copy.loadingDay : headline || "Сегодня — твой день"}
            </h2>
            <p className={styles.dateLine}>{dateLabel}</p>
          </div>
          <button type="button" className={styles.startCta} data-testid="today-greeting-start" onClick={onStart}>
            <span className={styles.startArrow} aria-hidden>
              →
            </span>
            <span className={styles.startCtaText}>
              <span className={styles.startCtaLabel}>Начать день</span>
              <span className={styles.startHint}>{copy.storyNext.energy}</span>
            </span>
          </button>
        </section>
      </div>
    </div>
  );
}

export function TodayEnergyFlowFrame({
  energyLine,
  energyCause,
  prioritize,
  avoid,
  moveDo,
  moveAvoid,
  onGoNext,
  nextTitle = copy.storyNext.symbols,
  nextHint = copy.storyNext.symbolsHint,
}: {
  energyLine: string | null;
  energyCause: string | null;
  prioritize?: string | null;
  avoid?: string | null;
  moveDo?: string | null;
  moveAvoid?: string | null;
  onGoNext: () => void;
  nextTitle?: string;
  nextHint?: string;
}) {
  const energy = (energyLine || "").trim() || null;
  const cause = (energyCause || "").trim() || null;
  const dayFlow = buildStoryDayFlow({
    energyLine: energy,
    prioritize,
    avoid,
    moveDo,
    moveAvoid,
  });
  return (
    <div
      className={immersiveClass("energy", styles.frame)}
      data-testid="today-frame-energy-flow"
      data-frame-art="energy"
    >
      <ImmersiveArtPlane role="energy" testId="today-frame-art-energy" />
      <div className={`${styles.immersiveContent} ${styles.storyScroll}`} data-story-scroll="pane">
        <section className={`${styles.storyPane} ${styles.storyPaneLift}`} data-story-block="energy-hero">
          <div className={styles.storyPaneBody}>
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
          </div>
          <StoryBlockCue targetId="energy-flow" label={copy.storyNext.scrollMore} />
        </section>

        <section
          className={`${styles.storyPane} ${styles.storyPaneStack}`}
          data-story-block="energy-flow"
          data-testid="today-frame-day-flow"
        >
          <div className={styles.storyPaneBody}>
            <div className={styles.flowBlock}>
              <header className={styles.flowHeader}>
                <p className={styles.eyebrowOnArt}>Поток дня</p>
                <p className={styles.flowLeadOnArt}>
                  Как пройти день: старт, задачи, диалоги, итог и отдых.
                </p>
              </header>
              <ol className={styles.dayFlow} data-testid="today-story-day-flow">
                {dayFlow.map((point, index) => (
                  <li
                    key={point.id}
                    className={styles.dayFlowItem}
                    data-valence={point.valence}
                    data-testid={`today-day-flow-${point.id}`}
                  >
                    <div className={styles.dayFlowRail} aria-hidden>
                      <span className={styles.dayFlowDot} />
                      {index < dayFlow.length - 1 ? <span className={styles.dayFlowLine} /> : null}
                    </div>
                    <div className={styles.dayFlowCopy}>
                      <p className={styles.dayFlowPhase}>{point.phase}</p>
                      <p className={styles.dayFlowCue} data-valence={point.valence}>
                        {point.cue}
                      </p>
                      <p className={styles.dayFlowBody}>{point.body}</p>
                    </div>
                  </li>
                ))}
              </ol>
            </div>
          </div>
          <StoryNextAnchor title={nextTitle} hint={nextHint} onNext={onGoNext} />
        </section>
      </div>
    </div>
  );
}

export function TodayAttributesFrame({
  themeLabel,
  themeText,
  plotSlot,
  dailyFocus,
  colorGuide,
  moveDo,
  moveAvoid,
  onGoNext,
}: {
  themeLabel: string;
  themeText: string | null;
  /** Full «Главный сюжет» (beats) — lives with theme, not a short substitute line. */
  plotSlot?: ReactNode;
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
  const hasPlot = Boolean(plotSlot);
  const hasThemePlot = hasTheme || hasPlot;
  const hasFocus = Boolean(focusTitle || prioritize);
  const hasAvoid = Boolean(avoid);
  const hasFocusAvoid = hasFocus || hasAvoid;

  return (
    <div className={`${styles.frame} ${styles.storyScroll}`} data-story-scroll="pane" data-testid="today-frame-attributes">
      {colorGuide ? (
        <section
          className={`${styles.storyPane} ${styles.storyPaneCenter}`}
          data-story-block="attr-color"
        >
          <div className={styles.storyPaneBody}>
            <div className={styles.colorHero}>
              <TodayDayColorGuideSection guide={colorGuide} />
            </div>
          </div>
          {hasThemePlot || hasFocusAvoid ? (
            <StoryBlockCue
              targetId={hasThemePlot ? "attr-theme-plot" : "attr-focus-avoid"}
              label={copy.storyNext.scrollMore}
            />
          ) : (
            <StoryNextAnchor
              title={copy.storyNext.practice}
              hint={copy.storyNext.practiceHint}
              onNext={onGoNext}
            />
          )}
        </section>
      ) : null}

      {hasThemePlot ? (
        <section
          className={`${styles.storyPane} ${styles.storyPaneStack}`}
          data-story-block="attr-theme-plot"
          data-testid="today-attributes-theme-plot"
        >
          <div className={styles.storyPaneBody}>
            <div className={styles.compassBlock}>
              {hasTheme ? (
                <div className={styles.compassSection} data-testid="today-attributes-theme">
                  <p className={styles.eyebrow}>{themeLabel}</p>
                  <h2 className={styles.themePrimary}>{themeText}</h2>
                </div>
              ) : null}
              {hasPlot ? (
                <div className={styles.compassSection} data-testid="today-attributes-plot">
                  {plotSlot}
                </div>
              ) : null}
            </div>
          </div>
          {hasFocusAvoid ? (
            <StoryBlockCue targetId="attr-focus-avoid" label={copy.storyNext.scrollMore} />
          ) : (
            <StoryNextAnchor
              title={copy.storyNext.practice}
              hint={copy.storyNext.practiceHint}
              onNext={onGoNext}
            />
          )}
        </section>
      ) : null}

      {hasFocusAvoid ? (
        <section
          className={`${styles.storyPane} ${styles.storyPaneCenter}`}
          data-story-block="attr-focus-avoid"
          data-testid="today-attributes-focus-avoid"
        >
          <div className={styles.storyPaneBody}>
            <div className={styles.compassBlock}>
              {hasFocus ? (
                <div className={styles.compassSection} data-testid="today-glance-daily-focus">
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
              {hasAvoid ? (
                <div className={styles.compassSection} data-testid="today-attributes-avoid">
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
            </div>
          </div>
          <StoryNextAnchor
            title={copy.storyNext.practice}
            hint={copy.storyNext.practiceHint}
            onNext={onGoNext}
          />
        </section>
      ) : null}

      {!colorGuide && !hasThemePlot && !hasFocusAvoid ? (
        <section className={`${styles.storyPane} ${styles.storyPaneCenter}`}>
          <StoryNextAnchor
            title={copy.storyNext.practice}
            hint={copy.storyNext.practiceHint}
            onNext={onGoNext}
          />
        </section>
      ) : null}
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
    <div
      className={immersiveClass("practice", styles.practice)}
      data-testid="today-frame-practice"
      data-frame-art="practice"
    >
      <ImmersiveArtPlane role="practice" testId="today-frame-art-practice" />
      <div className={styles.immersiveContent}>
        <section className={styles.storyPane} data-story-block="practice-hero">
          <div className={styles.storyPaneBody}>
            <p className={styles.eyebrowOnArt}>Практика дня</p>
            {title ? (
              <h2 className={styles.practiceTitleOnArt} data-testid="today-practice-title">
                {title}
              </h2>
            ) : (
              <p className={styles.mutedOnArt}>Сегодня без отдельной практики — держи ритм дня.</p>
            )}
            {meta ? <p className={styles.detailOnArt}>{meta}</p> : null}
            {completed ? <p className={styles.detailOnArt}>{copy.practiceCompleted}</p> : null}
            {linkSlot ? <div className={styles.linkOnArt}>{linkSlot}</div> : null}
          </div>
          <div className={styles.storyPaneFooter}>
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
            <StoryNextAnchor
              title={copy.storyNext.insight}
              hint={copy.storyNext.insightHint}
              onNext={onGoNext}
            />
          </div>
        </section>
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
    <div
      className={`${styles.insight} ${styles.storyScroll}`}
      data-story-scroll="pane"
      data-testid="today-frame-insight"
    >
      <section className={styles.storyPane} data-story-block="insight-hero">
        <div className={styles.storyPaneBody}>
          <div className={styles.insightHero}>
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
        </div>
        {hasStory ? (
          <StoryBlockCue targetId="insight-story" label={copy.storyNext.scrollMore} />
        ) : hasDialogue ? (
          <StoryBlockCue targetId="insight-dialogue" label={copy.storyNext.scrollMore} />
        ) : (
          <StoryNextAnchor
            title={copy.storyNext.close}
            hint={copy.storyNext.closeHint}
            onNext={onGoNext}
          />
        )}
      </section>

      {hasStory ? (
        <section className={styles.storyPane} data-story-block="insight-story">
          <div className={styles.storyPaneBody}>
            <div className={styles.insightBody}>{story}</div>
          </div>
          {hasDialogue ? (
            <StoryBlockCue targetId="insight-dialogue" label={copy.storyNext.scrollMore} />
          ) : (
            <StoryNextAnchor
              title={copy.storyNext.close}
              hint={copy.storyNext.closeHint}
              onNext={onGoNext}
            />
          )}
        </section>
      ) : null}

      {hasDialogue ? (
        <section className={styles.storyPane} data-story-block="insight-dialogue">
          <div className={styles.storyPaneBody}>
            <div className={styles.insightBody}>{dialogue}</div>
          </div>
          <StoryNextAnchor
            title={copy.storyNext.close}
            hint={copy.storyNext.closeHint}
            onNext={onGoNext}
          />
        </section>
      ) : null}
    </div>
  );
}

export function TodayCloseFrame({
  contract,
  dateISO,
  tapResponse,
  onTapRecorded,
  onOpenEvening,
}: {
  contract: TodayContractV1;
  dateISO: string;
  tapResponse?: TapResponseCode | null;
  onTapRecorded?: (response: TapResponseCode) => void;
  onOpenEvening: () => void;
}) {
  return (
    <div
      className={`${styles.frame} ${styles.storyScroll}`}
      data-story-scroll="pane"
      data-testid="today-frame-close"
    >
      <section
        className={styles.storyPane}
        data-story-block="close-response"
        data-testid="today-slot-tap-wrap"
      >
        <div className={styles.storyPaneBody}>
          <div className={styles.responseWrap}>
            <TodayTapWidget
              contract={contract}
              dateISO={dateISO}
              initialResponse={tapResponse}
              onRecorded={onTapRecorded}
            />
          </div>
        </div>
        <StoryBlockCue targetId="close-cta" label={copy.storyNext.scrollMore} />
      </section>

      <section className={styles.storyPane} data-story-block="close-cta">
        <div className={styles.storyPaneBody} />
        <div className={styles.storyPaneFooter}>
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
      </section>
    </div>
  );
}
