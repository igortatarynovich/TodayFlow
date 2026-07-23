"use client";

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
  archetypeSeed: string | null;
  identityMarkers: string[];
};

const recognitionNav = PROFILE_V2_DEPTH_NAV[0];

export function ProfileRecognitionScene({
  name,
  line,
  archetypeSeed,
  identityMarkers,
}: ProfileRecognitionSceneProps) {
  const hasPortraitSlot = Boolean(resolveArchetypeIllustrationSlug(archetypeSeed));

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
          <span>{PROFILE_V2_COPY.zones.recognition.title}</span>
        </p>
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
            {PROFILE_V2_COPY.zones.recognition.title}
          </h1>
        )}
        {line ? (
          <p className={styles.journeyRecognitionLine} data-testid="profile-v2-recognition-line">
            {line}
          </p>
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
