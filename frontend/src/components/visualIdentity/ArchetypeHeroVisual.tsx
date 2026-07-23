"use client";

import { useState } from "react";
import { ArchetypeSymbol } from "@/components/visualIdentity/ArchetypeSymbol";
import {
  archetypeIllustrationSrc,
  resolveArchetypeIllustrationSlug,
} from "@/lib/visualIdentity/registry";

export type ArchetypeHeroVisualProps = {
  seed: string | null | undefined;
  /** Line-symbol size when illustration missing / failed. */
  symbolSize?: number;
  className?: string;
  portraitClassName?: string;
  symbolClassName?: string;
};

/**
 * Profile Hero visual: premium WebP when mapped + file loads,
 * otherwise live ArchetypeSymbol placeholder in the same slot.
 * Portraits are pre-cropped 4:5 for the arch (`scripts/crop_archetype_heroes.py`).
 */
export function ArchetypeHeroVisual({
  seed,
  symbolSize = 152,
  className,
  portraitClassName,
  symbolClassName,
}: ArchetypeHeroVisualProps) {
  const slug = resolveArchetypeIllustrationSlug(seed);
  const src = archetypeIllustrationSrc(seed);
  const [failed, setFailed] = useState(false);
  const showPortrait = Boolean(src) && !failed;

  if (showPortrait && src) {
    return (
      <div
        className={className}
        data-testid="archetype-hero-visual"
        data-visual="portrait"
        data-illustration={slug ?? undefined}
      >
        {/* eslint-disable-next-line @next/next/no-img-element -- static public WebP; onError → symbol */}
        <img
          src={src}
          alt=""
          className={portraitClassName}
          data-testid="archetype-hero-portrait"
          data-illustration={slug ?? undefined}
          onError={() => setFailed(true)}
        />
      </div>
    );
  }

  return (
    <div className={className} data-testid="archetype-hero-visual" data-visual="symbol">
      <ArchetypeSymbol
        seed={seed}
        size={symbolSize}
        stroke="currentColor"
        className={symbolClassName}
      />
    </div>
  );
}
