"use client";

import { useState } from "react";
import type { DayFocusOutcome } from "@/lib/todayDayContinuity";
import type { TodayPromiseSuggestion } from "@/lib/todayDayDialogue";
import {
  TODAY_EVENING_HIGHLIGHTS,
  promiseOutcomeLabelRu,
} from "@/lib/todayDayDialogue";
import styles from "@/components/today/composition/TodayEveningProductClose.module.css";

const OUTCOMES: DayFocusOutcome[] = ["done", "partial", "not_done"];

const OUTCOME_LABELS: Record<DayFocusOutcome, string> = {
  done: "Да ✓",
  partial: "Частично",
  not_done: "Пока нет",
};

type Props = {
  userName?: string | null;
  userPromise: string | null;
  themeShort?: string | null;
  practiceCompleted: boolean;
  practiceStarted: boolean;
  affirmationRead: boolean;
  strengthenToolCount: number;
  activeHabit?: { id: number; name: string } | null;
  activeAscetic?: { id: number; title: string } | null;
  habitMarked?: boolean;
  asceticMarked?: boolean;
  /** Optional one-tap when user answers «Да» to evening habit/ascetic question. */
  onHabitEveningDone?: () => void;
  onAsceticEveningDone?: () => void;
  promiseSuggestions?: TodayPromiseSuggestion[];
  onPickPromise?: (text: string) => void;
  saving?: boolean;
  onSubmit: (outcome: DayFocusOutcome, highlightId: string | null, note: string) => void;
  onBack?: () => void;
};

function formatName(name: string | null | undefined): string | null {
  const trimmed = name?.trim();
  if (!trimmed) return null;
  return trimmed.split(/\s+/)[0] ?? trimmed;
}

export function TodayEveningProductClose({
  userName,
  userPromise,
  themeShort,
  practiceCompleted,
  practiceStarted,
  affirmationRead: _affirmationRead,
  strengthenToolCount,
  activeHabit = null,
  activeAscetic = null,
  habitMarked = false,
  asceticMarked = false,
  onHabitEveningDone,
  onAsceticEveningDone,
  promiseSuggestions = [],
  onPickPromise,
  saving = false,
  onSubmit,
  onBack,
}: Props) {
  const [outcome, setOutcome] = useState<DayFocusOutcome | null>(null);
  const [highlightId, setHighlightId] = useState<string | null>(null);
  const [skippedPromise, setSkippedPromise] = useState(false);
  const [habitOutcome, setHabitOutcome] = useState<DayFocusOutcome | null>(
    habitMarked ? "done" : null,
  );
  const [asceticOutcome, setAsceticOutcome] = useState<DayFocusOutcome | null>(
    asceticMarked ? "done" : null,
  );

  const showPromisePicker = !userPromise && !skippedPromise && promiseSuggestions.length > 0;
  const name = formatName(userName);
  const greetingName = name ? `${name}, день подходит к завершению.` : "День подходит к завершению.";

  const completedPractices =
    (practiceCompleted ? 1 : 0) + (practiceStarted && !practiceCompleted ? 0 : 0);
  const practiceSummary =
    strengthenToolCount > 0 ? `${Math.max(completedPractices, practiceCompleted ? 1 : 0)} из ${strengthenToolCount}` : "—";
  const intentionSummary = userPromise ? "Выполнено" : "Не выбрано";
  const reflectionSummary = highlightId ? "1" : "0";

  const showHabitQuestion = Boolean(activeHabit) && !habitMarked;
  const showAsceticQuestion = Boolean(activeAscetic) && !asceticMarked;

  return (
    <div className={styles.root} data-testid="today-composition-evening">
      <section data-testid="today-day-continuity-evening">
        <header className={styles.eveningHeader}>
          <h1 className={styles.eveningHeaderTitle}>{greetingName}</h1>
          <p className={styles.eveningHeaderMeta}>
            {themeShort ? `Тема: ${themeShort}` : "Тема дня"}
            {userPromise ? ` · Намерение: ${userPromise}` : ""}
          </p>
        </header>

        {showPromisePicker ? (
          <div className={styles.promisePicker} data-testid="evening-promise-picker">
            {promiseSuggestions.map((suggestion) => (
              <button
                key={suggestion.id}
                type="button"
                data-testid={`evening-promise-${suggestion.id}`}
                className="orbit-button orbit-button-secondary"
                disabled={saving}
                onClick={() => onPickPromise?.(suggestion.text)}
              >
                {suggestion.text}
              </button>
            ))}
            <button
              type="button"
              className="orbit-button orbit-button-ghost"
              disabled={saving}
              onClick={() => setSkippedPromise(true)}
              data-testid="evening-promise-skip"
            >
              Продолжить без обещания
            </button>
          </div>
        ) : (
          <>
            <article className={styles.questionCard}>
              <h2 className={styles.questionTitle}>Намерение выполнено?</h2>
              <div className={styles.outcomeRow} role="group" aria-label="Итог дня">
                {OUTCOMES.map((value) => (
                  <button
                    key={value}
                    type="button"
                    data-testid={`day-continuity-outcome-${value}`}
                    className={outcome === value ? styles.outcomePillSelected : styles.outcomePill}
                    disabled={saving}
                    onClick={() => setOutcome(value)}
                  >
                    {OUTCOME_LABELS[value] ?? promiseOutcomeLabelRu(value)}
                  </button>
                ))}
              </div>
            </article>

            {showHabitQuestion && activeHabit ? (
              <article className={styles.questionCard} data-testid="evening-habit-question">
                <h2 className={styles.questionTitle}>
                  Получилось сегодня с привычкой «{activeHabit.name}»?
                </h2>
                <div className={styles.outcomeRow} role="group" aria-label="Привычка сегодня">
                  {OUTCOMES.map((value) => (
                    <button
                      key={value}
                      type="button"
                      data-testid={`evening-habit-outcome-${value}`}
                      className={habitOutcome === value ? styles.outcomePillSelected : styles.outcomePill}
                      disabled={saving}
                      onClick={() => {
                        setHabitOutcome(value);
                        if (value === "done") onHabitEveningDone?.();
                      }}
                    >
                      {OUTCOME_LABELS[value] ?? promiseOutcomeLabelRu(value)}
                    </button>
                  ))}
                </div>
              </article>
            ) : null}

            {showAsceticQuestion && activeAscetic ? (
              <article className={styles.questionCard} data-testid="evening-ascetic-question">
                <h2 className={styles.questionTitle}>
                  Получилось сегодня с аскезой «{activeAscetic.title}»?
                </h2>
                <div className={styles.outcomeRow} role="group" aria-label="Аскеза сегодня">
                  {OUTCOMES.map((value) => (
                    <button
                      key={value}
                      type="button"
                      data-testid={`evening-ascetic-outcome-${value}`}
                      className={
                        asceticOutcome === value ? styles.outcomePillSelected : styles.outcomePill
                      }
                      disabled={saving}
                      onClick={() => {
                        setAsceticOutcome(value);
                        if (value === "done") onAsceticEveningDone?.();
                      }}
                    >
                      {OUTCOME_LABELS[value] ?? promiseOutcomeLabelRu(value)}
                    </button>
                  ))}
                </div>
              </article>
            ) : null}

            <section className={styles.highlightsSection}>
              <p className={styles.highlightsLabel}>Что запомнилось?</p>
              <div className={styles.highlightRow} role="group" aria-label="Самое важное сегодня">
                {TODAY_EVENING_HIGHLIGHTS.map((highlight) => (
                  <button
                    key={highlight.id}
                    type="button"
                    data-testid={`evening-highlight-${highlight.id}`}
                    className={highlightId === highlight.id ? styles.highlightChipSelected : styles.highlightChip}
                    disabled={saving}
                    onClick={() => setHighlightId((prev) => (prev === highlight.id ? null : highlight.id))}
                  >
                    {highlight.label}
                  </button>
                ))}
              </div>
            </section>

            <article className={styles.summaryCard}>
              <div className={styles.summaryRow}>
                <p className={styles.summaryLabel}>Практики</p>
                <p className={styles.summaryValue}>
                  {practiceSummary}
                  {practiceCompleted ? <span className={styles.summaryCheck}>✓</span> : null}
                </p>
              </div>
              <div className={styles.summaryDivider} />
              <div className={styles.summaryRow}>
                <p className={styles.summaryLabel}>Намерение</p>
                <p className={styles.summaryValue}>
                  {intentionSummary}
                  {userPromise && outcome === "done" ? <span className={styles.summaryCheck}>✓</span> : null}
                </p>
              </div>
              {activeHabit ? (
                <>
                  <div className={styles.summaryDivider} />
                  <div className={styles.summaryRow}>
                    <p className={styles.summaryLabel}>Привычка</p>
                    <p className={styles.summaryValue}>
                      {habitMarked || habitOutcome === "done" ? "Отмечено" : "—"}
                      {habitMarked || habitOutcome === "done" ? (
                        <span className={styles.summaryCheck}>✓</span>
                      ) : null}
                    </p>
                  </div>
                </>
              ) : null}
              {activeAscetic ? (
                <>
                  <div className={styles.summaryDivider} />
                  <div className={styles.summaryRow}>
                    <p className={styles.summaryLabel}>Аскеза</p>
                    <p className={styles.summaryValue}>
                      {asceticMarked || asceticOutcome === "done" ? "Отмечено" : "—"}
                      {asceticMarked || asceticOutcome === "done" ? (
                        <span className={styles.summaryCheck}>✓</span>
                      ) : null}
                    </p>
                  </div>
                </>
              ) : null}
              <div className={styles.summaryDivider} />
              <div className={styles.summaryRow}>
                <p className={styles.summaryLabel}>Рефлексий</p>
                <p className={styles.summaryValue}>
                  {reflectionSummary}
                  {highlightId ? <span className={styles.summaryCheck}>✓</span> : null}
                </p>
              </div>
            </article>

            <div className={styles.actions}>
              <button
                type="button"
                className={styles.submitButton}
                data-testid="day-continuity-submit"
                disabled={saving || outcome == null}
                onClick={() => {
                  if (outcome == null) return;
                  onSubmit(outcome, highlightId, "");
                }}
              >
                {saving ? "Сохраняем…" : "Завершить день"}
              </button>
              <p className={styles.footerHint}>Завтра твой день начнётся чуть точнее.</p>
            </div>
          </>
        )}

        {onBack ? (
          <button
            type="button"
            className={`orbit-button orbit-button-ghost ${styles.backButton}`}
            disabled={saving}
            onClick={onBack}
          >
            Назад к дню
          </button>
        ) : null}
      </section>
    </div>
  );
}
