"use client";

import { useState } from "react";
import { profileMotionStyles } from "@/components/foundation/ProfileMotion";
import { PROFILE_V2_COPY } from "@/components/profile/v2/profileV2SystemCopy";
import styles from "@/design-system/profile/dsProfileV2System.module.css";
import { ArchetypeHeroVisual } from "@/components/visualIdentity/ArchetypeHeroVisual";
import { SacredGeometryBackdrop } from "@/components/visualIdentity/SacredGeometryBackdrop";
import { MotionDrift } from "@/design-system/motion";
import { resolveArchetypeIllustrationSlug } from "@/lib/visualIdentity/registry";
import { compactProfileCopy } from "@/lib/profilePage/truncateProfileCopy";

export type ProfileRecognitionSceneProps = {
  name: string | null;
  line: string | null;
  /** Kitchen text — never the first-frame line. Behind the one signal. */
  identityCore: string | null;
  archetypeSeed: string | null;
  /** When set, the signal can move to Why if there is no deeper core. */
  hasWhy?: boolean;
};

const LINE_MAX = 120;

function sameLine(a: string, b: string): boolean {
  return a.trim().toLowerCase() === b.trim().toLowerCase();
}

/**
 * First viewport @390: portrait → name → one personal line → one signal.
 * identity_core is disclosure, not the line. No act badge.
 */
export function ProfileRecognitionScene({
  name,
  line,
  identityCore,
  archetypeSeed,
  hasWhy = false,
}: ProfileRecognitionSceneProps) {
  const hasPortraitSlot = Boolean(resolveArchetypeIllustrationSlug(archetypeSeed));
  const copy = PROFILE_V2_COPY.zones.recognition;
  const core = identityCore?.trim() || "";
  const lineText =
    compactProfileCopy(line?.trim() || "", LINE_MAX) ||
    compactProfileCopy(core, LINE_MAX) ||
    null;
  const deeper = core && lineText && !sameLine(core, lineText) ? core : null;
  const [open, setOpen] = useState(false);
  const showSignal = Boolean(deeper) || hasWhy;

  function onSignal() {
    if (deeper) {
      setOpen((v) => !v);
      return;
    }
    document.getElementById("profile-v2-why")?.scrollIntoView({ behavior: "smooth", block: "start" });
  }

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
        {lineText ? (
          <p className={styles.journeyRecognitionLine} data-testid="profile-v2-recognition-line">
            {lineText}
          </p>
        ) : null}
        {showSignal ? (
          <div className={styles.recognitionDeeper}>
            <button
              type="button"
              className={styles.recognitionDeeperToggle}
              onClick={onSignal}
              aria-expanded={deeper ? open : undefined}
              data-testid="profile-v2-recognition-signal"
            >
              {deeper && open ? copy.deeperHide : copy.signalLabel}
            </button>
            {deeper && open ? (
              <p className={styles.recognitionDeeperBody} data-testid="profile-v2-identity-core">
                {deeper}
              </p>
            ) : null}
          </div>
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
