"use client";

import styles from "./profileV0.module.css";

export type InsightLine = { label: string; value: string };

export function ProfileV0InsightLines({ lines }: { lines: InsightLine[] }) {
  return (
    <ul className={styles.insightLines}>
      {lines.map((line) => (
        <li key={line.label} className={styles.insightLine}>
          <span className={styles.insightLineLabel}>{line.label}</span>
          <span className={styles.insightLineValue}>{line.value}</span>
        </li>
      ))}
    </ul>
  );
}
