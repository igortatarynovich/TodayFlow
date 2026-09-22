"use client";

import { buildGratitudeMemorySlot, type EveningCloseSnapshot } from "@/lib/todayEveningGratitude";
import {
  todaySlotFailureCopy,
  type TodaySlotLoadFailure,
} from "@/lib/todaySlotAvailability";
import { DsContentCard } from "@/design-system";
import styles from "@/design-system/compositions/dsCompositionSurface.module.css";

type Props = {
  snapshot: EveningCloseSnapshot | null;
  failure?: TodaySlotLoadFailure | null;
};

/**
 * TODAY `T1.continuity` — yesterday gratitude recall, or honest transport chrome.
 * Empty omit. GET fail is not «no yesterday».
 */
export function TodayContinuityRecall({ snapshot, failure = null }: Props) {
  if (failure) {
    return (
      <div className={styles.continuityWrap} data-testid="today-zone-memory" data-memory-state={failure}>
        <DsContentCard
          tone="glass"
          testId="today-continuity-failure"
          title={todaySlotFailureCopy(failure)}
        />
      </div>
    );
  }
  const slot = buildGratitudeMemorySlot(snapshot);
  if (slot.state !== "filled") return null;
  return (
    <div className={styles.continuityWrap} data-testid="today-zone-memory" data-memory-state="filled">
      <section className={styles.continuityPill} data-testid="today-entity-continuity-recall">
        <div className={styles.continuityInner}>
          <span className={styles.continuityAccent} aria-hidden />
          <div>
            <p className={styles.continuityEyebrow}>{slot.eyebrow}</p>
            <p className={styles.continuityBody}>{slot.body}</p>
          </div>
        </div>
      </section>
    </div>
  );
}
