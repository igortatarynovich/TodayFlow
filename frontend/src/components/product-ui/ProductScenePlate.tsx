"use client";

import {
  resolveProductScenePlate,
  type ProductScenePlateId,
} from "@/lib/productScenePlates";
import styles from "@/components/product-ui/ProductScenePlate.module.css";

export type ProductScenePlateProps = {
  plate: ProductScenePlateId;
  /** Override crop when a screen needs a tighter subject. */
  position?: string;
  /** Marketing service column — taller crop than journey cinema strip. */
  frame?: "default" | "landingService" | "landingHero";
  className?: string;
  testId?: string;
};

/**
 * Visible product plate from public inventory.
 * Cover-crops panoramic banners into journey scenes — not a faint wash.
 */
export function ProductScenePlate({
  plate,
  position,
  frame = "default",
  className = "",
  testId = "product-scene-plate",
}: ProductScenePlateProps) {
  const spec = resolveProductScenePlate(plate);
  if (!spec) return null;

  const aspectClass =
    frame === "landingService"
      ? styles.aspectLandingService
      : frame === "landingHero"
        ? styles.aspectLandingHero
        : spec.aspect === "square"
          ? styles.aspectSquare
          : spec.aspect === "wide"
            ? styles.aspectWide
            : styles.aspectCinema;

  const toneClass =
    spec.tone === "night" ? styles.toneNight : spec.tone === "dusk" ? styles.toneDusk : styles.toneDay;

  return (
    <div
      className={`${styles.root} ${aspectClass} ${toneClass} ${className}`.trim()}
      data-testid={testId}
      data-plate={spec.id}
      data-plate-tone={spec.tone}
      data-plate-frame={frame}
      aria-hidden
    >
      {/* eslint-disable-next-line @next/next/no-img-element -- static public inventory */}
      <img
        className={styles.image}
        src={spec.src}
        alt=""
        style={{ objectPosition: position ?? spec.position }}
        loading="lazy"
        decoding="async"
      />
      <div className={styles.veil} />
    </div>
  );
}
