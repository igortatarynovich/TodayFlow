"use client";

import {
  DsActionCard,
  DsBody,
  DsButton,
  DsCaption,
  DsChip,
  DsChipCluster,
  DsContentCard,
  DsEyebrow,
  DsListPanel,
  DsListRow,
} from "@/design-system";
import { TODAY_COMPOSITION_COPY as copy } from "@/components/today/composition/todayCompositionCopy";
import type { TodayLoopModel } from "@/lib/todayLoopModel";
import layout from "@/design-system/compositions/dsCompositions.module.css";

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
 * Block 6 — morning accept + evening checkout (Form Kit).
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
      <div className={layout.stack} data-testid="today-loop-block" data-mode="evening">
        <DsEyebrow>{copy.loopEveningKicker}</DsEyebrow>
        <p data-testid="today-loop-title">
          <DsBody>{copy.loopEveningTitle}</DsBody>
        </p>
        {model.manifesto ? (
          <DsContentCard tone="glass" testId="today-loop-manifesto" body={model.manifesto} />
        ) : null}
        {model.trapCheck ? (
          <DsContentCard
            tone="accent"
            testId="today-loop-trap-check"
            eyebrow={copy.loopTrapCheckLabel}
            body={model.trapCheck}
          />
        ) : null}
        {onPickOutcome ? (
          <DsChipCluster testId="today-loop-outcomes">
            {OUTCOMES.map((row) => (
              <DsChip
                key={row.id}
                selected={outcome === row.id}
                testId={`today-loop-outcome-${row.id}`}
                onClick={() => onPickOutcome(row.id)}
              >
                {row.label}
              </DsChip>
            ))}
          </DsChipCluster>
        ) : null}
        {model.eveningClosure ? (
          <DsCaption>
            <span data-testid="today-loop-evening-closure">{model.eveningClosure}</span>
          </DsCaption>
        ) : (
          <DsCaption>{copy.loopEveningFallback}</DsCaption>
        )}
        <DsActionCard
          tone="accent"
          title={copy.loopSleepCta}
          action={
            <DsButton type="button" variant="primary" data-testid="today-loop-sleep-cta" onClick={onOpenEvening}>
              {copy.loopSleepCta}
            </DsButton>
          }
        />
      </div>
    );
  }

  return (
    <div className={layout.stack} data-testid="today-loop-block" data-mode="morning">
      <DsEyebrow>{copy.loopMorningKicker}</DsEyebrow>
      {model.manifesto ? (
        <DsContentCard tone="glass" testId="today-loop-manifesto" body={model.manifesto} />
      ) : (
        <DsCaption>
          <span data-testid="today-loop-empty">{copy.promiseUnsetHint}</span>
        </DsCaption>
      )}
      {model.accepted ? (
        <DsChip variant="status" testId="today-loop-accepted">
          {copy.loopAcceptedLabel}
        </DsChip>
      ) : model.manifesto ? (
        <DsButton
          type="button"
          variant="primary"
          data-testid="today-loop-accept-cta"
          onClick={() => onAccept(model.manifesto!)}
        >
          {copy.loopAcceptCta}
        </DsButton>
      ) : null}
      {!model.accepted && model.alternatives.length > 0 ? (
        <DsListPanel tone="subtle" title={copy.loopAlternativesLabel} testId="today-loop-alternatives">
          {model.alternatives.map((s) => (
            <DsListRow
              key={s.id}
              title={s.text}
              testId={`today-loop-alt-${s.id}`}
              onClick={() => onAccept(s.text)}
            />
          ))}
        </DsListPanel>
      ) : null}
      <DsButton type="button" variant="secondary" data-testid="today-evening-open" onClick={onOpenEvening}>
        {copy.eveningCta}
      </DsButton>
    </div>
  );
}
