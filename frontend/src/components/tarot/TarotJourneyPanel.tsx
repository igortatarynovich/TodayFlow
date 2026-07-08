"use client";

import Link from "next/link";
import { buildTarotJourneySummary } from "@/lib/buildTarotJourneySummary";
import { readTarotJourneyEntries, shouldShowTarotJourney } from "@/lib/tarotJourneyStore";
import styles from "@/components/tarot/TarotJourneyPanel.module.css";

type TarotJourneyPanelProps = {
  compact?: boolean;
};

export function TarotJourneyPanel({ compact = false }: TarotJourneyPanelProps) {
  const entries = readTarotJourneyEntries();
  if (!shouldShowTarotJourney()) return null;
  const summary = buildTarotJourneySummary(entries);

  return (
    <section className={styles.panel} aria-labelledby="tarot-journey-title">
      <p className={styles.eyebrow}>Твоё путешествие через карты</p>
      <h2 id="tarot-journey-title" className={styles.title}>
        {summary.periodLabel.charAt(0).toUpperCase() + summary.periodLabel.slice(1)}
      </h2>
      <p className={styles.sub}>
        Не статистика — история: какие темы и карты сопровождали твои вопросы.
      </p>

      {summary.themes.length ? (
        <div className={styles.section}>
          <p className={styles.sectionLabel}>Чаще всего встречались темы</p>
          <div className={styles.chips}>
            {summary.themes.map((theme) => (
              <span key={theme.label} className={styles.chip}>
                <span>{theme.emoji}</span>
                <span>{theme.label}</span>
              </span>
            ))}
          </div>
        </div>
      ) : null}

      {!compact && summary.frequentCards.length ? (
        <div className={styles.section}>
          <p className={styles.sectionLabel}>Карты, которые приходили чаще</p>
          <div className={styles.cardList}>
            {summary.frequentCards.map((card) => (
              <span key={card.cardId} className={styles.chip}>
                {card.name}
                {card.count > 1 ? ` · ${card.count}` : ""}
              </span>
            ))}
          </div>
        </div>
      ) : null}

      {!compact && summary.recentQuestions.length ? (
        <div className={styles.section}>
          <p className={styles.sectionLabel}>Вопросы, к которым ты возвращался</p>
          <ul className={styles.questionList}>
            {summary.recentQuestions.map((q) => (
              <li key={q} className={styles.questionItem}>
                «{q.length > 120 ? `${q.slice(0, 117)}…` : q}»
              </li>
            ))}
          </ul>
        </div>
      ) : null}

      <Link href="/tarot/journey" className={styles.link}>
        Открыть историю →
      </Link>
    </section>
  );
}
