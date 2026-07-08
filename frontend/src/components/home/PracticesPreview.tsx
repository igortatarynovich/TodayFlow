"use client";

import Link from "next/link";

interface Practice {
  id: string;
  title: string;
  description: string;
  icon: string;
  duration: string;
  free: boolean;
}

const PRACTICES: Practice[] = [
  {
    id: "breathing",
    title: "Дыхание",
    description: "Техники дыхания для успокоения и фокуса",
    icon: "🌬️",
    duration: "3-5 мин",
    free: true,
  },
  {
    id: "focus",
    title: "Фокус",
    description: "Практики концентрации и внимательности",
    icon: "🎯",
    duration: "5-10 мин",
    free: true,
  },
  {
    id: "gratitude",
    title: "Благодарность",
    description: "Ежедневная практика благодарности",
    icon: "🙏",
    duration: "3-7 мин",
    free: true,
  },
  {
    id: "desires",
    title: "Желания",
    description: "Работа с намерениями и желаниями",
    icon: "✨",
    duration: "5-10 мин",
    free: true,
  },
  {
    id: "emotional",
    title: "Эмоциональная стабилизация",
    description: "Практики для управления эмоциями",
    icon: "💫",
    duration: "7-10 мин",
    free: false,
  },
];

interface PracticesPreviewProps {
  isAuthenticated?: boolean;
  maxItems?: number;
}

export function PracticesPreview({ isAuthenticated = false, maxItems = 5 }: PracticesPreviewProps) {
  const practicesToShow = PRACTICES.slice(0, maxItems);

  return (
    <div 
      className="practices-preview-grid"
      style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
        gap: "var(--orbit-space-lg)",
        maxWidth: "900px",
        margin: "0 auto",
      }}
    >
      {practicesToShow.map((practice) => (
        <div
          key={practice.id}
          className="orbit-card"
          style={{
            padding: "var(--orbit-space-md)",
            textAlign: "center",
            transition: "transform 0.2s ease, box-shadow 0.2s ease",
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.transform = "translateY(-2px)";
            e.currentTarget.style.boxShadow = "0 4px 12px rgba(0, 0, 0, 0.1)";
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = "translateY(0)";
            e.currentTarget.style.boxShadow = "0 2px 8px rgba(0, 0, 0, 0.05)";
          }}
        >
          <div style={{ fontSize: "2rem", marginBottom: "var(--orbit-space-sm)" }}>
            {practice.icon}
          </div>
          <h3 className="orbit-body" style={{ fontWeight: 600, marginBottom: "var(--orbit-space-xs)" }}>
            {practice.title}
          </h3>
          <p className="orbit-body-sm orbit-text-muted" style={{ marginBottom: "var(--orbit-space-xs)", lineHeight: 1.4 }}>
            {practice.description}
          </p>
          <p className="orbit-body-xs orbit-text-muted" style={{ fontSize: "0.75rem", marginBottom: "var(--orbit-space-sm)" }}>
            {practice.duration}
          </p>
          {!practice.free && !isAuthenticated && (
            <div style={{
              fontSize: "0.7rem",
              color: "var(--orbit-color-coral)",
              fontWeight: 500,
              marginTop: "var(--orbit-space-xs)",
            }}>
              🔒 После регистрации
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

