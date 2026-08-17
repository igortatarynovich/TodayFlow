"use client";

import { resolveZodiacSignId } from "@/lib/zodiacKnowledge";
import {
  VISUAL_ASSET_MODE,
  zodiacAssetPath,
  zodiacIllustrationPath,
  type ZodiacSlug,
} from "@/lib/visualIdentity/registry";
import { InlineZodiacIcon } from "./icons/InlineZodiacIcons";
import type { SymbolicIconProps } from "./icons/iconProps";

export type ZodiacIconProps = SymbolicIconProps & {
  sign: string | null | undefined;
  /** `illustration` = painterly portrait; default gold seal. */
  variant?: "seal" | "illustration";
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
  variant,
}: {
  slug: ZodiacSlug;
  size: number;
  className?: string;
  stroke: string;
  variant: "seal" | "illustration";
}) {
  const src = variant === "illustration" ? zodiacIllustrationPath(slug) : zodiacAssetPath(slug);
  return (
    <span
      data-testid="zodiac-symbol"
      data-visual={variant}
      aria-hidden
      className={className}
      style={{
        width: size,
        height: size,
        display: "inline-flex",
        flexShrink: 0,
        alignItems: "center",
        justifyContent: "center",
        overflow: variant === "illustration" ? "hidden" : undefined,
        borderRadius: variant === "illustration" ? "50%" : undefined,
      }}
    >
      {/* eslint-disable-next-line @next/next/no-img-element -- static public WebP; size parity with prior mask slot */}
      <img
        src={src}
        alt=""
        width={size}
        height={size}
        draggable={false}
        style={{
          width: size,
          height: size,
          objectFit: variant === "illustration" ? "cover" : "contain",
          display: "block",
          borderRadius: variant === "illustration" ? "50%" : undefined,
        }}
      />
    </span>
  );
}

export function ZodiacIcon({
  sign,
  size = 28,
  className,
  stroke = "currentColor",
  variant = "seal",
}: ZodiacIconProps) {
  const slug = resolveZodiacSignId(sign ?? "", null);
  if (!slug || !isZodiacSlug(slug)) return null;

  if (VISUAL_ASSET_MODE === "asset") {
    return (
      <ZodiacAssetSymbol
        slug={slug}
        size={size}
        className={className}
        stroke={stroke}
        variant={variant}
      />
    );
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
