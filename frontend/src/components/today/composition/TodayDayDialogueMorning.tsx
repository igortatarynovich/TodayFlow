"use client";

import {
  TODAY_DAY_DIALOGUE_COPY,
  TODAY_FOCUS_TOPICS,
  TODAY_MORNING_MOODS,
  shouldAskMorningDialogue,
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

export function TodayDayDialogueMorning({
  dateISO,
  morningMoodId,
  morningMoodCapturedAtMs,
  focusTopicId,
  focusTopicCapturedAtMs,
  onSelectMood,
  onSelectFocus,
}: Props) {
  if (
    !shouldAskMorningDialogue({
      dateISO,
      morningMoodId,
      morningMoodCapturedAtMs,
      focusTopicId,
      focusTopicCapturedAtMs,
    })
  ) {
    return null;
  }

  const askMood = shouldAskMorningMood({ dateISO, morningMoodId, morningMoodCapturedAtMs });
  const askFocus =
    !askMood && shouldAskMorningFocus({ dateISO, focusTopicId, focusTopicCapturedAtMs });

  return (
    <section className={styles.dialogueCard} data-testid="today-zone-dialogue-morning">
      {askMood ? (
        <div className={styles.dialogueBlock}>
          <h2 className={styles.dialogueTitle}>{TODAY_DAY_DIALOGUE_COPY.moodTitle}</h2>
          <p className={styles.dialogueLead}>{TODAY_DAY_DIALOGUE_COPY.moodLead}</p>
          <div className={styles.moodGrid} role="group" aria-label="Состояние сейчас">
            {TODAY_MORNING_MOODS.map((m) => (
              <button
                key={m.id}
                type="button"
                className={styles.moodChip}
                data-testid={`today-mood-${m.id}`}
                onClick={() => onSelectMood(m.id)}
              >
                <span className={styles.moodIcon} aria-hidden>
                  {m.icon}
                </span>
                <span>{m.label}</span>
              </button>
            ))}
          </div>
        </div>
      ) : null}

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
    </section>
  );
}
