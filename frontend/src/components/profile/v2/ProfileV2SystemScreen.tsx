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
import { ArchetypeSymbol } from "@/components/visualIdentity/ArchetypeSymbol";
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
  const journey = live.journey;
  const formingMessage = portraitFormingMessageProp?.trim() || profilePortraitFormingMessage(null);
  const helps = live.helps;

  const recognitionName = journey.recognitionName || model.archetype || null;
  const recognitionLine = portraitForming
    ? null
    : journey.recognitionLine || buildProfileHeroQuote(model.archetype, model.identitySummary);
  const symbolSeed = journey.archetypeSeed || model.archetype || null;

  const whySelected = journey.whySelectedBy;
  const whyInfluenced = journey.whyInfluencedBy;
  const hasWhy =
    whySelected.length > 0 ||
    whyInfluenced.length > 0 ||
    Boolean(journey.whyHonesty) ||
    Boolean(live.evidenceBody);
  const node = journey.node;
  const effortVector = journey.effortVector;
  const bridgeLine = journey.bridgeLine;
  const showCharacterMore =
    Boolean(model.strengthens.length || model.drains.length || helps.length || model.decisionStyle || model.perceivedAs.length);

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

        <section
          id={zoneDomId("recognition")}
          className={styles.journeyHero}
          aria-labelledby="profile-v2-recognition-title"
          data-testid="profile-v2-recognition"
        >
          <div className={styles.journeyHeroVisual} aria-hidden={symbolSeed ? undefined : true}>
            {symbolSeed ? (
              <div className={styles.journeySymbolFrame}>
                <ArchetypeSymbol seed={symbolSeed} size={112} stroke="#5b4630" />
              </div>
            ) : null}
          </div>
          <div className={styles.journeyHeroCopy}>
            <p className={styles.heroEyebrow}>{PROFILE_V2_COPY.heroEyebrow}</p>
            {recognitionName ? (
              <h1 id="profile-v2-recognition-title" className={styles.journeyHeroTitle}>
                {recognitionName}
              </h1>
            ) : (
              <h1 id="profile-v2-recognition-title" className={styles.journeyHeroTitle}>
                {PROFILE_V2_COPY.zones.recognition.title}
              </h1>
            )}
            {recognitionLine ? (
              <p className={styles.journeyRecognitionLine} data-testid="profile-v2-recognition-line">
                {recognitionLine}
              </p>
            ) : null}
            {heroPills.length ? (
              <div className={styles.heroPills}>
                {heroPills.map((pill) => (
                  <span key={pill} className={styles.heroPill}>
                    {pill}
                  </span>
                ))}
              </div>
            ) : null}
          </div>
        </section>

        {hasWhy ? (
          <section
            id={zoneDomId("why")}
            className={styles.zone}
            aria-labelledby="profile-v2-why-title"
            data-testid="profile-v2-why"
          >
            <header className={styles.zoneHeader}>
              <div>
                <ZoneLabel
                  id="profile-v2-why-title"
                  title={journey.whyTitle || PROFILE_V2_COPY.zones.why.title}
                />
              </div>
            </header>

            {whySelected.length ? (
              <div className={styles.whyBlock}>
                <p className={styles.whyBlockLabel}>{PROFILE_V2_COPY.zones.why.selectedLabel}</p>
                <ul className={styles.whyList}>
                  {whySelected.map((row) => (
                    <li key={row.id} className={styles.whyItemSelected}>
                      {row.label}
                    </li>
                  ))}
                </ul>
              </div>
            ) : null}

            {whyInfluenced.length ? (
              <div className={styles.whyBlock}>
                <p className={styles.whyBlockLabel}>{PROFILE_V2_COPY.zones.why.influencedLabel}</p>
                <ul className={styles.whyList}>
                  {whyInfluenced.map((row) => (
                    <li key={row.id} className={styles.whyItemInfluenced}>
                      {row.label}
                    </li>
                  ))}
                </ul>
              </div>
            ) : null}

            <article className={styles.decisionBlock} data-testid="profile-v2-evidence">
              <p className={styles.characterPanelTitle}>
                {journey.whyHonesty
                  ? PROFILE_V2_COPY.zones.why.honestyFallbackTitle
                  : live.evidenceTitle}
              </p>
              <p className={styles.factHint}>{journey.whyHonesty || live.evidenceBody}</p>
              <p className={styles.factHint} style={{ marginTop: "0.5rem" }}>
                {PROFILE_V2_COPY.zones.evidence.levelPrefix}: {live.observationAccuracyLabel}
              </p>
              {live.evidenceNextStep ? (
                <>
                  <p className={styles.characterPanelTitle} style={{ marginTop: "0.85rem" }}>
                    {PROFILE_V2_COPY.zones.evidence.nextLabel}
                  </p>
                  <p className={styles.factHint}>{live.evidenceNextStep}</p>
                </>
              ) : null}
            </article>
          </section>
        ) : null}

        {node ? (
          <section
            id={zoneDomId("insight")}
            className={styles.zone}
            aria-labelledby="profile-v2-insight-title"
            data-testid="profile-v2-insight"
          >
            <header className={styles.zoneHeader}>
              <div>
                <ZoneLabel id="profile-v2-insight-title" title={PROFILE_V2_COPY.zones.insight.title} />
              </div>
            </header>
            <article className={styles.insightCard}>
              <p className={styles.insightKind}>{node.kind}</p>
              <h2 className={styles.insightTitle}>{node.title}</h2>
              <p className={styles.insightBody}>{node.insight}</p>
              {node.groundedOn.length ? (
                <div className={styles.insightMeta}>
                  <p className={styles.whyBlockLabel}>{PROFILE_V2_COPY.zones.insight.groundedLabel}</p>
                  <ul className={styles.whyList}>
                    {node.groundedOn.map((g) => (
                      <li key={g.id || g.label} className={styles.whyItemInfluenced}>
                        {g.label}
                      </li>
                    ))}
                  </ul>
                </div>
              ) : null}
              {node.help ? (
                <div className={styles.insightMeta}>
                  <p className={styles.whyBlockLabel}>{PROFILE_V2_COPY.zones.insight.helpLabel}</p>
                  <p className={styles.factHint}>{node.help}</p>
                </div>
              ) : null}
              {node.livingEvidence.length ? (
                <div className={styles.insightMeta} data-testid="profile-v2-living-adjacent">
                  <p className={styles.whyBlockLabel}>{PROFILE_V2_COPY.zones.insight.livingLabel}</p>
                  <p className={styles.livingNote}>{PROFILE_V2_COPY.zones.insight.livingNote}</p>
                  <ul className={styles.livingQuotes}>
                    {node.livingEvidence.map((q) => (
                      <li key={q} className={styles.livingQuote}>
                        «{q}»
                      </li>
                    ))}
                  </ul>
                </div>
              ) : null}
            </article>
          </section>
        ) : null}

        {effortVector ? (
          <section
            id={zoneDomId("effort")}
            className={styles.zone}
            aria-labelledby="profile-v2-effort-title"
            data-testid="profile-v2-effort"
          >
            <header className={styles.zoneHeader}>
              <div>
                <ZoneLabel id="profile-v2-effort-title" title={PROFILE_V2_COPY.zones.effort.title} />
                <p className={styles.zoneLead}>{PROFILE_V2_COPY.zones.effort.lead}</p>
              </div>
            </header>
            <p className={styles.effortVector}>{effortVector}</p>
          </section>
        ) : null}

        {bridgeLine ? (
          <section
            id={zoneDomId("bridge")}
            className={styles.zone}
            aria-labelledby="profile-v2-bridge-title"
            data-testid="profile-v2-bridge"
          >
            <header className={styles.zoneHeader}>
              <div>
                <ZoneLabel id="profile-v2-bridge-title" title={PROFILE_V2_COPY.zones.bridge.title} />
                <p className={styles.zoneLead}>{PROFILE_V2_COPY.zones.bridge.lead}</p>
              </div>
            </header>
            <p className={styles.bridgeLine}>{bridgeLine}</p>
            <Link href="/today" className={styles.bridgeCta}>
              {PROFILE_V2_COPY.zones.bridge.cta}
              <span aria-hidden> →</span>
            </Link>
          </section>
        ) : null}

        {model.lifeMission || lifeSpheres?.length ? (
          <section className={styles.zone} data-testid="profile-v2-direction-fold">
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
        ) : null}

        {showCharacterMore ? (
          <details className={styles.characterMore} data-testid="profile-v2-character-more">
            <summary className={styles.characterMoreSummary}>
              {PROFILE_V2_COPY.zones.characterMore.title}
            </summary>
            <div className={styles.characterGrid}>
              {model.strengthens.length ? (
                <article className={styles.characterPanel}>
                  <p className={styles.characterPanelTitle}>
                    {PROFILE_V2_COPY.zones.characterMore.strengthens}
                  </p>
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
                  <p className={styles.characterPanelTitle}>
                    {PROFILE_V2_COPY.zones.characterMore.drains}
                  </p>
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
                <p className={styles.characterPanelTitle}>
                  {PROFILE_V2_COPY.zones.characterMore.helps}
                </p>
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
                <p className={styles.characterPanelTitle}>
                  {PROFILE_V2_COPY.zones.characterMore.decisions}
                </p>
                <p className={styles.factHint}>{model.decisionStyle}</p>
              </article>
            ) : null}
            {model.perceivedAs.length && !node ? (
              <article className={styles.characterPanel} style={{ marginTop: "1rem" }}>
                <p className={styles.characterPanelTitle}>
                  {PROFILE_V2_COPY.zones.characterMore.patterns}
                </p>
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
          </details>
        ) : null}

        <p className={styles.zoneLead}>
          {PROFILE_V2_COPY.mapsCtaHint}{" "}
          <Link href="/maps/mood">{PROFILE_V2_COPY.mapsCta}</Link>
        </p>

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
