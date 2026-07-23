"use client";

import { useState, type ReactNode } from "react";
import type { ProfileLifeSphere } from "@/components/profile/ProfileLifeSection";
import type { ProfileQuickMapDeepProps, ProfileQuickMapScreenProps } from "@/components/profile/quickMap/ProfileQuickMapScreen";
import { ProfileV2MyDays } from "@/components/profile/v2/ProfileV2MyDays";
import {
  PROFILE_V2_COPY,
  type ProfileV2ZoneId,
} from "@/components/profile/v2/profileV2SystemCopy";
import { ProfileBridgeScene } from "@/components/profile/v2/scenes/ProfileBridgeScene";
import { ProfileCharacterScene } from "@/components/profile/v2/scenes/ProfileCharacterScene";
import { ProfileEffortScene } from "@/components/profile/v2/scenes/ProfileEffortScene";
import { ProfileExploreSection } from "@/components/profile/v2/scenes/ProfileExploreSection";
import { ProfileInsightScene } from "@/components/profile/v2/scenes/ProfileInsightScene";
import { ProfileRecognitionScene } from "@/components/profile/v2/scenes/ProfileRecognitionScene";
import { ProfileWhyScene } from "@/components/profile/v2/scenes/ProfileWhyScene";
import { ArchetypeSymbol } from "@/components/visualIdentity/ArchetypeSymbol";
import type { ProfileV2LiveContext } from "@/lib/profilePage/buildProfileV2LiveContext";
import { buildProfileFirstScreenProjection } from "@/lib/profilePage/buildProfileFirstScreenProjection";
import { buildProfileJourneyProjection } from "@/lib/profilePage/buildProfileJourneyProjection";
import { profilePortraitFormingMessage } from "@/lib/profilePage/profilePortraitForming";
import { buildProfileHeroQuote } from "@/lib/product-ui/profileWebFigmaHelpers";
import type { CoreProfile } from "@/lib/types";
import styles from "@/components/profile/v2/profileV2System.module.css";

export type ProfileV2SystemScreenProps = {
  model: ProfileQuickMapScreenProps["model"];
  live: ProfileV2LiveContext;
  /** @deprecated Prefer journey.identityMarkers from core — kept for legacy fallback. */
  identityPills?: string[];
  lifeSpheres?: ProfileLifeSphere[];
  deepExpanded?: boolean;
  deep?: ProfileQuickMapDeepProps | null;
  notices?: ReactNode;
  onOpenBirthData: () => void;
  portraitForming?: boolean;
  portraitFormingMessage?: string | null;
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
  const journey = buildProfileJourneyProjection(coreProfile);
  const useJourney = journey.hasJourneySurface && !portraitForming;
  const l3Message = live.userMessages.find((m) => m.code === "l3_gated") ?? null;
  const dataMessages = live.userMessages.filter((m) => m.code !== "l3_gated");

  const showCharacterMore = Boolean(
    model.strengthens.length ||
      model.drains.length ||
      helps.length ||
      model.decisionStyle ||
      model.perceivedAs.length ||
      model.lifeMission ||
      model.relationshipStyle ||
      model.moneyStyle ||
      model.frameworkLead,
  );
  const hasDirection = Boolean(model.lifeMission || lifeSpheres?.length);
  const hasExploreBody = Boolean(deep || journey.progressiveDetails.length || lifeSpheres?.length);

  const first = buildProfileFirstScreenProjection(coreProfile, {
    hasDeepSources: Boolean(deep),
    hasDirectionOrCharacter: hasDirection || showCharacterMore,
  });

  const [exploreOpen, setExploreOpen] = useState(false);

  const insightForScroll = (() => {
    const node = journey.insightNode;
    if (!node) return null;
    const help = node.help?.trim() || "";
    const effort = journey.effortVector?.trim() || "";
    if (help && effort && help.toLowerCase() === effort.toLowerCase()) {
      return { ...node, help: null };
    }
    return node;
  })();

  const progressiveForExplore = journey.progressiveDetails.filter((item) => {
    if (item.id === "relationship_style" && model.relationshipStyle) return false;
    if (item.id === "money_patterns" && model.moneyStyle) return false;
    if (item.id === "decision_style" && model.decisionStyle) return false;
    return true;
  });

  return (
    <div className={styles.pageRoot} data-testid="profile-v2-system">
      <div className={styles.mainColumn}>
        {notices}

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

        {useJourney ? (
          <>
            <ProfileRecognitionScene
              name={journey.recognition.name}
              line={journey.recognition.line}
              identityCore={journey.recognition.identityCore}
              archetypeSeed={journey.recognition.archetypeSeed}
              identityMarkers={journey.identityMarkers}
            />

            {journey.why ? <ProfileWhyScene why={journey.why} /> : null}

            {insightForScroll ? <ProfileInsightScene node={insightForScroll} /> : null}

            {showCharacterMore ? (
              <ProfileCharacterScene
                strengthens={model.strengthens}
                drains={model.drains}
                helps={helps}
                decisionStyle={model.decisionStyle}
                patterns={model.perceivedAs}
                lifeMission={model.lifeMission}
                relationshipStyle={model.relationshipStyle}
                moneyStyle={model.moneyStyle}
                livingChanges={model.frameworkLead}
              />
            ) : null}

            {journey.effortVector ? (
              <ProfileEffortScene
                effortVector={journey.effortVector}
                lifeSpheres={lifeSpheres}
              />
            ) : live.helpsAccessGated && l3Message ? (
              <section className={styles.zone} data-testid="profile-v2-helps-gated" aria-label="Глубина профиля">
                <p className={styles.zoneLead}>{l3Message.text}</p>
              </section>
            ) : null}

            <ProfileBridgeScene bridgeLine={journey.bridge?.line ?? null} />

            {hasExploreBody ? (
              <ProfileExploreSection
                open={exploreOpen}
                onToggle={() => setExploreOpen((v) => !v)}
                progressiveDetails={progressiveForExplore}
                model={model}
                lifeSpheres={lifeSpheres}
                deep={deep}
                deepExpanded={deepExpanded}
                hideMission
              />
            ) : null}

            <ProfileV2MyDays />
          </>
        ) : (
          <LegacyFirstScreen
            model={model}
            live={live}
            first={first}
            identityPills={identityPills}
            lifeSpheres={lifeSpheres}
            deep={deep}
            deepExpanded={deepExpanded}
            portraitForming={portraitForming}
            hasExploreBody={hasExploreBody}
            showCharacterMore={showCharacterMore}
            hasDirection={hasDirection}
            helps={helps}
            l3Message={l3Message}
            exploreOpen={exploreOpen}
            setExploreOpen={setExploreOpen}
          />
        )}
      </div>
    </div>
  );
}

/** Fallback when journey mechanisms are absent — Pattern-style first surface. */
function LegacyFirstScreen({
  model,
  live,
  first,
  identityPills,
  lifeSpheres,
  deep,
  deepExpanded,
  portraitForming,
  hasExploreBody,
  showCharacterMore,
  hasDirection,
  helps,
  l3Message,
  exploreOpen,
  setExploreOpen,
}: {
  model: ProfileQuickMapScreenProps["model"];
  live: ProfileV2LiveContext;
  first: ReturnType<typeof buildProfileFirstScreenProjection>;
  identityPills: string[];
  lifeSpheres?: ProfileLifeSphere[];
  deep?: ProfileQuickMapDeepProps | null;
  deepExpanded: boolean;
  portraitForming: boolean;
  hasExploreBody: boolean;
  showCharacterMore: boolean;
  hasDirection: boolean;
  helps: string[];
  l3Message: { code: string; text: string } | null | undefined;
  exploreOpen: boolean;
  setExploreOpen: (fn: (v: boolean) => boolean) => void;
}) {
  const whoLine = portraitForming
    ? null
    : first.whoLine || live.journey.recognition.line || buildProfileHeroQuote(model.archetype, model.identitySummary);
  const symbolSeed =
    first.archetypeSeed || live.journey.recognition.archetypeSeed || model.archetype || null;
  const archetypeLabel =
    first.archetypeLabel || live.journey.recognition.name || model.archetype || null;
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
  const helpsLine = first.helpsLine || live.journey.effortVector || helps[0] || null;
  const bridgeLine = first.bridgeLine || live.journey.bridge?.line || null;

  return (
    <>
      <section
        id={zoneDomId("recognition")}
        className={styles.journeyHero}
        aria-labelledby="profile-v2-recognition-title"
        data-testid="profile-v2-recognition"
      >
        <div className={styles.journeyHeroVisual} aria-hidden={symbolSeed ? undefined : true}>
          {symbolSeed ? (
            <div className={styles.journeySymbolFrame}>
              <ArchetypeSymbol seed={symbolSeed} size={112} stroke="var(--tf-ink-soft, #5b4630)" />
            </div>
          ) : null}
        </div>
        <div className={styles.journeyHeroCopy}>
          {archetypeLabel ? (
            <h1
              id="profile-v2-recognition-title"
              className={styles.journeyHeroName}
              data-testid="profile-v2-archetype-label"
            >
              {archetypeLabel}
            </h1>
          ) : (
            <h1 id="profile-v2-recognition-title" className={styles.journeyHeroName}>
              {PROFILE_V2_COPY.zones.recognition.title}
            </h1>
          )}
          {whoLine ? (
            <p className={styles.journeyRecognitionLine} data-testid="profile-v2-recognition-line">
              {whoLine}
            </p>
          ) : null}
          {identityPills.length ? (
            <div className={styles.heroPills}>
              {identityPills.slice(0, 3).map((pill) => (
                <span key={pill} className={styles.heroPill}>
                  {pill}
                </span>
              ))}
            </div>
          ) : null}
        </div>
      </section>

      {traits.length ? (
        <section
          id={zoneDomId("why")}
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
          id={zoneDomId("insight")}
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
          id={zoneDomId("effort")}
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
        <section className={styles.zone} data-testid="profile-v2-helps-gated" aria-label="Глубина профиля">
          <p className={styles.zoneLead}>{l3Message.text}</p>
        </section>
      ) : null}

      <ProfileBridgeScene bridgeLine={bridgeLine} />

      <ProfileV2MyDays />

      {hasExploreBody ? (
        <ProfileExploreSection
          open={exploreOpen}
          onToggle={() => setExploreOpen((v) => !v)}
          progressiveDetails={[]}
          model={model}
          lifeSpheres={hasDirection ? lifeSpheres : undefined}
          deep={deep}
          deepExpanded={deepExpanded}
          characterSlot={
            showCharacterMore ? (
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
                            <span
                              className={`${styles.bulletMark} ${styles.bulletMarkMuted}`.trim()}
                              aria-hidden
                            >
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
              </details>
            ) : null
          }
        />
      ) : null}
    </>
  );
}
