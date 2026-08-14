"use client";

import {
  isNumberDigit,
  numberDigitAssetPath,
  resolveNumberDigits,
} from "@/lib/visualIdentity/registry";

export type NumberIconProps = {
  value: string | number | null | undefined;
  /** Height of each digit glyph (px). Multi-digit values share this height. */
  size?: number;
  className?: string;
  /** Accessible label; decorative default. */
  alt?: string;
};

/**
 * Metallic numerology digits (1–9 WebP). Master numbers compose glyphs (11 → 1+1).
 * Unknown / 0 / non-digit → plain text fallback at the same slot size.
 */
export function NumberIcon({ value, size = 28, className, alt = "" }: NumberIconProps) {
  const digits = resolveNumberDigits(value);
  const label = String(value ?? "").trim();

  if (!digits) {
    if (!label || label === "—" || label === "-" || label === "…") return null;
    return (
      <span
        data-testid="number-symbol"
        data-visual="text"
        className={className}
        style={{
          display: "inline-flex",
          height: size,
          alignItems: "center",
          justifyContent: "center",
          fontFamily: "var(--tf-font-display, var(--orbit-font-display, Georgia, serif))",
          fontSize: Math.round(size * 0.72),
          fontWeight: 700,
          lineHeight: 1,
          flexShrink: 0,
        }}
        aria-hidden={alt ? undefined : true}
      >
        {label}
      </span>
    );
  }

  const digitSize = digits.length > 1 ? Math.round(size * 0.82) : size;
  const gap = Math.max(1, Math.round(size * 0.04));

  return (
    <span
      data-testid="number-symbol"
      data-visual="asset"
      data-value={digits.join("")}
      className={className}
      style={{
        display: "inline-flex",
        height: size,
        alignItems: "center",
        justifyContent: "center",
        gap,
        flexShrink: 0,
      }}
      aria-hidden={alt ? undefined : true}
      aria-label={alt || undefined}
    >
      {digits.map((digit, index) => (
        // eslint-disable-next-line @next/next/no-img-element -- static public WebP; size parity with icon slots
        <img
          key={`${digit}-${index}`}
          src={numberDigitAssetPath(digit)}
          alt=""
          width={digitSize}
          height={digitSize}
          draggable={false}
          style={{ width: digitSize, height: digitSize, objectFit: "contain", display: "block" }}
        />
      ))}
    </span>
  );
}

export function hasNumberDigitAsset(value: string | number | null | undefined): boolean {
  const digits = resolveNumberDigits(value);
  return Boolean(digits?.every((d) => isNumberDigit(d)));
}
