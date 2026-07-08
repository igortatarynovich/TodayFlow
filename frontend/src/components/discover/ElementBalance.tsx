"use client";

import { Element, elementNames, getElement } from "@/lib/zodiac-utils";

interface ElementBalanceProps {
  signs: string[];
  isGuest?: boolean;
}

export function ElementBalance({ signs, isGuest = false }: ElementBalanceProps) {
  const elements: Element[] = ["Fire", "Earth", "Air", "Water"];

  // Вычисляем реальный баланс из знаков пользователя
  // Логика: считаем, сколько знаков каждой стихии в Core Trio (Солнце, Луна, Асцендент)
  const totalSigns = signs.length || 1;
  const elementCounts = elements.reduce((acc, element) => {
    acc[element] = signs.filter(sign => {
      const signElement = getElement(sign);
      return signElement === element;
    }).length;
    return acc;
  }, {} as Record<Element, number>);

  return (
    <div
      style={{
        marginBottom: "var(--orbit-space-xl)",
      }}
    >
      <h3
        className="orbit-body"
        style={{
          marginBottom: "var(--orbit-space-md)",
          color: "#0f172a",
          fontWeight: 500,
        }}
      >
        Баланс стихий
      </h3>
      <div
        style={{
          display: "flex",
          gap: "var(--orbit-space-md)",
          alignItems: "flex-end",
          height: "80px",
          marginBottom: "var(--orbit-space-sm)",
        }}
      >
        {elements.map((element) => {
          const count = elementCounts[element];
          const percentage = (count / totalSigns) * 100;
          const height = Math.max(15, percentage); // Минимум 15% для видимости

          return (
            <div
              key={element}
              style={{
                flex: 1,
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                gap: "var(--orbit-space-xs)",
              }}
              title={`${elementNames[element]}: ${count} из ${totalSigns} (${Math.round(percentage)}%)`}
            >
              <div
                style={{
                  width: "100%",
                  height: `${height}%`,
                  backgroundColor: isGuest ? "#e5e0d8" : "#b87333",
                  borderRadius: "4px 4px 0 0",
                  transition: "all 0.3s ease",
                  opacity: isGuest ? 0.5 : 1,
                  minHeight: "15px",
                  display: "flex",
                  alignItems: "flex-end",
                  justifyContent: "center",
                  paddingBottom: "4px",
                }}
              >
                {!isGuest && count > 0 && (
                  <span
                    className="orbit-body-xs"
                    style={{
                      color: "#ffffff",
                      fontWeight: 600,
                    }}
                  >
                    {count}
                  </span>
                )}
              </div>
              <span
                className="orbit-body-sm"
                style={{
                  color: "#334155",
                  opacity: isGuest ? 0.6 : 1,
                  fontWeight: count > 0 ? 500 : 400,
                }}
              >
                {elementNames[element]}
              </span>
            </div>
          );
        })}
      </div>
      {!isGuest && (
        <p
          className="orbit-body-xs orbit-text-muted"
          style={{
            fontStyle: "italic",
            lineHeight: 1.5,
          }}
        >
          Это показывает, через какие энергии ты чаще всего проживаешь жизнь.
        </p>
      )}
    </div>
  );
}

