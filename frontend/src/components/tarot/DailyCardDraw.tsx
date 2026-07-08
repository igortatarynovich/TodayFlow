"use client";

import { useState, useEffect } from "react";
import { TarotCard } from "@/lib/types";
import { CardVisual } from "./CardVisual";
import Link from "next/link";
import { t } from "@/lib/i18n";

interface DailyCardDrawProps {
  card: TarotCard | null;
  orientation: "upright" | "reversed" | null;
  onDrawCard: () => Promise<void>;
  isDrawing: boolean;
  isAuthenticated: boolean;
  dashboardData?: any;
}

export function DailyCardDraw({ 
  card, 
  orientation, 
  onDrawCard, 
  isDrawing, 
  isAuthenticated,
  dashboardData 
}: DailyCardDrawProps) {
  const [isRevealed, setIsRevealed] = useState(false);

  // Сбрасываем isRevealed при изменении карты
  useEffect(() => {
    if (card && orientation) {
      setIsRevealed(false);
    }
  }, [card, orientation]);

  const handleReveal = () => {
    if (card && orientation) {
      setIsRevealed(true);
    }
  };

  // Если карта еще не вытянута
  if (!card || !orientation) {
    return (
      <div style={{ textAlign: "center", padding: "var(--orbit-space-xl)" }}>
        <h2 className="orbit-display-sm" style={{ marginBottom: "var(--orbit-space-md)" }}>
          {t("tarot.dailyCard.title", "Карта дня")}
        </h2>
        <p className="orbit-body-sm orbit-text-muted" style={{ marginBottom: "var(--orbit-space-lg)" }}>
          {t("tarot.dailyCard.drawFromDeck", "Карта из колоды — нажми ниже.")}
        </p>
        <button
          onClick={(e) => {
            e.preventDefault();
            onDrawCard();
          }}
          disabled={isDrawing}
          className="orbit-button orbit-button-primary"
          style={{ minWidth: "200px" }}
        >
          {isDrawing ? t("tarot.dailyCard.drawing", "Тяну…") : t("tarot.dailyCard.drawCard", "Вытянуть →")}
        </button>
      </div>
    );
  }

  // Если карта вытянута, но не перевернута
  if (!isRevealed) {
    return (
      <div style={{ textAlign: "center", padding: "var(--orbit-space-xl)" }}>
        <h2 className="orbit-display-sm" style={{ marginBottom: "var(--orbit-space-md)" }}>
          {t("tarot.dailyCard.title", "Карта дня")}
        </h2>
        <p className="orbit-body-sm orbit-text-muted" style={{ marginBottom: "var(--orbit-space-lg)" }}>
          {t("tarot.dailyCard.flipCard", "Нажми на рубашку — откроется значение.")}
        </p>
        
        {/* Карта рубашкой вверх */}
        <div
          onClick={handleReveal}
          style={{
            display: "inline-block",
            cursor: "pointer",
            transition: "transform 0.3s ease",
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.transform = "scale(1.05)";
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = "scale(1)";
          }}
        >
          <div
            style={{
              width: "234px",
              height: "390px",
              background: "linear-gradient(135deg, rgba(100, 100, 100, 0.2), rgba(150, 150, 150, 0.1))",
              border: "2px solid rgba(100, 100, 100, 0.4)",
              borderRadius: "var(--orbit-radius-md)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              boxShadow: "0 4px 16px rgba(0, 0, 0, 0.15)",
            }}
          >
            <div style={{ fontSize: "4rem", opacity: 0.6 }}>
              🃏
            </div>
          </div>
        </div>
        <p className="orbit-body-xs orbit-text-muted" style={{ marginTop: "var(--orbit-space-md)" }}>
          {t("tarot.dailyCard.clickToFlip", "Или тап по карте")}
        </p>
      </div>
    );
  }

  // Карта перевернута - показываем содержимое
  return (
    <div style={{ textAlign: "center", padding: "var(--orbit-space-xl)" }}>
      <h2 className="orbit-display-sm" style={{ marginBottom: "var(--orbit-space-md)" }}>
        {t("tarot.dailyCard.title", "Карта дня")}
      </h2>
      
      {/* Визуализация карты */}
      <div style={{ display: "flex", justifyContent: "center", marginBottom: "var(--orbit-space-lg)" }}>
        <CardVisual 
          card={card} 
          orientation={orientation} 
          size="lg"
          showName={true}
        />
      </div>

      {/* Интерпретация */}
      <div style={{ 
        padding: "var(--orbit-space-xl)",
        background: "var(--orbit-color-mist)",
        borderRadius: "var(--orbit-radius-md)",
        marginBottom: "var(--orbit-space-lg)",
        maxWidth: "600px",
        margin: "0 auto var(--orbit-space-lg)",
      }}>
        <h3 className="orbit-display-sm" style={{ marginBottom: "var(--orbit-space-sm)" }}>
          {card.name}
        </h3>
        <p className="orbit-body" style={{ marginBottom: "var(--orbit-space-md)", lineHeight: 1.6 }}>
          {orientation === "upright" ? card.upright : card.reversed}
        </p>
        {isAuthenticated && dashboardData?.liteReport?.internal_model && (
          <p className="orbit-body-sm orbit-text-muted" style={{ marginTop: "var(--orbit-space-md)", fontStyle: "italic" }}>
            {t("tarot.dailyCard.reflectsDay", "Фон дня и твой паттерн сегодня.")}
          </p>
        )}
      </div>

      {/* CTA: Связь с Dashboard */}
      <div style={{ marginTop: "var(--orbit-space-lg)" }}>
        {isAuthenticated ? (
          <>
            <Link href="/today" className="orbit-button orbit-button-secondary">
              {t("tarot.dailyCard.seeConnection", "К дню →")}
            </Link>
            {dashboardData?.liteReport?.internal_model && (
              <p className="orbit-body-xs orbit-text-muted" style={{ marginTop: "var(--orbit-space-sm)" }}>
                <Link href="/discover" className="orbit-link">
                  {t("tarot.dailyCard.whyThisCard", "Почему эта карта →")}
                </Link>
              </p>
            )}
          </>
        ) : (
          <Link href="/today" className="orbit-button orbit-button-secondary">
            {t("tarot.dailyCard.seeConnection", "К дню →")}
          </Link>
        )}
      </div>
    </div>
  );
}
