"use client";

import type { CSSProperties, ReactNode } from "react";
import { RITUAL_COPY } from "@/components/today/todayRitualCopy";

export function DaySectionHeader({
  icon,
  title,
  done,
  expanded,
  onToggle,
  /** null — не показывать вторую строку, когда блок отмечен выполненным */
  hintWhenDone = undefined,
}: {
  icon: ReactNode;
  title: string;
  done: boolean;
  expanded: boolean;
  onToggle: () => void;
  hintWhenDone?: string | null;
}) {
  const sub =
    done && hintWhenDone === null
      ? null
      : done
        ? hintWhenDone ?? RITUAL_COPY.daySectionHeaderHintWhenDone
        : RITUAL_COPY.daySectionHeaderHintNextStep;

  return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "var(--orbit-space-lg)", gap: "0.75rem", flexWrap: "wrap" }}>
      <div style={{ display: "flex", alignItems: "center", gap: "var(--orbit-space-md)" }}>
        {icon}
        <div>
          <h2 className="orbit-heading-2" style={{ margin: 0 }}>
            {title}
          </h2>
          {sub ? (
            <p className="orbit-body-xs" style={{ margin: "0.18rem 0 0", color: "#8a6f49" }}>
              {sub}
            </p>
          ) : null}
        </div>
      </div>
      <div style={{ display: "flex", alignItems: "center", gap: "0.55rem" }}>
        {done ? <span style={{ color: "#10b981", fontSize: "1.35rem" }}>✓</span> : null}
        <button onClick={onToggle} className="orbit-button orbit-button-secondary orbit-button-sm">
          {expanded ? RITUAL_COPY.todayUiCollapseCta : RITUAL_COPY.todayUiExpandCta}
        </button>
      </div>
    </div>
  );
}

export function PhaseCard({
  title,
  subtitle,
  children,
}: {
  title: string;
  subtitle?: string;
  children: ReactNode;
}) {
  return (
    <div
      style={{
        padding: "0.95rem",
        background: "rgba(255, 252, 247, 0.95)",
        borderRadius: "16px",
        border: "1px solid rgba(202, 177, 137, 0.32)",
      }}
    >
      <p className="orbit-body-sm" style={{ color: "#8a6f49", marginBottom: subtitle ? "0.2rem" : "var(--orbit-space-xs)", fontWeight: 700 }}>
        {title}
      </p>
      {subtitle ? (
        <p className="orbit-body-xs" style={{ margin: "0 0 0.55rem", color: "#6a5132", lineHeight: 1.55 }}>
          {subtitle}
        </p>
      ) : null}
      {children}
    </div>
  );
}

export function PhaseEmptyState({ text, action }: { text: string; action?: ReactNode }) {
  return (
    <div style={{ padding: "0.95rem", border: "1px solid #e2e8f0", borderRadius: "16px", background: "#f8fafc" }}>
      <p className="orbit-body-sm" style={{ margin: 0, color: "#334155", lineHeight: 1.65 }}>
        {text}
      </p>
      {action ? <div style={{ marginTop: "0.6rem" }}>{action}</div> : null}
    </div>
  );
}

export const summaryChipStyle: CSSProperties = {
  borderRadius: "999px",
  border: "1px solid rgba(194, 166, 120, 0.55)",
  padding: "0.1rem 0.55rem",
  background: "rgba(255, 248, 237, 0.95)",
  color: "#8a6a3c",
  fontWeight: 700,
};

export const inlineAreaStyle: CSSProperties = {
  width: "100%",
  minHeight: "72px",
  padding: "var(--orbit-space-sm)",
  borderRadius: "8px",
  border: "1px solid rgba(202, 177, 137, 0.45)",
  fontFamily: "inherit",
  fontSize: "0.9375rem",
  resize: "vertical",
  background: "rgba(255,255,255,0.92)",
  color: "#5f4a2f",
};
