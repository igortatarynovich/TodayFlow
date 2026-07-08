"use client";

import type { CSSProperties } from "react";
import styles from "./compatibilityOrbitSymbol.module.css";

/** Foundation G2 orbit primitive — Compatibility hero symbol slot (48px). */
export function CompatibilityOrbitSymbol({
  size = 48,
  className,
  stroke = "currentColor",
}: {
  size?: number;
  className?: string;
  stroke?: string;
}) {
  const style = { width: size, height: size, color: stroke } as CSSProperties;
  return (
    <svg
      viewBox="0 0 48 48"
      fill="none"
      className={[styles.root, className].filter(Boolean).join(" ")}
      style={style}
      aria-hidden
      data-testid="compatibility-orbit-symbol"
    >
      <circle cx="24" cy="24" r="17" stroke="currentColor" strokeWidth="1.25" opacity="0.22" />
      <ellipse cx="24" cy="24" rx="21" ry="11" stroke="currentColor" strokeWidth="1.25" opacity="0.34" />
      <ellipse
        cx="24"
        cy="24"
        rx="21"
        ry="11"
        stroke="currentColor"
        strokeWidth="1.25"
        opacity="0.34"
        transform="rotate(62 24 24)"
      />
      <circle cx="24" cy="24" r="3.5" fill="currentColor" opacity="0.55" />
    </svg>
  );
}
