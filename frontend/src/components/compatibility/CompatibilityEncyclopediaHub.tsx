"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { fetchCompatibilityEncyclopedia, type CompatibilityEncyclopediaResponse } from "@/lib/compatibilityEncyclopediaApi";
import { COMPATIBILITY_PLAYFUL_SCENARIOS, COMPATIBILITY_PRIMARY_SCENARIOS } from "@/lib/compatibilityScenarioSkins";
import { resolveClientLocale } from "@/lib/i18n";
import {
  buildCompatibilityEchoEvent,
  type CompatibilityLearningMeta,
} from "@/lib/compatibilityEcho";
import { useMeaningRuntime } from "@/hooks/useMeaningRuntime";
import { HeroSmall } from "@/components/foundation/HeroSmall";
import { compatibilityHubSymbol } from "@/lib/compatibilityHeroSymbol";
import styles from "@/components/compatibility/CompatibilityEncyclopediaHub.module.css";

type PairPickerProps = {
  profiles: Array<{ id: number; label: string }>;
  profile1Id: number | null;
  profile2Id: number | null;
  onProfile1Change: (id: number) => void;
  onProfile2Change: (id: number) => void;
  onSubmit: () => void;
  loading?: boolean;
  error?: string | null;
};

type CompatibilityEncyclopediaHubProps = {
  isAuthenticated: boolean;
  showPairPicker?: boolean;
  pairPicker?: PairPickerProps;
  onStartExplore?: () => void;
  /** When set, scenario cards link here instead of sign-only analyze URLs. */
  scenarioHref?: (scenarioId: string, defaultHref: string) => string;
};

export function CompatibilityEncyclopediaHub({
  isAuthenticated,
  showPairPicker = false,
  pairPicker,
  onStartExplore,
  scenarioHref,
}: CompatibilityEncyclopediaHubProps) {
  const locale = resolveClientLocale() === "ru" ? "ru" : "en";
  const [catalog, setCatalog] = useState<CompatibilityEncyclopediaResponse | null>(null);
  const { trackMeaningEvent } = useMeaningRuntime();
  const encyclopediaViewTracked = useRef(false);

  useEffect(() => {
    let cancelled = false;
    void fetchCompatibilityEncyclopedia(locale).then((data) => {
      if (!cancelled) {
        setCatalog(data);
        if (!encyclopediaViewTracked.current) {
          encyclopediaViewTracked.current = true;
          trackMeaningEvent({
            event_type: "compatibility_encyclopedia_view",
            event_source: "compatibility",
            idempotency_key: `compatibility_encyclopedia_view:${data.content_locale}:${data.version}`,
            payload: {
              content_locale: data.content_locale,
              catalog_version: data.version,
            },
          });
        }
      }
    });
    return () => {
      cancelled = true;
    };
  }, [locale, trackMeaningEvent]);

  const trackTopicSelect = (payload: Record<string, string | null | undefined>) => {
    const selectionId = payload.selection_id ?? payload.series_id ?? payload.reading_id ?? "unknown";
    trackMeaningEvent({
      event_type: "compatibility_topic_select",
      event_source: "compatibility",
      idempotency_key: `compatibility_topic_select:hub:${selectionId}:${new Date().toISOString().slice(0, 10)}`,
      payload,
    });
  };

  const trackScenarioPass = (scenarioId: string, toneMode?: string) => {
    const meta: CompatibilityLearningMeta = {
      surface: "hub",
      scenarioId,
      formatId: scenarioId,
      toneMode: toneMode ?? null,
    };
    trackMeaningEvent(buildCompatibilityEchoEvent(meta, `scenario:${scenarioId}`, "no"));
  };

  const hero = catalog?.hero ?? {
    eyebrow: locale === "ru" ? "Совместимость" : "Compatibility",
    title: locale === "ru" ? "Совместимость — это намного больше, чем любовь." : "Compatibility is much more than love.",
    lead:
      locale === "ru"
        ? "Сегодня можно посмотреть, как два человека взаимодействуют в десятках жизненных ситуаций — от романтики до совместного бизнеса."
        : "See how two people interact across dozens of life situations — from romance to running a business together.",
  };

  const sectionThemes = locale === "ru" ? "Выбери сценарий" : "Pick a scenario";
  const sectionThemesLead =
    locale === "ru"
      ? "Каждый сценарий — отдельный мини-продукт: своя атмосфера, свои проценты, свой юмор или серьёзность."
      : "Each scenario is its own mini-experience — its own mood, scores, humor or gravity.";
  const explorePairLabel = locale === "ru" ? "❤️ Исследовать мою пару" : "❤️ Explore my pair";
  const quickSignsLabel = locale === "ru" ? "🎲 Быстрый разбор по знакам" : "🎲 Quick reading by signs";
  const sectionPlayful = locale === "ru" ? "Эксперименты" : "Playful experiments";
  const sectionPlayfulLead =
    locale === "ru"
      ? "Не серьёзный анализ — игровой режим. Тот же движок, другой тон и юмор."
      : "Not a serious analysis — play mode. Same engine, different tone and humor.";
  const passLabel = locale === "ru" ? "Не сейчас" : "Not now";

  return (
    <div className={styles.root}>
      <section className={styles.hero}>
        <HeroSmall
          symbol={compatibilityHubSymbol()}
          kicker={hero.eyebrow}
          title={hero.title}
          meta={hero.lead}
          titleAs="h1"
          flush
        />
        <div className={styles.heroActions}>
          {isAuthenticated ? (
            <button type="button" className={`orbit-button orbit-button-primary ${styles.heroBtnPrimary}`} onClick={onStartExplore}>
              {explorePairLabel}
            </button>
          ) : (
            <Link href="/auth?redirect=/compatibility" className={`orbit-button orbit-button-primary ${styles.heroBtnPrimary}`} style={{ textDecoration: "none" }}>
              {explorePairLabel}
            </Link>
          )}
          <Link href="/compatibility/signs" className={`orbit-button orbit-button-secondary ${styles.heroBtnSecondary}`} style={{ textDecoration: "none" }}>
            {quickSignsLabel}
          </Link>
        </div>
      </section>

      {showPairPicker && pairPicker ? (
        <section id="compat-pair-picker" className={styles.pairPicker}>
          <h2 className={styles.pairPickerTitle}>{locale === "ru" ? "Выбери двух людей" : "Choose two people"}</h2>
          <p className={styles.pairPickerLead}>
            {locale === "ru" ? "Коллега, бывший, партнёр — любая пара, любой сценарий." : "Colleague, ex, partner — any pair, any scenario."}
          </p>
          <div className={styles.pairPickerForm}>
            <label className={styles.pairPickerRow}>
              <span className={styles.pairPickerLabel}>{locale === "ru" ? "Ты" : "You"}</span>
              <select value={pairPicker.profile1Id || ""} onChange={(e) => pairPicker.onProfile1Change(Number(e.target.value))} className="orbit-input">
                {pairPicker.profiles.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.label}
                  </option>
                ))}
              </select>
            </label>
            <label className={styles.pairPickerRow}>
              <span className={styles.pairPickerLabel}>{locale === "ru" ? "Другой человек" : "Other person"}</span>
              <select value={pairPicker.profile2Id || ""} onChange={(e) => pairPicker.onProfile2Change(Number(e.target.value))} className="orbit-input">
                {pairPicker.profiles.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.label}
                  </option>
                ))}
              </select>
            </label>
            <button
              type="button"
              className="orbit-button orbit-button-primary"
              disabled={pairPicker.loading || !pairPicker.profile1Id || !pairPicker.profile2Id || pairPicker.profile1Id === pairPicker.profile2Id}
              onClick={pairPicker.onSubmit}
            >
              {pairPicker.loading ? (locale === "ru" ? "Собираю разбор…" : "Building…") : locale === "ru" ? "Открыть разбор" : "Open reading"}
            </button>
            {pairPicker.error ? (
              <p className="orbit-body-sm" style={{ margin: 0, color: "#991b1b" }}>
                {pairPicker.error}
              </p>
            ) : null}
          </div>
          <Link href="/account/profiles" className="orbit-button orbit-button-secondary orbit-button-sm" style={{ textDecoration: "none", marginTop: "0.85rem", display: "inline-flex" }}>
            {locale === "ru" ? "Добавить человека в круг" : "Add someone"}
          </Link>
        </section>
      ) : !isAuthenticated ? (
        <section className={styles.pairPicker}>
          <h2 className={styles.pairPickerTitle}>{locale === "ru" ? "А если с коллегой? А если бывший?" : "What about a colleague? An ex?"}</h2>
          <p className={styles.pairPickerLead}>
            {locale === "ru" ? "Войди, чтобы сохранить людей и возвращаться к новым сценариям." : "Sign in to save people and return to new scenarios."}
          </p>
        </section>
      ) : (
        <section className={styles.pairPicker}>
          <h2 className={styles.pairPickerTitle}>{locale === "ru" ? "Добавь второго человека в круг" : "Add a second person"}</h2>
          <p className={styles.pairPickerLead}>
            {locale === "ru" ? "Пока один профиль — добавь партнёра, друга или коллегу." : "Add a partner, friend, or colleague."}
          </p>
          <Link href="/account/profiles" className="orbit-button orbit-button-primary" style={{ textDecoration: "none", marginTop: "0.75rem", display: "inline-flex" }}>
            {locale === "ru" ? "Добавить человека" : "Add someone"}
          </Link>
        </section>
      )}

      <section className={styles.section}>
        <h2 className={styles.sectionTitle}>{sectionThemes}</h2>
        <p className={styles.sectionLead}>{sectionThemesLead}</p>
        <div className={styles.scenarioGrid}>
          {COMPATIBILITY_PRIMARY_SCENARIOS.map((scenario) => (
            <div key={scenario.id} className={styles.scenarioCardWrap}>
              <Link
                href={scenarioHref ? scenarioHref(scenario.id, scenario.href) : scenario.href}
                className={`${styles.scenarioCard} ${styles[`skin_${scenario.id}`] ?? ""} ${styles[`tone_${scenario.tone}`] ?? ""}`}
                prefetch
                onClick={() =>
                  trackTopicSelect({
                    selection_kind: "series",
                    selection_id: scenario.id,
                    series_id: scenario.id,
                    format_id: scenario.id,
                    tone_mode: scenario.toneMode,
                  })
                }
              >
                <span className={styles.scenarioEmoji}>{scenario.emoji}</span>
                <p className={styles.scenarioTitle}>{scenario.title}</p>
                <p className={styles.scenarioHook}>{scenario.hook}</p>
                <span className={styles.scenarioFx} aria-hidden />
              </Link>
              <button
                type="button"
                className={styles.scenarioPass}
                onClick={() => trackScenarioPass(scenario.id, scenario.toneMode)}
              >
                {passLabel}
              </button>
            </div>
          ))}
        </div>
      </section>

      <section className={styles.section}>
        <h2 className={styles.sectionTitle}>{sectionPlayful}</h2>
        <p className={styles.sectionLead}>{sectionPlayfulLead}</p>
        <div className={`${styles.scenarioGrid} ${styles.playfulGrid}`}>
          {COMPATIBILITY_PLAYFUL_SCENARIOS.map((scenario) => (
            <div key={scenario.id} className={styles.scenarioCardWrap}>
              <Link
                href={scenarioHref ? scenarioHref(scenario.id, scenario.href) : scenario.href}
                className={`${styles.scenarioCard} ${styles.playfulCard} ${styles[`skin_${scenario.id}`] ?? ""} ${styles[`tone_${scenario.tone}`] ?? ""}`}
                prefetch
                onClick={() =>
                  trackTopicSelect({
                    selection_kind: "series",
                    selection_id: scenario.id,
                    series_id: scenario.id,
                    tone_mode: scenario.toneMode,
                    format_id: scenario.id,
                  })
                }
              >
                <span className={styles.scenarioEmoji}>{scenario.emoji}</span>
                <p className={styles.scenarioTitle}>{scenario.title}</p>
                <p className={styles.scenarioHook}>{scenario.hook}</p>
                <span className={styles.playfulBadge}>{locale === "ru" ? "🎲 игровой" : "🎲 playful"}</span>
                <span className={styles.scenarioFx} aria-hidden />
              </Link>
              <button
                type="button"
                className={styles.scenarioPass}
                onClick={() => trackScenarioPass(scenario.id, scenario.toneMode)}
              >
                {passLabel}
              </button>
            </div>
          ))}
        </div>
      </section>

      {catalog?.popular_readings?.length ? (
        <section className={styles.section}>
          <h2 className={styles.sectionTitle}>{locale === "ru" ? "Быстрые вопросы" : "Quick questions"}</h2>
          <div className={styles.readingGrid}>
            {catalog.popular_readings.slice(0, 6).map((reading) => (
              <Link
                key={reading.id}
                href={`/compatibility/analyze?reading=${reading.id}`}
                className={styles.readingCard}
                prefetch
                onClick={() =>
                  trackTopicSelect({
                    selection_kind: "reading",
                    selection_id: reading.id,
                    reading_id: reading.id,
                  })
                }
              >
                {reading.title}
              </Link>
            ))}
          </div>
        </section>
      ) : null}
    </div>
  );
}
