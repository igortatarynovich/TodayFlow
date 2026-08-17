"use client";

import { useState } from "react";
import {
  DsActionCard,
  DsButton,
  DsChip,
  DsChipCluster,
  DsContentCard,
  DsHeroBlock,
  DsListPanel,
  DsListRow,
  DsStarDivider,
} from "@/design-system";
import type { DayFocusOutcome } from "@/lib/todayDayContinuity";
import type { TodayPromiseSuggestion } from "@/lib/todayDayDialogue";
import {
  TODAY_EVENING_HIGHLIGHTS,
  promiseOutcomeLabelRu,
} from "@/lib/todayDayDialogue";
import layout from "@/design-system/compositions/dsCompositions.module.css";

const OUTCOMES: DayFocusOutcome[] = ["done", "partial", "not_done"];

const OUTCOME_LABELS: Record<DayFocusOutcome, string> = {
  done: "Получилось",
  partial: "Частично",
  not_done: "Не получилось",
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

function OutcomeChips({
  value,
  onChange,
  disabled,
  testIdPrefix,
  ariaLabel,
}: {
  value: DayFocusOutcome | null;
  onChange: (v: DayFocusOutcome) => void;
  disabled?: boolean;
  testIdPrefix: string;
  ariaLabel: string;
}) {
  return (
    <DsChipCluster testId={ariaLabel}>
      {OUTCOMES.map((id) => (
        <DsChip
          key={id}
          selected={value === id}
          disabled={disabled}
          testId={`${testIdPrefix}-${id}`}
          onClick={() => onChange(id)}
        >
          {OUTCOME_LABELS[id] ?? promiseOutcomeLabelRu(id)}
        </DsChip>
      ))}
    </DsChipCluster>
  );
}

/** Evening close — Form Kit hero / content / chips / action. */
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
    strengthenToolCount > 0
      ? `${Math.max(completedPractices, practiceCompleted ? 1 : 0)} из ${strengthenToolCount}`
      : "—";
  const intentionSummary = userPromise ? "Выполнено" : "Не выбрано";
  const reflectionSummary = highlightId ? "1" : "0";

  const showHabitQuestion = Boolean(activeHabit) && !habitMarked;
  const showAsceticQuestion = Boolean(activeAscetic) && !asceticMarked;

  return (
    <div className={layout.stack} data-testid="today-composition-evening">
      <section className={layout.stack} data-testid="today-day-continuity-evening">
        <DsHeroBlock
          tone="solid"
          title={greetingName}
          body={
            [
              themeShort ? `Тема: ${themeShort}` : "Тема дня",
              userPromise ? `Намерение: ${userPromise}` : null,
            ]
              .filter(Boolean)
              .join(" · ")
          }
        />

        {showPromisePicker ? (
          <DsListPanel tone="glass" testId="evening-promise-picker" title="Обещание">
            {promiseSuggestions.map((suggestion) => (
              <DsListRow
                key={suggestion.id}
                title={suggestion.text}
                testId={`evening-promise-${suggestion.id}`}
                onClick={() => onPickPromise?.(suggestion.text)}
              />
            ))}
            <DsButton
              type="button"
              variant="ghost"
              disabled={saving}
              onClick={() => setSkippedPromise(true)}
              data-testid="evening-promise-skip"
            >
              Продолжить без обещания
            </DsButton>
          </DsListPanel>
        ) : (
          <>
            <DsContentCard
              tone="glass"
              eyebrow="Главный фокус"
              title="Как прошёл сегодняшний главный фокус?"
              chips={
                <OutcomeChips
                  value={outcome}
                  onChange={setOutcome}
                  disabled={saving}
                  testIdPrefix="day-continuity-outcome"
                  ariaLabel="Итог дня"
                />
              }
            />

            {showHabitQuestion && activeHabit ? (
              <DsContentCard
                tone="subtle"
                testId="evening-habit-question"
                title={`Получилось сегодня с привычкой «${activeHabit.name}»?`}
                chips={
                  <OutcomeChips
                    value={habitOutcome}
                    onChange={(value) => {
                      setHabitOutcome(value);
                      if (value === "done") onHabitEveningDone?.();
                    }}
                    disabled={saving}
                    testIdPrefix="evening-habit-outcome"
                    ariaLabel="Привычка сегодня"
                  />
                }
              />
            ) : null}

            {showAsceticQuestion && activeAscetic ? (
              <DsContentCard
                tone="subtle"
                testId="evening-ascetic-question"
                title={`Получилось сегодня с аскезой «${activeAscetic.title}»?`}
                chips={
                  <OutcomeChips
                    value={asceticOutcome}
                    onChange={(value) => {
                      setAsceticOutcome(value);
                      if (value === "done") onAsceticEveningDone?.();
                    }}
                    disabled={saving}
                    testIdPrefix="evening-ascetic-outcome"
                    ariaLabel="Аскеза сегодня"
                  />
                }
              />
            ) : null}

            <DsContentCard
              tone="glass"
              eyebrow="Что запомнилось?"
              chips={
                <DsChipCluster>
                  {TODAY_EVENING_HIGHLIGHTS.map((highlight) => (
                    <DsChip
                      key={highlight.id}
                      selected={highlightId === highlight.id}
                      disabled={saving}
                      testId={`evening-highlight-${highlight.id}`}
                      onClick={() =>
                        setHighlightId((prev) => (prev === highlight.id ? null : highlight.id))
                      }
                    >
                      {highlight.label}
                    </DsChip>
                  ))}
                </DsChipCluster>
              }
            />

            <DsListPanel tone="solid" title="Итог">
              <DsListRow
                title="Практики"
                subtitle={`${practiceSummary}${practiceCompleted ? " ✓" : ""}`}
              />
              <DsListRow
                title="Намерение"
                subtitle={`${intentionSummary}${userPromise && outcome === "done" ? " ✓" : ""}`}
              />
              {activeHabit ? (
                <DsListRow
                  title="Привычка"
                  subtitle={habitMarked || habitOutcome === "done" ? "Отмечено ✓" : "—"}
                />
              ) : null}
              {activeAscetic ? (
                <DsListRow
                  title="Аскеза"
                  subtitle={asceticMarked || asceticOutcome === "done" ? "Отмечено ✓" : "—"}
                />
              ) : null}
              <DsListRow
                title="Рефлексий"
                subtitle={`${reflectionSummary}${highlightId ? " ✓" : ""}`}
              />
            </DsListPanel>

            <DsStarDivider />
            <DsActionCard
              tone="accent"
              title={saving ? "Сохраняем…" : "Сохранить день"}
              body="Завтра утром TodayFlow начнёт с того, что было сегодня."
              action={
                <DsButton
                  type="button"
                  variant="primary"
                  data-testid="day-continuity-submit"
                  disabled={saving || outcome == null}
                  onClick={() => {
                    if (outcome == null) return;
                    onSubmit(outcome, highlightId, "");
                  }}
                >
                  {saving ? "Сохраняем…" : "Сохранить день"}
                </DsButton>
              }
            />
          </>
        )}

        {onBack ? (
          <DsButton type="button" variant="ghost" disabled={saving} onClick={onBack}>
            Назад к дню
          </DsButton>
        ) : null}
      </section>
    </div>
  );
}
