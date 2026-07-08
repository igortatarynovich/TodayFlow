"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useState, useEffect } from "react";
import { ApiError, getJson } from "@/lib/api";
import { ProductPageScreen } from "@/components/product-ui/ProductPageScreen";
import pl from "@/design-system/layouts/productPageLayout.module.css";
import { DsButton } from "@/design-system";
import type { TarotCard } from "@/lib/types";

const CARD_SLUGS: Record<string, number> = {
  "the-fool": 0,
  "the-magician": 1,
  "the-high-priestess": 2,
  "the-empress": 3,
  "the-emperor": 4,
  "the-hierophant": 5,
  "the-lovers": 6,
  "the-chariot": 7,
  "strength": 8,
  "the-hermit": 9,
  "wheel-of-fortune": 10,
  "justice": 11,
  "the-hanged-man": 12,
  "death": 13,
  "temperance": 14,
  "the-devil": 15,
  "the-tower": 16,
  "the-star": 17,
  "the-moon": 18,
  "the-sun": 19,
  "judgement": 20,
  "the-world": 21,
};

export default function TarotCardPage() {
  const params = useParams();
  const slug = params?.slug as string;
  const cardId = CARD_SLUGS[slug];

  const [loading, setLoading] = useState(true);
  const [card, setCard] = useState<TarotCard | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!slug || cardId === undefined) {
      setError("Карта не найдена");
      setLoading(false);
      return;
    }

    const loadCard = async () => {
      try {
        const response = await getJson<TarotCard>(`/tarot/cards/${cardId}`);
        setCard(response);
      } catch (err) {
        console.error("Failed to load card", err);
        if (err instanceof ApiError && err.status === 404) {
          setError("Карта не найдена");
        } else {
          setError("Не удалось загрузить карту. Проверь соединение и попробуй снова.");
        }
      } finally {
        setLoading(false);
      }
    };

    loadCard();
  }, [slug, cardId]);

  if (loading) {
    return (
      <ProductPageScreen
        testId="tarot-card-page"
        title="Карта Таро"
        loading
        loadingLabel="Загрузка карты…"
      />
    );
  }

  if (error || !card) {
    return (
      <ProductPageScreen
        testId="tarot-card-page"
        title={error || "Карта не найдена"}
        contentClassName={`${pl.content} ${pl.legacyHost}`}
      >
        <section className={pl.panel} style={{ textAlign: "center" }}>
          <Link href="/tarot/card-of-the-day">
            <DsButton variant="secondary">Вернуться к таро</DsButton>
          </Link>
        </section>
      </ProductPageScreen>
    );
  }

  return (
    <ProductPageScreen
      testId="tarot-card-page"
      title={card.name}
      contentClassName={`${pl.content} ${pl.legacyHost}`}
    >
      {card.keywords.length > 0 && (
        <div className="orbit-card" style={{ padding: "var(--orbit-space-lg)" }}>
          <h3 className="orbit-body" style={{ fontWeight: 500, marginBottom: "var(--orbit-space-md)" }}>
            Ключевые слова
          </h3>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "var(--orbit-space-sm)" }}>
            {card.keywords.map((keyword, index) => (
              <span
                key={index}
                style={{
                  padding: "var(--orbit-space-xs) var(--orbit-space-md)",
                  background: "#FAF9F7",
                  border: "1px solid var(--orbit-color-border)",
                  borderRadius: "var(--orbit-radius-capsule)",
                  fontSize: "0.875rem",
                  color: "#334155",
                }}
              >
                {keyword}
              </span>
            ))}
          </div>
        </div>
      )}

      <div className="orbit-card" style={{ padding: "var(--orbit-space-lg)" }}>
        <h3 className="orbit-body" style={{ fontWeight: 500, marginBottom: "var(--orbit-space-md)" }}>
          Прямое положение
        </h3>
        <p className="orbit-body-sm" style={{ color: "#334155", lineHeight: 1.7, margin: 0 }}>
          {card.upright}
        </p>
      </div>

      <div className="orbit-card" style={{ padding: "var(--orbit-space-lg)" }}>
        <h3 className="orbit-body" style={{ fontWeight: 500, marginBottom: "var(--orbit-space-md)" }}>
          Перевёрнутое положение
        </h3>
        <p className="orbit-body-sm" style={{ color: "#334155", lineHeight: 1.7, margin: 0 }}>
          {card.reversed}
        </p>
      </div>

      <section className={pl.panel} style={{ textAlign: "center" }}>
        <p className="orbit-body" style={{ lineHeight: 1.7, marginBottom: "var(--orbit-space-xl)", color: "#334155" }}>
          Хочешь получить персональное значение этой карты на основе твоей натальной карты?
        </p>
        <Link href="/today">
          <DsButton variant="primary">Открыть в приложении</DsButton>
        </Link>
      </section>

      <section>
        <h2 className="orbit-display-sm" style={{ textAlign: "center", marginBottom: "var(--orbit-space-xl)" }}>
          Также интересно
        </h2>
        <div className={pl.grid2}>
          <Link href="/tarot" className="orbit-card orbit-card-link" style={{ padding: "var(--orbit-space-lg)", textAlign: "center", textDecoration: "none" }}>
            <p className="orbit-body-sm" style={{ margin: 0, color: "#0f172a" }}>
              Разобраться с вопросом
            </p>
          </Link>
          <Link href="/tarot/card-of-the-day" className="orbit-card orbit-card-link" style={{ padding: "var(--orbit-space-lg)", textAlign: "center", textDecoration: "none" }}>
            <p className="orbit-body-sm" style={{ margin: 0, color: "#0f172a" }}>
              Карта дня
            </p>
          </Link>
        </div>
      </section>
    </ProductPageScreen>
  );
}
