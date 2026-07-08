"use client";

import Link from "next/link";
import type { CSSProperties, ReactNode } from "react";
import { COMPATIBILITY_GENERATION_LIVE } from "@/lib/compatibilityDynamicsMode";
import type { GuidanceCompatibilityPrefillInput } from "@/lib/guidanceCompatibilityPrefill";
import { stashGuidanceCompatibilityPrefill } from "@/lib/guidanceCompatibilityPrefill";
import type { SignCompatProductSurface } from "./CompatibilityDynamicsSurface";
import { CompatibilityFunnelSection, type CompatibilityFunnelArtifact } from "./CompatibilityFunnelSection";

export type BlockEcho = "yes" | "partial" | "no";
export type { CompatibilityFunnelArtifact };

const SUB_ROWS: Array<{ key: keyof SignCompatProductSurface["subscores"]; label: string }> = [
  { key: "attraction", label: "Притяжение" },
  { key: "stability", label: "Стабильность" },
  { key: "conflicts", label: "Конфликты" },
  { key: "sexuality", label: "Сексуальность" },
];

const SCENARIO_DISPLAY_TITLE: Record<string, string> = {
  closer: "Сблизиться",
  clarity: "Прояснить",
  exit: "Выйти",
};

const ECHO_OPTIONS: Array<{ id: BlockEcho; label: string }> = [
  { id: "yes", label: "да, это про нас" },
  { id: "partial", label: "частично" },
  { id: "no", label: "нет" },
];

function MetricCell({ value, label }: { value: number; label: string }) {
  const w = Math.min(100, Math.max(0, value));
  return (
    <div className="compat-metric-cell">
      <span className="compat-metric-label">{label}</span>
      <div className="compat-metric-value">{value}%</div>
      <div className="compat-metric-bar" aria-hidden>
        <span style={{ width: `${w}%` }} />
      </div>
    </div>
  );
}

function BlockAccordion({
  block,
  highlight,
  echo,
  onEcho,
}: {
  block: SignCompatProductSurface["blocks"][number];
  highlight?: boolean;
  echo: BlockEcho | undefined;
  onEcho: (v: BlockEcho) => void;
}) {
  return (
    <details className={`compat-accordion ${highlight ? "compat-accordion--sexuality" : ""}`}>
      <summary className="orbit-body-sm" style={{ fontWeight: 700, color: "#0f172a" }}>
        {block.title}
        <span className="orbit-body-xs" style={{ display: "block", marginTop: "0.25rem", fontWeight: 500, color: "#64748b" }}>
          {block.subtitle}
        </span>
      </summary>
      <div style={{ display: "grid", gap: "0.65rem" }}>
        <p className="orbit-body-sm" style={{ margin: 0, fontWeight: 600, color: "#0f172a" }}>
          Короткий вывод
        </p>
        <p className="orbit-body-sm" style={{ margin: 0, color: "#334155", lineHeight: 1.75 }}>
          {block.takeaway}
        </p>
        <p className="orbit-body-sm" style={{ margin: 0, color: "#334155", lineHeight: 1.75 }}>
          {block.detail}
        </p>
        <div className="compat-callout-warn">
          <p className="orbit-body-xs" style={{ margin: 0, color: "#92400e", fontWeight: 700 }}>
            Риск
          </p>
          <p className="orbit-body-sm" style={{ margin: "0.35rem 0 0", color: "#78350f", lineHeight: 1.65 }}>
            {block.risk}
          </p>
        </div>
        <div className="compat-callout-go">
          <p className="orbit-body-xs" style={{ margin: 0, color: "#166534", fontWeight: 700 }}>
            Как действовать
          </p>
          <p className="orbit-body-sm" style={{ margin: "0.35rem 0 0", color: "#14532d", lineHeight: 1.65 }}>
            {block.action}
          </p>
        </div>

        <div>
          <p className="orbit-body-xs" style={{ margin: "0 0 0.45rem", color: "#64748b", fontWeight: 600 }}>
            Это про вас?
          </p>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "0.45rem" }}>
            {ECHO_OPTIONS.map((opt) => (
              <button
                key={opt.id}
                type="button"
                className="orbit-button orbit-button-secondary orbit-button-sm"
                onClick={() => onEcho(opt.id)}
                style={{
                  borderColor: echo === opt.id ? "rgba(167, 123, 55, 0.88)" : undefined,
                  background: echo === opt.id ? "rgba(242, 220, 181, 0.35)" : undefined,
                  fontSize: "0.78rem",
                }}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>
      </div>
    </details>
  );
}

export type CompatibilityDesktopWireframeProps = {
  pairTitle: string;
  contextSubline: string;
  score: number;
  productSurface: SignCompatProductSurface;
  youColumnLabel: string;
  partnerColumnLabel: string;
  blockFeedback: Partial<Record<string, BlockEcho>>;
  onBlockFeedback: (blockKey: string, value: BlockEcho) => void;
  onRebuildWithFeedback?: () => void;
  rebuildDisabled?: boolean;
  rebuildBusy?: boolean;
  generationSource?: string | null;
  personalizedSlot?: ReactNode;
  funnelArtifact?: CompatibilityFunnelArtifact | null;
  /** Prefill для Guidance: кладётся в sessionStorage по клику на CTA. */
  guidancePrefill?: GuidanceCompatibilityPrefillInput | null;
};

export function CompatibilityDesktopWireframe({
  pairTitle,
  contextSubline,
  score,
  productSurface,
  youColumnLabel,
  partnerColumnLabel,
  blockFeedback,
  onBlockFeedback,
  onRebuildWithFeedback,
  rebuildDisabled,
  rebuildBusy,
  generationSource,
  personalizedSlot,
  funnelArtifact,
  guidancePrefill,
}: CompatibilityDesktopWireframeProps) {
  const blocks = productSurface.blocks;
  const ringStyle = { "--compat-score-pct": score } as CSSProperties;

  return (
    <div className="compat-desktop-stack">
      <div className="compat-desktop-card compat-hero-unified">
        <div className="compat-hero-grid">
          <div className="compat-hero-main">
            <p className="compat-hero-eyebrow">Разбор динамики</p>
            <h1 className="compat-hero-title">{pairTitle}</h1>
            <p className="compat-hero-context">Контекст: {contextSubline}</p>
            {generationSource ? (
              <div className="compat-hero-badge-row">
                <span className="compat-source-pill">
                  {generationSource === COMPATIBILITY_GENERATION_LIVE ? "Живой текст" : "Шаблон"}
                </span>
              </div>
            ) : null}
            <div className="compat-hero-overview">
              {productSurface.overview_paragraphs.map((p, i) => (
                <p key={i}>{p}</p>
              ))}
            </div>
            {personalizedSlot ? <div className="compat-personalized-inline">{personalizedSlot}</div> : null}
          </div>

          <aside className="compat-hero-side">
            <div className="compat-score-ring-wrap" style={ringStyle}>
              <div className="compat-score-ring-inner">
                <span className="compat-score-ring-value">{score}%</span>
                <span className="compat-score-ring-label">Общий индекс</span>
              </div>
            </div>
            <p className="compat-score-tagline-side">{productSurface.score_tagline}</p>
            <div className="compat-metrics-grid">
              {SUB_ROWS.map((row) => (
                <MetricCell key={row.key} label={row.label} value={productSurface.subscores[row.key]} />
              ))}
            </div>
          </aside>
        </div>
      </div>

      {funnelArtifact ? <CompatibilityFunnelSection artifact={funnelArtifact} /> : null}

      <section>
        <h2 className="compat-section-title">Основной разбор</h2>
        <div className="compat-block-stack">
          {blocks.map((b) => (
            <BlockAccordion
              key={b.key}
              block={b}
              highlight={b.key === "sexuality"}
              echo={blockFeedback[b.key]}
              onEcho={(v) => onBlockFeedback(b.key, v)}
            />
          ))}
        </div>
      </section>

      {onRebuildWithFeedback ? (
        <div className="compat-rebuild-row">
          <button
            type="button"
            className="orbit-button orbit-button-primary orbit-button-sm"
            disabled={rebuildDisabled || rebuildBusy}
            onClick={onRebuildWithFeedback}
          >
            {rebuildBusy ? "Пересобираем…" : "Пересобрать с учётом отметок"}
          </button>
          <p className="orbit-body-xs" style={{ margin: 0, color: "#64748b", maxWidth: "32rem", lineHeight: 1.55 }}>
            Отметки по блокам отправляются на сервер и влияют на следующую генерацию (режим живого текста).
          </p>
        </div>
      ) : null}

      <div className="compat-desktop-card">
        <h2 className="compat-section-title" style={{ marginBottom: "0.5rem" }}>
          Кто как ведёт себя
        </h2>
        <p className="orbit-body-xs compat-desktop-muted" style={{ margin: 0 }}>
          Первый столбец — «ты» ({youColumnLabel}), второй — партнёр ({partnerColumnLabel}). Роли про темп и защиту, не про пол.
        </p>
        <div
          style={{
            marginTop: "1rem",
            display: "grid",
            gridTemplateColumns: "repeat(2, minmax(0, 1fr))",
            gap: "var(--compat-col-gap)",
          }}
          className="compat-desktop-roles-cols"
        >
          <div className="compat-role-card">
            <p className="orbit-body-sm" style={{ margin: 0, fontWeight: 700, color: "#0f172a" }}>
              Ты
            </p>
            <ul style={{ margin: "0.45rem 0 0", paddingLeft: "1.1rem", color: "#475569", lineHeight: 1.65, fontSize: "0.88rem" }}>
              {productSurface.roles.you_bullets.map((line, i) => (
                <li key={i}>{line}</li>
              ))}
            </ul>
          </div>
          <div className="compat-role-card compat-role-card--warm">
            <p className="orbit-body-sm" style={{ margin: 0, fontWeight: 700, color: "#0f172a" }}>
              Партнёр
            </p>
            <ul style={{ margin: "0.45rem 0 0", paddingLeft: "1.1rem", color: "#475569", lineHeight: 1.65, fontSize: "0.88rem" }}>
              {productSurface.roles.partner_bullets.map((line, i) => (
                <li key={i}>{line}</li>
              ))}
            </ul>
          </div>
        </div>
      </div>

      <div className="compat-desktop-card">
        <h2 className="compat-section-title" style={{ marginBottom: "0.75rem" }}>
          Что с этим делать
        </h2>
        <div style={{ display: "grid", gap: "var(--compat-col-gap)", gridTemplateColumns: "repeat(3, minmax(0, 1fr))" }} className="compat-desktop-action-cols">
          {productSurface.scenarios.map((group) => (
            <div key={group.id} className="compat-scenario-card">
              <p className="orbit-body-sm" style={{ margin: 0, fontWeight: 700, color: "#7c5a33" }}>
                {SCENARIO_DISPLAY_TITLE[group.id] ?? group.title}
              </p>
              <ul style={{ margin: "0.45rem 0 0", paddingLeft: "1.1rem", color: "#475569", lineHeight: 1.65, fontSize: "0.88rem" }}>
                {group.bullets.map((b, i) => (
                  <li key={i}>{b}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>

      <div className="compat-footer-actions">
        <div className="compat-desktop-card">
          <h3 className="orbit-heading-3" style={{ margin: 0, color: "#5f4323" }}>
            Guidance
          </h3>
          <p className="orbit-body-sm compat-desktop-muted" style={{ margin: "0.45rem 0 0" }}>
            Разобрать ситуацию по шагам и решениям.
          </p>
          <Link
            href="/tarot?from=compatibility"
            className="orbit-button orbit-button-primary orbit-button-sm"
            style={{ textDecoration: "none", marginTop: "0.85rem", display: "inline-flex" }}
            onClick={() => {
              if (guidancePrefill) stashGuidanceCompatibilityPrefill(guidancePrefill);
            }}
          >
            Разобрать ситуацию
          </Link>
        </div>
        <div className="compat-desktop-card">
          <h3 className="orbit-heading-3" style={{ margin: 0, color: "#5f4323" }}>
            Профиль
          </h3>
          <p className="orbit-body-sm compat-desktop-muted" style={{ margin: "0.45rem 0 0" }}>
            Понять свой паттерн и опоры.
          </p>
          <Link href="/profile" className="orbit-button orbit-button-secondary orbit-button-sm" style={{ textDecoration: "none", marginTop: "0.85rem", display: "inline-flex" }}>
            Понять себя
          </Link>
        </div>
        <div className="compat-desktop-card">
          <h3 className="orbit-heading-3" style={{ margin: 0, color: "#5f4323" }}>
            Глубже
          </h3>
          <p className="orbit-body-sm compat-desktop-muted" style={{ margin: "0.45rem 0 0" }}>
            Добавить данные или сменить контекст.
          </p>
          <a href="#compat-entry" className="orbit-button orbit-button-secondary orbit-button-sm" style={{ textDecoration: "none", marginTop: "0.85rem", display: "inline-flex" }}>
            Добавить данные
          </a>
        </div>
      </div>
    </div>
  );
}
