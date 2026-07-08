import type { ReactNode } from "react";

type AnchorCard = {
  label: string; // "Sun", "Moon", "Rising"
  sign: string; // "Aries", "Taurus", etc.
  element?: string; // "fire", "earth", "air", "water"
  modality?: string; // "cardinal", "fixed", "mutable"
  themes?: string[]; // краткие темы
};

type AxisHighlight = {
  axisId: string; // "A1", "A2", etc.
  label: string; // "Identity Orientation"
  value: number; // -100 to +100
  range: "inner" | "outer" | "balanced"; // для визуализации диапазона
  description?: string; // краткое пояснение
};

type MethodContextCapsuleProps = {
  anchorCards?: AnchorCard[];
  axisHighlights?: AxisHighlight[];
  traceHint?: string | ReactNode;
  showUnlockHint?: boolean; // для Lite режима
  unlockHintAction?: ReactNode; // CTA для unlock hint
  className?: string;
};

export function MethodContextCapsule({
  anchorCards = [],
  axisHighlights = [],
  traceHint,
  showUnlockHint = false,
  unlockHintAction,
  className
}: MethodContextCapsuleProps) {
  return (
    <div className={`orbit-method-context ${className || ""}`}>
      {anchorCards.length > 0 && (
        <section className="orbit-method-context__anchors">
          <h3 className="orbit-method-context__heading">Anchor Cards</h3>
          <div className="orbit-method-context__anchor-grid">
            {anchorCards.map((card, idx) => (
              <div key={idx} className="orbit-anchor-card">
                <div className="orbit-anchor-card__header">
                  <span className="orbit-anchor-card__label">{card.label}</span>
                  <span className="orbit-anchor-card__sign">{card.sign}</span>
                </div>
                {(card.element || card.modality) && (
                  <div className="orbit-anchor-card__meta">
                    {card.element && (
                      <span className="orbit-anchor-card__badge orbit-anchor-card__badge--element">
                        {card.element}
                      </span>
                    )}
                    {card.modality && (
                      <span className="orbit-anchor-card__badge orbit-anchor-card__badge--modality">
                        {card.modality}
                      </span>
                    )}
                  </div>
                )}
                {card.themes && card.themes.length > 0 && (
                  <div className="orbit-anchor-card__themes">
                    {card.themes.map((theme, themeIdx) => (
                      <span key={themeIdx} className="orbit-anchor-card__theme">
                        {theme}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </section>
      )}

      {axisHighlights.length > 0 && (
        <section className="orbit-method-context__axes">
          <h3 className="orbit-method-context__heading">Axis Highlights</h3>
          <div className="orbit-method-context__axis-list">
            {axisHighlights.map((axis, idx) => (
              <div key={idx} className="orbit-axis-card">
                <div className="orbit-axis-card__header">
                  <span className="orbit-axis-card__id">{axis.axisId}</span>
                  <span className="orbit-axis-card__label">{axis.label}</span>
                </div>
                <div className="orbit-axis-card__range">
                  <div className="orbit-axis-card__range-track">
                    <div
                      className="orbit-axis-card__range-fill"
                      style={{
                        left: `${50 + (axis.value / 100) * 50}%`,
                        transform: "translateX(-50%)"
                      }}
                    />
                    <div
                      className="orbit-axis-card__range-marker"
                      style={{
                        left: `${50 + (axis.value / 100) * 50}%`,
                        transform: "translateX(-50%)"
                      }}
                    />
                  </div>
                  <div className="orbit-axis-card__range-labels">
                    <span className="orbit-axis-card__range-label orbit-axis-card__range-label--inner">
                      Inner
                    </span>
                    <span className="orbit-axis-card__range-label orbit-axis-card__range-label--outer">
                      Outer
                    </span>
                  </div>
                </div>
                {axis.description && (
                  <p className="orbit-axis-card__description">{axis.description}</p>
                )}
              </div>
            ))}
          </div>
        </section>
      )}

      {traceHint && (
        <section className="orbit-method-context__trace">
          <p className="orbit-method-context__trace-hint">{traceHint}</p>
        </section>
      )}

      {showUnlockHint && (
        <section className="orbit-method-context__unlock">
          <p className="orbit-method-context__unlock-hint">
            Context unlocks in Full Report
          </p>
          {unlockHintAction && (
            <div className="orbit-method-context__unlock-action">
              {unlockHintAction}
            </div>
          )}
        </section>
      )}
    </div>
  );
}

