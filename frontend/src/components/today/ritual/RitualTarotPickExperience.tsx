"use client";

import type { CSSProperties } from "react";
import { useEffect, useRef, useState } from "react";
import {
  tarotCardBackSrc,
  tarotCardFaceSrc,
  TAROT_CARD_PIXEL_HEIGHT,
  TAROT_CARD_PIXEL_WIDTH,
} from "@/lib/tarotCardAssets";
import { RITUAL_COPY } from "@/components/today/todayRitualCopy";
import styles from "./RitualTarotPickExperience.module.css";

type Phase = "idle" | "grid" | "reveal";

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
  /** PR1 canon: 5 закрытых карт (default 5). */
  gridSize?: number;
  reduceMotion: boolean;
  /** Сразу сетка закрытых карт (Today experience), без одиночной рубашки. */
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
    if (startAtGrid) return "grid";
    return "idle";
  });
  const [pressed, setPressed] = useState(false);
  const [gridOpen, setGridOpen] = useState(false);
  const pickedRef = useRef<number | null>(null);
  const [picked, setPicked] = useState<number | null>(null);
  const continueRef = useRef(false);

  const back = tarotCardBackSrc();
  const face = tarotCardFaceSrc(effectiveId);

  useEffect(() => {
    if (resumeCommittedId != null && phase === "idle" && pickedRef.current == null) {
      setPhase("reveal");
    }
  }, [resumeCommittedId, phase]);

  useEffect(() => {
    if (phase !== "grid") return;
    const id = requestAnimationFrame(() => setGridOpen(true));
    return () => cancelAnimationFrame(id);
  }, [phase]);

  const onContinueClick = () => {
    if (continueRef.current) return;
    continueRef.current = true;
    vibrate(16, !reduceMotion);
    onContinue();
  };

  const onIdleActivate = () => {
    vibrate(12, !reduceMotion);
    if (reduceMotion) {
      setPhase("grid");
      return;
    }
    setPressed(true);
    window.setTimeout(() => setPressed(false), 200);
    window.setTimeout(() => setPhase("grid"), 190);
  };

  const onPick = (i: number) => {
    if (pickedRef.current != null) return;
    pickedRef.current = i;
    vibrate(14, !reduceMotion);
    setPicked(i);
    onCommitMain(anchorCardId);
    const delay = reduceMotion ? 0 : 280;
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

  if (phase === "reveal" && face) {
    return (
      <div className={styles.wrap} data-reduce={reduceMotion ? "true" : undefined}>
        <div>
          <p className={styles.revealScreenTitle}>{RITUAL_COPY.tarotRevealScreenTitle}</p>
          <div className={`${styles.revealStage} ${styles.revealFace}`}>
            {/* eslint-disable-next-line @next/next/no-img-element -- локальные PNG из public */}
            <img src={face} alt="" width={TAROT_CARD_PIXEL_WIDTH} height={TAROT_CARD_PIXEL_HEIGHT} draggable={false} />
          </div>
          <div className={styles.revealMeta}>
            <div style={{ fontFamily: "var(--orbit-font-display)", fontWeight: 600, color: "#2d241c", fontSize: "1.15rem" }}>
              {cardTitleRu}
            </div>
            {tagLabels.length > 0 ? (
              <div style={{ display: "flex", flexWrap: "wrap", gap: "0.35rem", justifyContent: "center", marginTop: "0.45rem" }}>
                {tagLabels.map((t) => (
                  <span
                    key={t}
                    style={{
                      fontSize: "0.72rem",
                      fontWeight: 600,
                      color: "#5f4930",
                      padding: "0.2rem 0.55rem",
                      borderRadius: 999,
                      background: "rgba(255, 237, 228, 0.75)",
                      border: "1px solid rgba(214,142,122,0.32)",
                    }}
                  >
                    {t}
                  </span>
                ))}
              </div>
            ) : null}
          </div>
          <div className={styles.revealCtaRow}>
            <button type="button" className={styles.revealPrimaryCta} onClick={onContinueClick}>
              {RITUAL_COPY.tarotRevealContinueCta}
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (phase === "grid") {
    return (
      <div
        className={`${styles.wrap} ${gridOpen ? styles.gridOpen : ""} ${picked != null ? styles.dimGridOthers : ""}`}
        data-testid="ritual-tarot-pick-grid"
        data-reduce={reduceMotion ? "true" : undefined}
      >
        <div className={styles.gridHeader}>
          <p className={styles.gridLead}>{gridLead ?? RITUAL_COPY.tarotGridLead}</p>
          <p className={styles.gridSub}>{gridSub ?? RITUAL_COPY.tarotGridSub}</p>
        </div>
        <div className={styles.gridRoot}>
          {Array.from({ length: gridSize }, (_, i) => (
            <button
              key={i}
              type="button"
              className={`${styles.gridCard} ${picked === i ? styles.gridPicked : ""}`}
              style={{ "--stagger": `${i * 55}ms` } as CSSProperties}
              onClick={() => onPick(i)}
            >
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src={back} alt="" width={TAROT_CARD_PIXEL_WIDTH} height={TAROT_CARD_PIXEL_HEIGHT} draggable={false} />
            </button>
          ))}
        </div>
        <div className={styles.gridHintPanel} role="note">
          <span className={styles.gridHintIcon} aria-hidden>
            ⓘ
          </span>
          <div className={styles.gridHintText}>
            <span className={styles.gridHintPrimary}>{RITUAL_COPY.tarotGridPickHintPrimary}</span>
            <span className={styles.gridHintSecondary}>{RITUAL_COPY.tarotGridPickHintSecondary}</span>
          </div>
        </div>
        <p className={styles.gridFooter}>{RITUAL_COPY.tarotGridPickFooter}</p>
      </div>
    );
  }

  return (
    <div
      className={`${styles.wrap} ${styles.breathe} ${pressed ? styles.press : ""}`}
      data-reduce={reduceMotion ? "true" : undefined}
    >
      <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 10 }}>
        <button type="button" className={styles.idleCard} onClick={onIdleActivate}>
          <span className={styles.breatheGlow} aria-hidden />
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src={back} alt="" width={TAROT_CARD_PIXEL_WIDTH} height={TAROT_CARD_PIXEL_HEIGHT} draggable={false} />
          <span className={styles.hint}>
            <span className={styles.hintSparkle} aria-hidden>
              ✦
            </span>
            <span>{RITUAL_COPY.tarotIdleHint}</span>
          </span>
        </button>
        {allowSkipAnimation ? (
          <button
            type="button"
            className="orbit-body-xs"
            style={{
              border: "none",
              background: "transparent",
              color: "#7a6a52",
              textDecoration: "underline",
              cursor: "pointer",
            }}
            onClick={skipToRevealCommitted}
          >
            {RITUAL_COPY.tarotSkipAnimationCta}
          </button>
        ) : null}
      </div>
    </div>
  );
}
