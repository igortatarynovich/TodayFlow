"use client";

import Link from "next/link";
import type { ProfileMapHeatmapId, ProfileMapHeatmapRow } from "@/lib/profileMapsHeatmapPreview";
import editorialStyles from "@/components/profile/editorial/profileEditorial.module.css";
import quickMapStyles from "@/components/profile/quickMap/profileQuickMap.module.css";

type Props = {
  row: ProfileMapHeatmapRow;
  variant?: "editorial" | "quickMap";
  selectedDate?: string | null;
  onSelectDate?: (mapId: ProfileMapHeatmapId, dateISO: string) => void;
  storyLine?: string | null;
};

export function ProfileMapHeatmapMini({
  row,
  variant = "editorial",
  selectedDate,
  onSelectDate,
  storyLine,
}: Props) {
  const styles = variant === "quickMap" ? quickMapStyles : editorialStyles;

  return (
    <article className={styles.profileMapHeatmapRow} data-testid={`profile-map-heatmap-${row.id}`}>
      <div className={styles.profileMapHeatmapRowHead}>
        <p className={styles.profileMapHeatmapRowTitle}>{row.title}</p>
        <Link href={row.href} className={styles.profileMapHeatmapOpenLink}>
          Открыть
        </Link>
      </div>

      <div
        className={styles.profileMapHeatmapGrid}
        role="grid"
        aria-label={`${row.title} — последние ${row.cells.length} дней`}
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
              data-testid={`profile-map-cell-${row.id}-${cell.dateISO}`}
              className={`${styles.profileMapHeatmapCell} ${selected ? styles.profileMapHeatmapCellSelected : ""}`}
              style={{
                background: cell.isFuture ? "rgba(236, 228, 214, 0.35)" : cell.color,
                opacity: cell.hasMark ? 1 : 0.55,
              }}
              onClick={() => cell.hasMark && onSelectDate?.(row.id, cell.dateISO)}
            />
          );
        })}
      </div>

      {storyLine ? <p className={styles.profileMapHeatmapStory}>{storyLine}</p> : null}
    </article>
  );
}
