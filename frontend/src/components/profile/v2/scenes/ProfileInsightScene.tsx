"use client";

import { useProfileMotionInView } from "@/components/foundation/ProfileMotion";
import { ProfileAtmosphere } from "@/components/profile/v2/ProfileAtmosphere";
import { PROFILE_V2_COPY, PROFILE_V2_DEPTH_NAV } from "@/components/profile/v2/profileV2SystemCopy";
import type { ProfileJourneyNode } from "@/lib/profilePage/buildProfileJourneyProjection";
import { scrubUserFacingText } from "@/lib/todayValueGate";
import styles from "@/components/profile/v2/profileV2System.module.css";

export type ProfileInsightSceneProps = {
  node: ProfileJourneyNode;
};

const insightNav = PROFILE_V2_DEPTH_NAV.find((s) => s.id === "insight") ?? PROFILE_V2_DEPTH_NAV[2];

/** Forms titles («Главное напряжение» / «Самая большая ловушка») are the only heading. */
function kindEyebrow(kind: string): string | null {
  const k = kind.toLowerCase();
  if (k === "strength") return PROFILE_V2_COPY.zones.insight.giftLabel;
  if (k === "repeat" || k === "tension") return null;
  return PROFILE_V2_COPY.zones.insight.title;
}

function kindClass(kind: string): string {
  const k = kind.toLowerCase();
  if (k === "strength") return styles.insightKind_strength;
  if (k === "tension" || k === "repeat") return styles.insightKind_tension;
  return "";
}

/**
 * Visual Modes #4 — Act 3: vertical story spine (≠ Act1 hero, ≠ Act2 proof grid).
 * Forms cascade: title → insight → grounded → help → living (omit empty).
 */
export function ProfileInsightScene({ node }: ProfileInsightSceneProps) {
  const copy = PROFILE_V2_COPY.zones.insight;
  const livingEvidence = node.livingEvidence
    .map((q) => scrubUserFacingText(q))
    .filter((q): q is string => Boolean(q));
  const showLiving = livingEvidence.length > 0;
  const showGrounded = node.groundedOn.length > 0;
  const help = scrubUserFacingText(node.help);
  const showHelp = Boolean(help);
  const insight = scrubUserFacingText(node.insight) || node.insight;
  const eyebrow = kindEyebrow(node.kind);
  const motion = useProfileMotionInView<HTMLElement>(60);
  const showSpine = showGrounded || showHelp || showLiving;

  return (
    <section
      id="profile-v2-insight"
      ref={motion.ref}
      className={`${styles.journeyScene} ${styles.journeySceneModeInsight} ${motion.className}`}
      style={motion.style}
      aria-labelledby="profile-v2-insight-title"
      data-testid="profile-v2-insight"
      data-visual-mode="insight-spine"
    >
      <ProfileAtmosphere motif="insight" />
      <header className={styles.zoneHeader}>
        <div>
          <p className={styles.journeyStepIndex}>
            <span className={styles.journeyStepBadge}>{insightNav.step.replace(/^0/, "")}</span>
            <span id="profile-v2-insight-title">{copy.title}</span>
          </p>
          {copy.lead ? <p className={styles.zoneLead}>{copy.lead}</p> : null}
        </div>
      </header>

      <div className={styles.insightScene} data-testid="profile-v2-insight-spine">
        <article
          className={[styles.insightNode, kindClass(node.kind)].filter(Boolean).join(" ")}
          data-testid="profile-v2-insight-node"
          data-insight-kind={node.kind}
        >
          <span className={styles.insightSpineDot} aria-hidden />
          {eyebrow ? <p className={styles.insightKind}>{eyebrow}</p> : null}
          <h2 className={styles.insightTitle}>{node.title}</h2>
          <p className={styles.insightBody}>{insight}</p>
        </article>

        {showSpine ? (
          <div className={styles.insightSpine} data-testid="profile-v2-insight-support">
            <span className={styles.insightSpineRail} aria-hidden />

            {showGrounded ? (
              <div
                className={`${styles.insightSpineStep} ${styles.insightSpineGround}`}
                data-testid="profile-v2-insight-grounded"
              >
                <span className={styles.insightSpineDot} aria-hidden />
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
                className={`${styles.insightSpineStep} ${styles.insightSpineHelp}`}
                data-testid="profile-v2-insight-help"
              >
                <span className={styles.insightSpineDot} aria-hidden />
                <p className={styles.insightChainLabel}>{copy.helpLabel}</p>
                <p className={styles.insightHelp}>{help}</p>
              </div>
            ) : null}

            {showLiving ? (
              <blockquote
                className={`${styles.insightSpineStep} ${styles.insightSpineLiving}`}
                data-testid="profile-v2-insight-living"
              >
                <span className={styles.insightSpineDot} aria-hidden />
                <p className={styles.insightChainLabel}>{copy.livingLabel}</p>
                <ul className={styles.insightLivingList}>
                  {livingEvidence.map((q) => (
                    <li key={q}>{q}</li>
                  ))}
                </ul>
                {copy.livingNote ? (
                  <p className={styles.livingNote} data-testid="profile-v2-insight-living-note">
                    {copy.livingNote}
                  </p>
                ) : null}
              </blockquote>
            ) : null}
          </div>
        ) : null}
      </div>
    </section>
  );
}
