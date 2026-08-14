"use client";

import { DsChip, DsEyebrow, DsListPanel, DsListRow } from "@/design-system";

export type TodayRecapItem = {
  id: string;
  label: string;
  value: string;
  done: boolean;
};

type Props = {
  items: TodayRecapItem[];
};

/** Thin handoff recap — Form Kit list panel. */
export function TodayRecapAchievements({ items }: Props) {
  return (
    <div data-testid="today-handoff-recap" style={{ width: "100%", maxWidth: "22rem", margin: "0 auto" }}>
      <DsListPanel tone="glass" testId="today-recap-sheet">
        {items.map((item) => (
          <DsListRow
            key={item.id}
            testId={`today-recap-${item.id}`}
            title={item.label}
            subtitle={item.value}
            leading={item.done ? <DsChip variant="status">✓</DsChip> : <DsEyebrow>·</DsEyebrow>}
          />
        ))}
      </DsListPanel>
    </div>
  );
}
