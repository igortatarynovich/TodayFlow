"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { DsButton } from "@/design-system";
import { ProductPageScreen } from "@/components/product-ui/ProductPageScreen";
import pl from "@/design-system/layouts/productPageLayout.module.css";
import v2 from "@/design-system/layouts/productV2Surface.module.css";
import { getJson } from "@/lib/api";
import { useAuth } from "@/lib/useAuth";
import type { MeaningRingsResponse, ProfileBuildStatus, ProfileSummary } from "@/lib/types";
import { flushMeaningOutbox, getCachedMeaningRings, refreshMeaningRings } from "@/lib/meaningRuntime";

const MISSING_CORE_FIELD_LABEL_RU: Record<string, string> = {
  gender: "обращение в текстах на «ты»",
  first_name: "полное имя (нумерология имени)",
  astro_birth_date: "дата рождения",
  astro_birth_time: "время рождения (Асцендент и дома)",
  astro_location_name: "место рождения (для домов при известном времени)",
  numerology_life_path: "число жизненного пути (нумерология)",
};

function missingCoreFieldsSummaryRu(fields: string[]): string {
  return fields.map((f) => MISSING_CORE_FIELD_LABEL_RU[f] ?? f).join(", ");
}

export default function ProfileSummaryPage() {
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const [loading, setLoading] = useState(true);
  const [summary, setSummary] = useState<ProfileSummary | null>(null);
  const [buildStatus, setBuildStatus] = useState<ProfileBuildStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [rings, setRings] = useState<MeaningRingsResponse["rings"]>([]);

  useEffect(() => {
    if (!isAuthenticated) return;
    let cancelled = false;
    setLoading(true);
    Promise.all([
      getJson<ProfileSummary>("/account/profile-summary"),
      getJson<ProfileBuildStatus>("/account/profile-build-status"),
    ])
      .then(([s, status]) => {
        if (cancelled) return;
        setSummary(s);
        setBuildStatus(status);
        setError(null);
      })
      .catch((err) => {
        if (cancelled) return;
        setError(err instanceof Error ? err.message : "Не удалось загрузить сводку профиля.");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [isAuthenticated]);

  useEffect(() => {
    if (!isAuthenticated) return;
    const cached = getCachedMeaningRings();
    if (cached?.rings?.length) {
      setRings(cached.rings);
    }
    flushMeaningOutbox().catch(() => undefined);
    refreshMeaningRings(28)
      .then((payload) => {
        if (payload?.rings) setRings(payload.rings);
      })
      .catch(() => undefined);
  }, [isAuthenticated]);

  const headline = useMemo(() => {
    if (!summary) return "Твоя сводка профиля";
    const name = summary.display_name || "Твой профиль";
    return `${name}, вот твоя сводка`;
  }, [summary]);

  if (authLoading || loading) {
    return (
      <ProductPageScreen
        testId="profile-summary-page"
        title="Сводка профиля"
        loading
        loadingLabel="Загрузка…"
      />
    );
  }

  if (!isAuthenticated) {
    return (
      <ProductPageScreen
        testId="profile-summary-page"
        title="Сводка профиля"
        guest={{
          message: "Войди в аккаунт, чтобы открыть сводку профиля и перейти в Today.",
          ctaHref: "/auth",
          ctaLabel: "Войти",
        }}
      />
    );
  }

  if (error || !summary) {
    return (
      <ProductPageScreen
        testId="profile-summary-page"
        title="Не удалось открыть сводку"
        contentClassName={`${pl.content} ${pl.legacyHost}`}
      >
        <section className={pl.panel} style={{ textAlign: "center" }}>
          <p className="orbit-body" style={{ color: "#475569" }}>
            {error || "Попробуй еще раз через минуту."}
          </p>
          <div style={{ display: "flex", justifyContent: "center", gap: "0.75rem", flexWrap: "wrap", marginTop: "1rem" }}>
            <DsButton href="/profile" variant="secondary">
              Открыть профиль
            </DsButton>
            <DsButton href="/today">Перейти в Today</DsButton>
          </div>
        </section>
      </ProductPageScreen>
    );
  }

  const trio = summary.core_trio || {};
  const baseline = summary.baseline || {};

  return (
    <ProductPageScreen
      testId="profile-summary-page"
      title={headline}
      subtitle="Короткий срез перед основным днем: кто ты сейчас, что усиливать, куда идти дальше."
      contentClassName={`${pl.content} ${pl.legacyHost}`}
    >
      <section className={pl.panel}>
        <h2 className={v2.sectionTitle}>Core Trio</h2>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: "0.75rem", marginTop: "0.75rem" }}>
          <div className="orbit-card" style={{ padding: "0.75rem" }}>
            <p className="orbit-body-xs" style={{ margin: 0, color: "#6b7280" }}>Солнце</p>
            <p className="orbit-body" style={{ margin: "0.25rem 0 0", fontWeight: 700 }}>{trio.sun_sign || "Пока не определено"}</p>
          </div>
          <div className="orbit-card" style={{ padding: "0.75rem" }}>
            <p className="orbit-body-xs" style={{ margin: 0, color: "#6b7280" }}>Время рождения</p>
            <p className="orbit-body" style={{ margin: "0.25rem 0 0", fontWeight: 700 }}>
              {trio.birth_time_known == null ? "Не заполнено" : trio.birth_time_known ? "Известно" : "Неизвестно"}
            </p>
          </div>
          <div className="orbit-card" style={{ padding: "0.75rem" }}>
            <p className="orbit-body-xs" style={{ margin: 0, color: "#6b7280" }}>Число пути</p>
            <p className="orbit-body" style={{ margin: "0.25rem 0 0", fontWeight: 700 }}>{trio.life_path ?? "—"}</p>
          </div>
        </div>
      </section>

      <section className={pl.panel}>
        <h2 className={v2.sectionTitle}>Твоя базовая линия</h2>
        <ul style={{ margin: "0.75rem 0 0", paddingLeft: "1rem", color: "#334155" }}>
          <li>{baseline.archetype_seed || "Архетип пока формируется"}</li>
          <li>{baseline.element_focus || "Фокус элемента появится после уточнения профиля"}</li>
          <li>{baseline.rhythm_style || "Ритм дня уточнится после первых действий"}</li>
        </ul>
        {summary.living_summary ? (
          <p className="orbit-body-sm" style={{ marginTop: "0.75rem", color: "#5f4323" }}>
            {summary.living_summary}
          </p>
        ) : null}
      </section>

      <section className={pl.panel}>
        <h2 className={v2.sectionTitle}>Готовность профиля</h2>
        <p className="orbit-body-sm" style={{ margin: "0.75rem 0 0", color: "#334155" }}>
          {buildStatus?.status === "ready"
            ? "Профиль готов. Можно идти в Today."
            : buildStatus?.status === "building"
              ? "Профиль доуточняется в фоне. Не нужно ждать."
              : "Профиль в очереди на доуточнение. Продолжай без паузы."}
        </p>
        {summary.missing_fields?.length ? (
          <p className="orbit-body-xs" style={{ marginTop: "0.5rem", color: "#6b7280" }}>
            Следующий слой откроется, если добавить: {missingCoreFieldsSummaryRu(summary.missing_fields)}.
          </p>
        ) : null}
      </section>

      <section className={pl.panel}>
        <h2 className={v2.sectionTitle}>Rings of Alignment</h2>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))", gap: "0.75rem", marginTop: "0.75rem" }}>
          {(rings.length ? rings : Object.entries(summary.rings_preview || {}).map(([ring, score]) => ({
            ring,
            score,
            trend_7d: 0,
            confidence: "low",
          }))).map((ring) => (
            <div key={ring.ring} className="orbit-card" style={{ padding: "0.75rem" }}>
              <p className="orbit-body-xs" style={{ margin: 0, color: "#6b7280" }}>{ring.ring}</p>
              <p className="orbit-body" style={{ margin: "0.25rem 0 0", fontWeight: 700 }}>
                {ring.score}%
              </p>
            </div>
          ))}
        </div>
      </section>

      <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap" }}>
        <DsButton href="/today">Открыть Today</DsButton>
        <DsButton href="/tarot" variant="secondary">
          Открыть Таро
        </DsButton>
        <DsButton href="/profile" variant="secondary">
          Открыть профиль
        </DsButton>
      </div>
    </ProductPageScreen>
  );
}
