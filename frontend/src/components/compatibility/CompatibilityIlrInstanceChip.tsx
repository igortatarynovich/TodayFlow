"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { TodayInterpretationConfirm } from "@/components/today/composition/TodayInterpretationConfirm";
import type { InterpretationResonance, ProximityChoiceId } from "@/lib/todayInterpretationConfirm";
import { fetchCompactUserModelCached, clearCompactUserModelCache } from "@/lib/compactUserModelCache";
import type { CompactUserModel } from "@/lib/types";
import { useAuth } from "@/lib/useAuth";
import { useMeaningRuntime } from "@/hooks/useMeaningRuntime";
import styles from "@/components/compatibility/CompatibilityExplorationResult.module.css";

const DISMISS_PREFIX = "todayflow.compat_ilr_instance.dismiss.v1";

type Props = {
  surface: string;
  scenarioId?: string | null;
};

import {
  isCompatInterpretationRef,
  mapInterpretationResonance,
  pendingInterpretationInstances,
} from "@/lib/interpretationInstanceConfirm";

export function CompatibilityIlrInstanceChip({ surface, scenarioId }: Props) {
  const { isAuthenticated } = useAuth();
  const { trackMeaningEvent } = useMeaningRuntime();
  const [model, setModel] = useState<CompactUserModel | null>(null);
  const [choiceId, setChoiceId] = useState<ProximityChoiceId | null>(null);
  const [dismissed, setDismissed] = useState(false);

  useEffect(() => {
    if (!isAuthenticated) {
      setModel(null);
      return;
    }
    void fetchCompactUserModelCached()
      .then((cum) => setModel(cum))
      .catch(() => setModel(null));
  }, [isAuthenticated]);

  const instance = useMemo(() => {
    const rows = pendingInterpretationInstances(
      model?.interpretation_instances_top_k,
      (refId) => isCompatInterpretationRef(refId),
      1,
    );
    return rows[0];
  }, [model?.interpretation_instances_top_k]);

  const dismissKey = instance?.instance_id ? `${DISMISS_PREFIX}.${instance.instance_id}` : null;

  useEffect(() => {
    if (!dismissKey || typeof window === "undefined") return;
    if (window.sessionStorage.getItem(dismissKey)) {
      setDismissed(true);
    }
  }, [dismissKey]);

  const onSelect = useCallback(
    (_choiceId: ProximityChoiceId, value: InterpretationResonance) => {
      if (!instance?.instance_id) return;
      setChoiceId(_choiceId);
      setDismissed(true);
      if (dismissKey && typeof window !== "undefined") {
        window.sessionStorage.setItem(dismissKey, value);
      }
      const dayKey = new Date().toISOString().slice(0, 10);
      const correction = mapInterpretationResonance(value);
      clearCompactUserModelCache();
      trackMeaningEvent({
        event_type: "interpretation_instance_confirm",
        event_source: "compatibility",
        local_date: dayKey,
        idempotency_key: `interpretation_instance_confirm:${instance.instance_id}:${value}:${dayKey}`,
        payload: {
          surface,
          scenario_id: scenarioId ?? null,
          instance_id: instance.instance_id,
          interpretation_ref_id: instance.interpretation_ref_id ?? null,
          correction,
          verdict: correction,
          summary: instance.summary ?? null,
        },
        refreshRings: false,
      });
    },
    [dismissKey, instance, scenarioId, surface, trackMeaningEvent],
  );

  if (!isAuthenticated || !instance?.instance_id || dismissed) return null;

  return (
    <section className={styles.attachmentLens} data-testid="compatibility-ilr-instance">
      <p className={styles.attachmentLensEyebrow}>Паттерн из твоих откликов · не вывод</p>
      <p className={styles.attachmentLensSummary}>{instance.summary}</p>
      <TodayInterpretationConfirm target="day_pulse" selectedChoiceId={choiceId} onSelect={onSelect} />
    </section>
  );
}
