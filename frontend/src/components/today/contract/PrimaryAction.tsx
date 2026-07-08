"use client";

import { TODAY_CONTRACT_COPY } from "@/components/today/contract/todayContractCopy";

type Props = {
  action: string;
  done?: boolean;
  disabled?: boolean;
  onMarkDone?: () => void;
};

export function PrimaryAction({ action, done = false, disabled = false, onMarkDone }: Props) {
  return (
    <section
      className="todayflow-surface-primary todayflow-inset"
      data-testid="today-contract-primary-action"
      style={{
        marginTop: "0.85rem",
        padding: "1rem",
        borderRadius: 16,
        border: "1px solid rgba(214,142,122,0.35)",
        background: "linear-gradient(180deg, rgba(255,252,248,0.98) 0%, rgba(252,236,220,0.55) 100%)",
      }}
    >
      <p className="todayflow-eyebrow" style={{ margin: 0 }}>{TODAY_CONTRACT_COPY.primaryActionEyebrow}</p>
      <p className="orbit-body" style={{ margin: "0.45rem 0 0", fontWeight: 600, lineHeight: 1.5, color: "#1f1a16" }}>
        {action}
      </p>
      {onMarkDone ? (
        <button
          type="button"
          className="orbit-button orbit-button-primary"
          style={{ marginTop: "0.75rem" }}
          disabled={disabled || done}
          onClick={onMarkDone}
        >
          {done ? "Шаг отмечен" : "Сделал этот шаг"}
        </button>
      ) : null}
    </section>
  );
}
