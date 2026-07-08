"use client";

import { useState } from "react";
import { ProfileSurfaceTile } from "@/components/profile/ProfileSurface";

type FitChoice = "yes" | "partial" | "no";

export function ProfileSnippetFitRow({ sectionLabel }: { sectionLabel: string }) {
  const [choice, setChoice] = useState<FitChoice | null>(null);
  return (
    <ProfileSurfaceTile tone="solid">
      <p className="orbit-body-xs" style={{ margin: 0, color: "#64748b", lineHeight: 1.6 }}>
        Насколько близок этот портрет? Отметка поможет со временем уточнять живой слой.
      </p>
      <div style={{ marginTop: "0.65rem", display: "flex", flexWrap: "wrap", gap: "0.45rem" }} role="group" aria-label={`Оценка: ${sectionLabel}`}>
        {(
          [
            { id: "yes" as const, label: "Про меня" },
            { id: "partial" as const, label: "Частично" },
            { id: "no" as const, label: "Не про меня" },
          ] as const
        ).map((b) => (
          <button
            key={b.id}
            type="button"
            className={choice === b.id ? "orbit-button orbit-button-primary orbit-button-sm" : "orbit-button orbit-button-secondary orbit-button-sm"}
            onClick={() => setChoice(b.id)}
          >
            {b.label}
          </button>
        ))}
      </div>
    </ProfileSurfaceTile>
  );
}
