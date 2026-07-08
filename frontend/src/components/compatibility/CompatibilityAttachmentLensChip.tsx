"use client";

import { useCallback, useEffect, useState } from "react";
import { TodayInterpretationConfirm } from "@/components/today/composition/TodayInterpretationConfirm";
import type { InterpretationResonance, ProximityChoiceId } from "@/lib/todayInterpretationConfirm";
import {
  attachmentLensKnowledgeId,
  type AttachmentReference,
  primaryAttachmentHint,
} from "@/lib/compatibilityAttachmentReference";
import { useMeaningRuntime } from "@/hooks/useMeaningRuntime";
import styles from "@/components/compatibility/CompatibilityExplorationResult.module.css";

const DISMISS_PREFIX = "todayflow.compat_attachment_lens.dismiss.v1";

type Props = {
  attachmentReference?: AttachmentReference | null;
  surface: string;
  scenarioId?: string | null;
};

function mapResonance(resonance: InterpretationResonance): "confirm" | "partial" | "reject" {
  if (resonance === "yes") return "confirm";
  if (resonance === "partial") return "partial";
  return "reject";
}

export function CompatibilityAttachmentLensChip({ attachmentReference, surface, scenarioId }: Props) {
  const { trackMeaningEvent } = useMeaningRuntime();
  const hint = primaryAttachmentHint(attachmentReference);
  const [choiceId, setChoiceId] = useState<ProximityChoiceId | null>(null);
  const [dismissed, setDismissed] = useState(false);

  const knowledgeId = hint ? attachmentLensKnowledgeId(hint.code) : null;
  const dismissKey = knowledgeId ? `${DISMISS_PREFIX}.${knowledgeId}` : null;

  useEffect(() => {
    if (!dismissKey || typeof window === "undefined") return;
    if (window.sessionStorage.getItem(dismissKey)) {
      setDismissed(true);
    }
  }, [dismissKey]);

  const onSelect = useCallback(
    (_choiceId: ProximityChoiceId, value: InterpretationResonance) => {
      if (!hint || !knowledgeId) return;
      setChoiceId(_choiceId);
      setDismissed(true);
      if (dismissKey && typeof window !== "undefined") {
        window.sessionStorage.setItem(dismissKey, value);
      }
      const dayKey = new Date().toISOString().slice(0, 10);
      const correction = mapResonance(value);
      trackMeaningEvent({
        event_type: "compatibility_attachment_confirm",
        event_source: "compatibility",
        local_date: dayKey,
        idempotency_key: `compat_attachment_confirm:${hint.code}:${value}:${dayKey}`,
        payload: {
          surface,
          scenario_id: scenarioId ?? null,
          attachment_style_code: hint.code,
          label: hint.label,
          summary: hint.summary,
          echo: value,
          verdict: correction,
          evidence_blocks: hint.evidence_blocks ?? [],
          knowledge_id: knowledgeId,
          reference_status: attachmentReference?.reference_status ?? "draft",
        },
        refreshRings: false,
      });
      trackMeaningEvent({
        event_type: "profile_atom_correction",
        event_source: "compatibility",
        local_date: dayKey,
        idempotency_key: `profile_atom_correction:${knowledgeId}:${value}`,
        payload: {
          knowledge_id: knowledgeId,
          correction,
          claim_summary: hint.summary,
          surface,
          attachment_style_code: hint.code,
        },
        refreshRings: false,
      });
    },
    [attachmentReference?.reference_status, dismissKey, hint, knowledgeId, scenarioId, surface, trackMeaningEvent],
  );

  if (!hint || !knowledgeId) return null;
  if (dismissed) return null;

  return (
    <section className={styles.attachmentLens} data-testid="compatibility-attachment-lens">
      <p className={styles.attachmentLensEyebrow}>Возможный паттерн · не диагноз</p>
      <p className={styles.attachmentLensTitle}>{hint.label}</p>
      <p className={styles.attachmentLensSummary}>{hint.summary}</p>
      <TodayInterpretationConfirm target="day_pulse" selectedChoiceId={choiceId} onSelect={onSelect} />
    </section>
  );
}
