import type { ReactNode } from "react";

type ActionItem = {
  label: string;
  href?: string;
  onClick?: () => void;
  variant?: "primary" | "secondary" | "ghost";
  icon?: ReactNode;
  disabled?: boolean;
};

type ActionFooterProps = {
  actions: ActionItem[];
  className?: string;
};

export function ActionFooter({ actions, className }: ActionFooterProps) {
  return (
    <footer className={`orbit-action-footer ${className || ""}`}>
      <div className="orbit-action-footer__actions">
        {actions.map((action, idx) => {
          const variantClass = action.variant
            ? `orbit-cta-capsule--${action.variant}`
            : "orbit-cta-capsule--secondary";
          const baseClass = "orbit-cta-capsule";
          const fullClass = `${baseClass} ${variantClass}`;

          if (action.disabled) {
            return (
              <button
                key={idx}
                type="button"
                disabled
                className={`${fullClass} orbit-cta-capsule--disabled`}
              >
                {action.icon && <span className="orbit-cta-capsule__icon">{action.icon}</span>}
                {action.label}
              </button>
            );
          }

          if (action.href) {
            return (
              <a
                key={idx}
                href={action.href}
                className={fullClass}
              >
                {action.icon && <span className="orbit-cta-capsule__icon">{action.icon}</span>}
                {action.label}
              </a>
            );
          }

          return (
            <button
              key={idx}
              type="button"
              onClick={action.onClick}
              className={fullClass}
            >
              {action.icon && <span className="orbit-cta-capsule__icon">{action.icon}</span>}
              {action.label}
            </button>
          );
        })}
      </div>
    </footer>
  );
}

