"use client";

import { useEffect, useMemo, useState } from "react";
import Image from "next/image";
import { useRouter } from "next/navigation";
import { getJson, postJson } from "@/lib/api";
import { buildAuthHref } from "@/lib/authRedirect";
import { t } from "@/lib/i18n";
import { MeaningCard, OrientationRail } from "@/components/orbit";
import { useAuth } from "@/lib/useAuth";

type Paragraph = {
  paragraph_id: string;
  section: string;
  sub_block: string;
  meaning_type: string;
  primary_axes: string[];
  secondary_axes?: string[];
  modulators?: string[];
  lite_allowed: boolean;
  full_allowed: boolean;
  has_text_override?: boolean;
  variants?: { variant_id: string; text: string; base_text: string; override_text?: string | null }[];
};

export default function AdminPage() {
  const router = useRouter();
  const { isAuthenticated, profile, isLoading: authLoading } = useAuth();
  const [paragraphs, setParagraphs] = useState<Paragraph[]>([]);
  const [selected, setSelected] = useState<Paragraph | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [auditLogs, setAuditLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [variantDrafts, setVariantDrafts] = useState<Record<string, string>>({});
  const [activeVariantId, setActiveVariantId] = useState<string | null>(null);
  const [showContent, setShowContent] = useState(false);

  useEffect(() => {
    if (authLoading) return;
    if (!isAuthenticated || !profile?.is_admin) {
      router.replace(buildAuthHref("login", "/admin"));
      return;
    }
    refreshList();
    refreshAudit();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [authLoading, isAuthenticated, profile?.is_admin, router]);

  const refreshList = async () => {
    try {
      const data = await getJson<Paragraph[]>("/admin/paragraphs");
      setParagraphs(Array.isArray(data) ? data : []);
      if (!Array.isArray(data)) {
        setMessage("Некорректный формат данных админки.");
      }
    } catch (err) {
      setMessage(err instanceof Error ? err.message : t("admin.errors.loadParagraphs"));
    } finally {
      setLoading(false);
      setTimeout(() => setShowContent(true), 100);
    }
  };

  const refreshAudit = async () => {
    try {
      const logs = await getJson<any[]>("/admin/paragraphs/audit");
      setAuditLogs(logs);
    } catch (err) {
      console.error(err);
    }
  };

  const loadDetails = async (paragraphId: string) => {
    const data = await getJson<Paragraph>(`/admin/paragraphs/${paragraphId}`);
    setSelected(data);
    const drafts: Record<string, string> = {};
    const variants = Array.isArray(data.variants) ? data.variants : [];
    variants.forEach((variant) => {
      drafts[variant.variant_id] = variant.override_text ?? variant.text ?? "";
    });
    setVariantDrafts(drafts);
    setActiveVariantId(variants[0]?.variant_id ?? null);
  };

  const toggleLite = async (paragraphId: string, nextState: boolean) => {
    setMessage(null);
    try {
      await postJson(`/admin/paragraphs/${paragraphId}/toggle`, { lite_enabled: nextState });
      await refreshList();
      await refreshAudit();
      if (selected?.paragraph_id === paragraphId) {
        await loadDetails(paragraphId);
      }
      setMessage(t("admin.messages.liteUpdated", undefined, { id: paragraphId }));
    } catch (err) {
      setMessage(err instanceof Error ? err.message : t("admin.errors.toggle"));
    }
  };

  const toggleFull = async (paragraphId: string, nextState: boolean) => {
    setMessage(null);
    try {
      await postJson(`/admin/paragraphs/${paragraphId}/toggle`, { full_enabled: nextState });
      await refreshList();
      await refreshAudit();
      if (selected?.paragraph_id === paragraphId) {
        await loadDetails(paragraphId);
      }
      setMessage(t("admin.messages.fullUpdated", undefined, { id: paragraphId }));
    } catch (err) {
      setMessage(err instanceof Error ? err.message : t("admin.errors.toggle"));
    }
  };

  const handleVariantChange = (variantId: string, value: string) => {
    setVariantDrafts((prev) => ({ ...prev, [variantId]: value }));
    setActiveVariantId(variantId);
  };

  const saveVariant = async (paragraphId: string, variantId: string, override?: string) => {
    setMessage(null);
    try {
      const payloadText = override ?? variantDrafts[variantId] ?? "";
      await postJson(`/admin/paragraphs/${paragraphId}/variants/${variantId}`, {
        text: payloadText
      });
      if (selected?.paragraph_id === paragraphId) {
        await loadDetails(paragraphId);
      }
      await refreshAudit();
      setMessage(t("admin.messages.variantUpdated", undefined, { id: variantId }));
    } catch (err) {
      setMessage(err instanceof Error ? err.message : t("admin.errors.updateVariant"));
    }
  };

  const resetVariant = async (paragraphId: string, variantId: string) => {
    setVariantDrafts((prev) => ({ ...prev, [variantId]: "" }));
    await saveVariant(paragraphId, variantId, "");
  };

  if (loading) {
    return (
      <main className="orbit-page">
        <section className="orbit-hero-content-block">
          <div className="orbit-hero-content-container">
            <div className="orbit-card">
              <p className="orbit-body">{t("admin.loading")}</p>
            </div>
          </div>
        </section>
      </main>
    );
  }

  const selectedVariants = Array.isArray(selected?.variants) ? selected.variants : [];

  return (
    <main className="orbit-page">
      {/* Hero Section */}
      <section className="orbit-hero-design orbit-hero-design-unified">
        <div className="orbit-hero-design-wrapper">
          <Image
            src="/images/hero-meditation.png"
            alt="Admin"
            fill
            priority
            className="orbit-hero-design-bg"
            style={{ objectFit: "cover", objectPosition: "center" }}
          />
          <div className="orbit-hero-design-overlay" />
          
          {/* Large transparent gradient forms (silk/fog effect) */}
          <div className="orbit-hero-design-silk">
            <div className="orbit-hero-design-silk-1" />
            <div className="orbit-hero-design-silk-2" />
            <div className="orbit-hero-design-silk-3" />
          </div>

          {/* Connecting lines */}
          <div className="orbit-hero-design-lines">
            <svg className="orbit-hero-design-lines-svg" viewBox="0 0 1920 1080" preserveAspectRatio="none">
              <path d="M300,200 Q600,150 900,200 T1500,200" stroke="rgba(255,255,255,0.25)" strokeWidth="1.5" fill="none" />
              <path d="M400,400 Q700,350 1000,400 T1600,400" stroke="rgba(255,255,255,0.2)" strokeWidth="1" fill="none" />
            </svg>
          </div>

          {/* Content */}
          <div className="orbit-hero-design-container">
            <h1 
              className="orbit-hero-design-title-text"
              style={{
                opacity: showContent ? 1 : 0,
                transform: showContent ? "translateY(0)" : "translateY(20px)",
                transition: "opacity 0.8s ease, transform 0.8s ease"
              }}
            >
              {t("admin.list.title", "Admin Panel")}
            </h1>
            <p 
              className="orbit-hero-design-subtitle" 
              style={{ 
                textAlign: "center", 
                marginTop: "var(--orbit-space-sm)",
                opacity: showContent ? 1 : 0,
                transform: showContent ? "translateY(0)" : "translateY(20px)",
                transition: "opacity 0.8s ease 0.2s, transform 0.8s ease 0.2s"
              }}
            >
              {t("admin.list.description", "Manage paragraph templates and content")}
            </p>
          </div>
        </div>
      </section>

      {/* Content Section */}
      <section className="orbit-hero-content-block">
        <div className="orbit-hero-content-container" style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "var(--orbit-space-xl)" }}>
          <section 
            className="orbit-card" 
            style={{ 
              background: "rgba(255, 255, 255, 0.95)", 
              boxShadow: "0 4px 16px rgba(0, 0, 0, 0.08)",
              opacity: showContent ? 1 : 0,
              transform: showContent ? "translateY(0)" : "translateY(30px)",
              transition: "opacity 0.8s ease 0.3s, transform 0.8s ease 0.3s"
            }}
          >
            <OrientationRail
              sectionLabel={t("admin.orientation.section.list", "ADMIN · Inventory")}
              metaLabel={t("admin.orientation.meta.list", "Paragraph catalogue")}
            />
            <h2 className="orbit-display-sm">{t("admin.list.title", "Paragraphs")}</h2>
            <p className="orbit-body-sm orbit-text-muted">{t("admin.list.description", "Select a paragraph to edit")}</p>
            <div style={{ maxHeight: "400px", overflowY: "auto", marginTop: "var(--orbit-space-md)" }}>
              {paragraphs.map((paragraph) => (
                <button
                  key={paragraph.paragraph_id}
                  className="orbit-button orbit-button-secondary"
                  style={{
                    width: "100%",
                    display: "grid",
                    gridTemplateColumns: "1.1fr 1fr 0.5fr 0.5fr 0.7fr",
                    padding: "var(--orbit-space-sm)",
                    marginBottom: "var(--orbit-space-xs)",
                    textAlign: "left",
                    background: selected?.paragraph_id === paragraph.paragraph_id ? "var(--orbit-color-mist)" : "var(--orbit-color-card)",
                    border: selected?.paragraph_id === paragraph.paragraph_id ? "2px solid var(--orbit-color-ink)" : "1px solid var(--orbit-color-border)"
                  }}
                  onClick={() => loadDetails(paragraph.paragraph_id)}
                >
                  <span className="orbit-body-sm" style={{ fontWeight: 600 }}>{paragraph.paragraph_id}</span>
                  <span className="orbit-body-sm">{paragraph.section}</span>
                  <span className="orbit-body-xs" style={{ color: paragraph.lite_allowed ? "var(--orbit-color-highlight)" : "var(--orbit-color-slate)" }}>
                    {t("admin.row.liteLabel")} {paragraph.lite_allowed ? t("admin.common.on") : t("admin.common.off")}
                  </span>
                  <span className="orbit-body-xs" style={{ color: paragraph.full_allowed ? "var(--orbit-color-highlight)" : "var(--orbit-color-slate)" }}>
                    {t("admin.row.fullLabel")} {paragraph.full_allowed ? t("admin.common.on") : t("admin.common.off")}
                  </span>
                  <span className="orbit-body-xs" style={{ color: paragraph.has_text_override ? "var(--orbit-color-ink)" : "var(--orbit-color-slate)" }}>
                    {t("admin.row.textLabel")} {paragraph.has_text_override ? t("admin.row.override") : t("admin.row.base")}
                  </span>
                </button>
              ))}
            </div>
          </section>
          <section 
            className="orbit-card" 
            style={{ 
              background: "rgba(255, 255, 255, 0.95)", 
              boxShadow: "0 4px 16px rgba(0, 0, 0, 0.08)",
              opacity: showContent ? 1 : 0,
              transform: showContent ? "translateY(0)" : "translateY(30px)",
              transition: "opacity 0.8s ease 0.4s, transform 0.8s ease 0.4s"
            }}
          >
        {selected ? (
          <>
            <OrientationRail
              sectionLabel={`${selected.section} · ${selected.sub_block}`}
              metaLabel={t("admin.orientation.meta.detail", "Layer: {layer}", {
                layer: deriveLayer(selected.paragraph_id, selected.meaning_type)
              })}
              statusLabel={selected.meaning_type}
              action={
                <div style={{ display: "flex", gap: "var(--orbit-space-xs)" }}>
                  <span className={`orbit-badge-xs ${selected.lite_allowed ? "" : "orbit-badge-xs--muted"}`}>
                    {t("admin.row.liteLabel")} {selected.lite_allowed ? t("admin.common.on") : t("admin.common.off")}
                  </span>
                  <span className={`orbit-badge-xs ${selected.full_allowed ? "" : "orbit-badge-xs--muted"}`}>
                    {t("admin.row.fullLabel")} {selected.full_allowed ? t("admin.common.on") : t("admin.common.off")}
                  </span>
                </div>
              }
            />
            <h2 className="orbit-display-sm">{selected.paragraph_id}</h2>
            <p className="orbit-body-sm">
              {selected.section} · {selected.sub_block}
            </p>
            <p className="orbit-body-sm">
              {t("admin.detail.meaning")} {selected.meaning_type}
            </p>
            <p className="orbit-body-sm">
              {t("admin.detail.axes")} {selected.primary_axes.join(", ")}
            </p>
            {selected.secondary_axes?.length ? (
              <p className="orbit-body-sm">
                {t("admin.detail.secondary")} {selected.secondary_axes.join(", ")}
              </p>
            ) : null}
            {selected.modulators?.length ? (
              <p className="orbit-body-sm">
                {t("admin.detail.modulators")} {selected.modulators.join(", ")}
              </p>
            ) : null}
            <div style={{ display: "flex", gap: "var(--orbit-space-sm)", marginTop: "var(--orbit-space-md)" }}>
              <button className="orbit-button orbit-button-secondary" onClick={() => toggleLite(selected.paragraph_id, !selected.lite_allowed)}>
                {t("admin.detail.toggleLite", undefined, {
                  action: selected.lite_allowed ? t("admin.common.disable") : t("admin.common.enable")
                })}
              </button>
              <button className="orbit-button orbit-button-secondary" onClick={() => toggleFull(selected.paragraph_id, !selected.full_allowed)}>
                {t("admin.detail.toggleFull", undefined, {
                  action: selected.full_allowed ? t("admin.common.disable") : t("admin.common.enable")
                })}
              </button>
            </div>
            <h3 className="orbit-display-xs" style={{ marginTop: "var(--orbit-space-xl)" }}>{t("admin.detail.variants")}</h3>
            <div style={{ display: "flex", flexDirection: "column", gap: "var(--orbit-space-md)", marginTop: "var(--orbit-space-md)" }}>
              {selectedVariants.map((variant) => (
                <div key={variant.variant_id} className="orbit-card" style={{ borderTop: "1px solid var(--orbit-color-border)", paddingTop: "var(--orbit-space-md)" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "var(--orbit-space-sm)" }}>
                    <div>
                      <strong className="orbit-body-sm">{variant.variant_id}</strong>{" "}
                      {variant.override_text ? (
                        <span className="orbit-body-xs" style={{ color: "var(--orbit-color-highlight)" }}>· {t("admin.detail.overrideActive")}</span>
                      ) : null}
                    </div>
                    <button
                      className={`orbit-button ${activeVariantId === variant.variant_id ? "orbit-button-primary" : "orbit-button-secondary"}`}
                      type="button"
                      onClick={() => setActiveVariantId(variant.variant_id)}
                    >
                      {t("admin.detail.preview")}
                    </button>
                  </div>
                  <textarea
                    className="orbit-form orbit-form-textarea"
                    value={variantDrafts[variant.variant_id] ?? ""}
                    onChange={(e) => handleVariantChange(variant.variant_id, e.target.value)}
                    style={{ width: "100%", minHeight: "120px", marginTop: "var(--orbit-space-sm)" }}
                  />
                  <div style={{ display: "flex", gap: "var(--orbit-space-sm)", marginTop: "var(--orbit-space-sm)" }}>
                    <button className="orbit-button orbit-button-primary" onClick={() => saveVariant(selected.paragraph_id, variant.variant_id)}>
                      {t("admin.detail.save")}
                    </button>
                    {variant.override_text && (
                      <button className="orbit-button orbit-button-secondary" onClick={() => resetVariant(selected.paragraph_id, variant.variant_id)}>
                        {t("admin.detail.revert")}
                      </button>
                    )}
                  </div>
                  <details style={{ marginTop: "var(--orbit-space-sm)" }}>
                    <summary className="orbit-body-sm">{t("admin.detail.viewBase")}</summary>
                    <p className="orbit-body-sm orbit-text-muted" style={{ marginTop: "var(--orbit-space-xs)" }}>{variant.base_text}</p>
                  </details>
                </div>
              ))}
            </div>
            {selectedVariants.length > 0 && activeVariantId && (
              <MeaningPreview
                paragraphId={selected.paragraph_id}
                section={selected.section}
                subBlock={selected.sub_block}
                meaningType={selected.meaning_type}
                liteAllowed={selected.lite_allowed}
                fullAllowed={selected.full_allowed}
                text={
                  variantDrafts[activeVariantId] ??
                  selectedVariants.find((variant) => variant.variant_id === activeVariantId)?.text ??
                  ""
                }
              />
            )}
          </>
        ) : (
          <p className="orbit-body-sm orbit-text-muted">{t("admin.detail.empty")}</p>
        )}
          </section>
        </div>
      </section>

      {/* Audit Section */}
      <section className="orbit-hero-content-block">
        <div className="orbit-hero-content-container">
          <section 
            className="orbit-card" 
            style={{ 
              background: "rgba(255, 255, 255, 0.95)", 
              boxShadow: "0 4px 16px rgba(0, 0, 0, 0.08)",
              opacity: showContent ? 1 : 0,
              transform: showContent ? "translateY(0)" : "translateY(30px)",
              transition: "opacity 0.8s ease 0.5s, transform 0.8s ease 0.5s"
            }}
          >
            <OrientationRail
              sectionLabel={t("admin.orientation.section.audit", "ADMIN · Audit")}
              metaLabel={t("admin.orientation.meta.audit", "Recent changes")}
            />
            <h2 className="orbit-display-sm">{t("admin.audit.title", "Audit Log")}</h2>
            <div style={{ maxHeight: "300px", overflowY: "auto", marginTop: "var(--orbit-space-md)" }}>
              <ul className="orbit-list-unstyled">
                {auditLogs.map((log) => (
                  <li key={log.created_at + log.paragraph_id} className="orbit-body-sm" style={{ padding: "var(--orbit-space-sm)", borderBottom: "1px solid var(--orbit-color-border)" }}>
                    <span className="orbit-text-muted">[{log.created_at}]</span> {log.paragraph_id} {log.action} → {JSON.stringify(log.after_state)}
                  </li>
                ))}
              </ul>
            </div>
          </section>
        </div>
      </section>

      {/* Message */}
      {message && (
        <section className="orbit-hero-content-block">
          <div className="orbit-hero-content-container">
            <div className="orbit-card" style={{ background: "rgba(255, 255, 255, 0.95)", boxShadow: "0 4px 16px rgba(0, 0, 0, 0.08)" }}>
              <p className="orbit-body-sm">{message}</p>
            </div>
          </div>
        </section>
      )}
    </main>
  );
}

type MeaningPreviewProps = {
  paragraphId: string;
  section: string;
  subBlock: string;
  meaningType: string;
  liteAllowed: boolean;
  fullAllowed: boolean;
  text: string;
};

function MeaningPreview({
  paragraphId,
  section,
  subBlock,
  meaningType,
  liteAllowed,
  fullAllowed,
  text
}: MeaningPreviewProps) {
  const layer = useMemo(() => deriveLayer(paragraphId, meaningType), [paragraphId, meaningType]);
  return (
    <div className="orbit-card" style={{ marginTop: "var(--orbit-space-xl)", background: "var(--orbit-color-mist)" }}>
      <OrientationRail
        sectionLabel={`${section} · ${subBlock}`}
        metaLabel={t("admin.orientation.meta.detail", "Layer: {layer}", { layer })}
        statusLabel={meaningType}
        action={
          <div style={{ display: "flex", gap: "var(--orbit-space-xs)" }}>
            <span className={`orbit-badge-xs ${liteAllowed ? "" : "orbit-badge-xs--muted"}`}>
              {t("admin.row.liteLabel")} {liteAllowed ? t("admin.common.on") : t("admin.common.off")}
            </span>
            <span className={`orbit-badge-xs ${fullAllowed ? "" : "orbit-badge-xs--muted"}`}>
              {t("admin.row.fullLabel")} {fullAllowed ? t("admin.common.on") : t("admin.common.off")}
            </span>
          </div>
        }
      />
      <MeaningCard
        label={t("admin.preview.cardLabel", "Paragraph {id}", { id: paragraphId })}
        badge={t("admin.preview.cardBadge", "Layer · {layer}", { layer })}
        heading={meaningType}
        body={<p className="orbit-body" style={{ margin: 0 }}>{text || t("admin.preview.noText")}</p>}
        footnote={<p className="orbit-body-xs orbit-text-muted" style={{ margin: 0 }}>{t("admin.preview.note")}</p>}
      />
    </div>
  );
}

const deriveLayer = (paragraphId: string, fallback: string) => {
  if (paragraphId.endsWith("-INT")) {
    return t("admin.preview.layers.interpretation");
  }
  if (paragraphId.endsWith("-CON") || paragraphId.endsWith("-CTX")) {
    return t("admin.preview.layers.context");
  }
  if (paragraphId.endsWith("-OBS") || paragraphId.split("-").length <= 3) {
    return t("admin.preview.layers.observation");
  }
  return fallback || t("admin.preview.layers.meaning");
};
