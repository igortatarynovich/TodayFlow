/**
 * Today story-deck frames — presentation polish (FOUNDATION_UI §16 / SCENARIO).
 * StoryBlockCue = within-step scroll · StoryNextAnchor = next ScreenFlow step.
 */
"use client";

import { useEffect, useLayoutEffect, useRef, useState, type CSSProperties, type ReactNode } from "react";
import { DsButton } from "@/design-system/primitives/DsButton";
import { DsCard } from "@/design-system/primitives/DsCard";
import {
  DsBody,
  DsDisplayTitle,
  DsEyebrow,
} from "@/design-system/primitives/DsTypography";
import { DsChipGroup, DsGlassCard } from "@/design-system/patterns/DsRitual";
import { TodayDayColorGuideSection } from "@/components/today/composition/TodayDayColorGuideSection";
import { TODAY_COMPOSITION_COPY as copy } from "@/components/today/composition/todayCompositionCopy";
import { TodayTapWidget } from "@/components/today/composition/TodayWave2Slots";
import type { TodayDayColorGuide } from "@/lib/todayDayColorGuide";
import type { GlanceDailyFocusModel } from "@/lib/todayDailyFocus";
import type { TodayContractV1 } from "@/lib/todayContract";
import type { TapResponseCode } from "@/lib/todayTapWidget";
import { TODAY_NO_SHARP_FOCUS_COPY } from "@/lib/todayGlanceTexture";
import { fetchDayFacts, clearDayFactsCache } from "@/lib/todayDayFacts";
import type { GlanceTimelineItem } from "@/lib/todayGlanceTimeline";
import {
  buildStoryDayFlow,
  valenceChromeLabel,
  type StoryDayFlowPoint,
} from "@/lib/todayStoryDayFlow";
import {
  resolveTodayStoryFrameArt,
  type TodayStoryArtRole,
} from "@/lib/todayStoryFrameArt";
import { findStoryBlockInStep, scrollStoryBlockIntoStep } from "@/lib/todayStoryScroll";
import {
  todaySlotFailureCopy,
  todaySlotFailureFromError,
  type TodaySlotLoadFailure,
} from "@/lib/todaySlotAvailability";
import styles from "@/components/today/composition/TodayStoryDeckFrames.module.css";

type StoryArtTone = "photo" | "energy" | "practice";

/**
 * Resolve art URL and bind it as this block's own background (not Day Atmosphere theme).
 * When `enabled` is false (inactive ScreenFlow step), skip the bitmap so only the active
 * step holds a photo — FOUNDATION_UI single-paint / phone heat.
 */
function useStoryFrameArt(role: TodayStoryArtRole, enabled = true): CSSProperties {
  const [src, setSrc] = useState(() => resolveTodayStoryFrameArt(role));
  useEffect(() => {
    if (!enabled) return;
    setSrc(resolveTodayStoryFrameArt(role));
    const root = document.documentElement;
    const sync = () => setSrc(resolveTodayStoryFrameArt(role));
    const obs = new MutationObserver(sync);
    obs.observe(root, { attributes: true, attributeFilter: ["data-day-mode", "data-day-phase"] });
    return () => obs.disconnect();
  }, [role, enabled]);
  if (!enabled) return {};
  return { "--story-art": `url("${src}")` } as CSSProperties;
}

function immersiveClass(tone: StoryArtTone, ...extra: Array<string | false | null | undefined>) {
  return [styles.immersive, tone === "energy" ? styles.immersiveEnergy : null, tone === "practice" ? styles.immersivePractice : null, ...extra]
    .filter(Boolean)
    .join(" ");
}

function readImmersiveStepActive(el: HTMLElement | null): boolean {
  if (!el) return true;
  const step = el.closest("[data-step-active]");
  if (!step) return true;
  return step.getAttribute("data-step-active") === "true";
}

/**
 * Full-bleed photo plane for the ScreenFlow step — stays pinned while content scrolls.
 * Active plane claims `html[data-day-photo=step]` so shell `--day-bg-art` + decor drop
 * (TODAY_MAKE_YOURS §0 single-paint). Inactive steps keep the node, no bitmap decode.
 */
function ImmersiveArtPlane({ role, testId }: { role: TodayStoryArtRole; testId: string }) {
  const ref = useRef<HTMLDivElement>(null);
  const [stepActive, setStepActive] = useState(false);
  useLayoutEffect(() => {
    const el = ref.current;
    if (!el) return;
    const step = el.closest("[data-step-active]");
    const sync = () => setStepActive(readImmersiveStepActive(el));
    sync();
    if (!step) return;
    const obs = new MutationObserver(sync);
    obs.observe(step, { attributes: true, attributeFilter: ["data-step-active"] });
    return () => obs.disconnect();
  }, []);
  useLayoutEffect(() => {
    if (!stepActive) return;
    const root = document.documentElement;
    root.setAttribute("data-day-photo", "step");
    return () => {
      if (root.getAttribute("data-day-photo") === "step") {
        root.removeAttribute("data-day-photo");
      }
    };
  }, [stepActive]);
  const artStyle = useStoryFrameArt(role, stepActive);
  return (
    <div
      ref={ref}
      className={styles.immersiveArt}
      style={artStyle}
      data-testid={testId}
      data-frame-art={role}
      data-frame-art-active={stepActive ? "true" : "false"}
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
  moodPills = [],
  reasonLine = null,
  activityTags = [],
  startHint = copy.storyNext.formDay,
}: {
  salutation: string;
  dateLabel: string;
  headline: string | null;
  loading?: boolean;
  onStart: () => void;
  /** Handoff welcome glass — omit clusters when empty. */
  moodPills?: string[];
  reasonLine?: string | null;
  activityTags?: string[];
  startHint?: string;
}) {
  const showGlass = moodPills.length > 0 || Boolean(reasonLine) || activityTags.length > 0;
  return (
    <div
      className={immersiveClass("photo", styles.frame)}
      data-testid="today-frame-greeting"
      data-frame-art="greeting"
    >
      <ImmersiveArtPlane role="greeting" testId="today-frame-art-greeting" />
      <div className={styles.immersiveContent}>
        <div className={styles.greetingStack} data-story-block="greeting-hero">
          <div className={styles.greetingCopy}>
            <DsEyebrow onDark>{salutation}</DsEyebrow>
            <DsDisplayTitle as="h2" size="md" className={styles.greetingHeadlineOnArt}>
              {loading ? copy.loadingDay : headline || "Сегодня — твой день"}
            </DsDisplayTitle>
            <DsBody size="sm" onDark>
              {dateLabel}
            </DsBody>
          </div>

          {showGlass ? (
            <DsGlassCard testId="today-welcome-glass" className={styles.welcomeGlassDs}>
              {(moodPills.length > 0 || reasonLine) && (
                <div className={styles.welcomeGlassTop}>
                  <span className={styles.welcomeMoon} aria-hidden>
                    ◐
                  </span>
                  <div className={styles.welcomeGlassMain}>
                    {moodPills.length > 0 ? (
                      <DsChipGroup
                        options={moodPills.map((label) => ({ label }))}
                        variant="solid"
                        columns={3}
                        testId="today-welcome-moods"
                      />
                    ) : null}
                    {reasonLine ? (
                      <DsBody size="sm" className={styles.welcomeReasonDs}>
                        <span data-testid="today-welcome-reason">{reasonLine}</span>
                      </DsBody>
                    ) : null}
                  </div>
                </div>
              )}
              {activityTags.length > 0 ? (
                <div className={styles.welcomeTagRow}>
                  <DsChipGroup
                    options={activityTags.map((label) => ({ label }))}
                    variant="outline"
                    columns={3}
                    testId="today-welcome-tags"
                  />
                </div>
              ) : null}
            </DsGlassCard>
          ) : null}

          <button type="button" className={styles.startCtaOnArt} data-testid="today-greeting-start" onClick={onStart}>
            <span className={styles.startArrow} aria-hidden>
              →
            </span>
            <span className={styles.startCtaText}>
              <span className={styles.startCtaLabelOnArt}>Начать день</span>
              <span className={styles.startHintOnArt}>{startHint}</span>
            </span>
          </button>
        </div>
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
  active = true,
}: {
  energyLine: string | null;
  energyCause: string | null;
  dateISO: string;
  onGoNext: () => void;
  nextTitle?: string;
  nextHint?: string;
  /** Only fetch day-flow when this ScreenFlow step is active. */
  active?: boolean;
}) {
  const energy = (energyLine || "").trim() || null;
  const cause = (energyCause || "").trim() || null;
  // Handoff hybrid: Поток дня sits on Day Atmosphere — no ImmersiveArtPlane energy photo.
  return (
    <div className={styles.frame} data-testid="today-frame-energy-flow" data-frame-art="atmosphere">
      <div className={styles.storyScroll} data-story-scroll="pane">
        <section className={`${styles.storyPane} ${styles.storyPaneLift}`} data-story-block="energy-hero">
          <div className={styles.storyPaneBody}>
            <div className={styles.centerStack}>
              <p className={styles.eyebrow}>{copy.pulseLabel}</p>
              {energy ? (
                <h2 className={styles.energyPrimary} data-testid="today-glance-energy-text">
                  {energy}
                </h2>
              ) : (
                <p className={styles.muted} data-testid="today-energy-empty">
                  Энергия дня сегодня без отдельной формулировки.
                </p>
              )}
              {cause ? (
                <p className={styles.detail} data-testid="today-glance-energy-cause">
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
                <p className={styles.eyebrow}>Поток дня</p>
              </header>
              <TodayStoryDayFlowPane dateISO={dateISO} active={active} />
            </div>
          </div>
          <StoryNextAnchor title={nextTitle} hint={nextHint} onNext={onGoNext} />
        </section>
      </div>
    </div>
  );
}

function TodayStoryDayFlowPane({ dateISO, active = true }: { dateISO: string; active?: boolean }) {
  const [windows, setWindows] = useState<GlanceTimelineItem[] | null>(null);
  const [failure, setFailure] = useState<TodaySlotLoadFailure | null>(null);
  const [loaded, setLoaded] = useState(false);
  const [reloadNonce, setReloadNonce] = useState(0);
  const autoRetried = useRef(false);

  useEffect(() => {
    if (!active) return;
    let cancelled = false;
    setLoaded(false);
    setFailure(null);
    void fetchDayFacts(dateISO)
      .then((data) => {
        if (cancelled) return;
        if (data.is_fallback ?? data.degraded) {
          setFailure("unavailable");
          setWindows([]);
        } else {
          setFailure(null);
          setWindows(data.glance_timeline ?? []);
        }
        setLoaded(true);
        autoRetried.current = false;
      })
      .catch((err: unknown) => {
        if (cancelled) return;
        const kind = todaySlotFailureFromError(err);
        if (kind == null) {
          return;
        }
        // One silent retry after cold timeout / flaky transport before painting failure.
        if (!autoRetried.current && (kind === "unavailable" || kind === "no_connection")) {
          autoRetried.current = true;
          clearDayFactsCache();
          setReloadNonce((n) => n + 1);
          return;
        }
        setFailure(kind);
        setWindows([]);
        setLoaded(true);
      });
    return () => {
      cancelled = true;
    };
  }, [dateISO, reloadNonce, active]);

  useEffect(() => {
    autoRetried.current = false;
  }, [dateISO]);

  useEffect(() => {
    const onAuth = () => {
      clearDayFactsCache();
      setReloadNonce((n) => n + 1);
    };
    window.addEventListener("auth:update", onAuth);
    return () => window.removeEventListener("auth:update", onAuth);
  }, []);

  if (!loaded) {
    return (
      <div className={styles.flowPane} data-testid="today-story-day-flow" data-loading="true" aria-busy />
    );
  }

  if (failure === "no_connection") {
    return (
      <div className={styles.flowPane} data-testid="today-story-day-flow" data-failure="no_connection" role="status">
        <p className={styles.flowFailInk}>{todaySlotFailureCopy("no_connection")}</p>
        <button
          type="button"
          className={styles.flowRetryInk}
          data-testid="today-day-flow-retry"
          onClick={() => {
            clearDayFactsCache();
            setReloadNonce((n) => n + 1);
          }}
        >
          Повторить
        </button>
      </div>
    );
  }

  if (failure === "unavailable") {
    return (
      <div className={styles.flowPane} data-testid="today-story-day-flow" data-failure="unavailable" role="status">
        <p className={styles.flowFailInk}>{todaySlotFailureCopy("unavailable")}</p>
        <button
          type="button"
          className={styles.flowRetryInk}
          data-testid="today-day-flow-retry"
          onClick={() => {
            clearDayFactsCache();
            setReloadNonce((n) => n + 1);
          }}
        >
          Повторить
        </button>
      </div>
    );
  }

  // Pure glance_timeline only — bookends УТРО/ВЕЧЕР are chrome labels (WAVE2 §4).
  // Empty windows → empty UI (no invented “no windows” prose).
  const points = buildStoryDayFlow({ glanceWindows: windows });
  if (points.length === 0) {
    return (
      <div className={styles.flowPane} data-testid="today-story-day-flow" data-empty="true" role="status" />
    );
  }

  return <StoryDayFlowList points={points} />;
}

function StoryDayFlowList({ points }: { points: StoryDayFlowPoint[] }) {
  const [openId, setOpenId] = useState<string | null>(null);

  return (
    <ol className={styles.dayFlow} data-testid="today-story-day-flow">
      <li className={styles.dayFlowItem} data-bookend="morning" data-testid="today-day-flow-morning">
        <div className={styles.dayFlowRail} aria-hidden>
          <span className={styles.dayFlowDot} data-muted="true" />
          <span className={styles.dayFlowLine} />
        </div>
        <div className={styles.dayFlowCopy}>
          <div className={styles.dayFlowHeadRow}>
            <p className={styles.dayFlowPhase}>УТРО</p>
            <span className={styles.dayFlowCue}>Старт</span>
          </div>
        </div>
      </li>
      {points.map((point) => {
        const chrome = valenceChromeLabel(point.valence);
        const expandable = Boolean(point.detail);
        const open = openId === point.id;
        return (
          <li
            key={point.id}
            className={styles.dayFlowItem}
            data-valence={point.valence}
            data-timed={point.timed ? "true" : "false"}
            data-expanded={open ? "true" : "false"}
            data-testid={`today-day-flow-${point.id}`}
          >
            <div className={styles.dayFlowRail} aria-hidden>
              <span className={styles.dayFlowDot} />
              <span className={styles.dayFlowLine} />
            </div>
            <div className={styles.dayFlowCopy}>
              <button
                type="button"
                className={styles.dayFlowToggle}
                data-expandable={expandable ? "true" : "false"}
                aria-expanded={expandable ? open : undefined}
                disabled={!expandable}
                onClick={() => {
                  if (!expandable) return;
                  setOpenId((cur) => (cur === point.id ? null : point.id));
                }}
              >
                <div className={styles.dayFlowHeadRow}>
                  <p className={styles.dayFlowPhase}>{point.phase}</p>
                  {chrome ? (
                    <span className={styles.dayFlowCue} data-valence={point.valence}>
                      {chrome}
                    </span>
                  ) : null}
                  {expandable ? (
                    <span className={styles.dayFlowChevron} aria-hidden>
                      {open ? "▾" : "▸"}
                    </span>
                  ) : null}
                </div>
                <p className={styles.dayFlowBody}>{point.body}</p>
              </button>
              {open && point.detail ? (
                <p className={styles.dayFlowDetail} data-testid={`today-day-flow-detail-${point.id}`}>
                  {point.detail}
                </p>
              ) : null}
            </div>
          </li>
        );
      })}
      <li className={styles.dayFlowItem} data-bookend="evening" data-testid="today-day-flow-evening">
        <div className={styles.dayFlowRail} aria-hidden>
          <span className={styles.dayFlowDot} data-muted="true" />
        </div>
        <div className={styles.dayFlowCopy}>
          <div className={styles.dayFlowHeadRow}>
            <p className={styles.dayFlowPhase}>ВЕЧЕР</p>
            <span className={styles.dayFlowCue}>итог</span>
          </div>
        </div>
      </li>
    </ol>
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
  dayPromise = null,
  onPickOutcome,
}: {
  contract: TodayContractV1;
  dateISO: string;
  tapResponse?: TapResponseCode | null;
  onTapRecorded?: (response: TapResponseCode) => void;
  onOpenEvening: () => void;
  dayPromise?: string | null;
  /** Inline handoff outcomes → continuity / ritual_feedback path. */
  onPickOutcome?: (outcome: "done" | "partial" | "not_done") => void;
}) {
  const [outcome, setOutcome] = useState<"done" | "partial" | "not_done" | null>(null);
  const outcomes: { id: "done" | "partial" | "not_done"; label: string }[] = [
    { id: "done", label: "Получилось" },
    { id: "partial", label: "Частично" },
    { id: "not_done", label: "Не получилось" },
  ];

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
          {dayPromise ? (
            <p className={styles.detail} data-testid="today-close-promise-line">
              {dayPromise}
            </p>
          ) : null}
          {onPickOutcome ? (
            <div className={styles.closeOutcomes} data-testid="today-close-outcomes">
              {outcomes.map((row) => (
                <button
                  key={row.id}
                  type="button"
                  className={outcome === row.id ? styles.closeOutcomeActive : styles.closeOutcome}
                  data-testid={`today-close-outcome-${row.id}`}
                  onClick={() => {
                    setOutcome(row.id);
                    onPickOutcome(row.id);
                  }}
                >
                  {row.label}
                </button>
              ))}
            </div>
          ) : null}
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
