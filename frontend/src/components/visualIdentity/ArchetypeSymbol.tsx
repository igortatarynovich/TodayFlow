"use client";

import {
  VISUAL_ASSET_MODE,
  archetypeAssetPath,
  resolveArchetypeSlug,
  type ArchetypeSlug,
} from "@/lib/visualIdentity/registry";
import { InlineArchetypeIcon } from "./icons/InlineArchetypeIcons";
import type { SymbolicIconProps } from "./icons/iconProps";

export type ArchetypeSymbolProps = SymbolicIconProps & {
  seed: string | null | undefined;
};

function ArchetypeAssetSymbol({
  slug,
  size,
  className,
  stroke,
}: {
  slug: ArchetypeSlug;
  size: number;
  className?: string;
  stroke: string;
}) {
  const tint = stroke === "currentColor" ? "currentColor" : stroke;
  return (
    <span
      data-testid="archetype-symbol"
      aria-hidden
      className={className}
      style={{
        width: size,
        height: size,
        display: "inline-block",
        flexShrink: 0,
        backgroundColor: tint,
        color: tint,
        maskImage: `url(${archetypeAssetPath(slug)})`,
        WebkitMaskImage: `url(${archetypeAssetPath(slug)})`,
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

export function ArchetypeSymbol({ seed, size = 56, className, stroke = "#5b4630" }: ArchetypeSymbolProps) {
  const slug: ArchetypeSlug = resolveArchetypeSlug(seed);

  if (VISUAL_ASSET_MODE === "asset") {
    return <ArchetypeAssetSymbol slug={slug} size={size} className={className} stroke={stroke} />;
  }

  return (
    <span
      data-testid="archetype-symbol"
      className={className}
      style={{ display: "inline-flex", width: size, height: size, flexShrink: 0 }}
    >
      <InlineArchetypeIcon slug={slug} size={size} stroke={stroke} />
    </span>
  );
}
