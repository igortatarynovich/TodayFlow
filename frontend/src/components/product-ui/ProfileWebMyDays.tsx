"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { profileWebChromeBundle } from "@/components/product-ui/profileWebChrome";
import type { FlowPracticesChromeLocale } from "@/components/today/flowPracticesMainTabChrome";
import { getLocale } from "@/lib/i18n";
import { listClosedDayContinuityRecords } from "@/lib/todayDayContinuity";
import s from "@/components/product-ui/productWebScreens.module.css";

const HEATMAP_SIZE = 21;

function heatOpacity(index: number, filled: number): number {
  if (index >= filled) return 0.18;
  const wave = [1, 0.4, 0.2, 0.8, 0.6, 1, 0.2, 0.4, 0.8, 1, 0.6, 0.4, 0.2, 0.6, 0.8, 1, 0.4, 0.2, 0.6, 0.8, 1];
  return wave[index % wave.length] ?? 0.5;
}

export function ProfileWebMyDays({ locale }: { locale?: FlowPracticesChromeLocale }) {
  const resolvedLocale: FlowPracticesChromeLocale =
    locale ?? (getLocale() === "ru" ? "ru" : "en");
  const chrome = useMemo(() => profileWebChromeBundle(resolvedLocale), [resolvedLocale]);
  const [filledDays, setFilledDays] = useState(0);

  useEffect(() => {
    setFilledDays(listClosedDayContinuityRecords(21).length);
  }, []);

  const cells = useMemo(
    () =>
      Array.from({ length: HEATMAP_SIZE }, (_, index) => ({
        key: index,
        opacity: heatOpacity(index, filledDays),
      })),
    [filledDays],
  );

  return (
    <section className={s.profileSection} aria-labelledby="profile-web-my-days">
      <div className={s.myDaysHeader}>
        <p id="profile-web-my-days" className={s.myDaysEyebrow}>
          {chrome.myDaysEyebrow}
        </p>
        <Link href="/today" className={s.myDaysLink}>
          {chrome.myDaysLink}
        </Link>
      </div>
      <div className={s.myDaysHeatmap} aria-label={chrome.myDaysHeatmapAria}>
        {cells.map((cell) => (
          <span
            key={cell.key}
            className={s.myDaysCell}
            style={{ opacity: cell.opacity }}
            aria-hidden
          />
        ))}
      </div>
    </section>
  );
}
