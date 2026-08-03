"use client";

import Link from "next/link";
import { useEffect, useMemo, useState, type CSSProperties } from "react";
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
import { TodayScreenBlock, TodayScreenBlockStack } from "@/components/today/composition/TodayScreenBlock";
import { TodayTapWidget } from "@/components/today/composition/TodayWave2Slots";
import { domainIconForChapterId } from "@/lib/todayReadingDomainIcon";
import { pickMoveIfThenFromContract } from "@/lib/todayMoveIfThen";
import { TODAY_NO_SHARP_FOCUS_COPY } from "@/lib/todayGlanceTexture";
import {
  isDayScenarioReadyForChapters,
} from "@/lib/todayScenarioChapters";
import {
  todaySlotFailureCopy,
  type TodaySlotLoadFailure,
} from "@/lib/todaySlotAvailability";
import styles from "@/components/today/composition/TodayPersonalizedProductSection.module.css";

export type TodayPersonalActFilter = "reading" | "move" | "response" | "all";

/** Which personal acts to mount for a given ScreenFlow slide filter. */
export function resolveTodayPersonalActVisibility(
  actFilter: TodayPersonalActFilter = "all",
): { showReading: boolean; showMove: boolean; showResponse: boolean } {
  return {
    showReading: actFilter === "all" || actFilter === "reading",
    showMove: actFilter === "all" || actFilter === "move",
    showResponse: actFilter === "all" || actFilter === "response",
  };
}

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
  actFilter?: TodayPersonalActFilter;
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
  const [expandedSphereIds, setExpandedSphereIds] = useState<Record<string, boolean>>({});

  useEffect(() => {
    if (!focusSphere || actFilter === "move" || actFilter === "response") return;
    const id = `today-narrative-sphere-${focusSphere}`;
    const el = document.querySelector(`[data-testid="today-narrative-block-${id}"], [data-testid="today-narrative-${id}"]`);
    if (el && "scrollIntoView" in el) {
      (el as HTMLElement).scrollIntoView({ behavior: "smooth", block: "nearest" });
    }
    // Deep-link from Glance opens opportunity/trap for that sphere
    setExpandedSphereIds((prev) => ({ ...prev, [`sphere-${focusSphere}`]: true, [focusSphere]: true }));
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

  /** v3.1: one support slot — practice XOR affirmation (rotate by local date). */
  const preferAffirmationSlot = useMemo(() => {
    const key = dateISO || "0";
    let h = 0;
    for (let i = 0; i < key.length; i += 1) h = (h * 31 + key.charCodeAt(i)) >>> 0;
    return h % 2 === 1;
  }, [dateISO]);

  const showAffirmationSupport = Boolean(
    (practiceRec?.kind === "affirmation" && practiceRec.text) || affirmationTool,
  );
  const showPracticeSupport = Boolean(practiceTool || (practiceRec?.kind === "practice" && practiceRec.text));
  const supportSlot: "affirmation" | "practice" | null =
    showAffirmationSupport && showPracticeSupport
      ? preferAffirmationSlot
        ? "affirmation"
        : "practice"
      : showAffirmationSupport
        ? "affirmation"
        : showPracticeSupport
          ? "practice"
          : null;

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
          <TodayScreenBlock testId="today-reading-fallback">
            <p
              className={styles.readingParagraph}
              role="status"
              data-fallback="true"
              data-failure={contentFailure}
            >
              {todaySlotFailureCopy(contentFailure)}
            </p>
          </TodayScreenBlock>
        ) : null}

        {!contentFailure && contract.day_story?.interpretation_status === "unavailable" ? (
          <TodayScreenBlock testId="today-interpretation-unavailable">
            <p className={styles.readingParagraph}>
              {contract.day_story.interpretation_unavailable_message ||
                "Мы не смогли подготовить персональную интерпретацию дня. Попробуйте обновить экран через несколько минут."}
            </p>
          </TodayScreenBlock>
        ) : null}

        {!contentFailure &&
        contract.day_story?.interpretation_status !== "unavailable" &&
        narrative.chapters.length === 0 ? (
          <TodayScreenBlock testId="today-reading-no-focus">
            <p className={styles.readingParagraph} role="status">
              {isDayScenarioReadyForChapters(contract)
                ? TODAY_NO_SHARP_FOCUS_COPY
                : todaySlotFailureCopy("unavailable")}
            </p>
          </TodayScreenBlock>
        ) : null}

        {!contentFailure && narrative.chapters.length > 0 ? (
        <TodayScreenBlockStack
          className={profileMotionStyles.staggerItem}
          testId="today-entity-synthesis"
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

            const isSphereChapter = chapter.id.startsWith("sphere-");
            const hasDual = Boolean(
              chapter.dual && (chapter.dual.strengthen.length || chapter.dual.soften.length),
            );
            const dualExpanded = !isSphereChapter || expandedSphereIds[chapter.id] === true;
            const DomainIcon = domainIconForChapterId(chapter.id);

            return (
              <div
                key={chapter.id}
                style={profileMotionStaggerDelay(chapterIndex + 1, 70) as CSSProperties}
                data-testid={`today-narrative-${chapter.id}`}
              >
                <TodayScreenBlock>
                <ProductNarrativeBlock
                  id={chapter.id}
                  kicker={chapter.kicker}
                  kickerIcon={
                    DomainIcon ? (
                      <span data-testid={`today-reading-domain-icon-${chapter.id}`}>
                        <DomainIcon />
                      </span>
                    ) : null
                  }
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
                  surface="plain"
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
                  {isSphereChapter && hasDual && !dualExpanded ? (
                    <button
                      type="button"
                      className={`orbit-button orbit-button-secondary ${styles.practiceAction}`}
                      data-testid={`today-reading-expand-${chapter.id}`}
                      onClick={() =>
                        setExpandedSphereIds((prev) => ({ ...prev, [chapter.id]: true }))
                      }
                    >
                      Возможность и ловушка
                    </button>
                  ) : null}
                  {dualExpanded &&
                  chapter.dual &&
                  (chapter.dual.strengthen.length || chapter.dual.soften.length) ? (
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
                </TodayScreenBlock>
              </div>
            );
          })}

          {narrative.vibeClosing && !narrative.chapters.some((c) => c.id === "vibe") ? (
            <p className={styles.vibeClosing} data-testid="today-vibe-closing">
              {narrative.vibeClosing}
            </p>
          ) : null}
        </TodayScreenBlockStack>
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
          <TodayScreenBlock testId="today-move-fallback">
            <p
              className={styles.readingParagraph}
              role="status"
              data-fallback="true"
              data-failure={contentFailure}
            >
              {todaySlotFailureCopy(contentFailure)}
            </p>
          </TodayScreenBlock>
        ) : (
          <TodayScreenBlockStack>
        {colorGuide ? (
          <TodayScreenBlock testId="today-zone-color-guide">
            <TodayDayColorGuideSection guide={colorGuide} />
          </TodayScreenBlock>
        ) : null}
        {moveIfThen && (moveIfThen.do || moveIfThen.avoid) ? (
          <TodayScreenBlock eyebrow={copy.journey.moveIfThenEyebrow} testId="today-zone-move-if-then">
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
          </TodayScreenBlock>
        ) : null}
        <TodayScreenBlock eyebrow="Цель на сегодня" testId="today-zone-promise">
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
        </TodayScreenBlock>

        {strengthenTools.length > 0 || practiceRec?.text || activeHabit || activeAscetic ? (
          <TodayScreenBlock testId="today-zone-strengthen">
            <div className={styles.practicesHeader}>
              <p className={styles.eyebrowInline}>Практики и опоры</p>
              {totalTools > 1 ? (
                <p className={styles.practicesProgress}>
                  {completedCount} из {totalTools}
                </p>
              ) : null}
            </div>

            {supportSlot === "affirmation" &&
            practiceRec?.text &&
            practiceRec.kind === "affirmation" &&
            !affirmationTool ? (
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

            {supportSlot === "practice" && practiceTool ? (
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

            {supportSlot === "affirmation" && affirmationTool ? (
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
          </TodayScreenBlock>
        ) : (
          <TodayScreenBlock eyebrow="Практики и опоры" testId="today-zone-strengthen-empty">
            <p className={styles.practiceMeta}>
              <Link href="/practices" data-testid="today-setup-practices-link">
                {copy.setupPracticesLink} →
              </Link>
            </p>
          </TodayScreenBlock>
        )}
          </TodayScreenBlockStack>
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
          <TodayScreenBlock testId="today-response-fallback">
            <p
              className={styles.readingParagraph}
              role="status"
              data-fallback="true"
              data-failure={contentFailure}
            >
              {todaySlotFailureCopy(contentFailure)}
            </p>
          </TodayScreenBlock>
        ) : (
          <TodayScreenBlock testId="today-slot-tap-wrap">
            <TodayTapWidget
              contract={contract}
              dateISO={dateISO || ""}
              initialResponse={tapResponse}
              onRecorded={onTapRecorded}
            />
          </TodayScreenBlock>
        )}
      </ProductJourneyScene>
  );

  // Parent ScreenFlow (TodayProductScreenFlow) already owns Reading/Move/Response
  // steps. When asScreenFlowSteps is set, strip section chrome and render only
  // the filtered act — do NOT nest another trio of ScreenFlowSteps (that made
  // steps 3–5 look identical).
  if (asScreenFlowSteps || actFilter !== "all") {
    const { showReading, showMove, showResponse } =
      resolveTodayPersonalActVisibility(actFilter);
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
