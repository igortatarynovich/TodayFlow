"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { getJson, putJson } from "@/lib/api";
import type { CoreProfile } from "@/lib/types";
import { DsButton } from "@/design-system";
import styles from "@/components/profile/v2/profileV2System.module.css";

export type DeepThemesApiState = {
  catalog: Array<{ id: string; label: string }>;
  selected: string[];
  cap: number;
  gated: boolean;
  billing_level?: string;
  next_change_at?: string | null;
  can_change?: boolean;
  change_window_days?: number;
};

type ProfileDeepThemesChooserProps = {
  deepFromCore?: CoreProfile["character_engine_deep_themes_v0"] | null;
  onChanged?: () => void;
};

function formatUnlock(iso: string | null | undefined): string | null {
  if (!iso) return null;
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return null;
  return d.toLocaleDateString("ru-RU", { day: "numeric", month: "long" });
}

/**
 * Paid L3 chooser: pick 1–2 deep themes for practical tips.
 * Base sphere copy stays unchanged — tips overlay only.
 */
export function ProfileDeepThemesChooser({ deepFromCore, onChanged }: ProfileDeepThemesChooserProps) {
  const seed = useMemo<DeepThemesApiState>(
    () => ({
      catalog: deepFromCore?.catalog ?? [
        { id: "sex", label: "Секс" },
        { id: "money", label: "Деньги" },
        { id: "love", label: "Любовь" },
        { id: "work", label: "Работа" },
        { id: "body", label: "Тело" },
      ],
      selected: deepFromCore?.selected ?? [],
      cap: deepFromCore?.cap ?? 0,
      gated: Boolean(deepFromCore?.gated ?? true),
      billing_level: deepFromCore?.billing_level,
      next_change_at: deepFromCore?.next_change_at,
      can_change: deepFromCore?.can_change,
      change_window_days: deepFromCore?.change_window_days ?? 7,
    }),
    [deepFromCore],
  );

  const [state, setState] = useState<DeepThemesApiState>(seed);
  const [draft, setDraft] = useState<string[]>(seed.selected);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [savedFlash, setSavedFlash] = useState(false);

  useEffect(() => {
    setState(seed);
    setDraft(seed.selected);
  }, [seed]);

  useEffect(() => {
    let cancelled = false;
    getJson<DeepThemesApiState>("/account/profile/deep-themes")
      .then((res) => {
        if (cancelled || !res) return;
        setState({
          catalog: res.catalog ?? seed.catalog,
          selected: res.selected ?? [],
          cap: res.cap ?? 0,
          gated: Boolean(res.gated),
          billing_level: res.billing_level,
          next_change_at: res.next_change_at,
          can_change: res.can_change,
          change_window_days: res.change_window_days ?? 7,
        });
        setDraft(res.selected ?? []);
      })
      .catch(() => {
        /* keep seed from core-profile */
      });
    return () => {
      cancelled = true;
    };
  }, [seed.catalog]);

  const toggle = useCallback(
    (id: string) => {
      if (state.gated) return;
      setError(null);
      setDraft((prev) => {
        if (prev.includes(id)) return prev.filter((x) => x !== id);
        if (prev.length >= state.cap) {
          // Replace oldest selection when at cap (single-slot UX: swap).
          if (state.cap === 1) return [id];
          return [...prev.slice(1), id].slice(0, state.cap);
        }
        return [...prev, id];
      });
    },
    [state.cap, state.gated],
  );

  const dirty = useMemo(() => {
    const a = [...draft].sort().join(",");
    const b = [...state.selected].sort().join(",");
    return a !== b;
  }, [draft, state.selected]);

  const save = useCallback(async () => {
    if (state.gated || !dirty) return;
    setBusy(true);
    setError(null);
    try {
      const res = await putJson<DeepThemesApiState>("/account/profile/deep-themes", {
        selected: draft,
      });
      setState({
        catalog: res.catalog ?? state.catalog,
        selected: res.selected ?? draft,
        cap: res.cap ?? state.cap,
        gated: Boolean(res.gated),
        billing_level: res.billing_level,
        next_change_at: res.next_change_at,
        can_change: res.can_change,
        change_window_days: res.change_window_days ?? 7,
      });
      setDraft(res.selected ?? draft);
      setSavedFlash(true);
      window.setTimeout(() => setSavedFlash(false), 1800);
      onChanged?.();
    } catch (e) {
      const msg = e instanceof Error ? e.message : "Не удалось сохранить темы.";
      setError(msg);
    } finally {
      setBusy(false);
    }
  }, [dirty, draft, onChanged, state.cap, state.catalog, state.gated]);

  const unlockLabel = formatUnlock(state.next_change_at);

  return (
    <div className={styles.deepThemesBlock} data-testid="profile-deep-themes">
      <p className={styles.deepThemesTitle}>Углубить тему</p>
      <p className={styles.deepThemesLead}>
        {state.gated
          ? "С подпиской можно выбрать тему и получить практические подсказки — без переписывания базового портрета."
          : `Выбери до ${state.cap} тем${state.cap === 1 ? "ы" : ""} — появятся прикладные шаги. Базовый текст сферы не меняется. Смена выбора — раз в ${state.change_window_days ?? 7} дней.`}
      </p>
      <div className={styles.deepThemesChips} role="group" aria-label="Темы глубины">
        {state.catalog.map((theme) => {
          const on = draft.includes(theme.id);
          return (
            <button
              key={theme.id}
              type="button"
              className={`${styles.deepThemesChip} ${on ? styles.deepThemesChipOn : ""}`}
              aria-pressed={on}
              disabled={state.gated || busy || state.can_change === false}
              onClick={() => toggle(theme.id)}
            >
              {theme.label}
            </button>
          );
        })}
      </div>
      {state.gated ? (
        <p className={styles.deepThemesHint}>
          <DsButton href="/pricing" variant="ghost" size="sm" className={styles.deepThemesAction}>
            Открыть trial или Plus/Pro
          </DsButton>
          {" — и выбрать, куда углубить практику."}
        </p>
      ) : null}
      {!state.gated && state.can_change === false && unlockLabel ? (
        <p className={styles.deepThemesHint}>Следующая смена тем — {unlockLabel}.</p>
      ) : null}
      {!state.gated ? (
        <div className={styles.deepThemesActions}>
          <DsButton
            variant="secondary"
            size="sm"
            disabled={!dirty || busy || state.can_change === false}
            onClick={() => void save()}
          >
            {busy ? "Сохраняю…" : "Сохранить выбор"}
          </DsButton>
          {savedFlash ? <span className={styles.deepThemesSaved}>Сохранено</span> : null}
        </div>
      ) : null}
      {error ? <p className={styles.deepThemesError}>{error}</p> : null}
      {!state.gated && deepFromCore?.tips_by_theme
        ? Object.entries(deepFromCore.tips_by_theme).map(([themeId, pack]) => {
            const tips = pack?.tips?.filter(Boolean) ?? [];
            if (!tips.length) return null;
            const label = state.catalog.find((c) => c.id === themeId)?.label ?? themeId;
            return (
              <div key={themeId} className={styles.deepThemesTipsPack} data-testid={`profile-deep-tips-${themeId}`}>
                <p className={styles.deepThemesTipsTitle}>{label}: практические шаги</p>
                <ul className={styles.effortSphereTipsList}>
                  {tips.map((tip) => (
                    <li key={tip}>{tip}</li>
                  ))}
                </ul>
              </div>
            );
          })
        : null}
    </div>
  );
}
