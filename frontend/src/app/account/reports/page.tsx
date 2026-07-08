"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { OrientationRail } from "@/components/orbit";
import { ProductPageScreen } from "@/components/product-ui/ProductPageScreen";
import pl from "@/design-system/layouts/productPageLayout.module.css";
import { getJson } from "@/lib/api";
import { getLocale, t } from "@/lib/i18n";
import { ruPluralForm } from "@/lib/ruPlural";

function reportsHistoryRailStepLabel(count: number): string {
  if (getLocale() === "ru") {
    const word = ruPluralForm(
      count,
      t("reports.history.rail.one", "отчёт"),
      t("reports.history.rail.few", "отчёта"),
      t("reports.history.rail.many", "отчётов"),
    );
    return `${count} ${word}`;
  }
  const word =
    count === 1 ? t("reports.history.rail.one", "report") : t("reports.history.rail.many", "reports");
  return `${count} ${word}`;
}
import { getThematicReportMeta } from "@/lib/thematicReports";
import type { ReportHistoryResponse, ReportHistoryItem } from "@/lib/types";

export default function AccountReportsPage() {
  const [loading, setLoading] = useState(true);
  const [history, setHistory] = useState<ReportHistoryResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showContent, setShowContent] = useState(false);
  const [filterType, setFilterType] = useState<"all" | "lite" | "full" | "thematic">("all");

  useEffect(() => {
    const token = typeof window !== "undefined" ? localStorage.getItem("todayflow_token") : null;
    if (!token) {
      setError(t("account.errors.authRequired", "Требуется авторизация"));
      setLoading(false);
      return;
    }

    const loadData = async () => {
      try {
        const data = await getJson<ReportHistoryResponse>("/reports/history");
        setHistory(data);
      } catch (err) {
        console.error("Failed to load report history", err);
        setError(err instanceof Error ? err.message : t("reports.errors.loadFailed", "Не удалось загрузить историю разборов"));
      } finally {
        setLoading(false);
        setTimeout(() => setShowContent(true), 100);
      }
    };

    loadData();
  }, []);

  const getReportTypeLabel = (productType: string) => {
    if (productType.startsWith("thematic_")) {
      const theme = productType.replace("thematic_", "");
      return getThematicReportMeta(theme)?.title || `Тематический разбор: ${theme}`;
    }
    switch (productType) {
      case "lite":
        return "Lite Report";
      case "full":
        return "Full Report";
      default:
        return productType;
    }
  };

  const getReportTypeColor = (productType: string) => {
    if (productType.startsWith("thematic_")) {
      const theme = productType.replace("thematic_", "");
      return getThematicReportMeta(theme)?.color || "var(--orbit-color-slate)";
    }
    switch (productType) {
      case "lite":
        return "var(--orbit-color-muted)";
      case "full":
        return "var(--orbit-color-primary-accent)";
      default:
        return "var(--orbit-color-slate)";
    }
  };

  const getReportViewUrl = (productType: string) => {
    if (productType.startsWith("thematic_")) {
      const theme = productType.replace("thematic_", "");
      return `/reports/thematic/${theme}`;
    }
    switch (productType) {
      case "full":
        return "/reports/full";
      case "lite":
        return "/profile";
      default:
        return "/profile";
    }
  };

  if (loading) {
    return (
      <ProductPageScreen
        title="История разборов"
        loading
        loadingLabel={t("reports.loading", "Загрузка истории разборов…")}
      />
    );
  }

  if (error) {
    return (
      <ProductPageScreen
        title="История разборов"
        guest={{
          message: error,
          ctaHref: "/auth",
          ctaLabel: "Войти",
        }}
      />
    );
  }

  return (
    <ProductPageScreen
      testId="account-reports-page"
      title="История разборов"
      subtitle="Просматривайте все ваши разборы и скачивайте PDF"
      railTitle={t("reports.history.rail.section", "Отчёты")}
      railHint={t("reports.history.rail.meta", "История")}
      contentClassName={`${pl.content} ${pl.legacyHost}`}
    >
      <div style={{ marginBottom: "1rem" }}>
        <Link href="/reports/thematic" className="orbit-button orbit-button-secondary orbit-button-sm">
          Тематические разборы →
        </Link>
      </div>

      {/* Reports History */}
      {history && history.history.length > 0 ? (
        <section className="orbit-hero-content-block">
          <div className="orbit-hero-content-container">
            <div
              className="orbit-card"
              style={{
                background: "rgba(255, 255, 255, 0.95)",
                boxShadow: "0 4px 16px rgba(0, 0, 0, 0.08)",
                opacity: showContent ? 1 : 0,
                transform: showContent ? "translateY(0)" : "translateY(30px)",
                transition: "opacity 0.8s ease 0.3s, transform 0.8s ease 0.3s",
              }}
            >
              <OrientationRail
                sectionLabel={t("reports.history.rail.section", "Отчёты")}
                metaLabel={t("reports.history.rail.meta", "История")}
                stepLabel={reportsHistoryRailStepLabel(history.total)}
              />
              
              {/* Filters */}
              <div style={{ marginTop: "var(--orbit-space-lg)", marginBottom: "var(--orbit-space-md)", display: "flex", gap: "var(--orbit-space-sm)", borderBottom: "1px solid var(--orbit-color-border)", paddingBottom: "var(--orbit-space-sm)", flexWrap: "wrap" }}>
                <button
                  onClick={() => setFilterType("all")}
                  className={`orbit-button orbit-button-text orbit-button-xs ${filterType === "all" ? "orbit-button-primary" : ""}`}
                  style={{ borderBottom: filterType === "all" ? "2px solid var(--orbit-color-primary)" : "2px solid transparent" }}
                >
                  Все ({history.history.length})
                </button>
                <button
                  onClick={() => setFilterType("full")}
                  className={`orbit-button orbit-button-text orbit-button-xs ${filterType === "full" ? "orbit-button-primary" : ""}`}
                  style={{ borderBottom: filterType === "full" ? "2px solid var(--orbit-color-primary)" : "2px solid transparent" }}
                >
                  Full ({history.history.filter(h => h.product_type === "full").length})
                </button>
                <button
                  onClick={() => setFilterType("lite")}
                  className={`orbit-button orbit-button-text orbit-button-xs ${filterType === "lite" ? "orbit-button-primary" : ""}`}
                  style={{ borderBottom: filterType === "lite" ? "2px solid var(--orbit-color-primary)" : "2px solid transparent" }}
                >
                  Lite ({history.history.filter(h => h.product_type === "lite").length})
                </button>
                <button
                  onClick={() => setFilterType("thematic")}
                  className={`orbit-button orbit-button-text orbit-button-xs ${filterType === "thematic" ? "orbit-button-primary" : ""}`}
                  style={{ borderBottom: filterType === "thematic" ? "2px solid var(--orbit-color-primary)" : "2px solid transparent" }}
                >
                  Тематические ({history.history.filter(h => h.product_type.startsWith("thematic_")).length})
                </button>
              </div>

              <div style={{ marginTop: "var(--orbit-space-md)", display: "flex", flexDirection: "column", gap: "var(--orbit-space-md)" }}>
                {history.history
                  .filter(item => {
                    if (filterType === "all") return true;
                    if (filterType === "thematic") return item.product_type.startsWith("thematic_");
                    return item.product_type === filterType;
                  })
                  .map((item) => (
                  <div
                    key={item.id}
                    style={{
                      padding: "var(--orbit-space-md)",
                      border: "1px solid var(--orbit-color-border)",
                      borderRadius: "var(--orbit-radius-sm)",
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "start",
                      flexWrap: "wrap",
                      gap: "var(--orbit-space-md)",
                    }}
                  >
                    <div style={{ flex: 1, minWidth: "200px" }}>
                      <div style={{ display: "flex", alignItems: "center", gap: "var(--orbit-space-sm)", marginBottom: "var(--orbit-space-xs)", flexWrap: "wrap" }}>
                        <h3 className="orbit-body" style={{ fontWeight: 600, margin: 0 }}>
                          {getReportTypeLabel(item.product_type)}
                        </h3>
                        <span
                          style={{
                            padding: "2px 8px",
                            background: getReportTypeColor(item.product_type),
                            color: "white",
                            borderRadius: "var(--orbit-radius-sm)",
                            fontSize: "0.75rem",
                            fontWeight: 600,
                          }}
                        >
                          {item.product_type.startsWith("thematic_") 
                            ? item.product_type.replace("thematic_", "").toUpperCase()
                            : item.product_type.toUpperCase()}
                        </span>
                      </div>
                      <p className="orbit-body-sm orbit-text-muted" style={{ marginBottom: "var(--orbit-space-xs)" }}>
                        {new Date(item.created_at).toLocaleDateString("ru-RU", {
                          day: "numeric",
                          month: "long",
                          year: "numeric",
                          hour: "2-digit",
                          minute: "2-digit",
                        })}
                      </p>
                      {item.profile_label && (
                        <p className="orbit-body-sm orbit-text-muted">
                          Профиль: {item.profile_label}
                        </p>
                      )}
                      <p className="orbit-body-xs orbit-text-muted" style={{ marginTop: "var(--orbit-space-xs)" }}>
                        Версия: {item.content_version}
                      </p>
                    </div>

                    <div style={{ display: "flex", gap: "var(--orbit-space-sm)", flexWrap: "wrap" }}>
                      {item.product_type === "full" && (
                        <a
                          href={`/reports/full/download?report_id=${item.id}`}
                          className="orbit-button orbit-button-secondary orbit-button-xs"
                          download
                        >
                          Скачать PDF
                        </a>
                      )}
                      <Link
                        href={getReportViewUrl(item.product_type)}
                        className="orbit-button orbit-button-secondary orbit-button-xs"
                      >
                        Просмотреть
                      </Link>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>
      ) : (
        <section className="orbit-hero-content-block">
          <div className="orbit-hero-content-container">
            <div
              className="orbit-card"
              style={{
                background: "rgba(255, 255, 255, 0.95)",
                boxShadow: "0 4px 16px rgba(0, 0, 0, 0.08)",
                opacity: showContent ? 1 : 0,
                transform: showContent ? "translateY(0)" : "translateY(30px)",
                transition: "opacity 0.8s ease 0.3s, transform 0.8s ease 0.3s",
                textAlign: "center",
                padding: "var(--orbit-space-2xl)",
              }}
            >
              <p className="orbit-body" style={{ marginBottom: "var(--orbit-space-lg)" }}>
                {t("reports.noReports", "У вас пока нет разборов")}
              </p>
              <div style={{ display: "flex", gap: "var(--orbit-space-md)", justifyContent: "center", flexWrap: "wrap" }}>
                <Link href="/onboarding/core" className="orbit-button orbit-button-primary">
                  {t("reports.createFirst", "Создать первый разбор")}
                </Link>
                <Link href="/today" className="orbit-button orbit-button-secondary">
                  {t("reports.backToDashboard", "Вернуться на главную")}
                </Link>
              </div>
            </div>
          </div>
        </section>
      )}
    </ProductPageScreen>
  );
}
