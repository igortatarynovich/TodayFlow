"use client";

import Link from "next/link";

interface OneTimePurchaseProps {
  title: string;
  description: string;
  icon: string;
  price?: string;
  href?: string;
}

export function OneTimePurchase({ title, description, icon, price, href }: OneTimePurchaseProps) {
  return (
    <div 
      className="orbit-card"
      style={{
        padding: "var(--orbit-space-lg)",
        textAlign: "center",
        transition: "transform 0.2s ease, box-shadow 0.2s ease",
        height: "100%",
        display: "flex",
        flexDirection: "column",
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.transform = "translateY(-2px)";
        e.currentTarget.style.boxShadow = "0 4px 12px rgba(0, 0, 0, 0.1)";
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.transform = "translateY(0)";
        e.currentTarget.style.boxShadow = "none";
      }}
    >
      <div style={{ fontSize: "2.5rem", marginBottom: "var(--orbit-space-md)" }}>
        {icon}
      </div>
      <h3 className="orbit-body" style={{ fontWeight: 600, marginBottom: "var(--orbit-space-xs)" }}>
        {title}
      </h3>
      <p className="orbit-body-sm orbit-text-muted" style={{ marginBottom: "var(--orbit-space-md)", lineHeight: 1.5, flex: 1 }}>
        {description}
      </p>
      {price && (
        <p className="orbit-body-sm" style={{ fontWeight: 600, color: "var(--orbit-color-primary)", marginBottom: "var(--orbit-space-sm)" }}>
          {price}
        </p>
      )}
      {href && (
        <Link href={href} className="orbit-button orbit-button-secondary orbit-button-xs" style={{ width: "100%" }}>
          Узнать больше →
        </Link>
      )}
    </div>
  );
}

