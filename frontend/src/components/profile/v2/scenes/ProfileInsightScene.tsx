"use client";

import { PROFILE_V2_COPY } from "@/components/profile/v2/profileV2SystemCopy";
import type { ProfileJourneyNode } from "@/lib/profilePage/buildProfileJourneyProjection";
import styles from "@/components/profile/v2/profileV2System.module.css";

export type ProfileInsightSceneProps = {
  node: ProfileJourneyNode;
};

export function ProfileInsightScene({ node }: ProfileInsightSceneProps) {
  const copy = PROFILE_V2_COPY.zones.insight;
  const showLiving = node.livingEvidence.length > 0;

  return (
    <section
      id="profile-v2-insight"
      className={styles.zone}
      aria-labelledby="profile-v2-insight-title"
      data-testid="profile-v2-insight"
    >
      <header className={styles.zoneHeader}>
        <div>
          <p id="profile-v2-insight-title" className={styles.zoneLabel}>
            {copy.title}
          </p>
        </div>
      </header>

      <article className={styles.insightScene} data-testid="profile-v2-insight-node">
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
          <div className={styles.insightChain} data-testid="profile-v2-insight-help">
            <p className={styles.insightChainLabel}>{copy.helpLabel}</p>
            <p className={styles.insightHelp}>{node.help}</p>
          </div>
        ) : null}

        {showLiving ? (
          <div className={styles.insightChain} data-testid="profile-v2-insight-living">
            <p className={styles.insightChainLabel}>{copy.livingLabel}</p>
            <ul className={styles.insightLivingList}>
              {node.livingEvidence.map((q) => (
                <li key={q}>«{q}»</li>
              ))}
            </ul>
            <p className={styles.zoneLead}>{copy.livingNote}</p>
          </div>
        ) : null}
      </article>
    </section>
  );
}
