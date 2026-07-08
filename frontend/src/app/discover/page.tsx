"use client";

import { PROFILE_CHART_DEEP_PATH } from "@/lib/profileRoutes";
import Link from "next/link";
import { Suspense } from "react";
import { DsBody, DsButton } from "@/design-system";
import { ProductPageScreen } from "@/components/product-ui/ProductPageScreen";
import pl from "@/design-system/layouts/productPageLayout.module.css";
import v2 from "@/design-system/layouts/productV2Surface.module.css";
import { useDashboardData } from "@/hooks/useDashboardData";
import { useAuth } from "@/lib/useAuth";

type AxisSummary = {
  axis_id: string;
  value: number;
};

const AXIS_TITLE: Record<string, string> = {
  A1: "Идентичность",
  A2: "Эмоции",
  A3: "Решения",
  A4: "Изменения",
  A5: "Контроль",
  A6: "Отношения",
  A7: "Энергия",
};

const LIFE_DOMAINS = [
  {
    id: "love",
    title: "Любовь и близость",
    description: "Смотри совместимость, сценарий отношений и то, как ты входишь в близкий контакт.",
    href: "/compatibility",
    cta: "Открыть совместимость",
  },
  {
    id: "career",
    title: "Карьера и реализация",
    description: "Здесь важны твой способ проявляться, рабочий ритм и то, как твое ядро раскрывается в работе и реализации.",
    href: "/profile",
    cta: "Открыть профиль",
  },
  {
    id: "money",
    title: "Деньги и устойчивость",
    description: "Деньги лучше читать через свою карту: сильные стороны, устойчивость, привычные ошибки и реальные способы роста.",
    href: "/profile",
    cta: "Открыть профиль",
  },
  {
    id: "family",
    title: "Круг людей и связи",
    description: "Добавляй важных людей из своего круга, сохраняй их профили и переходи к персональной совместимости.",
    href: "/account/profiles",
    cta: "Открыть круг людей",
  },
  {
    id: "life-path",
    title: "Личный путь",
    description: "Основная карта человека живет в профиле и натальной карте: там твое ядро, дома и ориентиры.",
    href: "/profile",
    cta: "Вернуться к профилю",
  },
];

function getDominantAxes(axes: AxisSummary[]): AxisSummary[] {
  return [...axes].sort((a, b) => Math.abs(b.value) - Math.abs(a.value)).slice(0, 3);
}

export default function DiscoverPage() {
  return (
    <Suspense fallback={<ProductPageScreen testId="discover-page" title="Карта ориентиров" loading />}>
      <DiscoverContent />
    </Suspense>
  );
}

function DiscoverContent() {
  const { isAuthenticated } = useAuth();
  const { data, loading } = useDashboardData();

  if (!isAuthenticated) {
    return (
      <ProductPageScreen
        testId="discover-page"
        eyebrow="Карта ориентиров"
        title="Сначала собери личное ядро"
        subtitle="Эта страница помогает понять, куда идти дальше: в личную карту, совместимость и разбор паттернов."
        contentClassName={pl.content}
      >
        <div style={{ display: "flex", gap: "0.65rem", flexWrap: "wrap" }}>
          <DsButton href="/onboarding/core">Собрать профиль</DsButton>
          <DsButton href="/today" variant="secondary">
            Открыть Today
          </DsButton>
        </div>
      </ProductPageScreen>
    );
  }

  if (loading) {
    return (
      <ProductPageScreen testId="discover-page" title="Карта ориентиров" loading loadingLabel="Загрузка…" />
    );
  }

  const axes = (data.liteReport?.internal_model?.axes || []) as AxisSummary[];
  const dominantAxes = getDominantAxes(axes);

  return (
    <ProductPageScreen
      testId="discover-page"
      eyebrow="Карта ориентиров"
      title="Дальше двигайся от своего ядра"
      subtitle="Личная карта уже собрана в профиле и натальной карте. Здесь — навигация по смысловым слоям."
      contentClassName={`${pl.content} ${pl.legacyHost}`}
    >
      <div style={{ display: "flex", gap: "0.65rem", flexWrap: "wrap" }}>
        <DsButton href="/profile" variant="secondary" size="sm">
          Открыть профиль
        </DsButton>
        <DsButton href={PROFILE_CHART_DEEP_PATH} variant="secondary" size="sm">
          Натальная карта
        </DsButton>
        <DsButton href="/today" variant="secondary" size="sm">
          Я сегодня
        </DsButton>
        <DsButton href="/tarot/card-of-the-day" variant="secondary" size="sm">
          Карта дня
        </DsButton>
      </div>

      {dominantAxes.length > 0 ? (
        <section className={pl.panel}>
          <p className={v2.eyebrow}>Твои ведущие паттерны</p>
          <h2 className={v2.sectionTitle}>Начни с самых выраженных осей</h2>
          <DsBody size="sm" muted className={pl.bodyMtSm}>
            Быстрый вход в точечный разбор того, что в тебе звучит сильнее всего.
          </DsBody>
          <div className={pl.gridHub} style={{ marginTop: "1rem" }}>
            {dominantAxes.map((axis) => (
              <Link key={axis.axis_id} href={`/discover/pattern/${axis.axis_id}`} className={pl.hubCard}>
                <DsBody size="sm" muted>
                  Разбор оси
                </DsBody>
                <span className={pl.hubCardTitle}>{AXIS_TITLE[axis.axis_id] || axis.axis_id}</span>
                <DsBody size="sm" muted>
                  Сила проявления: {Math.round(Math.abs(axis.value) * 100)}%
                </DsBody>
              </Link>
            ))}
          </div>
        </section>
      ) : null}

      <section className={pl.panel}>
        <p className={v2.eyebrow}>Сферы жизни</p>
        <h2 className={v2.sectionTitle}>Открывай нужный слой без поисков по меню</h2>
        <DsBody size="sm" muted className={pl.bodyMtSm}>
          Здесь собраны только направления. Полный смысл живет в профиле, натальной карте, прогнозах и совместимости.
        </DsBody>
        <div className={pl.gridHub} style={{ marginTop: "1rem" }}>
          {LIFE_DOMAINS.map((domain) => (
            <article key={domain.id} id={domain.id} className={pl.hubCard}>
              <span className={pl.hubCardTitle}>{domain.title}</span>
              <DsBody size="sm" muted className={pl.bodyMtSm}>
                {domain.description}
              </DsBody>
              <div style={{ marginTop: "0.75rem" }}>
                <DsButton href={domain.href} variant="secondary" size="sm">
                  {domain.cta}
                </DsButton>
              </div>
            </article>
          ))}
        </div>
      </section>
    </ProductPageScreen>
  );
}
