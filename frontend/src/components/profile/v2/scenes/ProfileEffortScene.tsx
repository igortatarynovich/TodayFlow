"use client";

import {
  profileMotionStaggerDelay,
  profileMotionStyles,
  useProfileMotionInView,
} from "@/components/foundation/ProfileMotion";
import type { ProfileLifeSphere } from "@/components/profile/ProfileLifeSection";
import { ProfileAtmosphere } from "@/components/profile/v2/ProfileAtmosphere";
import { PROFILE_V2_COPY, PROFILE_V2_DEPTH_NAV } from "@/components/profile/v2/profileV2SystemCopy";
import styles from "@/components/profile/v2/profileV2System.module.css";

export type ProfileEffortSceneProps = {
  effortVector: string;
  lifeSpheres?: ProfileLifeSphere[];
};

const effortNav = PROFILE_V2_DEPTH_NAV.find((s) => s.id === "effort") ?? PROFILE_V2_DEPTH_NAV[3];

/**
 * Effort + readable sphere portraits (how / need / risk) — not skim chips.
 */
export function ProfileEffortScene({ effortVector, lifeSpheres = [] }: ProfileEffortSceneProps) {
  const spheres = lifeSpheres.filter((s) => s.title?.trim()).slice(0, 6);
  const motion = useProfileMotionInView<HTMLElement>(80);
  const copy = PROFILE_V2_COPY.zones.effort;

  return (
    <section
      id="profile-v2-effort"
      ref={motion.ref}
      className={`${styles.zone} ${styles.journeyScene} ${motion.className}`}
      style={motion.style}
      aria-labelledby="profile-v2-effort-title"
      data-testid="profile-v2-effort"
    >
      <ProfileAtmosphere motif="effort" />
      <header className={styles.zoneHeader}>
        <div>
          <p className={styles.journeyStepIndex}>
            <span className={styles.journeyStepBadge}>{effortNav.step.replace(/^0/, "")}</span>
            <span id="profile-v2-effort-title">{copy.title}</span>
          </p>
          <p className={styles.zoneLead}>{copy.lead}</p>
        </div>
      </header>

      <div className={styles.effortLayout}>
        <div className={styles.effortFocus}>
          <p className={styles.effortFocusLabel}>{copy.focusLabel}</p>
          <div className={styles.effortFocusCard}>
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
        </div>

        {spheres.length ? (
          <div className={styles.effortSpheres} data-testid="profile-v2-effort-spheres">
            <p className={styles.effortSpheresLabel}>{copy.spheresLabel}</p>
            <ul className={styles.effortSphereReadGrid}>
              {spheres.map((sphere, index) => {
                const how = sphere.how?.trim() || "";
                const need = sphere.need?.trim() || "";
                const risk = sphere.risk?.trim() || "";
                const turnsOn = sphere.turnsOn?.trim() || "";
                const helps = sphere.helps?.trim() || "";
                return (
                  <li
                    key={sphere.id}
                    className={`${styles.effortSphereReadCard} ${profileMotionStyles.staggerItem}`}
                    style={profileMotionStaggerDelay(index, 90)}
                    data-testid={`profile-v2-effort-sphere-${sphere.id}`}
                  >
                    <p className={styles.effortSphereTitle}>
                      <span
                        className={styles.effortSphereDot}
                        style={sphere.accent ? { background: sphere.accent, display: "inline-block", marginRight: "0.45rem", marginTop: 0, verticalAlign: "middle" } : undefined}
                        aria-hidden
                      />
                      {sphere.title}
                    </p>
                    {how ? (
                      <p className={styles.effortSphereHow}>
                        <span className={styles.effortSphereMetaLabel}>{copy.sphereHow}</span>
                        {how}
                      </p>
                    ) : null}
                    {need ? (
                      <p className={styles.effortSphereNeedFull}>
                        <span className={styles.effortSphereMetaLabel}>{copy.sphereNeed}</span>
                        {need}
                      </p>
                    ) : null}
                    {risk ? (
                      <p className={styles.effortSphereRisk}>
                        <span className={styles.effortSphereMetaLabel}>{copy.sphereRisk}</span>
                        {risk}
                      </p>
                    ) : null}
                    {turnsOn ? (
                      <p className={styles.effortSphereNeedFull}>
                        <span className={styles.effortSphereMetaLabel}>{copy.sphereTurnsOn}</span>
                        {turnsOn}
                      </p>
                    ) : null}
                    {helps ? (
                      <p className={styles.effortSphereNeedFull}>
                        <span className={styles.effortSphereMetaLabel}>{copy.sphereHelps}</span>
                        {helps}
                      </p>
                    ) : null}
                  </li>
                );
              })}
            </ul>
          </div>
        ) : null}
      </div>
    </section>
  );
}
