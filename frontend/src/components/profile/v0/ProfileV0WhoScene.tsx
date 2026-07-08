"use client";

import type { ProfileV0WhoCard } from "@/lib/profilePage/buildProfileV0Data";
import styles from "./profileV0.module.css";

export function ProfileV0WhoScene({ who }: { who: ProfileV0WhoCard }) {
  const heading = `Почему именно ${who.archetypeLabel}`;

  return (
    <section className={`${styles.profileCard} ${styles.profileStatementCard}`} aria-label={heading}>
      <div className={styles.statementBody}>
        <h3 className={styles.statementHeading}>{heading}</h3>

        {who.whyManifest ? <p className={styles.statementPhrase}>{who.whyManifest}</p> : null}

        {who.whyInsights.length > 1 ? (
          <ul className={styles.statementInsights}>
            {who.whyInsights.slice(1).map((insight) => (
              <li key={insight} className={styles.statementInsightItem}>
                {insight}
              </li>
            ))}
          </ul>
        ) : null}

        <p className={styles.statementNote}>{who.layerHint}</p>
      </div>
    </section>
  );
}
