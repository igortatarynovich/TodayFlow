"use client";

import type { ProfileV0MovementCard } from "@/lib/profilePage/buildProfileV0Data";
import styles from "./profileV0.module.css";

export function ProfileV0ActionLayer({ action }: { action: ProfileV0MovementCard }) {
  return (
    <section className={styles.profileActionGrid} aria-label="Как двигаться">
      <article className={`${styles.profileCard} ${styles.profileActionCard} ${styles.profileActionCardGreen}`}>
        <p className={styles.compassLabel}>Как двигаться</p>
        <h3 className={styles.compassTitle}>{action.title}</h3>
        {action.mainText ? <p className={styles.compassMain}>{action.mainText}</p> : null}

        {action.rules.length ? (
          <ol className={styles.profileActionSteps}>
            {action.rules.map((rule, index) => (
              <li key={rule} className={styles.profileActionStep}>
                <span className={styles.profileActionStepNum}>{index + 1}</span>
                <span className={styles.profileActionStepText}>{rule}</span>
              </li>
            ))}
          </ol>
        ) : null}
      </article>

      <article className={`${styles.profileCard} ${styles.profileActionCard} ${styles.profileActionCardToday}`}>
        <p className={styles.compassTodayLabel}>Сегодня</p>
        <p className={styles.profileActionTodayText}>
          {action.recommendation || "Сфокусируйся на одном шаге, который усилит твой ритм."}
        </p>
      </article>
    </section>
  );
}
