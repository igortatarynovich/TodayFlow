"use client";

import { OrientationRail } from "@/components/orbit";
import { t } from "@/lib/i18n";
import type { AllHoroscopesResponse } from "@/lib/types";

interface HoroscopesResultsProps {
  horoscopes: AllHoroscopesResponse;
  showResults: boolean;
}

export function HoroscopesResults({ horoscopes, showResults }: HoroscopesResultsProps) {
  return (
    <section 
      className="orbit-hero-content-block"
      style={{
        paddingTop: "var(--orbit-space-xl)",
        paddingBottom: "var(--orbit-space-4xl)",
        opacity: showResults ? 1 : 0,
        transform: showResults ? "translateY(0)" : "translateY(30px)",
        transition: "opacity 0.8s ease, transform 0.8s ease"
      }}
    >
      <div className="orbit-hero-content-container" style={{ 
        gridTemplateColumns: "1fr",
        maxWidth: "100%",
        overflow: "hidden",
        paddingLeft: "var(--orbit-space-xl)",
        paddingRight: "var(--orbit-space-xl)"
      }}>
        <div className="orbit-horoscopes-waterfall" style={{ 
          display: "flex",
          flexDirection: "row",
          gap: "var(--orbit-space-lg)",
          overflowX: "auto",
          paddingBottom: "var(--orbit-space-lg)",
          paddingTop: "var(--orbit-space-sm)",
          scrollbarWidth: "thin",
          scrollbarColor: "var(--orbit-color-border) transparent",
          WebkitOverflowScrolling: "touch",
          position: "relative"
        }}>
          {/* Western Astrology */}
          {horoscopes.astrology && (
            <div 
              className="orbit-card" 
              style={{ 
                minWidth: "300px",
                maxWidth: "350px",
                flexShrink: 0,
                opacity: showResults ? 1 : 0,
                transform: showResults ? "translateY(0)" : "translateY(20px)",
                transition: "opacity 0.8s ease 0.3s, transform 0.8s ease 0.3s"
              }}
            >
              <OrientationRail
                sectionLabel="АСТРОЛОГИЯ"
                metaLabel={t("horoscopes.western.tradition", "Западная традиция")}
              />
              <div style={{ marginTop: "var(--orbit-space-md)" }}>
                <svg width={40} height={40} style={{ opacity: 0.8, marginBottom: "var(--orbit-space-sm)" }} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <circle cx="12" cy="12" r="10"/>
                  <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
                  <circle cx="12" cy="12" r="3"/>
                </svg>
                <h3 className="orbit-display-xs" style={{ marginBottom: "var(--orbit-space-xs)" }}>
                  {horoscopes.astrology.sun && `Солнце: ${horoscopes.astrology.sun}`}
                  {horoscopes.astrology.moon && ` · Луна: ${horoscopes.astrology.moon}`}
                  {horoscopes.astrology.rising && ` · Восходящий: ${horoscopes.astrology.rising}`}
                </h3>
                <p className="orbit-body-sm orbit-text-muted">
                  {horoscopes.astrology.description}
                </p>
              </div>
            </div>
          )}

          {/* Chinese Zodiac */}
          <div 
            className="orbit-card" 
            style={{ 
              minWidth: "300px",
              maxWidth: "350px",
              flexShrink: 0,
              opacity: showResults ? 1 : 0,
              transform: showResults ? "translateY(0)" : "translateY(20px)",
              transition: "opacity 0.8s ease 0.4s, transform 0.8s ease 0.4s"
            }}
          >
            <OrientationRail
              sectionLabel="ВОСТОЧНЫЙ"
              metaLabel={t("horoscopes.chinese.zodiac", "Китайский зодиак")}
            />
            <div style={{ marginTop: "var(--orbit-space-md)" }}>
              <svg width={40} height={40} style={{ opacity: 0.8, marginBottom: "var(--orbit-space-sm)" }} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                <circle cx="12" cy="12" r="10"/>
                <path d="M12 2v20M2 12h20"/>
                <circle cx="12" cy="12" r="2"/>
              </svg>
              <h3 className="orbit-display-xs" style={{ marginBottom: "var(--orbit-space-xs)" }}>
                {horoscopes.chinese.element} {horoscopes.chinese.animal}
              </h3>
              <p className="orbit-body-sm orbit-text-muted">
                {horoscopes.chinese.description}
              </p>
              <div style={{ display: "flex", flexWrap: "wrap", gap: "var(--orbit-space-xs)", marginTop: "var(--orbit-space-sm)" }}>
                {horoscopes.chinese.traits.slice(0, 3).map((trait, idx) => (
                  <span key={idx} className="orbit-badge-xs">{trait}</span>
                ))}
              </div>
            </div>
          </div>

          {/* Zoroastrian Horoscope */}
          {horoscopes.zoroastrian && (
            <div 
              className="orbit-card" 
              style={{ 
                minWidth: "300px",
                maxWidth: "350px",
                flexShrink: 0,
                opacity: showResults ? 1 : 0,
                transform: showResults ? "translateY(0)" : "translateY(20px)",
                transition: "opacity 0.8s ease 0.5s, transform 0.8s ease 0.5s"
              }}
            >
              <OrientationRail
                sectionLabel="ЗОРОАСТРИЙСКИЙ"
                metaLabel={t("horoscopes.zoroastrian.tradition", "Персидская традиция")}
              />
              <div style={{ marginTop: "var(--orbit-space-md)" }}>
                <svg width={40} height={40} style={{ opacity: 0.8, marginBottom: "var(--orbit-space-sm)" }} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <path d="M12 2L2 7l10 5 10-5-10-5z"/>
                  <path d="M2 17l10 5 10-5"/>
                  <path d="M2 12l10 5 10-5"/>
                </svg>
                <h3 className="orbit-display-xs" style={{ marginBottom: "var(--orbit-space-xs)" }}>
                  {horoscopes.zoroastrian.month} · {horoscopes.zoroastrian.day}
                </h3>
                <p className="orbit-body-sm orbit-text-muted">
                  {horoscopes.zoroastrian.description}
                </p>
                <p className="orbit-body-sm" style={{ marginTop: "var(--orbit-space-xs)", color: "var(--orbit-color-highlight)" }}>
                  Божество: {horoscopes.zoroastrian.deity.name}
                </p>
                <div style={{ display: "flex", flexWrap: "wrap", gap: "var(--orbit-space-xs)", marginTop: "var(--orbit-space-sm)" }}>
                  {horoscopes.zoroastrian.traits.slice(0, 3).map((trait, idx) => (
                    <span key={idx} className="orbit-badge-xs">{trait}</span>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Vedic Astrology */}
          {horoscopes.vedic && (
            <div 
              className="orbit-card" 
              style={{ 
                minWidth: "300px",
                maxWidth: "350px",
                flexShrink: 0,
                opacity: showResults ? 1 : 0,
                transform: showResults ? "translateY(0)" : "translateY(20px)",
                transition: "opacity 0.8s ease 0.5s, transform 0.8s ease 0.5s"
              }}
            >
              <OrientationRail
                sectionLabel="ВЕДИЧЕСКАЯ АСТРОЛОГИЯ"
                metaLabel="Джйотиш"
              />
              <div style={{ marginTop: "var(--orbit-space-md)" }}>
                <svg width={40} height={40} style={{ opacity: 0.8, marginBottom: "var(--orbit-space-sm)" }} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
                </svg>
                <h3 className="orbit-display-xs" style={{ marginBottom: "var(--orbit-space-xs)" }}>
                  {horoscopes.vedic.sun} / {horoscopes.vedic.moon}
                </h3>
                <p className="orbit-body-sm orbit-text-muted">
                  {horoscopes.vedic.summary}
                </p>
                <div style={{ display: "flex", flexWrap: "wrap", gap: "var(--orbit-space-xs)", marginTop: "var(--orbit-space-sm)" }}>
                  {horoscopes.vedic.traits.slice(0, 3).map((trait, idx) => (
                    <span key={idx} className="orbit-badge-xs">{trait}</span>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Tibetan Astrology */}
          <div 
            className="orbit-card" 
            style={{ 
              minWidth: "300px",
              maxWidth: "350px",
              flexShrink: 0,
              opacity: showResults ? 1 : 0,
              transform: showResults ? "translateY(0)" : "translateY(20px)",
              transition: "opacity 0.8s ease 0.6s, transform 0.8s ease 0.6s"
            }}
          >
            <OrientationRail
              sectionLabel="ТИБЕТСКИЙ"
              metaLabel={t("horoscopes.tibetan.tradition", "Буддийская традиция")}
            />
            <div style={{ marginTop: "var(--orbit-space-md)" }}>
              <svg width={40} height={40} style={{ opacity: 0.8, marginBottom: "var(--orbit-space-sm)" }} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                <circle cx="12" cy="12" r="10"/>
                <path d="M12 2v4M12 18v4M2 12h4M18 12h4"/>
                <circle cx="12" cy="12" r="2"/>
              </svg>
              <h3 className="orbit-display-xs" style={{ marginBottom: "var(--orbit-space-xs)" }}>
                {horoscopes.tibetan.element} {horoscopes.tibetan.animal}
              </h3>
              <p className="orbit-body-sm orbit-text-muted">
                {horoscopes.tibetan.description}
              </p>
              <div style={{ display: "flex", flexWrap: "wrap", gap: "var(--orbit-space-xs)", marginTop: "var(--orbit-space-sm)" }}>
                {horoscopes.tibetan.traits.slice(0, 3).map((trait, idx) => (
                  <span key={idx} className="orbit-badge-xs">{trait}</span>
                ))}
              </div>
            </div>
          </div>

          {/* Numerology */}
          {horoscopes.numerology && (
            <div 
              className="orbit-card" 
              style={{ 
                minWidth: "300px",
                maxWidth: "350px",
                flexShrink: 0,
                opacity: showResults ? 1 : 0,
                transform: showResults ? "translateY(0)" : "translateY(20px)",
                transition: "opacity 0.8s ease 0.7s, transform 0.8s ease 0.7s"
              }}
            >
              <OrientationRail
                sectionLabel="НУМЕРОЛОГИЯ"
                metaLabel={t("horoscopes.numerology.fate", "Числа судьбы")}
              />
              <div style={{ marginTop: "var(--orbit-space-md)" }}>
                <svg width={40} height={40} style={{ opacity: 0.8, marginBottom: "var(--orbit-space-sm)" }} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/>
                </svg>
                <h3 className="orbit-display-xs" style={{ marginBottom: "var(--orbit-space-xs)" }}>
                  Путь: {horoscopes.numerology.life_path}
                </h3>
                <p className="orbit-body-sm orbit-text-muted">
                  {horoscopes.numerology.life_path_summary}
                </p>
                <p className="orbit-body-sm" style={{ marginTop: "var(--orbit-space-sm)", color: "var(--orbit-color-slate)" }}>
                  Выражение: {horoscopes.numerology.expression}
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}

