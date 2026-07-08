"use client";

import Link from "next/link";
import { useState, type CSSProperties, type ReactNode } from "react";
import { HeroSmall } from "@/components/foundation/HeroSmall";
import { compatibilityPairSymbolFromDisplay } from "@/lib/compatibilityHeroSymbol";
import { stripCompatibilityDisplayGarbage } from "@/lib/compatibilityCopySanitize";

export type SignCompatProductSurface = {
  score_tagline: string;
  subscores: {
    attraction: number;
    stability: number;
    conflicts: number;
    sexuality: number;
  };
  overview_paragraphs: string[];
  blocks: Array<{
    key: string;
    title: string;
    subtitle: string;
    takeaway: string;
    detail: string;
    risk: string;
    action: string;
    tips?: string[];
  }>;
  roles: {
    you_bullets: string[];
    partner_bullets: string[];
  };
  scenarios: Array<{
    id: string;
    title: string;
    bullets: string[];
  }>;
};

type Props = {
  pairDisplay: string;
  youColumnLabel: string;
  partnerColumnLabel: string;
  score: number;
  productSurface: SignCompatProductSurface;
  readingLead?: string | null;
  personalizedCard?: ReactNode;
  extraParagraphs?: string[];
  paragraphsDetailTitle?: string;
  showParagraphsUpsell?: boolean;
  /** Если родитель уже показал заголовок пары — не дублируем верхнюю карточку. */
  omitIntroHero?: boolean;
};

const SUB_LABELS: Array<{ key: keyof SignCompatProductSurface["subscores"]; label: string; hint: string }> = [
  { key: "attraction", label: "Притяжение", hint: "сила и качество тяги друг к другу" },
  { key: "stability", label: "Стабильность", hint: "насколько ровно держится контакт в быту и фазах" },
  { key: "conflicts", label: "Конфликты", hint: "способность чинить контакт после срыва, без зацикливания" },
  { key: "sexuality", label: "Сексуальность", hint: "химия и честность телесного слоя" },
];

function MetricWithHint({ value, label, hint }: { value: number; label: string; hint: string }) {
  const w = Math.min(100, Math.max(0, value));
  return (
    <div className="compat-metric-cell">
      <span className="compat-metric-label">{label}</span>
      <div className="compat-metric-value">{value}%</div>
      <div className="compat-metric-bar" aria-hidden>
        <span style={{ width: `${w}%` }} />
      </div>
      <p className="compat-metric-hint">{hint}</p>
    </div>
  );
}

function CompactScoreRing({ score }: { score: number }) {
  const ringStyle = { "--compat-score-pct": score } as CSSProperties;
  return (
    <div className="compat-score-ring-wrap compat-score-ring-wrap--hero-small" style={ringStyle}>
      <div className="compat-score-ring-inner">
        <span className="compat-score-ring-value">{score}%</span>
      </div>
    </div>
  );
}

function ScoreAside({
  score,
  tagline,
  productSurface,
  variant = "grid",
}: {
  score: number;
  tagline: string;
  productSurface: SignCompatProductSurface;
  variant?: "grid" | "standalone";
}) {
  const ringStyle = { "--compat-score-pct": score } as CSSProperties;
  const sideClass = variant === "standalone" ? "compat-hero-side compat-hero-side--standalone" : "compat-hero-side";
  return (
    <aside className={sideClass}>
      <div className="compat-score-ring-wrap" style={ringStyle}>
        <div className="compat-score-ring-inner">
          <span className="compat-score-ring-value">{score}%</span>
          <span className="compat-score-ring-label">Общий индекс</span>
        </div>
      </div>
      <p className="compat-score-tagline-side">{tagline}</p>
      <div className="compat-metrics-grid">
        {SUB_LABELS.map((row) => (
          <MetricWithHint key={row.key} value={productSurface.subscores[row.key]} label={row.label} hint={row.hint} />
        ))}
      </div>
    </aside>
  );
}

const ECHO_OPTIONS = [
  { id: "yes" as const, label: "Да", title: "да, это про нас" },
  { id: "partial" as const, label: "Частично", title: "частично" },
  { id: "no" as const, label: "Нет", title: "нет" },
];

export function CompatibilityDynamicsSurface({
  pairDisplay,
  youColumnLabel,
  partnerColumnLabel,
  score,
  productSurface,
  personalizedCard,
  extraParagraphs,
  paragraphsDetailTitle = "Дополнительный текст",
  showParagraphsUpsell,
  readingLead,
  omitIntroHero,
}: Props) {
  const [blockEcho, setBlockEcho] = useState<Partial<Record<string, "yes" | "partial" | "no">>>({});

  return (
    <div className="compat-desktop-shell compat-desktop-stack">
      {!omitIntroHero ? (
        <div className="compat-desktop-card compat-hero-unified">
          <HeroSmall
            symbol={compatibilityPairSymbolFromDisplay(pairDisplay)}
            kicker="Совместимость"
            title={pairDisplay}
            titleAs="h1"
            meta={
              readingLead ||
              "Не «насколько вы подходите», а как вы цепляетесь, где спотыкаетесь и что с этим делать."
            }
            aside={<CompactScoreRing score={score} />}
            flush
          />
          <div className="compat-hero-metrics-below">
            <p className="compat-score-tagline-side">{productSurface.score_tagline}</p>
            <div className="compat-metrics-grid">
              {SUB_LABELS.map((row) => (
                <MetricWithHint key={row.key} value={productSurface.subscores[row.key]} label={row.label} hint={row.hint} />
              ))}
            </div>
          </div>
        </div>
      ) : (
        <>
          {readingLead ? <p className="compat-dynamics-lead">{readingLead}</p> : null}
          <div className="compat-desktop-card compat-hero-unified">
            <ScoreAside variant="standalone" score={score} tagline={productSurface.score_tagline} productSurface={productSurface} />
          </div>
        </>
      )}

      <div className="compat-desktop-card">
        <h2 className="compat-section-title" style={{ marginBottom: "0.75rem" }}>
          Что между вами происходит
        </h2>
        <div className="compat-hero-overview">
          {productSurface.overview_paragraphs.map((p, i) => {
            const text = stripCompatibilityDisplayGarbage(p);
            return text ? <p key={i}>{text}</p> : null;
          })}
        </div>
      </div>

      {personalizedCard}

      <section>
        <h2 className="compat-section-title">Основные слои</h2>
        <div className="compat-block-stack">
          {productSurface.blocks.map((block) => (
            <details key={block.key} className={`compat-accordion ${block.key === "sexuality" ? "compat-accordion--sexuality" : ""}`}>
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

                {block.key === "sexuality" && block.tips && block.tips.length > 0 ? (
                  <div className="compat-callout-go" style={{ background: "rgba(254, 243, 199, 0.45)", borderColor: "rgba(180, 83, 9, 0.18)" }}>
                    <p className="orbit-body-xs" style={{ margin: 0, color: "#92400e", fontWeight: 700 }}>
                      Практические подсказки
                    </p>
                    <ul className="orbit-body-sm" style={{ margin: "0.45rem 0 0", paddingLeft: "1.1rem", color: "#78350f", lineHeight: 1.65 }}>
                      {block.tips.map((tip, tipIdx) => (
                        <li key={tipIdx}>{tip}</li>
                      ))}
                    </ul>
                  </div>
                ) : null}

                <div>
                  <p className="orbit-body-xs" style={{ margin: "0 0 0.45rem", color: "#64748b", fontWeight: 600 }}>
                    Это про вас?
                  </p>
                  <div style={{ display: "flex", flexWrap: "wrap", gap: "0.45rem" }}>
                    {ECHO_OPTIONS.map((opt) => (
                      <button
                        key={opt.id}
                        type="button"
                        title={opt.title}
                        className="orbit-button orbit-button-secondary orbit-button-sm"
                        onClick={() => setBlockEcho((prev) => ({ ...prev, [block.key]: opt.id }))}
                        style={{
                          borderColor: blockEcho[block.key] === opt.id ? "rgba(167, 123, 55, 0.88)" : undefined,
                          background: blockEcho[block.key] === opt.id ? "rgba(242, 220, 181, 0.35)" : undefined,
                        }}
                      >
                        {opt.label}
                      </button>
                    ))}
                  </div>
                  {blockEcho[block.key] ? (
                    <p className="orbit-body-xs" style={{ margin: "0.55rem 0 0", color: "#64748b", lineHeight: 1.6 }}>
                      {blockEcho[block.key] === "yes"
                        ? block.key === "sexuality"
                          ? "Тогда сексуальный слой у вас реально силён — держите рядом ясность про желание, темп и границы."
                          : "Зафиксировали попадание — опирайтесь на формулировки блока в реальных сценах."
                        : blockEcho[block.key] === "partial"
                          ? "Частичное попадание нормально: добирайте контекст через конкретные ситуации, не через знаки."
                          : "Ок — используйте блок как гипотезу и проверяйте по фактам и другим слоям выше."}
                    </p>
                  ) : null}
                </div>
              </div>
            </details>
          ))}
        </div>
      </section>

      <div className="compat-desktop-card">
        <h2 className="compat-section-title" style={{ marginBottom: "0.5rem" }}>
          Кто как ведёт себя в этой паре
        </h2>
        <p className="orbit-body-xs compat-desktop-muted" style={{ margin: 0 }}>
          Роли ниже — про темп и защиту, не про пол. Первый столбец — «ты» ({youColumnLabel}), второй — партнёр ({partnerColumnLabel}).
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
                {group.title}
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

      {extraParagraphs && extraParagraphs.length ? (
        <details className="compat-accordion">
          <summary className="compat-section-title" style={{ cursor: "pointer", listStyle: "none", margin: 0 }}>
            {paragraphsDetailTitle}
          </summary>
          <div style={{ display: "grid", gap: "0.65rem" }}>
            {extraParagraphs.map((paragraph, index) => (
              <p key={index} className="orbit-body-sm" style={{ margin: 0, lineHeight: 1.75, color: "var(--compat-ink-soft)" }}>
                {paragraph}
              </p>
            ))}
            {showParagraphsUpsell ? (
              <p className="orbit-body-xs" style={{ margin: 0, color: "var(--compat-muted)" }}>
                Полный текст и более точный слой — в совместимости по профилям и датам с городом.
              </p>
            ) : null}
          </div>
        </details>
      ) : null}

      <section>
        <h2 className="compat-section-title" style={{ marginBottom: "0.5rem" }}>
          Хочешь разобраться глубже?
        </h2>
        <p className="orbit-body-sm compat-desktop-muted" style={{ margin: "0 0 1rem" }}>
          Если ситуация про конкретное решение — уводим в Guidance. Если хочется понять свой паттерн — в портрет профиля.
        </p>
        <div className="compat-footer-actions">
          <div className="compat-desktop-card">
            <h3 className="orbit-heading-3" style={{ margin: 0, color: "#5f4323" }}>
              Guidance
            </h3>
            <p className="orbit-body-sm compat-desktop-muted" style={{ margin: "0.45rem 0 0" }}>
              Разобрать ситуацию по шагам.
            </p>
            <Link href="/tarot" className="orbit-button orbit-button-primary orbit-button-sm" style={{ textDecoration: "none", marginTop: "0.85rem", display: "inline-flex" }}>
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
              Совместимость
            </h3>
            <p className="orbit-body-sm compat-desktop-muted" style={{ margin: "0.45rem 0 0" }}>
              Уровни по профилям и датам.
            </p>
            <Link href="/compatibility" className="orbit-button orbit-button-secondary orbit-button-sm" style={{ textDecoration: "none", marginTop: "0.85rem", display: "inline-flex" }}>
              Другие уровни
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
