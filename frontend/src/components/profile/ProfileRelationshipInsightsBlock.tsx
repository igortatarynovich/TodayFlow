"use client";

import type { CompactUserModel } from "@/lib/types";
import styles from "./quickMap/profileQuickMap.module.css";

type Props = {
  cum: CompactUserModel | null | undefined;
};

export function ProfileRelationshipInsightsBlock({ cum }: Props) {
  const insights = (cum?.relationship_insights_top_k ?? []).filter((row) => row.label?.trim());
  if (!insights.length) return null;

  return (
    <section
      className={styles.quickMapSection}
      data-testid="profile-relationship-insights"
      aria-labelledby="profile-relationship-insights-title"
    >
      <p className={styles.quickMapSectionLabel}>Отношения</p>
      <p id="profile-relationship-insights-title" className={styles.quickMapSectionTitle}>
        Ты подтвердил
      </p>
      <div style={{ display: "flex", flexDirection: "column", gap: "0.65rem", marginTop: "0.55rem" }}>
        {insights.map((item) => (
          <article key={item.knowledge_id ?? item.label} className={styles.quickMapCard}>
            <p style={{ margin: 0, fontSize: "0.72rem", fontWeight: 600, color: "#8b7355" }}>
              {item.kind === "attachment_lens" ? "Паттерн привязанности" : "Наблюдение"}
            </p>
            <p style={{ margin: "0.25rem 0 0", fontSize: "0.9375rem", lineHeight: 1.5, color: "#3d3228" }}>
              {item.label}
            </p>
            {item.summary && item.summary !== item.label ? (
              <p style={{ margin: "0.35rem 0 0", fontSize: "0.82rem", lineHeight: 1.45, color: "#6b5340" }}>
                {item.summary}
              </p>
            ) : null}
          </article>
        ))}
      </div>
    </section>
  );
}
