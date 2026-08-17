"use client";

import { useState } from "react";
import {
  resolveZodiacIllustrationSlug,
  zodiacIllustrationPath,
} from "@/lib/visualIdentity/registry";
import { ZodiacIcon } from "./ZodiacIcon";

export type ZodiacIllustrationProps = {
  sign: string | null | undefined;
  /** Line-symbol size when illustration missing / failed. */
  symbolSize?: number;
  className?: string;
  portraitClassName?: string;
  symbolClassName?: string;
  alt?: string;
};

/**
 * Painterly zodiac portrait (WebP) with ZodiacIcon fallback.
 * Assets: `public/images/zodiac/{slug}.webp` via `scripts/crop_zodiac_illustrations.py`.
 * Line glyphs stay in ZodiacIcon for pills / small slots.
 */
export function ZodiacIllustration({
  sign,
  symbolSize = 64,
  className,
  portraitClassName,
  symbolClassName,
  alt = "",
}: ZodiacIllustrationProps) {
  const slug = resolveZodiacIllustrationSlug(sign);
  const src = slug ? zodiacIllustrationPath(slug) : null;
  const [failed, setFailed] = useState(false);
  const showPortrait = Boolean(src) && !failed;

  if (showPortrait && src && slug) {
    return (
      <div
        className={className}
        data-testid="zodiac-illustration"
        data-visual="portrait"
        data-sign={slug}
      >
        {/* eslint-disable-next-line @next/next/no-img-element -- static public WebP; onError → glyph */}
        <img
          src={src}
          alt={alt}
          className={portraitClassName}
          data-testid="zodiac-illustration-portrait"
          data-sign={slug}
          onError={() => setFailed(true)}
        />
      </div>
    );
  }

  return (
    <div className={className} data-testid="zodiac-illustration" data-visual="symbol">
      <ZodiacIcon sign={sign} size={symbolSize} className={symbolClassName} stroke="currentColor" />
    </div>
  );
}
