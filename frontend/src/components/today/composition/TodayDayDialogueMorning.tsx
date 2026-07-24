"use client";

import {
  TODAY_DAY_DIALOGUE_COPY,
  TODAY_FOCUS_TOPICS,
  shouldAskMorningFocus,
} from "@/lib/todayDayDialogue";
import styles from "@/components/today/composition/TodayCompositionSurface.module.css";

type Props = {
  dateISO: string;
  morningMoodId: string | null;
  morningMoodCapturedAtMs?: number | null;
  focusTopicId: string | null;
  focusTopicCapturedAtMs?: number | null;
  onSelectMood: (id: string) => void;
  onSelectFocus: (id: string) => void;
};

/**
 * R18: mood chips removed — state is inferred, not polled.
 * Focus topic remains as a soft discovery ask (not a mood scale).
 */
export function TodayDayDialogueMorning({
  dateISO,
  focusTopicId,
  focusTopicCapturedAtMs,
  onSelectFocus,
}: Props) {
  const askFocus = shouldAskMorningFocus({ dateISO, focusTopicId, focusTopicCapturedAtMs });
  if (!askFocus) return null;

  return (
    <section className={styles.dialogueCard} data-testid="today-zone-dialogue-morning">
      <div className={styles.dialogueBlock}>
        <h2 className={styles.dialogueTitle}>{TODAY_DAY_DIALOGUE_COPY.focusTitle}</h2>
        <p className={styles.dialogueLead}>{TODAY_DAY_DIALOGUE_COPY.focusLead}</p>
        <div className={styles.focusGrid} role="group" aria-label="Главный фокус">
          {TODAY_FOCUS_TOPICS.map((t) => (
            <button
              key={t.id}
              type="button"
              className={styles.focusChip}
              data-testid={`today-focus-${t.id}`}
              onClick={() => onSelectFocus(t.id)}
            >
              {t.label}
            </button>
          ))}
        </div>
      </div>
    </section>
  );
}
