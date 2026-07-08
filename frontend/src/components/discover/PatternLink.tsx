"use client";

import Link from "next/link";

interface PatternLinkProps {
  axisId: string;
  patternName: string;
  message?: string;
  variant?: "after-practice" | "after-journal" | "default";
}

/**
 * Компонент для отображения связи с паттерном после действия
 * Используется в практиках и журналах
 */
export function PatternLink({ 
  axisId, 
  patternName, 
  message,
  variant = "default" 
}: PatternLinkProps) {
  const defaultMessages = {
    "after-practice": `Ты только что поработал с паттерном ${patternName}.`,
    "after-journal": `Твоя запись связана с паттерном ${patternName}.`,
    "default": `Это связано с паттерном ${patternName}.`,
  };

  const displayMessage = message || defaultMessages[variant];

  return (
    <div
      style={{
        padding: "var(--orbit-space-md)",
        background: "#fefcf9",
        border: "1px solid #e5e0d8",
        borderRadius: "var(--orbit-radius-sm)",
        marginTop: "var(--orbit-space-md)"
      }}
    >
      <p className="orbit-body-sm" style={{
        marginBottom: "var(--orbit-space-xs)",
        color: "#334155",
        lineHeight: 1.5
      }}>
        {displayMessage}
      </p>
      <Link
        href={`/discover/pattern/${axisId}`}
        className="orbit-link"
        style={{
          fontSize: "var(--orbit-text-body-sm)",
          color: "#b87333",
          textDecoration: "none",
          fontWeight: 500
        }}
      >
        → Посмотреть, как он устроен в твоей карте
      </Link>
    </div>
  );
}

