"use client";

import Link from "next/link";
import { useMemo } from "react";
import { DsBody, DsButton } from "@/design-system";
import {
  compatibilityWebChromeBundle,
  type CompatWebModeSpec,
} from "@/components/product-ui/compatibilityWebChrome";
import {
  ProductJourneyScene,
} from "@/components/product-ui/ProductJourneyScene";
import journeyStyles from "@/components/product-ui/ProductJourneyScene.module.css";
import type { FlowPracticesChromeLocale } from "@/components/today/flowPracticesMainTabChrome";
import { getLocale } from "@/lib/i18n";
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
  const selectedMode = chrome.modes.find((m) => m.id === selectedModeId) ?? chrome.modes[0];
  const canCalculate =
    isAuthenticated &&
    profile1Id &&
    profile2Id &&
    profile1Id !== profile2Id &&
    !loading;

  return (
    <div data-testid="compatibility-web-hub">
      <ProductJourneyScene
        step={1}
        title={chrome.hubContextEyebrow}
        lead={
          resolvedLocale === "ru"
            ? "Выбери угол связи — один тихий шаг до рассказа о паре."
            : "Pick the relationship angle — one quiet step before the pair story."
        }
        motif="insight"
        testId="compat-hub-direction"
      >
        <div className={journeyStyles.tabRow} role="group" aria-label={chrome.hubContextEyebrow}>
          {chrome.modes.map((mode) => {
            const active = selectedModeId === mode.id;
            return (
              <button
                key={mode.id}
                type="button"
                className={`${journeyStyles.tabChip} ${active ? journeyStyles.tabChipActive : ""}`.trim()}
                aria-pressed={active}
                onClick={() => onModeChange(mode.id)}
              >
                <span aria-hidden>{mode.emoji} </span>
                {mode.title}
              </button>
            );
          })}
        </div>
        {selectedMode ? (
          <p className={journeyStyles.pairSub} data-testid="compat-hub-direction-lead">
            {selectedMode.hint}
          </p>
        ) : null}
      </ProductJourneyScene>

      <ProductJourneyScene
        step={2}
        title={chrome.hubPairEyebrow}
        lead={
          resolvedLocale === "ru"
            ? "Два человека из круга — рассказ строится вокруг этой пары."
            : "Two people from your circle — the story is built around this pair."
        }
        motif="why"
        testId="compat-hub-pair"
      >
        {!isAuthenticated ? (
          <div className={journeyStyles.actionRow} style={{ flexDirection: "column", alignItems: "flex-start" }}>
            <DsBody size="sm" muted>
              Сначала собери свой Today — имя, дата, первый разбор и email для сохранения.
            </DsBody>
            <div className={journeyStyles.actionRow}>
              <DsButton href="/onboarding/welcome?fresh=1">Создать мой Today</DsButton>
              <DsButton href="/auth?mode=login&redirect=/compatibility" variant="ghost">
                Уже есть аккаунт? Войти
              </DsButton>
            </div>
          </div>
        ) : profiles.length < 2 ? (
          <div className={journeyStyles.actionRow} style={{ flexDirection: "column", alignItems: "flex-start" }}>
            <DsBody size="sm" muted>
              {chrome.hubNeedSecondHint}
            </DsBody>
            <DsBody size="sm" muted>
              Пока можно собрать разбор по знакам или датам — без второго профиля.
            </DsBody>
            <div className={journeyStyles.actionRow}>
              <DsButton href="/compatibility/analyze">Разбор по знакам</DsButton>
              <DsButton href="/compatibility/birthdates" variant="secondary">
                По датам
              </DsButton>
              <DsButton href="/account/profiles" variant="secondary">
                {chrome.hubAddPersonCta}
              </DsButton>
            </div>
          </div>
        ) : (
          <>
            <div className={journeyStyles.pairHero}>
              <div className={journeyStyles.avatarGroup} aria-hidden>
                <span className={journeyStyles.avatar}>
                  {profile1 ? initialFromName(profile1.label) : "?"}
                </span>
                <span className={`${journeyStyles.avatar} ${journeyStyles.avatarOverlap}`}>
                  {profile2 ? initialFromName(profile2.label) : "+"}
                </span>
              </div>
              <div className={journeyStyles.pairMeta}>
                <p className={journeyStyles.pairTitle}>
                  {profile1?.label ?? "—"} · {profile2?.label ?? chrome.hubAddOption}
                </p>
                <p className={journeyStyles.pairSub}>{selectedMode?.title}</p>
              </div>
            </div>
            <div className={pl.pairRow} style={{ justifyContent: "flex-start", marginTop: "0.35rem" }}>
              <div className={pl.pairSlot}>
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
            <Link href="/account/profiles" className={journeyStyles.bridgeLink}>
              {chrome.hubManageCircle}
            </Link>
          </>
        )}
      </ProductJourneyScene>

      <ProductJourneyScene
        step={3}
        title={resolvedLocale === "ru" ? "Разбор" : "Reading"}
        lead={
          resolvedLocale === "ru"
            ? "Один ход — собрать историю связи в выбранном направлении."
            : "One move — build the relationship story in the chosen direction."
        }
        motif="bridge"
        bridge
        testId="compat-hub-cta"
      >
        {error ? (
          <div style={{ color: "var(--tf-semantic-error, #991b1b)" }}>
            <DsBody size="sm">{error}</DsBody>
          </div>
        ) : null}
        <div className={journeyStyles.actionRow}>
          <DsButton size="block" disabled={!canCalculate} onClick={onCalculate}>
            {loading ? chrome.hubCalculateLoading : chrome.hubCalculateCta}
          </DsButton>
        </div>
      </ProductJourneyScene>
    </div>
  );
}
