"use client";

import {
  profileMotionStaggerDelay,
  profileMotionStyles,
  useProfileMotionInView,
} from "@/components/foundation/ProfileMotion";
import { ProfileAtmosphere } from "@/components/profile/v2/ProfileAtmosphere";
import { PROFILE_V2_COPY, PROFILE_V2_DEPTH_NAV } from "@/components/profile/v2/profileV2SystemCopy";
import { WhyAnchorGlyph } from "@/components/profile/v2/whyAnchorVisual";
import type { ProfileJourneyWhy } from "@/lib/profilePage/buildProfileJourneyProjection";
import { presentWhyAnchors } from "@/lib/profilePage/presentWhyAnchors";
import styles from "@/components/profile/v2/profileV2System.module.css";

export type ProfileWhySceneProps = {
  why: ProfileJourneyWhy;
};

const whyNav = PROFILE_V2_DEPTH_NAV[1];

export function ProfileWhyScene({ why }: ProfileWhySceneProps) {
  const anchors = [...why.selectedBy, ...why.influencedBy];
  const { primary, secondary } = presentWhyAnchors(anchors);
  const motion = useProfileMotionInView<HTMLElement>(40);
  if (!primary.length && !secondary.length && !why.honesty && !why.title) return null;

  return (
    <section
      id="profile-v2-why"
      ref={motion.ref}
      className={`${styles.zone} ${styles.journeyScene} ${motion.className}`}
      style={motion.style}
      aria-labelledby="profile-v2-why-title"
      data-testid="profile-v2-why"
    >
      <ProfileAtmosphere motif="why" />
      <header className={styles.zoneHeader}>
        <div>
          <p className={styles.journeyStepIndex}>
            <span className={styles.journeyStepBadge}>{whyNav.step.replace(/^0/, "")}</span>
            <span id="profile-v2-why-title">{PROFILE_V2_COPY.zones.why.title}</span>
          </p>
          <p className={styles.zoneLead}>{PROFILE_V2_COPY.zones.why.lead}</p>
        </div>
      </header>

      {primary.length ? (
        <ul className={styles.whyProofGrid} data-testid="profile-v2-why-primary">
          {primary.map((row, index) => (
            <li
              key={row.id}
              className={`${styles.whyProofCard} ${profileMotionStyles.staggerItem}`}
              style={profileMotionStaggerDelay(index, 80)}
              data-testid={`profile-v2-why-anchor-${row.id}`}
              data-why-class={row.class || undefined}
              data-why-tier="primary"
            >
              <div className={styles.whyProofCardTop}>
                <span className={styles.whyProofIcon} aria-hidden>
                  <WhyAnchorGlyph label={row.title} rowClass={row.class} size={28} />
                </span>
                <p className={styles.whyProofRole}>
                  {row.role === "selected"
                    ? PROFILE_V2_COPY.zones.why.selectedLabel
                    : PROFILE_V2_COPY.zones.why.influencedLabel}
                </p>
              </div>
              <p className={styles.whyProofTitle}>{row.title}</p>
              {row.detail ? <p className={styles.whyProofDetail}>{row.detail}</p> : null}
            </li>
          ))}
        </ul>
      ) : null}

      {secondary.length ? (
        <ul className={styles.whySecondaryRow} data-testid="profile-v2-why-secondary">
          {secondary.map((row) => (
            <li
              key={row.id}
              className={styles.whySecondaryChip}
              data-testid={`profile-v2-why-anchor-${row.id}`}
              data-why-class={row.class || undefined}
              data-why-tier="secondary"
            >
              <span className={styles.whySecondaryIcon} aria-hidden>
                <WhyAnchorGlyph label={row.title} rowClass={row.class} size={16} />
              </span>
              <span className={styles.whySecondaryText}>
                <span className={styles.whySecondaryTitle}>{row.title}</span>
                {row.detail ? <span className={styles.whySecondaryDetail}>{row.detail}</span> : null}
              </span>
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
