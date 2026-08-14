"use client";

import { useEffect, type ReactNode } from "react";
import Link from "next/link";
import { ScreenFlow, ScreenFlowStep, TODAY_SCREEN_FLOW_AXIS } from "@/design-system/primitives/ScreenFlow";
import { DsCaption, DsEyebrow, DsHeadline } from "@/design-system";
import { joinClass } from "@/design-system/utils/joinClass";
import { TODAY_COMPOSITION_COPY as copy } from "@/components/today/composition/todayCompositionCopy";
import sfStyles from "@/design-system/primitives/ScreenFlow/ScreenFlow.module.css";
import {
  StoryNextAnchor,
  TodayCloseFrame,
  TodayPracticeFrame,
} from "@/components/today/composition/TodayStoryDeckFrames";
import type { ScreenFlowChangeReason } from "@/design-system/primitives/ScreenFlow";
import type { TodayContractV1 } from "@/lib/todayContract";
import type { TapResponseCode } from "@/lib/todayTapWidget";
import { fetchDayFacts } from "@/lib/todayDayFacts";

/**
 * Today presentation v3.4.2 — six product blocks; Block 1 = dashboard + orientation.
 * День (dashboard / sheet) → Ориентир → Ритуалы → Инструкция → Цвет → Задания → Петля
 * Canon: docs/today/TODAY_SCREEN_SCENARIO_V3.md
 */

export type TodaySixBlockIndices = {
  day: number;
  orientation: number;
  rituals: number;
  instruction: number;
  color: number;
  tasks: number;
  loop: number;
  /** @deprecated aliases → six-block ids */
  welcome: number;
  number: number;
  card: number;
  focus: number;
  practice: number;
  close: number;
  priority: number;
  promise: number;
  makeYours: number;
  dayFlow: number;
  recap: number;
};

/** @deprecated name — use TodaySixBlockIndices */
export type TodayHandoffIndices = TodaySixBlockIndices;

export type TodayProductScreenFlowProps = {
  dateISO: string;
  dateLabel: string;
  showSymbols: boolean;
  showPersonalized: boolean;
  /** Block 1a — atmosphere */
  dayBody?: ReactNode;
  /** Block 1b — trap / cues / energy */
  orientationBody?: ReactNode;
  numberBody?: ReactNode;
  cardBody?: ReactNode;
  /** @deprecated */
  symbolsBody?: ReactNode;
  instructionBody?: ReactNode;
  /** @deprecated alias */
  focusBody?: ReactNode;
  colorBody?: ReactNode;
  tasksBody?: ReactNode;
  practiceBody?: ReactNode;
  practiceTitle?: string | null;
  practiceMeta?: string | null;
  practiceActionLabel?: string;
  practiceCompleted?: boolean;
  practiceCompleting?: boolean;
  onPracticeAction?: () => void;
  promiseBody?: ReactNode;
  /** When true, loop body owns accept/checkout — skip legacy CloseFrame. */
  loopOwnsClose?: boolean;
  contract: TodayContractV1;
  tapResponse?: TapResponseCode | null;
  onTapRecorded?: (response: TapResponseCode) => void;
  onOpenEvening: () => void;
  dayPromise?: string | null;
  onCloseOutcome?: (outcome: "done" | "partial" | "not_done") => void;
  activeIndex: number;
  onIndexChange: (index: number, meta: { reason: ScreenFlowChangeReason }) => void;
  embeddedInWebDashboard?: boolean;
  topRowSection?: ReactNode;
  greetingSection?: ReactNode;
};

export function todayHandoffIndices(showSymbols: boolean): TodaySixBlockIndices {
  if (showSymbols) {
    return {
      day: 0,
      orientation: 1,
      rituals: 2,
      instruction: 3,
      color: 4,
      tasks: 5,
      loop: 6,
      welcome: 0,
      number: 2,
      card: 2,
      focus: 3,
      practice: 5,
      close: 6,
      priority: -1,
      promise: 6,
      makeYours: 5,
      dayFlow: 0,
      recap: -1,
    };
  }
  return {
    day: 0,
    orientation: 1,
    rituals: -1,
    instruction: 2,
    color: 3,
    tasks: 4,
    loop: 5,
    welcome: 0,
    number: -1,
    card: -1,
    focus: 2,
    practice: 4,
    close: 5,
    priority: -1,
    promise: 5,
    makeYours: 4,
    dayFlow: 0,
    recap: -1,
  };
}

export function todayScreenFlowStepCount(opts: {
  showSymbols: boolean;
  showPersonalized: boolean;
}): number {
  if (!opts.showPersonalized) return 1;
  return opts.showSymbols ? 7 : 6;
}

export function todayScreenFlowReadingIndex(showSymbols: boolean): number {
  return todayHandoffIndices(showSymbols).instruction;
}

export function todayScreenFlowSymbolsIndex(): number {
  return todayHandoffIndices(true).rituals;
}

export function todayScreenFlowAttributesIndex(showSymbols: boolean): number {
  return todayHandoffIndices(showSymbols).color;
}

export function todayScreenFlowPracticeIndex(showSymbols: boolean): number {
  return todayHandoffIndices(showSymbols).tasks;
}

export function todayScreenFlowInsightIndex(showSymbols: boolean): number {
  return todayHandoffIndices(showSymbols).loop;
}

export function todayScreenFlowCloseIndex(showSymbols: boolean): number {
  return todayHandoffIndices(showSymbols).loop;
}

function SlotStep({
  testId,
  eyebrow,
  title,
  children,
  nextTitle,
  nextHint,
  onNext,
  wide = false,
  hideNext = false,
}: {
  testId: string;
  eyebrow?: string;
  title?: string;
  children: ReactNode;
  nextTitle: string;
  nextHint?: string;
  onNext: () => void;
  /** Wider readable column for day / orientation prose */
  wide?: boolean;
  /** Day dashboard owns its own continue CTA — do not duplicate StoryNextAnchor. */
  hideNext?: boolean;
}) {
  return (
    <div className={sfStyles.storyFrame} data-testid={testId} data-story-scroll="pane">
      <div className={joinClass(sfStyles.slotStack, wide ? sfStyles.slotStackWide : null)}>
        {eyebrow ? <DsEyebrow>{eyebrow}</DsEyebrow> : null}
        {title ? <DsHeadline as="h2">{title}</DsHeadline> : null}
        <div className={sfStyles.slotBody}>{children}</div>
        {hideNext ? null : (
          <StoryNextAnchor title={nextTitle} hint={nextHint} onNext={onNext} />
        )}
      </div>
    </div>
  );
}

export function TodayProductScreenFlow({
  dateISO,
  showSymbols,
  symbolsBody = null,
  numberBody = null,
  cardBody = null,
  showPersonalized,
  dayBody = null,
  orientationBody = null,
  instructionBody = null,
  focusBody = null,
  colorBody = null,
  tasksBody = null,
  practiceTitle = null,
  practiceMeta = null,
  practiceActionLabel = copy.practiceStart,
  practiceCompleted = false,
  practiceCompleting = false,
  onPracticeAction,
  practiceBody = null,
  promiseBody = null,
  loopOwnsClose = false,
  contract,
  tapResponse = null,
  onTapRecorded,
  onOpenEvening,
  dayPromise = null,
  onCloseOutcome,
  activeIndex,
  onIndexChange,
  embeddedInWebDashboard = false,
  topRowSection = null,
  greetingSection = null,
}: TodayProductScreenFlowProps) {
  const go = (index: number) => onIndexChange(index, { reason: "select" });
  const idx = todayHandoffIndices(showSymbols);
  const showChrome = activeIndex > 0;
  const instruction = instructionBody ?? focusBody;
  const numberSlot = numberBody ?? (showSymbols ? symbolsBody : null);
  const cardSlot = cardBody;
  // Dots after day: orientation + rituals? + instruction + color + tasks + loop
  const dotClusters = showSymbols ? [1, 1, 3, 1] : [1, 3, 1];

  useEffect(() => {
    if (!dateISO) return;
    void fetchDayFacts(dateISO).catch(() => {
      /* pane owns failure UI */
    });
  }, [dateISO]);

  const afterDay = idx.orientation;
  const afterOrientation = showSymbols ? idx.rituals : idx.instruction;
  const afterRituals = idx.instruction;
  const afterInstruction = idx.color;
  const afterColor = idx.tasks;
  const afterTasks = idx.loop;

  return (
    <div data-testid="today-zone-foundation" className={sfStyles.flowFoundation}>
      {!embeddedInWebDashboard ? topRowSection : null}
      {!embeddedInWebDashboard ? greetingSection : null}

      <ScreenFlow
        activeIndex={activeIndex}
        onIndexChange={onIndexChange}
        axis={TODAY_SCREEN_FLOW_AXIS}
        showChrome={showChrome}
        showFrameArrows={showChrome}
        dotStartIndex={1}
        dotClusters={showPersonalized ? dotClusters : undefined}
        className={sfStyles.storyBleed}
        testId="today-screen-flow"
      >
        <ScreenFlowStep id="day" label={copy.storyNext.day} scrollable>
          <SlotStep
            testId="today-frame-day"
            wide
            hideNext={showPersonalized}
            nextTitle={
              showPersonalized ? copy.storyNext.orientation : copy.storyNext.further
            }
            nextHint={showPersonalized ? copy.storyNext.orientationHint : undefined}
            onNext={() => go(showPersonalized ? afterDay : 0)}
          >
            {dayBody}
          </SlotStep>
        </ScreenFlowStep>

        {showPersonalized ? (
          <>
            <ScreenFlowStep id="orientation" label={copy.storyNext.orientation} scrollable>
              <SlotStep
                testId="today-frame-orientation"
                wide
                nextTitle={showSymbols ? copy.storyNext.rituals : copy.storyNext.instruction}
                nextHint={showSymbols ? copy.storyNext.ritualsHint : copy.storyNext.instructionHint}
                onNext={() => go(afterOrientation)}
              >
                {orientationBody}
              </SlotStep>
            </ScreenFlowStep>

            {showSymbols ? (
              <ScreenFlowStep id="rituals" label={copy.storyNext.rituals} scrollable>
                <div
                  className={joinClass(sfStyles.storyFrame, sfStyles.ritualFrame)}
                  data-testid="today-frame-rituals"
                  data-story-scroll="pane"
                >
                  <div className={sfStyles.slotStack}>
                    <DsEyebrow>{copy.storyNext.rituals}</DsEyebrow>
                    <div data-testid="today-frame-number">{numberSlot}</div>
                    <div data-testid="today-frame-card">{cardSlot}</div>
                    <StoryNextAnchor
                      title={copy.storyNext.instruction}
                      hint={copy.storyNext.instructionHint}
                      onNext={() => go(afterRituals)}
                    />
                  </div>
                </div>
              </ScreenFlowStep>
            ) : null}

            <ScreenFlowStep id="instruction" label={copy.storyNext.instruction} scrollable>
              <SlotStep
                testId="today-frame-instruction"
                eyebrow={copy.storyNext.instruction}
                title={copy.instructionTitle}
                nextTitle={copy.storyNext.color}
                nextHint={copy.storyNext.colorHint}
                onNext={() => go(afterInstruction)}
              >
                {instruction}
              </SlotStep>
            </ScreenFlowStep>

            <ScreenFlowStep id="color" label={copy.storyNext.color} scrollable={false}>
              <SlotStep
                testId="today-frame-color"
                eyebrow={copy.storyNext.color}
                nextTitle={copy.storyNext.tasks}
                nextHint={copy.storyNext.tasksHint}
                onNext={() => go(afterColor)}
              >
                {colorBody}
              </SlotStep>
            </ScreenFlowStep>

            <ScreenFlowStep id="tasks" label={copy.storyNext.tasks} scrollable>
              {tasksBody ? (
                <SlotStep
                  testId="today-frame-tasks"
                  eyebrow={copy.storyNext.tasks}
                  nextTitle={copy.storyNext.loop}
                  nextHint={copy.storyNext.loopHint}
                  onNext={() => go(afterTasks)}
                >
                  {tasksBody}
                </SlotStep>
              ) : practiceBody ? (
                <SlotStep
                  testId="today-frame-tasks"
                  eyebrow={copy.storyNext.tasks}
                  nextTitle={copy.storyNext.loop}
                  nextHint={copy.storyNext.loopHint}
                  onNext={() => go(afterTasks)}
                >
                  {practiceBody}
                </SlotStep>
              ) : (
                <TodayPracticeFrame
                  title={practiceTitle}
                  meta={practiceMeta}
                  actionLabel={practiceActionLabel}
                  completed={practiceCompleted}
                  completing={practiceCompleting}
                  onAction={() => onPracticeAction?.()}
                  onGoNext={() => go(afterTasks)}
                  linkSlot={
                    <DsCaption muted>
                      <Link href="/practices" data-testid="today-setup-practices-link">
                        {copy.setupPracticesLink} →
                      </Link>
                    </DsCaption>
                  }
                />
              )}
            </ScreenFlowStep>

            <ScreenFlowStep id="loop" label={copy.storyNext.loop} scrollable>
              <div className={sfStyles.storyFrame} data-testid="today-frame-loop" data-story-scroll="pane">
                <div className={sfStyles.slotStack}>
                  <DsEyebrow>{copy.storyNext.loop}</DsEyebrow>
                  <DsHeadline as="h2">
                    {loopOwnsClose ? copy.storyNext.loop : copy.promiseTitle}
                  </DsHeadline>
                  <div className={sfStyles.slotBody}>{promiseBody}</div>
                  {!loopOwnsClose ? (
                    <TodayCloseFrame
                      contract={contract}
                      dateISO={dateISO}
                      tapResponse={tapResponse}
                      onTapRecorded={onTapRecorded}
                      onOpenEvening={onOpenEvening}
                      dayPromise={dayPromise}
                      onPickOutcome={onCloseOutcome}
                    />
                  ) : null}
                </div>
              </div>
            </ScreenFlowStep>
          </>
        ) : null}
      </ScreenFlow>
    </div>
  );
}
