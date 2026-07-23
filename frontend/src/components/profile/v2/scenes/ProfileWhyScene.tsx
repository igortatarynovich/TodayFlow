"use client";

import { PROFILE_V2_COPY } from "@/components/profile/v2/profileV2SystemCopy";
import type { ProfileJourneyWhy } from "@/lib/profilePage/buildProfileJourneyProjection";
import styles from "@/components/profile/v2/profileV2System.module.css";

export type ProfileWhySceneProps = {
  why: ProfileJourneyWhy;
};

export function ProfileWhyScene({ why }: ProfileWhySceneProps) {
  const anchors = [...why.selectedBy, ...why.influencedBy];
  if (!anchors.length && !why.honesty && !why.title) return null;

  return (
    <section
      id="profile-v2-why"
      className={styles.zone}
      aria-labelledby="profile-v2-why-title"
      data-testid="profile-v2-why"
    >
      <header className={styles.zoneHeader}>
        <div>
          <p id="profile-v2-why-title" className={styles.zoneLabel}>
            {PROFILE_V2_COPY.zones.why.title}
          </p>
        </div>
      </header>
      {anchors.length ? (
        <ul className={styles.whyProofGrid}>
          {anchors.map((row) => (
            <li
              key={row.id}
              className={styles.whyProofCard}
              data-testid={`profile-v2-why-anchor-${row.id}`}
              data-why-class={row.class || undefined}
            >
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
