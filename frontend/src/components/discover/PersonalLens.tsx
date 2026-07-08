"use client";

import { useState } from "react";
import Link from "next/link";

interface LensChip {
  id: string;
  category: "ТЕМА" | "ПАТТЕРН" | "СТРЕСС" | "ОТНОШЕНИЯ" | "РЕШЕНИЯ";
  name: string;
  description?: string;
  locked?: boolean;
  content?: {
    whatItMeans: string;
    howItManifests: string[];
    whatToDo: {
      text: string;
      cta: string;
      href: string;
    };
    whereUsed: string[];
  };
}

interface PersonalLensProps {
  lens: LensChip[];
  isGuest?: boolean;
}

export function PersonalLens({ lens, isGuest = false }: PersonalLensProps) {
  const [selectedChip, setSelectedChip] = useState<string | null>(null);

  if (!lens || lens.length === 0) {
    return null;
  }

  const selectedLens = lens.find((l) => l.id === selectedChip);

  return (
    <section
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
          Твоя линза
        </h2>
        <p
          className="orbit-body"
          style={{
            color: "#334155",
            lineHeight: 1.6,
          }}
        >
          Это твой персональный фильтр. Он определяет, как TodayFlow показывает тебе практики, таро, карту дня и разборы.
        </p>
      </div>

      {/* Чипы линзы */}
      <div
        style={{
          display: "flex",
          flexWrap: "wrap",
          gap: "var(--orbit-space-md)",
          marginBottom: selectedLens ? "var(--orbit-space-xl)" : 0,
        }}
      >
        {lens.map((chip) => (
          <button
            key={chip.id}
            onClick={() => !chip.locked && setSelectedChip(selectedChip === chip.id ? null : chip.id)}
            disabled={chip.locked}
            style={{
              padding: "var(--orbit-space-md) var(--orbit-space-lg)",
              background: chip.locked
                ? "#f5f5f0"
                : selectedChip === chip.id
                ? "#fefcf9"
                : "#ffffff",
              border: chip.locked
                ? "1px solid #e5e0d8"
                : selectedChip === chip.id
                ? "2px solid #b87333"
                : "1px solid #e5e0d8",
              borderRadius: "var(--orbit-radius-md)",
              cursor: chip.locked ? "not-allowed" : "pointer",
              transition: "all 0.2s ease",
              opacity: chip.locked ? 0.6 : 1,
              textAlign: "left",
              display: "flex",
              flexDirection: "column",
              gap: "var(--orbit-space-xs)",
              minWidth: "200px",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: "var(--orbit-space-xs)" }}>
              <span
                className="orbit-body-xs"
                style={{
                  fontWeight: 600,
                  color: "#6b7280",
                  textTransform: "uppercase",
                  letterSpacing: "0.5px",
                }}
              >
                {chip.category}
              </span>
              {chip.locked && <span style={{ fontSize: "0.875rem" }}>🔒</span>}
            </div>
            <span
              className="orbit-body"
              style={{
                fontWeight: 500,
                color: "#0f172a",
              }}
            >
              {chip.name}
            </span>
            {chip.description && (
              <span
                className="orbit-body-xs orbit-text-muted"
                style={{ lineHeight: 1.4 }}
              >
                {chip.description}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Панель раскрытия */}
      {selectedLens && selectedLens.content && !selectedLens.locked && (
        <div
          className="orbit-card"
          style={{
            padding: "var(--orbit-space-xl)",
            background: "#ffffff",
            border: "1px solid #e5e0d8",
            borderRadius: "var(--orbit-radius-md)",
          }}
        >
          {/* Что это значит */}
          <div style={{ marginBottom: "var(--orbit-space-lg)" }}>
            <h3
              className="orbit-body"
              style={{
                fontWeight: 600,
                marginBottom: "var(--orbit-space-sm)",
                color: "#0f172a",
              }}
            >
              Что это значит
            </h3>
            <p
              className="orbit-body-sm"
              style={{
                color: "#334155",
                lineHeight: 1.6,
              }}
            >
              {selectedLens.content.whatItMeans}
            </p>
          </div>

          {/* Как проявляется */}
          {selectedLens.content.howItManifests && selectedLens.content.howItManifests.length > 0 && (
            <div style={{ marginBottom: "var(--orbit-space-lg)" }}>
              <h3
                className="orbit-body"
                style={{
                  fontWeight: 600,
                  marginBottom: "var(--orbit-space-sm)",
                  color: "#0f172a",
                }}
              >
                Как проявляется у тебя
              </h3>
              <ul
                style={{
                  listStyle: "none",
                  padding: 0,
                  margin: 0,
                  display: "flex",
                  flexDirection: "column",
                  gap: "var(--orbit-space-xs)",
                }}
              >
                {selectedLens.content.howItManifests.map((item, i) => (
                  <li
                    key={i}
                    className="orbit-body-sm"
                    style={{
                      color: "#334155",
                      paddingLeft: "var(--orbit-space-md)",
                      position: "relative",
                    }}
                  >
                    <span
                      style={{
                        position: "absolute",
                        left: 0,
                        top: "0.5em",
                        width: "4px",
                        height: "4px",
                        borderRadius: "50%",
                        background: "#b87333",
                      }}
                    />
                    {item}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Что делать сегодня */}
          {selectedLens.content.whatToDo && (
            <div style={{ marginBottom: "var(--orbit-space-lg)" }}>
              <h3
                className="orbit-body"
                style={{
                  fontWeight: 600,
                  marginBottom: "var(--orbit-space-sm)",
                  color: "#0f172a",
                }}
              >
                Что делать сегодня
              </h3>
              <p
                className="orbit-body-sm"
                style={{
                  color: "#334155",
                  marginBottom: "var(--orbit-space-sm)",
                  lineHeight: 1.6,
                }}
              >
                {selectedLens.content.whatToDo.text}
              </p>
              <Link
                href={selectedLens.content.whatToDo.href}
                className="orbit-button orbit-button-primary orbit-button-sm"
                style={{
                  textDecoration: "none",
                  display: "inline-block",
                }}
              >
                {selectedLens.content.whatToDo.cta} →
              </Link>
            </div>
          )}

          {/* Где используется */}
          {selectedLens.content.whereUsed && selectedLens.content.whereUsed.length > 0 && (
            <div>
              <h3
                className="orbit-body"
                style={{
                  fontWeight: 600,
                  marginBottom: "var(--orbit-space-sm)",
                  color: "#0f172a",
                }}
              >
                Где это применяется
              </h3>
              <div
                style={{
                  display: "flex",
                  flexWrap: "wrap",
                  gap: "var(--orbit-space-sm)",
                }}
              >
                {selectedLens.content.whereUsed.map((item, i) => (
                  <span
                    key={i}
                    className="orbit-body-xs"
                    style={{
                      padding: "var(--orbit-space-xs) var(--orbit-space-sm)",
                      background: "#f5f5f0",
                      borderRadius: "var(--orbit-radius-sm)",
                      color: "#334155",
                    }}
                  >
                    {item}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Правило "Почему это показывается" */}
      <div style={{ marginTop: "var(--orbit-space-lg)" }}>
        <details
          style={{
            cursor: "pointer",
          }}
        >
          <summary
            className="orbit-body-xs orbit-text-muted"
            style={{
              listStyle: "none",
              cursor: "pointer",
              textDecoration: "underline",
            }}
          >
            Почему TodayFlow показывает это?
          </summary>
          <p
            className="orbit-body-xs orbit-text-muted"
            style={{
              marginTop: "var(--orbit-space-sm)",
              paddingLeft: "var(--orbit-space-md)",
              lineHeight: 1.6,
            }}
          >
            Эти выводы собраны из твоих данных (карта рождения + внутренние паттерны) и активности в приложении.
          </p>
        </details>
      </div>
    </section>
  );
}

