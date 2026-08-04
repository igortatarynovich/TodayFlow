import Link from "next/link";
import type { ComponentPropsWithoutRef, ReactNode } from "react";
import { joinClass } from "@/design-system/utils/joinClass";
import p from "@/design-system/primitives/dsPrimitives.module.css";

type DsButtonProps = {
  variant?: "primary" | "secondary" | "ghost" | "destructive" | "icon";
  size?: "md" | "sm" | "block";
  href?: string;
  className?: string;
  children: ReactNode;
  disabled?: boolean;
} & Omit<ComponentPropsWithoutRef<"button">, "className" | "disabled">;

function buttonClass(variant: DsButtonProps["variant"], size: DsButtonProps["size"], disabled?: boolean) {
  return joinClass(
    p.btn,
    size === "sm" ? p.btnSm : size === "block" ? p.btnBlock : p.btnMd,
    variant === "primary"
      ? p.btnPrimary
      : variant === "secondary"
        ? p.btnSecondary
        : variant === "destructive"
          ? p.btnDestructive
          : variant === "icon"
            ? p.btnIcon
            : p.btnGhost,
    disabled ? p.btnDisabled : null,
  );
}

/** Button-only props that must not land on Next `<Link>`. */
const BUTTON_ONLY_KEYS = new Set([
  "type",
  "form",
  "formAction",
  "formEncType",
  "formMethod",
  "formNoValidate",
  "formTarget",
  "name",
  "value",
  "autoFocus",
]);

export function DsButton({
  variant = "primary",
  size = "md",
  href,
  className,
  children,
  disabled,
  ...rest
}: DsButtonProps) {
  const cls = joinClass(buttonClass(variant, size, disabled), className);

  if (href && !disabled) {
    const linkProps: Record<string, unknown> = {};
    for (const [key, value] of Object.entries(rest)) {
      if (BUTTON_ONLY_KEYS.has(key)) continue;
      linkProps[key] = value;
    }
    return (
      <Link href={href} className={cls} {...linkProps}>
        {children}
      </Link>
    );
  }

  return (
    <button type="button" className={cls} disabled={disabled} {...rest}>
      {children}
    </button>
  );
}
