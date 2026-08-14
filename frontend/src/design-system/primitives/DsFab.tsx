import type { ReactNode } from "react";
import Link from "next/link";
import { joinClass } from "@/design-system/utils/joinClass";
import fk from "@/design-system/primitives/dsFormKit.module.css";

export type DsFabSize = "sm" | "md" | "lg";

type DsFabProps = {
  children: ReactNode;
  size?: DsFabSize;
  className?: string;
  href?: string;
  onClick?: () => void;
  ariaLabel: string;
  testId?: string;
  disabled?: boolean;
};

export function DsFab({
  children,
  size = "md",
  className,
  href,
  onClick,
  ariaLabel,
  testId,
  disabled,
}: DsFabProps) {
  const cls = joinClass(
    fk.fab,
    size === "sm" ? fk.fabSm : null,
    size === "lg" ? fk.fabLg : null,
    className,
  );
  if (href && !disabled) {
    return (
      <Link href={href} className={cls} aria-label={ariaLabel} data-testid={testId}>
        {children}
      </Link>
    );
  }
  return (
    <button
      type="button"
      className={cls}
      aria-label={ariaLabel}
      data-testid={testId}
      onClick={onClick}
      disabled={disabled}
    >
      {children}
    </button>
  );
}
