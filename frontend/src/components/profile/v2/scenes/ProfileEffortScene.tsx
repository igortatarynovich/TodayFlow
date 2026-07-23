"use client";

import { PROFILE_V2_COPY } from "@/components/profile/v2/profileV2SystemCopy";
import type { ProfileLifeSphere } from "@/components/profile/ProfileLifeSection";
import styles from "@/components/profile/v2/profileV2System.module.css";

export type ProfileEffortSceneProps = {
  effortVector: string;
  lifeSpheres?: ProfileLifeSphere[];
};

export function ProfileEffortScene({ effortVector, lifeSpheres = [] }: ProfileEffortSceneProps) {
  const sphereLabels = lifeSpheres.map((s) => s.title).filter(Boolean).slice(0, 6);

  return (
    <section
      id="profile-v2-effort"
      className={styles.zone}
      aria-labelledby="profile-v2-effort-title"
      data-testid="profile-v2-effort"
    >
      <header className={styles.zoneHeader}>
        <div>
          <p id="profile-v2-effort-title" className={styles.zoneLabel}>
            {PROFILE_V2_COPY.zones.effort.title}
          </p>
          <p className={styles.zoneLead}>{PROFILE_V2_COPY.zones.effort.lead}</p>
        </div>
      </header>
      <p className={styles.effortVector} data-testid="profile-v2-effort-vector">
        {effortVector}
      </p>
      {sphereLabels.length ? (
        <div className={styles.effortSpheres} data-testid="profile-v2-effort-spheres">
          <p className={styles.effortSpheresLabel}>{PROFILE_V2_COPY.zones.effort.spheresLabel}</p>
          <p className={styles.effortSpheresLine}>{sphereLabels.join(" · ")}</p>
        </div>
      ) : null}
    </section>
  );
}
