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
  onPickPromise: _onPickPromise,
  onOpenGoalDraft,
  onGoalDraftChange,
  onSaveGoal,
  onPracticeAction,
  onAffirmationRead,
}: Props) {
  const compatibility = buildTodayCompatibilityHook(coreProfile);
  const reading = buildTodayLiteraryReading(story, contract);

  const synthesisTags = [
    story.tarotImpact ? { id: "tarot", label: story.tarotImpact.title } : null,
    story.skyCards[0] ? { id: story.skyCards[0].id, label: story.skyCards[0].title } : null,
    story.numberImpact ? { id: "number", label: story.numberImpact.title } : null,
  ].filter(Boolean) as Array<{ id: string; label: string }>;

  const completedCount = (practiceCompleted ? 1 : 0) + (affirmationRead ? 1 : 0);
  const totalTools = strengthenTools.length;

  const practiceTool = strengthenTools.find((tool) => tool.id === "practice");
  const affirmationTool = strengthenTools.find((tool) => tool.id === "affirmation");
  const otherTools = strengthenTools.filter((tool) => tool.id !== "practice" && tool.id !== "affirmation");

  const themeLine =
    contract.day_story?.theme?.trim() ||
    contract.global_context?.period?.trim() ||
    story.hero.themeHeadline;

  return (
    <section
      className={`${styles.section} ${embeddedInWebDashboard ? styles.sectionWebEmbed : ""}`.trim()}
      data-testid="today-zone-personal"
    >
      <article className={styles.synthesisCard} data-testid="today-entity-synthesis">
        <div>
          <p className={styles.synthesisKicker}>{themeLine || "Сегодня"}</p>
          {reading.opening ? <p className={styles.synthesisText}>{reading.opening}</p> : null}
        </div>
        {synthesisTags.length > 0 ? (
          <div className={styles.synthesisTags}>
            {synthesisTags.map((tag) => (
              <span key={tag.id} className={styles.synthesisTag}>
                {tag.label}
              </span>
            ))}
          </div>
        ) : null}
      </article>

      {(reading.lean || reading.ease || reading.close) && (
        <article className={styles.productCard} data-testid="today-zone-focus-card">
          {reading.lean ? <p className={styles.readingParagraph}>{reading.lean}</p> : null}
          {reading.ease ? <p className={styles.readingParagraph}>{reading.ease}</p> : null}
          {reading.close ? (
            <p className={`${styles.readingParagraph} ${styles.readingClose}`.trim()}>{reading.close}</p>
          ) : null}
        </article>
      )}

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

      {strengthenTools.length > 0 ? (
        <article className={styles.productCard} data-testid="today-zone-strengthen">
          <div className={styles.practicesHeader}>
            <p className={styles.cardEyebrow}>На сегодня</p>
            <p className={styles.practicesProgress}>
              {completedCount} из {totalTools}
            </p>
          </div>

          {practiceTool ? (
            <>
              <div className={styles.practiceRow}>
                <span
                  className={practiceCompleted ? styles.practiceCheckDone : styles.practiceCheck}
                  aria-hidden
                />
                <div className={styles.practiceBody}>
                  <p className={styles.practiceTitle}>{practiceTool.title}</p>
                  {practiceTool.duration ? <p className={styles.practiceMeta}>{practiceTool.duration}</p> : null}
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
            </>
          ) : null}

          {affirmationTool ? (
            <div className={styles.practiceRow}>
              <span className={affirmationRead ? styles.practiceCheckDone : styles.practiceCheck} aria-hidden />
              <div className={styles.practiceBody}>
                <p className={styles.practiceTitle}>{affirmationTool.title}</p>
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
                {tool.href ? (
                  <Link href={tool.href} className={styles.practiceAction}>
                    Открыть
                  </Link>
                ) : null}
              </div>
            </div>
          ))}
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
