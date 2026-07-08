"use client";

import Link from "next/link";
import type { ProfileHabitWeaveRow } from "@/lib/profileHabitWeavePreview";
import editorialStyles from "@/components/profile/editorial/profileEditorial.module.css";
import quickMapStyles from "@/components/profile/quickMap/profileQuickMap.module.css";

type Props = {
  row: ProfileHabitWeaveRow;
  variant?: "editorial" | "quickMap";
  selectedDate?: string | null;
  onSelectDate?: (habitId: number, dateISO: string) => void;
  storyLine?: string | null;
};

export function ProfileHabitWeaveMini({
  row,
  variant = "editorial",
  selectedDate,
  onSelectDate,
  storyLine,
}: Props) {
  const styles = variant === "quickMap" ? quickMapStyles : editorialStyles;

  return (
    <article className={styles.profileMapHeatmapRow} data-testid={`profile-habit-weave-${row.habitId}`}>
      <div className={styles.profileMapHeatmapRowHead}>
        <div>
          <p className={styles.profileMapHeatmapRowTitle}>{row.name}</p>
          {row.currentStreakDays > 0 ? (
            <p className={styles.profileHabitWeaveMeta}>
              {row.currentStreakDays}{" "}
              {row.currentStreakDays === 1 ? "день подряд" : row.currentStreakDays < 5 ? "дня подряд" : "дней подряд"}
            </p>
          ) : null}
        </div>
        <Link href={row.href} className={styles.profileMapHeatmapOpenLink}>
          Открыть
        </Link>
      </div>

      <div
        className={styles.profileMapHeatmapGrid}
        role="grid"
        aria-label={`${row.name} — последние ${row.cells.length} дней`}
      >
        {row.cells.map((cell) => {
          const selected = cell.dateISO === selectedDate;
          return (
            <button
              key={cell.dateISO}
              type="button"
              role="gridcell"
              disabled={!cell.hasMark}
              title={cell.title}
              aria-label={cell.title}
              data-testid={`profile-habit-cell-${row.habitId}-${cell.dateISO}`}
              className={`${styles.profileMapHeatmapCell} ${selected ? styles.profileMapHeatmapCellSelected : ""}`}
              style={{
                background: cell.isFuture ? "rgba(236, 228, 214, 0.35)" : cell.color,
                opacity: cell.hasMark ? 1 : 0.55,
              }}
              onClick={() => cell.hasMark && onSelectDate?.(row.habitId, cell.dateISO)}
            />
          );
        })}
      </div>

      {storyLine ? <p className={styles.profileMapHeatmapStory}>{storyLine}</p> : null}
    </article>
  );
}
