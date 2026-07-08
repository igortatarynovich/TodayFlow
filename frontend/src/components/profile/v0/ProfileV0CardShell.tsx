"use client";

import { useState, type ReactNode } from "react";
import styles from "./profileV0.module.css";

export type ProfileCardTone = "insight" | "growth" | "growthLove" | "growthMoney" | "discovery";
export type ProfileBlockType = "insight" | "action" | "portal";

export type ProfileV0CardShellProps = {
  label: string;
  ctaLabel?: string;
  tone?: ProfileCardTone;
  blockType?: ProfileBlockType;
  children: ReactNode;
  expandContent?: ReactNode;
};

export function ProfileV0CardShell({
  label,
  ctaLabel = "Подробнее",
  tone = "insight",
  blockType = "insight",
  children,
  expandContent,
}: ProfileV0CardShellProps) {
  const [expanded, setExpanded] = useState(false);
  const canExpand = Boolean(expandContent);

  const shellClass = {
    insight: styles.cardInsight,
    growth: styles.cardGrowth,
    growthLove: styles.cardGrowthLove,
    growthMoney: styles.cardGrowthMoney,
    discovery: styles.cardDiscovery,
  }[tone];

  const blockClass = {
    insight: styles.blockInsight,
    action: styles.blockAction,
    portal: styles.blockPortal,
  }[blockType];

  return (
    <article className={`${styles.cardShell} ${shellClass} ${blockClass}`}>
      <p className={styles.cardLabel}>{label}</p>
      <div className={styles.cardBody}>{children}</div>

      {canExpand ? (
        <>
          {expanded ? <div className={styles.cardExpand}>{expandContent}</div> : null}
          <button
            type="button"
            className={styles.cardCtaLink}
            aria-expanded={expanded}
            onClick={() => setExpanded((v) => !v)}
          >
            {expanded ? "Свернуть" : ctaLabel}
          </button>
        </>
      ) : null}
    </article>
  );
}
