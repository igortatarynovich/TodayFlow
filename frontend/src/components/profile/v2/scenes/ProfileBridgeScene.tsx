"use client";

import Link from "next/link";
import { PROFILE_V2_COPY } from "@/components/profile/v2/profileV2SystemCopy";
import styles from "@/components/profile/v2/profileV2System.module.css";

export type ProfileBridgeSceneProps = {
  bridgeLine: string | null;
};

export function ProfileBridgeScene({ bridgeLine }: ProfileBridgeSceneProps) {
  return (
    <section
      id="profile-v2-bridge"
      className={styles.bridgeScene}
      aria-labelledby="profile-v2-bridge-title"
      data-testid="profile-v2-bridge"
    >
      <p id="profile-v2-bridge-title" className={styles.zoneLabel}>
        {PROFILE_V2_COPY.zones.bridge.title}
      </p>
      {bridgeLine ? (
        <p className={styles.bridgeLine} data-testid="profile-v2-bridge-line">
          {bridgeLine}
        </p>
      ) : (
        <p className={styles.zoneLead}>{PROFILE_V2_COPY.zones.bridge.lead}</p>
      )}
      <Link href="/today" className={styles.bridgeCta} data-testid="profile-v2-open-today">
        {PROFILE_V2_COPY.zones.bridge.cta}
        <span aria-hidden> →</span>
      </Link>
    </section>
  );
}
