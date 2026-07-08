"use client";

import type { CSSProperties, ReactNode } from "react";
import { useMemo } from "react";
import { DsBody, DsEyebrow, DsRailPanel } from "@/design-system";
import {
  compatibilityWebChromeBundle,
  type CompatibilityWebChrome,
} from "@/components/product-ui/compatibilityWebChrome";
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
                  <span className={s.compatMetricFill} style={{ width: `${Math.min(100, Math.max(0, dimension.score))}%` }} />
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
  const hasLearningExtras = Boolean(model.mainThought || model.deepSections.length);

  return (
    <div className={s.compatResultRoot} data-testid="compatibility-web-result">
      <nav className={s.compatTabs} aria-label={chrome.resultTabsAria}>
        {chrome.scenarioTabs.map((tab) => {
          const href = buildScenarioHref(tab.id);
          const active = activeScenarioId === tab.id;
          return (
            <button
              key={tab.id}
              type="button"
              className={`${s.compatTab} ${active ? s.compatTabActive : ""}`.trim()}
              aria-current={active ? "true" : undefined}
              onClick={() => onScenarioSwitch?.(tab.id, href)}
            >
              {tab.label}
            </button>
          );
        })}
      </nav>

      <header className={s.compatHeader}>
        <div className={s.avatarGroup} aria-hidden>
          <span className={s.avatar}>{initialFromName(name1)}</span>
          <span className={`${s.avatar} ${s.avatarOverlap}`}>{initialFromName(name2)}</span>
        </div>
        <div>
          <p className={s.compatScore}>{model.score}%</p>
          <p className={s.compatScenario}>{model.scenarioTitle}</p>
          <p className={s.compatPairLine}>{pairLine}</p>
        </div>
        {metaChips.length ? (
          <div className={s.compatMetaChips}>
            {metaChips.map((chip) => (
              <span key={chip} className={s.compatMetaChip}>
                {chip}
              </span>
            ))}
          </div>
        ) : null}
      </header>

      <div className={s.compatBlocks}>
        {works.length ? (
          <section className={`${s.compatBlock} ${s.compatBlockWorks}`} aria-labelledby="compat-web-works">
            <DsEyebrow id="compat-web-works">{chrome.resultWorks}</DsEyebrow>
            <ul className={s.compatBullets}>
              {works.map((item) => (
                <li key={item} className={s.compatBullet}>
                  {item}
                </li>
              ))}
            </ul>
          </section>
        ) : null}

        {fails.length ? (
          <section className={`${s.compatBlock} ${s.compatBlockInset}`} aria-labelledby="compat-web-fails">
            <DsEyebrow id="compat-web-fails">{chrome.resultFails}</DsEyebrow>
            <ul className={s.compatBullets}>
              {fails.map((item) => (
                <li key={item} className={s.compatBullet}>
                  {item}
                </li>
              ))}
            </ul>
          </section>
        ) : null}

        {frictionTags.length ? (
          <section className={s.compatBlock} aria-labelledby="compat-web-friction">
            <DsEyebrow id="compat-web-friction">{chrome.resultFriction}</DsEyebrow>
            <div className={s.compatTagRow}>
              {frictionTags.map((tag) => (
                <span key={tag} className={s.compatFrictionTag}>
                  {tag}
                </span>
              ))}
            </div>
          </section>
        ) : null}

        <section className={`${s.compatBlock} ${s.compatBlockDark}`} aria-labelledby="compat-web-potential">
          <div className={s.compatPotential}>
            <div>
              <DsEyebrow onDark id="compat-web-potential">
                {chrome.resultPotential}
              </DsEyebrow>
              <p className={s.compatPotentialValue}>{potentialLabel}</p>
            </div>
            <span className={s.compatPotentialIcon} aria-hidden>
              ✦
            </span>
          </div>
        </section>

        {nextStep ? (
          <section className={`${s.compatBlock} ${s.compatBlockInset}`} aria-labelledby="compat-web-next">
            <DsEyebrow id="compat-web-next">{chrome.resultNextStep}</DsEyebrow>
            <p className={s.compatNextStep}>{nextStep}</p>
          </section>
        ) : null}

        {hasLearningExtras ? (
          <details className={s.compatLearningDetails}>
            <summary className={s.compatLearningSummary}>{chrome.resultDeepSummary}</summary>
            {model.mainThought ? (
              <section className={s.compatBlock} aria-labelledby="compat-web-thought">
                <DsEyebrow id="compat-web-thought">{chrome.resultMainThought}</DsEyebrow>
                <DsBody>{model.mainThought}</DsBody>
              </section>
            ) : null}

            {model.deepSections.length ? (
              <section className={s.compatBlock} aria-labelledby="compat-web-deep">
                <DsEyebrow id="compat-web-deep">{chrome.resultDeepTitle}</DsEyebrow>
                {model.deepSections.map((section) => (
                  <details
                    key={section.id}
                    open={false}
                    onToggle={(event) => {
                      if ((event.target as HTMLDetailsElement).open) onDeepOpen?.();
                    }}
                  >
                    <summary className={s.compatDeepSummary}>{section.title}</summary>
                    <DsBody size="sm">{section.takeaway}</DsBody>
                    {section.detail ? (
                      <DsBody size="sm" muted>
                        {section.detail}
                      </DsBody>
                    ) : null}
                  </details>
                ))}
              </section>
            ) : null}
          </details>
        ) : null}
      </div>

      <div className={s.compatActions}>
        <button type="button" className={s.compatActionSecondary} onClick={onShare}>
          {chrome.resultShare}
        </button>
        <button type="button" className={s.compatActionPrimary} onClick={onSave}>
          {chrome.resultSave}
        </button>
      </div>

      {extra}
    </div>
  );
}

export { potentialLabelFromScore } from "@/components/product-ui/compatibilityWebChrome";
