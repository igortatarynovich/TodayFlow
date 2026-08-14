import type { ReactNode } from "react";
import { joinClass } from "@/design-system/utils/joinClass";
import fk from "@/design-system/primitives/dsFormKit.module.css";

export type DsAvatarSize = "sm" | "md" | "lg";

type DsAvatarProps = {
  label?: string;
  children?: ReactNode;
  size?: DsAvatarSize;
  className?: string;
  testId?: string;
};

export function DsAvatar({ label, children, size = "md", className, testId }: DsAvatarProps) {
  const initial = (label || "").trim().slice(0, 1).toUpperCase() || "·";
  return (
    <span
      className={joinClass(
        fk.avatar,
        size === "sm" ? fk.avatarSm : null,
        size === "lg" ? fk.avatarLg : null,
        className,
      )}
      data-testid={testId}
      aria-hidden={label ? undefined : true}
      title={label}
    >
      {children ?? initial}
    </span>
  );
}
