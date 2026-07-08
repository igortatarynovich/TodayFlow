"use client";

import { TODAY_CONTRACT_COPY } from "@/components/today/contract/todayContractCopy";

type Props = {
  period: string;
  eyebrow?: string;
};

export function PeriodBlock({ period, eyebrow = TODAY_CONTRACT_COPY.periodEyebrow }: Props) {
  return (
    <header
      className="todayflow-surface-primary todayflow-inset"
      data-testid="today-contract-period"
      style={{
        padding: "1.1rem 1rem",
        borderRadius: 18,
        border: "1px solid rgba(201,168,115,0.28)",
        background: "rgba(255,255,255,0.92)",
      }}
    >
      <p className="todayflow-eyebrow" style={{ margin: 0 }}>{eyebrow}</p>
      <h1 className="orbit-heading-2" style={{ margin: "0.35rem 0 0", lineHeight: 1.35, color: "#1f1a16" }}>
        {period}
      </h1>
    </header>
  );
}
