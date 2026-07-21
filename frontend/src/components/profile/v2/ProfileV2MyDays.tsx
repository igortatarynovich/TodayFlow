"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { buildDayContinuityWeekCells } from "@/lib/todayDayContinuityHeatmap";
import styles from "@/components/profile/v2/profileV2System.module.css";

export function ProfileV2MyDays() {
  const [todayISO, setTodayISO] = useState<string | null>(null);

  useEffect(() => {
    setTodayISO(new Date().toISOString().slice(0, 10));
  }, []);

  const cells = useMemo(
    () => (todayISO ? buildDayContinuityWeekCells(todayISO, 7) : []),
    [todayISO],
  );

  return (
    <section className={styles.myDaysPanel} aria-labelledby="profile-v2-my-days-title">
      <div className={styles.myDaysPanelHeader}>
        <p id="profile-v2-my-days-title" className={styles.myDaysPanelEyebrow}>
          Мои дни · последняя неделя
        </p>
        <Link href="/today" className={styles.myDaysPanelLink}>
          Открыть Today →
        </Link>
      </div>
      <div className={styles.myDaysWeekGrid} aria-label="Закрытые дни за последнюю неделю">
        {cells.map((cell) => (
          <article
            key={cell.dateISO}
            className={styles.myDaysWeekCell}
            title={cell.closed ? `День закрыт · ${cell.dateISO}` : cell.dateISO}
          >
            <p className={styles.myDaysWeekLabel}>{cell.weekdayLabel}</p>
            <p
              className={`${styles.myDaysWeekMark} ${cell.closed ? styles.myDaysWeekMarkClosed : styles.myDaysWeekMarkOpen}`.trim()}
              aria-hidden
            >
              {cell.closed ? "●" : "◌"}
            </p>
          </article>
        ))}
      </div>
    </section>
  );
}
