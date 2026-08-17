"use client";

import {
  interpretationProximityQuestion,
  proximityOptionsForTarget,
  type InterpretationConfirmTarget,
  type InterpretationResonance,
  type ProximityChoiceId,
} from "@/lib/todayInterpretationConfirm";
import { DsButton } from "@/design-system";
import styles from "@/design-system/compositions/dsCompositionSurface.module.css";

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
            <DsButton
              key={option.choiceId}
              type="button"
              variant={active ? "primary" : "secondary"}
              size="sm"
              className={styles.interpretationConfirmChip}
              data-testid={`interpretation-confirm-${target}-${option.choiceId}`}
              disabled={disabled}
              onClick={() => onSelect(option.choiceId, option.resonance)}
            >
              {option.label}
            </DsButton>
          );
        })}
      </div>
    </div>
  );
}
