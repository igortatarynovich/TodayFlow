import type { ReactNode } from "react";
import styles from "./surfaceInsight.module.css";

export type SurfaceInsightVariant = "neutral" | "warm" | "love" | "money";

export type SurfaceInsightProps = {
  children: ReactNode;
  eyebrow?: string;
  variant?: SurfaceInsightVariant;
  className?: string;
  "data-testid"?: string;
};

function variantClass(variant: SurfaceInsightVariant): string {
  switch (variant) {
    case "warm":
      return styles.warm;
    case "love":
      return styles.love;
    case "money":
      return styles.money;
    default:
      return "";
  }
}

export function SurfaceInsight({
  children,
  eyebrow,
  variant = "neutral",
  className,
  "data-testid": testId,
}: SurfaceInsightProps) {
  const rootClass = [styles.surface, variantClass(variant), className ?? ""].filter(Boolean).join(" ");

  return (
    <section className={rootClass} data-testid={testId}>
      {eyebrow ? <p className={styles.eyebrow}>{eyebrow}</p> : null}
      {children}
    </section>
  );
}

export function SurfaceInsightBody({ children, className }: { children: ReactNode; className?: string }) {
  return <p className={`${styles.body} ${className ?? ""}`.trim()}>{children}</p>;
}

export function SurfaceInsightActions({ children }: { children: ReactNode }) {
  return <div className={styles.actions}>{children}</div>;
}

export { styles as surfaceInsightStyles };
