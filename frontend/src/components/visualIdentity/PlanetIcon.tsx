"use client";

import {
  VISUAL_ASSET_MODE,
  planetAssetPath,
  resolvePlanetSlug,
  type PlanetSlug,
} from "@/lib/visualIdentity/registry";
import { InlinePlanetIcon } from "./icons/InlinePlanetIcons";
import type { SymbolicIconProps } from "./icons/iconProps";

export type PlanetIconProps = SymbolicIconProps & {
  planet: string | null | undefined;
};

function PlanetAssetSymbol({
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

export function PlanetIcon({ planet, size = 24, className, stroke = "currentColor" }: PlanetIconProps) {
  const slug = resolvePlanetSlug(planet);
  if (!slug) return null;

  if (VISUAL_ASSET_MODE === "asset") {
    return <PlanetAssetSymbol slug={slug} size={size} className={className} stroke={stroke} />;
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
