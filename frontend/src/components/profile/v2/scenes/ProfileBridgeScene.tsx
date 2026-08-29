"use client";

import { useProfileMotionInView } from "@/components/foundation/ProfileMotion";
import { ProfileAtmosphere } from "@/components/profile/v2/ProfileAtmosphere";
import { PROFILE_V2_COPY, PROFILE_V2_DEPTH_NAV } from "@/components/profile/v2/profileV2SystemCopy";
import { DsButton } from "@/design-system";
import styles from "@/design-system/profile/dsProfileV2System.module.css";

export type ProfileBridgeSceneProps = {
  bridgeLine: string | null;
};

const bridgeNav = PROFILE_V2_DEPTH_NAV.find((s) => s.id === "bridge") ?? PROFILE_V2_DEPTH_NAV[4];

/**
 * Visual Modes #4 — Act 5 CTA-portal: why Today + one CTA (no second effort).
 */
export function ProfileBridgeScene({ bridgeLine }: ProfileBridgeSceneProps) {
  const motion = useProfileMotionInView<HTMLElement>(100);
  const copy = PROFILE_V2_COPY.zones.bridge;
  const line = bridgeLine?.trim() || copy.lead?.trim() || "";

  return (
    <section
      id="profile-v2-bridge"
      ref={motion.ref}
      className={`${styles.bridgeScene} ${styles.bridgeSceneModePortal} ${motion.className}`}
      style={motion.style}
      aria-labelledby="profile-v2-bridge-title"
      data-testid="profile-v2-bridge"
      data-visual-mode="bridge-portal"
    >
      <ProfileAtmosphere motif="bridge" />
      <div className={styles.bridgePortalBody}>
        <p className={styles.journeyStepIndex}>
          <span className={styles.journeyStepBadge}>{bridgeNav.step.replace(/^0/, "")}</span>
          <span id="profile-v2-bridge-title">{copy.title}</span>
        </p>
        {line ? (
          <p className={styles.bridgeHeadline} data-testid="profile-v2-bridge-line">
            {line}
          </p>
        ) : null}
        <DsButton
          href="/today"
          variant="primary"
          className={styles.bridgeAction}
          data-testid="profile-v2-open-today"
        >
          {copy.cta}
          <span aria-hidden> →</span>
        </DsButton>
      </div>
    </section>
  );
}
