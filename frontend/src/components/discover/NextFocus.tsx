"use client";

import Link from "next/link";

interface NextFocusProps {
  nextPattern?: {
    axis_id: string;
    name: string;
  };
  nextDomain?: string;
  isGuest?: boolean;
}

/**
 * Блок "Следующий фокус" - персональная рекомендация
 * Показывает, какой паттерн или сферу стоит изучить следующей
 */
export function NextFocus({ nextPattern, nextDomain, isGuest = false }: NextFocusProps) {
  if (isGuest) {
    return null;
  }

  // Определяем, что показывать (приоритет паттерну)
  const focusItem = nextPattern || (nextDomain ? { type: "domain", name: nextDomain } : null);

  if (!focusItem) {
    return null;
  }

  const href = nextPattern 
    ? `/discover/pattern/${nextPattern.axis_id}`
    : `/discover#${nextDomain?.toLowerCase().replace(/\s+/g, "-")}`;

  const title = nextPattern
    ? `Следующий важный фокус для тебя — паттерн «${nextPattern.name}»`
    : `Следующий важный фокус для тебя — сфера «${nextDomain}»`;

  return (
    <section
      style={{
        paddingTop: "var(--orbit-space-2xl)",
        paddingBottom: "var(--orbit-space-2xl)",
        background: "transparent"
      }}
    >
      <div style={{ maxWidth: "1200px", margin: "0 auto", width: "100%", padding: "0 var(--orbit-space-xl)" }}>
        <div
          className="orbit-card"
          style={{
            padding: "var(--orbit-space-xl)",
            background: "#fefcf9",
            border: "2px solid #b87333",
            borderRadius: "var(--orbit-radius-md)",
            textAlign: "center"
          }}
        >
          <p className="orbit-body" style={{
            marginBottom: "var(--orbit-space-lg)",
            color: "#0f172a",
            lineHeight: 1.6
          }}>
            {title}
          </p>
          <Link
            href={href}
            className="orbit-button orbit-button-primary"
            style={{
              textDecoration: "none"
            }}
          >
            Посмотреть →
          </Link>
        </div>
      </div>
    </section>
  );
}

