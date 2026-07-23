"use client";

import {
  profileMotionStaggerDelay,
  profileMotionStyles,
  useProfileMotionInView,
} from "@/components/foundation/ProfileMotion";
import { PROFILE_V2_COPY, PROFILE_V2_DEPTH_NAV } from "@/components/profile/v2/profileV2SystemCopy";
import { WhyAnchorGlyph } from "@/components/profile/v2/whyAnchorVisual";
import type { ProfileJourneyWhy } from "@/lib/profilePage/buildProfileJourneyProjection";
import styles from "@/components/profile/v2/profileV2System.module.css";

export type ProfileWhySceneProps = {
  why: ProfileJourneyWhy;
};

const whyNav = PROFILE_V2_DEPTH_NAV[1];

export function ProfileWhyScene({ why }: ProfileWhySceneProps) {
  const anchors = [...why.selectedBy, ...why.influencedBy];
  const motion = useProfileMotionInView<HTMLElement>(40);
  if (!anchors.length && !why.honesty && !why.title) return null;

  return (
    <section
      id="profile-v2-why"
      ref={motion.ref}
      className={`${styles.zone} ${styles.journeyScene} ${motion.className}`}
      style={motion.style}
      aria-labelledby="profile-v2-why-title"
      data-testid="profile-v2-why"
    >
      <header className={styles.zoneHeader}>
        <div>
          <p className={styles.journeyStepIndex}>
            <span className={styles.journeyStepBadge}>{whyNav.step.replace(/^0/, "")}</span>
            <span id="profile-v2-why-title">{PROFILE_V2_COPY.zones.why.title}</span>
          </p>
        </div>
      </header>
      {anchors.length ? (
        <ul className={styles.whyProofGrid}>
          {anchors.map((row, index) => (
            <li
              key={row.id}
              className={`${styles.whyProofCard} ${profileMotionStyles.staggerItem}`}
              style={profileMotionStaggerDelay(index, 80)}
              data-testid={`profile-v2-why-anchor-${row.id}`}
              data-why-class={row.class || undefined}
            >
              <span className={styles.whyProofIcon} aria-hidden>
                <WhyAnchorGlyph label={row.label} rowClass={row.class} size={28} />
              </span>
              <p className={styles.whyProofTitle}>{row.label}</p>
            </li>
          ))}
        </ul>
      ) : null}
      {why.title ? <p className={styles.whySynthesis}>{why.title}</p> : null}
      {why.honesty ? (
        <p className={styles.zoneLead} data-testid="profile-v2-why-honesty">
          {why.honesty}
        </p>
      ) : null}
    </section>
  );
}
