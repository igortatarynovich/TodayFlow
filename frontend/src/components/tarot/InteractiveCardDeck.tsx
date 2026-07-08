"use client";

import { useState } from "react";
import { TarotCard } from "@/lib/types";
import { CardVisual } from "./CardVisual";
import { TarotCardBack } from "./TarotCardBack";
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

export function InteractiveCardDeck({
  cards,
  requiredCount,
  onCardsSelected,
  spreadTitle,
  selectionLabels,
  ritualIntro,
  variant = "light",
}: InteractiveCardDeckProps) {
  const [selectedIndices, setSelectedIndices] = useState<Set<number>>(new Set());
  const [revealedCards, setRevealedCards] = useState<Map<number, "upright" | "reversed">>(new Map());

  const handleCardClick = (index: number) => {
    if (selectedIndices.has(index) || selectedIndices.size >= requiredCount) return;

    const orientation: "upright" | "reversed" = Math.random() < 0.5 ? "upright" : "reversed";
    const newSelected = new Set(selectedIndices);
    newSelected.add(index);
    setSelectedIndices(newSelected);

    const newRevealed = new Map(revealedCards);
    newRevealed.set(index, orientation);
    setRevealedCards(newRevealed);

    if (newSelected.size === requiredCount) {
      const selectedCards = Array.from(newSelected).map((idx) => ({
        card: cards[idx],
        orientation: (newRevealed.get(idx) || "upright") as "upright" | "reversed",
      }));
      onCardsSelected(selectedCards);
    }
  };

  const handleReset = () => {
    setSelectedIndices(new Set());
    setRevealedCards(new Map());
    onCardsSelected([]);
  };

  const canSelectMore = selectedIndices.size < requiredCount;
  const orderedSelected = Array.from(selectedIndices).map((index) => ({
    index,
    card: cards[index],
    orientation: revealedCards.get(index) || "upright",
  }));
  const activeStepLabel =
    selectionLabels?.[selectedIndices.size] ||
    `Карта ${Math.min(selectedIndices.size + 1, requiredCount)} из ${requiredCount}`;

  return (
    <div className={`${styles.root} ${variant === "dark" ? styles.rootDark : ""}`.trim()}>
      {spreadTitle ? (
        <div className={styles.header}>
          <h3 className={styles.spreadTitle}>{spreadTitle}</h3>
          <p className={styles.spreadMeta}>
            {requiredCount === 1 ? "1 карта" : `${requiredCount} карт`}
            {selectedIndices.size > 0 ? ` · ${selectedIndices.size}/${requiredCount}` : ""}
          </p>
        </div>
      ) : null}

      <div className={styles.stepPanel}>
        <div className={styles.stepRow}>
          <div>
            <p className={styles.stepEyebrow}>Шаг</p>
            <p className={styles.stepLabel}>
              {canSelectMore ? activeStepLabel : "Готово — открой результат или сбрось."}
            </p>
          </div>
          {selectedIndices.size > 0 ? (
            <button type="button" onClick={handleReset} className="orbit-button orbit-button-secondary orbit-button-sm">
              Сброс
            </button>
          ) : null}
        </div>

        {ritualIntro ? <p className={styles.intro}>{ritualIntro}</p> : null}

        <div className={styles.slots}>
          {Array.from({ length: requiredCount }).map((_, slotIndex) => {
            const selected = orderedSelected[slotIndex];
            const slotLabel = selectionLabels?.[slotIndex] || `Карта ${slotIndex + 1}`;

            return (
              <div
                key={slotLabel}
                className={`${styles.slot} ${selected ? styles.slotFilled : ""}`}
              >
                <div>
                  <p className={styles.slotIndex}>{String(slotIndex + 1).padStart(2, "0")}</p>
                  <p className={styles.slotLabel}>{slotLabel}</p>
                </div>

                {selected ? (
                  <div className={styles.slotCard}>
                    <CardVisual card={selected.card} orientation={selected.orientation} size="sm" showName={false} />
                    <p className={styles.slotName}>{selected.card?.name}</p>
                    <p className={styles.slotOrient}>
                      {selected.orientation === "reversed" ? "Перевёрнута" : "Прямая"}
                    </p>
                  </div>
                ) : (
                  <div className={styles.slotPlaceholder}>
                    <TarotCardBack widthPx={72} dimmed />
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      <div className={styles.deckGrid}>
        {cards.map((card, index) => {
          const isRevealed = revealedCards.has(index);
          const isSelected = selectedIndices.has(index);
          const orientation = revealedCards.get(index) || "upright";
          const disabled = !canSelectMore && !isSelected;

          return (
            <div
              key={`${card.id}-${index}`}
              className={`${styles.deckCell} ${disabled ? styles.deckCellDisabled : ""}`}
            >
              {isRevealed ? (
                <>
                  <CardVisual card={card} orientation={orientation} size="xs" showName={false} interactive={false} />
                  {isSelected ? <span className={styles.checkBadge}>✓</span> : null}
                </>
              ) : (
                <TarotCardBack
                  widthPx={68}
                  interactive={canSelectMore}
                  onClick={() => handleCardClick(index)}
                  dimmed={disabled}
                />
              )}
            </div>
          );
        })}
      </div>

      {selectedIndices.size === requiredCount ? (
        <p className={styles.doneNote}>Все выбраны — открой результат.</p>
      ) : null}
    </div>
  );
}
