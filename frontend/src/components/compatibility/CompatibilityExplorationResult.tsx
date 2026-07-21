"use client";

import Link from "next/link";
import { useEffect, useState, type CSSProperties, type ReactNode } from "react";
import type { CompatibilityExplorationModel } from "@/lib/buildCompatibilityExplorationModel";
import type { GuidanceCompatibilityPrefillInput } from "@/lib/guidanceCompatibilityPrefill";
import { stashGuidanceCompatibilityPrefill } from "@/lib/guidanceCompatibilityPrefill";
import { CompatibilityFunnelSection, type CompatibilityFunnelArtifact } from "@/components/compatibility/CompatibilityFunnelSection";
import {
  CompatibilityAccessDisclosure,
  type CompatibilityAccessDisclosureMeta,
} from "@/components/compatibility/CompatibilityAccessDisclosure";
import { dimensionsSectionTitle } from "@/lib/compatibilityScenarioMetrics";
import { HeroSmall } from "@/components/foundation/HeroSmall";
import { compatibilityScenarioSymbol } from "@/lib/compatibilityHeroSymbol";
import { recordRelationshipMapVisit } from "@/lib/relationshipMapStore";
import styles from "@/components/compatibility/CompatibilityExplorationResult.module.css";

type CompatibilityExplorationResultProps = {
  model: CompatibilityExplorationModel;
  personalizedSlot?: ReactNode;
  funnelArtifact?: CompatibilityFunnelArtifact | null;
  accessDisclosure?: CompatibilityAccessDisclosureMeta | null;
  guidancePrefill?: GuidanceCompatibilityPrefillInput | null;
  onGuidanceClick?: () => void;
  onRefresh?: () => void;
  refreshing?: boolean;
  onScenarioSwitch?: (scenarioId: string, href: string) => void;
  onDeepOpen?: () => void;
};

function DimensionCard({
  emoji,
  label,
  score,
  quip,
  delayMs,
  playful,
}: {
  emoji: string;
  label: string;
  score: number;
  quip?: string;
  delayMs: number;
  playful?: boolean;
}) {
  const [visible, setVisible] = useState(false);
  useEffect(() => {
    const t = window.setTimeout(() => setVisible(true), delayMs);
    return () => window.clearTimeout(t);
  }, [delayMs]);

  const pct = Math.min(100, Math.max(0, score));

  return (
    <div className={`${styles.dimensionCard} ${playful ? styles.dimensionCardPlayful : ""}`}>
      <div className={styles.dimensionHead}>
        <span className={styles.dimensionEmoji}>{emoji}</span>
        <span className={styles.dimensionLabel}>{label}</span>
      </div>
      <p className={styles.dimensionScore}>{score}%</p>
      <div className={styles.dimensionBar} aria-hidden>
        <span className={styles.dimensionBarFill} style={{ width: visible ? `${pct}%` : "0%" }} />
      </div>
      {quip ? <p className={styles.dimensionQuip}>{quip}</p> : null}
    </div>
  );
}

export function CompatibilityExplorationResult({
  model,
  personalizedSlot,
  funnelArtifact,
  accessDisclosure,
  guidancePrefill,
  onGuidanceClick,
  onRefresh,
  refreshing,
  onScenarioSwitch,
  onDeepOpen,
}: CompatibilityExplorationResultProps) {
  const [deepOpen, setDeepOpen] = useState(false);
  useEffect(() => {
    recordRelationshipMapVisit({
      label: model.pairLine,
      scenarioId: model.scenarioId,
      pairLine: model.pairLine,
      theme: model.scenarioTitle,
    });
  }, [model.pairLine, model.scenarioId, model.scenarioTitle]);
  const ringStyle = { "--ce-score-pct": model.score } as CSSProperties;
  const toneClass = styles[`tone_${model.tone}`] ?? styles.tone_romantic;
  const isPlayful = model.presentation === "playful";

  const openDeep = () => {
    setDeepOpen(true);
    onDeepOpen?.();
  };

  return (
    <div className={`${styles.root} ${toneClass} ${isPlayful ? styles.rootPlayful : ""}`}>
      <HeroSmall
        symbol={compatibilityScenarioSymbol(model.scenarioId)}
        kicker={isPlayful ? "Эксперимент" : "Исследование"}
        title={model.scenarioPoster}
        meta={model.scenarioSubtitle}
        flush
        className={styles.posterHero}
      />
      {isPlayful && model.playfulDisclaimer ? (
        <p className={styles.playfulDisclaimer}>{model.playfulDisclaimer}</p>
      ) : null}

      <section className={styles.hero}>
        <p className={styles.pairLine}>{model.pairLine}</p>
        <div className={styles.heroGrid}>
          <div className={styles.heroMain}>
            <p className={styles.mainThoughtLabel}>{isPlayful ? "Вердикт" : "Главная мысль"}</p>
            <p className={styles.mainThought}>{model.mainThought}</p>
            <p className={styles.scoreLabel}>{model.scoreLabel}</p>
          </div>
          <div className={styles.ringWrap} style={ringStyle}>
            <div className={styles.ringInner}>
              <span className={styles.ringValue}>{model.score}%</span>
              {isPlayful ? <span className={styles.ringPlayfulHint}>шуточный индекс</span> : null}
            </div>
          </div>
        </div>
      </section>

      <section className={styles.dimensions}>
        <h3 className={styles.blockTitle}>
          {dimensionsSectionTitle(model.scenarioId, isPlayful)}
        </h3>
        <div className={styles.dimensionsGrid}>
          {model.dimensions.map((d, i) => (
            <DimensionCard
              key={d.id}
              emoji={d.emoji}
              label={d.label}
              score={d.score}
              quip={d.quip}
              delayMs={120 + i * 90}
              playful={isPlayful}
            />
          ))}
        </div>
      </section>

      {isPlayful ? (
        <>
          {model.narrative.length ? (
            <section className={styles.playfulPunchline}>
              {model.narrative.map((p, i) => (
                <p key={i} className={styles.playfulPunchlineText}>
                  {p}
                </p>
              ))}
            </section>
          ) : null}
          <section className={styles.insights}>
            <div className={styles.insightCard}>
              <p className={styles.insightLabel}>🏆 Лидер stat</p>
              <p className={styles.insightBody}>{model.strongestResource}</p>
            </div>
            <div className={`${styles.insightCard} ${styles.insightCardRisk}`}>
              <p className={styles.insightLabel}>📉 Слабое звено</p>
              <p className={styles.insightBody}>{model.mainRisk}</p>
            </div>
          </section>
        </>
      ) : (
        <>
          {model.narrative.length ? (
            <section className={styles.narrative}>
              <h3 className={styles.blockTitle}>Что произойдёт, если сценарий случится завтра?</h3>
              {model.narrative.map((p, i) => (
                <p key={i} className={styles.narrativeP}>
                  {p}
                </p>
              ))}
            </section>
          ) : null}

          <section className={styles.insights}>
            <div className={styles.insightCard}>
              <p className={styles.insightLabel}>💎 Самый сильный ресурс</p>
              <p className={styles.insightBody}>{model.strongestResource}</p>
            </div>
            <div className={`${styles.insightCard} ${styles.insightCardRisk}`}>
              <p className={styles.insightLabel}>⚠ Главный риск</p>
              <p className={styles.insightBody}>{model.mainRisk}</p>
            </div>
          </section>

          {model.tips.length ? (
            <section className={styles.tips}>
              <h3 className={styles.blockTitle}>Что поможет именно вам</h3>
              <ul className={styles.tipsList}>
                {model.tips.map((tip) => (
                  <li key={tip}>{tip}</li>
                ))}
              </ul>
            </section>
          ) : null}

          {personalizedSlot ? <section className={styles.personalized}>{personalizedSlot}</section> : null}

          <CompatibilityAccessDisclosure access={accessDisclosure} />

          {funnelArtifact ? <CompatibilityFunnelSection artifact={funnelArtifact} /> : null}

          {!deepOpen && accessDisclosure?.tier !== "guest" ? (
            <div className={styles.deepCta}>
              <button type="button" className="orbit-button orbit-button-primary" onClick={openDeep}>
                Посмотреть глубже
              </button>
              <p className={styles.deepCtaHint}>Длинный разбор — только если захочешь копать дальше.</p>
            </div>
          ) : null}
          {deepOpen && accessDisclosure?.tier !== "guest" ? (
            <section className={styles.deepJournal}>
              <h3 className={styles.blockTitle}>Глубокий разбор</h3>
              <div className={styles.deepStack}>
                {model.deepSections.map((section) => (
                  <details key={section.id} className={styles.deepSection}>
                    <summary className={styles.deepSummary}>
                      {section.title}
                      {section.subtitle ? <span className={styles.deepSummarySub}>{section.subtitle}</span> : null}
                    </summary>
                    <div className={styles.deepBody}>
                      <p className={styles.deepTakeaway}>{section.takeaway}</p>
                      {section.detail ? <p className={styles.deepDetail}>{section.detail}</p> : null}
                      {section.risk ? (
                        <div className={styles.deepRisk}>
                          <strong>Риск:</strong> {section.risk}
                        </div>
                      ) : null}
                      {section.action ? (
                        <div className={styles.deepAction}>
                          <strong>Как действовать:</strong> {section.action}
                        </div>
                      ) : null}
                    </div>
                  </details>
                ))}
              </div>

              {model.roles ? (
                <div className={styles.rolesGrid}>
                  <div className={styles.roleCard}>
                    <p className={styles.roleTitle}>Ты</p>
                    <ul>
                      {model.roles.you_bullets.map((line) => (
                        <li key={line}>{line}</li>
                      ))}
                    </ul>
                  </div>
                  <div className={styles.roleCard}>
                    <p className={styles.roleTitle}>Партнёр</p>
                    <ul>
                      {model.roles.partner_bullets.map((line) => (
                        <li key={line}>{line}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              ) : null}
            </section>
          ) : null}
        </>
      )}

      {model.continuationScenarios.length ? (
        <section className={styles.continuation}>
          <h3 className={styles.blockTitle}>
            {isPlayful ? "Попробуйте другой шуточный сценарий" : "Попробуйте посмотреть вашу пару в других сценариях"}
          </h3>
          <p className={styles.continuationLead}>
            {isPlayful ? "Это эксперимент — можно переключить тему." : "Это не конец — продолжение исследования."}
          </p>
          <div className={styles.continuationGrid}>
            {model.continuationScenarios.map((s) => (
              <Link
                key={s.id}
                href={s.href}
                className={`${styles.continuationCard} ${styles[`cont_${s.tone}`] ?? ""}`}
                onClick={() => onScenarioSwitch?.(s.id, s.href)}
              >
                <span className={styles.continuationEmoji}>{s.emoji}</span>
                <span className={styles.continuationTitle}>{s.title}</span>
                <span className={styles.continuationHook}>{s.hook}</span>
              </Link>
            ))}
          </div>
        </section>
      ) : null}

      <div className={styles.footerActions}>
        {onRefresh ? (
          <button type="button" className="orbit-button orbit-button-secondary orbit-button-sm" disabled={refreshing} onClick={onRefresh}>
            {refreshing ? "Обновляю…" : "Обновить разбор"}
          </button>
        ) : null}
        <Link
          href="/tarot?from=compatibility"
          className="orbit-button orbit-button-primary orbit-button-sm"
          style={{ textDecoration: "none" }}
          onClick={() => {
            if (guidancePrefill) stashGuidanceCompatibilityPrefill(guidancePrefill);
            onGuidanceClick?.();
          }}
        >
          Задать вопрос про эту пару
        </Link>
        <Link href="/compatibility" className="orbit-button orbit-button-secondary orbit-button-sm" style={{ textDecoration: "none" }}>
          К исследованию
        </Link>
      </div>
    </div>
  );
}
