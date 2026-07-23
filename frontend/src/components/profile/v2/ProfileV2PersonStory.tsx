"use client";

import type { ReactNode } from "react";
import type { PersonStoryChapter, PersonStoryProjection } from "@/lib/profilePage/buildProfilePersonStoryProjection";
import styles from "@/components/profile/v2/profileV2System.module.css";

export type ProfileV2PersonStoryProps = {
  story: PersonStoryProjection;
  /** When matrix absent — caller keeps legacy first-screen. */
  onOpenBirthData?: () => void;
  /** Archetype / symbol block rendered by parent above if needed */
  heroSlot?: ReactNode;
};

function ChapterBlock({ chapter }: { chapter: PersonStoryChapter }) {
  if (chapter.kind === "identity") {
    return null; // rendered in hero by parent
  }

  return (
    <section
      className={styles.zone}
      data-testid={`profile-v2-chapter-${chapter.id}`}
      aria-labelledby={`profile-v2-chapter-title-${chapter.id}`}
    >
      <header className={styles.zoneHeader}>
        <p id={`profile-v2-chapter-title-${chapter.id}`} className={styles.zoneLabel}>
          {chapter.label}
        </p>
      </header>
      {chapter.kind === "style" || chapter.kind === "helps" ? (
        <div className={styles.traitCard}>
          {chapter.lines.map((line) => (
            <p key={line} className={styles.traitLine}>
              {line}
            </p>
          ))}
        </div>
      ) : chapter.kind === "strengths" || chapter.kind === "tensions" ? (
        <ul className={styles.traitGrid}>
          {chapter.lines.map((line) => (
            <li key={line} className={styles.traitCard}>
              <p className={styles.traitLine}>{line}</p>
            </li>
          ))}
        </ul>
      ) : (
        <ul className={styles.traitGrid}>
          {chapter.lines.map((line) => (
            <li key={line} className={styles.traitCard}>
              <p className={styles.traitLine}>{line}</p>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

/**
 * Person-story body from matrix revealed_slots (header facts → natal → styles → L3).
 * Identity line is expected in the hero; this renders the remaining chapters.
 */
export function ProfileV2PersonStory({ story, onOpenBirthData }: ProfileV2PersonStoryProps) {
  const bodyChapters = story.chapters.filter((c) => c.kind !== "identity");
  const dataMessages = story.userMessages.filter((m) => m.code !== "l3_gated");
  const l3Message = story.userMessages.find((m) => m.code === "l3_gated") ?? null;

  return (
    <div data-testid="profile-v2-person-story">
      {dataMessages.length ? (
        <section
          className={styles.zone}
          data-testid="profile-v2-capability-ctas"
          aria-label="Что откроет следующий шаг"
        >
          <ul className={styles.traitGrid}>
            {dataMessages.map((msg) => (
              <li key={msg.code || msg.text} className={styles.traitCard}>
                <p className={styles.traitLine}>{msg.text}</p>
                {onOpenBirthData ? (
                  <button type="button" className={styles.secondaryCta} onClick={onOpenBirthData}>
                    Данные рождения
                  </button>
                ) : null}
              </li>
            ))}
          </ul>
        </section>
      ) : null}

      {bodyChapters.map((chapter) => (
        <ChapterBlock key={chapter.id} chapter={chapter} />
      ))}

      {story.accessGatedHelps && l3Message && !story.helpsLine ? (
        <section className={styles.zone} data-testid="profile-v2-helps-gated">
          <p className={styles.zoneLabel}>Что помогает</p>
          <div className={styles.traitCard}>
            <p className={styles.traitLine}>{l3Message.text}</p>
          </div>
        </section>
      ) : null}
    </div>
  );
}
