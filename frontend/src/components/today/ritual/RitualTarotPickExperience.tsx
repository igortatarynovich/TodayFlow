"use client";

import type { CSSProperties } from "react";
import { useEffect, useRef, useState } from "react";
import { MotionFlip, MotionReveal } from "@/design-system/motion";
import { pulseDayPhaseRevealFlash } from "@/lib/dayPhaseAtmosphere";
import {
  tarotCardBackPicture,
  tarotCardFacePicture,
} from "@/lib/tarotCardAssets";
import { TarotPicture } from "@/components/tarot/TarotPicture";
import { RITUAL_COPY } from "@/components/today/todayRitualCopy";
import styles from "./RitualTarotPickExperience.module.css";

type Phase = "idle" | "fan" | "reveal";

type Props = {
  anchorCardId: number;
  /** Если карта уже зафиксирована (persist), показываем раскрытие до «Дальше». */
  resumeCommittedId: number | null;
  cardTitleRu: string;
  tagLabels: string[];
  onCommitMain: (id: number) => void;
  /** PR1: face visible — отдельный `tarot_revealed` event. */
  onRevealed?: (id: number) => void;
  onContinue: () => void;
  /** Fan size (default 5 closed backs). */
  gridSize?: number;
  reduceMotion: boolean;
  /** Сразу веер закрытых карт (Today experience), без одиночной рубашки. */
  startAtGrid?: boolean;
  /** Скрыть «Показать карту сразу» — обход выбора. */
  allowSkipAnimation?: boolean;
  gridLead?: string;
  gridSub?: string;
};

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

/** Fan arc transforms for 5 cards — center slightly raised. */
function fanStyle(index: number, count: number, picked: number | null): CSSProperties {
  const mid = (count - 1) / 2;
  const t = index - mid;
  const rotate = t * 7.5;
  const lift = -Math.abs(t) * 6 + (Math.abs(t) === 0 ? 10 : 0);
  const shiftX = t * 38;
  const z = 10 - Math.abs(t);
  const isPicked = picked === index;
  const isDimmed = picked != null && !isPicked;
  return {
    "--fan-rotate": `${rotate}deg`,
    "--fan-x": `${shiftX}px`,
    "--fan-y": `${lift}px`,
    "--fan-z": String(isPicked ? 40 : z),
    "--stagger": `${index * 55}ms`,
    ...(isDimmed
      ? { opacity: 0.28, transform: `translateX(${shiftX}px) translateY(${lift + 12}px) rotate(${rotate}deg) scale(0.92)` }
      : null),
    ...(isPicked
      ? {
          opacity: 1,
          transform: `translateX(${shiftX * 0.35}px) translateY(${lift - 28}px) rotate(${rotate * 0.25}deg) scale(1.08)`,
        }
      : null),
  } as CSSProperties;
}

export function RitualTarotPickExperience({
  anchorCardId,
  resumeCommittedId,
  cardTitleRu,
  tagLabels,
  onCommitMain,
  onRevealed,
  onContinue,
  reduceMotion,
  startAtGrid = false,
  allowSkipAnimation = true,
  gridSize = 5,
  gridLead,
  gridSub,
}: Props) {
  const effectiveId = resumeCommittedId ?? anchorCardId;
  const [phase, setPhase] = useState<Phase>(() => {
    if (resumeCommittedId != null) return "reveal";
    if (startAtGrid) return "fan";
    return "idle";
  });
  const [pressed, setPressed] = useState(false);
  const [fanOpen, setFanOpen] = useState(false);
  const pickedRef = useRef<number | null>(null);
  const [picked, setPicked] = useState<number | null>(null);
  const continueRef = useRef(false);
  const mountedInRevealRef = useRef(resumeCommittedId != null);
  const [cardFlipped, setCardFlipped] = useState(() => resumeCommittedId != null);

  const back = tarotCardBackPicture();
  const face = tarotCardFacePicture(effectiveId) ?? back;

  useEffect(() => {
    if (resumeCommittedId != null && phase === "idle" && pickedRef.current == null) {
      setPhase("reveal");
    }
  }, [resumeCommittedId, phase]);

  useEffect(() => {
    if (phase !== "fan") return;
    const id = requestAnimationFrame(() => setFanOpen(true));
    return () => cancelAnimationFrame(id);
  }, [phase]);

  useEffect(() => {
    if (phase !== "reveal") return;
    if (mountedInRevealRef.current || reduceMotion) {
      mountedInRevealRef.current = false;
      setCardFlipped(true);
      return;
    }
    setCardFlipped(false);
    const t = window.setTimeout(() => setCardFlipped(true), 40);
    pulseDayPhaseRevealFlash();
    return () => window.clearTimeout(t);
  }, [phase, reduceMotion]);

  const onContinueClick = () => {
    if (continueRef.current) return;
    continueRef.current = true;
    vibrate(16, !reduceMotion);
    onContinue();
  };

  const onIdleActivate = () => {
    vibrate(12, !reduceMotion);
    if (reduceMotion) {
      setPhase("fan");
      return;
    }
    setPressed(true);
    window.setTimeout(() => setPressed(false), 200);
    window.setTimeout(() => setPhase("fan"), 190);
  };

  /** Ritual reveal: any sleeve opens the same predetermined day card. */
  const onPickSleeve = (i: number) => {
    if (pickedRef.current != null) return;
    pickedRef.current = i;
    vibrate(14, !reduceMotion);
    setPicked(i);
    onCommitMain(anchorCardId);
    const delay = reduceMotion ? 0 : 320;
    window.setTimeout(() => {
      setPhase("reveal");
      onRevealed?.(anchorCardId);
      vibrate(18, !reduceMotion);
    }, delay);
  };

  const skipToRevealCommitted = () => {
    if (pickedRef.current != null) return;
    pickedRef.current = 0;
    onCommitMain(anchorCardId);
    setPhase("reveal");
    onRevealed?.(anchorCardId);
    vibrate(10, !reduceMotion);
  };

  if (phase === "reveal") {
    return (
      <div className={styles.wrap} data-reduce={reduceMotion ? "true" : undefined}>
        <div className={styles.scene}>
          <p className={styles.revealScreenTitle}>{RITUAL_COPY.tarotRevealScreenTitle}</p>
          <div className={styles.revealStage}>
            <MotionFlip
              testId="ritual-tarot-motion-flip"
              flipped={cardFlipped}
              reducedMotion={reduceMotion}
              back={<TarotPicture sources={back} sizes="(max-width: 40rem) 58vw, 220px" priority />}
              front={<TarotPicture sources={face} sizes="(max-width: 40rem) 58vw, 220px" priority />}
            />
          </div>
          <MotionReveal reducedMotion={reduceMotion} delayMs={reduceMotion ? 0 : 90}>
            <div className={styles.revealMeta}>
              <p className={styles.revealCardName}>{cardTitleRu}</p>
              {tagLabels.length > 0 ? (
                <ul className={styles.revealTags}>
                  {tagLabels.map((t) => (
                    <li key={t}>{t}</li>
                  ))}
                </ul>
              ) : null}
            </div>
          </MotionReveal>
          <div className={styles.revealCtaRow}>
            <button type="button" className={styles.revealPrimaryCta} onClick={onContinueClick}>
              {RITUAL_COPY.tarotRevealContinueCta}
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (phase === "fan") {
    return (
      <div
        className={`${styles.wrap} ${styles.table} ${fanOpen ? styles.fanOpen : ""} ${picked != null ? styles.fanPicked : ""}`}
        data-testid="ritual-tarot-pick-grid"
        data-reduce={reduceMotion ? "true" : undefined}
      >
        <div className={styles.gridHeader}>
          <p className={styles.gridLead}>{gridLead ?? RITUAL_COPY.tarotGridLead}</p>
          <p className={styles.gridSub}>{gridSub ?? RITUAL_COPY.tarotGridSub}</p>
        </div>
        <div className={styles.fanStage} aria-label="Ритуал раскрытия карты дня">
          {Array.from({ length: gridSize }, (_, i) => (
            <button
              key={i}
              type="button"
              className={`${styles.fanCard} ${picked === i ? styles.fanCardPicked : ""}`}
              style={fanStyle(i, gridSize, picked)}
              onClick={() => onPickSleeve(i)}
              aria-label={`Рубашка ${i + 1}`}
            >
              <TarotPicture sources={back} sizes="96px" />
            </button>
          ))}
        </div>
        <p className={styles.fanHonesty}>{RITUAL_COPY.tarotFanHonesty}</p>
        <p className={styles.gridFooter}>{RITUAL_COPY.tarotGridPickFooter}</p>
      </div>
    );
  }

  return (
    <div
      className={`${styles.wrap} ${styles.breathe} ${pressed ? styles.press : ""}`}
      data-reduce={reduceMotion ? "true" : undefined}
    >
      <div className={styles.idleStack}>
        <button type="button" className={styles.idleCard} onClick={onIdleActivate}>
          <span className={styles.breatheGlow} aria-hidden />
          <TarotPicture sources={back} sizes="168px" priority />
          <span className={styles.hint}>
            <span className={styles.hintSparkle} aria-hidden>
              ✦
            </span>
            <span>{RITUAL_COPY.tarotIdleHint}</span>
          </span>
        </button>
        {allowSkipAnimation ? (
          <button type="button" className={styles.skipLink} onClick={skipToRevealCommitted}>
            {RITUAL_COPY.tarotSkipAnimationCta}
          </button>
        ) : null}
      </div>
    </div>
  );
}
