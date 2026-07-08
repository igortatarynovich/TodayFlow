"use client";

import { TODAY_CONTRACT_COPY } from "@/components/today/contract/todayContractCopy";

type Props = {
  developmentPoint: string;
};

export function GrowthBlock({ developmentPoint }: Props) {
  return (
    <section
      className="todayflow-surface-soft todayflow-inset"
      data-testid="today-contract-growth"
      style={{
        marginTop: "0.85rem",
        padding: "1rem",
        borderRadius: 16,
        border: "1px solid rgba(201,168,115,0.2)",
        background: "rgba(255,250,245,0.9)",
      }}
    >
      <p className="todayflow-eyebrow" style={{ margin: 0 }}>{TODAY_CONTRACT_COPY.growthEyebrow}</p>
      <p className="orbit-body" style={{ margin: "0.4rem 0 0", lineHeight: 1.55, color: "#2d241c" }}>
        {developmentPoint}
      </p>
    </section>
  );
}
