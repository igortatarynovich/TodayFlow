"use client";

import type { ReactNode } from "react";
import { ArchetypeSymbol } from "@/components/visualIdentity/ArchetypeSymbol";
import { SacredGeometryBackdrop } from "@/components/visualIdentity/SacredGeometryBackdrop";
import { SurfaceInsight } from "@/components/foundation/SurfaceInsight";
import { profileMotionStaggerDelay, profileMotionStyles } from "@/components/foundation/ProfileMotion";
import styles from "./heroLarge.module.css";

export type HeroLargePillar = {
  id: string;
  label: string;
  accent?: boolean;
};

export type HeroLargeTrait = {
  title: string;
  subtitle: string;
};

export type HeroLargeProps = {
  /** Archetype seed for symbol */
  symbolSeed: string;
  title: string;
  kicker?: string;
  sectionLabel?: string;
  metaLine?: string | null;
  digest?: string | null;
  poeticCaption?: string | null;
  pillars?: HeroLargePillar[];
  traits?: HeroLargeTrait[];
  topAction?: ReactNode;
  ariaLabel?: string;
  /** When false, hero does not break out of shell gutter */
  edgeToEdge?: boolean;
  className?: string;
};

export function HeroLarge({
  symbolSeed,
  title,
  kicker,
  sectionLabel,
  metaLine,
  digest,
  poeticCaption,
  pillars,
  traits,
  topAction,
  ariaLabel,
  edgeToEdge = true,
  className,
}: HeroLargeProps) {
  const rootClass = [styles.heroLarge, !edgeToEdge ? styles.heroLargeFlush : "", className ?? ""]
    .filter(Boolean)
    .join(" ");

  return (
    <header className={rootClass} aria-label={ariaLabel ?? title} data-testid="hero-large">
      <div className={styles.geometry}>
        <SacredGeometryBackdrop emphasis="soft" preset="profile" />
      </div>
      <div className={styles.fade} aria-hidden />

      {kicker || topAction ? (
        <div className={styles.topBar}>
          {kicker ? <p className={styles.kicker}>{kicker}</p> : <span />}
          {topAction ?? null}
        </div>
      ) : null}

      <div className={`${styles.content} ${profileMotionStyles.heroEnter}`}>
        <ArchetypeSymbol
          seed={symbolSeed}
          size={120}
          className={`${styles.symbol} ${profileMotionStyles.heroSymbolEnter}`}
          stroke="currentColor"
        />

        {pillars?.length ? (
          <div className={styles.pillars}>
            {pillars.map((pillar, index) => (
              <p
                key={pillar.id}
                className={`${styles.pillar} ${pillar.accent ? styles.pillarAccent : ""} ${profileMotionStyles.staggerItem}`.trim()}
                style={profileMotionStaggerDelay(index, 120)}
              >
                {pillar.label}
              </p>
            ))}
          </div>
        ) : null}

        {sectionLabel ? <p className={styles.sectionLabel}>{sectionLabel}</p> : null}
        <h1 className={styles.title}>{title}</h1>

        {poeticCaption ? <p className={styles.poetic}>{poeticCaption}</p> : null}
        {metaLine ? <p className={styles.meta}>{metaLine}</p> : null}
        {digest ? <p className={styles.digest}>{digest}</p> : null}

        {traits?.length ? (
          <ul className={styles.traits}>
            {traits.map((trait, index) => (
              <li
                key={`${trait.title}-${trait.subtitle}`}
                className={`${styles.trait} ${profileMotionStyles.staggerItem}`}
                style={profileMotionStaggerDelay(index, 180)}
              >
                <span className={styles.traitLabel}>{trait.title}</span>
                <span className={styles.traitText}>{trait.subtitle}</span>
              </li>
            ))}
          </ul>
        ) : null}
      </div>
    </header>
  );
}

/** Foundation insight panels for FirstDay / onboarding strips */
export function HeroLargeInsightPanel({
  eyebrow,
  children,
  className,
}: {
  eyebrow: string;
  children: ReactNode;
  className?: string;
}) {
  return (
    <SurfaceInsight eyebrow={eyebrow} className={className}>
      {children}
    </SurfaceInsight>
  );
}

export function HeroLargeChipRow({ items }: { items: string[] }) {
  if (!items.length) return null;
  return (
    <div className={styles.chipRow}>
      {items.map((item, index) => (
        <span
          key={item}
          className={`${styles.chip} ${profileMotionStyles.staggerItem}`}
          style={profileMotionStaggerDelay(index, 120)}
        >
          {item}
        </span>
      ))}
    </div>
  );
}

export { styles as heroLargeStyles };
