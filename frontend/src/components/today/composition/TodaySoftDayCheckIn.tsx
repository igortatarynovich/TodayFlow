"use client";

import { pickSoftDayCheckIn } from "@/lib/todayDayDialogue";
import { DsButton } from "@/design-system";
import styles from "@/components/today/composition/TodayCompositionSurface.module.css";

type Props = {
  dateISO: string;
  selectedOptionId: string | null;
  onSelect: (checkInId: string, optionId: string, optionLabel: string) => void;
};

/** One indirect question per day — optional, no test framing. */
export function TodaySoftDayCheckIn({ dateISO, selectedOptionId, onSelect }: Props) {
  const checkIn = pickSoftDayCheckIn(dateISO);

  return (
    <div className={styles.softCheckIn} data-testid="today-soft-day-checkin">
      <p className={styles.softCheckInQuestion}>{checkIn.question}</p>
      <div className={styles.softCheckInChips} role="group" aria-label={checkIn.question}>
        {checkIn.options.map((option) => {
          const active = selectedOptionId === option.id;
          return (
            <DsButton
              key={option.id}
              type="button"
              variant={active ? "primary" : "secondary"}
              size="sm"
              className={styles.softCheckInChip}
              data-testid={`soft-checkin-${checkIn.id}-${option.id}`}
              onClick={() => onSelect(checkIn.id, option.id, option.label)}
            >
              {option.label}
            </DsButton>
          );
        })}
      </div>
    </div>
  );
}
