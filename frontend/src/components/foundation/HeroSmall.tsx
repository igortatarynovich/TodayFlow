"use client";

import type { ReactNode } from "react";
import { SacredGeometryBackdrop } from "@/components/visualIdentity/SacredGeometryBackdrop";
import { profileMotionStyles } from "@/components/foundation/ProfileMotion";
import styles from "./heroSmall.module.css";

export type HeroSmallProps = {
  symbol: ReactNode;
  title: string;
  kicker?: string;
  meta?: string | null;
  aside?: ReactNode;
  footer?: ReactNode;
  /** Inside parent card — no outer chrome. */
  flush?: boolean;
  titleAs?: "h1" | "h2";
  ariaLabel?: string;
  className?: string;
  titleTestId?: string;
};

export function HeroSmall({
  symbol,
  title,
  kicker,
  meta,
  aside,
  footer,
  flush = false,
  titleAs = "h2",
  ariaLabel,
  className,
  titleTestId,
}: HeroSmallProps) {
  const rootClass = [styles.heroSmall, flush ? styles.heroSmallFlush : "", className ?? ""].filter(Boolean).join(" ");
  const TitleTag = titleAs;

  return (
    <header className={rootClass} aria-label={ariaLabel ?? title} data-testid="hero-small">
      {!flush ? (
        <div className={styles.geometry}>
          <SacredGeometryBackdrop emphasis="soft" preset="profile" />
        </div>
      ) : null}

      <div className={`${styles.row} ${profileMotionStyles.heroEnter}`}>
        <div className={styles.symbol}>{symbol}</div>

        <div className={styles.main}>
          {kicker ? <p className={styles.kicker}>{kicker}</p> : null}
          <TitleTag className={styles.title} data-testid={titleTestId}>
            {title}
          </TitleTag>
          {meta ? <p className={styles.meta}>{meta}</p> : null}
        </div>

        {aside ? <div className={styles.aside}>{aside}</div> : null}
      </div>

      {footer ? <div className={styles.footer}>{footer}</div> : null}
    </header>
  );
}

export { styles as heroSmallStyles };
