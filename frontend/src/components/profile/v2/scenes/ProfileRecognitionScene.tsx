"use client";

import { profileMotionStyles } from "@/components/foundation/ProfileMotion";
import { PROFILE_V2_COPY, PROFILE_V2_DEPTH_NAV } from "@/components/profile/v2/profileV2SystemCopy";
import styles from "@/components/profile/v2/profileV2System.module.css";
import { ArchetypeHeroVisual } from "@/components/visualIdentity/ArchetypeHeroVisual";
import { SacredGeometryBackdrop } from "@/components/visualIdentity/SacredGeometryBackdrop";
import { MotionDrift } from "@/design-system/motion";
import { resolveArchetypeIllustrationSlug } from "@/lib/visualIdentity/registry";

export type ProfileRecognitionSceneProps = {
  name: string | null;
  line: string | null;
  /** Full identity_core — preferred body when present (no collapse / no duplicate). */
  identityCore: string | null;
  archetypeSeed: string | null;
};

const recognitionNav = PROFILE_V2_DEPTH_NAV[0];

/**
 * Act 1: archetype name + one full identity body + visual.
 * Prefer identity_core; fall back to recognition_line. No toggle / no dupe.
 */
export function ProfileRecognitionScene({
  name,
  line,
  identityCore,
  archetypeSeed,
}: ProfileRecognitionSceneProps) {
  const hasPortraitSlot = Boolean(resolveArchetypeIllustrationSlug(archetypeSeed));
  const body = (identityCore?.trim() || line?.trim() || "") || null;
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
        {copy.lead ? <p className={styles.zoneLead}>{copy.lead}</p> : null}
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
        {body ? (
          <p className={styles.journeyRecognitionLine} data-testid="profile-v2-recognition-line">
            {body}
          </p>
        ) : null}
      </div>

      <div
        className={`${styles.journeyHeroVisual} ${profileMotionStyles.heroSymbolEnter}`}
        aria-hidden={archetypeSeed ? undefined : true}
      >
        <MotionDrift durationSec={18} className={styles.journeyHeroDrift}>
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
        </MotionDrift>
      </div>
    </section>
  );
}
