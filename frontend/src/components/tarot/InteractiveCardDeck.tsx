"use client";

import type { CSSProperties } from "react";
import { useEffect, useMemo, useState } from "react";
import { TarotCard } from "@/lib/types";
import { CardVisual } from "./CardVisual";
import { TarotCardBack } from "./TarotCardBack";
import { MotionFlip } from "@/design-system/motion";
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
}

const FOCUS_WIDTH = 280;
const STRIP_WIDTH = 72;
const STACK_WIDTH = 132;
/** Visible back layers in the table deck (visual depth only). */
const STACK_LAYERS = 4;

export function InteractiveCardDeck({
  cards,
  requiredCount,
  onCardsSelected,
  spreadTitle,
  selectionLabels,
  ritualIntro,
  variant = "light",
}: InteractiveCardDeckProps) {
  const [selectedIndices, setSelectedIndices] = useState<number[]>([]);
  const [revealedCards, setRevealedCards] = useState<Map<number, "upright" | "reversed">>(new Map());
  const [focusIndex, setFocusIndex] = useState<number | null>(null);
  const [focusFlipped, setFocusFlipped] = useState(false);
  const [deckReady, setDeckReady] = useState(false);

  const focusHeight = tarotCardDisplayHeightPx(FOCUS_WIDTH);

  useEffect(() => {
    const id = requestAnimationFrame(() => setDeckReady(true));
    return () => cancelAnimationFrame(id);
  }, []);

  useEffect(() => {
    if (focusIndex == null) {
      setFocusFlipped(false);
      return;
    }
    setFocusFlipped(false);
    const t = window.setTimeout(() => setFocusFlipped(true), 40);
    return () => window.clearTimeout(t);
  }, [focusIndex]);

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
    () => cards.map((_, index) => index).filter((index) => !selectedIndices.includes(index)),
    [cards, selectedIndices],
  );

  const canSelectMore = selectedIndices.length < requiredCount && remainingIndices.length > 0;
  const focusCard = focusIndex != null ? cards[focusIndex] : null;
  const focusOrientation = focusIndex != null ? revealedCards.get(focusIndex) || "upright" : "upright";
  const focusSlot = focusIndex != null ? selectedIndices.indexOf(focusIndex) : -1;
  const activeStepLabel =
    selectionLabels?.[selectedIndices.length] ||
    `Карта ${Math.min(selectedIndices.length + 1, requiredCount)} из ${requiredCount}`;

  const emitSelection = (indices: number[], revealed: Map<number, "upright" | "reversed">) => {
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
  };

  const drawNext = () => {
    if (!canSelectMore) return;
    const index = remainingIndices[0];
    if (index == null) return;
    const orientation: "upright" | "reversed" = Math.random() < 0.5 ? "upright" : "reversed";
    const nextIndices = [...selectedIndices, index];
    const nextRevealed = new Map(revealedCards);
    nextRevealed.set(index, orientation);
    setSelectedIndices(nextIndices);
    setRevealedCards(nextRevealed);
    setFocusIndex(index);
    emitSelection(nextIndices, nextRevealed);
  };

  const handleReset = () => {
    setSelectedIndices([]);
    setRevealedCards(new Map());
    setFocusIndex(null);
    onCardsSelected([]);
  };

  const focusSlotLabel =
    focusSlot >= 0
      ? selectionLabels?.[focusSlot] || `Карта ${focusSlot + 1}`
      : canSelectMore
        ? activeStepLabel
        : "Расклад собран";

  const stackLayerCount = Math.min(STACK_LAYERS, Math.max(1, remainingIndices.length));

  return (
    <div
      className={`${styles.root} ${variant === "dark" ? styles.rootDark : ""} ${deckReady ? styles.deckReady : ""}`.trim()}
      data-testid="tarot-interactive-deck"
    >
      {spreadTitle ? (
        <div className={styles.header}>
          <h3 className={styles.spreadTitle}>{spreadTitle}</h3>
          <p className={styles.spreadMeta}>
            {requiredCount === 1 ? "1 карта" : `${requiredCount} карт`}
            {selectedIndices.length > 0 ? ` · ${selectedIndices.length}/${requiredCount}` : ""}
          </p>
        </div>
      ) : null}

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

      <p className={styles.stepLabel}>
        {canSelectMore ? `Сейчас: ${activeStepLabel}` : "Все карты открыты — можно смотреть толкование."}
      </p>
      {ritualIntro ? <p className={styles.intro}>{ritualIntro}</p> : null}

      <div className={styles.stage}>
        <div className={styles.stageFocus}>
          {focusCard ? (
            <>
              <div className={styles.focusFrame} style={{ width: FOCUS_WIDTH, maxWidth: "100%", height: focusHeight }}>
                <MotionFlip
                  testId={`tarot-deck-motion-flip-${focusIndex}`}
                  flipped={focusFlipped}
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
            <div className={styles.focusEmpty}>
              <p className={styles.focusEmptyTitle}>Карта откроется здесь</p>
              <p className={styles.focusEmptyBody}>Коснитесь колоды ниже — или нажмите «Взять карту».</p>
            </div>
          )}
        </div>

        <div className={styles.deckColumn}>
          {canSelectMore ? (
            <>
              <button
                type="button"
                className={styles.deckStack}
                onClick={drawNext}
                aria-label={`Взять карту: ${activeStepLabel}`}
                data-testid="tarot-deck-draw"
              >
                {Array.from({ length: stackLayerCount }).map((_, layer) => {
                  const fromBack = stackLayerCount - 1 - layer;
                  const style = {
                    "--stack-i": String(fromBack),
                    "--stack-n": String(stackLayerCount),
                  } as CSSProperties;
                  return (
                    <span key={layer} className={styles.deckLayer} style={style} aria-hidden={layer > 0}>
                      <TarotCardBack widthPx={STACK_WIDTH} chrome="bare" />
                    </span>
                  );
                })}
              </button>
              <button type="button" className={styles.drawCta} onClick={drawNext} data-testid="tarot-deck-draw-cta">
                Взять карту
              </button>
              <p className={styles.trustHint}>Одна колода — один жест. Без веера и мелких целей.</p>
            </>
          ) : (
            <p className={styles.fanDoneHint}>Расклад собран.</p>
          )}

          {selectedIndices.length > 0 ? (
            <button type="button" onClick={handleReset} className={styles.resetLink}>
              Сбросить выбор
            </button>
          ) : null}
        </div>
      </div>

      {selectedIndices.length === requiredCount ? (
        <p className={styles.doneNote}>Все карты на месте — откройте толкование.</p>
      ) : null}
    </div>
  );
}
