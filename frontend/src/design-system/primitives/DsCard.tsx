import type { ElementType, ReactNode } from "react";
import { joinClass } from "@/design-system/utils/joinClass";
import { type DsSurfaceTone } from "@/design-system/primitives/DsSurface";
import fk from "@/design-system/primitives/dsFormKit.module.css";

/**
 * Legacy card--* names from Figma map. Prefer `tone` (Form Kit §15.8).
 */
export type DsCardVariant =
  | "standard"
  | "glass"
  | "orbital"
  | "feature"
  | "dark"
  | "insight"
  | "elevated"
  | "outline"
  | "card";

export type DsCardSize = "default" | "compact";

const TONE_CLASS: Record<DsSurfaceTone, string> = {
  none: fk.toneNone,
  subtle: fk.toneSubtle,
  solid: fk.toneSolid,
  glass: fk.toneGlass,
  accent: fk.toneAccent,
};

export function cardVariantToTone(variant: DsCardVariant): DsSurfaceTone {
  switch (variant) {
    case "glass":
    case "insight":
    case "orbital":
      return "glass";
    case "feature":
      return "accent";
    case "outline":
      return "subtle";
    default:
      return "solid";
  }
}

type DsCardProps = {
  /** Form Kit surface tone. When set, wins over legacy `variant`. */
  tone?: DsSurfaceTone;
  /** @deprecated Prefer `tone`. */
  variant?: DsCardVariant;
  size?: DsCardSize;
  children: ReactNode;
  className?: string;
  as?: "div" | "section" | "article" | "button";
  testId?: string;
  onClick?: () => void;
};

/**
 * Compositional container whose skin comes from Form Kit Surface tones.
 * Pad / gap / `as` live here; visual shell = `tone` classes (same tokens as `DsSurface`).
 */
export function DsCard({
  tone,
  variant = "card",
  size = "default",
  children,
  className,
  as: Tag = "div",
  testId,
  onClick,
}: DsCardProps) {
  const resolvedTone = tone ?? cardVariantToTone(variant);
  const isButton = Tag === "button";
  const Comp = Tag as ElementType;
  return (
    <Comp
      className={joinClass(
        fk.surfaceBase,
        TONE_CLASS[resolvedTone],
        fk.cardShell,
        size === "compact" ? fk.cardPadCompact : fk.cardPadDefault,
        isButton ? fk.cardInteractive : undefined,
        className,
      )}
      data-surface-tone={resolvedTone}
      data-testid={testId}
      onClick={onClick}
      type={isButton ? "button" : undefined}
    >
      {children}
    </Comp>
  );
}

export function DsStatusBadge({ children, className }: { children: ReactNode; className?: string }) {
  return <span className={joinClass(fk.chip, fk.chipStatus, className)}>{children}</span>;
}
