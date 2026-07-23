"use client";

import styles from "./profileAtmosphere.module.css";

export type ProfileAtmosphereMotif = "why" | "insight" | "effort" | "bridge" | "natal";

export type ProfileAtmosphereProps = {
  motif: ProfileAtmosphereMotif;
  className?: string;
};

/**
 * Quiet decorative wash for Profile Journey scenes.
 * Images via CSS background only — never <img> in this layer.
 */
export function ProfileAtmosphere({ motif, className }: ProfileAtmosphereProps) {
  return (
    <div
      className={[styles.root, styles[`motif_${motif}`], className].filter(Boolean).join(" ")}
      aria-hidden
      data-profile-atmosphere={motif}
    />
  );
}
