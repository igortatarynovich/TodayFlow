"use client";

import { useProfileMotionInView } from "@/components/foundation/ProfileMotion";
import { PROFILE_V2_COPY, PROFILE_V2_DEPTH_NAV } from "@/components/profile/v2/profileV2SystemCopy";
import type { ProfileJourneyNode } from "@/lib/profilePage/buildProfileJourneyProjection";
import styles from "@/components/profile/v2/profileV2System.module.css";

export type ProfileInsightSceneProps = {
  node: ProfileJourneyNode;
};

const insightNav = PROFILE_V2_DEPTH_NAV[2];

function kindEyebrow(kind: string): string {
  const k = kind.toLowerCase();
  if (k === "strength") return PROFILE_V2_COPY.zones.insight.giftLabel;
  if (k === "repeat") return PROFILE_V2_COPY.zones.insight.trapLabel;
  if (k === "tension") return PROFILE_V2_COPY.zones.insight.trapLabel;
  return PROFILE_V2_COPY.zones.insight.title;
}

/**
 * Locked form (PROFILE_PRODUCT_JOURNEY_FORMS_V1): one node cascade —
 * title → insight → grounded → help → living. Not three equal gift/trap/grow documents.
 */
export function ProfileInsightScene({ node }: ProfileInsightSceneProps) {
  const copy = PROFILE_V2_COPY.zones.insight;
  const showLiving = node.livingEvidence.length > 0;
  const motion = useProfileMotionInView<HTMLElement>(60);

  return (
    <section
      id="profile-v2-insight"
      ref={motion.ref}
      className={`${styles.zone} ${styles.journeyScene} ${motion.className}`}
      style={motion.style}
      aria-labelledby="profile-v2-insight-title"
      data-testid="profile-v2-insight"
    >
      <header className={styles.zoneHeader}>
        <div>
          <p className={styles.journeyStepIndex}>
            <span className={styles.journeyStepBadge}>{insightNav.step.replace(/^0/, "")}</span>
            <span id="profile-v2-insight-title">{copy.title}</span>
          </p>
        </div>
      </header>

      <article
        className={[
          styles.insightNode,
          node.kind === "strength" ? styles.insightKind_strength : "",
          node.kind === "tension" || node.kind === "repeat" ? styles.insightKind_tension : "",
        ]
          .filter(Boolean)
          .join(" ")}
        data-testid="profile-v2-insight-node"
        data-insight-kind={node.kind}
      >
        <p className={styles.insightKind}>{kindEyebrow(node.kind)}</p>
        <h2 className={styles.insightTitle}>{node.title}</h2>
        <p className={styles.insightBody}>{node.insight}</p>

        {node.groundedOn.length ? (
          <div className={styles.insightChain} data-testid="profile-v2-insight-grounded">
            <p className={styles.insightChainLabel}>{copy.groundedLabel}</p>
            <ul className={styles.insightGroundList}>
              {node.groundedOn.map((g) => (
                <li key={g.id || g.label}>{g.label}</li>
              ))}
            </ul>
          </div>
        ) : null}

        {node.help ? (
          <div className={styles.insightHelpBlock} data-testid="profile-v2-insight-help">
            <p className={styles.insightChainLabel}>{copy.restoreLabel}</p>
            <p className={styles.insightHelp}>{node.help}</p>
          </div>
        ) : null}

        {showLiving ? (
          <blockquote className={styles.insightQuote} data-testid="profile-v2-insight-living">
            <span className={styles.insightQuoteMark} aria-hidden>
              “
            </span>
            <p className={styles.insightChainLabel}>{copy.livingLabel}</p>
            <ul className={styles.insightLivingList}>
              {node.livingEvidence.map((q) => (
                <li key={q}>{q}</li>
              ))}
            </ul>
            <p className={styles.zoneLead}>{copy.livingNote}</p>
          </blockquote>
        ) : null}
      </article>
    </section>
  );
}
