import React from "react";
import Link from "next/link";

interface EmptyStateProps {
  title: string;
  description?: string;
  icon?: React.ReactNode;
  action?: {
    label: string;
    href: string;
    variant?: "primary" | "secondary";
  };
  className?: string;
}

export function EmptyState({
  title,
  description,
  icon,
  action,
  className = "",
}: EmptyStateProps) {
  return (
    <div className={`orbit-empty-state ${className}`}>
      {icon && <div className="orbit-empty-state__icon">{icon}</div>}
      <h3 className="orbit-empty-state__title">{title}</h3>
      {description && (
        <p className="orbit-empty-state__description">{description}</p>
      )}
      {action && (
        <Link
          href={action.href}
          className={`orbit-button orbit-button-${
            action.variant || "primary"
          }`}
        >
          {action.label}
        </Link>
      )}
    </div>
  );
}

