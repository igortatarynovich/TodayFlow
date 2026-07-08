"use client";

import Image from "next/image";

interface TarotHeroProps {
  streakDays: number;
  showContent: boolean;
}

export function TarotHero({ streakDays, showContent }: TarotHeroProps) {
  return (
    <section className="orbit-hero-design orbit-hero-design-unified">
      <div className="orbit-hero-design-wrapper">
        <Image
          src="/images/hero-meditation.png"
          alt="Tarot Flow"
          fill
          priority
          className="orbit-hero-design-bg"
          style={{ objectFit: "cover", objectPosition: "center" }}
        />
        <div className="orbit-hero-design-overlay" />
        
        <div className="orbit-hero-design-silk">
          <div className="orbit-hero-design-silk-1" />
          <div className="orbit-hero-design-silk-2" />
          <div className="orbit-hero-design-silk-3" />
        </div>

        <div className="orbit-hero-design-lines">
          <svg className="orbit-hero-design-lines-svg" viewBox="0 0 1920 1080" preserveAspectRatio="none">
            <path d="M300,200 Q600,150 900,200 T1500,200" stroke="rgba(255,255,255,0.25)" strokeWidth="1.5" fill="none" />
            <path d="M400,400 Q700,350 1000,400 T1600,400" stroke="rgba(255,255,255,0.2)" strokeWidth="1" fill="none" />
          </svg>
        </div>

        <div className="orbit-hero-design-container">
          <h1 
            className="orbit-hero-design-title-text"
            style={{
              opacity: showContent ? 1 : 0,
              transform: showContent ? "translateY(0)" : "translateY(20px)",
              transition: "opacity 0.8s ease, transform 0.8s ease"
            }}
          >
            Tarot Flow
          </h1>
          <p 
            className="orbit-hero-design-subtitle" 
            style={{ 
              textAlign: "center", 
              marginTop: "var(--orbit-space-sm)",
              opacity: showContent ? 1 : 0,
              transform: showContent ? "translateY(0)" : "translateY(20px)",
              transition: "opacity 0.8s ease 0.2s, transform 0.8s ease 0.2s"
            }}
          >
            Ежедневные карты таро и ритуалы для осознанного дня
          </p>
          {streakDays > 0 && (
            <p 
              className="orbit-body-sm" 
              style={{ 
                marginTop: "var(--orbit-space-sm)", 
                color: "rgba(255, 255, 255, 0.9)",
                opacity: showContent ? 1 : 0,
                transform: showContent ? "translateY(0)" : "translateY(20px)",
                transition: "opacity 0.8s ease 0.4s, transform 0.8s ease 0.4s"
              }}
            >
              Серия дней: {streakDays} {streakDays === 1 ? "день" : streakDays < 5 ? "дня" : "дней"}
            </p>
          )}
        </div>
      </div>
    </section>
  );
}

