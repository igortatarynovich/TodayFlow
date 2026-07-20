"use client";

import type { CSSProperties, ReactNode } from "react";
import { useState } from "react";
import { ProfileChartSection } from "@/components/profile/ProfileChartSection";
import { ProfileCumInsightsBlock } from "@/components/profile/ProfileCumInsightsBlock";
import type { ProfileLifeSphere } from "@/components/profile/ProfileLifeSection";
import { ProfileLivingMapsSection } from "@/components/profile/ProfileLivingMapsSection";
import { ProfilePortalDeepSection } from "@/components/profile/ProfilePortalDeepSection";
import { ProfileRelationshipInsightsBlock } from "@/components/profile/ProfileRelationshipInsightsBlock";
import type { ProfileQuickMapDeepProps, ProfileQuickMapScreenProps } from "@/components/profile/quickMap/ProfileQuickMapScreen";
import { ProfileV2MyDays } from "@/components/profile/v2/ProfileV2MyDays";
import { ProfileV2SkySection } from "@/components/profile/v2/ProfileV2SkySection";
import {
  PROFILE_V2_COPY,
  PROFILE_V2_DEPTH_NAV,
  type ProfileV2ZoneId,
} from "@/components/profile/v2/profileV2SystemCopy";
import type { ProfileV2LiveContext } from "@/lib/profilePage/buildProfileV2LiveContext";
import {
  profilePortraitFormingMessage,
} from "@/lib/profilePage/profilePortraitForming";
import {
  profileV2SphereCardLine,
  profileV2SphereProgressPercent,
} from "@/lib/profilePage/profileV2SpherePresentation";
import { buildProfileHeroQuote } from "@/lib/product-ui/profileWebFigmaHelpers";
import type { CompactUserModel } from "@/lib/types";
import styles from "@/components/profile/v2/profileV2System.module.css";

export type ProfileV2SystemScreenProps = {
  model: ProfileQuickMapScreenProps["model"];
  live: ProfileV2LiveContext;
  identityPills?: string[];
  lifeSpheres?: ProfileLifeSphere[];
  cum?: CompactUserModel | null;
  deepExpanded?: boolean;
  deep?: ProfileQuickMapDeepProps | null;
  livingObservation?: string | null;
  notices?: ReactNode;
  onOpenBirthData: () => void;
  portraitForming?: boolean;
  portraitFormingMessage?: string | null;
};

function zoneDomId(zone: ProfileV2ZoneId): string {
  return `profile-v2-${zone}`;
}

function buildAstroFactsLine(anchors: ProfileQuickMapScreenProps["model"]["frameworkAnchors"]): string {
  const sun = anchors.find((item) => item.id === "sun")?.label.replace(/^солнце\s*/i, "") ?? "";
  const moon = anchors.find((item) => item.id === "moon")?.label.replace(/^луна\s*/i, "") ?? "";
  if (sun && moon) {
    const sunSign = sun.replace(/\s*в\s*/i, " · ").trim();
    const moonSign = moon.replace(/\s*в\s*/i, " · ").trim();
    return `${sunSign} · ${moonSign}`.replace(/·\s*·/g, "·").trim();
  }
  return anchors
    .slice(0, 2)
    .map((item) => item.label)
    .join(" · ");
}

export function ProfileV2SystemScreen({
  model,
  live,
  identityPills = [],
  lifeSpheres,
  cum,
  deepExpanded = false,
  deep,
  livingObservation,
  notices,
  onOpenBirthData,
  portraitForming = false,
  portraitFormingMessage: portraitFormingMessageProp = null,
}: ProfileV2SystemScreenProps) {
  const [activeZone, setActiveZone] = useState<ProfileV2ZoneId>("facts");

  const quote = portraitForming
    ? null
    : buildProfileHeroQuote(model.archetype, model.identitySummary);
  const formingMessage = portraitFormingMessageProp?.trim() || profilePortraitFormingMessage(null);
  const astroFacts = buildAstroFactsLine(model.frameworkAnchors);
  const helps = live.helps.length ? live.helps : model.thriveAreas.slice(0, 3);
  const awarenessPercent = live.awarenessPercent;
  const awarenessDeg = `${Math.round((awarenessPercent / 100) * 360)}deg`;
  const heroPills = [
    ...identityPills,
    ...(live.elementLabel ? [live.elementLabel] : []),
  ];

  return (
    <div className={styles.pageRoot}>
      <div className={styles.shell} data-testid="profile-v2-system">
      <nav className={styles.depthNav} aria-label="Глубина профиля">
        <div className={styles.depthNavInner}>
          <div className={styles.depthRail} aria-hidden />
          {PROFILE_V2_DEPTH_NAV.map((item) => (
            <a
              key={item.id}
              href={`#${zoneDomId(item.id)}`}
              className={styles.depthStep}
              onClick={() => setActiveZone(item.id)}
            >
              <span
                className={`${styles.depthStepBadge} ${activeZone === item.id ? styles.depthStepBadgeActive : ""}`.trim()}
              >
                {item.step}
              </span>
              <span>
                <p className={styles.depthStepTitle}>{item.title}</p>
                <p className={styles.depthStepHint}>{item.hint}</p>
              </span>
            </a>
          ))}
        </div>
      </nav>

      <div className={styles.mainColumn}>
        {notices}

        <div className={styles.topMeta}>
          <span className={styles.liveChip}>
            <span className={styles.liveDot} aria-hidden />
            {PROFILE_V2_COPY.liveBadge}
          </span>
          <span className={styles.liveChip}>{live.updatedLabel}</span>
          <button type="button" className={styles.birthDataBtn} onClick={onOpenBirthData}>
            Данные рождения
          </button>
        </div>

        {portraitForming ? (
          <div className={styles.zone} data-testid="profile-portrait-forming" role="status">
            <p className={styles.zoneLead}>{formingMessage}</p>
          </div>
        ) : null}

        <section className={styles.heroGrid} aria-label="Профиль">
          <article className={styles.heroCard}>
            <p className={styles.heroEyebrow}>{PROFILE_V2_COPY.heroEyebrow}</p>
            <h2 className={styles.heroTitle}>{PROFILE_V2_COPY.heroTitle}</h2>
            {quote ? <blockquote className={styles.heroQuote}>{quote}</blockquote> : null}
            {heroPills.length ? (
              <div className={styles.heroPills}>
                {heroPills.map((pill) => (
                  <span key={pill} className={styles.heroPill}>
                    {pill}
                  </span>
                ))}
              </div>
            ) : null}
          </article>

          <aside className={styles.sideCard}>
            <div className={styles.awarenessRow}>
              <div
                className={styles.awarenessRing}
                style={{ "--awareness-deg": awarenessDeg } as CSSProperties}
                aria-hidden
              >
                <div className={styles.awarenessRingInner}>{awarenessPercent}%</div>
              </div>
              <div>
                <p className={styles.sideEyebrow}>{PROFILE_V2_COPY.awarenessTitle}</p>
                <p className={styles.sideBody}>{PROFILE_V2_COPY.awarenessLead}</p>
              </div>
            </div>
            <div className={styles.anchorBlock}>
              <p className={styles.anchorTitle}>{live.stoneCardTitle}</p>
              <p className={styles.anchorBody}>{live.stoneCardBody}</p>
            </div>
            <div className={styles.anchorBlock}>
              <p className={styles.anchorTitle}>{live.supportsCardTitle}</p>
              <p className={styles.anchorBody}>{live.supportsCardBody}</p>
            </div>
          </aside>
        </section>

        <section id={zoneDomId("facts")} className={styles.zone} aria-labelledby="profile-v2-facts-title">
          <header className={styles.zoneHeader}>
            <p className={styles.zoneStep}>01</p>
            <div>
              <h3 id="profile-v2-facts-title" className={styles.zoneTitle}>
                {PROFILE_V2_COPY.zones.facts.title}
              </h3>
              <p className={styles.zoneLead}>{PROFILE_V2_COPY.zones.facts.lead}</p>
            </div>
            <span className={styles.liveChip}>
              <span className={styles.liveDot} aria-hidden />
              {live.updatedLabel.replace(PROFILE_V2_COPY.updatedPrefix, "обновлено")}
            </span>
          </header>
          <div className={styles.factGrid}>
            <article className={styles.factCard}>
              <p className={styles.factLabel}>{PROFILE_V2_COPY.zones.facts.cards.archetype}</p>
              <p className={styles.factValue}>{model.archetype}</p>
              {model.identitySummary ? (
                <p className={styles.factHint}>{model.identitySummary}</p>
              ) : null}
            </article>
            <article className={styles.factCard}>
              <p className={styles.factLabel}>{PROFILE_V2_COPY.zones.facts.cards.astro}</p>
              <p className={styles.factValue}>{astroFacts || "—"}</p>
              <p className={styles.factHint}>{PROFILE_V2_COPY.zones.facts.astroHint}</p>
            </article>
            <article className={styles.factCard}>
              <p className={styles.factLabel}>{PROFILE_V2_COPY.zones.facts.cards.awareness}</p>
              <p className={styles.factValue}>
                {awarenessPercent}%
                {live.awarenessDeltaLabel ? ` · ${live.awarenessDeltaLabel.replace(" за 30 дн", "")}` : ""}
              </p>
              <div className={styles.progressBar} aria-hidden>
                <div className={styles.progressFill} style={{ width: `${awarenessPercent}%` }} />
              </div>
            </article>
            <article className={styles.factCard}>
              <p className={styles.factLabel}>{PROFILE_V2_COPY.zones.facts.cards.anchors}</p>
              <p className={styles.factValue}>{live.dailyAnchors.line}</p>
              <p className={styles.factHint}>{PROFILE_V2_COPY.zones.facts.anchorsHint}</p>
            </article>
          </div>
        </section>

        <section id={zoneDomId("character")} className={styles.zone} aria-labelledby="profile-v2-character-title">
          <header className={styles.zoneHeader}>
            <p className={styles.zoneStep}>02</p>
            <div>
              <h3 id="profile-v2-character-title" className={styles.zoneTitle}>
                {PROFILE_V2_COPY.zones.character.title}
              </h3>
              <p className={styles.zoneLead}>{PROFILE_V2_COPY.zones.character.lead}</p>
            </div>
          </header>
          <div className={styles.characterGrid}>
            {model.strengthens.length ? (
              <article className={styles.characterPanel}>
                <p className={styles.characterPanelTitle}>{PROFILE_V2_COPY.zones.character.strengthens}</p>
                <ul className={styles.bulletList}>
                  {model.strengthens.map((item) => (
                    <li key={item} className={styles.bulletItem}>
                      <span className={styles.bulletMark} aria-hidden>
                        ✓
                      </span>
                      {item}
                    </li>
                  ))}
                </ul>
              </article>
            ) : null}
            {model.drains.length ? (
              <article className={styles.characterPanel}>
                <p className={styles.characterPanelTitle}>{PROFILE_V2_COPY.zones.character.drains}</p>
                <ul className={styles.bulletList}>
                  {model.drains.map((item) => (
                    <li key={item} className={styles.bulletItem}>
                      <span className={`${styles.bulletMark} ${styles.bulletMarkMuted}`.trim()} aria-hidden>
                        •
                      </span>
                      {item}
                    </li>
                  ))}
                </ul>
              </article>
            ) : null}
          </div>
          {helps.length ? (
            <article className={styles.characterPanel} style={{ marginTop: "1rem" }}>
              <p className={styles.characterPanelTitle}>{PROFILE_V2_COPY.zones.character.helps}</p>
              <ul className={styles.bulletList}>
                {helps.map((item) => (
                  <li key={item} className={styles.bulletItem}>
                    <span className={styles.bulletMark} aria-hidden>
                      ◆
                    </span>
                    {item}
                  </li>
                ))}
              </ul>
            </article>
          ) : null}
          {model.decisionStyle ? (
            <article className={styles.decisionBlock}>
              <p className={styles.characterPanelTitle}>{PROFILE_V2_COPY.zones.character.decisions}</p>
              <p className={styles.factHint}>{model.decisionStyle}</p>
            </article>
          ) : null}
          {model.perceivedAs.length ? (
            <article className={styles.characterPanel} style={{ marginTop: "1rem" }}>
              <p className={styles.characterPanelTitle}>Повторяющиеся паттерны</p>
              <ul className={styles.bulletList}>
                {model.perceivedAs.map((item) => (
                  <li key={item} className={styles.bulletItem}>
                    <span className={`${styles.bulletMark} ${styles.bulletMarkMuted}`.trim()} aria-hidden>
                      ◦
                    </span>
                    {item}
                  </li>
                ))}
              </ul>
            </article>
          ) : null}
          {model.frameworkLead ? (
            <article className={styles.decisionBlock} style={{ marginTop: "1rem" }}>
              <p className={styles.characterPanelTitle}>Что меняется сейчас</p>
              <p className={styles.factHint}>{model.frameworkLead}</p>
            </article>
          ) : null}
        </section>

        <section id={zoneDomId("direction")} className={styles.zone} aria-labelledby="profile-v2-direction-title">
          <header className={styles.zoneHeader}>
            <p className={styles.zoneStep}>03</p>
            <div>
              <h3 id="profile-v2-direction-title" className={styles.zoneTitle}>
                {PROFILE_V2_COPY.zones.direction.title}
              </h3>
              <p className={styles.zoneLead}>{PROFILE_V2_COPY.zones.direction.lead}</p>
            </div>
          </header>
          {model.lifeMission ? (
            <article className={styles.missionCard}>
              <p className={styles.factLabel}>{PROFILE_V2_COPY.zones.direction.missionLabel}</p>
              <p className={styles.missionText}>{model.lifeMission}</p>
            </article>
          ) : null}
          {lifeSpheres?.length ? (
            <div className={styles.sphereGrid}>
              {lifeSpheres.map((sphere) => {
                const progress = profileV2SphereProgressPercent(sphere.id, awarenessPercent);
                return (
                  <details key={sphere.id} className={styles.sphereCard}>
                    <summary className={styles.sphereSummary}>
                      <div className={styles.sphereSummaryMain}>
                        <p className={styles.sphereTitle}>{sphere.title}</p>
                        <p className={styles.sphereNeedLine}>{profileV2SphereCardLine(sphere)}</p>
                        <div className={styles.sphereProgressTrack} aria-hidden>
                          <span className={styles.sphereProgressFill} style={{ width: `${progress}%` }} />
                        </div>
                      </div>
                      <span className={styles.sphereChevron} aria-hidden>
                        ›
                      </span>
                    </summary>
                    <div className={styles.sphereDetails}>
                      <p className={styles.sphereDetailLabel}>Как проявляется</p>
                      <p className={styles.sphereBody}>{sphere.how}</p>
                      <p className={styles.sphereDetailLabel}>Нужно</p>
                      <p className={styles.sphereMeta}>{sphere.need}</p>
                      <p className={styles.sphereDetailLabel}>Риск</p>
                      <p className={styles.sphereMeta}>{sphere.risk}</p>
                      <p className={styles.sphereDetailLabel}>Включает</p>
                      <p className={styles.sphereMeta}>{sphere.turnsOn}</p>
                    </div>
                  </details>
                );
              })}
            </div>
          ) : null}
        </section>

        <section id={zoneDomId("history")} className={styles.zone} aria-labelledby="profile-v2-history-title">
          <header className={styles.zoneHeader}>
            <p className={styles.zoneStep}>04</p>
            <div>
              <h3 id="profile-v2-history-title" className={styles.zoneTitle}>
                {PROFILE_V2_COPY.zones.history.title}
              </h3>
              <p className={styles.zoneLead}>{PROFILE_V2_COPY.zones.history.lead}</p>
            </div>
          </header>
          <div className={styles.historyStack}>
            <ProfileV2MyDays />
            <ProfileLivingMapsSection variant="quickMap" livingObservation={livingObservation} />
            <div className={styles.historyStackWide}>
              <ProfileRelationshipInsightsBlock cum={cum} />
            </div>
            <div className={styles.historyStackWide}>
              <ProfileCumInsightsBlock cum={cum} />
            </div>
          </div>
        </section>

        {deep ? (
          <section
            id={zoneDomId("sky")}
            className={`${styles.zone} ${styles.skyZone}`.trim()}
            aria-labelledby="profile-v2-sky-title"
          >
            <header className={styles.zoneHeader}>
              <p className={styles.zoneStep}>05</p>
              <div>
                <h3 id="profile-v2-sky-title" className={styles.zoneTitle}>
                  {PROFILE_V2_COPY.zones.sky.title}
                </h3>
                <p className={styles.zoneLead}>{PROFILE_V2_COPY.zones.sky.lead}</p>
              </div>
            </header>
            <div className={styles.skyContent}>
              <ProfileV2SkySection
                natalPreview={deep.natalPreview}
                previewError={deep.previewError}
                onReloadPreview={deep.onReloadPreview}
                updatedLabel={live.updatedLabel}
              />
              <ProfilePortalDeepSection defaultOpen={false}>
                <ProfileChartSection
                  natalPreview={deep.natalPreview}
                  coreNumerology={deep.coreNumerology}
                  previewError={deep.previewError}
                  onReloadPreview={deep.onReloadPreview}
                  lifeMapSections={deep.lifeMapSections}
                  fullChartOpen={deepExpanded}
                />
              </ProfilePortalDeepSection>
            </div>
            <p className={styles.zoneLead} style={{ marginTop: "1rem" }}>
              {PROFILE_V2_COPY.zones.sky.updatedNote}
            </p>
          </section>
        ) : null}
      </div>
    </div>
    </div>
  );
}
