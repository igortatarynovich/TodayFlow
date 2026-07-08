"use client";

interface ArchetypeCardProps {
  type: "sun" | "moon" | "rising";
  title: string;
  description: string;
  subtitle: string;
}

const archetypeConfig = {
  sun: {
    icon: "☉",
    background: "#fefcf9",
    borderColor: "#b87333",
  },
  moon: {
    icon: "☽",
    background: "#f8f6f3",
    borderColor: "#e5e0d8",
  },
  rising: {
    icon: "↑",
    background: "#ffffff",
    borderColor: "#e5e0d8",
  },
};

export function ArchetypeCard({ type, title, description, subtitle }: ArchetypeCardProps) {
  const config = archetypeConfig[type];

  return (
    <div className="orbit-card" style={{
      padding: "var(--orbit-space-lg)",
      background: config.background,
      border: `1px solid ${config.borderColor}`
    }}>
      <div style={{ fontSize: "2rem", marginBottom: "var(--orbit-space-sm)" }}>{config.icon}</div>
      <h3 className="orbit-body" style={{
        fontWeight: 600,
        marginBottom: "var(--orbit-space-xs)",
        color: "#0f172a"
      }}>
        {title}
      </h3>
      <p className="orbit-body-sm" style={{ color: "#334155", marginBottom: "var(--orbit-space-xs)", fontWeight: 500 }}>
        {description}
      </p>
      <p className="orbit-body-xs orbit-text-muted" style={{ lineHeight: 1.5 }}>
        {subtitle}
      </p>
    </div>
  );
}

