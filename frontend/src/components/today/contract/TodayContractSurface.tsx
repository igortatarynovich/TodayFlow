"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { PageShell, ProgressLine, SceneStack } from "@/components/foundation/TodayFlowScene";
import { PrimaryAction } from "@/components/today/contract/PrimaryAction";
import { TodayNarrativeView } from "@/components/today/contract/TodayNarrativeView";
import { TODAY_CONTRACT_COPY } from "@/components/today/contract/todayContractCopy";
import { RITUAL_COPY } from "@/components/today/todayRitualCopy";
import { buildTodayNarrativeV1 } from "@/lib/todayNarrativeFromContract";
import type { TodayContractV1 } from "@/lib/todayContract";

type Props = {
  contract: TodayContractV1;
  displayDate: string;
  streakDays?: number;
  actionDoneInitial?: boolean;
  onActionComplete?: () => void;
  onVisible?: () => void;
  eveningMode?: boolean;
  eveningReflectionInput?: string;
  eveningSaving?: boolean;
  eveningDone?: boolean;
  onEveningReflectionChange?: (value: string) => void;
  onSaveEvening?: () => void;
};

export function TodayContractSurface({
  contract,
  displayDate,
  streakDays = 0,
  actionDoneInitial = false,
  onActionComplete,
  onVisible,
  eveningMode = false,
  eveningReflectionInput = "",
  eveningSaving = false,
  eveningDone = false,
  onEveningReflectionChange,
  onSaveEvening,
}: Props) {
  const [actionDone, setActionDone] = useState(actionDoneInitial);
  const narrative = useMemo(() => buildTodayNarrativeV1(contract), [contract]);

  useEffect(() => {
    setActionDone(actionDoneInitial);
  }, [actionDoneInitial]);

  useEffect(() => {
    onVisible?.();
  }, [onVisible]);

  const onMarkDone = useCallback(() => {
    if (actionDone) return;
    setActionDone(true);
    onActionComplete?.();
  }, [actionDone, onActionComplete]);

  const progressPrimary = useMemo(() => {
    if (eveningMode && (actionDone || eveningDone)) {
      return RITUAL_COPY.todayExperienceEveningProgressDone;
    }
    if (actionDone || eveningDone) {
      return streakDays > 0
        ? `День отмечен · серия ${streakDays}`
        : RITUAL_COPY.todayExperienceActionDoneCta;
    }
    return streakDays > 0 ? `Серия ${streakDays} · шаг дня ещё открыт` : "Отметь главный шаг, когда сделаешь";
  }, [actionDone, eveningDone, eveningMode, streakDays]);

  return (
    <PageShell>
      <SceneStack>
        <p className="todayflow-eyebrow" style={{ margin: "0 0 0.5rem" }}>
          {RITUAL_COPY.todayExperienceDayEyebrow} · {displayDate}
        </p>

        <TodayNarrativeView narrative={narrative} />

        {eveningMode && onSaveEvening && onEveningReflectionChange ? (
          <section
            className="todayflow-surface-soft todayflow-inset"
            style={{ marginTop: "0.85rem", padding: "1rem", borderRadius: 16 }}
          >
            <p className="todayflow-eyebrow" style={{ margin: 0 }}>{RITUAL_COPY.todayExperienceEveningEyebrow}</p>
            <p className="orbit-body-sm" style={{ margin: "0.35rem 0 0.65rem", fontWeight: 600 }}>
              {RITUAL_COPY.todayExperienceEveningQuestion}
            </p>
            <textarea
              className="orbit-input"
              value={eveningReflectionInput}
              onChange={(e) => onEveningReflectionChange(e.target.value)}
              placeholder={RITUAL_COPY.todayExperienceEveningPlaceholder}
              aria-label={RITUAL_COPY.todayExperienceEveningQuestion}
              rows={3}
              style={{ width: "100%", marginBottom: "0.65rem" }}
            />
            <button
              type="button"
              className="orbit-button orbit-button-primary"
              onClick={onSaveEvening}
              disabled={eveningSaving}
            >
              {eveningSaving ? RITUAL_COPY.todayExperienceEveningSavingCta : RITUAL_COPY.todayExperienceEveningCta}
            </button>
          </section>
        ) : (
          <PrimaryAction
            action={narrative.primaryAction}
            done={actionDone}
            onMarkDone={onMarkDone}
          />
        )}

        <ProgressLine
          active={actionDone || eveningDone}
          primary={progressPrimary}
          secondary={TODAY_CONTRACT_COPY.narrativeMainEyebrow}
        />
      </SceneStack>
    </PageShell>
  );
}
