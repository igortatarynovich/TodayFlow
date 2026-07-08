"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { getBinary, getJson, postJson } from "@/lib/api";
import { t } from "@/lib/i18n";
import type {
  AccountProfile,
  BirthData,
  ChartSnapshot,
  InternalModelSnapshot,
  ZodiacReference
} from "@/lib/types";
import { MeaningCard, OrientationRail, MethodContextCapsule, LoadingSpinner } from "@/components/orbit";
import { ProductPageScreen } from "@/components/product-ui/ProductPageScreen";
import pl from "@/design-system/layouts/productPageLayout.module.css";
import { DsButton } from "@/design-system";

type FullReport = {
  summary: ChartSnapshot;
  internal_model: InternalModelSnapshot;
  sections: {
    section: string;
    paragraphs: {
      paragraph_id: string;
      text: string;
      meaning_type?: string;
    }[];
  }[];
  content_version: string;
};

export default function FullReportPage() {
  const [profile, setProfile] = useState<AccountProfile | null>(null);
  const [report, setReport] = useState<FullReport | null>(null);
  const [form, setForm] = useState<BirthData>({ date: "", time: "", location: "" });
  const [activeMeaningIndex, setActiveMeaningIndex] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [authMissing, setAuthMissing] = useState(false);
  const [initializing, setInitializing] = useState(true);
  const [downloading, setDownloading] = useState(false);
  const [zodiacReference, setZodiacReference] = useState<ZodiacReference[]>([]);
  const [showContent, setShowContent] = useState(false);
  const sectionOutline = useMemo(
    () => [
      { title: t("full.sections.exec.title"), blurb: t("full.sections.exec.blurb") },
      { title: t("full.sections.core.title"), blurb: t("full.sections.core.blurb") },
      { title: t("full.sections.emotions.title"), blurb: t("full.sections.emotions.blurb") },
      { title: t("full.sections.relationships.title"), blurb: t("full.sections.relationships.blurb") },
      { title: t("full.sections.career.title"), blurb: t("full.sections.career.blurb") },
      { title: t("full.sections.strengths.title"), blurb: t("full.sections.strengths.blurb") },
      { title: t("full.sections.blindspots.title"), blurb: t("full.sections.blindspots.blurb") },
      { title: t("full.sections.life.title"), blurb: t("full.sections.life.blurb") },
      { title: t("full.sections.guidance.title"), blurb: t("full.sections.guidance.blurb") }
    ],
    []
  );

  useEffect(() => {
    const token = typeof window !== "undefined" ? localStorage.getItem("todayflow_token") : null;
    if (!token) {
      setAuthMissing(true);
      setInitializing(false);
      return;
    }

    const bootstrap = async () => {
      try {
        const data = await getJson<AccountProfile>("/auth/me");
        setProfile(data);
        if (data.is_paid || data.has_full_report) {
          try {
            const existing = await getJson<FullReport>("/reports/full");
            setReport(existing);
          } catch (err) {
            console.warn("No saved full report yet", err);
          }
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : t("full.errors.loadProfile", "Не удалось загрузить профиль"));
      } finally {
        setInitializing(false);
        setTimeout(() => setShowContent(true), 100);
      }
    };

    bootstrap();
  }, []);

  useEffect(() => {
    const loadReference = async () => {
      try {
        const zodiac = await getJson<ZodiacReference[]>("/reference/zodiac");
        setZodiacReference(zodiac);
      } catch (err) {
        console.warn("Failed to fetch zodiac reference", err);
      }
    };
    loadReference();
  }, []);

  useEffect(() => {
    setActiveMeaningIndex(0);
  }, [report]);

  const { meaningBlocks, sectionOffsets } = useMemo(() => {
    if (!report) {
      return { meaningBlocks: [] as EnrichedFullMeaning[], sectionOffsets: {} as Record<string, number> };
    }
    const blocks: EnrichedFullMeaning[] = [];
    const offsets: Record<string, number> = {};
    let cursor = 0;
    report.sections.forEach((section) => {
      if (!section.paragraphs.length) {
        return;
      }
      offsets[section.section] = cursor;
      section.paragraphs.forEach((paragraph, index) => {
        blocks.push({
          ...paragraph,
          section: section.section,
          step: index + 1,
          total: section.paragraphs.length
        });
        cursor += 1;
      });
    });
    return { meaningBlocks: blocks, sectionOffsets: offsets };
  }, [report]);

  const activeMeaning = meaningBlocks[activeMeaningIndex];
  const activePhaseLabel =
    activeMeaning?.meaning_type || t("dashboard.orientation.phase.integration", "Integration");
  const viewerOrientationStep = activeMeaning
    ? t("dashboard.orientation.step", undefined, {
        phase: activePhaseLabel,
        current: activeMeaning.step,
        total: activeMeaning.total
      })
    : undefined;

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!profile?.is_paid) {
      setError(t("full.errors.upgradeRequired"));
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const payload: BirthData = {
        date: form.date,
        time: form.time || undefined,
        location: form.location
      };
      const data = await postJson<FullReport>("/reports/full", payload);
      setReport(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : t("full.errors.generate"));
    } finally {
      setLoading(false);
    }
  };

  const handlePdfDownload = async () => {
    setError(null);
    try {
      setDownloading(true);
      const blob = await getBinary("/reports/full/download");
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = "todayflow_full_report.pdf";
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
    } catch (err) {
      setError(err instanceof Error ? err.message : t("dashboard.errors.pdfDownload"));
    } finally {
      setDownloading(false);
    }
  };

  if (initializing) {
    return (
      <ProductPageScreen
        testId="full-report-page"
        title={t("full.hero.paid.title")}
        loading
        loadingLabel={t("full.hero.loading")}
      />
    );
  }

  if (authMissing) {
    return (
      <ProductPageScreen
        testId="full-report-page"
        title={t("full.hero.auth.title")}
        subtitle={t("full.hero.auth.description")}
        contentClassName={`${pl.content} ${pl.legacyHost}`}
      >
        <div style={{ display: "flex", gap: "var(--orbit-space-md)", flexWrap: "wrap" }}>
          <Link href="/auth?mode=signup"><DsButton variant="primary">{t("dashboard.auth.signup")}</DsButton></Link>
          <Link href="/auth?mode=login"><DsButton variant="secondary">{t("dashboard.auth.login")}</DsButton></Link>
        </div>
      </ProductPageScreen>
    );
  }

  if (!profile?.is_paid) {
    return (
      <ProductPageScreen
        testId="full-report-page"
        eyebrow={t("full.hero.sales.eyebrow")}
        title={t("full.hero.sales.title")}
        subtitle={t("full.hero.sales.body")}
        contentClassName={`${pl.content} ${pl.legacyHost}`}
      >
        <div style={{ marginBottom: "var(--orbit-space-xl)" }}>
          <Link href="/pricing"><DsButton variant="primary">{t("full.hero.sales.cta")}</DsButton></Link>
        </div>
        <section className="orbit-card-grid">
          {sectionOutline.map((section) => (
            <article key={section.title} className="orbit-card">
              <h3 className="orbit-display-sm">{section.title}</h3>
              <p className="orbit-body-sm">{section.blurb}</p>
            </article>
          ))}
        </section>
        <section className="orbit-card-sales" style={{ marginTop: "var(--orbit-space-xl)" }}>
          <p className="orbit-body">{t("full.sections.footer.body")}</p>
          <Link href="/pricing" className="orbit-button orbit-button-primary">
            {t("full.sections.footer.cta")}
          </Link>
        </section>
      </ProductPageScreen>
    );
  }

  return (
    <ProductPageScreen
      testId="full-report-page"
      eyebrow={t("full.hero.paid.eyebrow")}
      title={t("full.hero.paid.title")}
      subtitle={t("full.hero.paid.body")}
      contentClassName={`${pl.content} ${pl.legacyHost}`}
    >
      <section
        className="orbit-card"
        style={{
          background: "rgba(255, 255, 255, 0.95)",
          boxShadow: "0 4px 16px rgba(0, 0, 0, 0.08)",
          opacity: showContent ? 1 : 0,
          transform: showContent ? "translateY(0)" : "translateY(30px)",
          transition: "opacity 0.8s ease 0.2s, transform 0.8s ease 0.2s",
        }}
      >
            <OrientationRail
              sectionLabel={t("full.orientation.section.input", "FULL · Inputs")}
              metaLabel={t("full.orientation.meta.input", "Step 1 · Confirm birth data")}
            />
            <h2 className="orbit-display-sm">{t("full.form.title")}</h2>
            <p className="orbit-body-sm">{t("full.form.description")}</p>
            <form onSubmit={handleSubmit} className="orbit-form">
              <label>
                {t("birth.form.dateLabel")}
                <input type="date" value={form.date} onChange={(e) => setForm({ ...form, date: e.target.value })} required />
              </label>
              <label>
                {t("birth.form.timeLabel")}
                <input type="time" value={form.time} onChange={(e) => setForm({ ...form, time: e.target.value })} />
              </label>
              <label>
                {t("birth.form.locationLabel")}
                <input
                  type="text"
                  value={form.location}
                  onChange={(e) => setForm({ ...form, location: e.target.value })}
                  placeholder={t("full.form.locationPlaceholder")}
                  required
                />
              </label>
              <button type="submit" disabled={loading} className="orbit-button orbit-button-primary">
                {loading ? t("full.form.button.generating") : t("full.form.button.generate")}
              </button>
            </form>
            {error && <p className="orbit-error">{error}</p>}
          </section>

          {report ? (
            <section 
              className="orbit-viewer-layout" 
              style={{ 
                background: "rgba(255, 255, 255, 0.95)", 
                boxShadow: "0 4px 16px rgba(0, 0, 0, 0.08)", 
                marginTop: "var(--orbit-space-xl)", 
                padding: "var(--orbit-space-xl)", 
                borderRadius: "2px",
                opacity: showContent ? 1 : 0,
                transform: showContent ? "translateY(0)" : "translateY(30px)",
                transition: "opacity 0.8s ease 0.4s, transform 0.8s ease 0.4s"
              }}
            >
              <aside className="orbit-toc" style={{ position: "sticky", top: "var(--orbit-space-lg)", maxHeight: "calc(100vh - var(--orbit-space-2xl))", overflowY: "auto" }}>
                <div style={{ marginBottom: "var(--orbit-space-md)" }}>
                  <p className="orbit-body-sm" style={{ fontWeight: 600, marginBottom: "var(--orbit-space-sm)" }}>{t("full.viewer.sectionsLabel")}</p>
                  <p className="orbit-body-xs orbit-text-muted" style={{ lineHeight: 1.5 }}>
                    {meaningBlocks.length} {meaningBlocks.length === 1 ? t("reports.full.block", "блок") : meaningBlocks.length < 5 ? t("reports.full.blocks2to4", "блока") : t("reports.full.blocks5plus", "блоков")} {t("reports.full.content", "контента")}
                  </p>
                </div>
                <ul className="orbit-toc-list" style={{ marginBottom: "var(--orbit-space-lg)" }}>
                  {report.sections.map((section) => {
                    const sectionStart = sectionOffsets[section.section] ?? 0;
                    const sectionLength = section.paragraphs.length;
                    const isActive = activeMeaningIndex >= sectionStart && activeMeaningIndex < sectionStart + sectionLength;
                    return (
                      <li key={section.section}>
                        <button
                          type="button"
                          className="orbit-toc-button"
                          onClick={() => setActiveMeaningIndex(sectionStart)}
                          style={{
                            background: isActive ? "var(--orbit-color-mist)" : "transparent",
                            fontWeight: isActive ? 600 : 400,
                            borderLeft: isActive ? "3px solid var(--orbit-color-primary-accent)" : "3px solid transparent"
                          }}
                        >
                          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", width: "100%" }}>
                            <span>{section.section}</span>
                            <span className="orbit-body-xs orbit-text-muted" style={{ marginLeft: "var(--orbit-space-xs)" }}>
                              {sectionLength}
                            </span>
                          </div>
                        </button>
                      </li>
                    );
                  })}
                </ul>
                <div style={{ paddingTop: "var(--orbit-space-md)", borderTop: "1px solid var(--orbit-color-border)" }}>
                  <button
                    className="orbit-button orbit-button-primary"
                    onClick={handlePdfDownload}
                    disabled={downloading}
                    style={{ width: "100%" }}
                  >
                    {downloading ? (
                      <>
                        <LoadingSpinner size="sm" />
                        <span style={{ marginLeft: "var(--orbit-space-xs)" }}>{t("full.viewer.download.preparing")}</span>
                      </>
                    ) : (
                      t("full.viewer.download.cta")
                    )}
                  </button>
                  <p className="orbit-body-xs orbit-text-muted" style={{ marginTop: "var(--orbit-space-xs)", textAlign: "center" }}>
                    {t("full.viewer.download.hint", "Скачать PDF-версию разбора")}
                  </p>
                </div>
              </aside>
              <div className="orbit-viewer-body">
                <OrientationRail
                  sectionLabel={t("full.orientation.section.viewer", "FULL · Narrative")}
                  metaLabel={t("full.orientation.meta.viewer", "Observation → Integration flow")}
                  stepLabel={viewerOrientationStep}
                />
                <h2 className="orbit-display-sm">
                  {t("full.viewer.summaryHeading", undefined, {
                    sunLabel: t("dashboard.lite.sunLabel"),
                    sun: report.summary.sun,
                    moonLabel: t("dashboard.lite.moonLabel"),
                    moon: report.summary.moon,
                    risingLabel: t("dashboard.lite.risingLabel"),
                    rising: report.summary.rising
                  })}
                </h2>
                <MethodContextPanel report={report} zodiacReference={zodiacReference} />
                {activeMeaning ? (
                  <FullMeaningBlock
                    block={activeMeaning}
                    overallIndex={activeMeaningIndex}
                    overallTotal={meaningBlocks.length}
                    onPrev={() => setActiveMeaningIndex((idx) => Math.max(idx - 1, 0))}
                    onNext={() => setActiveMeaningIndex((idx) => Math.min(idx + 1, meaningBlocks.length - 1))}
                    canPrev={activeMeaningIndex > 0}
                    canNext={activeMeaningIndex < meaningBlocks.length - 1}
                  />
                ) : (
                  <p className="orbit-soft">{t("full.viewer.noBlocks")}</p>
                )}
              </div>
            </section>
          ) : (
            <section className="orbit-empty-state">
              <p className="orbit-body">{t("full.viewer.emptyState")}</p>
            </section>
          )}
    </ProductPageScreen>
  );
}

type MethodContextProps = {
  report: FullReport;
  zodiacReference: ZodiacReference[];
};

function MethodContextPanel({ report, zodiacReference }: MethodContextProps) {
  if (!report) {
    return null;
  }
  const findSignMeta = (name: string) =>
    zodiacReference.find((ref) => ref.name.toLowerCase() === name.toLowerCase());

  const anchorCards = [
    { label: t("dashboard.lite.sunLabel"), value: report.summary.sun },
    { label: t("dashboard.lite.moonLabel"), value: report.summary.moon },
    { label: t("dashboard.lite.risingLabel"), value: report.summary.rising }
  ].map((anchor) => {
    const meta = findSignMeta(anchor.value);
    return {
      label: anchor.label,
      sign: anchor.value || t("dashboard.methodContext.unknown"),
      element: meta?.element,
      modality: meta?.modality,
      themes: meta?.themes
    };
  });

  const dominantAxes =
    report.internal_model?.axes
      ?.slice()
      .sort((a, b) => Math.abs(b.value) - Math.abs(a.value))
      .slice(0, 3)
      .map((axis) => ({
        axisId: axis.axis_id,
        label: t(`full.axis.${axis.axis_id}.title`, axis.axis_id),
        value: axis.value,
        range: axis.value > 0 ? ("outer" as const) : axis.value < 0 ? ("inner" as const) : ("balanced" as const),
        description: t(`full.axis.${axis.axis_id}.description`, "")
      })) ?? [];

  return (
    <MethodContextCapsule
      anchorCards={anchorCards}
      axisHighlights={dominantAxes}
      traceHint={t("full.method.description")}
    />
  );
}

// All styles moved to CSS classes in globals.css

type EnrichedFullMeaning = FullReport["sections"][number]["paragraphs"][number] & {
  section: string;
  step: number;
  total: number;
};

type MeaningBlockProps = {
  block: EnrichedFullMeaning;
  overallIndex: number;
  overallTotal: number;
  onPrev: () => void;
  onNext: () => void;
  canPrev: boolean;
  canNext: boolean;
};

function FullMeaningBlock({ block, overallIndex, overallTotal, onPrev, onNext, canPrev, canNext }: MeaningBlockProps) {
  const label = t("full.viewer.rail.stepLabel", undefined, {
    section: block.section,
    step: block.step,
    total: block.total
  });
  const badge = t("full.viewer.rail.badge");
  const navLabel = t("full.viewer.counter", undefined, { index: overallIndex + 1, total: overallTotal });
  return (
    <MeaningCard
      label={label}
      badge={badge}
      heading={block.meaning_type || t("full.viewer.meaningTypeFallback")}
      body={<p>{block.text}</p>}
      navLabel={navLabel}
      prevLabel={t("full.viewer.prevMeaning")}
      nextLabel={t("full.viewer.nextMeaning")}
      onPrev={onPrev}
      onNext={onNext}
      disablePrev={!canPrev}
      disableNext={!canNext}
    />
  );
}
