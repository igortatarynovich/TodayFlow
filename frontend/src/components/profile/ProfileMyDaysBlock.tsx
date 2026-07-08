"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import {
  formatDayContinuityDateRu,
  listClosedDayContinuityRecords,
  outcomeLabelRu,
  type DayContinuityRecord,
} from "@/lib/todayDayContinuity";
import editorialStyles from "@/components/profile/editorial/profileEditorial.module.css";

export const PROFILE_MY_DAYS_COPY = {
  label: "Мои дни",
  title: "История, которую собирает Today",
  emptyLead: "Заверши день в Today — здесь появятся фокус и итог последних дней.",
  ctaToday: "Перейти в Today",
  focusLabel: "Фокус",
  outcomeLabel: "Итог",
} as const;

type Props = {
  className?: string;
};

export function ProfileMyDaysBlock({ className }: Props) {
  const [days, setDays] = useState<DayContinuityRecord[]>([]);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    setDays(listClosedDayContinuityRecords(3));
    setReady(true);
  }, []);

  if (!ready) return null;

  return (
    <section
      className={`${editorialStyles.section} ${editorialStyles.myDays} ${className ?? ""}`.trim()}
      aria-labelledby="profile-my-days"
      data-testid="profile-my-days"
    >
      <p id="profile-my-days" className={editorialStyles.sectionLabel}>
        {PROFILE_MY_DAYS_COPY.label}
      </p>
      <h2 className={editorialStyles.sectionTitle}>{PROFILE_MY_DAYS_COPY.title}</h2>

      {days.length === 0 ? (
        <p className={editorialStyles.sectionLead}>{PROFILE_MY_DAYS_COPY.emptyLead}</p>
      ) : (
        <ul className={editorialStyles.myDaysList}>
          {days.map((day) => (
            <li key={day.dateISO} className={editorialStyles.myDaysItem} data-testid={`profile-my-days-row-${day.dateISO}`}>
              <p className={editorialStyles.myDaysDate}>{formatDayContinuityDateRu(day.dateISO)}</p>
              <p className={editorialStyles.myDaysFocus}>
                <span className={editorialStyles.myDaysFieldLabel}>{PROFILE_MY_DAYS_COPY.focusLabel}</span>
                {day.mainFocus}
              </p>
              {day.outcome ? (
                <p className={editorialStyles.myDaysOutcome}>
                  <span className={editorialStyles.myDaysFieldLabel}>{PROFILE_MY_DAYS_COPY.outcomeLabel}</span>
                  {outcomeLabelRu(day.outcome)}
                </p>
              ) : null}
            </li>
          ))}
        </ul>
      )}

      <Link href="/today" className={`orbit-button orbit-button-secondary ${editorialStyles.myDaysCta}`} data-testid="profile-my-days-today-link">
        {PROFILE_MY_DAYS_COPY.ctaToday}
      </Link>
    </section>
  );
}
