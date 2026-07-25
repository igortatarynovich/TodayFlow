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

const FAN_WIDTH = 112;
const FOCUS_WIDTH = 300;
const STRIP_WIDTH = 76;

function fanStyle(index: number, count: number): CSSProperties {
  const mid = (count - 1) / 2;
  const t = index - mid;
  const rotate = t * 6.5;
  const lift = -Math.abs(t) * 5 + (t === 0 ? 8 : 0);
  const shiftX = t * 42;
  const z = 20 - Math.abs(t);
  return {
    "--fan-rotate": `${rotate}deg`,
    "--fan-x": `${shiftX}px`,
    "--fan-y": `${lift}px`,
    "--fan-z": String(z),
    "--stagger": `${index * 40}ms`,
  } as CSSProperties;
}

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
  const [fanOpen, setFanOpen] = useState(false);
  const [focusFlipped, setFocusFlipped] = useState(false);

  const focusHeight = tarotCardDisplayHeightPx(FOCUS_WIDTH);

  useEffect(() => {
    const id = requestAnimationFrame(() => setFanOpen(true));
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

  const available = useMemo(
    () => cards.map((card, index) => ({ card, index })).filter((item) => !selectedIndices.includes(item.index)),
    [cards, selectedIndices],
  );

  const canSelectMore = selectedIndices.length < requiredCount;
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

  const handlePick = (index: number) => {
    if (selectedIndices.includes(index) || selectedIndices.length >= requiredCount) return;
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

  return (
    <div className={`${styles.root} ${variant === "dark" ? styles.rootDark : ""} ${fanOpen ? styles.fanOpen : ""}`.trim()}>
      {spreadTitle ? (
        <div className={styles.header}>
          <h3 className={styles.spreadTitle}>{spreadTitle}</h3>
          <p className={styles.spreadMeta}>
            {requiredCount === 1 ? "1 карта" : `${requiredCount} карт`}
            {selectedIndices.length > 0 ? ` · ${selectedIndices.length}/${requiredCount}` : ""}
          </p>
        </div>
      ) : null}

      <div className={styles.stage}>
        <div className={styles.stageLeft}>
          <p className={styles.stepEyebrow}>Шаг</p>
          <p className={styles.stepLabel}>
            {canSelectMore ? `Выбери: ${activeStepLabel}` : "Готово — открой толкование или сбрось."}
          </p>
          {ritualIntro ? <p className={styles.intro}>{ritualIntro}</p> : null}

          {canSelectMore && available.length > 0 ? (
            <div className={styles.fanStage} aria-label="Колода для выбора">
              {available.slice(0, 7).map((item, fanIndex, arr) => (
                <button
                  key={`${item.card.id}-${item.index}`}
                  type="button"
                  className={styles.fanCard}
                  style={fanStyle(fanIndex, arr.length)}
                  onClick={() => handlePick(item.index)}
                  aria-label={`Выбрать рубашку ${fanIndex + 1}`}
                >
                  <TarotCardBack widthPx={FAN_WIDTH} chrome="bare" />
                </button>
              ))}
            </div>
          ) : (
            <p className={styles.fanDoneHint}>Все карты выбраны — смотри фокус и полосу расклада.</p>
          )}

          <p className={styles.trustHint}>Прислушайся к первому импульсу.</p>

          {selectedIndices.length > 0 ? (
            <button type="button" onClick={handleReset} className={styles.resetLink}>
              Сбросить выбор
            </button>
          ) : null}
        </div>

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
              <p className={styles.focusEmptyBody}>Выбери рубашку слева — иллюстрация раскроется крупно.</p>
            </div>
          )}
        </div>
      </div>

      <div className={styles.strip} aria-label="Карты расклада">
        {Array.from({ length: requiredCount }).map((_, slotIndex) => {
          const selected = orderedSelected[slotIndex];
          const slotLabel = selectionLabels?.[slotIndex] || `Карта ${slotIndex + 1}`;
          const isActive = selected != null && selected.index === focusIndex;

          return (
            <button
              key={slotLabel}
              type="button"
              className={`${styles.stripSlot} ${selected ? styles.stripSlotFilled : ""} ${isActive ? styles.stripSlotActive : ""}`}
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
                  <p className={styles.stripOrient}>
                    {selected.orientation === "reversed" ? "Перевёрнута" : "Прямая"}
                  </p>
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

      {selectedIndices.length === requiredCount ? (
        <p className={styles.doneNote}>Все выбраны — открой толкование.</p>
      ) : null}
    </div>
  );
}
