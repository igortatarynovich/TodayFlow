"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { useMeaningRuntime } from "@/hooks/useMeaningRuntime";
import { fetchCompactUserModelCached, clearCompactUserModelCache } from "@/lib/compactUserModelCache";
import {
  INTERPRETATION_RESONANCE_OPTIONS,
  type InterpretationResonance,
} from "@/lib/todayInterpretationConfirm";
import type { CompactUserModel } from "@/lib/types";
import styles from "./profileQuickMap.module.css";

const VERDICT_PREFIX = "todayflow.profile_atom_verdict.v1";

function readVerdicts(): Record<string, string> {
  if (typeof window === "undefined") return {};
  try {
    const raw = window.localStorage.getItem(VERDICT_PREFIX);
    if (!raw) return {};
    const parsed = JSON.parse(raw) as Record<string, string>;
    return parsed && typeof parsed === "object" ? parsed : {};
  } catch {
    return {};
  }
}

function writeVerdict(knowledgeId: string, verdict: InterpretationResonance): void {
  if (typeof window === "undefined") return;
  const next = { ...readVerdicts(), [knowledgeId]: verdict };
  try {
    window.localStorage.setItem(VERDICT_PREFIX, JSON.stringify(next));
  } catch {
    /* quota */
  }
}

function mapResonanceToCorrection(resonance: InterpretationResonance): string {
  if (resonance === "yes") return "confirm";
  if (resonance === "partial") return "partial";
  return "reject";
}

/** Profile ILR v0 — confirm or reject knowledge atoms from CUM. */
export function ProfileKnowledgeConfirmBlock() {
  const { trackMeaningEvent } = useMeaningRuntime();
  const [model, setModel] = useState<CompactUserModel | null>(null);
  const [verdicts, setVerdicts] = useState<Record<string, string>>({});

  useEffect(() => {
    setVerdicts(readVerdicts());
    void fetchCompactUserModelCached()
      .then((cum) => setModel(cum))
      .catch(() => setModel(null));
  }, []);

  const atoms = useMemo(() => {
    const rows = model?.knowledge_atoms_top_k ?? [];
    return rows
      .filter((a) => a.knowledge_id && !verdicts[a.knowledge_id!])
      .filter((a) => Boolean(a.claim_summary?.trim() || a.claim))
      .slice(0, 3);
  }, [model?.knowledge_atoms_top_k, verdicts]);

  const onVerdict = useCallback(
    (knowledgeId: string, claimSummary: string | undefined, resonance: InterpretationResonance) => {
      writeVerdict(knowledgeId, resonance);
      setVerdicts((prev) => ({ ...prev, [knowledgeId]: resonance }));
      clearCompactUserModelCache();
      trackMeaningEvent({
        event_type: "profile_atom_correction",
        event_source: "profile",
        local_date: new Date().toISOString().slice(0, 10),
        idempotency_key: `profile_atom_correction:${knowledgeId}:${resonance}`,
        payload: {
          knowledge_id: knowledgeId,
          correction: mapResonanceToCorrection(resonance),
          claim_summary: claimSummary ?? null,
          surface: "profile_quick_map",
        },
        refreshRings: false,
      });
    },
    [trackMeaningEvent],
  );

  if (atoms.length === 0) return null;

  return (
    <section
      className={styles.quickMapSection}
      data-testid="profile-knowledge-confirm"
      aria-labelledby="profile-knowledge-confirm-title"
    >
      <p className={styles.quickMapSectionLabel}>Про тебя</p>
      <h2 id="profile-knowledge-confirm-title" className={styles.quickMapSectionTitle}>
        Это похоже на правду?
      </h2>
      <div style={{ display: "flex", flexDirection: "column", gap: "0.85rem", marginTop: "0.65rem" }}>
        {atoms.map((atom) => {
          const id = atom.knowledge_id!;
          const label = atom.claim_summary?.trim() || atom.claim || id;
          return (
            <article
              key={id}
              data-testid={`profile-atom-confirm-${id}`}
              className={styles.quickMapCard}
            >
              <p style={{ margin: 0, fontSize: "0.9375rem", lineHeight: 1.5, color: "#3d3228" }}>{label}</p>
              <div
                style={{ display: "flex", flexWrap: "wrap", gap: "0.4rem", marginTop: "0.55rem" }}
                role="group"
                aria-label={`Подтверждение: ${label}`}
              >
                {INTERPRETATION_RESONANCE_OPTIONS.map((option) => (
                  <button
                    key={option.id}
                    type="button"
                    data-testid={`profile-atom-${id}-${option.id}`}
                    className={
                      option.id === "yes"
                        ? "orbit-button orbit-button-primary orbit-button-sm"
                        : "orbit-button orbit-button-secondary orbit-button-sm"
                    }
                    style={{ borderRadius: 999 }}
                    onClick={() => onVerdict(id, atom.claim_summary, option.id)}
                  >
                    {option.label}
                  </button>
                ))}
              </div>
            </article>
          );
        })}
      </div>
    </section>
  );
}
