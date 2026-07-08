"use client";

import Link from "next/link";

interface SubscriptionTierProps {
  name: string;
  features: string[];
  price?: string;
  recommended?: boolean;
  highlight?: boolean;
  ctaText?: string;
  ctaHref?: string;
}

export function SubscriptionTier({ 
  name, 
  features, 
  price, 
  recommended = false,
  highlight = false,
  ctaText,
  ctaHref 
}: SubscriptionTierProps) {
  return (
    <div 
      className="orbit-card" 
      style={{ 
        padding: "var(--orbit-space-xl)",
        position: "relative",
        border: highlight 
          ? "2px solid rgba(212, 175, 55, 0.5)" 
          : recommended 
          ? "2px solid rgba(212, 175, 55, 0.3)" 
          : "1px solid var(--orbit-color-border)",
        background: highlight
          ? "linear-gradient(135deg, rgba(212, 175, 55, 0.15), rgba(212, 175, 55, 0.08))"
          : recommended
          ? "linear-gradient(135deg, rgba(212, 175, 55, 0.08), rgba(212, 175, 55, 0.03))"
          : "var(--orbit-color-white)",
        transition: "transform 0.2s ease, box-shadow 0.2s ease",
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.transform = "translateY(-4px)";
        e.currentTarget.style.boxShadow = highlight 
          ? "0 8px 24px rgba(212, 175, 55, 0.2)" 
          : "0 4px 16px rgba(0, 0, 0, 0.1)";
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.transform = "translateY(0)";
        e.currentTarget.style.boxShadow = "none";
      }}
    >
      {recommended && (
        <div style={{
          position: "absolute",
          top: "-12px",
          left: "50%",
          transform: "translateX(-50%)",
          background: "var(--orbit-color-primary)",
          color: "var(--orbit-color-white)",
          padding: "4px 12px",
          borderRadius: "12px",
          fontSize: "0.75rem",
          fontWeight: 600,
          whiteSpace: "nowrap",
        }}>
          Рекомендуется
        </div>
      )}

      <h3 className="orbit-body" style={{ fontWeight: 600, marginBottom: "var(--orbit-space-xs)", textAlign: "center" }}>
        {name}
      </h3>

      {price && (
        <div style={{ textAlign: "center", marginBottom: "var(--orbit-space-md)" }}>
          <p className="orbit-display-sm" style={{ fontWeight: 700, color: highlight ? "var(--orbit-color-primary)" : "var(--orbit-color-ink)" }}>
            {price}
          </p>
        </div>
      )}

      <ul style={{ listStyle: "none", padding: 0, margin: "var(--orbit-space-md) 0", textAlign: "left" }}>
        {features.map((feature, idx) => (
          <li 
            key={idx}
            style={{ 
              marginBottom: "var(--orbit-space-xs)", 
              fontSize: "0.875rem", 
              color: "var(--orbit-color-slate)",
              position: "relative",
              paddingLeft: "1.5rem",
            }}
          >
            <span style={{ 
              position: "absolute", 
              left: 0,
              color: highlight ? "var(--orbit-color-primary)" : "var(--orbit-color-slate)",
            }}>
              {highlight || recommended ? "✓" : "•"}
            </span>
            {feature}
          </li>
        ))}
      </ul>

      {ctaText && ctaHref && (
        <div style={{ marginTop: "var(--orbit-space-lg)", textAlign: "center" }}>
          <Link 
            href={ctaHref}
            className={highlight ? "orbit-button orbit-button-primary orbit-button-medium" : "orbit-button orbit-button-secondary orbit-button-medium"}
            style={{ width: "100%" }}
          >
            {ctaText}
          </Link>
        </div>
      )}

      {!price && !ctaText && (
        <p className="orbit-body-sm orbit-text-muted" style={{ fontWeight: 600, marginTop: "var(--orbit-space-md)", textAlign: "center" }}>
          Бесплатно
        </p>
      )}
    </div>
  );
}

