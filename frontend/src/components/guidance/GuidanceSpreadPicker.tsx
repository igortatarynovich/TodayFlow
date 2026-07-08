"use client";

import type { GuidanceSpreadCatalogEntry, GuidanceSpreadSection } from "@/lib/guidance/catalog";

type Props = {
  spreadsBySection: Map<string, GuidanceSpreadCatalogEntry[]>;
  selectedId: string;
  onSelectedIdChange: (entry: GuidanceSpreadCatalogEntry) => void;
  disabled?: boolean;
  sectionLabels: Record<GuidanceSpreadSection, string>;
  spreadSelectLabel: string;
};

const SECTION_ORDER = ["quick", "medium", "deep"] as const;

export function GuidanceSpreadPicker({
  spreadsBySection,
  selectedId,
  onSelectedIdChange,
  disabled = false,
  sectionLabels,
  spreadSelectLabel,
}: Props) {
  const flat = SECTION_ORDER.flatMap((section) => spreadsBySection.get(section) ?? []);
  const active = flat.find((e) => e.id === selectedId) ?? flat[0];

  return (
    <div className="todayflow-stack" style={{ gap: "0.65rem", width: "100%", maxWidth: "100%" }}>
      <label htmlFor="guidance-spread-select" className="guidance-field-label">
        {spreadSelectLabel}
      </label>
      <select
        id="guidance-spread-select"
        className="guidance-select"
        disabled={disabled}
        value={selectedId}
        onChange={(e) => {
          const entry = flat.find((item) => item.id === e.target.value);
          if (entry) onSelectedIdChange(entry);
        }}
      >
        {SECTION_ORDER.map((section) => (
          <optgroup key={section} label={sectionLabels[section]}>
            {(spreadsBySection.get(section) ?? []).map((entry) => (
              <option key={entry.id} value={entry.id}>
                {entry.title}
              </option>
            ))}
          </optgroup>
        ))}
      </select>

      {active ? (
        <div
          className="todayflow-inset-tight"
          style={{
            borderRadius: "var(--orbit-radius-md)",
            border: "1px solid var(--orbit-color-border)",
            background: "var(--orbit-color-mist)",
            padding: "0.85rem 1rem",
          }}
        >
          <p className="orbit-body-sm" style={{ margin: 0, color: "var(--orbit-color-slate)", lineHeight: 1.62 }}>
            {active.description}
          </p>
          <ul className="orbit-body-xs" style={{ margin: "0.55rem 0 0", paddingLeft: "1.1rem", color: "var(--orbit-color-muted)", lineHeight: 1.55 }}>
            {active.fitsFor.slice(0, 5).map((line) => (
              <li key={line} style={{ marginBottom: "0.2rem" }}>
                {line}
              </li>
            ))}
          </ul>
        </div>
      ) : null}
    </div>
  );
}
