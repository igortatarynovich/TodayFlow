"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { DsBody, DsButton, DsEyebrow, DsRailPanel } from "@/design-system";
import {
  compatibilityWebChromeBundle,
  type CompatWebModeSpec,
} from "@/components/product-ui/compatibilityWebChrome";
import type { FlowPracticesChromeLocale } from "@/components/today/flowPracticesMainTabChrome";
import { readRelationshipMapCircles, type RelationshipCircleRecord } from "@/lib/relationshipMapStore";
import { getLocale } from "@/lib/i18n";
import s from "@/components/product-ui/productWebScreens.module.css";
import pl from "@/design-system/layouts/productPageLayout.module.css";

export type CompatWebModeId = CompatWebModeSpec["id"];

export type CompatibilityWebHubProps = {
  locale?: FlowPracticesChromeLocale;
  isAuthenticated: boolean;
  profiles: Array<{ id: number; label: string }>;
  profile1Id: number | null;
  profile2Id: number | null;
  selectedModeId: CompatWebModeId;
  onModeChange: (modeId: CompatWebModeId) => void;
  onProfile1Change: (id: number) => void;
  onProfile2Change: (id: number) => void;
  onCalculate: () => void;
  loading?: boolean;
  error?: string | null;
};

function initialFromName(name: string): string {
  const trimmed = name.trim();
  return trimmed ? trimmed.charAt(0).toUpperCase() : "+";
}

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

export function CompatibilityWebHubRail({ locale }: { locale?: FlowPracticesChromeLocale }) {
  const resolvedLocale: FlowPracticesChromeLocale =
    locale ?? (getLocale() === "ru" ? "ru" : "en");
  const chrome = useMemo(() => compatibilityWebChromeBundle(resolvedLocale), [resolvedLocale]);
  const [history, setHistory] = useState<RelationshipCircleRecord[]>([]);

  useEffect(() => {
    setHistory(readRelationshipMapCircles().slice(0, 4));
  }, []);

  return (
    <>
      <DsRailPanel title={chrome.railReadTitle}>
        <ul className={s.balanceList}>
          <li className={s.balanceItem}>
            <span className={s.balanceDot} aria-hidden />
            {chrome.railReadWorks}
          </li>
          <li className={s.balanceItem}>
            <span className={s.balanceDot} aria-hidden />
            {chrome.railReadFriction}
          </li>
          <li className={s.balanceItem}>
            <span className={s.balanceDot} aria-hidden />
            {chrome.railReadStep}
          </li>
        </ul>
      </DsRailPanel>
      <DsRailPanel title={chrome.railHistoryTitle}>
        {history.length ? (
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
        ) : (
          <DsBody size="sm" muted>
            {chrome.railHistoryEmpty}
          </DsBody>
        )}
        <p className={s.compatRailQuote}>{chrome.railQuote}</p>
      </DsRailPanel>
    </>
  );
}

export function CompatibilityWebHub({
  locale,
  isAuthenticated,
  profiles,
  profile1Id,
  profile2Id,
  selectedModeId,
  onModeChange,
  onProfile1Change,
  onProfile2Change,
  onCalculate,
  loading,
  error,
}: CompatibilityWebHubProps) {
  const resolvedLocale: FlowPracticesChromeLocale =
    locale ?? (getLocale() === "ru" ? "ru" : "en");
  const chrome = useMemo(() => compatibilityWebChromeBundle(resolvedLocale), [resolvedLocale]);

  const profile1 = profiles.find((p) => p.id === profile1Id) ?? null;
  const profile2 = profiles.find((p) => p.id === profile2Id) ?? null;
  const canCalculate =
    isAuthenticated &&
    profile1Id &&
    profile2Id &&
    profile1Id !== profile2Id &&
    !loading;

  return (
    <div className={pl.content} data-testid="compatibility-web-hub">
      <section className={pl.modeSection} aria-labelledby="compat-hub-modes">
        <DsEyebrow id="compat-hub-modes">{chrome.hubContextEyebrow}</DsEyebrow>
        <div className={pl.modeGrid}>
          {chrome.modes.map((mode) => {
            const active = selectedModeId === mode.id;
            return (
              <button
                key={mode.id}
                type="button"
                className={`${pl.modeCard} ${active ? pl.modeCardActive : ""}`.trim()}
                aria-pressed={active}
                onClick={() => onModeChange(mode.id)}
              >
                <span className={pl.modeIcon} aria-hidden>
                  {mode.emoji}
                </span>
                <p className={pl.modeTitle}>{mode.title}</p>
                <p className={pl.modeHint}>{mode.hint}</p>
              </button>
            );
          })}
        </div>
      </section>

      {!isAuthenticated ? (
        <section className={pl.pairPicker}>
          <div style={{ textAlign: "center" }}>
            <DsBody size="sm" muted>
              {chrome.hubLoginHint}
            </DsBody>
          </div>
          <DsButton href="/auth?redirect=/compatibility">{chrome.hubLoginCta}</DsButton>
        </section>
      ) : profiles.length < 2 ? (
        <section className={pl.pairPicker}>
          <div style={{ textAlign: "center" }}>
            <DsBody size="sm" muted>
              {chrome.hubNeedSecondHint}
            </DsBody>
          </div>
          <DsButton href="/account/profiles">{chrome.hubAddPersonCta}</DsButton>
        </section>
      ) : (
        <section className={pl.pairPicker} aria-labelledby="compat-hub-pair">
          <DsEyebrow id="compat-hub-pair">{chrome.hubPairEyebrow}</DsEyebrow>
          <div className={pl.pairRow}>
            <div className={pl.pairSlot}>
              <span className={`${pl.pairAvatar} ${profile1 ? pl.pairAvatarFilled : ""}`.trim()} aria-hidden>
                {profile1 ? initialFromName(profile1.label) : "?"}
              </span>
              <select
                className={pl.pairSelect}
                value={profile1Id ?? ""}
                onChange={(event) => onProfile1Change(Number(event.target.value))}
                aria-label={chrome.hubProfile1Aria}
              >
                {profiles.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.label}
                  </option>
                ))}
              </select>
            </div>
            <span className={pl.pairConnector} aria-hidden>
              ⇄
            </span>
            <div className={pl.pairSlot}>
              <span className={`${pl.pairAvatar} ${profile2 ? pl.pairAvatarFilled : ""}`.trim()} aria-hidden>
                {profile2 ? initialFromName(profile2.label) : "+"}
              </span>
              <select
                className={pl.pairSelect}
                value={profile2Id ?? ""}
                onChange={(event) => onProfile2Change(Number(event.target.value))}
                aria-label={chrome.hubProfile2Aria}
              >
                <option value="">{chrome.hubAddOption}</option>
                {profiles.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
          <Link href="/account/profiles" className={pl.manageLink}>
            {chrome.hubManageCircle}
          </Link>
        </section>
      )}

      {error ? (
        <div style={{ color: "var(--tf-semantic-error, #991b1b)" }}>
          <DsBody size="sm">{error}</DsBody>
        </div>
      ) : null}

      <div style={{ display: "flex", justifyContent: "center" }}>
        <DsButton size="block" disabled={!canCalculate} onClick={onCalculate}>
          {loading ? chrome.hubCalculateLoading : chrome.hubCalculateCta}
        </DsButton>
      </div>
    </div>
  );
}
