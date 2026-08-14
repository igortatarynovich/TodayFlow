import type { ReactNode } from "react";
import { joinClass } from "@/design-system/utils/joinClass";
import fk from "@/design-system/primitives/dsFormKit.module.css";

/** Form Kit surface tones — visual shell only (FOUNDATION_UI §15.8). */
export type DsSurfaceTone = "none" | "subtle" | "solid" | "glass" | "accent" | "overlay";

/** @deprecated Use `tone`. Maps legacy Surface variants → Form Kit tones. */
export type DsSurfaceLegacyVariant = "elevated" | "outline" | "glass" | "card";

const TONE_CLASS: Record<DsSurfaceTone, string> = {
  none: fk.toneNone,
  subtle: fk.toneSubtle,
  solid: fk.toneSolid,
  glass: fk.toneGlass,
  accent: fk.toneAccent,
  overlay: fk.toneOverlay,
};

export function legacySurfaceVariantToTone(variant: DsSurfaceLegacyVariant): DsSurfaceTone {
  if (variant === "glass") return "glass";
  if (variant === "outline") return "subtle";
  return "solid";
}

type DsSurfaceProps = {
  children?: ReactNode;
  tone?: DsSurfaceTone;
  /** @deprecated Prefer `tone`. */
  variant?: DsSurfaceLegacyVariant;
  className?: string;
  as?: "div" | "section" | "article" | "span";
  testId?: string;
};

export function DsSurface({
  children,
  tone,
  variant = "card",
  className,
  as: Tag = "div",
  testId,
}: DsSurfaceProps) {
  const resolved = tone ?? legacySurfaceVariantToTone(variant);
  return (
    <Tag
      className={joinClass(fk.surfaceBase, TONE_CLASS[resolved], className)}
      data-surface-tone={resolved}
      data-testid={testId}
    >
      {children}
    </Tag>
  );
}
