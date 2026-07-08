import type { ReactNode } from "react";

type PracticeCapsuleProps = {
  type: "tarot" | "check-in" | "numerology" | "ritual" | "mantra";
  title: string;
  description?: string;
  icon?: ReactNode;
  steps?: string[];
  cta?: {
    label: string;
    href?: string;
    onClick?: () => void;
  };
  metadata?: {
    date?: string;
    card?: string;
    number?: string;
    ritual?: string;
  };
  className?: string;
};

export function PracticeCapsule({
  type,
  title,
  description,
  icon,
  steps = [],
  cta,
  metadata,
  className
}: PracticeCapsuleProps) {
  const typeClass = `orbit-practice-capsule--${type}`;

  return (
    <div className={`orbit-practice-capsule ${typeClass} ${className || ""}`}>
      <header className="orbit-practice-capsule__header">
        {icon && <div className="orbit-practice-capsule__icon">{icon}</div>}
        <div className="orbit-practice-capsule__title-group">
          <h3 className="orbit-practice-capsule__title">{title}</h3>
          {metadata && (
            <div className="orbit-practice-capsule__metadata">
              {metadata.date && (
                <span className="orbit-practice-capsule__meta-item">
                  {metadata.date}
                </span>
              )}
              {metadata.card && (
                <span className="orbit-practice-capsule__meta-item">
                  {metadata.card}
                </span>
              )}
              {metadata.number && (
                <span className="orbit-practice-capsule__meta-item">
                  {metadata.number}
                </span>
              )}
              {metadata.ritual && (
                <span className="orbit-practice-capsule__meta-item">
                  {metadata.ritual}
                </span>
              )}
            </div>
          )}
        </div>
      </header>

      {description && (
        <p className="orbit-practice-capsule__description">{description}</p>
      )}

      {steps.length > 0 && (
        <ol className="orbit-practice-capsule__steps">
          {steps.map((step, idx) => (
            <li key={idx} className="orbit-practice-capsule__step">
              {step}
            </li>
          ))}
        </ol>
      )}

      {cta && (
        <footer className="orbit-practice-capsule__footer">
          {cta.href ? (
            <a href={cta.href} className="orbit-cta-capsule orbit-cta-capsule--primary">
              {cta.label}
            </a>
          ) : (
            <button
              type="button"
              onClick={cta.onClick}
              className="orbit-cta-capsule orbit-cta-capsule--primary"
            >
              {cta.label}
            </button>
          )}
        </footer>
      )}
    </div>
  );
}

