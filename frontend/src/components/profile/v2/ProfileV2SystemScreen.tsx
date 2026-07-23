"use client";

import { useState, type ReactNode } from "react";
import Link from "next/link";
import { ProfileChartSection } from "@/components/profile/ProfileChartSection";
import type { ProfileLifeSphere } from "@/components/profile/ProfileLifeSection";
import { ProfilePortalDeepSection } from "@/components/profile/ProfilePortalDeepSection";
import type { ProfileQuickMapDeepProps, ProfileQuickMapScreenProps } from "@/components/profile/quickMap/ProfileQuickMapScreen";
import { ProfileV2MyDays } from "@/components/profile/v2/ProfileV2MyDays";
import { ProfileV2PersonStory } from "@/components/profile/v2/ProfileV2PersonStory";
import { ProfileV2SkySection } from "@/components/profile/v2/ProfileV2SkySection";
import {
  PROFILE_V2_COPY,
  type ProfileV2ZoneId,
} from "@/components/profile/v2/profileV2SystemCopy";
import { ArchetypeSymbol } from "@/components/visualIdentity/ArchetypeSymbol";
import type { ProfileV2LiveContext } from "@/lib/profilePage/buildProfileV2LiveContext";
import { buildProfileFirstScreenProjection } from "@/lib/profilePage/buildProfileFirstScreenProjection";
import { buildProfilePersonStoryProjection } from "@/lib/profilePage/buildProfilePersonStoryProjection";
import { profilePortraitFormingMessage } from "@/lib/profilePage/profilePortraitForming";
import { profileV2SphereCardLine } from "@/lib/profilePage/profileV2SpherePresentation";
import { buildProfileHeroQuote } from "@/lib/product-ui/profileWebFigmaHelpers";
import type { CoreProfile } from "@/lib/types";
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
  /** CoreProfile for first-screen reshape (recognition / traits / contradiction). */
  coreProfile?: CoreProfile | null;
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
  coreProfile = null,
}: ProfileV2SystemScreenProps) {
  const formingMessage = portraitFormingMessageProp?.trim() || profilePortraitFormingMessage(null);
  const helps = live.helps;
  const personStory = buildProfilePersonStoryProjection(coreProfile);
  const usePersonStory = personStory.hasMatrix && !portraitForming;
  const dataMessages = usePersonStory
    ? []
    : live.userMessages.filter((m) => m.code !== "l3_gated");
  const l3Message = live.userMessages.find((m) => m.code === "l3_gated") ?? null;

  const showCharacterMore =
    Boolean(model.strengthens.length || model.drains.length || helps.length || model.decisionStyle || model.perceivedAs.length);
  const hasDirection = Boolean(model.lifeMission || lifeSpheres?.length);
  const hasFullBody = Boolean(hasDirection || showCharacterMore || deep);

  const first = buildProfileFirstScreenProjection(coreProfile, {
    hasDeepSources: Boolean(deep),
    hasDirectionOrCharacter: hasDirection || showCharacterMore,
  });

  const whoLine = portraitForming
    ? null
    : personStory.identityLine ||
      first.whoLine ||
      live.journey.recognitionLine ||
      buildProfileHeroQuote(model.archetype, model.identitySummary);
  const symbolSeed = first.archetypeSeed || live.journey.archetypeSeed || model.archetype || null;
  const archetypeLabel = first.archetypeLabel || live.journey.recognitionName || model.archetype || null;

  const traits =
    first.traits.length > 0
      ? first.traits
      : [
          model.decisionStyle
            ? {
                id: "decisions" as const,
                label: PROFILE_V2_COPY.zones.traits.decisions,
                line: model.decisionStyle,
              }
            : null,
          model.drains[0]
            ? {
                id: "self_friction" as const,
                label: PROFILE_V2_COPY.zones.traits.selfFriction,
                line: model.drains[0],
              }
            : null,
        ].filter((row): row is NonNullable<typeof row> => Boolean(row));
  const contradiction = first.contradiction;
  const helpsLine =
    personStory.helpsLine || first.helpsLine || live.journey.effortVector || helps[0] || null;
  const bridgeLine = first.bridgeLine || live.journey.bridgeLine;

  const [fullOpen, setFullOpen] = useState(false);

  const sunChapter = personStory.chapters.find((c) => c.kind === "sun_facts");
  const heroPills = [
    ...identityPills,
    ...(live.elementLabel ? [live.elementLabel] : []),
    ...(sunChapter?.lines ?? []),
  ].filter((v, i, arr) => arr.indexOf(v) === i);

  return (
    <div className={styles.pageRoot} data-testid="profile-v2-system">
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

        {dataMessages.length ? (
          <section
            className={styles.zone}
            data-testid="profile-v2-capability-ctas"
            aria-label="Что откроет следующий шаг"
          >
            <ul className={styles.traitGrid}>
              {dataMessages.map((msg) => (
                <li key={msg.code || msg.text} className={styles.traitCard}>
                  <p className={styles.traitLine}>{msg.text}</p>
                  <button type="button" className={styles.secondaryCta} onClick={onOpenBirthData}>
                    Данные рождения
                  </button>
                </li>
              ))}
            </ul>
          </section>
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
            {whoLine ? (
              <h1
                id="profile-v2-recognition-title"
                className={styles.journeyHeroTitle}
                data-testid="profile-v2-recognition-line"
              >
                {whoLine}
              </h1>
            ) : (
              <h1 id="profile-v2-recognition-title" className={styles.journeyHeroTitle}>
                {PROFILE_V2_COPY.zones.recognition.title}
              </h1>
            )}
            {archetypeLabel ? (
              <p className={styles.journeyRecognitionLine} data-testid="profile-v2-archetype-label">
                {archetypeLabel}
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

        {usePersonStory ? (
          <ProfileV2PersonStory story={personStory} onOpenBirthData={onOpenBirthData} />
        ) : (
          <>
            {traits.length ? (
              <section
                id={zoneDomId("traits")}
                className={styles.zone}
                aria-labelledby="profile-v2-traits-title"
                data-testid="profile-v2-traits"
              >
                <header className={styles.zoneHeader}>
                  <div>
                    <ZoneLabel id="profile-v2-traits-title" title={PROFILE_V2_COPY.zones.traits.title} />
                  </div>
                </header>
                <ul className={styles.traitGrid}>
                  {traits.map((trait) => (
                    <li key={trait.id} className={styles.traitCard} data-testid={`profile-v2-trait-${trait.id}`}>
                      <p className={styles.traitLabel}>{trait.label}</p>
                      <p className={styles.traitLine}>{trait.line}</p>
                    </li>
                  ))}
                </ul>
              </section>
            ) : null}

            {contradiction ? (
              <section
                id={zoneDomId("contradiction")}
                className={styles.zone}
                aria-labelledby="profile-v2-contradiction-title"
                data-testid="profile-v2-contradiction"
              >
                <header className={styles.zoneHeader}>
                  <div>
                    <ZoneLabel
                      id="profile-v2-contradiction-title"
                      title={PROFILE_V2_COPY.zones.contradiction.title}
                    />
                  </div>
                </header>
                <article className={styles.insightCard}>
                  <h2 className={styles.insightTitle}>{contradiction.title}</h2>
                  <p className={styles.insightBody}>{contradiction.insight}</p>
                </article>
              </section>
            ) : null}

            {helpsLine ? (
              <section
                id={zoneDomId("helps")}
                className={styles.zone}
                aria-labelledby="profile-v2-helps-title"
                data-testid="profile-v2-helps"
              >
                <header className={styles.zoneHeader}>
                  <div>
                    <ZoneLabel id="profile-v2-helps-title" title={PROFILE_V2_COPY.zones.helps.title} />
                    <p className={styles.zoneLead}>{PROFILE_V2_COPY.zones.helps.lead}</p>
                  </div>
                </header>
                <p className={styles.effortVector}>{helpsLine}</p>
              </section>
            ) : live.helpsAccessGated && l3Message ? (
              <section
                className={styles.zone}
                data-testid="profile-v2-helps-gated"
                aria-label="Глубина профиля"
              >
                <p className={styles.zoneLead}>{l3Message.text}</p>
              </section>
            ) : null}
          </>
        )}

        <ProfileV2MyDays />

        <section
          className={styles.zone}
          data-testid="profile-v2-actions"
          aria-label="Дальше по профилю"
        >
          <div className={styles.actionRow}>
            <Link href="/today" className={styles.bridgeCta} data-testid="profile-v2-open-today">
              {PROFILE_V2_COPY.zones.actions.today}
              <span aria-hidden> →</span>
            </Link>
            {hasFullBody ? (
              <button
                type="button"
                className={styles.secondaryCta}
                data-testid="profile-v2-open-full"
                aria-expanded={fullOpen}
                aria-controls="profile-v2-full"
                onClick={() => setFullOpen((v) => !v)}
              >
                {fullOpen
                  ? PROFILE_V2_COPY.zones.actions.hideFullProfile
                  : PROFILE_V2_COPY.zones.actions.fullProfile}
                <span aria-hidden> {fullOpen ? "↑" : "→"}</span>
              </button>
            ) : null}
          </div>
          {bridgeLine ? <p className={styles.bridgeLine}>{bridgeLine}</p> : null}
          {!bridgeLine ? (
            <p className={styles.zoneLead}>{PROFILE_V2_COPY.zones.actions.todayLead}</p>
          ) : null}
        </section>

        {fullOpen && hasFullBody ? (
          <div id="profile-v2-full" data-testid="profile-v2-full">
            {hasDirection ? (
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
              <details className={styles.characterMore} data-testid="profile-v2-character-more" open>
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
                {model.perceivedAs.length && !contradiction ? (
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
                id={zoneDomId("full")}
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
        ) : null}
      </div>
    </div>
  );
}
