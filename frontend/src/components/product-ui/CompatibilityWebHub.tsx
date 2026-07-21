"use client";

import Link from "next/link";
import { useMemo } from "react";
import { DsBody, DsButton, DsEyebrow } from "@/design-system";
import {
  compatibilityWebChromeBundle,
  type CompatWebModeSpec,
} from "@/components/product-ui/compatibilityWebChrome";
import type { FlowPracticesChromeLocale } from "@/components/today/flowPracticesMainTabChrome";
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

export { useCompatibilityHubRail, CompatibilityWebHubRail } from "@/components/product-ui/CompatibilityWebHubRail";


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
          <div style={{ textAlign: "center", display: "grid", gap: "0.55rem" }}>
            <DsBody size="sm" muted>
              Сначала собери свой Today — имя, дата, первый разбор и email для сохранения.
            </DsBody>
          </div>
          <div style={{ display: "grid", gap: "0.55rem", justifyItems: "center" }}>
            <DsButton href="/onboarding/welcome?fresh=1">Создать мой Today</DsButton>
            <DsButton href="/auth?mode=login&redirect=/compatibility" variant="ghost">
              Уже есть аккаунт? Войти
            </DsButton>
          </div>
        </section>
      ) : profiles.length < 2 ? (
        <section className={pl.pairPicker}>
          <div style={{ textAlign: "center", display: "grid", gap: "0.65rem" }}>
            <DsBody size="sm" muted>
              {chrome.hubNeedSecondHint}
            </DsBody>
            <DsBody size="sm" muted>
              Пока можно собрать разбор по знакам или датам — без второго профиля.
            </DsBody>
          </div>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "0.55rem", justifyContent: "center" }}>
            <DsButton href="/compatibility/analyze">Разбор по знакам</DsButton>
            <DsButton href="/compatibility/birthdates" variant="secondary">
              По датам
            </DsButton>
            <DsButton href="/account/profiles" variant="secondary">
              {chrome.hubAddPersonCta}
            </DsButton>
          </div>
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
