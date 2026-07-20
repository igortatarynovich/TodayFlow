"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { LoadingSpinner } from "@/components/orbit";
import { FlippableInfoCard } from "@/components/tarot/FlippableInfoCard";
import { TarotCardBack } from "@/components/tarot/TarotCardBack";
import { getJson } from "@/lib/api";
import type { MoonPhaseResponse, TarotDailyDraw } from "@/lib/types";

interface DailyCardPreviewProps {
  isAuthenticated?: boolean;
  compact?: boolean;
}

export function DailyCardPreview({ isAuthenticated = false, compact = false }: DailyCardPreviewProps) {
  const [moonPhase, setMoonPhase] = useState<MoonPhaseResponse | null>(null);
  const [tarotCard, setTarotCard] = useState<TarotDailyDraw | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Do not fetch card-of-day identity here — public daily is gated not_selected.
        const moon = await getJson<MoonPhaseResponse>("/celestial/moon-phase").catch(() => null);
        setMoonPhase(moon);
        setTarotCard({
          date: new Date().toISOString().slice(0, 10),
          selection_status: "not_selected",
          card: null,
        });
      } catch (err) {
        console.error("Error fetching daily card:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const getMoonEmoji = (phaseId: string) => {
    const emojiMap: Record<string, string> = {
      new_moon: "🌑",
      waxing_crescent: "🌒",
      first_quarter: "🌓",
      waxing_gibbous: "🌔",
      full_moon: "🌕",
      waning_gibbous: "🌖",
      last_quarter: "🌗",
      waning_crescent: "🌘",
    };
    return emojiMap[phaseId] || "🌙";
  };

  if (loading) {
    return (
      <div style={{ display: "flex", justifyContent: "center", alignItems: "center", minHeight: "200px" }}>
        <LoadingSpinner size="sm" />
      </div>
    );
  }

  if (compact) {
    // Компактная версия для главной страницы
    return (
      <div 
        className="daily-cards-preview"
        style={{
          display: "flex",
          justifyContent: "center",
          gap: "var(--orbit-space-xl)",
          flexWrap: "wrap",
          maxWidth: "900px",
          margin: "0 auto",
        }}
      >
        {/* Астрология */}
        <div style={{ transform: "scale(0.75)", transformOrigin: "center" }}>
          <FlippableInfoCard
            title=""
            backLabel="Астрология"
            icon={moonPhase ? getMoonEmoji(moonPhase.current.id) : "🌙"}
            frontContent={
              moonPhase ? (
                <div style={{ textAlign: "center", padding: "var(--orbit-space-xs)" }}>
                  <div style={{ fontSize: "1.5rem", marginBottom: "var(--orbit-space-xs)" }}>
                    {getMoonEmoji(moonPhase.current.id)}
                  </div>
                  <p style={{ fontSize: "0.7rem", fontWeight: 600, marginBottom: "var(--orbit-space-xs)" }}>
                    {moonPhase.current.name}
                  </p>
                  <p style={{ fontSize: "0.65rem", color: "var(--orbit-color-slate)", opacity: 0.7 }}>
                    {moonPhase.current.themes?.split(",")[0]}
                  </p>
                </div>
              ) : (
                <div style={{ textAlign: "center", padding: "var(--orbit-space-xs)" }}>
                  <p style={{ fontSize: "0.7rem", color: "var(--orbit-color-slate)", opacity: 0.6 }}>
                    Загрузка...
                  </p>
                </div>
              )
            }
            backContent={
              <div style={{ textAlign: "center", padding: "var(--orbit-space-xs)" }}>
                <Link 
                  href="/today" 
                  className="orbit-button orbit-button-secondary orbit-button-xs"
                  style={{ width: "100%" }}
                  onClick={(e) => e.stopPropagation()}
                >
                  Открыть →
                </Link>
              </div>
            }
          />
        </div>

        {/* Аффирмация */}
        <div style={{ transform: "scale(0.75)", transformOrigin: "center" }}>
          <FlippableInfoCard
            title=""
            backLabel="Аффирмация"
            icon="🧘"
            frontContent={
              <div style={{ textAlign: "center", padding: "var(--orbit-space-xs)" }}>
                <p style={{ fontSize: "0.7rem", fontWeight: 600, marginBottom: "var(--orbit-space-xs)", lineHeight: 1.35, color: "var(--orbit-color-slate)" }}>
                  Аффирмация дня
                </p>
                <p style={{ fontSize: "0.65rem", lineHeight: 1.4, color: "var(--orbit-color-slate)", opacity: 0.85 }}>
                  Появится после того, как ты откроешь карту дня в Today — здесь без спойлеров.
                </p>
              </div>
            }
            backContent={
              <div style={{ textAlign: "center", padding: "var(--orbit-space-xs)" }}>
                <Link 
                  href="/today" 
                  className="orbit-button orbit-button-secondary orbit-button-xs"
                  style={{ width: "100%" }}
                  onClick={(e) => e.stopPropagation()}
                >
                  Открыть →
                </Link>
              </div>
            }
          />
        </div>

        {/* Таро */}
        <div style={{ transform: "scale(0.75)", transformOrigin: "center" }}>
          <FlippableInfoCard
            title=""
            backLabel="Таро"
            icon="🔮"
            isTarotCard={true}
            tarotCardBack={<TarotCardBack widthPx={72} />}
            frontContent={
              <div
                style={{
                  display: "flex",
                  flexDirection: "column",
                  alignItems: "center",
                  justifyContent: "center",
                  flex: 1,
                  padding: "var(--orbit-space-xs)",
                  gap: "var(--orbit-space-xs)",
                }}
              >
                <div style={{ width: "72px", height: "112px" }}>
                  <TarotCardBack widthPx={72} />
                </div>
                <p style={{ fontSize: "0.65rem", textAlign: "center", lineHeight: 1.35, color: "var(--orbit-color-slate)", margin: 0, opacity: 0.9 }}>
                  {tarotCard?.card ? "Открой в Today, чтобы увидеть аркан." : "Карта дня скоро."}
                </p>
              </div>
            }
            backContent={
              <div style={{ textAlign: "center", padding: "var(--orbit-space-xs)" }}>
                <Link 
                  href="/today" 
                  className="orbit-button orbit-button-secondary orbit-button-xs"
                  style={{ width: "100%" }}
                  onClick={(e) => e.stopPropagation()}
                >
                  Открыть →
                </Link>
              </div>
            }
          />
        </div>
      </div>
    );
  }

  // Полная версия (можно использовать позже)
  return null;
}
