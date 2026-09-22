"use client";

import type { ReactNode } from "react";
import {
  DsCallout,
  DsChip,
  DsContentCard,
  DsListPanel,
  DsListRow,
} from "@/design-system";
import { TODAY_COMPOSITION_COPY as copy } from "@/components/today/composition/todayCompositionCopy";
import layout from "@/design-system/compositions/dsCompositions.module.css";
import { TODAY_UNAVAILABLE_COPY } from "@/lib/todaySlotAvailability";

type Props = {
  headline?: string | null;
  focusTitle?: string | null;
  focusBody?: string | null;
  priorities?: string[];
  cautions?: string[];
  timeline?: ReactNode;
  colorCard?: ReactNode;
  extraCards?: ReactNode;
  /** Inventory `T3.tracker` — user habit rows. Survives meaning unavailable. */
  tracker?: ReactNode;
  depthLayer?: ReactNode;
  /** Personal Day meaning missing — one honest status, no leftover color/timeline/focus/extraCards. */
  meaningUnavailable?: boolean;
};

/**
 * MY DAY — personal headline · focus · priority · cautions · timeline · optional cards.
 * Canon: docs/today/TODAY_PRODUCT_FLOW_V1.md §3. Kit only. Honest omit.
 * TIC-K20: unavailable paints T3.unavailable — extraCards are not surrogate meaning.
 * X14: `T3.tracker` is user habit state and stays on the pane.
 */
export function TodayMyDayPane({
  headline = null,
  focusTitle = null,
  focusBody = null,
  priorities = [],
  cautions = [],
  timeline = null,
  colorCard = null,
  extraCards = null,
  tracker = null,
  depthLayer = null,
  meaningUnavailable = false,
}: Props) {
  if (meaningUnavailable) {
    return (
      <div className={layout.stack} data-testid="today-my-day" data-fallback="unavailable">
        <DsContentCard
          tone="glass"
          testId="today-my-day-unavailable"
          title={TODAY_UNAVAILABLE_COPY}
        />
        {tracker}
      </div>
    );
  }

  return (
    <div className={layout.stack} data-testid="today-my-day">
      {headline ? (
        <DsContentCard tone="glass" testId="today-my-day-headline" title={headline} />
      ) : null}

      {focusTitle || focusBody ? (
        <DsCallout
          tone="insight"
          label="main"
          icon="spark"
          title={focusTitle || copy.myDayFocusLabel}
          testId="today-handoff-focus"
        >
          {focusBody ? <p data-testid="today-instruction-bridge">{focusBody}</p> : null}
        </DsCallout>
      ) : null}

      {priorities.length > 0 ? (
        <DsListPanel tone="subtle" title={copy.myDayPriorityLabel} testId="today-handoff-focus-prioritize">
          {priorities.map((item) => (
            <DsListRow
              key={item}
              leading={<DsChip variant="status" statusTone="good"> </DsChip>}
              title={item}
            />
          ))}
        </DsListPanel>
      ) : null}

      {cautions.length > 0 ? (
        <DsListPanel tone="solid" title={copy.myDayCautionLabel} testId="today-handoff-focus-avoid">
          {cautions.map((item) => (
            <DsListRow
              key={item}
              leading={<DsChip variant="status" statusTone="risk"> </DsChip>}
              title={item}
            />
          ))}
        </DsListPanel>
      ) : null}

      {timeline}

      {colorCard}
      {tracker}
      {extraCards}
      {depthLayer}
    </div>
  );
}
