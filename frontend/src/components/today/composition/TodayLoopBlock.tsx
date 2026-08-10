"use client";

import { DsButton } from "@/design-system";
import { TODAY_COMPOSITION_COPY as copy } from "@/components/today/composition/todayCompositionCopy";
import type { TodayLoopModel } from "@/lib/todayLoopModel";
import styles from "@/components/today/composition/TodayLoopBlock.module.css";

export type TodayLoopBlockProps = {
  model: TodayLoopModel;
  onAccept: (text: string) => void;
  onOpenEvening: () => void;
  onPickOutcome?: (outcome: "done" | "partial" | "not_done") => void;
  outcome?: "done" | "partial" | "not_done" | null;
};

const OUTCOMES: { id: "done" | "partial" | "not_done"; label: string }[] = [
  { id: "done", label: "Получилось" },
  { id: "partial", label: "Частично" },
  { id: "not_done", label: "Не получилось" },
];

/**
 * Block 6 — morning accept + evening checkout.
 * Renders assembled model only — no invent.
 */
export function TodayLoopBlock({
  model,
  onAccept,
  onOpenEvening,
  onPickOutcome,
  outcome = null,
}: TodayLoopBlockProps) {
  if (model.mode === "evening") {
    return (
      <div className={styles.root} data-testid="today-loop-block" data-mode="evening">
        <p className={styles.kicker}>{copy.loopEveningKicker}</p>
        <h3 className={styles.title} data-testid="today-loop-title">
          {copy.loopEveningTitle}
        </h3>
        {model.manifesto ? (
          <p className={styles.manifesto} data-testid="today-loop-manifesto">
            {model.manifesto}
          </p>
        ) : null}
        {model.trapCheck ? (
          <section className={styles.trapCheck} data-testid="today-loop-trap-check">
            <p className={styles.label}>{copy.loopTrapCheckLabel}</p>
            <p className={styles.body}>{model.trapCheck}</p>
          </section>
        ) : null}
        {onPickOutcome ? (
          <div className={styles.outcomes} data-testid="today-loop-outcomes">
            {OUTCOMES.map((row) => (
              <button
                key={row.id}
                type="button"
                className={outcome === row.id ? styles.outcomeActive : styles.outcome}
                data-testid={`today-loop-outcome-${row.id}`}
                onClick={() => onPickOutcome(row.id)}
              >
                {row.label}
              </button>
            ))}
          </div>
        ) : null}
        {model.eveningClosure ? (
          <p className={styles.closure} data-testid="today-loop-evening-closure">
            {model.eveningClosure}
          </p>
        ) : (
          <p className={styles.closureMuted}>{copy.loopEveningFallback}</p>
        )}
        <DsButton
          type="button"
          variant="primary"
          className={styles.primaryCta}
          data-testid="today-loop-sleep-cta"
          onClick={onOpenEvening}
        >
          {copy.loopSleepCta}
        </DsButton>
      </div>
    );
  }

  return (
    <div className={styles.root} data-testid="today-loop-block" data-mode="morning">
      <p className={styles.kicker}>{copy.loopMorningKicker}</p>
      {model.manifesto ? (
        <p className={styles.manifesto} data-testid="today-loop-manifesto">
          {model.manifesto}
        </p>
      ) : (
        <p className={styles.closureMuted} data-testid="today-loop-empty">
          {copy.promiseUnsetHint}
        </p>
      )}
      {model.accepted ? (
        <p className={styles.accepted} data-testid="today-loop-accepted">
          {copy.loopAcceptedLabel}
        </p>
      ) : model.manifesto ? (
        <DsButton
          type="button"
          variant="primary"
          className={styles.primaryCta}
          data-testid="today-loop-accept-cta"
          onClick={() => onAccept(model.manifesto!)}
        >
          {copy.loopAcceptCta}
        </DsButton>
      ) : null}
      {!model.accepted && model.alternatives.length > 0 ? (
        <div className={styles.alts} data-testid="today-loop-alternatives">
          <p className={styles.label}>{copy.loopAlternativesLabel}</p>
          {model.alternatives.map((s) => (
            <button
              key={s.id}
              type="button"
              className={styles.altChip}
              data-testid={`today-loop-alt-${s.id}`}
              onClick={() => onAccept(s.text)}
            >
              {s.text}
            </button>
          ))}
        </div>
      ) : null}
      <DsButton
        type="button"
        variant="secondary"
        className={styles.eveningSoft}
        data-testid="today-evening-open"
        onClick={onOpenEvening}
      >
        {copy.eveningCta}
      </DsButton>
    </div>
  );
}
