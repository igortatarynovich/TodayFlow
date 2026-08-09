"use client";

import {
  TODAY_DAY_DIALOGUE_COPY,
  TODAY_FOCUS_PRIORITY_CARDS,
  TODAY_MORNING_MOODS,
  shouldAskMorningFocus,
  shouldAskMorningMood,
} from "@/lib/todayDayDialogue";
import { FOCUS_DEEPEN_CTA_LABEL } from "@/lib/todayFocusDeepen";
import styles from "@/components/today/composition/TodayCompositionSurface.module.css";

type Props = {
  dateISO: string;
  morningMoodId: string | null;
  morningMoodCapturedAtMs?: number | null;
  focusTopicId: string | null;
  focusTopicCapturedAtMs?: number | null;
  onSelectMood: (id: string) => void;
  onSelectFocus: (id: string) => void;
  /** Handoff CTA → Reading / depth_layer (no new screen). */
  showDeepenCta?: boolean;
  onDeepenTopic?: () => void;
};

/**
 * Morning dialogue: focus first (day lens), mood second (writes mood_selected / PIM).
 * Priority = 6 two-line cards (handoff). Mood demoted below.
 */
export function TodayDayDialogueMorning({
  dateISO,
  morningMoodId,
  morningMoodCapturedAtMs,
  focusTopicId,
  focusTopicCapturedAtMs,
  onSelectMood,
  onSelectFocus,
  showDeepenCta = false,
  onDeepenTopic,
}: Props) {
  const askFocus = shouldAskMorningFocus({ dateISO, focusTopicId, focusTopicCapturedAtMs });
  const askMood = shouldAskMorningMood({ dateISO, morningMoodId, morningMoodCapturedAtMs });
  const deepenOnly = !askFocus && !askMood && showDeepenCta && Boolean(onDeepenTopic);
  if (!askFocus && !askMood && !deepenOnly) return null;

  return (
    <section className={styles.dialogueCard} data-testid="today-zone-dialogue-morning">
      {askFocus ? (
        <div className={styles.dialogueBlock}>
          <h2 className={styles.dialogueTitle}>{TODAY_DAY_DIALOGUE_COPY.focusTitle}</h2>
          <div className={styles.priorityCardGrid} role="group" aria-label="Главный фокус">
            {TODAY_FOCUS_PRIORITY_CARDS.map((t) => (
              <button
                key={t.id}
                type="button"
                className={
                  focusTopicId === t.id
                    ? `${styles.priorityCard} ${styles.priorityCardActive}`
                    : styles.priorityCard
                }
                data-testid={`today-focus-${t.id}`}
                data-selected={focusTopicId === t.id ? "true" : "false"}
                onClick={() => onSelectFocus(t.id)}
              >
                <span className={styles.priorityCardLabel}>{t.label}</span>
                <span className={styles.priorityCardSub}>{t.sub}</span>
              </button>
            ))}
          </div>
        </div>
      ) : null}
      {askMood ? (
        <div className={styles.dialogueBlock} data-testid="today-dialogue-mood">
          <h2 className={styles.dialogueTitle}>{TODAY_DAY_DIALOGUE_COPY.moodTitle}</h2>
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
      {deepenOnly ? (
        <div className={styles.dialogueBlock}>
          <button
            type="button"
            className={styles.deepenTopicLink}
            data-testid="today-focus-deepen-cta"
            onClick={onDeepenTopic}
          >
            {FOCUS_DEEPEN_CTA_LABEL}
          </button>
        </div>
      ) : null}
    </section>
  );
}
