"use client";

import type { DomainLensV1, TodayContractDomainId } from "@/lib/todayContract";
import { TODAY_CONTRACT_COPY } from "@/components/today/contract/todayContractCopy";

const DOMAIN_TITLE: Record<TodayContractDomainId, string> = {
  work: TODAY_CONTRACT_COPY.domainWork,
  money: TODAY_CONTRACT_COPY.domainMoney,
  relationships: TODAY_CONTRACT_COPY.domainRelationships,
  energy: TODAY_CONTRACT_COPY.domainEnergy,
};

type SlotKey = keyof DomainLensV1;

function slotLabel(slot: SlotKey): string {
  if (slot === "status") return TODAY_CONTRACT_COPY.slotStatus;
  if (slot === "opportunity") return TODAY_CONTRACT_COPY.slotOpportunity;
  if (slot === "risk") return TODAY_CONTRACT_COPY.slotRisk;
  return TODAY_CONTRACT_COPY.slotAction;
}

const SLOT_ORDER: SlotKey[] = ["status", "opportunity", "risk", "action"];

type Props = {
  domain: TodayContractDomainId;
  lens: DomainLensV1;
};

export function TodayDomainLens({ domain, lens }: Props) {
  return (
    <article
      className="todayflow-surface-soft"
      data-testid={`today-domain-lens-${domain}`}
      style={{
        padding: "1rem",
        borderRadius: 16,
        border: "1px solid rgba(201,168,115,0.22)",
        background: "rgba(255,255,255,0.88)",
      }}
    >
      <h2 className="orbit-heading-3" style={{ margin: "0 0 0.65rem", color: "#1f1a16" }}>
        {DOMAIN_TITLE[domain]}
      </h2>
      <div style={{ display: "flex", flexDirection: "column", gap: "0.55rem" }}>
        {SLOT_ORDER.map((slot) => (
          <div key={slot}>
            <p className="orbit-body-xs" style={{ margin: 0, fontWeight: 700, color: "#8a6a42" }}>
              {slotLabel(slot)}
            </p>
            <p className="orbit-body-sm" style={{ margin: "0.2rem 0 0", lineHeight: 1.5, color: "#2d241c" }}>
              {lens[slot]}
            </p>
          </div>
        ))}
      </div>
    </article>
  );
}
