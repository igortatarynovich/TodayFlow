"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";
import { DsBody } from "@/design-system";
import { ProductPageScreen } from "@/components/product-ui/ProductPageScreen";
import pl from "@/design-system/layouts/productPageLayout.module.css";
import v2 from "@/design-system/layouts/productV2Surface.module.css";
import { LoadingSpinner } from "@/components/orbit";
import { tempoLabelForEnergyScore } from "@/components/today/todayRitualCopy";
import type { FusionResponse } from "@/components/today/todayPageUtils";
import {
  buildEnergyDayStory,
  buildEnergyMapCells,
  buildEnergyMapObservation,
  buildEnergyMapRecordsWithMoodFallback,
  ENERGY_CELL_EMPTY,
  energyCellColor,
  type EnergyMapDayCell,
} from "@/lib/energyMapModel";
import { energyMapCopy } from "@/lib/energyMapCopy";
import { getJson } from "@/lib/api";
import { getLocale } from "@/lib/i18n";
import { useAuth } from "@/lib/useAuth";
import { buildMoodMapWindow } from "@/lib/moodMapModel";
import { persistEnergyFromFusionResponse } from "@/lib/energyMapStorage";

export default function EnergyMapPage() {
  const locale = getLocale() === "ru" ? "ru" : "en";
  const copy = energyMapCopy(locale);
  const dateLocale = locale === "ru" ? "ru-RU" : "en-US";
  const { isAuthenticated, isLoading: authLoading } = useAuth();

  const todayISO = useMemo(() => new Date().toISOString().split("T")[0], []);
  const [cells, setCells] = useState<EnergyMapDayCell[]>([]);
  const [records, setRecords] = useState<ReturnType<typeof buildEnergyMapRecordsWithMoodFallback>>([]);
  const [selectedDate, setSelectedDate] = useState<string | null>(null);
  const [syncing, setSyncing] = useState(false);

  const refreshLocal = useCallback(() => {
    const nextRecords = buildEnergyMapRecordsWithMoodFallback();
    setRecords(nextRecords);
    setCells(buildEnergyMapCells(todayISO));
    if (!selectedDate && nextRecords[0]) setSelectedDate(nextRecords[0].dateISO);
  }, [selectedDate, todayISO]);

  useEffect(() => {
    refreshLocal();
  }, [refreshLocal]);

  useEffect(() => {
    if (authLoading || !isAuthenticated) return;

    let cancelled = false;
    (async () => {
      setSyncing(true);
      try {
        const dates = buildMoodMapWindow(todayISO, 35);
        await Promise.all(
          dates.map(async (dateISO) => {
            const fusion = await getJson<FusionResponse>(`/tracking/fusion/${dateISO}`).catch(() => null);
            if (fusion) persistEnergyFromFusionResponse(dateISO, fusion, "fusion_api");
          }),
        );
        if (!cancelled) refreshLocal();
      } finally {
        if (!cancelled) setSyncing(false);
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [authLoading, isAuthenticated, refreshLocal, todayISO]);

  const observation = useMemo(() => buildEnergyMapObservation(records, locale), [records, locale]);
  const selectedRecord = useMemo(
    () => records.find((record) => record.dateISO === selectedDate) ?? null,
    [records, selectedDate],
  );
  const selectedStory = selectedRecord ? buildEnergyDayStory(selectedRecord, locale) : null;

  const legend = [
    { label: copy.legendQuiet, color: energyCellColor(30) },
    { label: copy.legendCalm, color: energyCellColor(48) },
    { label: copy.legendSteady, color: energyCellColor(68) },
    { label: copy.legendActive, color: energyCellColor(85) },
  ];

  return (
    <ProductPageScreen
      testId="energy-map-page"
      eyebrow={copy.eyebrow}
      title={copy.title}
      subtitle={records.length > 0 ? copy.lead : copy.emptyLead}
      contentClassName={`${pl.content} ${pl.legacyHost}`}
    >
      {syncing ? (
        <DsBody size="sm" muted className={pl.flexRowCenter}>
          <LoadingSpinner size="sm" />
          {copy.loading}
        </DsBody>
      ) : null}

      <nav className={pl.toolbar} aria-label="Maps">
        <Link href="/today" className={pl.textLink}>
          {copy.linkToday}
        </Link>
        <Link href="/profile" className={pl.textLink}>
          {copy.linkProfile}
        </Link>
        <Link href="/maps/mood" className={pl.textLink}>
          {copy.linkMood}
        </Link>
        <Link href="/habits" className={pl.textLink}>
          {copy.linkHabits}
        </Link>
        <Link href="/tracking/calendar" className={pl.textLink}>
          {copy.linkRhythm}
        </Link>
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
                ? `${cell.dateISO} — ${cell.tempoLabel ?? tempoLabelForEnergyScore(cell.record.energyScore)}`
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
              <span aria-hidden style={{ width: "0.75rem", height: "0.75rem", borderRadius: "4px", background: ENERGY_CELL_EMPTY }} />
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
          <DsBody size="sm" muted className={pl.bodyMtSm}>
            {copy.howToReadLine1}
          </DsBody>
          <DsBody size="sm" muted className={pl.bodyMtXs}>
            {copy.howToReadLine2}
          </DsBody>
        </section>
    </ProductPageScreen>
  );
}
