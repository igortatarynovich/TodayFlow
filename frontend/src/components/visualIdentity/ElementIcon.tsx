"use client";

import type { Element } from "@/lib/zodiac-utils";
import {
  VISUAL_ASSET_MODE,
  elementAssetPath,
  resolveElementSlug,
  type ElementSlug,
} from "@/lib/visualIdentity/registry";
import { InlineElementIcon } from "./icons/InlineElementIcons";
import type { SymbolicIconProps } from "./icons/iconProps";

export type ElementIconProps = SymbolicIconProps & {
  element: Element | string | null | undefined;
};

function ElementAssetSymbol({
  slug,
  size,
  className,
  stroke,
}: {
  slug: ElementSlug;
  size: number;
  className?: string;
  stroke: string;
}) {
  const tint = stroke === "currentColor" ? "currentColor" : stroke;
  return (
    <span
      data-testid="element-symbol"
      aria-hidden
      className={className}
      style={{
        width: size,
        height: size,
        display: "inline-block",
        flexShrink: 0,
        backgroundColor: tint,
        color: tint,
        maskImage: `url(${elementAssetPath(slug)})`,
        WebkitMaskImage: `url(${elementAssetPath(slug)})`,
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

export function ElementIcon({ element, size = 24, className, stroke = "currentColor" }: ElementIconProps) {
  const slug = resolveElementSlug(element);
  if (!slug) return null;

  if (VISUAL_ASSET_MODE === "asset") {
    return <ElementAssetSymbol slug={slug} size={size} className={className} stroke={stroke} />;
  }

  return (
    <span
      data-testid="element-symbol"
      className={className}
      style={{ display: "inline-flex", width: size, height: size, flexShrink: 0 }}
    >
      <InlineElementIcon slug={slug} size={size} stroke={stroke} />
    </span>
  );
}
