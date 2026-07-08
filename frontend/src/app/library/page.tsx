"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { DsBody, DsButton } from "@/design-system";
import { ProductPageScreen } from "@/components/product-ui/ProductPageScreen";
import pl from "@/design-system/layouts/productPageLayout.module.css";
import { useAuth } from "@/lib/useAuth";
import { getJson, postJson } from "@/lib/api";
import { buildAuthHref } from "@/lib/authRedirect";
import { t } from "@/lib/i18n";

type SavedCalc = { calc_type: string; key: string; payload: Record<string, unknown> };

function parseForecastId(id: string): { date: string; locale: string } | null {
  const m = id.match(/^forecast-(.+)-([a-z]{2})$/);
  if (!m) return null;
  return { date: m[1], locale: m[2] };
}

function formatDate(d: string, locale: string) {
  const date = new Date(d + "T12:00:00");
  return date.toLocaleDateString(locale === "ru" ? "ru-RU" : "en-US", {
    weekday: "short",
    day: "numeric",
    month: "short",
  });
}

function calcLabel(c: SavedCalc): string {
  const p = c.payload?.input as Record<string, unknown> | undefined;
  if (!p) return c.key;
  if (c.calc_type === "life_path" && p.birth_date) return `Число жизненного пути — ${String(p.birth_date)}`;
  if (c.calc_type === "birthday_number" && p.birth_day != null) return `Число дня рождения — ${p.birth_day}`;
  if (c.calc_type === "personal_year" && p.birth_day != null && p.birth_month != null && p.year != null) {
    return `Личный год — ${p.birth_day}.${p.birth_month}.${p.year}`;
  }
  return c.key;
}

function calcHref(c: SavedCalc): string {
  return "/profile?focus=numerology";
}

export default function LibraryPage() {
  const router = useRouter();
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState<"forecasts" | "calculations">("forecasts");
  const [forecasts, setForecasts] = useState<string[]>([]);
  const [calculations, setCalculations] = useState<SavedCalc[]>([]);
  const [removing, setRemoving] = useState<string | null>(null);

  useEffect(() => {
    if (!isAuthenticated && !authLoading) {
      router.replace(buildAuthHref("login", "/library"));
      return;
    }
    if (!isAuthenticated) return;

    const load = async () => {
      try {
        const [f, c] = await Promise.all([
          getJson<{ saved: string[] }>("/library/forecasts"),
          getJson<{ saved: SavedCalc[] }>("/library/calculations"),
        ]);
        setForecasts(Array.isArray(f?.saved) ? f.saved : []);
        setCalculations(Array.isArray(c?.saved) ? c.saved : []);
      } catch {
        setForecasts([]);
        setCalculations([]);
      } finally {
        setLoading(false);
      }
    };
    void load();
  }, [isAuthenticated, authLoading, router]);

  const handleRemoveCalc = async (item: SavedCalc) => {
    if (removing) return;
    setRemoving(item.key);
    try {
      const res = await postJson<{ saved: SavedCalc[] }>("/library/calculations/toggle", {
        calc_type: item.calc_type,
        key: item.key,
        payload: item.payload,
      });
      setCalculations(Array.isArray(res?.saved) ? res.saved : []);
    } catch (e) {
      console.error("Remove calc failed", e);
    } finally {
      setRemoving(null);
    }
  };

  if (authLoading || loading) {
    return (
      <ProductPageScreen
        testId="library-page"
        title={t("library.title", "Моя библиотека")}
        loading
        loadingLabel="Загрузка…"
      />
    );
  }

  if (!isAuthenticated) return null;

  const forecastItems = forecasts
    .map((id) => {
      const p = parseForecastId(id);
      return p ? { id, ...p } : null;
    })
    .filter((x): x is { id: string; date: string; locale: string } => x != null);

  return (
    <ProductPageScreen
      testId="library-page"
      title={t("library.title", "Моя библиотека")}
      subtitle={t("library.subtitle", "Сохранённые прогнозы и расчёты.")}
      contentClassName={pl.content}
    >
      <div style={{ display: "flex", gap: "0.65rem", flexWrap: "wrap" }}>
        <DsButton variant={tab === "forecasts" ? "primary" : "secondary"} size="sm" onClick={() => setTab("forecasts")}>
          Прогнозы
        </DsButton>
        <DsButton
          variant={tab === "calculations" ? "primary" : "secondary"}
          size="sm"
          onClick={() => setTab("calculations")}
        >
          Расчёты
        </DsButton>
      </div>

      {tab === "forecasts" ? (
        <div className={pl.formStack}>
          {forecastItems.length === 0 ? (
            <DsBody size="sm" muted>
              {t("library.empty", "Пока ничего нет. Сохраняй прогнозы на странице «Прогнозы».")}
            </DsBody>
          ) : (
            forecastItems.map(({ id, date, locale }) => (
              <Link key={id} href={`/forecasts/${date}?locale=${locale}`} className={pl.hubCard}>
                <time dateTime={date}>
                  <DsBody>{formatDate(date, locale)}</DsBody>
                </time>
              </Link>
            ))
          )}
        </div>
      ) : (
        <div className={pl.formStack}>
          {calculations.length === 0 ? (
            <DsBody size="sm" muted>
              Пока ничего нет. Сохраняй результаты калькуляторов (Life Path, Число дня рождения, Личный год).
            </DsBody>
          ) : (
            calculations.map((c) => (
              <div key={c.key} className={pl.panel}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: "0.75rem", flexWrap: "wrap" }}>
                  <div>
                    <Link href={calcHref(c)}>
                      <DsBody>{calcLabel(c)} →</DsBody>
                    </Link>
                    {(() => {
                      const out = c.payload?.output as { number?: number } | undefined;
                      if (out?.number != null) {
                        return (
                          <DsBody size="sm" muted className={pl.bodyMtXs}>
                            Число: {out.number}
                          </DsBody>
                        );
                      }
                      return null;
                    })()}
                  </div>
                  <DsButton variant="secondary" size="sm" onClick={() => handleRemoveCalc(c)} disabled={removing === c.key}>
                    {removing === c.key ? "…" : "Убрать"}
                  </DsButton>
                </div>
              </div>
            ))
          )}
        </div>
      )}

      <div style={{ display: "flex", flexWrap: "wrap", gap: "0.65rem" }}>
        <DsButton href="/forecasts" variant="secondary" size="sm">
          {t("forecasts.title", "Прогнозы на день")}
        </DsButton>
        <DsButton href="/numerology/life-path" variant="secondary" size="sm">
          Нумерология
        </DsButton>
      </div>
    </ProductPageScreen>
  );
}
