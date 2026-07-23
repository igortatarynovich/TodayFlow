"use client";

import Link from "next/link";
import type { TodayPromiseSuggestion } from "@/lib/todayDayDialogue";
import type { TodayContractV1 } from "@/lib/todayContract";
import type { TodayStrengthenTool } from "@/lib/todayCompositionModel";
import type { TodayDayStoryViewModel } from "@/lib/todayDayStoryModel";
import type { CoreProfile } from "@/lib/types";
import { buildTodayCompatibilityHook } from "@/lib/todayCompatibilityHook";
import { buildTodayLiteraryReading } from "@/lib/todayLiteraryReading";
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
  /** Authoritative day_story — one continuous reading, ≤1 tool. */
  singleVoice?: boolean;
  onPickPromise: (text: string) => void;
  onOpenGoalDraft: () => void;
  onGoalDraftChange: (value: string) => void;
  onSaveGoal: () => void;
  onPracticeAction: () => void;
  onAffirmationRead: () => void;
};

function pickPrimaryTool(tools: TodayStrengthenTool[]): TodayStrengthenTool | null {
  if (!tools.length) return null;
  return (
    tools.find((t) => t.id === "practice") ||
    tools.find((t) => t.id === "affirmation") ||
    tools[0] ||
    null
  );
}

export function TodayPersonalizedProductSection({
  story,
  contract,
  strengthenTools,
  promiseSuggestions: _promiseSuggestions,
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
  singleVoice = false,
  onPickPromise: _onPickPromise,
  onOpenGoalDraft,
  onGoalDraftChange,
  onSaveGoal,
  onPracticeAction,
  onAffirmationRead,
}: Props) {
  const compatibility = buildTodayCompatibilityHook(coreProfile);
  const reading = buildTodayLiteraryReading(story, contract);

  const tools = singleVoice ? (pickPrimaryTool(strengthenTools) ? [pickPrimaryTool(strengthenTools)!] : []) : strengthenTools;
  const primaryTool = pickPrimaryTool(tools);

  const themeLine =
    contract.day_story?.theme?.trim() ||
    contract.global_context?.period?.trim() ||
    story.hero.themeHeadline;

  return (
    <section
      className={`${styles.section} ${embeddedInWebDashboard ? styles.sectionWebEmbed : ""} ${singleVoice ? styles.sectionLiterary : ""}`.trim()}
      data-testid="today-zone-personal"
      data-literary={singleVoice ? "1" : undefined}
    >
      <article
        className={singleVoice ? styles.literaryReading : styles.synthesisCard}
        data-testid="today-entity-synthesis"
      >
        <p className={styles.synthesisKicker}>{themeLine || "Сегодня"}</p>
        {reading.opening ? <p className={styles.synthesisText}>{reading.opening}</p> : null}
        {reading.why ? (
          <p className={styles.softWhy} data-testid="today-soft-why">
            <span className={styles.softWhyLabel}>Почему это важно сегодня</span>
            {reading.why}
          </p>
        ) : null}
        {reading.lean ? <p className={styles.readingParagraph}>{reading.lean}</p> : null}
        {reading.ease ? <p className={styles.readingParagraph}>{reading.ease}</p> : null}
        {reading.anchor ? (
          <p className={styles.readingParagraph} data-testid="today-literary-anchor">
            {reading.anchor}
          </p>
        ) : null}
        {reading.close ? (
          <p className={`${styles.readingParagraph} ${styles.readingClose}`.trim()}>{reading.close}</p>
        ) : null}
      </article>

      {(dayGoal || goalDraftOpen) && (
        <article className={styles.productCard} data-testid="today-zone-promise">
          <p className={styles.cardEyebrow}>Если хочется зафиксировать</p>
          {dayGoal && !goalDraftOpen ? (
            <p className={styles.readingParagraph} data-testid="today-promise-active">
              {dayGoal}
            </p>
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
            <button type="button" className={styles.customGoalRow} onClick={onOpenGoalDraft}>
              {dayGoal ? "Изменить своими словами…" : "+ Своими словами…"}
            </button>
          )}
        </article>
      )}
      {!dayGoal && !goalDraftOpen ? (
        <button
          type="button"
          className={styles.customGoalRow}
          data-testid="today-zone-promise-open"
          onClick={onOpenGoalDraft}
        >
          + Если хочется — своими словами
        </button>
      ) : null}

      {primaryTool ? (
        <article className={styles.productCard} data-testid="today-zone-strengthen">
          <p className={styles.cardEyebrow}>На сегодня</p>
          <div className={styles.practiceRow}>
            <span
              className={
                (primaryTool.id === "practice" && practiceCompleted) ||
                (primaryTool.id === "affirmation" && affirmationRead)
                  ? styles.practiceCheckDone
                  : styles.practiceCheck
              }
              aria-hidden
            />
            <div className={styles.practiceBody}>
              <p className={styles.practiceTitle}>{primaryTool.title}</p>
              {primaryTool.duration ? <p className={styles.practiceMeta}>{primaryTool.duration}</p> : null}
              {primaryTool.detail && primaryTool.id !== "practice" && primaryTool.id !== "affirmation" ? (
                <p className={styles.practiceMeta}>{primaryTool.detail}</p>
              ) : null}
              {primaryTool.id === "practice" ? (
                !practiceCompleted ? (
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
                )
              ) : null}
              {primaryTool.id === "affirmation" && !affirmationRead ? (
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
        </article>
      ) : null}

      <nav className={styles.bridges} aria-label="Связанные разделы" data-testid="today-zone-bridges">
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
    </section>
  );
}
