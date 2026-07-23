"use client";

import { ArchetypeSymbol } from "@/components/visualIdentity/ArchetypeSymbol";
import { PROFILE_V2_COPY } from "@/components/profile/v2/profileV2SystemCopy";
import styles from "@/components/profile/v2/profileV2System.module.css";

export type ProfileRecognitionSceneProps = {
  name: string | null;
  line: string | null;
  archetypeSeed: string | null;
  identityMarkers: string[];
};

export function ProfileRecognitionScene({
  name,
  line,
  archetypeSeed,
  identityMarkers,
}: ProfileRecognitionSceneProps) {
  return (
    <section
      id="profile-v2-recognition"
      className={styles.journeyHero}
      aria-labelledby="profile-v2-recognition-title"
      data-testid="profile-v2-recognition"
    >
      <div className={styles.journeyHeroVisual} aria-hidden={archetypeSeed ? undefined : true}>
        {archetypeSeed ? (
          <div className={styles.journeySymbolFrame}>
            <ArchetypeSymbol seed={archetypeSeed} size={140} stroke="var(--tf-ink-soft, #5b4630)" />
          </div>
        ) : null}
      </div>
      <div className={styles.journeyHeroCopy}>
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
            {identityMarkers.slice(0, 3).map((marker) => (
              <span key={marker} className={styles.heroPill}>
                {marker}
              </span>
            ))}
          </div>
        ) : null}
      </div>
    </section>
  );
}
