"use client";

import { ProfileExpandableSection } from "@/components/profile/ProfileExpandableSection";
import { ProfileSurfaceTile } from "@/components/profile/ProfileSurface";

export type ChartPillar = {
  title: string;
  body: string;
};

export function ProfileChartPillars({ pillars }: { pillars: ChartPillar[] }) {
  const ready = pillars.filter((p) => p.body.trim().length > 0);
  if (!ready.length) return null;
  return (
    <ProfileExpandableSection
      id="profile-chart-pillars"
      title="Главные опоры карты"
      subtitle="Коротко: как Солнце, Луна, асцендент и ключевые планеты задают базовый тон — без «списка планет ради списка»."
      defaultOpen
    >
      <div style={{ display: "grid", gap: "0.65rem", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))" }}>
        {ready.map((p) => (
          <ProfileSurfaceTile key={p.title} tone="sm">
            <p className="orbit-body-sm" style={{ margin: 0, fontWeight: 700, color: "#0f172a" }}>
              {p.title}
            </p>
            <p className="orbit-body-xs" style={{ margin: "0.4rem 0 0", color: "#475569", lineHeight: 1.7 }}>
              {p.body}
            </p>
          </ProfileSurfaceTile>
        ))}
      </div>
    </ProfileExpandableSection>
  );
}
