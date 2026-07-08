import type { ReactNode } from "react";
import { joinClass } from "@/design-system/utils/joinClass";
import p from "@/design-system/primitives/dsPrimitives.module.css";

/** Figma card--* variants */
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

const CARD_CLASS: Record<DsCardVariant, string> = {
  standard: p.cardStandard,
  glass: p.cardGlass,
  orbital: p.cardOrbital,
  feature: p.cardFeature,
  dark: p.cardDark,
  insight: p.cardInsight,
  elevated: p.elevated,
  outline: p.outline,
  card: p.card,
};

type DsCardProps = {
  variant?: DsCardVariant;
  children: ReactNode;
  className?: string;
  as?: "div" | "section" | "article" | "button";
  testId?: string;
  onClick?: () => void;
};

export function DsCard({
  variant = "card",
  children,
  className,
  as: Tag = "div",
  testId,
  onClick,
}: DsCardProps) {
  const isButton = Tag === "button";
  return (
    <Tag
      className={joinClass(p.surface, CARD_CLASS[variant], className)}
      data-testid={testId}
      onClick={onClick}
      type={isButton ? "button" : undefined}
    >
      {variant === "feature" ? <span className={p.cardFeatureAccent} aria-hidden /> : null}
      {variant === "orbital" ? <DsCardOrbitalDecor /> : null}
      {children}
    </Tag>
  );
}

function DsCardOrbitalDecor() {
  return (
    <span aria-hidden style={{ position: "absolute", right: "-3.8rem", bottom: "-3.8rem", opacity: 0.4 }}>
      <span
        style={{
          display: "block",
          width: "15rem",
          height: "15rem",
          borderRadius: "50%",
          border: "1px solid rgba(201, 169, 110, 0.25)",
          boxShadow: "inset 0 0 0 36px rgba(201,169,110,0.08), inset 0 0 0 72px rgba(201,169,110,0.05)",
        }}
      />
    </span>
  );
}

export function DsStatusBadge({ children, className }: { children: ReactNode; className?: string }) {
  return <span className={joinClass(p.statusBadge, className)}>{children}</span>;
}
