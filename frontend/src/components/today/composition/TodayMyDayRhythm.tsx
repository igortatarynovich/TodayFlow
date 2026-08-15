"use client";

import { useCallback, useEffect, useId, useState } from "react";
import {
  DsBody,
  DsCard,
  DsEyebrow,
  DsListPanel,
  DsListRow,
  DsOverlaySheet,
} from "@/design-system";
import { TODAY_COMPOSITION_COPY as copy } from "@/components/today/composition/todayCompositionCopy";
import layout from "@/design-system/compositions/dsCompositions.module.css";
import { fetchDayFacts, type DayFactsResponse } from "@/lib/todayDayFacts";
import type { GlanceTimelineItem } from "@/lib/todayGlanceTimeline";
import type { TodayContractGlobalDayWindowV1 } from "@/lib/todayContract";
import {
  todaySlotFailureCopy,
  type TodaySlotLoadFailure,
} from "@/lib/todaySlotAvailability";
import { buildTodayMyDayRhythm, type TodayMyDayRhythmRow } from "@/lib/todayMyDayRhythm";

type Props = {
  dateISO: string;
  windows?: TodayContractGlobalDayWindowV1[] | null;
  glanceRows?: GlanceTimelineItem[] | null;
};

type SheetState = TodayMyDayRhythmRow | null;

/**
 * Personal timeline on MY DAY. Kit only.
 * Omit when no natal clocks. Failure copy is transport-only — no invent.
 */
export function TodayMyDayRhythm({ dateISO, windows = null, glanceRows }: Props) {
  const fromParent = glanceRows != null;
  const [rows, setRows] = useState(() =>
    fromParent ? buildTodayMyDayRhythm({ glanceRows, windows }) : [],
  );
  const [failure, setFailure] = useState<TodaySlotLoadFailure | null>(null);
  const [loaded, setLoaded] = useState(fromParent);
  const [sheet, setSheet] = useState<SheetState>(null);
  const closeSheet = useCallback(() => setSheet(null), []);

  useEffect(() => {
    if (glanceRows != null) {
      setFailure(null);
      setRows(buildTodayMyDayRhythm({ glanceRows, windows }));
      setLoaded(true);
      return;
    }

    let cancelled = false;
    setLoaded(false);
    setFailure(null);
    void fetchDayFacts(dateISO)
      .then((data: DayFactsResponse) => {
        if (cancelled) return;
        if (data.is_fallback ?? data.degraded) {
          setFailure("unavailable");
          setRows([]);
        } else {
          setFailure(null);
          setRows(buildTodayMyDayRhythm({ glanceRows: data.glance_timeline ?? [], windows }));
        }
        setLoaded(true);
      })
      .catch(() => {
        if (cancelled) return;
        setFailure("no_connection");
        setRows([]);
        setLoaded(true);
      });
    return () => {
      cancelled = true;
    };
  }, [dateISO, glanceRows, windows]);

  if (!loaded) {
    return (
      <div className={layout.stack} data-testid="today-my-day-rhythm" data-loading="true" aria-busy="true" />
    );
  }

  if (failure) {
    return (
      <DsCard tone="glass" size="compact" testId="today-my-day-rhythm">
        <DsEyebrow>{copy.myDayRhythmLabel}</DsEyebrow>
        <p data-testid="today-my-day-rhythm-failure" role="status">
          <DsBody size="sm" muted>
            {todaySlotFailureCopy(failure)}
          </DsBody>
        </p>
      </DsCard>
    );
  }

  if (rows.length === 0) return null;

  return (
    <>
      <DsCard tone="glass" size="compact" testId="today-my-day-rhythm">
        <DsEyebrow>{copy.myDayRhythmLabel}</DsEyebrow>
        <DsListPanel tone="subtle" testId="today-my-day-rhythm-list">
          {rows.map((row) => (
            <DsListRow
              key={row.id}
              testId={`today-my-day-rhythm-${row.id}`}
              title={row.timeLabel}
              subtitle={row.title}
              onClick={() => setSheet(row)}
            />
          ))}
        </DsListPanel>
      </DsCard>
      <RhythmDetailSheet sheet={sheet} onClose={closeSheet} />
    </>
  );
}

function RhythmDetailSheet({ sheet, onClose }: { sheet: SheetState; onClose: () => void }) {
  const titleId = useId();
  useEffect(() => {
    if (!sheet) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    const prev = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      window.removeEventListener("keydown", onKey);
      document.body.style.overflow = prev;
    };
  }, [sheet, onClose]);

  if (!sheet) return null;

  const rows: Array<{ label: string; value: string }> = [];
  if (sheet.supports.length) {
    rows.push({ label: copy.windowSupportLabel, value: sheet.supports.join(" · ") });
  }
  if (sheet.cautions.length) {
    rows.push({ label: copy.windowCautionLabel, value: sheet.cautions.join(" · ") });
  }
  if (sheet.detail) {
    rows.push({ label: copy.sheetContext, value: sheet.detail });
  }

  return (
    <DsOverlaySheet
      testId="today-my-day-rhythm-sheet"
      titleId={titleId}
      title={sheet.timeLabel}
      kicker={copy.myDayRhythmLabel}
      body={sheet.title}
      closeLabel={copy.sheetClose}
      onClose={onClose}
    >
      {rows.length ? (
        <DsListPanel tone="subtle" testId="today-my-day-rhythm-sheet-rows">
          {rows.map((row) => (
            <DsListRow key={row.label} title={row.label} subtitle={row.value} />
          ))}
        </DsListPanel>
      ) : null}
    </DsOverlaySheet>
  );
}
