"use client";

import { t } from "@/lib/i18n";

import { OrientationRail } from "@/components/orbit";
import type { ThematicReport } from "@/lib/types";

interface ThematicReportDisplayProps {
  report: ThematicReport;
  themeTitle: string;
  onRegenerate: () => void;
  generating: boolean;
  showContent: boolean;
}

export function ThematicReportDisplay({
  report,
  themeTitle,
  onRegenerate,
  generating,
  showContent,
}: ThematicReportDisplayProps) {
  return (
    <section className="orbit-hero-content-block" style={{ paddingTop: "var(--orbit-space-xl)", paddingBottom: "var(--orbit-space-4xl)" }}>
      <div className="orbit-hero-content-container" style={{ maxWidth: "1000px", margin: "0 auto" }}>
        <OrientationRail
          sectionLabel={t("reports.thematic.display.rail.section", "Тематический разбор")}
          metaLabel={themeTitle}
          stepLabel={`${report.sections.length} ${t("reports.thematic.display.rail.stepSuffix", "секций")}`}
        />

        <div
          style={{
            marginTop: "var(--orbit-space-lg)",
            opacity: showContent ? 1 : 0,
            transform: showContent ? "translateY(0)" : "translateY(30px)",
            transition: "opacity 0.8s ease 0.4s, transform 0.8s ease 0.4s"
          }}
        >
          {report.sections.map((section, idx) => (
            <div
              key={idx}
              className="orbit-card"
              style={{
                marginBottom: "var(--orbit-space-xl)",
                padding: "var(--orbit-space-xl)",
                background: "rgba(255, 255, 255, 0.95)",
                boxShadow: "0 4px 16px rgba(0, 0, 0, 0.08)"
              }}
            >
              <h3 className="orbit-display-xs" style={{ marginBottom: "var(--orbit-space-lg)", color: "var(--orbit-color-primary)" }}>
                {section.section}
              </h3>
              <div style={{ display: "flex", flexDirection: "column", gap: "var(--orbit-space-md)" }}>
                {section.paragraphs.map((paragraph, pIdx) => (
                  <div key={pIdx} style={{ lineHeight: 1.8 }}>
                    <p className="orbit-body" style={{ color: "var(--orbit-color-slate)" }}>
                      {paragraph.text}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>

        <div style={{ marginTop: "var(--orbit-space-xl)", textAlign: "center" }}>
          <button
            onClick={onRegenerate}
            disabled={generating}
            className="orbit-button orbit-button-secondary"
          >
            {generating ? t("reports.updating", "Обновляю разбор...") : t("reports.update", "Обновить разбор")}
          </button>
        </div>
      </div>
    </section>
  );
}

