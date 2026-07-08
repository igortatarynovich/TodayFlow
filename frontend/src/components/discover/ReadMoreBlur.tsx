"use client";

import Link from "next/link";

interface ReadMoreBlurProps {
  hasAccess: boolean;
  children: React.ReactNode;
  ctaText?: string;
  ctaHref?: string;
}

/**
 * Компонент для blur-эффекта и "читать дальше"
 * Используется вместо paywall-экранов
 */
export function ReadMoreBlur({ 
  hasAccess, 
  children, 
  ctaText = "Читать дальше",
  ctaHref = "/reports/full"
}: ReadMoreBlurProps) {
  if (hasAccess) {
    return <>{children}</>;
  }

  return (
    <div style={{ position: "relative" }}>
      <div
        style={{
          filter: "blur(4px)",
          pointerEvents: "none",
          userSelect: "none",
          maxHeight: "200px",
          overflow: "hidden"
        }}
      >
        {children}
      </div>
      <div
        style={{
          position: "absolute",
          bottom: 0,
          left: 0,
          right: 0,
          background: "linear-gradient(to top, rgba(250, 249, 247, 0.95), transparent)",
          padding: "var(--orbit-space-lg)",
          textAlign: "center"
        }}
      >
        <Link
          href={ctaHref}
          className="orbit-button orbit-button-secondary orbit-button-sm"
          style={{
            textDecoration: "none"
          }}
        >
          {ctaText} →
        </Link>
      </div>
    </div>
  );
}

