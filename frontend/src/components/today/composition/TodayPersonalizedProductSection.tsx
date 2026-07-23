"use client";

import Link from "next/link";
import { useMemo } from "react";
import {
  profileMotionStaggerDelay,
  profileMotionStyles,
  useProfileMotionInView,
} from "@/components/foundation/ProfileMotion";
import { ProfileAtmosphere } from "@/components/profile/v2/ProfileAtmosphere";
import type { MorningRitualData } from "@/components/today/todayPageUtils";
import type { TodayPromiseSuggestion } from "@/lib/todayDayDialogue";
import type { TodayContractV1 } from "@/lib/todayContract";
import type { TodayStrengthenTool } from "@/lib/todayCompositionModel";
import type { TodayDayColorGuide } from "@/lib/todayDayColorGuide";
import type { TodaySkyCard } from "@/lib/todayDaySpine";
import { buildTodayDayNarrative } from "@/lib/todayDayNarrative";
import type { TodayDayStoryViewModel } from "@/lib/todayDayStoryModel";
import type { CoreProfile } from "@/lib/types";
import { buildTodayCompatibilityHook } from "@/lib/todayCompatibilityHook";
import { TODAY_COMPOSITION_COPY as copy } from "@/components/today/composition/todayCompositionCopy";
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
  goalDraftOpen: boolean;
  goalDraft: string;
  coreProfile?: CoreProfile | null;
  tarotDeepenHref?: string | null;
  embeddedInWebDashboard?: boolean;
  skyCards?: TodaySkyCard[];
  colorGuide?: TodayDayColorGuide | null;
  morningRitualData?: MorningRitualData | null;
  onPickPromise: (text: string) => void;
  onOpenGoalDraft: () => void;
  onGoalDraftChange: (value: string) => void;
  onSaveGoal: () => void;
  onPracticeAction: () => void;
  onAffirmationRead: () => void;
};

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
  goalDraftOpen,
  goalDraft,
  coreProfile,
  tarotDeepenHref,
  embeddedInWebDashboard = false,
  skyCards = [],
  colorGuide = null,
  morningRitualData = null,
  onPickPromise,
  onOpenGoalDraft,
  onGoalDraftChange,
  onSaveGoal,
  onPracticeAction,
  onAffirmationRead,
}: Props) {
  const compatibility = buildTodayCompatibilityHook(coreProfile);
  const practiceRec = contract.day_story?.practice_recommendation;

  const completedCount = (practiceCompleted ? 1 : 0) + (affirmationRead ? 1 : 0);
  const totalTools = strengthenTools.length;

  const practiceTool = strengthenTools.find((tool) => tool.id === "practice");
  const affirmationTool = strengthenTools.find((tool) => tool.id === "affirmation");
  const otherTools = strengthenTools.filter((tool) => tool.id !== "practice" && tool.id !== "affirmation");

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

  return (
    <section
      ref={motion.ref}
      className={`${styles.section} ${embeddedInWebDashboard ? styles.sectionWebEmbed : ""} ${motion.className}`.trim()}
      style={motion.style}
      data-testid="today-zone-personal"
    >
      <div className={styles.journeyScene} data-testid="today-zone-reading">
        <ProfileAtmosphere motif="today" />
        <header className={styles.journeySceneHeader}>
          <p className={styles.journeyStepIndex}>
            <span className={styles.journeyStepBadge}>3</span>
            <span>{copy.journey.readingTitle}</span>
          </p>
          <p className={styles.journeySceneLead}>{copy.journey.readingLead}</p>
        </header>

        <article
          className={`${styles.narrativeScroll} ${profileMotionStyles.staggerItem}`}
          style={profileMotionStaggerDelay(0, 60)}
          data-testid="today-entity-synthesis"
        >
          {narrative.theme ? (
            <p className={styles.synthesisKicker} data-testid="today-narrative-theme">
              {narrative.theme}
            </p>
          ) : null}

          {narrative.chapters.map((chapter, chapterIndex) => (
            <section
              key={chapter.id}
              className={styles.narrativeChapter}
              data-testid={`today-narrative-${chapter.id}`}
              style={profileMotionStaggerDelay(chapterIndex + 1, 70)}
            >
              <p className={styles.narrativeKicker}>{chapter.kicker}</p>
              {chapter.paragraphs.map((paragraph) => {
                const isSoftWhy =
                  chapter.id === "opening" && Boolean(narrative.softWhy) && paragraph === narrative.softWhy;
                return (
                  <p
                    key={`${chapter.id}-${paragraph.slice(0, 48)}`}
                    className={isSoftWhy ? `${styles.narrativeParagraph} ${styles.narrativeWhy}` : styles.narrativeParagraph}
                    data-testid={isSoftWhy ? "today-soft-why" : undefined}
                  >
                    {isSoftWhy ? (
                      <>
                        <span className={styles.softWhyLabel}>Почему это важно сегодня</span>
                        {paragraph}
                      </>
                    ) : (
                      paragraph
                    )}
                  </p>
                );
              })}
            </section>
          ))}
        </article>
      </div>

      <div className={styles.journeyScene} data-testid="today-zone-move">
        <ProfileAtmosphere motif="effort" />
        <header className={styles.journeySceneHeader}>
          <p className={styles.journeyStepIndex}>
            <span className={styles.journeyStepBadge}>4</span>
            <span>{copy.journey.moveTitle}</span>
          </p>
          <p className={styles.journeySceneLead}>{copy.journey.moveLead}</p>
        </header>

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

        {strengthenTools.length > 0 || practiceRec?.text ? (
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
                <span className={styles.practiceCheck} aria-hidden />
                <div className={styles.practiceBody}>
                  <p className={styles.practiceTitle}>{practiceRec.text}</p>
                  {practiceRec.reason ? <p className={styles.practiceMeta}>{practiceRec.reason}</p> : null}
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
                      onClick={onAffirmationRead}
                    >
                      {copy.readAffirmation}
                    </button>
                  ) : null}
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
          </article>
        ) : null}
      </div>

      <div className={`${styles.journeyScene} ${styles.bridgeScene}`} data-testid="today-zone-bridges-wrap">
        <ProfileAtmosphere motif="bridge" />
        <header className={styles.journeySceneHeader}>
          <p className={styles.journeyStepIndex}>
            <span className={styles.journeyStepBadge}>5</span>
            <span>{copy.journey.bridgeTitle}</span>
          </p>
          <p className={styles.journeySceneLead}>{copy.journey.bridgeLead}</p>
        </header>
        <nav className={styles.bridges} aria-label="Связанные разделы" data-testid="today-zone-bridges">
          <Link href="/profile" className={styles.bridgeCta}>
            Открыть карту личности
            <span aria-hidden> →</span>
          </Link>
          <Link href={compatibility.href} className={styles.bridgeLink}>
            → {compatibility.hasSavedPerson ? "Совместимость с партнёром" : "Проверить совместимость"}
          </Link>
          {tarotDeepenHref ? (
            <Link href={tarotDeepenHref} className={styles.bridgeLink} data-testid="today-tarot-deepen">
              → Исследовать тему: Таро
            </Link>
          ) : (
            <Link href="/tarot" className={styles.bridgeLink}>
              → Исследовать тему: Таро
            </Link>
          )}
        </nav>
      </div>
    </section>
  );
}
