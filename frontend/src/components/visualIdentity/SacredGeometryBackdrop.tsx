"use client";

import { FoundationGeometryLayers } from "@/components/foundation/geometry/FoundationGeometryLayers";
import {
  resolveGeometryPreset,
  type FoundationGeometryPreset,
  type FoundationGeometryTone,
} from "@/lib/foundationGeometry";
import styles from "./sacredGeometry.module.css";

export type SacredGeometryBackdropProps = {
  /** Сильнее орбиты за primary-героем */
  emphasis?: "soft" | "strong";
  /** §3.3 composition — default: profile (soft) or portal (strong). */
  preset?: FoundationGeometryPreset;
  /** Dark portal surfaces (Surface D). */
  tone?: FoundationGeometryTone;
};

export function SacredGeometryBackdrop({
  emphasis = "soft",
  preset,
  tone = "light",
}: SacredGeometryBackdropProps) {
  const resolvedPreset = resolveGeometryPreset(preset, emphasis);
  const strong = emphasis === "strong";

  return (
    <div
      className={[
        styles.backdrop,
        strong ? styles.strong : styles.soft,
        tone === "dark" ? styles.dark : "",
      ]
        .filter(Boolean)
        .join(" ")}
      aria-hidden
      data-testid="foundation-geometry-backdrop"
      data-geometry-preset={resolvedPreset}
    >
      <svg className={styles.svg} viewBox="0 0 400 280" preserveAspectRatio="xMidYMid slice">
        <FoundationGeometryLayers preset={resolvedPreset} emphasis={emphasis} tone={tone} />
      </svg>
    </div>
  );
}
