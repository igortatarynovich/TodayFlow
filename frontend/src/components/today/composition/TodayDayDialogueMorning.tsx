"use client";

import {
  TODAY_DAY_DIALOGUE_COPY,
  TODAY_FOCUS_TOPICS,
  TODAY_MORNING_MOODS,
  shouldAskMorningFocus,
  shouldAskMorningMood,
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
 * Morning dialogue: focus first (day lens), mood second (writes mood_selected / PIM).
 * Mood is demoted — never competes with pulse / card / number for first viewport attention.
 */
export function TodayDayDialogueMorning({
  dateISO,
  morningMoodId,
  morningMoodCapturedAtMs,
  focusTopicId,
  focusTopicCapturedAtMs,
  onSelectMood,
  onSelectFocus,
}: Props) {
  const askFocus = shouldAskMorningFocus({ dateISO, focusTopicId, focusTopicCapturedAtMs });
  const askMood = shouldAskMorningMood({ dateISO, morningMoodId, morningMoodCapturedAtMs });
  if (!askFocus && !askMood) return null;

  return (
    <section className={styles.dialogueCard} data-testid="today-zone-dialogue-morning">
      {askFocus ? (
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
      ) : null}
      {askMood ? (
        <div className={styles.dialogueBlock} data-testid="today-dialogue-mood">
          <h2 className={styles.dialogueTitle}>{TODAY_DAY_DIALOGUE_COPY.moodTitle}</h2>
          <p className={styles.dialogueLead}>{TODAY_DAY_DIALOGUE_COPY.moodLead}</p>
          <div className={styles.focusGrid} role="group" aria-label="Настроение">
            {TODAY_MORNING_MOODS.map((m) => (
              <button
                key={m.id}
                type="button"
                className={styles.focusChip}
                data-testid={`today-mood-${m.id}`}
                onClick={() => onSelectMood(m.id)}
              >
                {m.label}
              </button>
            ))}
          </div>
        </div>
      ) : null}
    </section>
  );
}
