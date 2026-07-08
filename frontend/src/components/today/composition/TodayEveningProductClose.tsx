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
  affirmationRead,
  strengthenToolCount,
  promiseSuggestions = [],
  onPickPromise,
  saving = false,
  onSubmit,
  onBack,
}: Props) {
  const [outcome, setOutcome] = useState<DayFocusOutcome | null>(null);
  const [highlightId, setHighlightId] = useState<string | null>(null);
  const [skippedPromise, setSkippedPromise] = useState(false);

  const showPromisePicker = !userPromise && !skippedPromise && promiseSuggestions.length > 0;
  const name = formatName(userName);
  const greetingName = name ? `${name}, день подходит к завершению.` : "День подходит к завершению.";

  const completedPractices =
    (practiceCompleted ? 1 : 0) + (practiceStarted && !practiceCompleted ? 0 : 0);
  const practiceSummary =
    strengthenToolCount > 0 ? `${Math.max(completedPractices, practiceCompleted ? 1 : 0)} из ${strengthenToolCount}` : "—";
  const intentionSummary = userPromise ? "Выполнено" : "Не выбрано";
  const reflectionSummary = highlightId ? "1" : "0";

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
