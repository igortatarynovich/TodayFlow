"use client";

import { funnelSectionTitle } from "@/lib/compatibilityScenarioMetrics";
import { t } from "@/lib/i18n";

/** Ответ API `funnel_artifact` — воронка точности и доменные скоры. */
export type CompatibilityFunnelArtifact = {
  pipeline_version: string;
  scenario_id?: string | null;
  accuracy_tier: string;
  accuracy_label: string;
  relationship_context: string;
  score_semantics: string;
  confidence_note: string;
  overall_score: number;
  domain_scores: Array<{
    domain_id: string;
    label: string;
    score_pct: number;
    confidence: number;
    applicable: boolean;
    basis: string;
    raises: string[];
    lowers: string[];
    improve: string[];
  }>;
  children_relevant: boolean;
  timeline: Array<{ phase_id: string; headline: string; body: string }>;
  dynamic_core: {
    you_line: string;
    partner_line: string;
    control_pattern: string;
    clarity_note: string;
  };
  risk_bands: Array<{
    level: string;
    headline: string;
    when_ok: string;
    when_shifts: string;
    when_breaks: string;
  }>;
  today_alignment?: {
    source: string;
    focus_label: string;
    do_echo: string;
    avoid_echo: string;
    sync_note: string;
  } | null;
  llm_base_model?: {
    pull_vs_tension: string;
    attraction_or_dependency: string;
    conflict_cycle: string;
    sexual_dynamic: string;
    aligned_actions_hint: string;
  } | null;
};

type Props = {
  artifact: CompatibilityFunnelArtifact;
  /** Внутри `CompatibilityDesktopWireframe` верхний отступ уже задан сеткой — можно убрать. */
  omitTopMargin?: boolean;
};

function FunnelDomainRow({ row }: { row: CompatibilityFunnelArtifact["domain_scores"][number] }) {
  if (!row.applicable) return null;
  const w = Math.min(100, Math.max(0, row.score_pct));
  const confPct = Math.round(row.confidence * 100);
  return (
    <div className="compat-metric-cell" style={{ gridColumn: "span 1" }}>
      <span className="compat-metric-label">{row.label}</span>
      <div className="compat-metric-value">
        {row.score_pct}%{" "}
        <span className="orbit-body-xs" style={{ color: "#94a3b8", fontWeight: 500 }}>
          · {confPct}% уверен.
        </span>
      </div>
      <div className="compat-metric-bar" aria-hidden>
        <span style={{ width: `${w}%` }} />
      </div>
      <p className="compat-metric-hint" style={{ marginTop: "0.35rem" }}>
        {row.basis}
      </p>
      {row.raises.length ? (
        <p className="orbit-body-xs" style={{ margin: "0.35rem 0 0", color: "#166534", lineHeight: 1.5 }}>
          ↑ {row.raises.join(" ")}
        </p>
      ) : null}
      {row.lowers.length ? (
        <p className="orbit-body-xs" style={{ margin: "0.2rem 0 0", color: "#9a3412", lineHeight: 1.5 }}>
          ↓ {row.lowers.join(" ")}
        </p>
      ) : null}
      <p className="orbit-body-xs" style={{ margin: "0.35rem 0 0", color: "#334155", lineHeight: 1.55 }}>
        Как улучшить: {row.improve.join(" ")}
      </p>
    </div>
  );
}

export function CompatibilityFunnelSection({ artifact, omitTopMargin }: Props) {
  const domains = artifact.domain_scores.filter((d) => d.applicable);
  return (
    <div
      className="compat-desktop-card"
      style={omitTopMargin ? undefined : { marginTop: "var(--compat-col-gap, 1rem)" }}
    >
      <p className="orbit-body-xs" style={{ margin: 0, color: "#8b7355", textTransform: "uppercase", letterSpacing: "0.08em" }}>
        Воронка точности
      </p>
      <h2 className="compat-section-title" style={{ marginTop: "0.35rem", marginBottom: "0.35rem" }}>
        {artifact.accuracy_label}
      </h2>
      <p className="orbit-body-sm compat-desktop-muted" style={{ margin: "0 0 0.65rem", lineHeight: 1.65 }}>
        {artifact.score_semantics}
      </p>
      <p className="orbit-body-xs" style={{ margin: "0 0 1rem", color: "#64748b", lineHeight: 1.55 }}>
        {artifact.confidence_note}
      </p>

      {artifact.today_alignment &&
      (artifact.today_alignment.do_echo || artifact.today_alignment.avoid_echo || artifact.today_alignment.focus_label) ? (
        <div className="compat-callout-go" style={{ marginBottom: "1rem", borderColor: "rgba(22, 101, 52, 0.25)" }}>
          <p className="orbit-body-xs" style={{ margin: 0, color: "#166534", fontWeight: 700 }}>
            {t("compat.funnel.today_layer.title")}
          </p>
          {artifact.today_alignment.sync_note ? (
            <p className="orbit-body-xs" style={{ margin: "0.35rem 0 0", color: "#334155", lineHeight: 1.55 }}>
              {artifact.today_alignment.sync_note}
            </p>
          ) : null}
          {artifact.today_alignment.focus_label ? (
            <p className="orbit-body-sm" style={{ margin: "0.45rem 0 0", color: "#0f172a", lineHeight: 1.6 }}>
              <strong>{t("compat.funnel.today_layer.focus_label")}:</strong> {artifact.today_alignment.focus_label}
            </p>
          ) : null}
          {artifact.today_alignment.do_echo ? (
            <p className="orbit-body-sm" style={{ margin: "0.35rem 0 0", color: "#14532d", lineHeight: 1.6 }}>
              <strong>{t("compat.funnel.today_layer.do_echo")}:</strong> {artifact.today_alignment.do_echo}
            </p>
          ) : null}
          {artifact.today_alignment.avoid_echo ? (
            <p className="orbit-body-sm" style={{ margin: "0.35rem 0 0", color: "#9a3412", lineHeight: 1.6 }}>
              <strong>{t("compat.funnel.today_layer.avoid_echo")}:</strong> {artifact.today_alignment.avoid_echo}
            </p>
          ) : null}
        </div>
      ) : null}

      {artifact.llm_base_model &&
      (artifact.llm_base_model.pull_vs_tension ||
        artifact.llm_base_model.attraction_or_dependency ||
        artifact.llm_base_model.conflict_cycle ||
        artifact.llm_base_model.sexual_dynamic ||
        artifact.llm_base_model.aligned_actions_hint) ? (
        <div className="compat-desktop-card" style={{ marginBottom: "1rem", padding: "0.85rem", background: "rgba(255,255,255,0.55)" }}>
          <p className="orbit-body-xs" style={{ margin: 0, color: "#8b7355", fontWeight: 700 }}>
            {t("compat.funnel.llm_base.title")}
          </p>
          {artifact.llm_base_model.pull_vs_tension ? (
            <p className="orbit-body-sm" style={{ margin: "0.45rem 0 0", color: "#334155", lineHeight: 1.65 }}>
              <strong>{t("compat.funnel.llm_base.pull")}:</strong> {artifact.llm_base_model.pull_vs_tension}
            </p>
          ) : null}
          {artifact.llm_base_model.attraction_or_dependency ? (
            <p className="orbit-body-sm" style={{ margin: "0.35rem 0 0", color: "#334155", lineHeight: 1.65 }}>
              <strong>{t("compat.funnel.llm_base.attr_dep")}:</strong> {artifact.llm_base_model.attraction_or_dependency}
            </p>
          ) : null}
          {artifact.llm_base_model.conflict_cycle ? (
            <p className="orbit-body-sm" style={{ margin: "0.35rem 0 0", color: "#334155", lineHeight: 1.65 }}>
              <strong>{t("compat.funnel.llm_base.conflict")}:</strong> {artifact.llm_base_model.conflict_cycle}
            </p>
          ) : null}
          {artifact.llm_base_model.sexual_dynamic ? (
            <p className="orbit-body-sm" style={{ margin: "0.35rem 0 0", color: "#334155", lineHeight: 1.65 }}>
              <strong>{t("compat.funnel.llm_base.sex")}:</strong> {artifact.llm_base_model.sexual_dynamic}
            </p>
          ) : null}
          {artifact.llm_base_model.aligned_actions_hint ? (
            <p className="orbit-body-sm" style={{ margin: "0.35rem 0 0", color: "#0f172a", lineHeight: 1.65 }}>
              <strong>{t("compat.funnel.llm_base.actions")}:</strong> {artifact.llm_base_model.aligned_actions_hint}
            </p>
          ) : null}
        </div>
      ) : null}

      <h3 className="orbit-heading-3" style={{ margin: "0 0 0.5rem", color: "#5f4323", fontSize: "1rem" }}>
        {funnelSectionTitle(artifact.scenario_id)}
      </h3>
      <div
        className="compat-metrics-grid"
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fill, minmax(220px, 1fr))",
          gap: "0.85rem",
        }}
      >
        {domains.map((d) => (
          <FunnelDomainRow key={d.domain_id} row={d} />
        ))}
      </div>

      <h3 className="orbit-heading-3" style={{ margin: "1.25rem 0 0.5rem", color: "#5f4323", fontSize: "1rem" }}>
        Главная динамика (асимметрия)
      </h3>
      <div style={{ display: "grid", gap: "0.5rem" }}>
        <p className="orbit-body-sm" style={{ margin: 0, color: "#334155", lineHeight: 1.65 }}>
          {artifact.dynamic_core.you_line}
        </p>
        <p className="orbit-body-sm" style={{ margin: 0, color: "#334155", lineHeight: 1.65 }}>
          {artifact.dynamic_core.partner_line}
        </p>
        <p className="orbit-body-sm" style={{ margin: 0, color: "#0f172a", lineHeight: 1.65 }}>
          <strong>Контроль / темп:</strong> {artifact.dynamic_core.control_pattern}
        </p>
        <p className="orbit-body-sm" style={{ margin: 0, color: "#475569", lineHeight: 1.65 }}>
          {artifact.dynamic_core.clarity_note}
        </p>
      </div>

      <h3 className="orbit-heading-3" style={{ margin: "1.25rem 0 0.5rem", color: "#5f4323", fontSize: "1rem" }}>
        Время
      </h3>
      <div style={{ display: "grid", gap: "0.45rem" }}>
        {artifact.timeline.map((t) => (
          <details key={t.phase_id} className="compat-accordion">
            <summary className="orbit-body-sm" style={{ fontWeight: 700, color: "#0f172a" }}>
              {t.headline}
            </summary>
            <p className="orbit-body-sm" style={{ margin: "0.5rem 0 0", color: "#334155", lineHeight: 1.7 }}>
              {t.body}
            </p>
          </details>
        ))}
      </div>

      <h3 className="orbit-heading-3" style={{ margin: "1.25rem 0 0.5rem", color: "#5f4323", fontSize: "1rem" }}>
        Пороги риска
      </h3>
      <div style={{ display: "grid", gap: "0.65rem" }}>
        {artifact.risk_bands.map((b) => (
          <div key={b.level} className="compat-callout-warn" style={{ borderColor: b.level === "critical" ? "#fecaca" : undefined }}>
            <p className="orbit-body-xs" style={{ margin: 0, color: "#92400e", fontWeight: 700 }}>
              {b.headline}
            </p>
            <p className="orbit-body-xs" style={{ margin: "0.35rem 0 0", color: "#78350f", lineHeight: 1.55 }}>
              Ок: {b.when_ok}
            </p>
            <p className="orbit-body-xs" style={{ margin: "0.25rem 0 0", color: "#78350f", lineHeight: 1.55 }}>
              Сдвиг: {b.when_shifts}
            </p>
            <p className="orbit-body-xs" style={{ margin: "0.25rem 0 0", color: "#78350f", lineHeight: 1.55 }}>
              Ломается: {b.when_breaks}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
