"use client";

import type { CSSProperties } from "react";
import { useCallback, useRef, useState } from "react";
import { RITUAL_COPY } from "@/components/today/todayRitualCopy";
import { pulseDayPhaseRevealFlash } from "@/lib/dayPhaseAtmosphere";
import styles from "./RitualNumberPickExperience.module.css";

type Props = {
  /** Уже рассчитанное число дня (показываем после «выбора»). */
  systemDisplay: string;
  numberMeaning?: string;
  /** symbol — рубашки без цифр; digit — декоративные 1–6. */
  tileMode?: "symbol" | "digit";
  reduceMotion: boolean;
  onComplete: () => void;
};

const NUMBER_TILE_SYMBOLS = ["✦", "○", "●", "◇", "◆", "✧"] as const;

function vibrate(pattern: number | number[], allow: boolean) {
  if (!allow) return;
  try {
    if (typeof navigator !== "undefined" && typeof navigator.vibrate === "function") {
      navigator.vibrate(pattern);
    }
  } catch {
    /* noop */
  }
}

const R = 92;
const CX = 130;
const CY = 130;

export function RitualNumberPickExperience({
  systemDisplay,
  numberMeaning,
  tileMode = "digit",
  reduceMotion,
  onComplete,
}: Props) {
  const [revealed, setRevealed] = useState(false);
  const doneRef = useRef(false);

  const finish = useCallback(() => {
    if (doneRef.current) return;
    doneRef.current = true;
    onComplete();
  }, [onComplete]);

  const onPick = () => {
    if (revealed) return;
    vibrate(12, !reduceMotion);
    setRevealed(true);
    if (!reduceMotion) pulseDayPhaseRevealFlash();
    vibrate(14, !reduceMotion);
  };

  const onConfirm = () => {
    if (!revealed || doneRef.current) return;
    vibrate(18, !reduceMotion);
    finish();
  };

  if (revealed) {
    return (
      <div className={styles.wrap} data-reduce={reduceMotion ? "true" : undefined}>
        <div className={styles.reveal}>
          <div className={styles.halo}>
            <span className={styles.bigNum}>{systemDisplay}</span>
          </div>
          {numberMeaning ? (
            <p className={styles.revealMeaning}>{numberMeaning}</p>
          ) : null}
        </div>
        <div className={styles.revealActions}>
          <button type="button" className={styles.revealPrimaryCta} onClick={onConfirm}>
            {RITUAL_COPY.numberRevealDoneCta}
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.wrap} data-testid="ritual-number-pick-flower" data-reduce={reduceMotion ? "true" : undefined}>
      <div className={styles.flower} aria-hidden />
      <div className={styles.ring}>
        {[1, 2, 3, 4, 5, 6].map((n, i) => {
          const ang = -Math.PI / 2 + (i * Math.PI * 2) / 6;
          const x = CX + R * Math.cos(ang) - 23;
          const y = CY + R * Math.sin(ang) - 23;
          return (
            <button
              key={n}
              type="button"
              className={styles.numBtn}
              style={{ left: x, top: y, "--ni": i } as CSSProperties}
              onClick={onPick}
            >
              {tileMode === "symbol" ? NUMBER_TILE_SYMBOLS[i] : n}
            </button>
          );
        })}
      </div>
      <div className={styles.energyInfo} role="note">
        <span className={styles.energyInfoIcon} aria-hidden>
          ⓘ
        </span>
        <span>{RITUAL_COPY.numberDayEnergyInfo}</span>
      </div>
      <p className={styles.hint}>{RITUAL_COPY.numberCircleHint}</p>
    </div>
  );
}
