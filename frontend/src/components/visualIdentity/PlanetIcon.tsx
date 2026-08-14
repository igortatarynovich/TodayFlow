"use client";

import {
  VISUAL_ASSET_MODE,
  planetAssetPath,
  planetHasPhotoAsset,
  planetPhotoPath,
  resolvePlanetSlug,
  type PlanetSlug,
} from "@/lib/visualIdentity/registry";
import { InlinePlanetIcon } from "./icons/InlinePlanetIcons";
import type { SymbolicIconProps } from "./icons/iconProps";

export type PlanetIconProps = SymbolicIconProps & {
  planet: string | null | undefined;
  /**
   * Photo fit inside the size box.
   * `cover` fills a circular slot (natal disc); `contain` keeps full art + padding.
   */
  fit?: "contain" | "cover";
};

function PlanetPhotoSymbol({
  slug,
  size,
  className,
  fit = "contain",
}: {
  slug: PlanetSlug;
  size: number;
  className?: string;
  fit?: "contain" | "cover";
}) {
  const cover = fit === "cover";
  return (
    <span
      data-testid="planet-symbol"
      data-visual="photo"
      data-fit={fit}
      aria-hidden
      className={className}
      style={{
        width: size,
        height: size,
        display: "inline-flex",
        flexShrink: 0,
        alignItems: "center",
        justifyContent: "center",
        overflow: cover ? "hidden" : undefined,
        borderRadius: cover ? "50%" : undefined,
      }}
    >
      {/* eslint-disable-next-line @next/next/no-img-element -- static public WebP; size parity with prior mask slot */}
      <img
        src={planetPhotoPath(slug)}
        alt=""
        width={size}
        height={size}
        draggable={false}
        style={{
          width: size,
          height: size,
          objectFit: cover ? "cover" : "contain",
          objectPosition: "center",
          display: "block",
          borderRadius: cover ? "50%" : undefined,
        }}
      />
    </span>
  );
}

function PlanetSealSymbol({
  slug,
  size,
  className,
  stroke,
}: {
  slug: PlanetSlug;
  size: number;
  className?: string;
  stroke: string;
}) {
  const tint = stroke === "currentColor" ? "currentColor" : stroke;
  return (
    <span
      data-testid="planet-symbol"
      data-visual="seal"
      aria-hidden
      className={className}
      style={{
        width: size,
        height: size,
        display: "inline-block",
        flexShrink: 0,
        backgroundColor: tint,
        color: tint,
        maskImage: `url(${planetAssetPath(slug)})`,
        WebkitMaskImage: `url(${planetAssetPath(slug)})`,
        maskSize: "contain",
        WebkitMaskSize: "contain",
        maskRepeat: "no-repeat",
        WebkitMaskRepeat: "no-repeat",
        maskPosition: "center",
        WebkitMaskPosition: "center",
      }}
    />
  );
}

export function PlanetIcon({
  planet,
  size = 24,
  className,
  stroke = "currentColor",
  fit = "contain",
}: PlanetIconProps) {
  const slug = resolvePlanetSlug(planet);
  if (!slug) return null;

  if (VISUAL_ASSET_MODE === "asset") {
    if (planetHasPhotoAsset(slug)) {
      return <PlanetPhotoSymbol slug={slug} size={size} className={className} fit={fit} />;
    }
    return <PlanetSealSymbol slug={slug} size={size} className={className} stroke={stroke} />;
  }

  return (
    <span
      data-testid="planet-symbol"
      className={className}
      style={{ display: "inline-flex", width: size, height: size, flexShrink: 0 }}
    >
      <InlinePlanetIcon slug={slug} size={size} stroke={stroke} />
    </span>
  );
}
