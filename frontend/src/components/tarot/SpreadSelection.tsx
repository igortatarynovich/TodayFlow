"use client";

import { LoadingSpinner } from "@/components/orbit";
import { InteractiveCardDeck } from "./InteractiveCardDeck";
import { TarotSpread } from "./TarotSpread";
import type { TarotCard, TarotSpreadResult, TarotSpreadHistoryResponse } from "@/lib/types";

interface Spread {
  id: string;
  title: string;
  description: string;
  icon: string;
  cards: number;
}

interface SpreadSelectionProps {
  spreads: Spread[];
  selectedSpread: Spread | null;
  loadingDeck: boolean;
  deckCards: TarotCard[];
  currentSpread: TarotSpreadResult | null;
  spreadHistory: TarotSpreadHistoryResponse | null;
  onSelectSpread: (spread: Spread) => void;
  onCardsSelected: (cards: Array<{ card: TarotCard; orientation: "upright" | "reversed" }>) => void;
  onCloseSpread: () => void;
  onSelectHistorySpread: (spread: TarotSpreadResult) => void;
}

export function SpreadSelection({
  spreads,
  selectedSpread,
  loadingDeck,
  deckCards,
  currentSpread,
  spreadHistory,
  onSelectSpread,
  onCardsSelected,
  onCloseSpread,
  onSelectHistorySpread,
}: SpreadSelectionProps) {
  return (
    <section className="orbit-hero-content-block">
      <div className="orbit-hero-content-container">
        <div className="orbit-card" style={{ background: "rgba(255, 255, 255, 0.95)", boxShadow: "0 4px 16px rgba(0, 0, 0, 0.08)" }}>
          <h2 className="orbit-display-sm" style={{ marginBottom: "var(--orbit-space-lg)" }}>
            Расклад
          </h2>
          
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "var(--orbit-space-md)", marginBottom: "var(--orbit-space-lg)" }}>
            {spreads.map(spread => (
              <button
                key={spread.id}
                onClick={() => onSelectSpread(spread)}
                disabled={loadingDeck}
                className="orbit-button orbit-button-secondary"
                style={{ 
                  padding: "var(--orbit-space-md)", 
                  textAlign: "left",
                  display: "flex",
                  flexDirection: "column",
                  gap: "var(--orbit-space-xs)",
                  alignItems: "flex-start",
                  transition: "transform 0.2s ease, box-shadow 0.2s ease",
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = "translateY(-2px)";
                  e.currentTarget.style.boxShadow = "0 4px 12px rgba(0, 0, 0, 0.15)";
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = "translateY(0)";
                  e.currentTarget.style.boxShadow = "none";
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: "var(--orbit-space-xs)", width: "100%" }}>
                  <span style={{ fontSize: "1.5rem" }}>{spread.icon}</span>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: 600, marginBottom: "2px" }}>{spread.title}</div>
                    <div style={{ fontSize: "0.75rem", opacity: 0.7 }}>{spread.cards} карт</div>
                  </div>
                </div>
                <div style={{ fontSize: "0.875rem", opacity: 0.8, textAlign: "left", width: "100%" }}>
                  {spread.description}
                </div>
              </button>
            ))}
          </div>

          {/* Интерактивная колода для выбора карт */}
          {selectedSpread && (
            <div style={{ marginTop: "var(--orbit-space-lg)" }}>
              {loadingDeck ? (
                <div style={{ 
                  display: "flex", 
                  flexDirection: "column",
                  alignItems: "center",
                  justifyContent: "center", 
                  padding: "var(--orbit-space-xl)",
                  gap: "var(--orbit-space-md)"
                }}>
                  <LoadingSpinner size="md" />
                  <p className="orbit-body-sm orbit-text-muted">Колода…</p>
                </div>
              ) : deckCards.length > 0 ? (
                <InteractiveCardDeck
                  cards={deckCards}
                  requiredCount={selectedSpread.cards}
                  onCardsSelected={onCardsSelected}
                  spreadTitle={selectedSpread.title}
                />
              ) : null}

              {/* Кнопка возврата к выбору расклада */}
              <div style={{ marginTop: "var(--orbit-space-lg)", textAlign: "center" }}>
                <button
                  onClick={onCloseSpread}
                  className="orbit-button orbit-button-secondary"
                >
                  ← Другой тип
                </button>
              </div>
            </div>
          )}

          {currentSpread && (
            <div 
              id="generated-spread"
              style={{ 
                marginTop: "var(--orbit-space-xl)", 
                borderTop: "1px solid var(--orbit-color-border)", 
                paddingTop: "var(--orbit-space-lg)",
                animation: "fadeIn 0.5s ease"
              }}
            >
              <style jsx>{`
                @keyframes fadeIn {
                  from {
                    opacity: 0;
                    transform: translateY(10px);
                  }
                  to {
                    opacity: 1;
                    transform: translateY(0);
                  }
                }
              `}</style>
              <TarotSpread spread={currentSpread} onClose={onCloseSpread} />
            </div>
          )}

          {spreadHistory && spreadHistory.history.length > 0 && (
            <div style={{ marginTop: "var(--orbit-space-xl)", borderTop: "1px solid var(--orbit-color-border)", paddingTop: "var(--orbit-space-lg)" }}>
              <h3 className="orbit-display-xs" style={{ marginBottom: "var(--orbit-space-md)" }}>
                Недавние
              </h3>
              <div style={{ display: "flex", flexDirection: "column", gap: "var(--orbit-space-md)" }}>
                {spreadHistory.history.slice(0, 5).map((record, idx) => (
                  <div
                    key={idx}
                    onClick={() => onSelectHistorySpread(record.spread)}
                    style={{
                      padding: "var(--orbit-space-md)",
                      border: "1px solid var(--orbit-color-border)",
                      borderRadius: "var(--orbit-radius-sm)",
                      cursor: "pointer",
                      transition: "background 0.2s ease",
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.background = "var(--orbit-color-mist)";
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.background = "transparent";
                    }}
                  >
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "start" }}>
                      <div>
                        <p className="orbit-body" style={{ fontWeight: 600 }}>{record.spread.title}</p>
                        <p className="orbit-body-sm orbit-text-muted">{record.draw_date}</p>
                      </div>
                      <span className="orbit-badge-xs">{record.spread.cards.length} карт</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}

