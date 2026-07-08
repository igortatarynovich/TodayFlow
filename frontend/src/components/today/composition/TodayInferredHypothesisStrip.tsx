"use client";

import { useEffect, useMemo, useState } from "react";
import { useMeaningRuntime } from "@/hooks/useMeaningRuntime";
import { fetchCompactUserModelCached } from "@/lib/compactUserModelCache";
import { TodayInterpretationConfirm } from "@/components/today/composition/TodayInterpretationConfirm";
import type { ProximityChoiceId } from "@/lib/todayInterpretationConfirm";
import type { CompactUserModel } from "@/lib/types";
import styles from "@/components/today/composition/TodayCompositionSurface.module.css";

const DISMISS_PREFIX = "todayflow.inferred_hypothesis.dismiss.v1";

type Props = {
  dateISO: string;
  visible: boolean;
};

export function TodayInferredHypothesisStrip({ dateISO, visible }: Props) {
  const { trackMeaningEvent } = useMeaningRuntime();
  const [model, setModel] = useState<CompactUserModel | null>(null);
  const [choiceId, setChoiceId] = useState<ProximityChoiceId | null>(null);

  useEffect(() => {
    if (!visible) return;
    void fetchCompactUserModelCached({ localDate: dateISO, force: true })
      .then((cum) => setModel(cum))
      .catch(() => setModel(null));
  }, [dateISO, visible]);

  const hypothesis = useMemo(() => {
    const atoms = model?.knowledge_atoms_top_k ?? [];
    return atoms.find((a) => a.confirmation_required && a.claim_summary?.trim());
  }, [model?.knowledge_atoms_top_k]);

  const dismissed =
    typeof window !== "undefined" &&
    hypothesis?.knowledge_id &&
    window.sessionStorage.getItem(`${DISMISS_PREFIX}.${hypothesis.knowledge_id}`) &&
    !choiceId;

  if (!visible || !hypothesis?.knowledge_id || !hypothesis.claim_summary || dismissed) {
    return null;
  }

  const dismissKey = `${DISMISS_PREFIX}.${hypothesis.knowledge_id}`;

  return (
    <section className={styles.inferredHypothesis} data-testid="today-inferred-hypothesis">
      <p className={styles.inferredHypothesisEyebrow}>Мы заметили: это наблюдение, не вывод</p>
      <p className={styles.inferredHypothesisText}>{hypothesis.claim_summary}</p>
      <TodayInterpretationConfirm
        target="day_pulse"
        selectedChoiceId={choiceId}
        onSelect={(nextChoiceId, resonance) => {
          setChoiceId(nextChoiceId);
          if (typeof window !== "undefined") {
            window.sessionStorage.setItem(dismissKey, nextChoiceId);
          }
          trackMeaningEvent({
            event_type: "profile_atom_correction",
            event_source: "today",
            local_date: dateISO,
            idempotency_key: `inferred_hypothesis:${hypothesis.knowledge_id}:${nextChoiceId}`,
            payload: {
              knowledge_id: hypothesis.knowledge_id,
              correction: resonance === "yes" ? "confirm" : resonance === "partial" ? "partial" : "reject",
              claim_summary: hypothesis.claim_summary,
              proximity_choice: nextChoiceId,
              surface: "today_inferred_hypothesis",
              inferred: true,
            },
            refreshRings: false,
          });
        }}
      />
    </section>
  );
}
