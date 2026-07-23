"use client";

import type { CSSProperties, ReactNode } from "react";
import { useMemo } from "react";
import { DsBody, DsButton, DsRailPanel } from "@/design-system";
import {
  compatibilityWebChromeBundle,
  type CompatibilityWebChrome,
} from "@/components/product-ui/compatibilityWebChrome";
import {
  ProductJourneyScene,
  ProductNarrativeScroll,
  type ProductNarrativeChapter,
} from "@/components/product-ui/ProductJourneyScene";
import journeyStyles from "@/components/product-ui/ProductJourneyScene.module.css";
import type { FlowPracticesChromeLocale } from "@/components/today/flowPracticesMainTabChrome";
import type { CompatibilityExplorationModel } from "@/lib/buildCompatibilityExplorationModel";
import { getLocale } from "@/lib/i18n";
import s from "@/components/product-ui/productWebScreens.module.css";

export type CompatibilityWebResultProps = {
  model: CompatibilityExplorationModel;
  name1: string;
  name2: string;
  activeScenarioId: string;
  works: string[];
  fails: string[];
  frictionTags: string[];
  potentialLabel: string;
  nextStep: string;
  metaChips?: string[];
  locale?: FlowPracticesChromeLocale;
  buildScenarioHref: (scenarioId: string) => string;
  onScenarioSwitch?: (scenarioId: string, href: string) => void;
  onShare?: () => void;
  onSave?: () => void;
  onDeepOpen?: () => void;
  extra?: ReactNode;
};

function initialFromName(name: string): string {
  const trimmed = name.trim();
  return trimmed ? trimmed.charAt(0).toUpperCase() : "?";
}

function ensurePeriod(text: string): string {
  const t = text.replace(/\s+/g, " ").trim();
  if (!t) return "";
  return /[.!?…]$/.test(t) ? t : `${t}.`;
}

export function CompatibilityWebResultRail({
  score,
  dimensions,
  chrome,
}: {
  score: number;
  dimensions: CompatibilityExplorationModel["dimensions"];
  chrome: CompatibilityWebChrome;
}) {
  const ringStyle = { "--ce-score-pct": score } as CSSProperties;

  return (
    <>
      <DsRailPanel title={chrome.resultScoreTitle}>
        <div className={s.compatRailScore}>
          <div className={s.compatScoreRing} style={ringStyle} aria-hidden>
            <div className={s.compatScoreRingInner}>{score}%</div>
          </div>
        </div>
      </DsRailPanel>
      {dimensions.length ? (
        <DsRailPanel title={chrome.resultDimensionsTitle}>
          <div className={s.compatMetricList}>
            {dimensions.map((dimension) => (
              <div key={dimension.id} className={s.compatMetricRow}>
                <div className={s.compatMetricHead}>
                  <span>
                    {dimension.emoji} {dimension.label}
                  </span>
                  <span>{dimension.score}%</span>
                </div>
                <div className={s.compatMetricTrack} aria-hidden>
                  <span
                    className={s.compatMetricFill}
                    style={{ width: `${Math.min(100, Math.max(0, dimension.score))}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </DsRailPanel>
      ) : null}
    </>
  );
}

export function CompatibilityWebResult({
  model,
  name1,
  name2,
  activeScenarioId,
  works,
  fails,
  frictionTags,
  potentialLabel,
  nextStep,
  metaChips = [],
  locale,
  buildScenarioHref,
  onScenarioSwitch,
  onShare,
  onSave,
  onDeepOpen,
  extra,
}: CompatibilityWebResultProps) {
  const resolvedLocale: FlowPracticesChromeLocale =
    locale ?? (getLocale() === "ru" ? "ru" : "en");
  const chrome = useMemo(() => compatibilityWebChromeBundle(resolvedLocale), [resolvedLocale]);

  const pairLine = model.pairLine || `${name1} и ${name2}`;

  const storyChapters = useMemo((): ProductNarrativeChapter[] => {
    const chapters: ProductNarrativeChapter[] = [];
    const opening: string[] = [];
    if (model.mainThought?.trim()) opening.push(ensurePeriod(model.mainThought));
    for (const line of model.narrative ?? []) {
      const clean = ensurePeriod(line);
      if (clean && !opening.some((o) => o.includes(clean.slice(0, 24)))) opening.push(clean);
    }
    if (opening.length) {
      chapters.push({ id: "opening", kicker: "Как звучит эта связь", paragraphs: opening });
    }

    const force: string[] = [];
    if (works.length) force.push(`Что усиливает: ${works.map(ensurePeriod).join(" ")}`);
    if (model.strongestResource?.trim()) {
      force.push(ensurePeriod(`Опора пары — ${model.strongestResource}`));
    }
    if (fails.length) force.push(`Что ослабляет: ${fails.map(ensurePeriod).join(" ")}`);
    if (model.mainRisk?.trim()) force.push(ensurePeriod(`Главный риск — ${model.mainRisk}`));
    if (frictionTags.length) {
      force.push(`Зоны трения: ${frictionTags.join("; ")}.`);
    }
    if (force.length) {
      chapters.push({ id: "force", kicker: "Что усиливает и что ослабляет", paragraphs: force });
    }

    const move: string[] = [];
    if (potentialLabel?.trim()) move.push(ensurePeriod(`${chrome.resultPotential}: ${potentialLabel}`));
    if (nextStep?.trim()) move.push(ensurePeriod(nextStep));
    for (const tip of (model.tips ?? []).slice(0, 3)) {
      const clean = ensurePeriod(tip);
      if (clean) move.push(clean);
    }
    if (move.length) {
      chapters.push({ id: "move", kicker: "Один ход для этой связи", paragraphs: move });
    }

    if (model.deepSections.length) {
      const deepParas = model.deepSections
        .slice(0, 4)
        .map((section) => {
          const bits = [section.title, section.takeaway, section.detail, section.risk, section.action]
            .map((x) => (x || "").trim())
            .filter(Boolean);
          return bits.length ? ensurePeriod(bits.join(". ").replace(/\.\./g, ".")) : "";
        })
        .filter(Boolean);
      if (deepParas.length) {
        chapters.push({ id: "deep", kicker: chrome.resultDeepTitle, paragraphs: deepParas });
      }
    }

    return chapters;
  }, [
    model.mainThought,
    model.narrative,
    model.strongestResource,
    model.mainRisk,
    model.tips,
    model.deepSections,
    works,
    fails,
    frictionTags,
    potentialLabel,
    nextStep,
    chrome.resultPotential,
    chrome.resultDeepTitle,
  ]);

  return (
    <div className={s.compatResultRoot} data-testid="compatibility-web-result">
      <ProductJourneyScene
        step={1}
        title="Пара"
        lead={model.scenarioSubtitle || chrome.resultTabsAria}
        motif="insight"
        testId="compat-journey-pair"
      >
        <div className={journeyStyles.pairHero}>
          <div className={journeyStyles.avatarGroup} aria-hidden>
            <span className={journeyStyles.avatar}>{initialFromName(name1)}</span>
            <span className={`${journeyStyles.avatar} ${journeyStyles.avatarOverlap}`}>
              {initialFromName(name2)}
            </span>
          </div>
          <div className={journeyStyles.pairMeta}>
            <p className={journeyStyles.pairTitle}>{pairLine}</p>
            <p className={journeyStyles.pairSub}>{model.scenarioTitle}</p>
            <p className={journeyStyles.pairScoreQuiet}>
              {model.scoreLabel || chrome.resultScoreTitle}: {model.score}%
              {metaChips.length ? ` · ${metaChips.slice(0, 2).join(" · ")}` : ""}
            </p>
          </div>
        </div>
      </ProductJourneyScene>

      <ProductJourneyScene
        step={2}
        title="История связи"
        lead="Рассказ о том, как вы звучите вместе — и почему именно так."
        motif="why"
        testId="compat-journey-story"
      >
        {storyChapters.length ? (
          <ProductNarrativeScroll
            theme={model.scoreLabel || model.scenarioTitle}
            chapters={storyChapters}
            softWhy={model.mainThought ? ensurePeriod(model.mainThought) : null}
            softWhyLabel={chrome.resultMainThought}
            testId="compat-narrative-scroll"
          />
        ) : (
          <DsBody muted>Пока мало сигналов для полного рассказа — открой другой сценарий или углуби профили.</DsBody>
        )}
      </ProductJourneyScene>

      <ProductJourneyScene
        step={3}
        title="Продолжение"
        lead="Другой угол той же пары — без потери контекста."
        motif="bridge"
        bridge
        testId="compat-journey-bridge"
      >
        <div className={journeyStyles.tabRow} aria-label={chrome.resultTabsAria}>
          {chrome.scenarioTabs.map((tab) => {
            const href = buildScenarioHref(tab.id);
            const active = activeScenarioId === tab.id;
            return (
              <button
                key={tab.id}
                type="button"
                className={`${journeyStyles.tabChip} ${active ? journeyStyles.tabChipActive : ""}`.trim()}
                aria-current={active ? "true" : undefined}
                onClick={() => onScenarioSwitch?.(tab.id, href)}
              >
                {tab.label}
              </button>
            );
          })}
        </div>
        <div className={journeyStyles.actionRow}>
          {onShare ? (
            <DsButton type="button" variant="secondary" onClick={onShare}>
              {chrome.resultShare}
            </DsButton>
          ) : null}
          {onSave ? (
            <DsButton type="button" variant="secondary" onClick={onSave}>
              {chrome.resultSave}
            </DsButton>
          ) : null}
        </div>
        {extra}
      </ProductJourneyScene>
    </div>
  );
}

export { potentialLabelFromScore } from "@/components/product-ui/compatibilityWebChrome";
