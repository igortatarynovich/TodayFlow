"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { DsBody } from "@/design-system";
import { ProductPageScreen } from "@/components/product-ui/ProductPageScreen";
import pl from "@/design-system/layouts/productPageLayout.module.css";
import v2 from "@/design-system/layouts/productV2Surface.module.css";
import {
  buildPromiseDayStory,
  buildPromiseMapCells,
  buildPromiseMapObservation,
  promiseCellColor,
  PROMISE_CELL_EMPTY,
  scanPromiseMapDayRecords,
  type PromiseMapDayCell,
} from "@/lib/promiseMapModel";
import { promiseMapCopy } from "@/lib/promiseMapCopy";
import { getLocale } from "@/lib/i18n";

export default function PromiseMapPage() {
  const locale = getLocale() === "ru" ? "ru" : "en";
  const copy = promiseMapCopy(locale);
  const dateLocale = locale === "ru" ? "ru-RU" : "en-US";

  const todayISO = useMemo(() => new Date().toISOString().split("T")[0], []);
  const [cells, setCells] = useState<PromiseMapDayCell[]>([]);
  const [records, setRecords] = useState<ReturnType<typeof scanPromiseMapDayRecords>>([]);
  const [selectedDate, setSelectedDate] = useState<string | null>(null);

  useEffect(() => {
    setCells(buildPromiseMapCells(todayISO));
    const nextRecords = scanPromiseMapDayRecords();
    setRecords(nextRecords);
    if (nextRecords[0]) setSelectedDate(nextRecords[0].dateISO);
  }, [todayISO]);

  const observation = useMemo(() => buildPromiseMapObservation(records, locale), [records, locale]);
  const selectedRecord = useMemo(
    () => records.find((record) => record.dateISO === selectedDate) ?? null,
    [records, selectedDate],
  );
  const selectedStory = selectedRecord ? buildPromiseDayStory(selectedRecord, locale) : null;

  const legend = [
    { label: copy.legendDone, color: promiseCellColor("done", false) },
    { label: copy.legendPartial, color: promiseCellColor("partial", false) },
    { label: copy.legendNotDone, color: promiseCellColor("not_done", false) },
    { label: copy.legendOpen, color: promiseCellColor("open", false) },
  ];

  return (
    <ProductPageScreen
      testId="promise-map-page"
      eyebrow={copy.eyebrow}
      title={copy.title}
      subtitle={records.length > 0 ? copy.lead : copy.emptyLead}
      contentClassName={`${pl.content} ${pl.legacyHost}`}
    >
      <nav className={pl.toolbar} aria-label="Maps">
        <Link href="/today" className={pl.textLink}>{copy.linkToday}</Link>
        <Link href="/profile" className={pl.textLink}>{copy.linkProfile}</Link>
        <Link href="/maps/mood" className={pl.textLink}>{copy.linkMood}</Link>
        <Link href="/maps/energy" className={pl.textLink}>{copy.linkEnergy}</Link>
        <Link href="/habits" className={pl.textLink}>{copy.linkHabits}</Link>
        <Link href="/tracking/calendar" className={pl.textLink}>{copy.linkRhythm}</Link>
      </nav>

      <section className={pl.panel}>
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(7, minmax(0, 1fr))",
              gap: "0.35rem",
              maxWidth: "560px",
            }}
            role="grid"
            aria-label={copy.title}
          >
            {cells.map((cell) => {
              const selected = cell.dateISO === selectedDate;
              const title = cell.record
                ? `${cell.dateISO} — ${cell.record.promiseText}`
                : new Date(`${cell.dateISO}T12:00:00`).toLocaleDateString(dateLocale);
              return (
                <button
                  key={cell.dateISO}
                  type="button"
                  role="gridcell"
                  disabled={!cell.record}
                  onClick={() => cell.record && setSelectedDate(cell.dateISO)}
                  title={title}
                  style={{
                    width: "100%",
                    aspectRatio: "1 / 1",
                    borderRadius: "6px",
                    border: selected ? "2px solid rgba(91, 67, 53, 0.65)" : "1px solid rgba(166, 124, 58, 0.12)",
                    background: cell.isFuture ? "rgba(236, 228, 214, 0.35)" : cell.color,
                    cursor: cell.record ? "pointer" : "default",
                    opacity: cell.record ? 1 : 0.55,
                    padding: 0,
                  }}
                />
              );
            })}
          </div>

          <ul
            style={{
              display: "flex",
              flexWrap: "wrap",
              gap: "0.55rem 0.9rem",
              margin: "0.85rem 0 0",
              padding: 0,
              listStyle: "none",
            }}
          >
            {legend.map((item) => (
              <li key={item.label} style={{ display: "inline-flex", alignItems: "center", gap: "0.35rem", fontSize: "0.78rem", color: "#7c6241" }}>
                <span aria-hidden style={{ width: "0.75rem", height: "0.75rem", borderRadius: "4px", background: item.color }} />
                {item.label}
              </li>
            ))}
            <li style={{ display: "inline-flex", alignItems: "center", gap: "0.35rem", fontSize: "0.78rem", color: "#9a8468" }}>
              <span aria-hidden style={{ width: "0.75rem", height: "0.75rem", borderRadius: "4px", background: PROMISE_CELL_EMPTY }} />
              {copy.legendEmpty}
            </li>
          </ul>
        </section>

        {observation ? (
          <section className={pl.panel}>
            <p className={v2.eyebrow}>{copy.observationEyebrow}</p>
            <DsBody className={pl.bodyMtSm}>{observation.text}</DsBody>
          </section>
        ) : null}

        <section className={pl.panel}>
          <p className={v2.eyebrow}>{copy.selectedDayEyebrow}</p>
          <DsBody className={pl.bodyMtMd}>{selectedStory ?? copy.selectedDayEmpty}</DsBody>
        </section>

        <section className={pl.panel}>
          <h2 className={v2.sectionTitle}>{copy.howToReadTitle}</h2>
          <DsBody size="sm" muted className={pl.bodyMtSm}>{copy.howToReadLine1}</DsBody>
          <DsBody size="sm" muted className={pl.bodyMtXs}>{copy.howToReadLine2}</DsBody>
        </section>
    </ProductPageScreen>
  );
}
