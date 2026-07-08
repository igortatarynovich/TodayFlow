"use client";

import type { TodaySkyCard } from "@/lib/todayDaySpine";
import styles from "@/components/today/composition/TodayCompositionSurface.module.css";

type Props = {
  cards: TodaySkyCard[];
  testId?: string;
};

export function TodaySkyStoryCards({ cards, testId = "today-zone-sky-cards" }: Props) {
  if (cards.length === 0) return null;

  return (
    <div className={styles.skyCardGrid} data-testid={testId}>
      {cards.map((card) => (
        <article key={card.id} className={styles.skyCard} data-testid={`today-sky-${card.id}`}>
          <span className={styles.skyCardEmoji} aria-hidden>
            {card.emoji}
          </span>
          <p className={styles.skyCardLabel}>{card.label}</p>
          <p className={styles.skyCardTitle}>{card.title}</p>
          <p className={styles.skyCardStory}>{card.story}</p>
        </article>
      ))}
    </div>
  );
}
