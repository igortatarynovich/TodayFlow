"use client";

import { useState, type ReactNode } from "react";
import styles from "./conversation.module.css";

type Props = {
  turnId: string;
  message: ReactNode;
  response?: ReactNode;
  deepen?: ReactNode;
  deepenLabel?: string;
  roleLabel?: string;
  continuity?: ReactNode;
};

export function ConversationTurn({
  turnId,
  message,
  response,
  deepen,
  deepenLabel = "Развернуть подробнее",
  roleLabel = "TodayFlow",
  continuity,
}: Props) {
  const [deepenOpen, setDeepenOpen] = useState(false);

  return (
    <article className={styles.turn} data-testid={`conversation-turn-${turnId}`}>
      {continuity ? <div className={styles.continuity}>{continuity}</div> : null}
      <div className={styles.turnPractitioner}>
        <p className={styles.role}>{roleLabel}</p>
        <div className={styles.message}>{message}</div>
        {deepen ? (
          <div className={styles.deepen}>
            <button
              type="button"
              className={styles.deepenToggle}
              aria-expanded={deepenOpen}
              onClick={() => setDeepenOpen((open) => !open)}
            >
              {deepenOpen ? "Свернуть" : deepenLabel}
            </button>
            {deepenOpen ? <div className={styles.deepenPanel}>{deepen}</div> : null}
          </div>
        ) : null}
      </div>
      {response ? <div className={styles.response}>{response}</div> : null}
    </article>
  );
}
