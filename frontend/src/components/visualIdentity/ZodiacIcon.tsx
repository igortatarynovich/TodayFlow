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
}: {
  slug: ZodiacSlug;
  size: number;
  className?: string;
  stroke: string;
}) {
  return (
    <span
      data-testid="zodiac-symbol"
      aria-hidden
      className={className}
      style={{
        width: size,
        height: size,
        display: "inline-flex",
        flexShrink: 0,
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      {/* eslint-disable-next-line @next/next/no-img-element -- static public WebP seal; size parity with prior mask slot */}
      <img
        src={zodiacAssetPath(slug)}
        alt=""
        width={size}
        height={size}
        draggable={false}
        style={{ width: size, height: size, objectFit: "contain", display: "block" }}
      />
    </span>
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
