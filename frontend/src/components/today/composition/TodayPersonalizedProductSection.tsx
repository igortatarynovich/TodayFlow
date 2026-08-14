"use client";

import Link from "next/link";
import { useEffect, useMemo, useState, type CSSProperties } from "react";
import { DsButton, DsCallout, DsQuote } from "@/design-system";
import { DsTextField } from "@/design-system/primitives/DsForm";
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
import type { TodayContractV1, TodayDepthTopicId } from "@/lib/todayContract";
import type { TodayStrengthenTool } from "@/lib/todayCompositionModel";
import type { TodayDayColorGuide } from "@/lib/todayDayColorGuide";
import type { TodaySkyCard } from "@/lib/todayDaySpine";
import { buildTodayDayNarrative } from "@/lib/todayDayNarrative";
import type { TodayDayStoryViewModel } from "@/lib/todayDayStoryModel";
import type { CoreProfile } from "@/lib/types";
import { TODAY_COMPOSITION_COPY as copy } from "@/components/today/composition/todayCompositionCopy";
import { TodayDayColorGuideSection } from "@/components/today/composition/TodayDayColorGuideSection";
import { TodayDepthLayerSection } from "@/components/today/composition/TodayDepthLayerSection";
import { pickTodayDepthMenu } from "@/lib/todayDepthMenuToday";
import { TodayPracticeGiftBlock } from "@/components/today/composition/TodayPracticeGiftBlock";
import { TodayProgressTracker } from "@/components/today/composition/TodayProgressTracker";
import { TodayScreenBlock, TodayScreenBlockStack } from "@/components/today/composition/TodayScreenBlock";
import { TodayTapWidget } from "@/components/today/composition/TodayWave2Slots";
import { domainIconForChapterId } from "@/lib/todayReadingDomainIcon";
import { calloutLabelForChapterId } from "@/lib/todayReadingCallout";
import { pickMoveIfThenFromContract } from "@/lib/todayMoveIfThen";
import { TODAY_NO_SHARP_FOCUS_COPY } from "@/lib/todayGlanceTexture";
import {
  isDayScenarioReadyForChapters,
} from "@/lib/todayScenarioChapters";
import {
  fetchDomainVerdicts,
  isSilentCalmBank,
  orderDomainVerdicts,
  scrubDomainVerdictJargon,
  type DomainKey,
} from "@/lib/todayDomainVerdicts";
import {
  todaySlotFailureCopy,
  type TodaySlotLoadFailure,
} from "@/lib/todaySlotAvailability";
import { readingSphereChapterId } from "@/lib/todayFocusDeepen";
import type { TodayProgressRow } from "@/lib/todayGrowthTrackers";
import styles from "@/design-system/compositions/dsPersonalizedProduct.module.css";

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
  progressRows?: TodayProgressRow[];
  preferredDepthTopic?: TodayDepthTopicId | string | null;
  autoPickDepthTopic?: boolean;
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
  progressRows = [],
  preferredDepthTopic = null,
  autoPickDepthTopic = false,
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
  const [domainWhys, setDomainWhys] = useState<Partial<Record<string, string>>>({});

  useEffect(() => {
    if (!dateISO || actFilter === "move" || actFilter === "response") return;
    let cancelled = false;
    void fetchDomainVerdicts(dateISO)
      .then((data) => {
        if (cancelled || data.is_fallback || data.degraded) return;
        const ordered = scrubDomainVerdictJargon(orderDomainVerdicts(data.domain_verdicts ?? []));
        if (isSilentCalmBank(ordered)) return;
        const next: Partial<Record<string, string>> = {};
        for (const row of ordered) {
          const why = (row.why_short || "").trim();
          if (!why) continue;
          next[row.domain as DomainKey] = why;
        }
        if (Object.keys(next).length) setDomainWhys(next);
      })
      .catch(() => {
        /* Reading may still use scene.why — no invented fallback. */
      });
    return () => {
      cancelled = true;
    };
  }, [dateISO, actFilter]);

  useEffect(() => {
    if (!focusSphere || actFilter === "move" || actFilter === "response") return;
    const chapterId = readingSphereChapterId(focusSphere);
    if (!chapterId) return;
    const el = document.querySelector(
      `[data-testid="today-narrative-block-${chapterId}"], [data-testid="today-narrative-${chapterId}"]`,
    );
    if (el && "scrollIntoView" in el) {
      (el as HTMLElement).scrollIntoView({ behavior: "smooth", block: "nearest" });
    }
    // Deep-link from Glance / focus deepen opens opportunity/trap for that sphere
    setExpandedSphereIds((prev) => ({ ...prev, [chapterId]: true }));
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
      domainWhys,
    });
  }, [contract, story, skyCards, morningRitualData, colorGuide, domainWhys]);

  const motion = useProfileMotionInView<HTMLElement>(40);

  const readingScene = (
      <ProductJourneyScene
        step={3}
        title={asScreenFlowSteps ? undefined : (narrative.composition === "scenario_chapters" ? copy.journey.readingTitleStory : copy.journey.readingTitle)}
        lead={asScreenFlowSteps ? null : copy.journey.readingLead}
        motif="today"
        accent="sky"
        chrome={!asScreenFlowSteps}
        className={asScreenFlowSteps ? styles.storyAct : undefined}
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
            const hasNarrative = Boolean(
              (chapter.lead || "").trim() || chapter.paragraphs.some((p) => (p || "").trim()),
            );
            const sphereWhy = isSphereChapter ? (chapter.why || "").trim() || null : null;
            // Progressive (SCENARIO_V3): why first; narrative + dual behind expand when why present.
            const needsProgressive = isSphereChapter && Boolean(sphereWhy) && (hasNarrative || hasDual);
            const dualExpanded = !isSphereChapter || expandedSphereIds[chapter.id] === true;
            const showNarrative = !needsProgressive || dualExpanded;
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
                  lead={isSphereChapter ? null : chapter.lead}
                  paragraphs={
                    isSphereChapter
                      ? []
                      : softWhyInBody
                        ? bodyParagraphs.filter((p) => p !== narrative.softWhy)
                        : chapter.lead
                          ? chapter.paragraphs
                          : bodyParagraphs
                  }
                  accent={chapter.accent ?? "default"}
                  media={showNarrative ? media : null}
                  collapseAfter={isSphereChapter ? undefined : chapter.collapseAfter}
                  surface="plain"
                  testId={`today-narrative-block-${chapter.id}`}
                >
                  {sphereWhy ? (
                    <DsCallout
                      tone="insight"
                      label={calloutLabelForChapterId(chapter.id)}
                      icon="spark"
                      className={styles.narrativeWhy}
                      testId={`today-reading-sphere-why-${chapter.id}`}
                    >
                      <p>{sphereWhy}</p>
                    </DsCallout>
                  ) : null}
                  {/* Sphere lead/body stay at Body size — DsQuote is pull-quote only (vibe). */}
                  {isSphereChapter && showNarrative && chapter.lead ? (
                    <p className={journeyStyles.narrativeBlockLead}>{chapter.lead}</p>
                  ) : null}
                  {isSphereChapter && showNarrative
                    ? chapter.paragraphs.map((para) => (
                        <p key={para.slice(0, 48)} className={journeyStyles.narrativeBlockBody}>
                          {para}
                        </p>
                      ))
                    : null}
                  {softWhyInBody && narrative.softWhy ? (
                    <DsCallout tone="insight" label="attention" icon="flag" testId="today-soft-why">
                      <p>{narrative.softWhy}</p>
                    </DsCallout>
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
                  {isSphereChapter && (hasDual || needsProgressive) && !dualExpanded ? (
                    <DsButton
                      type="button"
                      variant="secondary"
                      className={styles.practiceAction}
                      data-testid={`today-reading-expand-${chapter.id}`}
                      onClick={() =>
                        setExpandedSphereIds((prev) => ({ ...prev, [chapter.id]: true }))
                      }
                    >
                      {needsProgressive
                        ? copy.journey.readingExpandLabel
                        : "Возможность и ловушка"}
                    </DsButton>
                  ) : null}
                  {dualExpanded &&
                  chapter.dual &&
                  (chapter.dual.strengthen.length || chapter.dual.soften.length) ? (
                    <div className={journeyStyles.dualPanels} data-testid={`today-reading-dual-${chapter.id}`}>
                      {chapter.dual.strengthen.length ? (
                        <DsCallout
                          tone={chapter.id === "force" ? "insight" : "help"}
                          label={
                            chapter.id === "force"
                              ? "main"
                              : chapter.id.startsWith("sphere-")
                                ? calloutLabelForChapterId(chapter.id)
                                : "help"
                          }
                          icon={chapter.id === "force" ? "spark" : "sun"}
                          testId={`today-reading-dual-strengthen-${chapter.id}`}
                        >
                          {chapter.dual.strengthen.map((line) => (
                            <p key={line.slice(0, 40)}>{line}</p>
                          ))}
                        </DsCallout>
                      ) : null}
                      {chapter.dual.soften.length ? (
                        <DsCallout
                          tone="avoid"
                          label="attention"
                          icon="flag"
                          testId={`today-reading-dual-soften-${chapter.id}`}
                        >
                          {chapter.dual.soften.map((line) => (
                            <p key={line.slice(0, 40)}>{line}</p>
                          ))}
                        </DsCallout>
                      ) : null}
                    </div>
                  ) : null}
                </ProductNarrativeBlock>
                </TodayScreenBlock>
              </div>
            );
          })}

          {narrative.vibeClosing && !narrative.chapters.some((c) => c.id === "vibe") ? (
            <DsQuote kicker="Сегодня" testId="today-vibe-closing">
              {narrative.vibeClosing}
            </DsQuote>
          ) : null}
        </TodayScreenBlockStack>
        ) : null}

        {contract.depth_layer &&
        Array.isArray(contract.depth_layer.menu) &&
        contract.depth_layer.menu.length > 0 ? (
          <TodayDepthLayerSection
            dateISO={dateISO}
            depthLayer={{
              ...contract.depth_layer,
              menu: pickTodayDepthMenu(contract.depth_layer.menu, contract),
            }}
            preferredTopic={preferredDepthTopic}
            autoPickPreferred={autoPickDepthTopic}
          />
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
        chrome={!asScreenFlowSteps}
        className={asScreenFlowSteps ? styles.storyAct : undefined}
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
          <TodayScreenBlockStack className={styles.moveStack}>
        {colorGuide ? (
          <div className={styles.moveColorAnchor}>
            <TodayDayColorGuideSection guide={colorGuide} />
          </div>
        ) : null}
        {moveIfThen && (moveIfThen.do || moveIfThen.avoid) ? (
          <div className={styles.moveDirections} data-testid="today-zone-move-if-then">
            <p className={styles.moveEyebrow}>{copy.journey.moveIfThenEyebrow}</p>
            {moveIfThen.do ? (
              <DsCallout
                tone="practice"
                label="next_step"
                icon="arrowDown"
                title={moveIfThen.do}
                testId="today-move-do"
              />
            ) : null}
            {moveIfThen.avoid ? (
              <DsCallout
                tone="avoid"
                label="attention"
                icon="flag"
                title={moveIfThen.avoid}
                testId="today-move-avoid"
              />
            ) : null}
          </div>
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
              <DsTextField
                id="day-goal-input-product"
                label={copy.goalPrompt}
                value={goalDraft}
                onChange={onGoalDraftChange}
                maxLength={200}
                placeholder={copy.goalPlaceholder}
              />
              <DsButton type="button" variant="primary" onClick={onSaveGoal}>
                {copy.goalSave}
              </DsButton>
            </div>
          ) : (
            <button
              type="button"
              className={styles.customGoalRow}
              data-testid="today-zone-promise-open"
              onClick={onOpenGoalDraft}
            >
              {dayGoal ? copy.editOwnPromise : copy.writeOwnPromise}
            </button>
          )}
        </TodayScreenBlock>

        {strengthenTools.length > 0 || practiceRec?.text || activeHabit || activeAscetic ? (
          <TodayScreenBlock testId="today-zone-strengthen" className={styles.practiceCluster}>
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
                    <DsButton
                      type="button"
                      variant="secondary"
                      className={styles.practiceAction}
                      data-testid="today-tool-affirmation-done"
                      onClick={onAffirmationDone}
                    >
                      {copy.markAffirmationDone}
                    </DsButton>
                  ) : (
                    <p className={styles.practiceMeta}>{copy.affirmationDone}</p>
                  )}
                </div>
              </div>
            ) : null}

            {supportSlot === "practice" && practiceTool ? (
              <TodayPracticeGiftBlock
                title={practiceTool.title}
                detail={practiceTool.detail}
                duration={practiceTool.duration}
                reason={practiceRec?.kind === "practice" ? practiceRec.reason : null}
                practiceStarted={practiceStarted}
                practiceCompleted={practiceCompleted}
                practiceCompleting={practiceCompleting}
                onPracticeAction={onPracticeAction}
              />
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
                    <DsButton
                      type="button"
                      variant="secondary"
                      className={styles.practiceAction}
                      data-testid="today-tool-affirmation-done"
                      onClick={onAffirmationDone}
                    >
                      {copy.markAffirmationDone}
                    </DsButton>
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
                    <DsButton
                      type="button"
                      variant="secondary"
                      className={styles.practiceAction}
                      data-testid="today-tool-habit-done"
                      disabled={habitMarking || !onHabitMark}
                      onClick={() => onHabitMark?.()}
                    >
                      {copy.markHabitDone}
                    </DsButton>
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
                    <DsButton
                      type="button"
                      variant="secondary"
                      className={styles.practiceAction}
                      data-testid="today-tool-ascetic-done"
                      disabled={asceticMarking || !onAsceticMark}
                      onClick={() => onAsceticMark?.()}
                    >
                      {copy.markAsceticDone}
                    </DsButton>
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

            {supportSlot !== "practice" ? (
              <p className={styles.practiceMeta} style={{ marginTop: "0.75rem" }}>
                <Link href="/practices" data-testid="today-setup-practices-link">
                  {copy.setupPracticesLink} →
                </Link>
              </p>
            ) : null}
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
        {progressRows.length > 0 ? <TodayProgressTracker rows={progressRows} /> : null}
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
        chrome={!asScreenFlowSteps}
        className={asScreenFlowSteps ? styles.storyActResponse : undefined}
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
          <div className={styles.responseStage} data-testid="today-slot-tap-wrap">
            <TodayTapWidget
              contract={contract}
              dateISO={dateISO || ""}
              initialResponse={tapResponse}
              onRecorded={onTapRecorded}
            />
          </div>
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
