import type { ReactNode } from "react";
import { joinClass } from "@/design-system/utils/joinClass";
import fk from "@/design-system/primitives/dsFormKit.module.css";

export type DsChipVariant = "default" | "status" | "ghost";

type DsChipProps = {
  children: ReactNode;
  icon?: ReactNode;
  variant?: DsChipVariant;
  className?: string;
  testId?: string;
};

export function DsChip({
  children,
  icon,
  variant = "default",
  className,
  testId,
}: DsChipProps) {
  return (
    <span
      className={joinClass(
        fk.chip,
        variant === "status" ? fk.chipStatus : null,
        variant === "ghost" ? fk.chipGhost : null,
        className,
      )}
      data-testid={testId}
    >
      {icon ? <span className={fk.chipIcon}>{icon}</span> : null}
      {children}
    </span>
  );
}

type DsChipGroupProps = {
  children: ReactNode;
  className?: string;
  testId?: string;
};

export function DsChipCluster({ children, className, testId }: DsChipGroupProps) {
  return (
    <div className={joinClass(fk.chipGroup, className)} data-testid={testId}>
      {children}
    </div>
  );
}
