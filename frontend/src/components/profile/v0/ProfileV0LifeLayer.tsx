"use client";

import type { ProfileV0LoveCard, ProfileV0MoneyCard } from "@/lib/profilePage/buildProfileV0SphereCards";
import { ProfileV0LoveObject } from "./ProfileV0LoveObject";
import { ProfileV0MoneyObject } from "./ProfileV0MoneyObject";
import styles from "./profileV0.module.css";

export function ProfileV0LifeLayer({ love, money }: { love: ProfileV0LoveCard | null; money: ProfileV0MoneyCard | null }) {
  if (!love && !money) return null;

  return (
    <section className={styles.profileGrid2} aria-label="Как это проявляется в жизни">
      {love ? (
        <div className={`${styles.profileCard} ${styles.profileLifeCardLove}`}>
          <ProfileV0LoveObject love={love} />
        </div>
      ) : null}
      {money ? (
        <div className={`${styles.profileCard} ${styles.profileLifeCardMoney}`}>
          <ProfileV0MoneyObject money={money} />
        </div>
      ) : null}
    </section>
  );
}
