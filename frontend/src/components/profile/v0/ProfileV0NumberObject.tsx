"use client";

import type { ProfileV0NumberRow } from "@/lib/profilePage/buildProfileV0Data";
import styles from "./profileV0.module.css";

export function ProfileV0NumberObject({
  row,
  variant = "default",
}: {
  row: ProfileV0NumberRow;
  variant?: "default" | "hero";
}) {
  if (variant === "hero") {
    return (
      <article className={styles.numberHero}>
        <div className={styles.numberHeroRing} aria-hidden>
          <span className={styles.numberHeroValue}>{row.value}</span>
        </div>
        <p className={styles.numberHeroCaption}>{row.caption}</p>
        {row.blurb ? <p className={styles.numberHeroBlurb}>{row.blurb}</p> : null}
      </article>
    );
  }

  return (
    <article className={styles.numberSecondary}>
      <p className={styles.numberSecondaryValue}>{row.value}</p>
      <p className={styles.numberSecondaryCaption}>{row.caption}</p>
      {row.blurb ? <p className={styles.numberSecondaryBlurb}>{row.blurb}</p> : null}
    </article>
  );
}
