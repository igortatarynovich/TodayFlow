"use client";

import { useState } from "react";
import type { BlockEcho } from "@/lib/compatibilityEcho";
import { COMPATIBILITY_ECHO_OPTIONS } from "@/lib/compatibilityEcho";
import styles from "@/components/compatibility/CompatibilityMicroEcho.module.css";

type CompatibilityMicroEchoProps = {
  label?: string;
  value?: BlockEcho;
  onSelect: (echo: BlockEcho) => void;
  compact?: boolean;
  givebackHint?: string;
};

export function CompatibilityMicroEcho({
  label = "Попадает?",
  value,
  onSelect,
  compact = false,
  givebackHint = "Запомним — учтём в следующем разборе.",
}: CompatibilityMicroEchoProps) {
  const [ack, setAck] = useState(false);

  const handleSelect = (echo: BlockEcho) => {
    onSelect(echo);
    setAck(true);
    window.setTimeout(() => setAck(false), 2400);
  };

  return (
    <div className={`${styles.root} ${compact ? styles.compact : ""}`}>
      <p className={styles.label}>{label}</p>
      <div className={styles.options}>
        {COMPATIBILITY_ECHO_OPTIONS.map((opt) => (
          <button
            key={opt.id}
            type="button"
            className={`${styles.chip} ${value === opt.id ? styles.chipActive : ""}`}
            onClick={() => handleSelect(opt.id)}
            aria-pressed={value === opt.id}
          >
            {opt.label}
          </button>
        ))}
      </div>
      {ack ? <p className={styles.giveback}>{givebackHint}</p> : null}
    </div>
  );
}
