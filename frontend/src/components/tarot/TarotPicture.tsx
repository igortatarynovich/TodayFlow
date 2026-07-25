"use client";

import type { CSSProperties } from "react";
import type { TarotPictureSources } from "@/lib/tarotCardAssets";

type Props = {
  sources: TarotPictureSources;
  alt?: string;
  className?: string;
  sizes: string;
  style?: CSSProperties;
  draggable?: boolean;
  priority?: boolean;
};

/**
 * Density-aware tarot face/back: AVIF → WebP → img fallback.
 * Never renders emoji placeholders.
 */
export function TarotPicture({
  sources,
  alt = "",
  className,
  sizes,
  style,
  draggable = false,
  priority = false,
}: Props) {
  return (
    <picture className={className} style={style}>
      {sources.avifSrcSet ? (
        <source type="image/avif" srcSet={sources.avifSrcSet} sizes={sizes} />
      ) : null}
      {sources.webpSrcSet ? (
        <source type="image/webp" srcSet={sources.webpSrcSet} sizes={sizes} />
      ) : null}
      {/* eslint-disable-next-line @next/next/no-img-element -- picture/srcSet; next/image lacks multi-format static srcSet */}
      <img
        src={sources.src}
        alt={alt}
        width={sources.width}
        height={sources.height}
        sizes={sizes}
        draggable={draggable}
        decoding="async"
        loading={priority ? "eager" : "lazy"}
        style={{ width: "100%", height: "100%", objectFit: "contain", display: "block" }}
      />
    </picture>
  );
}
