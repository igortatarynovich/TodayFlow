"use client";

import type { ReactNode } from "react";
import { SacredGeometryBackdrop } from "@/components/visualIdentity/SacredGeometryBackdrop";
import { profileMotionStyles } from "@/components/foundation/ProfileMotion";
import styles from "./heroMedium.module.css";

export type HeroMediumPillar = {
  id: string;
  label: string;
  icon?: ReactNode;
};

export type HeroMediumProps = {
  symbol: ReactNode;
  title: string;
  kicker?: string;
  subline?: string | null;
  pillars?: HeroMediumPillar[];
  loading?: boolean;
  loadingText?: string;
  /** Nested inside Today day-anchor card — skips full viewport height. */
  embedded?: boolean;
  ariaLabel?: string;
  className?: string;
  /** Preserves Today entity test hooks when wired from composition surface. */
  titleTestId?: string;
};

export function HeroMedium({
  symbol,
  title,
  kicker,
  subline,
  pillars,
  loading = false,
  loadingText,
  embedded = false,
  ariaLabel,
  className,
  titleTestId,
}: HeroMediumProps) {
  const rootClass = [styles.heroMedium, embedded ? styles.heroMediumEmbedded : "", className ?? ""]
    .filter(Boolean)
    .join(" ");

  return (
    <header className={rootClass} aria-label={ariaLabel ?? title} data-testid="hero-medium">
      {!embedded ? (
        <>
          <div className={styles.geometry}>
            <SacredGeometryBackdrop emphasis="soft" preset="today" />
          </div>
          <div className={styles.fade} aria-hidden />
        </>
      ) : null}

      <div className={`${styles.content} ${profileMotionStyles.heroEnter}`}>
        <div className={styles.symbol}>{symbol}</div>

        {kicker ? <p className={styles.kicker}>{kicker}</p> : null}

        {loading ? (
          <p className={styles.loading}>{loadingText ?? "Загрузка…"}</p>
        ) : (
          <>
            <h2 className={styles.title} data-testid={titleTestId}>
              {title}
            </h2>
            {subline ? <p className={styles.subline}>{subline}</p> : null}
          </>
        )}

        {!loading && pillars?.length ? (
          <div className={styles.pillars}>
            {pillars.map((pillar) => (
              <p key={pillar.id} className={styles.pillar}>
                {pillar.icon ? <span className={styles.pillarIcon}>{pillar.icon}</span> : null}
                {pillar.label}
              </p>
            ))}
          </div>
        ) : null}
      </div>
    </header>
  );
}

export { styles as heroMediumStyles };
