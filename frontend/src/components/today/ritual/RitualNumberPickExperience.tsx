"use client";

import type { CSSProperties } from "react";
import { useCallback, useRef, useState } from "react";
import { RITUAL_COPY } from "@/components/today/todayRitualCopy";
import { pulseDayPhaseRevealFlash } from "@/lib/dayPhaseAtmosphere";
import styles from "./RitualNumberPickExperience.module.css";

type Props = {
  /** Уже известное число дня (если есть в morning после reveal). */
  systemDisplay: string;
  numberMeaning?: string;
  /** symbol — рубашки без цифр; digit — декоративные 1–6. */
  tileMode?: "symbol" | "digit";
  reduceMotion: boolean;
  /**
   * Resolve the system day number on first tile pick (server reveal).
   * Must return a displayable digit string — never "—".
   */
  onRevealRequest?: () => Promise<{ display: string; meaning?: string | null }>;
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

function isDisplayableNumber(value: string | null | undefined): boolean {
  const t = String(value ?? "").trim();
  return Boolean(t) && t !== "—" && t !== "-" && t !== "…";
}

export function RitualNumberPickExperience({
  systemDisplay,
  numberMeaning,
  tileMode = "digit",
  reduceMotion,
  onRevealRequest,
  onComplete,
}: Props) {
  const [revealed, setRevealed] = useState(false);
  const [resolving, setResolving] = useState(false);
  const [display, setDisplay] = useState(systemDisplay);
  const [meaning, setMeaning] = useState(numberMeaning);
  const [resolveError, setResolveError] = useState(false);
  const doneRef = useRef(false);

  const finish = useCallback(() => {
    if (doneRef.current) return;
    doneRef.current = true;
    onComplete();
  }, [onComplete]);

  const onPick = () => {
    if (revealed || resolving) return;
    vibrate(12, !reduceMotion);

    const show = (value: string, nextMeaning?: string | null) => {
      setDisplay(value);
      if (nextMeaning) setMeaning(nextMeaning);
      setRevealed(true);
      if (!reduceMotion) pulseDayPhaseRevealFlash();
      vibrate(14, !reduceMotion);
    };

    if (isDisplayableNumber(systemDisplay) && !onRevealRequest) {
      show(systemDisplay, numberMeaning);
      return;
    }

    if (!onRevealRequest) {
      if (isDisplayableNumber(systemDisplay)) {
        show(systemDisplay, numberMeaning);
      } else {
        setResolveError(true);
      }
      return;
    }

    setResolving(true);
    setResolveError(false);
    void onRevealRequest()
      .then((result) => {
        const value = String(result.display ?? "").trim();
        if (!isDisplayableNumber(value)) {
          setResolveError(true);
          return;
        }
        show(value, result.meaning ?? numberMeaning);
      })
      .catch(() => {
        setResolveError(true);
      })
      .finally(() => {
        setResolving(false);
      });
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
            <span className={styles.bigNum}>{display}</span>
          </div>
          {meaning ? <p className={styles.revealMeaning}>{meaning}</p> : null}
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
              disabled={resolving}
              aria-busy={resolving || undefined}
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
      <p className={styles.hint}>
        {resolving ? "Открываем число дня…" : RITUAL_COPY.numberCircleHint}
      </p>
      {resolveError ? (
        <p className={styles.hint} role="alert">
          Не удалось открыть число дня. Попробуй ещё раз.
        </p>
      ) : null}
    </div>
  );
}
