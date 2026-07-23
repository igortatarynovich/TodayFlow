"use client";

import Link from "next/link";
import { useProfileMotionInView } from "@/components/foundation/ProfileMotion";
import { ProfileAtmosphere } from "@/components/profile/v2/ProfileAtmosphere";
import { PROFILE_V2_COPY, PROFILE_V2_DEPTH_NAV } from "@/components/profile/v2/profileV2SystemCopy";
import styles from "@/components/profile/v2/profileV2System.module.css";

export type ProfileBridgeSceneProps = {
  bridgeLine: string | null;
};

const bridgeNav = PROFILE_V2_DEPTH_NAV.find((s) => s.id === "bridge") ?? PROFILE_V2_DEPTH_NAV[5];

export function ProfileBridgeScene({ bridgeLine }: ProfileBridgeSceneProps) {
  const motion = useProfileMotionInView<HTMLElement>(100);

  return (
    <section
      id="profile-v2-bridge"
      ref={motion.ref}
      className={`${styles.bridgeScene} ${motion.className}`}
      style={motion.style}
      aria-labelledby="profile-v2-bridge-title"
      data-testid="profile-v2-bridge"
    >
      <ProfileAtmosphere motif="bridge" />
      <p className={styles.journeyStepIndex}>
        <span className={styles.journeyStepBadge}>{bridgeNav.step.replace(/^0/, "")}</span>
        <span id="profile-v2-bridge-title">{PROFILE_V2_COPY.zones.bridge.title}</span>
      </p>
      {bridgeLine ? (
        <p className={styles.bridgeHeadline} data-testid="profile-v2-bridge-line">
          {bridgeLine}
        </p>
      ) : (
        <p className={styles.bridgeHeadline}>{PROFILE_V2_COPY.zones.bridge.lead}</p>
      )}
      <Link href="/today" className={styles.bridgeCta} data-testid="profile-v2-open-today">
        {PROFILE_V2_COPY.zones.bridge.cta}
        <span aria-hidden> →</span>
      </Link>
    </section>
  );
}
