"use client";

import { useProfileMotionInView } from "@/components/foundation/ProfileMotion";
import { ProfileAtmosphere } from "@/components/profile/v2/ProfileAtmosphere";
import { PROFILE_V2_COPY, PROFILE_V2_DEPTH_NAV } from "@/components/profile/v2/profileV2SystemCopy";
import type { ProfileJourneyNode } from "@/lib/profilePage/buildProfileJourneyProjection";
import styles from "@/components/profile/v2/profileV2System.module.css";

export type ProfileInsightSceneProps = {
  node: ProfileJourneyNode;
};

const insightNav = PROFILE_V2_DEPTH_NAV.find((s) => s.id === "insight") ?? PROFILE_V2_DEPTH_NAV[2];

function kindEyebrow(kind: string): string {
  const k = kind.toLowerCase();
  if (k === "strength") return PROFILE_V2_COPY.zones.insight.giftLabel;
  if (k === "repeat") return PROFILE_V2_COPY.zones.insight.trapLabel;
  if (k === "tension") return PROFILE_V2_COPY.zones.insight.trapLabel;
  return PROFILE_V2_COPY.zones.insight.title;
}

function kindClass(kind: string): string {
  const k = kind.toLowerCase();
  if (k === "strength") return styles.insightKind_strength;
  if (k === "tension" || k === "repeat") return styles.insightKind_tension;
  return "";
}

/**
 * Locked form: one node cascade (title → insight → grounded → help → living).
 * Visual accents echo the reference triad without three equal documents.
 */
export function ProfileInsightScene({ node }: ProfileInsightSceneProps) {
  const copy = PROFILE_V2_COPY.zones.insight;
  const showLiving = node.livingEvidence.length > 0;
  const showGrounded = node.groundedOn.length > 0;
  const showHelp = Boolean(node.help);
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
      <ProfileAtmosphere motif="insight" />
      <header className={styles.zoneHeader}>
        <div>
          <p className={styles.journeyStepIndex}>
            <span className={styles.journeyStepBadge}>{insightNav.step.replace(/^0/, "")}</span>
            <span id="profile-v2-insight-title">{copy.title}</span>
          </p>
          <p className={styles.zoneLead}>{copy.lead}</p>
        </div>
      </header>

      <div className={styles.insightScene}>
        <article
          className={[styles.insightNode, kindClass(node.kind)].filter(Boolean).join(" ")}
          data-testid="profile-v2-insight-node"
          data-insight-kind={node.kind}
        >
          <p className={styles.insightKind}>{kindEyebrow(node.kind)}</p>
          <h2 className={styles.insightTitle}>{node.title}</h2>
          <p className={styles.insightBody}>{node.insight}</p>
        </article>

        {showGrounded || showHelp ? (
          <div
            className={styles.insightSupportGrid}
            data-testid="profile-v2-insight-support"
            data-cols={showGrounded && showHelp ? "2" : "1"}
          >
            {showGrounded ? (
              <div
                className={`${styles.insightSupportCard} ${styles.insightSupportGround}`}
                data-testid="profile-v2-insight-grounded"
              >
                <p className={styles.insightChainLabel}>{copy.groundedLabel}</p>
                <ul className={styles.insightGroundList}>
                  {node.groundedOn.map((g) => (
                    <li key={g.id || g.label}>{g.label}</li>
                  ))}
                </ul>
              </div>
            ) : null}

            {showHelp ? (
              <div
                className={`${styles.insightSupportCard} ${styles.insightSupportHelp}`}
                data-testid="profile-v2-insight-help"
              >
                <p className={styles.insightChainLabel}>{copy.restoreLabel}</p>
                <p className={styles.insightHelp}>{node.help}</p>
              </div>
            ) : null}
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
      </div>
    </section>
  );
}
