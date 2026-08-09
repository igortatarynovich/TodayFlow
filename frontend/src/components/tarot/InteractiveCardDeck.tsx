"use client";

import type { CSSProperties, KeyboardEvent, PointerEvent as ReactPointerEvent } from "react";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { TarotCard } from "@/lib/types";
import { CardVisual } from "./CardVisual";
import { TarotCardBack } from "./TarotCardBack";
import { MotionFlip } from "@/design-system/motion";
import { usePrefersReducedMotion } from "@/design-system/motion/usePrefersReducedMotion";
import { tarotCardDisplayHeightPx } from "@/lib/tarotCardAssets";
import styles from "./InteractiveCardDeck.module.css";

interface InteractiveCardDeckProps {
  cards: TarotCard[];
  requiredCount: number;
  onCardsSelected: (selectedCards: Array<{ card: TarotCard; orientation: "upright" | "reversed" }>) => void;
  spreadTitle?: string;
  selectionLabels?: string[];
  ritualIntro?: string;
  variant?: "light" | "dark";
  /** Show wallet-stack skeleton while deck loads. */
  loading?: boolean;
  /** Re-draw a fresh deck from the server (called on reset). */
  onReshuffle?: () => void;
  /** Today ritual: wallet only — no focus empty panel / swipe explainers. */
  stackOnly?: boolean;
}

const FOCUS_WIDTH = 280;
const STRIP_WIDTH = 72;
/** Wallet stack card width — same sleeve proportions as ritual back. */
const STACK_WIDTH = 176;
const VISIBLE_STACK = 4;
const SWIPE_DISTANCE_RATIO = 0.3;
const SWIPE_VELOCITY_PX_MS = 0.55;
const FLY_MS = 280;
const FLY_MS_REDUCED = 150;
const TAP_MOVE_TOLERANCE_PX = 12;

type DragState = {
  pointerId: number;
  startX: number;
  startY: number;
  startAt: number;
  dx: number;
  dy: number;
};

type FlyIntent = "select" | "cycle";

function hashSeed(seed: string): number {
  let h = 2166136261;
  for (let i = 0; i < seed.length; i += 1) {
    h ^= seed.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return h >>> 0;
}

/** Fixed angles for session — avoid re-roll on re-render. */
function stackPoseAngles(seed: string, count: number): number[] {
  const base = hashSeed(seed || "deck");
  const out: number[] = [];
  for (let i = 0; i < count; i += 1) {
    const n = (base + i * 9973) % 1000;
    out.push(-3 + (n / 999) * 6);
  }
  return out;
}

function shuffleIndices(count: number): number[] {
  const arr = Array.from({ length: count }, (_, i) => i);
  for (let i = arr.length - 1; i > 0; i -= 1) {
    const j = Math.floor(Math.random() * (i + 1));
    const tmp = arr[i];
    arr[i] = arr[j]!;
    arr[j] = tmp!;
  }
  return arr;
}

function cardsFingerprint(cards: TarotCard[]): string {
  return cards.map((c) => c.id).join(",");
}

export function InteractiveCardDeck({
  cards,
  requiredCount,
  onCardsSelected,
  spreadTitle,
  selectionLabels,
  ritualIntro,
  variant = "light",
  loading = false,
  onReshuffle,
  stackOnly = false,
}: InteractiveCardDeckProps) {
  const reduceMotion = usePrefersReducedMotion();
  const [deckOrder, setDeckOrder] = useState<number[]>(() => shuffleIndices(cards.length));
  const [shuffleEpoch, setShuffleEpoch] = useState(0);
  const [selectedIndices, setSelectedIndices] = useState<number[]>([]);
  const [revealedCards, setRevealedCards] = useState<Map<number, "upright" | "reversed">>(new Map());
  const [focusIndex, setFocusIndex] = useState<number | null>(null);
  const [focusFlipped, setFocusFlipped] = useState(false);
  const [drag, setDrag] = useState<DragState | null>(null);
  const [flyOut, setFlyOut] = useState<{ dx: number; dy: number; intent: FlyIntent } | null>(null);
  const [springing, setSpringing] = useState(false);
  const [busy, setBusy] = useState(false);
  const dragRef = useRef<DragState | null>(null);
  const topCardRef = useRef<HTMLButtonElement | null>(null);
  const cardsFpRef = useRef(cardsFingerprint(cards));
  const selectedRef = useRef(selectedIndices);
  selectedRef.current = selectedIndices;

  const focusHeight = tarotCardDisplayHeightPx(FOCUS_WIDTH);
  const stackHeight = tarotCardDisplayHeightPx(STACK_WIDTH);

  // New deck from parent → reshuffle local order and clear selection.
  useEffect(() => {
    const fp = cardsFingerprint(cards);
    if (fp === cardsFpRef.current && deckOrder.length === cards.length) return;
    cardsFpRef.current = fp;
    setDeckOrder(shuffleIndices(cards.length));
    setShuffleEpoch((n) => n + 1);
    setSelectedIndices([]);
    setRevealedCards(new Map());
    setFocusIndex(null);
    setFlyOut(null);
    setDrag(null);
    dragRef.current = null;
    setBusy(false);
  }, [cards, deckOrder.length]);

  const poseSeed = useMemo(
    () => `${shuffleEpoch}:${requiredCount}:${cardsFingerprint(cards)}`,
    [cards, requiredCount, shuffleEpoch],
  );
  const layerAngles = useMemo(() => stackPoseAngles(poseSeed, VISIBLE_STACK), [poseSeed]);

  useEffect(() => {
    if (focusIndex == null) {
      setFocusFlipped(false);
      return;
    }
    setFocusFlipped(false);
    const t = window.setTimeout(() => setFocusFlipped(true), reduceMotion ? 0 : 40);
    return () => window.clearTimeout(t);
  }, [focusIndex, reduceMotion]);

  const orderedSelected = useMemo(
    () =>
      selectedIndices.map((index) => ({
        index,
        card: cards[index],
        orientation: revealedCards.get(index) || "upright",
      })),
    [selectedIndices, cards, revealedCards],
  );

  const remainingIndices = useMemo(
    () => deckOrder.filter((index) => !selectedIndices.includes(index)),
    [deckOrder, selectedIndices],
  );

  const canSelectMore = selectedIndices.length < requiredCount && remainingIndices.length > 0;
  const canCycle = remainingIndices.length > 1;
  const visibleRemaining = remainingIndices.slice(0, VISIBLE_STACK);
  const focusCard = focusIndex != null ? cards[focusIndex] : null;
  const focusOrientation = focusIndex != null ? revealedCards.get(focusIndex) || "upright" : "upright";
  const focusSlot = focusIndex != null ? selectedIndices.indexOf(focusIndex) : -1;
  const progressLabel = `Карта ${Math.min(selectedIndices.length + 1, requiredCount)} из ${requiredCount}`;
  const activeStepLabel = selectionLabels?.[selectedIndices.length] || progressLabel;

  const emitSelection = useCallback(
    (indices: number[], revealed: Map<number, "upright" | "reversed">) => {
      if (indices.length === requiredCount) {
        onCardsSelected(
          indices.map((idx) => ({
            card: cards[idx],
            orientation: (revealed.get(idx) || "upright") as "upright" | "reversed",
          })),
        );
      } else {
        onCardsSelected([]);
      }
    },
    [cards, onCardsSelected, requiredCount],
  );

  const finalizeSelect = useCallback(() => {
    const remaining = deckOrder.filter((index) => !selectedRef.current.includes(index));
    if (selectedRef.current.length >= requiredCount || remaining.length === 0) {
      setBusy(false);
      return;
    }
    const index = remaining[0];
    if (index == null) {
      setBusy(false);
      return;
    }
    const orientation: "upright" | "reversed" = Math.random() < 0.5 ? "upright" : "reversed";
    const nextIndices = [...selectedRef.current, index];
    const nextRevealed = new Map(revealedCards);
    nextRevealed.set(index, orientation);
    setSelectedIndices(nextIndices);
    setRevealedCards(nextRevealed);
    setFocusIndex(index);
    setFlyOut(null);
    setDrag(null);
    dragRef.current = null;
    setSpringing(false);
    emitSelection(nextIndices, nextRevealed);
    window.setTimeout(() => setBusy(false), reduceMotion ? 160 : 420);
  }, [deckOrder, emitSelection, reduceMotion, requiredCount, revealedCards]);

  const finalizeCycle = useCallback(() => {
    setDeckOrder((prev) => {
      const selected = new Set(selectedRef.current);
      const remaining = prev.filter((index) => !selected.has(index));
      if (remaining.length < 2) return prev;
      const top = remaining[0]!;
      return [...prev.filter((index) => index !== top), top];
    });
    setFlyOut(null);
    setDrag(null);
    dragRef.current = null;
    setSpringing(false);
    setBusy(false);
  }, []);

  const commitSelect = useCallback(() => {
    if (!canSelectMore || busy) return;
    setBusy(true);
    finalizeSelect();
  }, [busy, canSelectMore, finalizeSelect]);

  const startFly = useCallback(
    (dx: number, dy: number, intent: FlyIntent) => {
      if (busy || !canSelectMore) return;
      if (intent === "cycle" && !canCycle) {
        // Only one card left — treat as select.
        setBusy(true);
        finalizeSelect();
        return;
      }
      setBusy(true);
      setDrag(null);
      dragRef.current = null;
      if (reduceMotion) {
        setFlyOut({ dx: 0, dy: intent === "cycle" ? -18 : -24, intent });
      } else {
        const mag = Math.max(Math.hypot(dx, dy), 1);
        const boost = Math.max(STACK_WIDTH * 1.35, mag * 1.8);
        setFlyOut({ dx: (dx / mag) * boost, dy: (dy / mag) * boost, intent });
      }
      window.setTimeout(
        () => {
          if (intent === "cycle") finalizeCycle();
          else finalizeSelect();
        },
        reduceMotion ? FLY_MS_REDUCED : FLY_MS,
      );
    },
    [busy, canCycle, canSelectMore, finalizeCycle, finalizeSelect, reduceMotion],
  );

  const handleReset = () => {
    if (busy) return;
    setSelectedIndices([]);
    setRevealedCards(new Map());
    setFocusIndex(null);
    setFlyOut(null);
    setDrag(null);
    dragRef.current = null;
    setSpringing(false);
    onCardsSelected([]);
    // Always reshuffle local order immediately; fresh draw may follow via onReshuffle.
    setDeckOrder(shuffleIndices(cards.length));
    setShuffleEpoch((n) => n + 1);
    onReshuffle?.();
  };

  const onPointerDown = (event: ReactPointerEvent<HTMLButtonElement>) => {
    if (busy || flyOut || !canSelectMore) return;
    if (event.button !== 0 && event.pointerType === "mouse") return;
    const next: DragState = {
      pointerId: event.pointerId,
      startX: event.clientX,
      startY: event.clientY,
      startAt: performance.now(),
      dx: 0,
      dy: 0,
    };
    dragRef.current = next;
    setDrag(next);
    event.currentTarget.setPointerCapture(event.pointerId);
  };

  const onPointerMove = (event: ReactPointerEvent<HTMLButtonElement>) => {
    const current = dragRef.current;
    if (!current || current.pointerId !== event.pointerId || flyOut) return;
    const next = {
      ...current,
      dx: event.clientX - current.startX,
      dy: event.clientY - current.startY,
    };
    dragRef.current = next;
    setDrag(next);
  };

  const finishPointer = (event: ReactPointerEvent<HTMLButtonElement>) => {
    const current = dragRef.current;
    if (!current || current.pointerId !== event.pointerId) return;
    try {
      event.currentTarget.releasePointerCapture(event.pointerId);
    } catch {
      /* already released */
    }
    const dx = event.clientX - current.startX;
    const dy = event.clientY - current.startY;
    const elapsed = Math.max(performance.now() - current.startAt, 1);
    const distance = Math.hypot(dx, dy);
    const velocity = distance / elapsed;
    const threshold = STACK_WIDTH * SWIPE_DISTANCE_RATIO;
    dragRef.current = null;

    if (distance < TAP_MOVE_TOLERANCE_PX) {
      setDrag(null);
      // Tap = choose this card.
      commitSelect();
      return;
    }

    if (distance >= threshold || velocity >= SWIPE_VELOCITY_PX_MS) {
      // Swipe = leaf to the next card (browse), not select.
      startFly(dx, dy, "cycle");
      return;
    }

    setDrag(null);
    setSpringing(true);
    window.setTimeout(() => setSpringing(false), 300);
  };

  const onKeyDownTop = (event: KeyboardEvent<HTMLButtonElement>) => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      commitSelect();
      return;
    }
    if ((event.key === "ArrowRight" || event.key === "ArrowLeft" || event.key === "ArrowDown") && canCycle) {
      event.preventDefault();
      const dx = event.key === "ArrowLeft" ? -STACK_WIDTH : event.key === "ArrowRight" ? STACK_WIDTH : 0;
      const dy = event.key === "ArrowDown" ? STACK_WIDTH * 0.6 : 0;
      startFly(dx || 0, dy || -STACK_WIDTH * 0.4, "cycle");
    }
  };

  const focusSlotLabel =
    focusSlot >= 0
      ? selectionLabels?.[focusSlot] || `Карта ${focusSlot + 1}`
      : canSelectMore
        ? activeStepLabel
        : "Расклад собран";

  const topDragDx = flyOut?.dx ?? drag?.dx ?? 0;
  const topDragDy = flyOut?.dy ?? drag?.dy ?? 0;
  const topDragging = Boolean(drag) && !flyOut;
  const topFlying = Boolean(flyOut);
  const topRotate = topDragging || topFlying ? topDragDx * 0.045 : 0;

  if (loading) {
    return (
      <div
        className={`${styles.root} ${variant === "dark" ? styles.rootDark : ""}`.trim()}
        data-testid="tarot-interactive-deck-loading"
      >
        <div className={styles.walletStage} aria-hidden>
          <div className={styles.walletStack} style={{ width: STACK_WIDTH, height: stackHeight + 18 }}>
            {[0, 1, 2].map((i) => (
              <div
                key={i}
                className={`${styles.walletLayer} ${styles.walletSkeleton}`}
                style={
                  {
                    "--layer-y": `${i * 5}px`,
                    "--layer-rot": `${(i - 1) * 2}deg`,
                    "--layer-scale": `${1 - i * 0.025}`,
                    "--layer-z": String(10 - i),
                  } as CSSProperties
                }
              />
            ))}
          </div>
        </div>
        <p className={styles.trustHint}>Готовим колоду…</p>
      </div>
    );
  }

  return (
    <div
      className={`${styles.root} ${variant === "dark" ? styles.rootDark : ""}`.trim()}
      data-testid="tarot-interactive-deck"
    >
      {spreadTitle ? (
        <div className={styles.header}>
          <h3 className={styles.spreadTitle}>{spreadTitle}</h3>
          <p className={styles.spreadMeta}>
            {requiredCount === 1 ? "1 карта" : `${requiredCount} карт`}
          </p>
        </div>
      ) : null}

      {requiredCount > 1 ? (
        <div className={styles.strip} aria-label="Карты расклада">
          {Array.from({ length: requiredCount }).map((_, slotIndex) => {
            const selected = orderedSelected[slotIndex];
            const slotLabel = selectionLabels?.[slotIndex] || `Карта ${slotIndex + 1}`;
            const isActive = selected != null && selected.index === focusIndex;
            const isNext = canSelectMore && slotIndex === selectedIndices.length;

            return (
              <button
                key={slotLabel}
                type="button"
                className={`${styles.stripSlot} ${selected ? styles.stripSlotFilled : ""} ${isActive ? styles.stripSlotActive : ""} ${isNext ? styles.stripSlotNext : ""}`.trim()}
                disabled={!selected}
                onClick={() => selected && setFocusIndex(selected.index)}
                aria-label={selected ? `${slotLabel}: ${selected.card.name}` : `${slotLabel}: пусто`}
                aria-pressed={isActive}
              >
                <p className={styles.stripLabel}>{slotLabel}</p>
                {selected ? (
                  <>
                    <div className={styles.stripArt}>
                      <CardVisual
                        card={selected.card}
                        orientation={selected.orientation}
                        size="xs"
                        widthPx={STRIP_WIDTH}
                        chrome="bare"
                        showName={false}
                      />
                    </div>
                    <p className={styles.stripName}>{selected.card.name}</p>
                  </>
                ) : (
                  <div className={styles.stripArt}>
                    <TarotCardBack widthPx={STRIP_WIDTH} chrome="bare" dimmed />
                  </div>
                )}
              </button>
            );
          })}
        </div>
      ) : null}

      {ritualIntro && !stackOnly ? <p className={styles.intro}>{ritualIntro}</p> : null}

      <div className={stackOnly ? styles.stageStackOnly : styles.stage}>
        {!stackOnly ? (
          <div className={styles.stageFocus}>
            {focusCard ? (
              <>
                <div className={styles.focusFrame} style={{ width: FOCUS_WIDTH, maxWidth: "100%", height: focusHeight }}>
                  <MotionFlip
                    testId={`tarot-deck-motion-flip-${focusIndex}`}
                    flipped={focusFlipped}
                    reducedMotion={reduceMotion}
                    durationMs={reduceMotion ? 150 : 450}
                    back={
                      <div className={styles.focusFill}>
                        <TarotCardBack widthPx={FOCUS_WIDTH} chrome="bare" />
                      </div>
                    }
                    front={
                      <div className={styles.focusFill}>
                        <CardVisual
                          card={focusCard}
                          orientation={focusOrientation}
                          size="hero"
                          widthPx={FOCUS_WIDTH}
                          chrome="bare"
                          showName={false}
                        />
                      </div>
                    }
                  />
                </div>
                <div className={styles.focusMeta}>
                  <p className={styles.focusSlot}>{focusSlotLabel}</p>
                  <p className={styles.focusName}>{focusCard.name}</p>
                  <p className={styles.focusOrient}>
                    {focusOrientation === "reversed" ? "Перевёрнутое положение" : "Прямое положение"}
                  </p>
                </div>
              </>
            ) : (
              <div className={styles.focusEmpty} aria-hidden={canSelectMore}>
                <p className={styles.focusEmptyTitle}>Карта откроется здесь</p>
                <p className={styles.focusEmptyBody}>Листайте стопку свайпом и тапните, когда почувствуете свою карту.</p>
              </div>
            )}
          </div>
        ) : null}

        <div className={styles.deckColumn}>
          {canSelectMore ? (
            <>
              {selectionLabels?.[selectedIndices.length] && !stackOnly ? (
                <p className={styles.stepLabel}>{selectionLabels[selectedIndices.length]}</p>
              ) : null}
              <div className={styles.walletStage}>
                <div
                  className={styles.walletStack}
                  style={{ width: STACK_WIDTH, height: stackHeight + (VISIBLE_STACK - 1) * 6 }}
                  data-testid="tarot-wallet-stack"
                >
                  {[...visibleRemaining].reverse().map((cardIndex, reverseLayer) => {
                    const layerFromTop = visibleRemaining.length - 1 - reverseLayer;
                    const isTop = layerFromTop === 0;
                    const angle = layerAngles[layerFromTop] ?? 0;
                    const y = layerFromTop * 5;
                    const scale = 1 - layerFromTop * 0.025;
                    const layerStyle = {
                      "--layer-y": `${y}px`,
                      "--layer-rot": `${angle}deg`,
                      "--layer-scale": String(scale),
                      "--layer-z": String(20 - layerFromTop),
                      ...(isTop
                        ? {
                            "--drag-x": `${topDragDx}px`,
                            "--drag-y": `${topDragDy}px`,
                            "--drag-rot": `${topRotate}deg`,
                          }
                        : null),
                    } as CSSProperties;

                    if (!isTop) {
                      return (
                        <div
                          key={`layer-${cardIndex}-${shuffleEpoch}`}
                          className={styles.walletLayer}
                          style={layerStyle}
                          aria-hidden
                        >
                          <TarotCardBack widthPx={STACK_WIDTH} chrome="bare" />
                        </div>
                      );
                    }

                    return (
                      <button
                        key={`layer-${cardIndex}-${shuffleEpoch}`}
                        ref={topCardRef}
                        type="button"
                        className={`${styles.walletLayer} ${styles.walletTop} ${topDragging ? styles.walletDragging : ""} ${topFlying ? styles.walletFlying : ""} ${topFlying && reduceMotion ? styles.walletFlyingFade : ""} ${springing ? styles.walletSpring : ""}`.trim()}
                        style={layerStyle}
                        onPointerDown={onPointerDown}
                        onPointerMove={onPointerMove}
                        onPointerUp={finishPointer}
                        onPointerCancel={finishPointer}
                        onKeyDown={onKeyDownTop}
                        aria-label="Открыть карту дня"
                        data-testid="tarot-deck-draw"
                        disabled={busy}
                      >
                        <TarotCardBack widthPx={STACK_WIDTH} chrome="bare" />
                      </button>
                    );
                  })}
                </div>
              </div>
              {!stackOnly ? (
                <>
                  <p className={styles.progress}>{progressLabel}</p>
                  <p className={styles.trustHint}>
                    {canCycle
                      ? "Свайп — листать. Тап — выбрать эту карту."
                      : "Тап — выбрать последнюю карту."}
                  </p>
                </>
              ) : null}
            </>
          ) : remainingIndices.length === 0 || selectedIndices.length >= requiredCount ? (
            stackOnly ? null : (
              <p className={styles.fanDoneHint}>
                {selectedIndices.length >= requiredCount ? "Расклад собран." : "Карты закончились"}
              </p>
            )
          ) : null}

          {selectedIndices.length > 0 && !stackOnly ? (
            <button type="button" onClick={handleReset} className={styles.resetLink} disabled={busy}>
              Сбросить и перетасовать
            </button>
          ) : null}
        </div>
      </div>

      {selectedIndices.length === requiredCount && !stackOnly ? (
        <p className={styles.doneNote}>Все карты на месте — откройте толкование.</p>
      ) : null}
    </div>
  );
}
