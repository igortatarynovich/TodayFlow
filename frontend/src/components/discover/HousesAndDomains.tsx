"use client";

import { useState } from "react";
import Link from "next/link";

interface HousesAndDomainsProps {
  houses?: Record<string, any>;
  houseReferences?: Array<{ id: string; name: string; number?: number; description?: string }>;
  isGuest?: boolean;
}

// Описания домов (что означает каждый дом)
const houseMeanings: Record<number, { general: string; personal: string }> = {
  1: {
    general: "Дом личности и самовыражения. Показывает, как ты входишь в мир и как тебя воспринимают.",
    personal: "Это твой способ предъявления себя миру. Здесь активны энергии, которые определяют твою внешнюю идентичность.",
  },
  2: {
    general: "Дом ресурсов и ценностей. Отвечает за материальные блага, деньги, самооценку и то, что ты ценишь.",
    personal: "Здесь проявляется твоё отношение к материальному миру и то, через что ты чувствуешь свою ценность.",
  },
  3: {
    general: "Дом общения и обучения. Отвечает за коммуникацию, мышление, близкое окружение и обучение.",
    personal: "Это твой стиль общения, способ обработки информации и взаимодействия с ближайшим окружением.",
  },
  4: {
    general: "Дом дома и семьи. Отвечает за корни, семью, внутренний мир, эмоциональную основу.",
    personal: "Здесь проявляется твоя потребность в безопасности, связь с семьёй и то, что даёт тебе опору.",
  },
  5: {
    general: "Дом творчества и самовыражения. Отвечает за творчество, любовь, детей, удовольствия и игру.",
    personal: "Это сфера, где ты можешь выразить себя свободно, получать удовольствие и проявлять творчество.",
  },
  6: {
    general: "Дом работы и здоровья. Отвечает за повседневную работу, здоровье, рутину и служение.",
    personal: "Здесь проявляется твой подход к работе, заботе о здоровье и организации повседневной жизни.",
  },
  7: {
    general: "Дом партнёрства. Отвечает за отношения, партнёрство, брак и то, как ты взаимодействуешь с другими.",
    personal: "Это твой стиль в отношениях и то, что ты ищешь в партнёрах и близких связях.",
  },
  8: {
    general: "Дом трансформации и глубины. Отвечает за кризисы, трансформацию, общие ресурсы и тайны.",
    personal: "Здесь происходят глубокие изменения, работа с травмами и доступ к общим ресурсам.",
  },
  9: {
    general: "Дом мировоззрения и расширения. Отвечает за философию, высшее образование, путешествия и смыслы.",
    personal: "Это твоё стремление к расширению горизонтов, поиск смыслов и формирование мировоззрения.",
  },
  10: {
    general: "Дом карьеры и статуса. Отвечает за профессию, репутацию, общественное положение и достижения.",
    personal: "Здесь проявляется твоя карьерная ориентация, амбиции и то, как ты хочешь быть признан в обществе.",
  },
  11: {
    general: "Дом дружбы и сообществ. Отвечает за дружбу, группы, мечты, инновации и будущее.",
    personal: "Это твои дружеские связи, участие в сообществах и мечты о будущем.",
  },
  12: {
    general: "Дом подсознания и завершения. Отвечает за тайное, подсознание, уединение и завершение циклов.",
    personal: "Здесь проявляется твоя связь с подсознанием, потребность в уединении и работа с прошлым.",
  },
};

export function HousesAndDomains({ houses, houseReferences, isGuest = false }: HousesAndDomainsProps) {
  const [expandedHouse, setExpandedHouse] = useState<number | null>(null);

  if (!houses || !houseReferences || Object.keys(houses).length === 0) {
    return null;
  }

  return (
    <section
      id="domains"
      style={{
        marginBottom: "var(--orbit-space-3xl)",
        paddingTop: "var(--orbit-space-2xl)",
      }}
    >
      <div style={{ marginBottom: "var(--orbit-space-lg)" }}>
        <h2
          className="orbit-display-sm"
          style={{
            fontSize: "clamp(1.5rem, 3vw, 2rem)",
            marginBottom: "var(--orbit-space-sm)",
            color: "#0f172a",
            fontWeight: 500,
          }}
        >
          Дома и жизненные сферы
        </h2>
        <p
          className="orbit-body"
          style={{
            color: "#334155",
            lineHeight: 1.6,
          }}
        >
          Где в жизни происходят основные события. Каждый дом показывает, в какой сфере проявляются разные энергии.
        </p>
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))",
          gap: "var(--orbit-space-md)",
          marginBottom: "var(--orbit-space-2xl)",
        }}
      >
        {Array.from({ length: 12 }, (_, i) => {
          const houseNumber = i + 1;
          const houseKey = `house_${houseNumber}`;
          const houseData = houses[houseKey] as any;
          const houseRef = houseReferences.find(h => h.id === houseKey || h.number === houseNumber);
          
          // Определяем, активен ли дом (есть ли знак или планеты)
          const hasData = houseData && (
            (typeof houseData === 'object' && (houseData.sign || Object.keys(houseData).length > 0)) ||
            (typeof houseData === 'string' && houseData.length > 0)
          );
          
          const houseSign = typeof houseData === 'object' && houseData.sign ? houseData.sign : null;
          const meaning = houseMeanings[houseNumber];
          const isExpanded = expandedHouse === houseNumber;

          return (
            <div
              key={houseNumber}
              className="orbit-card"
              style={{
                padding: "var(--orbit-space-md)",
                background: hasData ? "#fefcf9" : "#ffffff",
                border: hasData ? "2px solid #b87333" : "1px solid #e5e0d8",
                borderRadius: "var(--orbit-radius-md)",
                transition: "all 0.2s ease",
                cursor: "pointer",
                opacity: isGuest && !hasData ? 0.6 : 1,
              }}
              onClick={() => !isGuest && setExpandedHouse(isExpanded ? null : houseNumber)}
              onMouseEnter={(e) => {
                if (!isGuest) {
                  e.currentTarget.style.borderColor = "#b87333";
                  e.currentTarget.style.boxShadow = "0 2px 8px rgba(184, 115, 51, 0.1)";
                }
              }}
              onMouseLeave={(e) => {
                if (!isGuest) {
                  e.currentTarget.style.borderColor = hasData ? "#b87333" : "#e5e0d8";
                  e.currentTarget.style.boxShadow = "none";
                }
              }}
            >
              <div style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                marginBottom: "var(--orbit-space-xs)"
              }}>
                <span className="orbit-body-xs" style={{
                  fontWeight: 600,
                  color: "#0f172a"
                }}>
                  {houseNumber} дом
                </span>
                {hasData && (
                  <span style={{
                    width: "8px",
                    height: "8px",
                    borderRadius: "50%",
                    background: "#b87333"
                  }} />
                )}
              </div>
              <h3 className="orbit-body-sm" style={{
                fontWeight: 500,
                color: "#0f172a",
                marginBottom: "var(--orbit-space-xs)"
              }}>
                {houseRef?.name || `Дом ${houseNumber}`}
              </h3>
              {houseSign && (
                <p className="orbit-body-xs orbit-text-muted" style={{
                  marginBottom: "var(--orbit-space-sm)"
                }}>
                  Знак: {houseSign}
                </p>
              )}
              
              {/* Раскрытое описание */}
              {isExpanded && !isGuest && meaning && (
                <div
                  style={{
                    marginTop: "var(--orbit-space-sm)",
                    paddingTop: "var(--orbit-space-sm)",
                    borderTop: "1px solid #e5e0d8",
                  }}
                >
                  <p
                    className="orbit-body-xs"
                    style={{
                      color: "#334155",
                      lineHeight: 1.6,
                      marginBottom: "var(--orbit-space-xs)",
                    }}
                  >
                    {meaning.general}
                  </p>
                  <p
                    className="orbit-body-xs orbit-text-muted"
                    style={{
                      lineHeight: 1.6,
                      fontStyle: "italic",
                    }}
                  >
                    {meaning.personal}
                    {houseSign && ` Знак ${houseSign} в этом доме показывает, как именно это проявляется в твоей жизни.`}
                  </p>
                </div>
              )}

              {/* Для гостей показываем подсказку */}
              {isGuest && !hasData && (
                <p className="orbit-body-xs orbit-text-muted" style={{
                  marginTop: "var(--orbit-space-xs)",
                  fontStyle: "italic",
                }}>
                  После ввода данных
                </p>
              )}
            </div>
          );
        })}
      </div>

      {/* Связь со сферами жизни */}
      {!isGuest && (
        <div
          style={{
            padding: "var(--orbit-space-lg)",
            background: "#f5f5f0",
            borderRadius: "var(--orbit-radius-md)",
            border: "1px solid #e5e0d8",
          }}
        >
          <p
            className="orbit-body-sm"
            style={{
              color: "#334155",
              lineHeight: 1.6,
              marginBottom: "var(--orbit-space-sm)",
            }}
          >
            <strong>Как это связано со сферами жизни?</strong>
          </p>
          <p
            className="orbit-body-xs orbit-text-muted"
            style={{
              lineHeight: 1.6,
              marginBottom: "var(--orbit-space-md)",
            }}
          >
            Дома показывают, где в жизни проявляются разные энергии. Например, 7 дом связан со сферой &quot;Любовь и отношения&quot;, 
            10 дом — с &quot;Карьерой&quot;, 2 дом — с &quot;Деньгами&quot;. Ниже ты увидишь, как эти энергии проявляются конкретно в твоих сферах жизни.
          </p>
          <Link
            href="#domains"
            className="orbit-button orbit-button-secondary orbit-button-sm"
            style={{
              textDecoration: "none",
              display: "inline-block",
            }}
          >
            Смотреть сферы жизни ↓
          </Link>
        </div>
      )}
    </section>
  );
}

