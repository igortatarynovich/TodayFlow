"use client";

import Image from "next/image";

interface ThematicReportHeroProps {
  title: string;
  description: string;
  icon: string;
  showContent: boolean;
}

export function ThematicReportHero({ title, description, icon, showContent }: ThematicReportHeroProps) {
  return (
    <section className="orbit-hero-design orbit-hero-design-unified">
      <div className="orbit-hero-design-wrapper">
        <Image
          src="/images/hero-meditation.png"
          alt={title}
          fill
          priority
          className="orbit-hero-design-bg"
          style={{ objectFit: "cover", objectPosition: "center" }}
        />
        <div className="orbit-hero-design-overlay" />
        <div className="orbit-hero-design-container">
          <h1
            className="orbit-hero-design-title-text"
            style={{
              opacity: showContent ? 1 : 0,
              transform: showContent ? "translateY(0)" : "translateY(20px)",
              transition: "opacity 0.8s ease, transform 0.8s ease"
            }}
          >
            {icon} {title}
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
            {description}
          </p>
        </div>
      </div>
    </section>
  );
}

