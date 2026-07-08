"use client";

import Link from "next/link";

interface PatternProgressProps {
  viewedPatterns: number; // Сколько паттернов просмотрено
  totalPatterns: number; // Всего паттернов (обычно 7)
  isGuest?: boolean;
}

/**
 * Индикатор прогресса понимания паттернов
 * Показывает, сколько из 7 ключевых паттернов пользователь уже разобрал
 */
export function PatternProgress({ viewedPatterns, totalPatterns, isGuest = false }: PatternProgressProps) {
  if (isGuest) {
    return null;
  }

  const percentage = Math.round((viewedPatterns / totalPatterns) * 100);
  const remaining = totalPatterns - viewedPatterns;

  return (
    <div
      className="orbit-card"
      style={{
        padding: "var(--orbit-space-lg)",
        background: "#fefcf9",
        border: "1px solid #e5e0d8",
        borderRadius: "var(--orbit-radius-md)",
        marginBottom: "var(--orbit-space-xl)"
      }}
    >
      <div style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        marginBottom: "var(--orbit-space-sm)"
      }}>
        <p className="orbit-body-sm" style={{
          color: "#334155",
          fontWeight: 500
        }}>
          Ты разобрал {viewedPatterns} из {totalPatterns} ключевых паттернов
        </p>
        <span className="orbit-body-xs orbit-text-muted" style={{
          color: "#64748b"
        }}>
          {percentage}%
        </span>
      </div>

      {/* Визуальный индикатор прогресса (не геймификация!) */}
      <div style={{
        width: "100%",
        height: "4px",
        background: "#e5e0d8",
        borderRadius: "2px",
        overflow: "hidden",
        marginBottom: "var(--orbit-space-md)"
      }}>
        <div
          style={{
            width: `${percentage}%`,
            height: "100%",
            background: "#b87333",
            transition: "width 0.3s ease"
          }}
        />
      </div>

      {remaining > 0 && (
        <p className="orbit-body-xs orbit-text-muted" style={{
          color: "#64748b",
          lineHeight: 1.5
        }}>
          Осталось {remaining} {remaining === 1 ? "паттерн" : remaining < 5 ? "паттерна" : "паттернов"} для полного понимания своей карты
        </p>
      )}

      {remaining === 0 && (
        <p className="orbit-body-xs" style={{
          color: "#334155",
          lineHeight: 1.5,
          fontStyle: "italic"
        }}>
          Ты изучил все ключевые паттерны. Теперь можешь наблюдать, как они проявляются каждый день.
        </p>
      )}
    </div>
  );
}

