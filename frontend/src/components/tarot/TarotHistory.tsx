"use client";

import { CardVisual } from "./CardVisual";
import type { TarotDailyDraw } from "@/lib/types";

interface TarotHistoryProps {
  history: TarotDailyDraw[];
  filteredHistory: TarotDailyDraw[];
  favorites: number[];
  filterOrientation: "all" | "upright" | "reversed";
  filterCardName: string;
  filterDateFrom: string;
  filterDateTo: string;
  onToggleFavorite: (cardId: number) => void;
  onExportHistory: () => void;
  onFilterOrientationChange: (value: "all" | "upright" | "reversed") => void;
  onFilterCardNameChange: (value: string) => void;
  onFilterDateFromChange: (value: string) => void;
  onFilterDateToChange: (value: string) => void;
}

export function TarotHistory({
  history,
  filteredHistory,
  favorites,
  filterOrientation,
  filterCardName,
  filterDateFrom,
  filterDateTo,
  onToggleFavorite,
  onExportHistory,
  onFilterOrientationChange,
  onFilterCardNameChange,
  onFilterDateFromChange,
  onFilterDateToChange,
}: TarotHistoryProps) {
  if (history.length === 0) return null;

  return (
    <section className="orbit-hero-content-block">
      <div className="orbit-hero-content-container">
        <div className="orbit-card" style={{ background: "rgba(255, 255, 255, 0.95)", boxShadow: "0 4px 16px rgba(0, 0, 0, 0.08)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "start", marginBottom: "var(--orbit-space-lg)" }}>
            <h2 className="orbit-display-sm">История карт</h2>
            <button onClick={onExportHistory} className="orbit-button orbit-button-xs orbit-button-ghost">
              Экспорт CSV
            </button>
          </div>

          {/* Фильтры */}
          <div style={{ 
            display: "grid", 
            gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))", 
            gap: "var(--orbit-space-md)",
            marginBottom: "var(--orbit-space-lg)",
            padding: "var(--orbit-space-md)",
            background: "var(--orbit-color-mist)",
            borderRadius: "var(--orbit-radius-sm)"
          }}>
            <div>
              <label className="orbit-body-xs" style={{ display: "block", marginBottom: "var(--orbit-space-xs)" }}>
                Ориентация
              </label>
              <select
                value={filterOrientation}
                onChange={(e) => onFilterOrientationChange(e.target.value as "all" | "upright" | "reversed")}
                className="orbit-form"
                style={{ width: "100%", padding: "var(--orbit-space-xs)" }}
              >
                <option value="all">Все</option>
                <option value="upright">Прямые</option>
                <option value="reversed">Перевернутые</option>
              </select>
            </div>
            <div>
              <label className="orbit-body-xs" style={{ display: "block", marginBottom: "var(--orbit-space-xs)" }}>
                Название карты
              </label>
              <input
                type="text"
                value={filterCardName}
                onChange={(e) => onFilterCardNameChange(e.target.value)}
                placeholder="Поиск..."
                className="orbit-form"
                style={{ width: "100%", padding: "var(--orbit-space-xs)" }}
              />
            </div>
            <div>
              <label className="orbit-body-xs" style={{ display: "block", marginBottom: "var(--orbit-space-xs)" }}>
                От даты
              </label>
              <input
                type="date"
                value={filterDateFrom}
                onChange={(e) => onFilterDateFromChange(e.target.value)}
                className="orbit-form"
                style={{ width: "100%", padding: "var(--orbit-space-xs)" }}
              />
            </div>
            <div>
              <label className="orbit-body-xs" style={{ display: "block", marginBottom: "var(--orbit-space-xs)" }}>
                До даты
              </label>
              <input
                type="date"
                value={filterDateTo}
                onChange={(e) => onFilterDateToChange(e.target.value)}
                className="orbit-form"
                style={{ width: "100%", padding: "var(--orbit-space-xs)" }}
              />
            </div>
          </div>

          <div style={{ marginTop: "var(--orbit-space-md)", display: "flex", flexDirection: "column", gap: "var(--orbit-space-md)" }}>
            {filteredHistory.length === 0 ? (
              <p className="orbit-body-sm orbit-text-muted" style={{ textAlign: "center", padding: "var(--orbit-space-xl)" }}>
                Нет карт, соответствующих фильтрам
              </p>
            ) : (
              filteredHistory
                .filter((draw): draw is TarotDailyDraw & { card: NonNullable<TarotDailyDraw["card"]> } => Boolean(draw.card))
                .map((draw, idx) => (
                <div key={idx} style={{ 
                  padding: "var(--orbit-space-md)",
                  border: "1px solid var(--orbit-color-border)",
                  borderRadius: "var(--orbit-radius-sm)",
                  display: "flex",
                  gap: "var(--orbit-space-md)",
                  alignItems: "start"
                }}>
                  <CardVisual 
                    card={draw.card} 
                    orientation={draw.orientation as "upright" | "reversed"} 
                    size="sm"
                    showName={false}
                  />
                  <div style={{ flex: 1 }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "start", marginBottom: "var(--orbit-space-xs)" }}>
                      <div>
                        <h3 className="orbit-body" style={{ fontWeight: 600 }}>{draw.card.name}</h3>
                        <span className="orbit-body-sm orbit-text-muted">{draw.date}</span>
                      </div>
                      <div style={{ display: "flex", gap: "var(--orbit-space-xs)", alignItems: "center" }}>
                        <span className="orbit-badge-xs">{draw.orientation === "upright" ? "Прямая" : "Перевернутая"}</span>
                        <button
                          onClick={() => onToggleFavorite(draw.card.id)}
                          style={{
                            background: "none",
                            border: "none",
                            cursor: "pointer",
                            fontSize: "18px",
                            color: favorites.includes(draw.card.id) ? "var(--orbit-color-coral)" : "var(--orbit-color-slate)",
                            padding: "4px",
                          }}
                          title={favorites.includes(draw.card.id) ? "Удалить из избранного" : "Добавить в избранное"}
                        >
                          {favorites.includes(draw.card.id) ? "★" : "☆"}
                        </button>
                      </div>
                    </div>
                    <p className="orbit-body-sm orbit-text-muted" style={{ marginTop: "var(--orbit-space-xs)" }}>
                      {draw.orientation === "upright" ? draw.card.upright.substring(0, 150) + "..." : draw.card.reversed.substring(0, 150) + "..."}
                    </p>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </section>
  );
}

