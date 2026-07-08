"use client";

import { useState } from "react";
import { ReactNode } from "react";
import Image from "next/image";
import Link from "next/link";

interface FlippableServiceCardProps {
  title: string;
  backLabel: string;
  icon?: string;
  imageSrc?: string;
  frontContent: ReactNode;
  backContent?: ReactNode;
  linkHref?: string;
  linkText?: string;
  gradientColor?: string;
  size?: "sm" | "md" | "lg";
}

export function FlippableServiceCard({ 
  title, 
  backLabel, 
  icon,
  imageSrc,
  frontContent, 
  backContent,
  linkHref,
  linkText,
  gradientColor = "linear-gradient(135deg, rgba(180, 150, 200, 0.3), rgba(200, 170, 220, 0.2))",
  size = "md"
}: FlippableServiceCardProps) {
  const [isFlipped, setIsFlipped] = useState(false);
  const [isAnimating, setIsAnimating] = useState(false);

  const handleFlip = () => {
    if (isAnimating) return;
    setIsAnimating(true);
    setIsFlipped(!isFlipped);
    setTimeout(() => {
      setIsAnimating(false);
    }, 600);
  };

  const sizeClasses = {
    sm: { width: "200px", height: "280px" },
    md: { width: "234px", height: "310px" },
    lg: { width: "280px", height: "360px" },
  };

  const dimensions = sizeClasses[size];
  const cardWidth = dimensions.width;
  const cardHeight = dimensions.height;

  return (
    <div
      style={{
        perspective: "1000px",
        width: cardWidth,
        height: cardHeight,
        margin: "0 auto",
        cursor: "pointer",
      }}
      onClick={handleFlip}
    >
      <div
        style={{
          position: "relative",
          width: "100%",
          height: "100%",
          transformStyle: "preserve-3d",
          transition: "transform 0.6s ease",
          transform: isFlipped ? "rotateY(180deg)" : "rotateY(0deg)",
        }}
      >
        {/* Рубашка карты (лицевая сторона) */}
        <div
          style={{
            position: "absolute",
            width: "100%",
            height: "100%",
            backfaceVisibility: "hidden",
            WebkitBackfaceVisibility: "hidden",
            transform: "rotateY(0deg)",
          }}
        >
          <div
            style={{
              width: "100%",
              height: "100%",
              background: gradientColor,
              border: "3px solid rgba(150, 120, 180, 0.5)",
              borderRadius: "var(--orbit-radius-md)",
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              padding: "var(--orbit-space-lg)",
              boxShadow: "0 4px 16px rgba(0, 0, 0, 0.15)",
              position: "relative",
              overflow: "hidden",
              boxSizing: "border-box",
            }}
          >
            {/* Декоративный узор на рубашке */}
            <div
              style={{
                position: "absolute",
                top: "50%",
                left: "50%",
                transform: "translate(-50%, -50%)",
                width: "80%",
                height: "80%",
                background: `
                  radial-gradient(circle at 30% 30%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
                  radial-gradient(circle at 70% 70%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
                  repeating-linear-gradient(
                    45deg,
                    transparent,
                    transparent 10px,
                    rgba(255, 255, 255, 0.03) 10px,
                    rgba(255, 255, 255, 0.03) 20px
                  )
                `,
                borderRadius: "var(--orbit-radius-md)",
              }}
            />
            
            {/* Изображение или иконка */}
            {imageSrc ? (
              <div style={{ position: "relative", width: "64px", height: "64px", marginBottom: "var(--orbit-space-md)", zIndex: 1 }}>
                <Image 
                  src={imageSrc} 
                  alt={backLabel}
                  fill
                  style={{ objectFit: "contain", opacity: 0.9 }}
                />
              </div>
            ) : icon ? (
              <div
                style={{
                  fontSize: "3rem",
                  opacity: 0.6,
                  zIndex: 1,
                  marginBottom: "var(--orbit-space-md)",
                  filter: "drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2))",
                }}
              >
                {icon}
              </div>
            ) : null}
            
            {/* Название на рубашке */}
            <div
              style={{
                fontSize: "0.875rem",
                fontWeight: 600,
                color: "rgba(100, 80, 120, 0.9)",
                textAlign: "center",
                zIndex: 1,
                lineHeight: 1.4,
              }}
            >
              {backLabel}
            </div>
            
            {/* Текст "Нажми, чтобы открыть" */}
            <div
              style={{
                position: "absolute",
                bottom: "12px",
                fontSize: "0.7rem",
                color: "rgba(100, 80, 120, 0.7)",
                fontWeight: 500,
                textAlign: "center",
                zIndex: 1,
              }}
            >
              Нажми, чтобы открыть
            </div>

            {/* Grain overlay */}
            <div
              style={{
                position: "absolute",
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                background: "url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZGVmcz48ZmlsdGVyIGlkPSJncmFpbiI+PGZlVHVyYnVsZW5jZSB0eXBlPSJmcmFjdGFsTm9pc2UiIGJhc2VGcmVxdWVuY3k9IjAuOSIgbnVtT2N0YXZlcz0iNCIvPjwvZmlsdGVyPjwvZGVmcz48cmVjdCB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgZmlsdGVyPSJ1cmwoI2dyYWluKSIgb3BhY2l0eT0iMC4wNSIvPjwvc3ZnPg==')",
                opacity: 0.4,
                pointerEvents: "none",
                borderRadius: "var(--orbit-radius-md)",
              }}
            />
          </div>
        </div>

        {/* Лицевая сторона с контентом */}
        <div
          style={{
            position: "absolute",
            width: "100%",
            height: "100%",
            backfaceVisibility: "hidden",
            WebkitBackfaceVisibility: "hidden",
            transform: "rotateY(180deg)",
          }}
        >
          <div
            style={{
              width: "100%",
              height: "100%",
              background: "rgba(255, 255, 255, 0.98)",
              border: "2px solid var(--orbit-color-border)",
              borderRadius: "var(--orbit-radius-md)",
              padding: "var(--orbit-space-md)",
              display: "flex",
              flexDirection: "column",
              boxShadow: "0 4px 16px rgba(0, 0, 0, 0.15)",
              overflow: "hidden",
            }}
          >
            {/* Заголовок */}
            {title && (
              <h3
                style={{
                  fontSize: "0.875rem",
                  fontWeight: 600,
                  marginBottom: "var(--orbit-space-sm)",
                  textAlign: "center",
                  color: "var(--orbit-color-slate)",
                  lineHeight: 1.3,
                }}
              >
                {title}
              </h3>
            )}

            {/* Контент */}
            <div
              style={{
                flex: 1,
                overflowY: "auto",
                display: "flex",
                flexDirection: "column",
                gap: "var(--orbit-space-xs)",
                minHeight: 0,
              }}
            >
              {frontContent}
            </div>
            
            {/* Кнопка внизу (если есть backContent или link) */}
            {(backContent || linkHref) && (
              <div style={{ marginTop: "auto", paddingTop: "var(--orbit-space-xs)" }}>
                {backContent || (linkHref && linkText && (
                  <Link 
                    href={linkHref} 
                    className="orbit-button orbit-button-primary orbit-button-xs"
                    style={{ width: "100%", justifyContent: "center" }}
                    onClick={(e) => e.stopPropagation()}
                  >
                    {linkText} →
                  </Link>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

