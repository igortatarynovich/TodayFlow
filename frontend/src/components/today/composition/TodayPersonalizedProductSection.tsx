"use client";

import Link from "next/link";
import { useEffect, useMemo, type CSSProperties } from "react";
import {
  profileMotionStaggerDelay,
  profileMotionStyles,
  useProfileMotionInView,
} from "@/components/foundation/ProfileMotion";
import {
  ProductJourneyScene,
  ProductNarrativeBlock,
  planetIconSrc,
} from "@/components/product-ui/ProductJourneyScene";
import journeyStyles from "@/components/product-ui/ProductJourneyScene.module.css";
import type { MorningRitualData } from "@/components/today/todayPageUtils";
import type { TodayPromiseSuggestion } from "@/lib/todayDayDialogue";
import type { TodayContractV1 } from "@/lib/todayContract";
import type { TodayStrengthenTool } from "@/lib/todayCompositionModel";
import type { TodayDayColorGuide } from "@/lib/todayDayColorGuide";
import type { TodaySkyCard } from "@/lib/todayDaySpine";
import { buildTodayDayNarrative } from "@/lib/todayDayNarrative";
import type { TodayDayStoryViewModel } from "@/lib/todayDayStoryModel";
import type { CoreProfile } from "@/lib/types";
import { TODAY_COMPOSITION_COPY as copy } from "@/components/today/composition/todayCompositionCopy";
import { TodayDayColorGuideSection } from "@/components/today/composition/TodayDayColorGuideSection";
import { TodayTapWidget } from "@/components/today/composition/TodayWave2Slots";
import { ScreenFlowStep } from "@/design-system/primitives/ScreenFlow";
import { pickMoveIfThenFromContract } from "@/lib/todayMoveIfThen";
import {
  todaySlotFailureCopy,
  type TodaySlotLoadFailure,
} from "@/lib/todaySlotAvailability";
import styles from "@/components/today/composition/TodayPersonalizedProductSection.module.css";

type Props = {
  story: TodayDayStoryViewModel;
  contract: TodayContractV1;
  strengthenTools: TodayStrengthenTool[];
  promiseSuggestions: TodayPromiseSuggestion[];
  dayGoal: string | null;
  practiceCompleted: boolean;
  practiceStarted: boolean;
  affirmationRead: boolean;
  practiceCompleting: boolean;
  activeHabit?: { id: number; name: string } | null;
  activeAscetic?: { id: number; title: string } | null;
  habitMarked: boolean;
  asceticMarked: boolean;
  habitMarking?: boolean;
  asceticMarking?: boolean;
  goalDraftOpen: boolean;
  goalDraft: string;
  coreProfile?: CoreProfile | null;
  tarotDeepenHref?: string | null;
  embeddedInWebDashboard?: boolean;
  skyCards?: TodaySkyCard[];
  colorGuide?: TodayDayColorGuide | null;
  morningRitualData?: MorningRitualData | null;
  dateISO?: string;
  /** Deep-link from Glance sphere token — scroll/highlight matching Reading card */
  focusSphere?: string | null;
  /** Transport / degraded — never leave Reading/Move/Response silently empty */
  contentFailure?: TodaySlotLoadFailure | null;
  tapResponse?: "avoided_trap" | "fell_into_trap" | "not_applicable" | "skipped" | null;
  onTapRecorded?: (response: "avoided_trap" | "fell_into_trap" | "not_applicable" | "skipped") => void;
  onPickPromise: (text: string) => void;
  onOpenGoalDraft: () => void;
  onGoalDraftChange: (value: string) => void;
  onSaveGoal: () => void;
  onPracticeAction: () => void;
  onAffirmationDone: () => void;
  onHabitMark?: () => void;
  onAsceticMark?: () => void;
  asScreenFlowSteps?: boolean;
  /** When set, render only one act (for ScreenFlow parent wrappers). */
  actFilter?: "reading" | "move" | "response" | "all";
};

function electionalStatusLabel(status: string): string {
  switch (status) {
    case "fail":
      return "Стоп";
    case "caution":
      return "Осторожно";
    case "pass":
      return "Ок";
    case "supportive":
      return "Поддержка";
    case "avoid":
      return "Избегать";
    default:
      return "Заметка";
  }
}

export function TodayPersonalizedProductSection({
  story,
  contract,
  strengthenTools,
  promiseSuggestions,
  dayGoal,
  practiceCompleted,
  practiceStarted,
  affirmationRead,
  practiceCompleting,
  activeHabit = null,
  activeAscetic = null,
  habitMarked,
  asceticMarked,
  habitMarking = false,
  asceticMarking = false,
  goalDraftOpen,
  goalDraft,
  coreProfile: _coreProfile,
  tarotDeepenHref: _tarotDeepenHref,
  embeddedInWebDashboard = false,
  skyCards = [],
  colorGuide = null,
  morningRitualData = null,
  dateISO = "",
  focusSphere = null,
  contentFailure = null,
  tapResponse = null,
  onTapRecorded,
  onPickPromise,
  onOpenGoalDraft,
  onGoalDraftChange,
  onSaveGoal,
  onPracticeAction,
  onAffirmationDone,
  onHabitMark,
  onAsceticMark,
  asScreenFlowSteps = false,
  actFilter = "all",
}: Props) {
  const practiceRec = contract.day_story?.practice_recommendation;

  useEffect(() => {
    if (!focusSphere || actFilter === "move" || actFilter === "response") return;
    const id = `today-narrative-sphere-${focusSphere}`;
    const el = document.querySelector(`[data-testid="today-narrative-block-${id}"], [data-testid="today-narrative-${id}"]`);
    if (el && "scrollIntoView" in el) {
      (el as HTMLElement).scrollIntoView({ behavior: "smooth", block: "nearest" });
    }
  }, [focusSphere, actFilter]);

  const completedCount =
    (practiceCompleted ? 1 : 0) +
    (affirmationRead ? 1 : 0) +
    (habitMarked ? 1 : 0) +
    (asceticMarked ? 1 : 0);
  const totalTools =
    strengthenTools.length + (activeHabit ? 1 : 0) + (activeAscetic ? 1 : 0);

  const practiceTool = strengthenTools.find((tool) => tool.id === "practice");
  const affirmationTool = strengthenTools.find((tool) => tool.id === "affirmation");
  const otherTools = strengthenTools.filter((tool) => tool.id !== "practice" && tool.id !== "affirmation");

  const moveIfThen = useMemo(() => pickMoveIfThenFromContract(contract), [contract]);

  const narrative = useMemo(() => {
    const storyWithSky =
      skyCards.length && (!story.skyCards || story.skyCards.length === 0)
        ? { ...story, skyCards }
        : story.skyCards?.length
          ? story
          : { ...story, skyCards };
    return buildTodayDayNarrative({
      contract,
      story: storyWithSky,
      morningRitualData,
      colorGuide: colorGuide ?? story.colorGuide,
    });
  }, [contract, story, skyCards, morningRitualData, colorGuide]);

  const motion = useProfileMotionInView<HTMLElement>(40);

  const readingLabel =
    narrative.composition === "scenario_chapters"
      ? copy.journey.readingTitleStory
      : copy.journey.readingTitle;

  const readingScene = (
      <ProductJourneyScene
        step={3}
        title={asScreenFlowSteps ? undefined : (narrative.composition === "scenario_chapters" ? copy.journey.readingTitleStory : copy.journey.readingTitle)}
        lead={asScreenFlowSteps ? null : copy.journey.readingLead}
        motif="today"
        accent="sky"
        testId="today-zone-reading"
      >
        {contentFailure ? (
          <p
            className={styles.readingParagraph}
            role="status"
            data-testid="today-reading-fallback"
            data-fallback="true"
            data-failure={contentFailure}
          >
            {todaySlotFailureCopy(contentFailure)}
          </p>
        ) : null}

        {!contentFailure && contract.day_story?.interpretation_status === "unavailable" ? (
          <p className={styles.readingParagraph} data-testid="today-interpretation-unavailable">
            {contract.day_story.interpretation_unavailable_message ||
              "Мы не смогли подготовить персональную интерпретацию дня. Попробуйте обновить экран через несколько минут."}
          </p>
        ) : null}

        {!contentFailure &&
        contract.day_story?.interpretation_status !== "unavailable" &&
        narrative.chapters.length === 0 ? (
          <p
            className={styles.readingParagraph}
            role="status"
            data-testid="today-reading-fallback"
            data-fallback="true"
            data-failure="unavailable"
          >
            {todaySlotFailureCopy("unavailable")}
          </p>
        ) : null}

        {!contentFailure && narrative.chapters.length > 0 ? (
        <div
          className={`${styles.narrativeBlocks} ${profileMotionStyles.staggerItem}`}
          style={profileMotionStaggerDelay(0, 60) as CSSProperties}
          data-testid="today-entity-synthesis"
        >
          {narrative.chapters.map((chapter, chapterIndex) => {
            const planetSrc = planetIconSrc(chapter.planetHint);
            const chapterAccent =
              chapter.id === "opening"
                ? "/images/cosmic/moon_orb.webp"
                : chapter.id === "force"
                  ? "/images/cosmic/eclipse_wash.webp"
                  : null;
            const media =
              chapter.id === "supports" && chapter.colorHex
                ? ({ kind: "color" as const, hex: chapter.colorHex, label: chapter.colorLabel ?? undefined })
                : planetSrc
                  ? ({ kind: "image" as const, src: planetSrc, alt: chapter.planetHint ?? "" })
                  : chapterAccent
                    ? ({ kind: "image" as const, src: chapterAccent, alt: "" })
                    : null;

            const bodyParagraphs = [...(chapter.lead ? [chapter.lead] : []), ...chapter.paragraphs];
            // Soft why stays visible with label when present in opening.
            const softWhyInBody =
              chapter.id === "opening" && narrative.softWhy
                ? bodyParagraphs.includes(narrative.softWhy)
                : false;

            return (
              <div
                key={chapter.id}
                style={profileMotionStaggerDelay(chapterIndex + 1, 70) as CSSProperties}
                data-testid={`today-narrative-${chapter.id}`}
              >
                <ProductNarrativeBlock
                  id={chapter.id}
                  kicker={chapter.kicker}
                  lead={chapter.lead}
                  paragraphs={
                    softWhyInBody
                      ? bodyParagraphs.filter((p) => p !== narrative.softWhy)
                      : chapter.lead
                        ? chapter.paragraphs
                        : bodyParagraphs
                  }
                  accent={chapter.accent ?? "default"}
                  media={media}
                  collapseAfter={chapter.collapseAfter}
                  testId={`today-narrative-block-${chapter.id}`}
                >
                  {softWhyInBody && narrative.softWhy ? (
                    <p className={`${journeyStyles.narrativeBlockBody} ${styles.narrativeWhy}`} data-testid="today-soft-why">
                      <span className={styles.softWhyLabel}>Почему это важно сегодня</span>
                      {narrative.softWhy}
                    </p>
                  ) : null}
                  {chapter.id === "personal" && chapter.signals?.length ? (
                    <dl className={styles.personalSignals} data-testid="today-personal-signals">
                      {chapter.signals.map((signal) => (
                        <div key={`${signal.label}-${signal.value}`} className={styles.personalSignalRow}>
                          <dt className={styles.personalSignalLabel}>{signal.label}</dt>
                          <dd className={styles.personalSignalValue}>{signal.value}</dd>
                        </div>
                      ))}
                    </dl>
                  ) : null}
                  {chapter.id === "electional" && chapter.checklist?.length ? (
                    <dl className={styles.electionalChecklist} data-testid="today-electional-checklist">
                      {chapter.checklist.map((row) => (
                        <div
                          key={`${row.id}-${row.title}`}
                          className={styles.electionalCheckRow}
                          data-status={row.status}
                        >
                          <dt className={styles.electionalCheckStatus}>{electionalStatusLabel(row.status)}</dt>
                          <dd className={styles.electionalCheckBody}>
                            <span className={styles.electionalCheckTitle}>{row.title}</span>
                            {row.story ? (
                              <span className={styles.electionalCheckStory}>{row.story}</span>
                            ) : null}
                          </dd>
                        </div>
                      ))}
                    </dl>
                  ) : null}
                  {chapter.dual && (chapter.dual.strengthen.length || chapter.dual.soften.length) ? (
                    <div className={journeyStyles.dualPanels}>
                      {chapter.dual.strengthen.length ? (
                        <div className={journeyStyles.dualPanel}>
                          <p className={journeyStyles.dualPanelTitle}>
                            {chapter.id === "force"
                              ? copy.expectLabel
                              : chapter.id === "scenes" || chapter.id.startsWith("sphere-")
                                ? copy.journey.sceneOpportunityLabel
                                : "Сильнее"}
                          </p>
                          {chapter.dual.strengthen.map((line) => (
                            <p key={line.slice(0, 40)} className={journeyStyles.dualPanelBody}>
                              {line}
                            </p>
                          ))}
                        </div>
                      ) : null}
                      {chapter.dual.soften.length ? (
                        <div className={journeyStyles.dualPanel}>
                          <p className={journeyStyles.dualPanelTitle}>
                            {chapter.id === "force"
                              ? copy.trapLabel
                              : chapter.id === "scenes" || chapter.id.startsWith("sphere-")
                                ? copy.journey.sceneTrapLabel
                                : "Мягче / не дожимать"}
                          </p>
                          {chapter.dual.soften.map((line) => (
                            <p key={line.slice(0, 40)} className={journeyStyles.dualPanelBody}>
                              {line}
                            </p>
                          ))}
                        </div>
                      ) : null}
                    </div>
                  ) : null}
                </ProductNarrativeBlock>
              </div>
            );
          })}

          {narrative.vibeClosing && !narrative.chapters.some((c) => c.id === "vibe") ? (
            <p className={styles.vibeClosing} data-testid="today-vibe-closing">
              {narrative.vibeClosing}
            </p>
          ) : null}
        </div>
        ) : null}
      </ProductJourneyScene>
  );

  const moveScene = (
      <ProductJourneyScene
        step={4}
        title={asScreenFlowSteps ? undefined : copy.journey.moveTitle}
        lead={asScreenFlowSteps ? null : copy.journey.moveLead}
        motif="effort"
        accent="support"
        testId="today-zone-move"
      >
        {contentFailure ? (
          <p
            className={styles.readingParagraph}
            role="status"
            data-testid="today-move-fallback"
            data-fallback="true"
            data-failure={contentFailure}
          >
            {todaySlotFailureCopy(contentFailure)}
          </p>
        ) : (
          <>
        {moveIfThen && (moveIfThen.do || moveIfThen.avoid) ? (
          <article className={styles.productCard} data-testid="today-zone-move-if-then">
            <p className={styles.cardEyebrow}>{copy.journey.moveIfThenEyebrow}</p>
            {moveIfThen.do ? (
              <div className={styles.moveIfThenRow} data-testid="today-move-do">
                <p className={styles.moveIfThenLabel}>{copy.journey.moveDoLabel}</p>
                <p className={styles.readingParagraph}>{moveIfThen.do}</p>
              </div>
            ) : null}
            {moveIfThen.avoid ? (
              <div className={styles.moveIfThenRow} data-testid="today-move-avoid">
                <p className={styles.moveIfThenLabel}>{copy.journey.moveAvoidLabel}</p>
                <p className={styles.readingParagraph}>{moveIfThen.avoid}</p>
              </div>
            ) : null}
          </article>
        ) : null}
        {colorGuide ? <TodayDayColorGuideSection guide={colorGuide} /> : null}
        <article className={styles.productCard} data-testid="today-zone-promise">
          <p className={styles.cardEyebrow}>Цель на сегодня</p>
          {dayGoal && !goalDraftOpen ? (
            <p className={styles.readingParagraph} data-testid="today-promise-active">
              {dayGoal}
            </p>
          ) : null}
          {!dayGoal && promiseSuggestions.length ? (
            <div className={styles.suggestionRow} data-testid="today-promise-suggestions">
              {promiseSuggestions.map((item) => (
                <button
                  key={item.id}
                  type="button"
                  className={styles.suggestionChip}
                  onClick={() => onPickPromise(item.text)}
                >
                  {item.text}
                </button>
              ))}
            </div>
          ) : null}
          {goalDraftOpen ? (
            <div className={styles.customGoalForm} data-testid="today-entity-daily-goal">
              <input
                id="day-goal-input-product"
                className={styles.goalInput}
                value={goalDraft}
                onChange={(event) => onGoalDraftChange(event.target.value)}
                maxLength={200}
                placeholder="Своими словами — из того, что уже звучит в дне"
              />
              <button type="button" className="orbit-button orbit-button-primary" onClick={onSaveGoal}>
                {copy.goalSave}
              </button>
            </div>
          ) : (
            <button
              type="button"
              className={styles.customGoalRow}
              data-testid="today-zone-promise-open"
              onClick={onOpenGoalDraft}
            >
              {dayGoal ? "Изменить своими словами…" : "+ Своя цель"}
            </button>
          )}
        </article>

        {strengthenTools.length > 0 || practiceRec?.text || activeHabit || activeAscetic ? (
          <article className={styles.productCard} data-testid="today-zone-strengthen">
            <div className={styles.practicesHeader}>
              <p className={styles.cardEyebrow}>Практики и опоры</p>
              {totalTools > 1 ? (
                <p className={styles.practicesProgress}>
                  {completedCount} из {totalTools}
                </p>
              ) : null}
            </div>

            {practiceRec?.text && practiceRec.kind === "affirmation" && !affirmationTool ? (
              <div className={styles.practiceRow}>
                <span
                  className={affirmationRead ? styles.practiceCheckDone : styles.practiceCheck}
                  aria-hidden
                />
                <div className={styles.practiceBody}>
                  <p className={styles.practiceTitle}>{practiceRec.text}</p>
                  {practiceRec.reason ? <p className={styles.practiceMeta}>{practiceRec.reason}</p> : null}
                  {!affirmationRead ? (
                    <button
                      type="button"
                      className={`orbit-button orbit-button-secondary ${styles.practiceAction}`}
                      data-testid="today-tool-affirmation-done"
                      onClick={onAffirmationDone}
                    >
                      {copy.markAffirmationDone}
                    </button>
                  ) : (
                    <p className={styles.practiceMeta}>{copy.affirmationDone}</p>
                  )}
                </div>
              </div>
            ) : null}

            {practiceTool ? (
              <div className={styles.practiceRow}>
                <span
                  className={practiceCompleted ? styles.practiceCheckDone : styles.practiceCheck}
                  aria-hidden
                />
                <div className={styles.practiceBody}>
                  <p className={styles.practiceTitle}>{practiceTool.title}</p>
                  {practiceTool.duration ? <p className={styles.practiceMeta}>{practiceTool.duration}</p> : null}
                  {practiceRec?.reason && practiceRec.kind === "practice" ? (
                    <p className={styles.practiceMeta}>{practiceRec.reason}</p>
                  ) : null}
                  {!practiceCompleted ? (
                    <button
                      type="button"
                      className={`orbit-button orbit-button-secondary ${styles.practiceAction}`}
                      data-testid="today-tool-practice"
                      disabled={practiceCompleting}
                      onClick={() => void onPracticeAction()}
                    >
                      {practiceStarted ? copy.practiceComplete : copy.practiceStart}
                    </button>
                  ) : (
                    <p className={styles.practiceMeta}>{copy.practiceCompleted}</p>
                  )}
                </div>
              </div>
            ) : null}

            {affirmationTool ? (
              <div className={styles.practiceRow}>
                <span className={affirmationRead ? styles.practiceCheckDone : styles.practiceCheck} aria-hidden />
                <div className={styles.practiceBody}>
                  <p className={styles.practiceTitle}>{affirmationTool.title}</p>
                  {practiceRec?.reason && practiceRec.kind === "affirmation" ? (
                    <p className={styles.practiceMeta}>{practiceRec.reason}</p>
                  ) : null}
                  {!affirmationRead ? (
                    <button
                      type="button"
                      className={`orbit-button orbit-button-secondary ${styles.practiceAction}`}
                      data-testid="today-tool-affirmation-done"
                      onClick={onAffirmationDone}
                    >
                      {copy.markAffirmationDone}
                    </button>
                  ) : (
                    <p className={styles.practiceMeta}>{copy.affirmationDone}</p>
                  )}
                </div>
              </div>
            ) : null}

            {activeHabit ? (
              <div className={styles.practiceRow} data-testid="today-tool-habit-row">
                <span className={habitMarked ? styles.practiceCheckDone : styles.practiceCheck} aria-hidden />
                <div className={styles.practiceBody}>
                  <p className={styles.practiceTitle}>{activeHabit.name}</p>
                  <p className={styles.practiceMeta}>Привычка</p>
                  {!habitMarked ? (
                    <button
                      type="button"
                      className={`orbit-button orbit-button-secondary ${styles.practiceAction}`}
                      data-testid="today-tool-habit-done"
                      disabled={habitMarking || !onHabitMark}
                      onClick={() => onHabitMark?.()}
                    >
                      {copy.markHabitDone}
                    </button>
                  ) : (
                    <p className={styles.practiceMeta}>{copy.habitDone}</p>
                  )}
                </div>
              </div>
            ) : null}

            {activeAscetic ? (
              <div className={styles.practiceRow} data-testid="today-tool-ascetic-row">
                <span className={asceticMarked ? styles.practiceCheckDone : styles.practiceCheck} aria-hidden />
                <div className={styles.practiceBody}>
                  <p className={styles.practiceTitle}>{activeAscetic.title}</p>
                  <p className={styles.practiceMeta}>Аскеза</p>
                  {!asceticMarked ? (
                    <button
                      type="button"
                      className={`orbit-button orbit-button-secondary ${styles.practiceAction}`}
                      data-testid="today-tool-ascetic-done"
                      disabled={asceticMarking || !onAsceticMark}
                      onClick={() => onAsceticMark?.()}
                    >
                      {copy.markAsceticDone}
                    </button>
                  ) : (
                    <p className={styles.practiceMeta}>{copy.asceticDone}</p>
                  )}
                </div>
              </div>
            ) : null}

            {otherTools.map((tool) => (
              <div key={tool.id} className={styles.practiceRow}>
                <span className={styles.practiceCheck} aria-hidden />
                <div className={styles.practiceBody}>
                  <p className={styles.practiceTitle}>{tool.title}</p>
                  {tool.detail ? <p className={styles.practiceMeta}>{tool.detail}</p> : null}
                </div>
              </div>
            ))}

            <p className={styles.practiceMeta} style={{ marginTop: "0.75rem" }}>
              <Link href="/practices" data-testid="today-setup-practices-link">
                {copy.setupPracticesLink} →
              </Link>
            </p>
          </article>
        ) : (
          <article className={styles.productCard} data-testid="today-zone-strengthen-empty">
            <p className={styles.cardEyebrow}>Практики и опоры</p>
            <p className={styles.practiceMeta}>
              <Link href="/practices" data-testid="today-setup-practices-link">
                {copy.setupPracticesLink} →
              </Link>
            </p>
          </article>
        )}
          </>
        )}
      </ProductJourneyScene>
  );

  const bridgeScene = (
      <ProductJourneyScene
        step={5}
        title={asScreenFlowSteps ? undefined : copy.journey.bridgeTitle}
        lead={asScreenFlowSteps ? null : copy.journey.bridgeLead}
        motif="bridge"
        accent="action"
        bridge
        testId="today-zone-bridges-wrap"
      >
        {contentFailure ? (
          <p
            className={styles.readingParagraph}
            role="status"
            data-testid="today-response-fallback"
            data-fallback="true"
            data-failure={contentFailure}
          >
            {todaySlotFailureCopy(contentFailure)}
          </p>
        ) : (
          <TodayTapWidget
            contract={contract}
            dateISO={dateISO || ""}
            initialResponse={tapResponse}
            onRecorded={onTapRecorded}
          />
        )}
      </ProductJourneyScene>
  );

  if (asScreenFlowSteps) {
    return (
      <>
        <ScreenFlowStep id="reading" label={readingLabel} scrollable>{readingScene}</ScreenFlowStep>
        <ScreenFlowStep id="move" label={copy.journey.moveTitle} scrollable>{moveScene}</ScreenFlowStep>
        <ScreenFlowStep id="response" label={copy.journey.bridgeTitle} scrollable>{bridgeScene}</ScreenFlowStep>
      </>
    );
  }

  const showReading = actFilter === "all" || actFilter === "reading";
  const showMove = actFilter === "all" || actFilter === "move";
  const showResponse = actFilter === "all" || actFilter === "response";

  if (actFilter !== "all") {
    return (
      <>
        {showReading ? readingScene : null}
        {showMove ? moveScene : null}
        {showResponse ? bridgeScene : null}
      </>
    );
  }

  return (
    <section
      ref={motion.ref}
      className={`${styles.section} ${embeddedInWebDashboard ? styles.sectionWebEmbed : ""} ${motion.className}`.trim()}
      style={motion.style}
      data-testid="today-zone-personal"
    >
      {readingScene}
      {moveScene}
      {bridgeScene}
    </section>
  );
}
