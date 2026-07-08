"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { DsBody, DsButton } from "@/design-system";
import { ProductPageScreen } from "@/components/product-ui/ProductPageScreen";
import pl from "@/design-system/layouts/productPageLayout.module.css";
import v2 from "@/design-system/layouts/productV2Surface.module.css";
import { getJson } from "@/lib/api";
import { useAuth } from "@/lib/useAuth";
import { getLocale } from "@/lib/i18n";
import { buildMoodMapWindow } from "@/lib/moodMapModel";
import {
  asceticJourneyStepColor,
  buildAsceticDayStory,
  buildAsceticJourneyArcs,
  buildAsceticJourneyObservation,
  buildAsceticShareLine,
  type AsceticCalendarTrackIn,
  type AsceticContractIn,
  type AsceticJourneyArc,
} from "@/lib/asceticMapModel";
import { asceticMapCopy } from "@/lib/asceticMapCopy";
import { copyMapShareLine } from "@/lib/mapShareCard";

type AsceticContractAPI = AsceticContractIn;
type CalendarPayload = { ascetic_tracks?: AsceticCalendarTrackIn[] };

export default function AsceticMapPage() {
  const locale = getLocale() === "ru" ? "ru" : "en";
  const copy = asceticMapCopy(locale);
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const todayISO = useMemo(() => new Date().toISOString().split("T")[0], []);

  const [loading, setLoading] = useState(true);
  const [arcs, setArcs] = useState<AsceticJourneyArc[]>([]);
  const [selectedArcId, setSelectedArcId] = useState<number | null>(null);
  const [selectedDate, setSelectedDate] = useState<string | null>(null);
  const [shareCopied, setShareCopied] = useState(false);

  useEffect(() => {
    if (authLoading) return;
    if (!isAuthenticated) {
      setArcs([]);
      setLoading(false);
      return;
    }
    let cancelled = false;
    (async () => {
      setLoading(true);
      try {
        const window = buildMoodMapWindow(todayISO, 35);
        const fromIso = window[0] ?? todayISO;
        const toIso = window[window.length - 1] ?? todayISO;
        const [contracts, calendar] = await Promise.all([
          getJson<AsceticContractAPI[]>("/tracking/ascetic-contracts").catch(() => []),
          getJson<CalendarPayload>(`/tracking/calendar?from_date=${fromIso}&to_date=${toIso}`).catch(() => ({
            ascetic_tracks: [],
          })),
        ]);
        if (cancelled) return;
        const nextArcs = buildAsceticJourneyArcs(contracts, calendar.ascetic_tracks ?? [], todayISO);
        setArcs(nextArcs);
        if (nextArcs[0]) {
          setSelectedArcId(nextArcs[0].contractId);
          const marked = [...nextArcs[0].steps].reverse().find((s) => s.completed && !s.isFuture);
          setSelectedDate(marked?.dateISO ?? nextArcs[0].steps.find((s) => !s.isFuture)?.dateISO ?? null);
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [authLoading, isAuthenticated, todayISO]);

  const selectedArc = useMemo(
    () => arcs.find((arc) => arc.contractId === selectedArcId) ?? arcs[0] ?? null,
    [arcs, selectedArcId],
  );
  const observation = useMemo(() => buildAsceticJourneyObservation(arcs, locale), [arcs, locale]);
  const selectedStory =
    selectedArc && selectedDate ? buildAsceticDayStory(selectedArc, selectedDate, locale) : null;
  const shareLine = useMemo(() => buildAsceticShareLine(arcs, locale), [arcs, locale]);

  const onShare = async () => {
    if (!shareLine) return;
    const ok = await copyMapShareLine(shareLine);
    if (ok) {
      setShareCopied(true);
      window.setTimeout(() => setShareCopied(false), 2000);
    }
  };

  if (authLoading || loading) {
    return (
      <ProductPageScreen testId="ascetic-map-page" title={copy.title} loading loadingLabel="Загрузка…" />
    );
  }

  return (
    <ProductPageScreen
      testId="ascetic-map-page"
      eyebrow={copy.eyebrow}
      title={copy.title}
      subtitle={arcs.length > 0 ? copy.lead : copy.emptyLead}
      contentClassName={`${pl.content} ${pl.legacyHost}`}
    >
      <nav className={pl.toolbar} aria-label="Maps">
        <Link href="/today" className={pl.textLink}>{copy.linkToday}</Link>
        <Link href="/profile" className={pl.textLink}>{copy.linkProfile}</Link>
        <Link href="/tracking/calendar" className={pl.textLink}>{copy.linkRhythm}</Link>
        <Link href="/maps/promise" className={pl.textLink}>{copy.linkPromise}</Link>
        <Link href="/asceticisms" className={pl.textLink}>Аскезы</Link>
      </nav>

      {selectedArc ? (
        <section className={pl.panel}>
            {arcs.length > 1 ? (
              <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem", marginBottom: "0.85rem" }}>
                {arcs.map((arc) => (
                  <button
                    key={arc.contractId}
                    type="button"
                    onClick={() => {
                      setSelectedArcId(arc.contractId);
                      const marked = [...arc.steps].reverse().find((s) => s.completed && !s.isFuture);
                      setSelectedDate(marked?.dateISO ?? arc.steps.find((s) => !s.isFuture)?.dateISO ?? null);
                    }}
                    className={pl.domainChip}
                    style={{
                      borderColor: selectedArcId === arc.contractId ? "rgba(91, 67, 53, 0.55)" : undefined,
                    }}
                  >
                    {arc.title}
                  </button>
                ))}
              </div>
            ) : null}
            <p className="orbit-body-sm" style={{ margin: "0 0 0.75rem", color: "#7c6241" }}>
              {selectedArc.title}
              {selectedArc.streakDays > 0
                ? ` · ${selectedArc.streakDays} ${locale === "ru" ? "дн. подряд" : "days in a row"}`
                : ""}
            </p>
            <div style={{ display: "flex", flexWrap: "wrap", gap: "0.35rem" }}>
              {selectedArc.steps.map((step) => {
                const selected = step.dateISO === selectedDate;
                return (
                  <button
                    key={step.dateISO}
                    type="button"
                    disabled={step.isFuture}
                    onClick={() => setSelectedDate(step.dateISO)}
                    title={step.dateISO}
                    style={{
                      width: "1.35rem",
                      height: "1.35rem",
                      borderRadius: "5px",
                      border: selected ? "2px solid rgba(91, 67, 53, 0.65)" : "1px solid rgba(166, 124, 58, 0.12)",
                      background: asceticJourneyStepColor(step.completed, step.isFuture),
                      cursor: step.isFuture ? "default" : "pointer",
                      padding: 0,
                    }}
                  />
                );
              })}
            </div>
            <ul style={{ display: "flex", gap: "1rem", margin: "0.85rem 0 0", padding: 0, listStyle: "none", fontSize: "0.78rem", color: "#7c6241" }}>
              <li style={{ display: "inline-flex", alignItems: "center", gap: "0.35rem" }}>
                <span aria-hidden style={{ width: "0.75rem", height: "0.75rem", borderRadius: "4px", background: asceticJourneyStepColor(true, false) }} />
                {copy.legendDone}
              </li>
              <li style={{ display: "inline-flex", alignItems: "center", gap: "0.35rem" }}>
                <span aria-hidden style={{ width: "0.75rem", height: "0.75rem", borderRadius: "4px", background: asceticJourneyStepColor(false, false) }} />
                {copy.legendEmpty}
              </li>
            </ul>
          </section>
        ) : null}

        {observation ? (
          <section className={pl.panel}>
            <p className={v2.eyebrow}>{copy.observationEyebrow}</p>
            <DsBody className={pl.bodyMtSm}>{observation}</DsBody>
          </section>
        ) : null}

        <section className={pl.panel}>
          <p className={v2.eyebrow}>{copy.selectedDayEyebrow}</p>
          <DsBody className={pl.bodyMtMd}>{selectedStory ?? copy.selectedDayEmpty}</DsBody>
        </section>

        {shareLine ? (
          <DsButton variant="secondary" onClick={onShare}>
            {shareCopied ? copy.shareCopied : copy.shareCta}
          </DsButton>
        ) : null}

        <section className={pl.panel}>
          <h2 className={v2.sectionTitle}>{copy.howToReadTitle}</h2>
          <DsBody size="sm" muted className={pl.bodyMtSm}>{copy.howToRead}</DsBody>
        </section>
    </ProductPageScreen>
  );
}
