"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { getLocale, t } from "@/lib/i18n";
import { ruPluralForm } from "@/lib/ruPlural";
import { THEMATIC_REPORTS } from "@/lib/thematicReports";
import { ProductPageScreen } from "@/components/product-ui/ProductPageScreen";
import pl from "@/design-system/layouts/productPageLayout.module.css";

function thematicCatalogStepLabel(count: number): string {
  if (getLocale() === "ru") {
    const word = ruPluralForm(
      count,
      t("reports.thematic.rail.one", "разбор"),
      t("reports.thematic.rail.few", "разбора"),
      t("reports.thematic.rail.many", "разборов"),
    );
    return `${count} ${word}`;
  }
  const word =
    count === 1 ? t("reports.thematic.rail.one", "report") : t("reports.thematic.rail.many", "reports");
  return `${count} ${word}`;
}

export default function ThematicReportsPage() {
  const [showContent, setShowContent] = useState(false);

  useEffect(() => {
    setTimeout(() => setShowContent(true), 100);
  }, []);

  return (
    <ProductPageScreen
      testId="thematic-reports-page"
      title="Тематические разборы"
      subtitle="Фокусированные разборы по конкретным темам жизни"
      railHint={thematicCatalogStepLabel(THEMATIC_REPORTS.length)}
      contentClassName={`${pl.content} ${pl.legacyHost}`}
    >
      <div
        className={pl.grid2}
        style={{
          opacity: showContent ? 1 : 0,
          transform: showContent ? "translateY(0)" : "translateY(30px)",
          transition: "opacity 0.8s ease 0.2s, transform 0.8s ease 0.2s",
        }}
      >
        {THEMATIC_REPORTS.map((report) => (
          <Link
            key={report.id}
            href={`/reports/thematic/${report.id}`}
            className="orbit-card"
            style={{
              padding: "var(--orbit-space-xl)",
              textDecoration: "none",
              display: "block",
              borderLeft: `4px solid ${report.color}`,
              background: "rgba(255, 255, 255, 0.95)",
              boxShadow: "0 4px 16px rgba(0, 0, 0, 0.08)",
              transition: "transform 0.2s ease, box-shadow 0.2s ease",
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = "translateY(-4px)";
              e.currentTarget.style.boxShadow = "0 8px 24px rgba(0, 0, 0, 0.12)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = "translateY(0)";
              e.currentTarget.style.boxShadow = "0 4px 16px rgba(0, 0, 0, 0.08)";
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: "var(--orbit-space-md)", marginBottom: "var(--orbit-space-md)" }}>
              <div style={{ fontSize: "3rem" }}>{report.icon}</div>
              <h3 className="orbit-display-xs" style={{ margin: 0, color: report.color }}>
                {report.title}
              </h3>
            </div>
            <p className="orbit-body-sm orbit-text-muted" style={{ marginBottom: "var(--orbit-space-md)", lineHeight: 1.6 }}>
              {report.description}
            </p>
            <div style={{ marginTop: "var(--orbit-space-md)" }}>
              <p className="orbit-body-xs orbit-text-muted" style={{ marginBottom: "var(--orbit-space-xs)" }}>
                Включает секции:
              </p>
              <div style={{ display: "flex", flexWrap: "wrap", gap: "var(--orbit-space-xs)" }}>
                {report.sections.map((section) => (
                  <span
                    key={section}
                    className="orbit-badge-xs"
                    style={{ background: `${report.color}15`, color: report.color }}
                  >
                    {section}
                  </span>
                ))}
              </div>
            </div>
            <div style={{ marginTop: "var(--orbit-space-md)", textAlign: "right" }}>
              <span className="orbit-link" style={{ color: report.color }}>
                {report.ctaLabel} →
              </span>
            </div>
          </Link>
        ))}
      </div>

      <p style={{ textAlign: "center", marginTop: "var(--orbit-space-xl)" }}>
        <Link href="/account/reports" className="orbit-link-subtle">
          ← Вернуться к истории разборов
        </Link>
      </p>
    </ProductPageScreen>
  );
}
