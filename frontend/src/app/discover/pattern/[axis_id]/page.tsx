"use client";

import { Suspense } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { DsButton } from "@/design-system";
import { ProductPageScreen } from "@/components/product-ui/ProductPageScreen";
import pl from "@/design-system/layouts/productPageLayout.module.css";
import v2 from "@/design-system/layouts/productV2Surface.module.css";
import { useDashboardData } from "@/hooks/useDashboardData";
import { buildAuthHref } from "@/lib/authRedirect";
import { useAuth } from "@/lib/useAuth";

export default function PatternDetailPage() {
  return (
    <Suspense
      fallback={
        <ProductPageScreen testId="discover-pattern-page" title="Паттерн" loading loadingLabel="Загрузка…" />
      }
    >
      <PatternDetailContent />
    </Suspense>
  );
}

function PatternDetailContent() {
  const params = useParams();
  const router = useRouter();
  const axisId = typeof params?.axis_id === "string" ? params.axis_id : null;
  const { isAuthenticated } = useAuth();
  const { data, loading } = useDashboardData();

  if (!isAuthenticated) {
    router.push(buildAuthHref("login", axisId ? `/discover/pattern/${axisId}` : "/discover"));
    return (
      <ProductPageScreen testId="discover-pattern-page" title="Паттерн" loading loadingLabel="Перенаправление…" />
    );
  }

  if (loading) {
    return (
      <ProductPageScreen testId="discover-pattern-page" title="Паттерн" loading loadingLabel="Загрузка…" />
    );
  }

  const axisNames: Record<string, string> = {
    A1: "Ориентация идентичности",
    A2: "Эмоциональная обработка",
    A3: "Принятие решений",
    A4: "Стабильность и изменения",
    A5: "Ориентация контроля",
    A6: "Реляционная ориентация",
    A7: "Управление энергией",
  };

  if (!axisId) {
    return (
      <ProductPageScreen testId="discover-pattern-page" title="Паттерн" contentClassName={`${pl.content} ${pl.legacyHost}`}>
        <section className={pl.panel} style={{ textAlign: "center" }}>
          <p className="orbit-body-sm orbit-text-muted">Неверный идентификатор паттерна</p>
          <div style={{ marginTop: "1rem" }}>
            <DsButton href="/discover">Вернуться к карте →</DsButton>
          </div>
        </section>
      </ProductPageScreen>
    );
  }

  if (!data.liteReport?.internal_model?.axes) {
    return (
      <ProductPageScreen testId="discover-pattern-page" title="Паттерн" contentClassName={`${pl.content} ${pl.legacyHost}`}>
        <section className={pl.panel} style={{ textAlign: "center" }}>
          <p className="orbit-body-sm orbit-text-muted">Паттерн не найден</p>
          <div style={{ marginTop: "1rem" }}>
            <DsButton href="/discover">Вернуться к карте →</DsButton>
          </div>
        </section>
      </ProductPageScreen>
    );
  }

  const axis = data.liteReport.internal_model.axes.find((a) => a.axis_id === axisId);

  if (!axis) {
    return (
      <ProductPageScreen testId="discover-pattern-page" title="Паттерн" contentClassName={`${pl.content} ${pl.legacyHost}`}>
        <section className={pl.panel} style={{ textAlign: "center" }}>
          <p className="orbit-body-sm orbit-text-muted">Паттерн не найден</p>
          <div style={{ marginTop: "1rem" }}>
            <DsButton href="/discover">Вернуться к карте →</DsButton>
          </div>
        </section>
      </ProductPageScreen>
    );
  }

  const axisName = axisNames[axisId] || axisId;
  const strength = Math.abs(axis.value);
  const isPositive = axis.value > 0;

  const getPatternDescription = () => {
    if (!data.liteReport?.paragraphs || !Array.isArray(data.liteReport.paragraphs)) {
      return null;
    }
    const patternParagraphs = data.liteReport.paragraphs.filter(
      (p) => p.section === "emotional_patterns" || p.section === "core_personality",
    );
    const relevantParagraph = patternParagraphs.find((p) => p.text && p.text.length > 0);
    return relevantParagraph?.text ?? null;
  };

  const description = getPatternDescription();

  const allParagraphs = (data.liteReport?.paragraphs || []).filter(
    (p) =>
      (p.section === "emotional_patterns" ||
        p.section === "core_personality" ||
        p.section === "relationships" ||
        p.section === "career" ||
        p.section === "money") &&
      p.text &&
      p.text.length > 0,
  );

  const strengthLabel =
    strength > 0.7 ? "Сильно выражен" : strength > 0.4 ? "Умеренно выражен" : "Слабо выражен";

  return (
    <ProductPageScreen
      testId="discover-pattern-page"
      title={axisName}
      subtitle={strengthLabel}
      contentClassName={`${pl.content} ${pl.legacyHost}`}
    >
      <Link href="/discover" className={pl.textLink}>
        ← Вернуться к карте
      </Link>

      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: "var(--orbit-space-md)",
          marginBottom: "var(--orbit-space-lg)",
        }}
      >
        <div
          style={{
            width: "200px",
            height: "6px",
            background: "#e5e0d8",
            borderRadius: "3px",
            overflow: "hidden",
          }}
        >
          <div
            style={{
              width: `${strength * 100}%`,
              height: "100%",
              background: isPositive ? "#b87333" : "#6b7280",
            }}
          />
        </div>
        <span className="orbit-body-sm" style={{ color: "#6b7280" }}>
          {strengthLabel}
        </span>
      </div>

      {description ? (
        <section className={pl.panel}>
          <h2 className={v2.sectionTitle}>О паттерне</h2>
          <p className="orbit-body" style={{ lineHeight: 1.7, color: "#334155", marginTop: "0.75rem" }}>
            {description}
          </p>
        </section>
      ) : null}

      {allParagraphs.length > 0 ? (
        <section className={pl.panel}>
          <h2 className={v2.sectionTitle}>Как это проявляется</h2>
          <div style={{ display: "flex", flexDirection: "column", gap: "var(--orbit-space-md)", marginTop: "1rem" }}>
            {allParagraphs.map((paragraph, index) => (
              <article key={index} className="orbit-card" style={{ padding: "var(--orbit-space-lg)" }}>
                <p className="orbit-body" style={{ lineHeight: 1.7, color: "#334155" }}>
                  {paragraph.text}
                </p>
                {paragraph.section ? (
                  <p className="orbit-body-xs orbit-text-muted" style={{ marginTop: "var(--orbit-space-sm)" }}>
                    {paragraph.section === "emotional_patterns" && "Эмоциональные паттерны"}
                    {paragraph.section === "core_personality" && "Ядро личности"}
                    {paragraph.section === "relationships" && "Отношения"}
                    {paragraph.section === "career" && "Карьера и ответственность"}
                    {paragraph.section === "money" && "Деньги и безопасность"}
                  </p>
                ) : null}
              </article>
            ))}
          </div>
        </section>
      ) : null}

      <section className={pl.panel} style={{ textAlign: "center" }}>
        <p className="orbit-body" style={{ marginBottom: "var(--orbit-space-md)", color: "#334155" }}>
          Как этот паттерн проявляется сегодня?
        </p>
        <DsButton href="/today">Перейти в «Я сегодня» →</DsButton>
      </section>
    </ProductPageScreen>
  );
}
