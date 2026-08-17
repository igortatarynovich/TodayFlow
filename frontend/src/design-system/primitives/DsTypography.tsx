import type { CSSProperties, ReactNode } from "react";
import { joinClass } from "@/design-system/utils/joinClass";
import p from "@/design-system/primitives/dsPrimitives.module.css";

export type DsInkTone = "primary" | "secondary" | "quiet" | "accent" | "action";

type TextProps = {
  children: ReactNode;
  className?: string;
  as?: "p" | "h1" | "h2" | "h3" | "span";
  muted?: boolean;
  onDark?: boolean;
  id?: string;
  style?: CSSProperties;
  /** Ink quintet (§5.1). `muted` maps to secondary when tone omitted. */
  tone?: DsInkTone;
};

function inkToneClass(tone?: DsInkTone, muted?: boolean): string | null {
  if (tone === "secondary" || (!tone && muted)) return p.muted;
  if (tone === "quiet") return p.inkQuiet;
  if (tone === "accent") return p.inkAccent;
  if (tone === "action") return p.inkAction;
  return null;
}

export function DsDisplayTitle({
  children,
  className,
  as: Tag = "h1",
  size = "xl",
  id,
}: TextProps & { size?: "xl" | "lg" | "md" | "sm" }) {
  const sizeClass =
    size === "lg" ? p.displayLg : size === "md" ? p.displayMd : size === "sm" ? p.displaySm : p.displayXl;
  return (
    <Tag id={id} className={joinClass(sizeClass, className)}>
      {children}
    </Tag>
  );
}

export function DsSectionTitle({ children, className, as: Tag = "h2", id }: TextProps) {
  return (
    <Tag id={id} className={joinClass(p.sectionTitle, className)}>
      {children}
    </Tag>
  );
}

export function DsEyebrow({ children, className, onDark }: TextProps & { onDark?: boolean }) {
  return <p className={joinClass(p.eyebrow, onDark ? p.eyebrowOnDark : null, className)}>{children}</p>;
}

export function DsBody({
  children,
  className,
  size = "md",
  muted,
  onDark,
  tone,
  style,
}: TextProps & { size?: "lg" | "md" | "sm" }) {
  const sizeClass = size === "lg" ? p.bodyLg : size === "sm" ? p.bodySm : p.bodyMd;
  return (
    <p
      style={style}
      className={joinClass(
        sizeClass,
        inkToneClass(tone, muted),
        onDark ? p.mutedOnDark : null,
        className,
      )}
    >
      {children}
    </p>
  );
}

export function DsLabel({ children, className, tone }: TextProps) {
  return <p className={joinClass(p.label, inkToneClass(tone), className)}>{children}</p>;
}

export function DsHeadline({ children, className, as: Tag = "h1", id }: TextProps) {
  return (
    <Tag id={id} className={joinClass(p.headline, className)}>
      {children}
    </Tag>
  );
}

export function DsTitle({ children, className, as: Tag = "h2", id }: TextProps) {
  return (
    <Tag id={id} className={joinClass(p.title, className)}>
      {children}
    </Tag>
  );
}

export function DsSubtitle({ children, className, as: Tag = "h3", id }: TextProps) {
  return (
    <Tag id={id} className={joinClass(p.subtitle, className)}>
      {children}
    </Tag>
  );
}

export function DsCaption({ children, className, muted, tone }: TextProps) {
  return (
    <p className={joinClass(p.caption, inkToneClass(tone, muted), className)}>{children}</p>
  );
}

export function DsPill({ children, className }: { children: ReactNode; className?: string }) {
  return <span className={joinClass(p.pill, className)}>{children}</span>;
}

export function DsTag({
  children,
  className,
  onDark,
  outline,
}: {
  children: ReactNode;
  className?: string;
  onDark?: boolean;
  outline?: boolean;
}) {
  return (
    <span className={joinClass(p.tag, onDark ? p.tagOnDark : null, outline ? p.tagOutline : null, className)}>
      {children}
    </span>
  );
}

export { DsSurface } from "@/design-system/primitives/DsSurface";
export type { DsSurfaceTone, DsSurfaceLegacyVariant } from "@/design-system/primitives/DsSurface";

export function DsIconBadge({
  children,
  size = "md",
  className,
}: {
  children: ReactNode;
  size?: "md" | "lg";
  className?: string;
}) {
  return (
    <span className={joinClass(p.iconBadge, size === "lg" ? p.iconBadgeLg : p.iconBadgeMd, className)}>
      {children}
    </span>
  );
}
