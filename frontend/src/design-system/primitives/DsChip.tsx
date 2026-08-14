import type { ButtonHTMLAttributes, ReactNode } from "react";
import { joinClass } from "@/design-system/utils/joinClass";
import fk from "@/design-system/primitives/dsFormKit.module.css";

export type DsChipVariant = "default" | "status" | "time" | "selection" | "ghost";

/** Stable semantic tones only — `--tf-semantic-*`, never `--day-*`. */
export type DsChipStatusTone = "neutral" | "good" | "warn" | "risk";

type DsChipProps = {
  children: ReactNode;
  icon?: ReactNode;
  variant?: DsChipVariant;
  /** Selected / pressed look (time & selection use day mood; status uses semantic wash). */
  selected?: boolean;
  /** Only for `variant="status"` — maps to stable `--tf-semantic-*` tokens. */
  statusTone?: DsChipStatusTone;
  className?: string;
  testId?: string;
  onClick?: ButtonHTMLAttributes<HTMLButtonElement>["onClick"];
  disabled?: boolean;
  type?: "button" | "submit";
};

function statusToneClass(tone: DsChipStatusTone | undefined): string | null {
  if (!tone) return null;
  if (tone === "good") return fk.chipStatusGood;
  if (tone === "warn") return fk.chipStatusWarn;
  if (tone === "risk") return fk.chipStatusRisk;
  return fk.chipStatusNeutral;
}

export function DsChip({
  children,
  icon,
  variant = "default",
  selected = false,
  statusTone,
  className,
  testId,
  onClick,
  disabled,
  type = "button",
}: DsChipProps) {
  const isStatus = variant === "status";
  const cls = joinClass(
    fk.chip,
    isStatus ? fk.chipStatus : null,
    isStatus && statusTone ? fk.chipStatusTone : null,
    isStatus ? statusToneClass(statusTone ?? "neutral") : null,
    variant === "time" ? fk.chipTime : null,
    variant === "selection" ? fk.chipSelection : null,
    variant === "ghost" ? fk.chipGhost : null,
    onClick ? fk.chipButton : null,
    className,
  );
  const content = (
    <>
      {isStatus ? <span className={fk.chipStatusDot} aria-hidden /> : null}
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
        data-status-tone={isStatus ? statusTone ?? "neutral" : undefined}
        onClick={onClick}
        disabled={disabled}
      >
        {content}
      </button>
    );
  }
  return (
    <span
      className={cls}
      data-testid={testId}
      data-selected={selected ? "true" : undefined}
      data-status-tone={isStatus ? statusTone ?? "neutral" : undefined}
    >
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
