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
import {
  buildWhyFormationCards,
  type WhyFormationCard,
} from "@/lib/profilePage/buildWhyFormationCards";
import type { ProfileFrameworkCard } from "@/lib/profilePage/buildProfileQuickMapData";
import type { CoreProfile } from "@/lib/types";
import styles from "@/components/profile/v2/profileV2System.module.css";

export type ProfileWhySceneProps = {
  why: ProfileJourneyWhy;
  coreProfile?: CoreProfile | null;
  frameworkCards?: ProfileFrameworkCard[] | null;
  /** Act 1 line — used for anti-dupe against Act 2 meanings. */
  recognitionLine?: string | null;
  identityCore?: string | null;
};

const whyNav = PROFILE_V2_DEPTH_NAV[1];

function WhyCard({
  row,
  index,
}: {
  row: WhyFormationCard;
  index: number;
}) {
  return (
    <li
      className={`${styles.whyProofCard} ${profileMotionStyles.staggerItem}`}
      style={profileMotionStaggerDelay(index, 80)}
      data-testid={`profile-v2-why-anchor-${row.id}`}
      data-why-class={row.class || undefined}
      data-why-tier="primary"
      data-why-role={row.role}
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
      <p className={styles.whyProofMeaning} data-testid={`profile-v2-why-meaning-${row.id}`}>
        {row.meaning}
      </p>
    </li>
  );
}

export function ProfileWhyScene({
  why,
  coreProfile = null,
  frameworkCards = null,
  recognitionLine = null,
  identityCore = null,
}: ProfileWhySceneProps) {
  const anchors = [...why.selectedBy, ...why.influencedBy];
  const { selected, influenced } = buildWhyFormationCards(anchors, {
    core: coreProfile,
    frameworkCards,
    recognitionLine,
    identityCore,
  });
  const motion = useProfileMotionInView<HTMLElement>(40);
  if (!selected.length && !influenced.length && !why.honesty && !why.title) return null;

  const copy = PROFILE_V2_COPY.zones.why;

  return (
    <section
      id="profile-v2-why"
      ref={motion.ref}
      className={`${styles.journeyScene} ${motion.className}`}
      style={motion.style}
      aria-labelledby="profile-v2-why-title"
      data-testid="profile-v2-why"
    >
      <ProfileAtmosphere motif="why" />
      <header className={styles.zoneHeader}>
        <div>
          <p className={styles.journeyStepIndex}>
            <span className={styles.journeyStepBadge}>{whyNav.step.replace(/^0/, "")}</span>
            <span id="profile-v2-why-title">{copy.title}</span>
          </p>
          {copy.lead ? <p className={styles.zoneLead}>{copy.lead}</p> : null}
        </div>
      </header>

      {selected.length ? (
        <div className={styles.whyFormationBlock} data-testid="profile-v2-why-selected">
          <p className={styles.whyFormationLabel}>{copy.selectedSection}</p>
          <ul className={styles.whyProofGrid} data-testid="profile-v2-why-primary">
            {selected.map((row, index) => (
              <WhyCard key={row.id} row={row} index={index} />
            ))}
          </ul>
        </div>
      ) : null}

      {influenced.length ? (
        <div className={styles.whyFormationBlock} data-testid="profile-v2-why-influenced">
          <p className={styles.whyFormationLabel}>{copy.influencedSection}</p>
          <ul className={styles.whyProofGrid} data-testid="profile-v2-why-influenced-grid">
            {influenced.map((row, index) => (
              <WhyCard key={row.id} row={row} index={index} />
            ))}
          </ul>
        </div>
      ) : null}

      {why.title && why.title !== copy.title ? (
        <p className={styles.whySynthesis}>{why.title}</p>
      ) : null}
      {why.honesty ? (
        <p className={styles.zoneLead} data-testid="profile-v2-why-honesty">
          {why.honesty}
        </p>
      ) : null}
    </section>
  );
}
