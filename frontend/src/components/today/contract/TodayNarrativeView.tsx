"use client";

import type { TodayNarrativeV1 } from "@/lib/todayNarrativeFromContract";
import { TODAY_CONTRACT_COPY } from "@/components/today/contract/todayContractCopy";

type Props = {
  narrative: TodayNarrativeV1;
};

export function TodayNarrativeView({ narrative }: Props) {
  return (
    <div data-testid="today-narrative-view" style={{ display: "flex", flexDirection: "column", gap: "0.85rem" }}>
      <section
        className="todayflow-surface-primary todayflow-inset"
        data-testid="today-narrative-main-thought"
        style={{
          padding: "1.15rem 1rem",
          borderRadius: 18,
          border: "1px solid rgba(201,168,115,0.28)",
          background: "rgba(255,255,255,0.94)",
        }}
      >
        <p className="todayflow-eyebrow" style={{ margin: 0 }}>{TODAY_CONTRACT_COPY.narrativeMainEyebrow}</p>
        <h1 className="orbit-heading-2" style={{ margin: "0.35rem 0 0", lineHeight: 1.35, color: "#1f1a16" }}>
          {narrative.mainThought.headline}
        </h1>
        {narrative.mainThought.subline ? (
          <p className="orbit-body" style={{ margin: "0.5rem 0 0", lineHeight: 1.55, color: "#3d3228" }}>
            {narrative.mainThought.subline}
          </p>
        ) : null}
        <p
          className="orbit-body-sm"
          data-testid="today-narrative-growth"
          style={{ margin: "0.65rem 0 0", lineHeight: 1.55, color: "#5a4a38" }}
        >
          {narrative.growthPoint}
        </p>
      </section>

      {narrative.manifestations.length > 0 ? (
        <section
          className="todayflow-surface-soft todayflow-inset"
          data-testid="today-narrative-manifestations"
          style={{
            padding: "1rem",
            borderRadius: 16,
            border: "1px solid rgba(201,168,115,0.2)",
            background: "rgba(255,250,245,0.92)",
          }}
        >
          <p className="todayflow-eyebrow" style={{ margin: "0 0 0.55rem" }}>
            {TODAY_CONTRACT_COPY.narrativeManifestationsEyebrow}
          </p>
          <ul style={{ margin: 0, padding: 0, listStyle: "none", display: "flex", flexDirection: "column", gap: "0.55rem" }}>
            {narrative.manifestations.map((item) => (
              <li key={item.domainId} data-testid={`today-narrative-manifestation-${item.domainId}`}>
                <p className="orbit-body-sm" style={{ margin: 0, lineHeight: 1.55, color: "#2d241c" }}>
                  {item.line}
                </p>
              </li>
            ))}
          </ul>
        </section>
      ) : null}

      {narrative.caution ? (
        <p
          className="orbit-body-xs"
          data-testid="today-narrative-caution"
          style={{ margin: 0, lineHeight: 1.5, color: "#7a5c40", padding: "0 0.15rem" }}
        >
          {narrative.caution}
        </p>
      ) : null}
    </div>
  );
}
