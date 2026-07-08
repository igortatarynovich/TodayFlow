import type { ReactNode } from "react";

type MeaningCardProps = {
  label: string;
  badge?: string;
  locked?: boolean;
  layer?: "observation" | "interpretation" | "context";
  heading?: string;
  body: ReactNode;
  navLabel?: string;
  prevLabel?: string;
  nextLabel?: string;
  disablePrev?: boolean;
  disableNext?: boolean;
  onPrev?: () => void;
  onNext?: () => void;
  footnote?: ReactNode;
  cta?: ReactNode;
  className?: string;
};

export function MeaningCard({
  label,
  badge,
  locked = false,
  layer,
  heading,
  body,
  navLabel,
  prevLabel = "← Previous",
  nextLabel = "Next →",
  disablePrev,
  disableNext,
  onPrev,
  onNext,
  footnote,
  cta,
  className
}: MeaningCardProps) {
  const layerClass = layer ? `orbit-meaning-card--${layer}` : "";
  
  return (
    <article 
      className={["orbit-meaning-card", layerClass, className].filter(Boolean).join(" ")} 
      data-locked={locked}
      data-layer={layer}
    >
      <header className="orbit-meaning-card__rail">
        <p className="orbit-rail__label">{label}</p>
        {badge && (
          <span className="orbit-rail__badge">
            {badge}
            {locked && (
              <span role="img" aria-label="Locked context" style={{ marginLeft: "0.25rem" }}>
                🔒
              </span>
            )}
          </span>
        )}
      </header>
      <section className="orbit-meaning-card__body">
        {heading && (
          <p className={`orbit-meaning-card__heading orbit-meaning-card__heading--${layer || "default"}`}>
            {heading}
          </p>
        )}
        <div className={`orbit-meaning-card__text orbit-meaning-card__text--${layer || "default"}`}>
          {body}
        </div>
      </section>
      {(onPrev || onNext || navLabel) && (
        <footer className="orbit-meaning-card__nav">
          {onPrev ? (
            <button 
              type="button" 
              onClick={onPrev} 
              disabled={disablePrev}
              className="orbit-cta-capsule"
            >
              {prevLabel}
            </button>
          ) : (
            <span />
          )}
          {navLabel && <p className="orbit-meaning-card__counter">{navLabel}</p>}
          {onNext ? (
            <button 
              type="button" 
              onClick={onNext} 
              disabled={disableNext}
              className="orbit-cta-capsule"
            >
              {nextLabel}
            </button>
          ) : (
            <span />
          )}
        </footer>
      )}
      {footnote && <div className="orbit-meaning-card__note">{footnote}</div>}
      {cta && <div className="orbit-meaning-card__cta">{cta}</div>}
    </article>
  );
}
