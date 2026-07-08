"use client";

import { useState } from "react";
import type { DayFocusOutcome } from "@/lib/todayDayContinuity";
import type { TodayPromiseSuggestion } from "@/lib/todayDayDialogue";
import {
  TODAY_EVENING_HIGHLIGHTS,
  promiseOutcomeLabelRu,
} from "@/lib/todayDayDialogue";

const OUTCOMES: DayFocusOutcome[] = ["done", "partial", "not_done"];

type Props = {
  userPromise: string | null;
  themeShort?: string | null;
  promiseSuggestions?: TodayPromiseSuggestion[];
  onPickPromise?: (text: string) => void;
  saving?: boolean;
  onSubmit: (outcome: DayFocusOutcome, highlightId: string | null, note: string) => void;
  onBack?: () => void;
};

/** Evening story closure — reflection, not a checklist. */
export function TodayDayContinuityEveningClose({
  userPromise,
  themeShort,
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

  return (
    <section
      className="today-experience-stage-enter"
      data-testid="today-day-continuity-evening"
      style={{
        flex: 1,
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        gap: "0.85rem",
        padding: "0.25rem 0",
      }}
    >
      <div>
        <p className="todayflow-eyebrow" style={{ margin: 0 }}>
          Закрытие дня
        </p>
        <h2 className="orbit-heading-2" style={{ margin: "0.35rem 0 0", lineHeight: 1.35, color: "#1f1a16" }}>
          Сегодня подходит к концу
        </h2>
        {themeShort ? (
          <p className="orbit-body-sm" style={{ margin: "0.55rem 0 0", lineHeight: 1.55, color: "#5a4f45" }}>
            Главная тема: {themeShort}
          </p>
        ) : null}
        {userPromise ? (
          <p className="orbit-body-sm" style={{ margin: "0.55rem 0 0", lineHeight: 1.55, color: "#3d3228" }}>
            Сегодня ты обещал себе: {userPromise}. Удалось ли сохранить этот ритм?
          </p>
        ) : skippedPromise ? (
          <p className="orbit-body-sm" style={{ margin: "0.55rem 0 0", lineHeight: 1.55, color: "#3d3228" }}>
            Как прошёл день — в духе темы «{themeShort ?? "сегодня"}»?
          </p>
        ) : (
          <p className="orbit-body-sm" style={{ margin: "0.55rem 0 0", lineHeight: 1.55, color: "#3d3228" }}>
            Если хочешь — выбери одно маленькое обещание, которым можно завершить день. Это необязательно.
          </p>
        )}
      </div>

      {showPromisePicker ? (
        <div data-testid="evening-promise-picker">
          <div style={{ display: "flex", flexDirection: "column", gap: "0.45rem" }}>
            {promiseSuggestions.map((s) => (
              <button
                key={s.id}
                type="button"
                data-testid={`evening-promise-${s.id}`}
                className="orbit-button orbit-button-secondary"
                style={{ width: "100%", justifyContent: "center", textAlign: "center" }}
                disabled={saving}
                onClick={() => onPickPromise?.(s.text)}
              >
                {s.text}
              </button>
            ))}
          </div>
          <button
            type="button"
            className="orbit-button orbit-button-ghost"
            style={{ width: "100%", marginTop: "0.45rem" }}
            disabled={saving}
            onClick={() => setSkippedPromise(true)}
            data-testid="evening-promise-skip"
          >
            Продолжить без обещания
          </button>
        </div>
      ) : (
        <>
          <div role="group" aria-label="Итог дня" style={{ display: "flex", flexDirection: "column", gap: "0.45rem" }}>
            {OUTCOMES.map((value) => {
              const selected = outcome === value;
              return (
                <button
                  key={value}
                  type="button"
                  data-testid={`day-continuity-outcome-${value}`}
                  className={selected ? "orbit-button orbit-button-primary" : "orbit-button orbit-button-secondary"}
                  style={{ width: "100%", justifyContent: "center" }}
                  disabled={saving}
                  onClick={() => setOutcome(value)}
                >
                  {promiseOutcomeLabelRu(value)}
                </button>
              );
            })}
          </div>

          <div>
            <p className="orbit-body-sm" style={{ margin: "0 0 0.45rem", color: "#5a4f45" }}>
              Какое событие запомнилось сильнее всего?
            </p>
            <div
              style={{ display: "flex", flexWrap: "wrap", gap: "0.45rem" }}
              role="group"
              aria-label="Самое важное сегодня"
            >
              {TODAY_EVENING_HIGHLIGHTS.map((h) => (
                <button
                  key={h.id}
                  type="button"
                  data-testid={`evening-highlight-${h.id}`}
                  className={
                    highlightId === h.id ? "orbit-button orbit-button-primary" : "orbit-button orbit-button-secondary"
                  }
                  onClick={() => setHighlightId((prev) => (prev === h.id ? null : h.id))}
                  disabled={saving}
                >
                  {h.label}
                </button>
              ))}
            </div>
          </div>

          <button
            type="button"
            className="orbit-button orbit-button-primary"
            data-testid="day-continuity-submit"
            style={{ width: "100%" }}
            disabled={saving || outcome == null}
            onClick={() => {
              if (outcome == null) return;
              onSubmit(outcome, highlightId, "");
            }}
          >
            {saving ? "Сохраняем…" : "Закрыть день"}
          </button>
        </>
      )}

      {onBack ? (
        <button
          type="button"
          className="orbit-button orbit-button-ghost"
          style={{ width: "100%" }}
          disabled={saving}
          onClick={onBack}
        >
          Назад к дню
        </button>
      ) : null}
    </section>
  );
}
