import type { ButtonHTMLAttributes, ReactNode } from "react";
import { joinClass } from "@/design-system/utils/joinClass";
import fk from "@/design-system/primitives/dsFormKit.module.css";

export type DsChipVariant = "default" | "status" | "ghost";

type DsChipProps = {
  children: ReactNode;
  icon?: ReactNode;
  variant?: DsChipVariant;
  /** Selected / pressed look (status wash). */
  selected?: boolean;
  className?: string;
  testId?: string;
  onClick?: ButtonHTMLAttributes<HTMLButtonElement>["onClick"];
  disabled?: boolean;
  type?: "button" | "submit";
};

export function DsChip({
  children,
  icon,
  variant = "default",
  selected = false,
  className,
  testId,
  onClick,
  disabled,
  type = "button",
}: DsChipProps) {
  const cls = joinClass(
    fk.chip,
    variant === "status" || selected ? fk.chipStatus : null,
    variant === "ghost" ? fk.chipGhost : null,
    onClick ? fk.chipButton : null,
    className,
  );
  const content = (
    <>
      {icon ? <span className={fk.chipIcon}>{icon}</span> : null}
      {children}
    </>
  );
  if (onClick) {
    return (
      <button
        type={type}
        className={cls}
        data-testid={testId}
        data-selected={selected ? "true" : undefined}
        onClick={onClick}
        disabled={disabled}
      >
        {content}
      </button>
    );
  }
  return (
    <span className={cls} data-testid={testId} data-selected={selected ? "true" : undefined}>
      {content}
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
