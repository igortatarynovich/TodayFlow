"use client";

/**
 * Today tarot pick — same wallet deck as Tarot spreads (not a fan).
 * Any sleeve opens the predetermined day card (ritual honesty).
 */
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { InteractiveCardDeck } from "@/components/tarot/InteractiveCardDeck";
import { TarotPicture } from "@/components/tarot/TarotPicture";
import { MotionFlip, MotionReveal } from "@/design-system/motion";
import { pulseDayPhaseRevealFlash } from "@/lib/dayPhaseAtmosphere";
import {
  tarotCardBackPicture,
  tarotCardFacePicture,
} from "@/lib/tarotCardAssets";
import type { TarotCard } from "@/lib/types";
import { postJson } from "@/lib/api";
import { TAROT_DECK_INDICES } from "@/components/today/todayTarotDraw";
import { RITUAL_COPY } from "@/components/today/todayRitualCopy";
import { ritualRevealCtaReady, useRitualRevealStages } from "@/lib/ritualRevealCascade";
import styles from "@/design-system/patterns/dsRitualTarotPick.module.css";

type Phase = "idle" | "deck" | "reveal";

type Props = {
  anchorCardId: number;
  /** Если карта уже зафиксирована (persist), показываем раскрытие до «Дальше». */
  resumeCommittedId: number | null;
  cardTitleRu: string;
  tagLabels: string[];
  /** «Значение» — base meaning / legacy body. */
  meaningText?: string | null;
  /** «Для тебя сегодня» — personal/bridge, optionally with number cross-ref. */
  personalTodayText?: string | null;
  onCommitMain: (id: number) => void;
  /** PR1: face visible — отдельный `tarot_revealed` event. */
  onRevealed?: (id: number) => void;
  onContinue: () => void;
  /** Kept for API compat; deck uses a fixed visual stack size. */
  gridSize?: number;
  reduceMotion: boolean;
  /** Сразу колода (Today), без одиночной рубашки. */
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

function localDeckCards(count: number): TarotCard[] {
  const n = Math.max(8, Math.min(count, TAROT_DECK_INDICES.length));
  return TAROT_DECK_INDICES.slice(0, n).map((id) => ({
    id,
    name: `Card ${id}`,
    keywords: [],
    upright: "",
    reversed: "",
    correspondences: {},
  }));
}

export function RitualTarotPickExperience({
  anchorCardId,
  resumeCommittedId,
  cardTitleRu,
  tagLabels,
  meaningText = null,
  personalTodayText = null,
  onCommitMain,
  onRevealed,
  onContinue,
  reduceMotion,
  startAtGrid = false,
  allowSkipAnimation = true,
  gridSize = 12,
  gridLead,
  gridSub,
}: Props) {
  const effectiveId = resumeCommittedId ?? anchorCardId;
  const [phase, setPhase] = useState<Phase>(() => {
    if (resumeCommittedId != null) return "reveal";
    if (startAtGrid) return "deck";
    return "idle";
  });
  const [pressed, setPressed] = useState(false);
  const [deckCards, setDeckCards] = useState<TarotCard[]>(() => localDeckCards(gridSize));
  const [deckLoading, setDeckLoading] = useState(false);
  const committedRef = useRef(false);
  const continueRef = useRef(false);
  const mountedInRevealRef = useRef(resumeCommittedId != null);
  const [cardFlipped, setCardFlipped] = useState(() => resumeCommittedId != null);
  const revealActive = phase === "reveal" && cardFlipped;
  const { showMeaning, showContext } = useRitualRevealStages(revealActive, reduceMotion);
  const hasMeaning = Boolean(String(meaningText ?? "").trim());
  const hasPersonal = Boolean(String(personalTodayText ?? "").trim());
  const ctaReady = ritualRevealCtaReady({
    showMeaning,
    showContext,
    hasMeaning,
    hasContext: hasPersonal,
  });

  const back = tarotCardBackPicture();
  const face = tarotCardFacePicture(effectiveId) ?? back;

  const deckKey = useMemo(
    () => `today-deck:${anchorCardId}:${gridSize}`,
    [anchorCardId, gridSize],
  );

  useEffect(() => {
    if (resumeCommittedId == null) return;
    if (phase === "reveal") return;
    committedRef.current = true;
    setPhase("reveal");
  }, [resumeCommittedId, phase]);

  useEffect(() => {
    if (phase !== "deck") return;
    let cancelled = false;
    setDeckLoading(true);
    void (async () => {
      try {
        const data = await postJson<TarotCard[]>("/tarot/deck/draw", {
          count: Math.max(8, gridSize),
        });
        if (!cancelled && Array.isArray(data) && data.length > 0) {
          setDeckCards(data);
        }
      } catch {
        try {
          const data = await postJson<TarotCard[]>("/tarot/deck/draw/public", {
            count: Math.max(8, gridSize),
          });
          if (!cancelled && Array.isArray(data) && data.length > 0) {
            setDeckCards(data);
          }
        } catch {
          /* keep localDeckCards */
        }
      } finally {
        if (!cancelled) setDeckLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [phase, gridSize, deckKey]);

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

  const commitDayCard = useCallback(() => {
    if (committedRef.current) return;
    committedRef.current = true;
    vibrate(14, !reduceMotion);
    onCommitMain(anchorCardId);
    setPhase("reveal");
    onRevealed?.(anchorCardId);
    vibrate(18, !reduceMotion);
  }, [anchorCardId, onCommitMain, onRevealed, reduceMotion]);

  const onContinueClick = () => {
    if (!ctaReady || continueRef.current) return;
    continueRef.current = true;
    vibrate(16, !reduceMotion);
    onContinue();
  };

  const onIdleActivate = () => {
    vibrate(12, !reduceMotion);
    if (reduceMotion) {
      setPhase("deck");
      return;
    }
    setPressed(true);
    window.setTimeout(() => setPressed(false), 200);
    window.setTimeout(() => setPhase("deck"), 190);
  };

  const skipToRevealCommitted = () => {
    commitDayCard();
  };

  if (phase === "reveal") {
    return (
      <div
        className={styles.wrap}
        data-testid="ritual-tarot-reveal"
        data-reduce={reduceMotion ? "true" : undefined}
      >
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

          {hasMeaning && showMeaning ? (
            <div className={styles.cascadeCard} data-testid="ritual-tarot-meaning">
              <p className={styles.cascadeEyebrow}>Значение</p>
              <p className={styles.cascadeBody}>{meaningText}</p>
            </div>
          ) : null}

          {hasPersonal && showContext ? (
            <div className={styles.cascadeCard} data-testid="ritual-tarot-personal">
              <p className={styles.cascadeEyebrow}>Для тебя сегодня</p>
              <p className={styles.cascadeBody}>{personalTodayText}</p>
            </div>
          ) : null}

          {ctaReady ? (
            <div className={styles.revealCtaRow}>
              <button type="button" className={styles.revealPrimaryCta} onClick={onContinueClick}>
                {RITUAL_COPY.tarotRevealContinueCta}
              </button>
            </div>
          ) : null}
        </div>
      </div>
    );
  }

  if (phase === "deck") {
    return (
      <div
        className={`${styles.wrap} ${styles.table}`}
        data-testid="ritual-tarot-pick-grid"
        data-pick-mode="deck"
        data-reduce={reduceMotion ? "true" : undefined}
      >
        <div className={styles.deckStage} aria-label="Колода карты дня">
          <InteractiveCardDeck
            key={deckKey}
            cards={deckCards}
            requiredCount={1}
            loading={deckLoading && deckCards.length === 0}
            onCardsSelected={() => {
              commitDayCard();
            }}
            ritualIntro=""
            variant="light"
            stackOnly
          />
        </div>
        <button
          type="button"
          className={styles.skipLink}
          data-testid="ritual-tarot-deck-commit"
          onClick={commitDayCard}
        >
          Открыть карту
        </button>
      </div>
    );
  }

  return (
    <div
      className={`${styles.wrap} ${styles.breathe} ${pressed ? styles.press : ""}`}
      data-reduce={reduceMotion ? "true" : undefined}
      data-testid="ritual-tarot-idle"
    >
      <div className={styles.idleStack}>
        <button
          type="button"
          className={styles.idleDeck}
          onClick={onIdleActivate}
          aria-label={RITUAL_COPY.tarotIdleHint}
          data-testid="ritual-tarot-idle-deck"
        >
          <span className={`${styles.idleDeckBack}`} aria-hidden>
            <TarotPicture sources={back} sizes="168px" />
          </span>
          <span className={`${styles.idleDeckBack}`} aria-hidden>
            <TarotPicture sources={back} sizes="168px" />
          </span>
          <span className={`${styles.idleDeckBack}`}>
            <span className={styles.breatheGlow} aria-hidden />
            <TarotPicture sources={back} sizes="168px" priority />
          </span>
        </button>
        <span className={styles.hint}>
          <span className={styles.hintSparkle} aria-hidden>
            ✦
          </span>
          <span>{RITUAL_COPY.tarotIdleHint}</span>
        </span>
        {allowSkipAnimation ? (
          <button type="button" className={styles.skipLink} onClick={skipToRevealCommitted}>
            {RITUAL_COPY.tarotSkipAnimationCta}
          </button>
        ) : null}
      </div>
    </div>
  );
}
