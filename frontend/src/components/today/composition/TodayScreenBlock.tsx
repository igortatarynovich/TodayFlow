"use client";

import type { ReactNode } from "react";
import { DsCard } from "@/design-system/primitives/DsCard";
import { joinClass } from "@/design-system/utils/joinClass";
import styles from "@/components/today/composition/TodayScreenBlock.module.css";

type BlockProps = {
  /** Eyebrow — muted label (FOUNDATION_UI §16.2). */
  eyebrow?: string | null;
  /** Primary — short main value; not a paragraph. */
  primary?: ReactNode;
  /** Optional detail / caption. */
  detail?: ReactNode;
  children?: ReactNode;
  className?: string;
  testId?: string;
  as?: "div" | "section" | "article" | "button";
  onClick?: () => void;
};

/**
 * Today ScreenFlow Block — `DsCard glass + compact` (FOUNDATION_UI §16).
 * Content SoT stays in TODAY_SCREEN_SCENARIO_V3; this is visual grammar only.
 */
export function TodayScreenBlock({
  eyebrow = null,
  primary = null,
  detail = null,
  children = null,
  className,
  testId,
  as = "div",
  onClick,
}: BlockProps) {
  return (
    <DsCard
      variant="glass"
      size="compact"
      as={as}
      className={joinClass(styles.block, className)}
      testId={testId}
      onClick={onClick}
    >
      {eyebrow ? <p className={styles.eyebrow}>{eyebrow}</p> : null}
      {primary != null && primary !== false && primary !== "" ? (
        <div className={styles.primary}>{primary}</div>
      ) : null}
      {detail != null && detail !== false && detail !== "" ? (
        <div className={styles.detail}>{detail}</div>
      ) : null}
      {children}
    </DsCard>
  );
}

type StackProps = {
  children: ReactNode;
  className?: string;
  testId?: string;
};

/** Vertical rhythm between Blocks — `--tf-ds-space-5` / `6` (§16.3). */
export function TodayScreenBlockStack({ children, className, testId }: StackProps) {
  return (
    <div className={joinClass(styles.stack, className)} data-testid={testId}>
      {children}
    </div>
  );
}
