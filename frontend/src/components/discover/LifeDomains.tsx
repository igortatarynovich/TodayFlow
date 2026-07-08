"use client";

import Link from "next/link";
import { FullReportUpsell } from "./FullReportUpsell";

interface LifeDomain {
  id: string;
  name: string;
  description: string;
  influences: Array<{
    type: "Паттерн" | "Тема" | "Луна" | "Дом";
    label: string;
  }>;
  cta: {
    text: string;
    href: string;
  };
}

interface LifeDomainsProps {
  domains?: LifeDomain[];
  isGuest?: boolean;
  axes?: Array<{ axis_id: string; value: number }>;
  sun?: string;
  moon?: string;
  rising?: string;
  personalLens?: {
    top_axes: Array<{ axis_id: string; value: number }>;
    dominant_domains: string[];
  } | null;
  hasFullReport?: boolean;
}

const defaultDomains: Omit<LifeDomain, "description" | "influences">[] = [
  {
    id: "love",
    name: "Любовь и отношения",
    cta: {
      text: "Посмотреть, как это проявляется сейчас",
      href: "/discover#love",
    },
  },
  {
    id: "career",
    name: "Карьера и предназначение",
    cta: {
      text: "Разобрать карьерный фокус",
      href: "/discover#career",
    },
  },
  {
    id: "money",
    name: "Деньги и безопасность",
    cta: {
      text: "Понять свои финансовые паттерны",
      href: "/discover#money",
    },
  },
  {
    id: "family",
    name: "Дом, семья, близкие",
    cta: {
      text: "Увидеть семейную динамику",
      href: "/discover#family",
    },
  },
  {
    id: "life-path",
    name: "Жизненные темы и путь",
    cta: {
      text: "Смотреть полную карту пути",
      href: "/discover#life-path",
    },
  },
];

export function LifeDomains({ domains, isGuest = false, axes, sun, moon, rising, personalLens, hasFullReport = false }: LifeDomainsProps) {
  // Генерируем персональные выводы и влияния, если не предоставлены
  const generateDomain = (domain: Omit<LifeDomain, "description" | "influences">): LifeDomain => {
    // Ищем существующий домен или создаём новый
    const existing = domains?.find((d) => d.id === domain.id);
    if (existing) return existing;

    // Генерируем описание на основе осей
    let description = "";
    const influences: LifeDomain["influences"] = [];

    // Используем Personal Lens для более точных выводов
    const isDominantDomain = personalLens?.dominant_domains?.some(d => {
      const domainMap: Record<string, string> = {
        "Любовь": "love",
        "Карьера": "career",
        "Деньги": "money",
        "Семья": "family",
        "Жизненные темы": "life-path",
      };
      return domainMap[d] === domain.id;
    });

    if (domain.id === "love") {
      const a6 = axes?.find((a) => a.axis_id === "A6");
      const topAxis = personalLens?.top_axes?.[0];
      
      description = a6
        ? a6.value > 0
          ? "В отношениях тебе важно чувствовать свободу и обратную связь, но при этом ты остро реагируешь на нестабильность."
          : "В отношениях тебе нужна автономия и пространство, но при этом ты ценишь глубокую связь."
        : "В отношениях тебе важно найти баланс между близостью и свободой.";
      
      if (a6) {
        influences.push({
          type: "Паттерн",
          label: a6.value > 0 ? "Ориентация на связи" : "Независимость",
        });
      }
      if (moon) {
        influences.push({ type: "Луна", label: `Луна в ${moon}` });
      }
      if (topAxis && topAxis.axis_id === "A6") {
        influences.push({
          type: "Паттерн",
          label: `Доминирующий: ${topAxis.axis_id}`,
        });
      }
    } else if (domain.id === "career") {
      const a5 = axes?.find((a) => a.axis_id === "A5");
      const topAxis = personalLens?.top_axes?.[0];
      
      description = a5
        ? a5.value > 0
          ? "В карьере ты склонен брать инициативу и контролировать процесс, но можешь перегружаться ответственностью."
          : "В карьере ты адаптируешься к обстоятельствам, но можешь терять фокус при неопределённости."
        : "В карьере тебе важно найти баланс между инициативой и адаптивностью.";
      
      if (a5) {
        influences.push({
          type: "Паттерн",
          label: a5.value > 0 ? "Директивный стиль" : "Адаптивный стиль",
        });
      }
      if (sun) {
        influences.push({ type: "Тема", label: `Солнце в ${sun}` });
      }
      if (topAxis && topAxis.axis_id === "A5") {
        influences.push({
          type: "Паттерн",
          label: `Доминирующий: ${topAxis.axis_id}`,
        });
      }
    } else if (domain.id === "money") {
      const a4 = axes?.find((a) => a.axis_id === "A4");
      const topAxis = personalLens?.top_axes?.[0];
      
      description = a4
        ? a4.value > 0
          ? "В финансах ты открыт к изменениям и новым возможностям, но можешь рисковать без достаточной стабильности."
          : "В финансах ты стремишься к стабильности и безопасности, но можешь упускать возможности роста."
        : "В финансах тебе важно найти баланс между стабильностью и возможностями.";
      
      if (a4) {
        influences.push({
          type: "Паттерн",
          label: a4.value > 0 ? "Открытость к изменениям" : "Стремление к стабильности",
        });
      }
      if (topAxis && topAxis.axis_id === "A4") {
        influences.push({
          type: "Паттерн",
          label: `Доминирующий: ${topAxis.axis_id}`,
        });
      }
    } else if (domain.id === "family") {
      const a1 = axes?.find((a) => a.axis_id === "A1");
      const a6 = axes?.find((a) => a.axis_id === "A6");
      
      description = a1
        ? a1.value > 0
          ? "В семье ты ориентируешься на обратную связь и потребности близких, но можешь терять собственные границы."
          : "В семье ты опираешься на внутренние ценности, но можешь быть менее чувствительным к потребностям других."
        : "В семье тебе важно найти баланс между собственными потребностями и потребностями близких.";
      
      if (a1) {
        influences.push({
          type: "Паттерн",
          label: a1.value > 0 ? "Внешняя ориентация" : "Внутренняя ориентация",
        });
      }
      if (a6 && Math.abs(a6.value) > 0.3) {
        influences.push({
          type: "Паттерн",
          label: a6.value > 0 ? "Ориентация на связи" : "Независимость",
        });
      }
      if (rising) {
        influences.push({ type: "Дом", label: `Асцендент в ${rising}` });
      }
    } else if (domain.id === "life-path") {
      const topAxis = personalLens?.top_axes?.[0] || axes
        ?.map((a) => ({ ...a, absValue: Math.abs(a.value) }))
        .sort((a, b) => b.absValue - a.absValue)[0];
      
      description = topAxis
        ? `Твой жизненный путь формируется через паттерн ${topAxis.axis_id}, который определяет основные темы и направления развития.`
        : "Твой жизненный путь формируется через уникальное сочетание паттернов и энергий.";
      
      if (topAxis) {
        influences.push({
          type: "Паттерн",
          label: `Паттерн ${topAxis.axis_id}`,
        });
      }
      if (sun) {
        influences.push({ type: "Тема", label: `Солнце в ${sun}` });
      }
    }

    return {
      ...domain,
      description,
      influences: influences.length > 0 ? influences : [],
    };
  };

  const finalDomains = defaultDomains.map(generateDomain);

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
          Где это проявляется в твоей жизни
        </h2>
        <p
          className="orbit-body"
          style={{
            color: "#334155",
            lineHeight: 1.6,
          }}
        >
          Одни и те же паттерны работают по-разному в разных сферах.
        </p>
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))",
          gap: "var(--orbit-space-lg)",
        }}
      >
        {finalDomains.map((domain) => (
          <div
            key={domain.id}
            className="orbit-card"
            style={{
              padding: "var(--orbit-space-xl)",
              background: "#ffffff",
              border: "1px solid #e5e0d8",
              borderRadius: "var(--orbit-radius-md)",
              display: "flex",
              flexDirection: "column",
              gap: "var(--orbit-space-md)",
            }}
          >
            {/* Название сферы */}
            <h3
              className="orbit-body"
              style={{
                fontWeight: 600,
                color: "#0f172a",
                marginBottom: "var(--orbit-space-xs)",
              }}
            >
              {domain.name}
            </h3>

            {/* Персональный вывод */}
            <p
              className="orbit-body-sm"
              style={{
                color: "#334155",
                lineHeight: 1.6,
                opacity: isGuest ? 0.6 : 1,
              }}
            >
              {isGuest ? "Общий текст для гостей. После ввода данных появится персональный вывод." : domain.description}
            </p>

            {/* Активные влияния */}
            {domain.influences.length > 0 && !isGuest && (
              <div
                style={{
                  display: "flex",
                  flexWrap: "wrap",
                  gap: "var(--orbit-space-xs)",
                }}
              >
                {domain.influences.map((influence, i) => (
                  <span
                    key={i}
                    className="orbit-body-xs"
                    style={{
                      padding: "var(--orbit-space-xs) var(--orbit-space-sm)",
                      background: "#f5f5f0",
                      borderRadius: "var(--orbit-radius-sm)",
                      color: "#334155",
                      cursor: "pointer",
                      transition: "all 0.2s ease",
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.background = "#fefcf9";
                      e.currentTarget.style.border = "1px solid #b87333";
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.background = "#f5f5f0";
                      e.currentTarget.style.border = "none";
                    }}
                    title={`${influence.type}: ${influence.label}`}
                  >
                    <strong>{influence.type}:</strong> {influence.label}
                  </span>
                ))}
              </div>
            )}

            {/* CTA */}
            {isGuest ? (
              <Link
                href="/onboarding/core"
                className="orbit-button orbit-button-secondary orbit-button-sm"
                style={{
                  textDecoration: "none",
                  display: "inline-block",
                  marginTop: "auto",
                }}
              >
                Рассчитать мою карту →
              </Link>
            ) : (
              <>
                <Link
                  href={domain.cta.href}
                  className="orbit-button orbit-button-primary orbit-button-sm"
                  style={{
                    textDecoration: "none",
                    display: "inline-block",
                    marginTop: "auto",
                  }}
                >
                  {domain.cta.text} →
                </Link>
                {/* МОНЕТИЗАЦИЯ: Апселл Full Report в конце карточки сферы */}
                <FullReportUpsell
                  context="domain"
                  domainName={domain.name}
                  hasFullReport={hasFullReport}
                />
              </>
            )}
          </div>
        ))}
      </div>
    </section>
  );
}
