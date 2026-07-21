"use client";

import type { ReactNode } from "react";
import { useEffect, useMemo, useState } from "react";
import { DsBody, DsRailPanel } from "@/design-system";
import {
  compatibilityWebChromeBundle,
} from "@/components/product-ui/compatibilityWebChrome";
import type { FlowPracticesChromeLocale } from "@/components/today/flowPracticesMainTabChrome";
import { readRelationshipMapCircles, type RelationshipCircleRecord } from "@/lib/relationshipMapStore";
import { getLocale } from "@/lib/i18n";
import s from "@/components/product-ui/productWebScreens.module.css";

function formatHistoryDate(iso: string, locale: FlowPracticesChromeLocale): string {
  try {
    return new Intl.DateTimeFormat(locale === "ru" ? "ru-RU" : "en-US", {
      day: "numeric",
      month: "short",
      year: "numeric",
    }).format(new Date(iso));
  } catch {
    return iso;
  }
}

/**
 * PR-2: context rail only when local pair history exists.
 * Returns null (not an empty panel) so the shell drops the rail column.
 */
export function useCompatibilityHubRail(locale?: FlowPracticesChromeLocale): ReactNode | null {
  const resolvedLocale: FlowPracticesChromeLocale =
    locale ?? (getLocale() === "ru" ? "ru" : "en");
  const chrome = useMemo(() => compatibilityWebChromeBundle(resolvedLocale), [resolvedLocale]);
  const [history, setHistory] = useState<RelationshipCircleRecord[]>([]);

  useEffect(() => {
    setHistory(readRelationshipMapCircles().slice(0, 4));
  }, []);

  if (!history.length) return null;

  return (
    <DsRailPanel title={chrome.railHistoryTitle}>
      <ul className={s.compatHistoryList}>
        {history.map((row) => (
          <li key={row.id} className={s.compatHistoryRow}>
            <div className={s.compatHistoryMeta}>
              <span className={s.compatHistoryLabel}>{row.pairLine ?? row.label}</span>
              <span className={s.compatHistoryDate}>{formatHistoryDate(row.lastSeenAt, resolvedLocale)}</span>
            </div>
            {row.theme ? <span className={s.compatHistoryBadge}>{row.theme}</span> : null}
          </li>
        ))}
      </ul>
    </DsRailPanel>
  );
}

/** @deprecated Prefer useCompatibilityHubRail — keeps decorative how-to out of the shell. */
export function CompatibilityWebHubRail({ locale }: { locale?: FlowPracticesChromeLocale }) {
  return useCompatibilityHubRail(locale);
}
