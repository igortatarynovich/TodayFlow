"use client";

import type { CSSProperties } from "react";
import { useCallback, useEffect, useRef, useState } from "react";
import { RITUAL_COPY } from "@/components/today/todayRitualCopy";
import { pulseDayPhaseRevealFlash } from "@/lib/dayPhaseAtmosphere";
import { ritualRevealCtaReady, useRitualRevealStages } from "@/lib/ritualRevealCascade";
import styles from "./RitualNumberPickExperience.module.css";

type Props = {
  /** Уже известное число дня (если есть в morning после reveal). */
  systemDisplay: string;
  /** Title under the digit (e.g. Управленец). */
  numberTitle?: string | null;
  /** «Значение» body. */
  numberMeaning?: string | null;
  /** «Опора дня» body — bridge / personal, never invent. */
  daySupport?: string | null;
  /** symbol — рубашки без цифр; digit — декоративные 1–6. */
  tileMode?: "symbol" | "digit";
  reduceMotion: boolean;
  /**
   * Resolve the system day number on first tile pick (server reveal).
   * Must return a displayable digit string — never "—".
   */
  onRevealRequest?: () => Promise<{
    display: string;
    title?: string | null;
    meaning?: string | null;
    support?: string | null;
  }>;
  onComplete: () => void;
  /** Already confirmed today — show reveal, not pick ring. */
  alreadyConfirmed?: boolean;
};

/** Handoff closed state: 9 unlabeled circular slots (ritual gesture, not a real pick). */
const RING_SLOT_COUNT = 9;

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
  numberTitle = null,
  numberMeaning = null,
  daySupport = null,
  tileMode: _tileMode = "digit",
  reduceMotion,
  onRevealRequest,
  onComplete,
  alreadyConfirmed = false,
}: Props) {
  const [revealed, setRevealed] = useState(
    () => alreadyConfirmed && isDisplayableNumber(systemDisplay),
  );
  const [resolving, setResolving] = useState(false);
  const [display, setDisplay] = useState(systemDisplay);
  const [title, setTitle] = useState(numberTitle);
  const [meaning, setMeaning] = useState(numberMeaning);
  const [support, setSupport] = useState(daySupport);
  const [resolveError, setResolveError] = useState(false);
  const doneRef = useRef(alreadyConfirmed);
  const { showMeaning, showContext } = useRitualRevealStages(revealed, reduceMotion);

  useEffect(() => {
    if (!alreadyConfirmed) return;
    if (isDisplayableNumber(systemDisplay)) {
      setDisplay(systemDisplay);
      setRevealed(true);
      doneRef.current = true;
    }
  }, [alreadyConfirmed, systemDisplay]);

  useEffect(() => {
    if (numberTitle) setTitle(numberTitle);
  }, [numberTitle]);
  useEffect(() => {
    if (numberMeaning) setMeaning(numberMeaning);
  }, [numberMeaning]);
  useEffect(() => {
    if (daySupport) setSupport(daySupport);
  }, [daySupport]);

  const hasMeaning = Boolean(String(meaning ?? "").trim());
  const hasSupport = Boolean(String(support ?? "").trim());
  const ctaReady = ritualRevealCtaReady({
    showMeaning,
    showContext,
    hasMeaning,
    hasContext: hasSupport,
  });

  const finish = useCallback(() => {
    if (doneRef.current) return;
    doneRef.current = true;
    onComplete();
  }, [onComplete]);

  const onPick = () => {
    if (revealed || resolving) return;
    vibrate(12, !reduceMotion);

    const show = (payload: {
      value: string;
      nextTitle?: string | null;
      nextMeaning?: string | null;
      nextSupport?: string | null;
    }) => {
      setDisplay(payload.value);
      if (payload.nextTitle) setTitle(payload.nextTitle);
      if (payload.nextMeaning) setMeaning(payload.nextMeaning);
      if (payload.nextSupport) setSupport(payload.nextSupport);
      setRevealed(true);
      if (!reduceMotion) pulseDayPhaseRevealFlash();
      vibrate(14, !reduceMotion);
    };

    if (isDisplayableNumber(systemDisplay) && !onRevealRequest) {
      show({
        value: systemDisplay,
        nextTitle: numberTitle,
        nextMeaning: numberMeaning,
        nextSupport: daySupport,
      });
      return;
    }

    if (!onRevealRequest) {
      if (isDisplayableNumber(systemDisplay)) {
        show({
          value: systemDisplay,
          nextTitle: numberTitle,
          nextMeaning: numberMeaning,
          nextSupport: daySupport,
        });
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
        show({
          value,
          nextTitle: result.title ?? numberTitle,
          nextMeaning: result.meaning ?? numberMeaning,
          nextSupport: result.support ?? daySupport,
        });
      })
      .catch(() => {
        setResolveError(true);
      })
      .finally(() => {
        setResolving(false);
      });
  };

  const onConfirm = () => {
    if (!revealed || !ctaReady || doneRef.current) return;
    vibrate(18, !reduceMotion);
    finish();
  };

  if (revealed) {
    return (
      <div
        className={styles.wrap}
        data-testid="ritual-number-reveal"
        data-reduce={reduceMotion ? "true" : undefined}
      >
        <div className={styles.cascade}>
          <div className={styles.cascadeCard} data-testid="ritual-number-value">
            <div className={styles.halo}>
              <span className={styles.bigNum}>{display}</span>
            </div>
            {title ? <p className={styles.valueTitle}>{title}</p> : null}
          </div>

          {hasMeaning && showMeaning ? (
            <div className={styles.cascadeCard} data-testid="ritual-number-meaning">
              <p className={styles.cascadeEyebrow}>Значение</p>
              <p className={styles.cascadeBody}>{meaning}</p>
            </div>
          ) : null}

          {hasSupport && showContext ? (
            <div className={styles.cascadeCard} data-testid="ritual-number-support">
              <p className={styles.cascadeEyebrow}>{RITUAL_COPY.dayEngineBriefEyebrow}</p>
              <p className={styles.cascadeBody}>{support}</p>
            </div>
          ) : null}
        </div>

        {ctaReady && !alreadyConfirmed ? (
          <div className={styles.revealActions}>
            <button type="button" className={styles.revealPrimaryCta} onClick={onConfirm}>
              {RITUAL_COPY.numberRevealDoneCta}
            </button>
          </div>
        ) : null}
      </div>
    );
  }

  return (
    <div className={styles.wrap} data-testid="ritual-number-pick-flower" data-reduce={reduceMotion ? "true" : undefined}>
      <div className={styles.flower} aria-hidden />
      <div className={styles.ring} data-slots={RING_SLOT_COUNT}>
        {Array.from({ length: RING_SLOT_COUNT }, (_, i) => {
          const ang = -Math.PI / 2 + (i * Math.PI * 2) / RING_SLOT_COUNT;
          const x = CX + R * Math.cos(ang) - 23;
          const y = CY + R * Math.sin(ang) - 23;
          return (
            <button
              key={i}
              type="button"
              className={styles.numBtn}
              data-blank="true"
              style={{ left: x, top: y, "--ni": i } as CSSProperties}
              onClick={onPick}
              disabled={resolving}
              aria-busy={resolving || undefined}
              aria-label="Открыть число дня"
            />
          );
        })}
      </div>
      {resolving ? <p className={styles.hint}>…</p> : null}
      {resolveError ? (
        <p className={styles.hint} role="alert">
          Не удалось открыть. Попробуй ещё раз.
        </p>
      ) : null}
    </div>
  );
}
