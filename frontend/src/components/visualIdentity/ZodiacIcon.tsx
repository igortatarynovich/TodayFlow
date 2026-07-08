"use client";

import { resolveZodiacSignId } from "@/lib/zodiacKnowledge";
import {
  VISUAL_ASSET_MODE,
  zodiacAssetPath,
  type ZodiacSlug,
} from "@/lib/visualIdentity/registry";
import { InlineZodiacIcon } from "./icons/InlineZodiacIcons";
import type { SymbolicIconProps } from "./icons/iconProps";

export type ZodiacIconProps = SymbolicIconProps & {
  sign: string | null | undefined;
};

function isZodiacSlug(id: string): id is ZodiacSlug {
  return [
    "aries",
    "taurus",
    "gemini",
    "cancer",
    "leo",
    "virgo",
    "libra",
    "scorpio",
    "sagittarius",
    "capricorn",
    "aquarius",
    "pisces",
  ].includes(id);
}

function ZodiacAssetSymbol({
  slug,
  size,
  className,
  stroke,
}: {
  slug: ZodiacSlug;
  size: number;
  className?: string;
  stroke: string;
}) {
  const tint = stroke === "currentColor" ? "currentColor" : stroke;
  return (
    <span
      data-testid="zodiac-symbol"
      aria-hidden
      className={className}
      style={{
        width: size,
        height: size,
        display: "inline-block",
        flexShrink: 0,
        backgroundColor: tint,
        color: tint,
        maskImage: `url(${zodiacAssetPath(slug)})`,
        WebkitMaskImage: `url(${zodiacAssetPath(slug)})`,
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

export function ZodiacIcon({ sign, size = 28, className, stroke = "currentColor" }: ZodiacIconProps) {
  const slug = resolveZodiacSignId(sign ?? "", null);
  if (!slug || !isZodiacSlug(slug)) return null;

  if (VISUAL_ASSET_MODE === "asset") {
    return <ZodiacAssetSymbol slug={slug} size={size} className={className} stroke={stroke} />;
  }

  return (
    <span
      data-testid="zodiac-symbol"
      className={className}
      style={{ display: "inline-flex", width: size, height: size, flexShrink: 0 }}
    >
      <InlineZodiacIcon slug={slug} size={size} stroke={stroke} />
    </span>
  );
}
