"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { TodayInterpretationConfirm } from "@/components/today/composition/TodayInterpretationConfirm";
import type { InterpretationResonance, ProximityChoiceId } from "@/lib/todayInterpretationConfirm";
import { fetchCompactUserModelCached, clearCompactUserModelCache } from "@/lib/compactUserModelCache";
import {
  isCompatInterpretationRef,
  mapInterpretationResonance,
  pendingInterpretationInstances,
} from "@/lib/interpretationInstanceConfirm";
import { useMeaningRuntime } from "@/hooks/useMeaningRuntime";
import styles from "./profileQuickMap.module.css";

const DISMISS_PREFIX = "todayflow.profile_ilr_instance.dismiss.v1";

export function ProfileInterpretationInstanceBlock() {
  const { trackMeaningEvent } = useMeaningRuntime();
  const [verdicts, setVerdicts] = useState<Record<string, ProximityChoiceId>>({});
  const [instances, setInstances] = useState<
    ReturnType<typeof pendingInterpretationInstances>
  >([]);

  useEffect(() => {
    void fetchCompactUserModelCached()
      .then((cum) => {
        setInstances(
          pendingInterpretationInstances(
            cum?.interpretation_instances_top_k,
            (refId) => !isCompatInterpretationRef(refId),
            2,
          ),
        );
      })
      .catch(() => setInstances([]));
  }, []);

  const visible = useMemo(
    () =>
      instances.filter((row) => {
        const id = row.instance_id!;
        if (verdicts[id]) return false;
        if (typeof window !== "undefined" && window.sessionStorage.getItem(`${DISMISS_PREFIX}.${id}`)) {
          return false;
        }
        return true;
      }),
    [instances, verdicts],
  );

  const onVerdict = useCallback(
    (instanceId: string, refId: string | undefined, summary: string, choiceId: ProximityChoiceId, resonance: InterpretationResonance) => {
      setVerdicts((prev) => ({ ...prev, [instanceId]: choiceId }));
      if (typeof window !== "undefined") {
        window.sessionStorage.setItem(`${DISMISS_PREFIX}.${instanceId}`, choiceId);
      }
      clearCompactUserModelCache();
      const dayKey = new Date().toISOString().slice(0, 10);
      const correction = mapInterpretationResonance(resonance);
      trackMeaningEvent({
        event_type: "interpretation_instance_confirm",
        event_source: "profile",
        local_date: dayKey,
        idempotency_key: `interpretation_instance_confirm:${instanceId}:${resonance}:${dayKey}`,
        payload: {
          surface: "profile_quick_map",
          instance_id: instanceId,
          interpretation_ref_id: refId ?? null,
          correction,
          verdict: correction,
          summary,
        },
        refreshRings: false,
      });
    },
    [trackMeaningEvent],
  );

  if (!visible.length) return null;

  return (
    <section
      className={styles.quickMapSection}
      data-testid="profile-interpretation-instance-confirm"
      aria-labelledby="profile-interpretation-instance-title"
    >
      <p className={styles.quickMapSectionLabel}>Паттерны</p>
      <h2 id="profile-interpretation-instance-title" className={styles.quickMapSectionTitle}>
        Это откликается?
      </h2>
      <div style={{ display: "flex", flexDirection: "column", gap: "0.85rem", marginTop: "0.65rem" }}>
        {visible.map((row) => {
          const id = row.instance_id!;
          return (
            <article key={id} className={styles.quickMapCard} data-testid={`profile-ilr-${id}`}>
              <p style={{ margin: 0, fontSize: "0.72rem", fontWeight: 600, color: "#8b7355" }}>
                Наблюдение · не вывод
              </p>
              <p style={{ margin: "0.35rem 0 0", fontSize: "0.9375rem", lineHeight: 1.5, color: "#3d3228" }}>
                {row.summary}
              </p>
              <div style={{ marginTop: "0.55rem" }}>
                <TodayInterpretationConfirm
                  target="day_pulse"
                  selectedChoiceId={verdicts[id] ?? null}
                  onSelect={(choiceId, resonance) => onVerdict(id, row.interpretation_ref_id, row.summary ?? "", choiceId, resonance)}
                />
              </div>
            </article>
          );
        })}
      </div>
    </section>
  );
}
