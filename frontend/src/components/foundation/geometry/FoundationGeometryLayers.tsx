"use client";

import type {
  FoundationGeometryEmphasis,
  FoundationGeometryPreset,
  FoundationGeometryTone,
} from "@/lib/foundationGeometry";
import styles from "./foundationGeometry.module.css";

type Props = {
  preset: FoundationGeometryPreset;
  emphasis?: FoundationGeometryEmphasis;
  tone?: FoundationGeometryTone;
};

/** G1–G5 SVG layers for Foundation geometry compositions (§3.3). */
export function FoundationGeometryLayers({ preset, emphasis = "soft", tone = "light" }: Props) {
  const gridId = `tf-geo-grid-${preset}`;

  return (
    <g
      className={styles.layers}
      data-geometry-preset={preset}
      data-geometry-emphasis={emphasis}
      data-geometry-tone={tone}
    >
      {preset === "portal" ? (
        <>
          <defs>
            <pattern id={gridId} width="20" height="20" patternUnits="userSpaceOnUse">
              <path d="M 20 0 L 0 0 0 20" className={styles.g3} />
            </pattern>
          </defs>
          <rect width="400" height="280" fill={`url(#${gridId})`} className={styles.g3Fill} />
        </>
      ) : null}

      {preset === "profile" ? (
        <>
          <circle cx="200" cy="120" r="96" className={styles.g1} />
          <circle cx="200" cy="120" r="64" className={styles.g1} />
          <circle cx="200" cy="120" r="36" className={styles.g1Inner} />
          <ellipse cx="200" cy="120" rx="120" ry="44" className={styles.g2} transform="rotate(-18 200 120)" />
          <path d="M80 60 L320 180" className={styles.g4} />
          <path d="M320 60 L80 180" className={styles.g4Faint} />
          <circle cx="296" cy="72" r="3" className={styles.g4Node} />
          <circle cx="104" cy="168" r="3" className={styles.g4Node} />
        </>
      ) : null}

      {preset === "today" ? (
        <>
          <ellipse cx="200" cy="130" rx="118" ry="42" className={styles.g2} transform="rotate(-14 200 130)" />
          <ellipse cx="200" cy="130" rx="92" ry="32" className={styles.g2Inner} transform="rotate(22 200 130)" />
          <circle cx="200" cy="130" r="28" className={styles.g1Inner} />
        </>
      ) : null}

      {preset === "portal" ? (
        <>
          <circle cx="200" cy="140" r="88" className={styles.g1} />
          <circle cx="200" cy="140" r="56" className={styles.g1Inner} />
          <ellipse cx="200" cy="140" rx="130" ry="48" className={styles.g2} transform="rotate(-12 200 140)" />
          <ellipse cx="200" cy="140" rx="104" ry="36" className={styles.g2Inner} transform="rotate(24 200 140)" />
          <path d="M40 140 L360 140" className={styles.g4} />
          <path d="M200 24 L200 256" className={styles.g4} />
          <path d="M72 52 L328 228" className={styles.g4Faint} />
          <path d="M328 52 L72 228" className={styles.g4Faint} />
          <circle cx="300" cy="68" r="3" className={styles.g4Node} />
          <circle cx="100" cy="212" r="3" className={styles.g4Node} />
        </>
      ) : null}
    </g>
  );
}

/** G5 radial vignette — optional overlay (hero fade uses CSS elsewhere). */
export function FoundationRadialFade({ className }: { className?: string }) {
  return <div className={[styles.g5, className].filter(Boolean).join(" ")} aria-hidden />;
}
