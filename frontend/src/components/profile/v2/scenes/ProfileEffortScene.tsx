"use client";

import {
  profileMotionStaggerDelay,
  profileMotionStyles,
  useProfileMotionInView,
} from "@/components/foundation/ProfileMotion";
import type { ProfileLifeSphere } from "@/components/profile/ProfileLifeSection";
import { PROFILE_V2_COPY, PROFILE_V2_DEPTH_NAV } from "@/components/profile/v2/profileV2SystemCopy";
import styles from "@/components/profile/v2/profileV2System.module.css";

export type ProfileEffortSceneProps = {
  effortVector: string;
  lifeSpheres?: ProfileLifeSphere[];
};

const effortNav = PROFILE_V2_DEPTH_NAV[3];

export function ProfileEffortScene({ effortVector, lifeSpheres = [] }: ProfileEffortSceneProps) {
  const spheres = lifeSpheres.filter((s) => s.title?.trim()).slice(0, 8);
  const motion = useProfileMotionInView<HTMLElement>(80);

  return (
    <section
      id="profile-v2-effort"
      ref={motion.ref}
      className={`${styles.zone} ${styles.journeyScene} ${motion.className}`}
      style={motion.style}
      aria-labelledby="profile-v2-effort-title"
      data-testid="profile-v2-effort"
    >
      <header className={styles.zoneHeader}>
        <div>
          <p className={styles.journeyStepIndex}>
            <span className={styles.journeyStepBadge}>{effortNav.step.replace(/^0/, "")}</span>
            <span id="profile-v2-effort-title">{PROFILE_V2_COPY.zones.effort.title}</span>
          </p>
          <p className={styles.zoneLead}>{PROFILE_V2_COPY.zones.effort.lead}</p>
        </div>
      </header>

      <div className={styles.effortLayout}>
        <div className={styles.effortFocus}>
          <span className={styles.effortCompass} aria-hidden>
            <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
              <circle cx="14" cy="14" r="12.5" stroke="currentColor" strokeWidth="1.25" />
              <path d="M14 6.5v15M6.5 14h15" stroke="currentColor" strokeWidth="1.25" />
              <path d="M14 5.5l2.2 5.2L14 14l-2.2-3.3L14 5.5z" fill="currentColor" />
            </svg>
          </span>
          <p className={styles.effortVector} data-testid="profile-v2-effort-vector">
            {effortVector}
          </p>
        </div>

        {spheres.length ? (
          <div className={styles.effortSpheres} data-testid="profile-v2-effort-spheres">
            <p className={styles.effortSpheresLabel}>{PROFILE_V2_COPY.zones.effort.spheresLabel}</p>
            <ul className={styles.effortSphereRow}>
              {spheres.map((sphere, index) => (
                <li
                  key={sphere.id}
                  className={`${styles.effortSphereChip} ${profileMotionStyles.staggerItem}`}
                  style={profileMotionStaggerDelay(index, 100)}
                  title={sphere.title}
                >
                  <span
                    className={styles.effortSphereDot}
                    style={sphere.accent ? { background: sphere.accent } : undefined}
                    aria-hidden
                  />
                  <span>{sphere.title}</span>
                </li>
              ))}
            </ul>
          </div>
        ) : null}
      </div>
    </section>
  );
}
