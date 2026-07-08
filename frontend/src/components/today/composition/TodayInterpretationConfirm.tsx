"use client";

import {
  interpretationProximityQuestion,
  proximityOptionsForTarget,
  type InterpretationConfirmTarget,
  type InterpretationResonance,
  type ProximityChoiceId,
} from "@/lib/todayInterpretationConfirm";
import styles from "@/components/today/composition/TodayCompositionSurface.module.css";

type Props = {
  target: InterpretationConfirmTarget;
  selectedChoiceId: ProximityChoiceId | null;
  disabled?: boolean;
  onSelect: (choiceId: ProximityChoiceId, resonance: InterpretationResonance) => void;
};

export function TodayInterpretationConfirm({ target, selectedChoiceId, disabled = false, onSelect }: Props) {
  const question = interpretationProximityQuestion(target);
  const options = proximityOptionsForTarget(target);

  return (
    <div className={styles.interpretationConfirm} data-testid={`today-interpretation-confirm-${target}`}>
      <p className={styles.interpretationConfirmQuestion}>{question}</p>
      <div className={styles.interpretationConfirmChips} role="group" aria-label={question}>
        {options.map((option) => {
          const active = selectedChoiceId === option.choiceId;
          return (
            <button
              key={option.choiceId}
              type="button"
              data-testid={`interpretation-confirm-${target}-${option.choiceId}`}
              className={
                active
                  ? `orbit-button orbit-button-primary ${styles.interpretationConfirmChip}`
                  : `orbit-button orbit-button-secondary ${styles.interpretationConfirmChip}`
              }
              disabled={disabled}
              onClick={() => onSelect(option.choiceId, option.resonance)}
            >
              {option.label}
            </button>
          );
        })}
      </div>
    </div>
  );
}
