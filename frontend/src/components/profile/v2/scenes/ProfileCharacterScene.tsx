"use client";

import {
  profileMotionStaggerDelay,
  profileMotionStyles,
  useProfileMotionInView,
} from "@/components/foundation/ProfileMotion";
import { PROFILE_V2_COPY, PROFILE_V2_DEPTH_NAV } from "@/components/profile/v2/profileV2SystemCopy";
import styles from "@/components/profile/v2/profileV2System.module.css";

export type ProfileCharacterSceneProps = {
  strengthens: string[];
  drains: string[];
  helps: string[];
  decisionStyle: string | null;
  patterns: string[];
  lifeMission: string | null;
  relationshipStyle?: string | null;
  moneyStyle?: string | null;
  livingChanges?: string | null;
};

const characterNav = PROFILE_V2_DEPTH_NAV.find((s) => s.id === "character");

/**
 * Portrait materials already in contract — main scroll, not buried in natal fold.
 */
export function ProfileCharacterScene({
  strengthens,
  drains,
  helps,
  decisionStyle,
  patterns,
  lifeMission,
  relationshipStyle = null,
  moneyStyle = null,
  livingChanges = null,
}: ProfileCharacterSceneProps) {
  const hasBody =
    strengthens.length ||
    drains.length ||
    helps.length ||
    decisionStyle ||
    patterns.length ||
    lifeMission ||
    relationshipStyle ||
    moneyStyle ||
    livingChanges;
  const motion = useProfileMotionInView<HTMLElement>(70);
  if (!hasBody) return null;

  const copy = PROFILE_V2_COPY.zones.characterMore;

  return (
    <section
      id="profile-v2-character"
      ref={motion.ref}
      className={`${styles.zone} ${styles.journeyScene} ${motion.className}`}
      style={motion.style}
      aria-labelledby="profile-v2-character-title"
      data-testid="profile-v2-character"
    >
      <header className={styles.zoneHeader}>
        <div>
          <p className={styles.journeyStepIndex}>
            <span className={styles.journeyStepBadge}>
              {characterNav?.step.replace(/^0/, "") ?? "·"}
            </span>
            <span id="profile-v2-character-title">{copy.title}</span>
          </p>
          <p className={styles.zoneLead}>{copy.lead}</p>
        </div>
      </header>

      {lifeMission ? (
        <article className={styles.missionCard} data-testid="profile-v2-character-mission">
          <p className={styles.factLabel}>{PROFILE_V2_COPY.zones.direction.missionLabel}</p>
          <p className={styles.missionText}>{lifeMission}</p>
        </article>
      ) : null}

      <div className={styles.characterGrid}>
        {strengthens.length ? (
          <article
            className={`${styles.characterPanel} ${styles.characterPanelGift} ${profileMotionStyles.staggerItem}`}
            style={profileMotionStaggerDelay(0, 70)}
            data-testid="profile-v2-character-strengthens"
          >
            <p className={styles.characterPanelTitle}>{copy.strengthens}</p>
            <ul className={styles.bulletList}>
              {strengthens.map((item) => (
                <li key={item} className={styles.bulletItem}>
                  <span className={styles.bulletMark} aria-hidden>
                    ✓
                  </span>
                  {item}
                </li>
              ))}
            </ul>
          </article>
        ) : null}

        {drains.length ? (
          <article
            className={`${styles.characterPanel} ${styles.characterPanelTrap} ${profileMotionStyles.staggerItem}`}
            style={profileMotionStaggerDelay(1, 70)}
            data-testid="profile-v2-character-drains"
          >
            <p className={styles.characterPanelTitle}>{copy.drains}</p>
            <ul className={styles.bulletList}>
              {drains.map((item) => (
                <li key={item} className={styles.bulletItem}>
                  <span className={`${styles.bulletMark} ${styles.bulletMarkMuted}`.trim()} aria-hidden>
                    •
                  </span>
                  {item}
                </li>
              ))}
            </ul>
          </article>
        ) : null}

        {helps.length ? (
          <article
            className={`${styles.characterPanel} ${styles.characterPanelHelp} ${profileMotionStyles.staggerItem}`}
            style={profileMotionStaggerDelay(2, 70)}
            data-testid="profile-v2-character-helps"
          >
            <p className={styles.characterPanelTitle}>{copy.helps}</p>
            <ul className={styles.bulletList}>
              {helps.map((item) => (
                <li key={item} className={styles.bulletItem}>
                  <span className={styles.bulletMark} aria-hidden>
                    ◆
                  </span>
                  {item}
                </li>
              ))}
            </ul>
          </article>
        ) : null}
      </div>

      {decisionStyle ? (
        <article className={styles.decisionBlock} data-testid="profile-v2-character-decisions">
          <p className={styles.characterPanelTitle}>{copy.decisions}</p>
          <p className={styles.factHint}>{decisionStyle}</p>
        </article>
      ) : null}

      {relationshipStyle ? (
        <article className={styles.decisionBlock} data-testid="profile-v2-character-relationship">
          <p className={styles.characterPanelTitle}>{copy.intimacy}</p>
          <p className={styles.factHint}>{relationshipStyle}</p>
        </article>
      ) : null}

      {moneyStyle ? (
        <article className={styles.decisionBlock} data-testid="profile-v2-character-money">
          <p className={styles.characterPanelTitle}>{copy.money}</p>
          <p className={styles.factHint}>{moneyStyle}</p>
        </article>
      ) : null}

      {patterns.length ? (
        <article
          className={styles.characterPanel}
          style={{ marginTop: "1rem" }}
          data-testid="profile-v2-character-patterns"
        >
          <p className={styles.characterPanelTitle}>{copy.patterns}</p>
          <ul className={styles.bulletList}>
            {patterns.map((item) => (
              <li key={item} className={styles.bulletItem}>
                <span className={`${styles.bulletMark} ${styles.bulletMarkMuted}`.trim()} aria-hidden>
                  ◦
                </span>
                {item}
              </li>
            ))}
          </ul>
        </article>
      ) : null}

      {livingChanges ? (
        <article className={styles.decisionBlock} data-testid="profile-v2-character-living">
          <p className={styles.characterPanelTitle}>{copy.living}</p>
          <p className={styles.factHint}>{livingChanges}</p>
        </article>
      ) : null}
    </section>
  );
}
