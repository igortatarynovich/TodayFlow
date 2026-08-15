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

type Props = {
  headline?: string | null;
  focusTitle?: string | null;
  focusBody?: string | null;
  priorities?: string[];
  cautions?: string[];
  timeline?: ReactNode;
  colorCard?: ReactNode;
  extraCards?: ReactNode;
  depthLayer?: ReactNode;
};

/**
 * MY DAY — personal headline · focus · priority · cautions · timeline · optional cards.
 * Canon: docs/today/TODAY_PRODUCT_FLOW_V1.md §3. Kit only. Honest omit.
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
  depthLayer = null,
}: Props) {
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
      {extraCards}
      {depthLayer}
    </div>
  );
}
