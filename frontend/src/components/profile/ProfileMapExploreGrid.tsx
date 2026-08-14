"use client";

import Link from "next/link";
import { PROFILE_MAP_EXPLORE_CARDS } from "@/lib/profileMapsExplore";
import editorialStyles from "@/design-system/profile/dsProfileEditorial.module.css";
import quickMapStyles from "@/design-system/profile/dsProfileQuickMap.module.css";

type Props = {
  variant?: "editorial" | "quickMap";
  ariaLabel?: string;
};

export function ProfileMapExploreGrid({ variant = "editorial", ariaLabel = "Открыть карты" }: Props) {
  const styles = variant === "quickMap" ? quickMapStyles : editorialStyles;

  return (
    <nav className={styles.mapsExploreGrid} aria-label={ariaLabel} data-testid="profile-maps-explore-grid">
      {PROFILE_MAP_EXPLORE_CARDS.map((card) => (
        <Link
          key={card.id}
          href={card.href}
          className={`${styles.mapsExploreCard} ${card.primary ? styles.mapsExploreCardPrimary : ""}`.trim()}
        >
          <span className={styles.mapsExploreCardTitle}>{card.title}</span>
          <span className={styles.mapsExploreCardDesc}>{card.desc}</span>
        </Link>
      ))}
    </nav>
  );
}
