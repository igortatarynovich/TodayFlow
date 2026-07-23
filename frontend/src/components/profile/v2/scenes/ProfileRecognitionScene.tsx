"use client";

import { useState } from "react";
import { profileMotionStaggerDelay, profileMotionStyles } from "@/components/foundation/ProfileMotion";
import { PROFILE_V2_COPY, PROFILE_V2_DEPTH_NAV } from "@/components/profile/v2/profileV2SystemCopy";
import styles from "@/components/profile/v2/profileV2System.module.css";
import { WhyAnchorGlyph } from "@/components/profile/v2/whyAnchorVisual";
import { ArchetypeHeroVisual } from "@/components/visualIdentity/ArchetypeHeroVisual";
import { SacredGeometryBackdrop } from "@/components/visualIdentity/SacredGeometryBackdrop";
import { resolveArchetypeIllustrationSlug } from "@/lib/visualIdentity/registry";

export type ProfileRecognitionSceneProps = {
  name: string | null;
  line: string | null;
  /** Full identity_core — shown under recognition line (existing contract text). */
  identityCore: string | null;
  archetypeSeed: string | null;
  identityMarkers: string[];
};

const recognitionNav = PROFILE_V2_DEPTH_NAV[0];

export function ProfileRecognitionScene({
  name,
  line,
  identityCore,
  archetypeSeed,
  identityMarkers,
}: ProfileRecognitionSceneProps) {
  const hasPortraitSlot = Boolean(resolveArchetypeIllustrationSlug(archetypeSeed));
  const deeper =
    identityCore?.trim() &&
    identityCore.trim() !== line?.trim() &&
    identityCore.trim().length > (line?.trim().length || 0) + 12
      ? identityCore.trim()
      : null;
  /** Open by default — profile must be readable, not hunted. */
  const [deeperOpen, setDeeperOpen] = useState(Boolean(deeper));
  const copy = PROFILE_V2_COPY.zones.recognition;

  return (
    <section
      id="profile-v2-recognition"
      className={styles.journeyHero}
      aria-labelledby="profile-v2-recognition-title"
      data-testid="profile-v2-recognition"
      data-hero-portrait={hasPortraitSlot ? "true" : "false"}
    >
      <div className={styles.journeyHeroAtmosphere} aria-hidden>
        <SacredGeometryBackdrop emphasis="soft" preset="profile" />
      </div>

      <div className={`${styles.journeyHeroCopy} ${profileMotionStyles.heroEnter}`}>
        <p className={styles.journeyStepIndex}>
          <span className={styles.journeyStepBadge}>{recognitionNav.step.replace(/^0/, "")}</span>
          <span>{copy.title}</span>
        </p>
        <p className={styles.zoneLead}>{copy.lead}</p>
        {name ? (
          <h1
            id="profile-v2-recognition-title"
            className={styles.journeyHeroName}
            data-testid="profile-v2-archetype-label"
          >
            {name}
          </h1>
        ) : (
          <h1 id="profile-v2-recognition-title" className={styles.journeyHeroName}>
            {copy.title}
          </h1>
        )}
        {line ? (
          <p className={styles.journeyRecognitionLine} data-testid="profile-v2-recognition-line">
            {line}
          </p>
        ) : null}

        {deeper ? (
          <div className={styles.recognitionDeeper} data-testid="profile-v2-identity-core">
            <button
              type="button"
              className={styles.recognitionDeeperToggle}
              aria-expanded={deeperOpen}
              onClick={() => setDeeperOpen((v) => !v)}
            >
              {deeperOpen ? copy.deeperHide : copy.deeperLabel}
              <span aria-hidden> {deeperOpen ? "↑" : "↓"}</span>
            </button>
            {deeperOpen ? <p className={styles.recognitionDeeperBody}>{deeper}</p> : null}
          </div>
        ) : null}

        {identityMarkers.length ? (
          <div className={styles.heroPills} data-testid="profile-v2-identity-markers">
            {identityMarkers.slice(0, 3).map((marker, index) => (
              <span
                key={marker}
                className={`${styles.heroPill} ${profileMotionStyles.staggerItem}`}
                style={profileMotionStaggerDelay(index, 140)}
              >
                <WhyAnchorGlyph label={marker} size={14} />
                <span>{marker}</span>
              </span>
            ))}
          </div>
        ) : null}
      </div>

      <div
        className={`${styles.journeyHeroVisual} ${profileMotionStyles.heroSymbolEnter}`}
        aria-hidden={archetypeSeed ? undefined : true}
      >
        <div
          className={`${styles.journeyHeroArch} ${hasPortraitSlot ? styles.journeyHeroArchFilled : ""}`.trim()}
          data-testid="profile-v2-hero-arch"
        >
          <div className={styles.journeyHeroArchGlow} aria-hidden />
          <ArchetypeHeroVisual
            seed={archetypeSeed}
            className={styles.journeySymbolFrame}
            portraitClassName={styles.journeyHeroPortrait}
          />
        </div>
      </div>
    </section>
  );
}
