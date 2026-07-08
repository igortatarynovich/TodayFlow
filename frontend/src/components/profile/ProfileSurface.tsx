import type { ReactNode } from "react";
import { SurfaceInsight, type SurfaceInsightVariant } from "@/components/foundation/SurfaceInsight";
import styles from "./profileSurface.module.css";

export type ProfileSurfaceTone =
  | "default"
  | "soft"
  | "solid"
  | "sm"
  | "nested"
  | "numerology"
  | "outline";

const toneClass: Record<ProfileSurfaceTone, string> = {
  default: styles.tile,
  soft: `${styles.tile} ${styles.tileSoft}`,
  solid: `${styles.tile} ${styles.tileSolid}`,
  sm: `${styles.tile} ${styles.tileSm} ${styles.tileSolid}`,
  nested: styles.nested,
  numerology: styles.numerologyTile,
  outline: styles.outlineTile,
};

const panelClassMap = {
  living: styles.panelLiving,
  portrait: styles.panelPortrait,
  plain: styles.panelPlain,
  numerology: styles.panelNumerology,
} as const;

export type ProfileSurfacePanelKind = keyof typeof panelClassMap;

export function ProfileSurfaceTile({
  children,
  className,
  tone = "default",
  id,
}: {
  children: ReactNode;
  className?: string;
  tone?: ProfileSurfaceTone;
  id?: string;
}) {
  return (
    <div id={id} className={[toneClass[tone], className].filter(Boolean).join(" ")}>
      {children}
    </div>
  );
}

export function ProfileSurfacePanel({
  children,
  eyebrow,
  variant = "neutral",
  className,
  panelClass,
}: {
  children: ReactNode;
  eyebrow?: string;
  variant?: SurfaceInsightVariant;
  className?: string;
  panelClass?: ProfileSurfacePanelKind;
}) {
  const extra = panelClass ? panelClassMap[panelClass] : "";
  return (
    <SurfaceInsight eyebrow={eyebrow} variant={variant} className={[extra, className].filter(Boolean).join(" ") || undefined}>
      {children}
    </SurfaceInsight>
  );
}

export { styles as profileSurfaceStyles };
