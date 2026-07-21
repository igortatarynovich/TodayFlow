"use client";

import type { ReactNode } from "react";
import Link from "next/link";
import { ProfileChartSection } from "@/components/profile/ProfileChartSection";
import type { ProfileLifeSphere } from "@/components/profile/ProfileLifeSection";
import { ProfilePortalDeepSection } from "@/components/profile/ProfilePortalDeepSection";
import type { ProfileQuickMapDeepProps, ProfileQuickMapScreenProps } from "@/components/profile/quickMap/ProfileQuickMapScreen";
import { ProfileV2MobileDepthJump } from "@/components/profile/v2/ProfileV2DepthRail";
import { ProfileV2SkySection } from "@/components/profile/v2/ProfileV2SkySection";
import {
  PROFILE_V2_COPY,
  type ProfileV2ZoneId,
} from "@/components/profile/v2/profileV2SystemCopy";
import type { ProfileV2LiveContext } from "@/lib/profilePage/buildProfileV2LiveContext";
import { profilePortraitFormingMessage } from "@/lib/profilePage/profilePortraitForming";
import { profileV2SphereCardLine } from "@/lib/profilePage/profileV2SpherePresentation";
import { buildProfileHeroQuote } from "@/lib/product-ui/profileWebFigmaHelpers";
import styles from "@/components/profile/v2/profileV2System.module.css";

export type ProfileV2SystemScreenProps = {
  model: ProfileQuickMapScreenProps["model"];
  live: ProfileV2LiveContext;
  identityPills?: string[];
  lifeSpheres?: ProfileLifeSphere[];
  deepExpanded?: boolean;
  deep?: ProfileQuickMapDeepProps | null;
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

function ZoneLabel({ id, title }: { id: string; title: string }) {
  return (
    <p id={id} className={styles.zoneLabel}>
      {title}
    </p>
  );
}

export function ProfileV2SystemScreen({
  model,
  live,
  identityPills = [],
  lifeSpheres,
  deepExpanded = false,
  deep,
  notices,
  onOpenBirthData,
  portraitForming = false,
  portraitFormingMessage: portraitFormingMessageProp = null,
}: ProfileV2SystemScreenProps) {
  const quote = portraitForming
    ? null
    : buildProfileHeroQuote(model.archetype, model.identitySummary);
  const formingMessage = portraitFormingMessageProp?.trim() || profilePortraitFormingMessage(null);
  const astroFacts = buildAstroFactsLine(model.frameworkAnchors);
  const helps = live.helps.length ? live.helps : model.thriveAreas.slice(0, 3);
  const heroPills = [
    ...identityPills,
    ...(live.elementLabel ? [live.elementLabel] : []),
  ];

  return (
    <div className={styles.pageRoot} data-testid="profile-v2-system">
      <ProfileV2MobileDepthJump />

      <div className={styles.mainColumn}>
        {notices}

        <div className={styles.topMeta}>
          <span className={styles.liveChip}>
            <span className={styles.liveDot} aria-hidden />
            {PROFILE_V2_COPY.liveBadge}
          </span>
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
            <h1 className={styles.heroTitle}>{PROFILE_V2_COPY.heroTitle}</h1>
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

          <aside className={styles.sideCard} data-testid="profile-v2-evidence-aside">
            <p className={styles.sideEyebrow}>{live.evidenceTitle}</p>
            <p className={styles.sideBody}>{live.evidenceBody}</p>
            <p className={styles.factHint}>
              {PROFILE_V2_COPY.zones.evidence.levelPrefix}: {live.observationAccuracyLabel}
            </p>
          </aside>
        </section>

        <section id={zoneDomId("identity")} className={styles.zone} aria-labelledby="profile-v2-identity-title">
          <header className={styles.zoneHeader}>
            <div>
              <ZoneLabel id="profile-v2-identity-title" title={PROFILE_V2_COPY.zones.identity.title} />
              <p className={styles.zoneLead}>{PROFILE_V2_COPY.zones.identity.lead}</p>
            </div>
          </header>
          <div className={styles.factGrid}>
            <article className={styles.factCard}>
              <p className={styles.factLabel}>{PROFILE_V2_COPY.zones.identity.cards.archetype}</p>
              <p className={styles.factValue}>{model.archetype}</p>
              {model.identitySummary ? (
                <p className={styles.factHint}>{model.identitySummary}</p>
              ) : null}
            </article>
            {astroFacts ? (
              <article className={styles.factCard}>
                <p className={styles.factLabel}>{PROFILE_V2_COPY.zones.identity.cards.astro}</p>
                <p className={styles.factValue}>{astroFacts}</p>
                <p className={styles.factHint}>{PROFILE_V2_COPY.zones.identity.astroHint}</p>
              </article>
            ) : null}
          </div>
        </section>

        <section id={zoneDomId("character")} className={styles.zone} aria-labelledby="profile-v2-character-title">
          <header className={styles.zoneHeader}>
            <div>
              <ZoneLabel id="profile-v2-character-title" title={PROFILE_V2_COPY.zones.character.title} />
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
              <p className={styles.characterPanelTitle}>{PROFILE_V2_COPY.zones.character.patterns}</p>
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
              <p className={styles.characterPanelTitle}>{PROFILE_V2_COPY.zones.character.forming}</p>
              <p className={styles.factHint}>{model.frameworkLead}</p>
            </article>
          ) : null}
        </section>

        <section id={zoneDomId("direction")} className={styles.zone} aria-labelledby="profile-v2-direction-title">
          <header className={styles.zoneHeader}>
            <div>
              <ZoneLabel id="profile-v2-direction-title" title={PROFILE_V2_COPY.zones.direction.title} />
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
              {lifeSpheres.map((sphere) => (
                <details key={sphere.id} className={styles.sphereCard}>
                  <summary className={styles.sphereSummary}>
                    <div className={styles.sphereSummaryMain}>
                      <p className={styles.sphereTitle}>{sphere.title}</p>
                      <p className={styles.sphereNeedLine}>{profileV2SphereCardLine(sphere)}</p>
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
              ))}
            </div>
          ) : null}
        </section>

        <section id={zoneDomId("evidence")} className={styles.zone} aria-labelledby="profile-v2-evidence-title">
          <header className={styles.zoneHeader}>
            <div>
              <ZoneLabel id="profile-v2-evidence-title" title={PROFILE_V2_COPY.zones.evidence.title} />
              <p className={styles.zoneLead}>{PROFILE_V2_COPY.zones.evidence.lead}</p>
            </div>
          </header>
          <article className={styles.decisionBlock} data-testid="profile-v2-evidence">
            <p className={styles.characterPanelTitle}>{live.evidenceTitle}</p>
            <p className={styles.factHint}>{live.evidenceBody}</p>
            {live.evidenceNextStep ? (
              <>
                <p className={styles.characterPanelTitle} style={{ marginTop: "0.85rem" }}>
                  {PROFILE_V2_COPY.zones.evidence.nextLabel}
                </p>
                <p className={styles.factHint}>{live.evidenceNextStep}</p>
              </>
            ) : null}
          </article>
          <p className={styles.zoneLead} style={{ marginTop: "1rem" }}>
            {PROFILE_V2_COPY.mapsCtaHint}{" "}
            <Link href="/maps/mood">{PROFILE_V2_COPY.mapsCta}</Link>
          </p>
        </section>

        {deep ? (
          <section
            id={zoneDomId("sources")}
            className={`${styles.zone} ${styles.skyZone}`.trim()}
            aria-labelledby="profile-v2-sources-title"
          >
            <header className={styles.zoneHeader}>
              <div>
                <ZoneLabel id="profile-v2-sources-title" title={PROFILE_V2_COPY.zones.sources.title} />
                <p className={styles.zoneLead}>{PROFILE_V2_COPY.zones.sources.lead}</p>
              </div>
            </header>
            <div className={styles.skyContent}>
              <ProfileV2SkySection
                natalPreview={deep.natalPreview}
                previewError={deep.previewError}
                onReloadPreview={deep.onReloadPreview}
                frameworkAnchors={model.frameworkAnchors}
                frameworkCards={model.frameworkCards}
              />
              <ProfilePortalDeepSection defaultOpen={false}>
                <p className={styles.zoneLead} style={{ marginBottom: "0.75rem" }}>
                  {PROFILE_V2_COPY.zones.sources.exploreHint}
                </p>
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
              {PROFILE_V2_COPY.zones.sources.updatedNote}
            </p>
          </section>
        ) : null}
      </div>
    </div>
  );
}
