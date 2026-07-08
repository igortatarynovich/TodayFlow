"use client";

interface CoreTrioProps {
  sun?: string;
  moon?: string;
  rising?: string;
  isGuest?: boolean;
}

export function CoreTrio({ sun, moon, rising, isGuest = false }: CoreTrioProps) {
  const coreItems = [
    {
      symbol: "☉",
      name: "Солнце",
      sign: sun,
      description: "Направление и воля",
    },
    {
      symbol: "☽",
      name: "Луна",
      sign: moon,
      description: "Как ты чувствуешь",
    },
    {
      symbol: "↑",
      name: "Асцендент",
      sign: rising,
      description: "Как ты входишь в мир",
    },
  ].filter((item) => item.sign); // Показываем только те, у которых есть знак

  if (coreItems.length === 0) {
    return null;
  }

  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
        gap: "var(--orbit-space-lg)",
        marginBottom: "var(--orbit-space-2xl)",
      }}
    >
      {coreItems.map((item) => (
        <div
          key={item.name}
          className="orbit-card"
          style={{
            padding: "var(--orbit-space-xl)",
            background: "#ffffff",
            border: "1px solid #e5e0d8",
            borderRadius: "var(--orbit-radius-md)",
            textAlign: "center",
            transition: "all 0.2s ease",
          }}
        >
          <div
            style={{
              fontSize: "3rem",
              marginBottom: "var(--orbit-space-md)",
              opacity: isGuest ? 0.5 : 1,
            }}
          >
            {item.symbol}
          </div>
          <h3
            className="orbit-body"
            style={{
              fontWeight: 600,
              marginBottom: "var(--orbit-space-xs)",
              color: "#0f172a",
            }}
          >
            {item.name}
          </h3>
          {item.sign ? (
            <p
              className="orbit-body-sm"
              style={{
                color: "#334155",
                marginBottom: "var(--orbit-space-sm)",
                fontWeight: 500,
                opacity: isGuest ? 0.6 : 1,
              }}
            >
              {item.sign}
            </p>
          ) : (
            <p
              className="orbit-body-xs orbit-text-muted"
              style={{ marginBottom: "var(--orbit-space-sm)" }}
            >
              {isGuest ? "После ввода данных" : "Не указано"}
            </p>
          )}
          <p
            className="orbit-body-xs orbit-text-muted"
            style={{
              lineHeight: 1.5,
              opacity: isGuest ? 0.6 : 1,
            }}
          >
            {item.description}
          </p>
        </div>
      ))}
    </div>
  );
}

