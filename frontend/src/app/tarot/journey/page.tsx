"use client";

import Link from "next/link";
import { useMemo } from "react";
import { TarotJourneyPanel } from "@/components/tarot/TarotJourneyPanel";
import { buildTarotJourneySummary } from "@/lib/buildTarotJourneySummary";
import { readTarotJourneyEntries, shouldShowTarotJourney } from "@/lib/tarotJourneyStore";
import styles from "@/app/tarot/journey/TarotJourneyPage.module.css";

export default function TarotJourneyPage() {
  const summary = useMemo(() => buildTarotJourneySummary(readTarotJourneyEntries()), []);
  const visible = shouldShowTarotJourney();

  return (
    <main className={styles.page}>
      <div className={styles.shell}>
        {!visible ? (
          <section className={styles.empty}>
            <h1 className={styles.title}>Путешествие через карты</h1>
            <p className={styles.body}>
              История появится после нескольких раскладов — когда будет из чего собрать личную линию, а не цифры ради цифр.
            </p>
            <Link href="/tarot" className={styles.btnPrimary}>
              К вопросам →
            </Link>
          </section>
        ) : (
          <>
            <header className={styles.header}>
              <Link href="/tarot" className={styles.back}>
                ← Таро
              </Link>
              <h1 className={styles.title}>Твоё путешествие через карты</h1>
              <p className={styles.meta}>
                {summary.totalSessions} {summary.totalSessions === 1 ? "расклад" : "раскладов"} · {summary.periodLabel}
              </p>
            </header>
            <TarotJourneyPanel />
          </>
        )}
      </div>
    </main>
  );
}
