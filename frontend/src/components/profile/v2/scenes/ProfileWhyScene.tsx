"use client";

import { useEffect, useState } from "react";
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
import { consumeProfileMotionOnce } from "@/lib/profile/profileMotionOnce";
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

const TAP_EXPAND_IDS = new Set(["sun", "moon", "asc", "rising", "mc"]);

function isTapExpandCard(row: WhyFormationCard): boolean {
  return row.role === "influenced" && TAP_EXPAND_IDS.has(row.id.toLowerCase());
}

function WhyCard({
  row,
  index,
  selectedOnce,
}: {
  row: WhyFormationCard;
  index: number;
  selectedOnce?: boolean;
}) {
  const tapExpand = isTapExpandCard(row);
  const [open, setOpen] = useState(!tapExpand);

  const className = [
    styles.whyProofCard,
    selectedOnce ? profileMotionStyles.selectedOnceReveal : profileMotionStyles.staggerItem,
    tapExpand ? styles.whyProofCardInteractive : "",
    tapExpand && open ? styles.whyProofCardExpanded : "",
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <li
      className={className}
      style={profileMotionStaggerDelay(index, 80)}
      data-testid={`profile-v2-why-anchor-${row.id}`}
      data-why-class={row.class || undefined}
      data-why-tier="primary"
      data-why-role={row.role}
      data-expanded={tapExpand ? (open ? "true" : "false") : undefined}
    >
      {tapExpand ? (
        <button
          type="button"
          className={styles.whyProofHit}
          onClick={() => setOpen((v) => !v)}
          aria-expanded={open}
          data-testid={`profile-v2-why-toggle-${row.id}`}
        >
          <WhyCardBody row={row} open={open} collapseMeaning={!open} />
        </button>
      ) : (
        <WhyCardBody row={row} open />
      )}
    </li>
  );
}

function WhyCardBody({
  row,
  open = true,
  collapseMeaning = false,
}: {
  row: WhyFormationCard;
  open?: boolean;
  collapseMeaning?: boolean;
}) {
  return (
    <>
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
      <div
        className={styles.whyProofMeaningShell}
        data-open={collapseMeaning ? "false" : open ? "true" : "false"}
      >
        <p className={styles.whyProofMeaning} data-testid={`profile-v2-why-meaning-${row.id}`}>
          {row.meaning}
        </p>
      </div>
      {collapseMeaning ? (
        <p className={styles.whyProofExpandHint}>Нажми — смысл за фактом</p>
      ) : null}
    </>
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
  const [selectedOnce, setSelectedOnce] = useState(false);

  useEffect(() => {
    if (motion.className !== profileMotionStyles.reveal) return;
    if (!selected.length) return;
    if (!consumeProfileMotionOnce("act2-selected-by-reveal")) return;
    setSelectedOnce(true);
  }, [motion.className, selected.length]);

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
              <WhyCard key={row.id} row={row} index={index} selectedOnce={selectedOnce} />
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
