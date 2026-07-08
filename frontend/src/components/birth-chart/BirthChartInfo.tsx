"use client";

export function BirthChartInfo() {
  return (
    <div style={{ 
      marginTop: "var(--orbit-space-xl)",
      padding: "var(--orbit-space-lg)",
      background: "var(--orbit-color-mist)",
      borderRadius: "var(--orbit-radius-md)",
      border: "1px solid var(--orbit-color-border-light)"
    }}>
      <h3 className="orbit-body" style={{ fontWeight: 600, marginBottom: "var(--orbit-space-sm)" }}>
        Что такое астро профиль?
      </h3>
      <div style={{ display: "grid", gap: "var(--orbit-space-sm)" }}>
        <p className="orbit-body-sm" style={{ lineHeight: 1.6 }}>
          <strong>Астро профиль</strong> — это ваши данные рождения, на основе которых рассчитываются:
        </p>
        <ul style={{ 
          listStyle: "none", 
          padding: 0, 
          margin: 0,
          display: "grid",
          gap: "var(--orbit-space-xs)"
        }}>
          <li className="orbit-body-sm" style={{ lineHeight: 1.6, display: "flex", alignItems: "flex-start", gap: "var(--orbit-space-xs)" }}>
            <span style={{ color: "var(--orbit-color-highlight)" }}>•</span>
            <span>Персонализированные практики и рекомендации</span>
          </li>
          <li className="orbit-body-sm" style={{ lineHeight: 1.6, display: "flex", alignItems: "flex-start", gap: "var(--orbit-space-xs)" }}>
            <span style={{ color: "var(--orbit-color-highlight)" }}>•</span>
            <span>Карта дня и таро расклады</span>
          </li>
          <li className="orbit-body-sm" style={{ lineHeight: 1.6, display: "flex", alignItems: "flex-start", gap: "var(--orbit-space-xs)" }}>
            <span style={{ color: "var(--orbit-color-highlight)" }}>•</span>
            <span>Анализ паттернов и совместимости</span>
          </li>
          <li className="orbit-body-sm" style={{ lineHeight: 1.6, display: "flex", alignItems: "flex-start", gap: "var(--orbit-space-xs)" }}>
            <span style={{ color: "var(--orbit-color-highlight)" }}>•</span>
            <span>Ежедневные инсайты и разборы</span>
          </li>
        </ul>
        <p className="orbit-body-xs orbit-text-muted" style={{ marginTop: "var(--orbit-space-sm)", lineHeight: 1.6 }}>
          Если вы авторизованы, профиль сохранится автоматически и будет использоваться для всех персонализированных функций.
        </p>
      </div>
    </div>
  );
}

