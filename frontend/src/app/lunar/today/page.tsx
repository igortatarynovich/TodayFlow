"use client";

import Link from "next/link";
import { useState, useEffect } from "react";
import { DsBody, DsButton } from "@/design-system";
import { ProductPageScreen } from "@/components/product-ui/ProductPageScreen";
import pl from "@/design-system/layouts/productPageLayout.module.css";
import v2 from "@/design-system/layouts/productV2Surface.module.css";
import { PROFILE_CHART_DEEP_PATH } from "@/lib/profileRoutes";

type MoonPhaseResponse = {
  current: {
    id: string;
    name: string;
    themes: string;
    guidance: string;
    keywords: string[];
  };
  next_phase?: {
    name: string;
    date: string;
    in_days: number;
  };
};

export default function LunarTodayPage() {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<MoonPhaseResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadMoonPhase = async () => {
      try {
        const { getJson } = await import("@/lib/api");
        const response = await getJson<MoonPhaseResponse>("/celestial/moon-phase");
        setData(response);
      } catch (err) {
        console.error("Failed to load moon phase", err);
        setError("Не удалось загрузить данные о луне");
      } finally {
        setLoading(false);
      }
    };

    void loadMoonPhase();
  }, []);

  const dateLabel = new Date().toLocaleDateString("ru-RU", {
    weekday: "long",
    year: "numeric",
    month: "long",
    day: "numeric",
  });

  if (loading) {
    return (
      <ProductPageScreen testId="lunar-today-page" title="Луна сегодня" loading loadingLabel="Загрузка…" />
    );
  }

  if (error || !data) {
    return (
      <ProductPageScreen testId="lunar-today-page" title={error || "Ошибка загрузки"} contentClassName={pl.content}>
        <DsButton href="/today" variant="secondary">
          Вернуться на главную
        </DsButton>
      </ProductPageScreen>
    );
  }

  const themeLines = (data.current.themes || "")
    .split(/[.;]/)
    .map((line) => line.trim())
    .filter(Boolean);

  return (
    <ProductPageScreen
      testId="lunar-today-page"
      title="Луна сегодня"
      subtitle={dateLabel}
      contentClassName={pl.content}
    >
      <section className={pl.panel} style={{ textAlign: "center" }}>
        <div
          aria-hidden
          style={{
            width: "7.5rem",
            height: "7.5rem",
            margin: "0 auto 1rem",
            borderRadius: "50%",
            background: 'url("/images/cosmic/moon_cutout.webp") center / cover no-repeat',
            boxShadow: "0 12px 32px rgba(42, 37, 32, 0.14)",
          }}
        />
        <h2 className={v2.sectionTitle}>{data.current.name}</h2>
        <DsBody size="sm" muted className={pl.bodyMtSm}>
          Фаза: {data.current.id}
        </DsBody>
        <DsBody className={pl.bodyMtLg}>{data.current.guidance}</DsBody>
      </section>

      <div className={pl.grid2}>
        <section className={pl.panel}>
          <h3 className={v2.sectionTitle}>Темы фазы</h3>
          <ul className={pl.formStack} style={{ marginTop: "0.75rem", listStyle: "none", padding: 0 }}>
            {themeLines.map((item, index) => (
              <li key={index}>
                <DsBody size="sm">✓ {item}</DsBody>
              </li>
            ))}
          </ul>
        </section>

        <section className={pl.panel}>
          <h3 className={v2.sectionTitle}>Ключевые слова</h3>
          <ul className={pl.formStack} style={{ marginTop: "0.75rem", listStyle: "none", padding: 0 }}>
            {(data.current.keywords || []).map((item, index) => (
              <li key={index}>
                <DsBody size="sm">• {item}</DsBody>
              </li>
            ))}
          </ul>
        </section>
      </div>

      {data.next_phase ? (
        <section className={pl.panel}>
          <DsBody size="sm">
            Следующая фаза: <strong>{data.next_phase.name}</strong> (
            {new Date(data.next_phase.date).toLocaleDateString("ru-RU")}, через{" "}
            {Math.round(data.next_phase.in_days)} дн.)
          </DsBody>
        </section>
      ) : null}

      <section className={pl.panel}>
        <DsBody className={pl.bodyMbMd}>
          Хочешь персональные рекомендации на основе твоей натальной карты?
        </DsBody>
        <DsButton href="/onboarding/core">Открыть в приложении</DsButton>
      </section>

      <section>
        <h2 className={v2.sectionTitle}>Также интересно</h2>
        <div className={pl.gridHub} style={{ marginTop: "0.75rem" }}>
          <Link href="/today" className={pl.hubCard}>
            <DsBody size="sm">Карта таро дня</DsBody>
          </Link>
          <Link href="/horoscope/today" className={pl.hubCard}>
            <DsBody size="sm">Гороскоп сегодня</DsBody>
          </Link>
          <Link href={PROFILE_CHART_DEEP_PATH} className={pl.hubCard}>
            <DsBody size="sm">Натальная карта</DsBody>
          </Link>
        </div>
      </section>
    </ProductPageScreen>
  );
}
