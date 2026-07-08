"use client";

import Link from "next/link";
import { useEffect, useMemo, useState, type ReactNode } from "react";
import type { FirstTodayPackage } from "@/lib/firstTodayPackage";
import { useMeaningRuntime } from "@/hooks/useMeaningRuntime";

type FirstTodaySurfaceProps = {
  displayDate: string;
  package: FirstTodayPackage;
  onVisible?: () => void;
  onActionComplete?: () => void;
};

function Block({
  eyebrow,
  children,
}: {
  eyebrow: string;
  children: ReactNode;
}) {
  return (
    <section className="orbit-card todayflow-inset" style={{ padding: "0.9rem 1rem", borderRadius: "16px" }}>
      <p className="todayflow-eyebrow" style={{ margin: "0 0 0.45rem" }}>
        {eyebrow}
      </p>
      {children}
    </section>
  );
}

export function FirstTodaySurface({ displayDate, package: pkg, onVisible, onActionComplete }: FirstTodaySurfaceProps) {
  const { trackMeaningEvent } = useMeaningRuntime();
  const [actionDone, setActionDone] = useState(false);
  const [whyOpen, setWhyOpen] = useState(false);
  const [symbolicOpen, setSymbolicOpen] = useState(false);

  const hasSymbolic = Boolean(pkg.symbolic.tarot || pkg.symbolic.number);

  useEffect(() => {
    onVisible?.();
  }, [onVisible]);

  const markActionDone = () => {
    if (actionDone) return;
    setActionDone(true);
    onActionComplete?.();
    trackMeaningEvent({
      event_type: "action_option_selected",
      event_source: "today",
      quality_score: 1,
      payload: { first_today: true, primary_step: true },
      idempotency_key: `first-today-action-${new Date().toISOString().split("T")[0]}`,
      refreshRings: false,
    });
  };

  const whyPreview = useMemo(() => pkg.why.lines.slice(0, 2).join(" "), [pkg.why.lines]);

  return (
    <div id="today-first-day-surface" style={{ maxWidth: "640px", margin: "0 auto", width: "100%" }}>
      <header style={{ marginBottom: "1rem" }}>
        <p
          className="orbit-body-xs"
          style={{
            margin: 0,
            color: "#a67c3a",
            textTransform: "uppercase",
            letterSpacing: "0.08em",
            fontWeight: 700,
          }}
        >
          Твой первый Today
        </p>
        <p className="orbit-body-sm" style={{ margin: "0.45rem 0 0", color: "#64748b", lineHeight: 1.6 }}>
          {displayDate} · без ритуала — сразу к делу
        </p>
      </header>

      <div style={{ display: "flex", flexDirection: "column", gap: "0.65rem" }}>
        <Block eyebrow="Тема дня">
          <p className="orbit-body-sm" style={{ margin: 0, fontWeight: 700, color: "#3f3428", lineHeight: 1.5 }}>
            {pkg.theme.headline}
          </p>
          <p className="orbit-body-sm" style={{ margin: "0.45rem 0 0", color: "#5f4930", lineHeight: 1.55 }}>
            {pkg.theme.body}
          </p>
        </Block>

        <section
          className="orbit-card"
          style={{
            padding: "0.75rem 0.9rem",
            borderRadius: "14px",
            background: "rgba(255, 251, 243, 0.95)",
            border: "1px solid rgba(201, 168, 115, 0.22)",
          }}
        >
          <p className="orbit-body-xs" style={{ margin: 0, color: "#8f7756", fontWeight: 700 }}>
            {pkg.progress.statusLabel}
          </p>
          <p className="orbit-body-xs" style={{ margin: "0.3rem 0 0", color: "#5f4930", lineHeight: 1.55 }}>
            {pkg.progress.hint}
          </p>
        </section>

        <Block eyebrow="Три сферы дня">
          <div style={{ display: "flex", flexDirection: "column", gap: "0.55rem" }}>
            {pkg.insight.spheres.map((sphere) => (
              <div
                key={sphere.id}
                style={{
                  padding: "0.55rem 0.65rem",
                  borderRadius: "12px",
                  background: "rgba(255,255,255,0.72)",
                  border: "1px solid rgba(201, 168, 115, 0.18)",
                }}
              >
                <p className="orbit-body-xs" style={{ margin: 0, fontWeight: 700, color: "#8f7756" }}>
                  {sphere.label}
                </p>
                <p className="orbit-body-sm" style={{ margin: "0.25rem 0 0", color: "#5f4930", lineHeight: 1.55 }}>
                  {sphere.line}
                </p>
              </div>
            ))}
          </div>
        </Block>

        <Block eyebrow="Главный шаг">
          <p
            className="orbit-body-sm"
            style={{
              margin: 0,
              fontWeight: 600,
              color: actionDone ? "#64748b" : "#3f3428",
              lineHeight: 1.55,
              textDecoration: actionDone ? "line-through" : "none",
            }}
          >
            {pkg.action.primary}
          </p>
          {pkg.action.supports.length ? (
            <ul style={{ margin: "0.55rem 0 0", paddingLeft: "1.1rem", color: "#5f4930" }}>
              {pkg.action.supports.map((line) => (
                <li key={line} className="orbit-body-xs" style={{ lineHeight: 1.55, marginBottom: "0.2rem" }}>
                  {line}
                </li>
              ))}
            </ul>
          ) : null}
          {actionDone ? (
            <p className="orbit-body-xs" style={{ margin: "0.45rem 0 0", color: "#166534", lineHeight: 1.55 }}>
              {pkg.action.afterComplete}
            </p>
          ) : (
            <button
              type="button"
              className="orbit-button orbit-button-primary orbit-button-sm"
              style={{ marginTop: "0.65rem" }}
              onClick={markActionDone}
            >
              Отметить шаг
            </button>
          )}
        </Block>

        <section className="orbit-card" style={{ padding: "0.75rem 0.9rem", borderRadius: "14px" }}>
          <button
            type="button"
            onClick={() => {
              setWhyOpen((v) => !v);
              if (!whyOpen) {
                trackMeaningEvent({
                  event_type: "today_guide_why_opened",
                  event_source: "today",
                  payload: { first_today: true },
                  idempotency_key: `first-today-why-${new Date().toISOString().split("T")[0]}`,
                  refreshRings: false,
                });
              }
            }}
            className="orbit-button orbit-button-secondary orbit-button-sm"
            style={{ width: "100%" }}
          >
            {whyOpen ? "Скрыть почему так" : "Почему так сегодня?"}
          </button>
          {whyOpen ? (
            <ul style={{ margin: "0.65rem 0 0", paddingLeft: "1.1rem", color: "#5f4930" }}>
              {pkg.why.lines.map((line) => (
                <li key={line} className="orbit-body-xs" style={{ lineHeight: 1.55, marginBottom: "0.25rem" }}>
                  {line}
                </li>
              ))}
            </ul>
          ) : (
            <p className="orbit-body-xs" style={{ margin: "0.45rem 0 0", color: "#7a623d", lineHeight: 1.55 }}>
              {whyPreview}
            </p>
          )}
        </section>

        {hasSymbolic ? (
          <section className="orbit-card" style={{ padding: "0.75rem 0.9rem", borderRadius: "14px" }}>
            <button
              type="button"
              onClick={() => setSymbolicOpen((v) => !v)}
              className="orbit-button orbit-button-secondary orbit-button-sm"
              style={{ width: "100%" }}
            >
              {symbolicOpen ? "Скрыть символический слой" : "Символический слой (необязательно)"}
            </button>
            {symbolicOpen ? (
              <div style={{ marginTop: "0.55rem", display: "grid", gap: "0.35rem" }}>
                {pkg.symbolic.tarot ? (
                  <p className="orbit-body-xs" style={{ margin: 0, color: "#5f4930" }}>
                    Карта дня: {pkg.symbolic.tarot}
                  </p>
                ) : null}
                {pkg.symbolic.number ? (
                  <p className="orbit-body-xs" style={{ margin: 0, color: "#5f4930" }}>
                    Число дня: {pkg.symbolic.number}
                  </p>
                ) : null}
              </div>
            ) : null}
          </section>
        ) : null}
      </div>

      <div
        className="orbit-card"
        style={{
          marginTop: "1.1rem",
          padding: "1rem",
          borderRadius: "18px",
          background: "linear-gradient(135deg, #fffaf0 0%, #ffffff 45%, #f8fafc 100%)",
          border: "1px solid #f0e1c7",
        }}
      >
        <h2 className="orbit-heading-3" style={{ margin: "0 0 0.35rem" }}>
          {pkg.depth.label}
        </h2>
        <p className="orbit-body-sm" style={{ margin: "0 0 0.85rem", color: "#475569", lineHeight: 1.6 }}>
          Первый день закрыт. Можно углубиться в карту или вернуться завтра — Today уже знает твой фокус и состояние.
        </p>
        <div style={{ display: "flex", flexWrap: "wrap", gap: "0.55rem" }}>
          <Link href={pkg.depth.href} className="orbit-button orbit-button-primary" style={{ textDecoration: "none" }}>
            {pkg.depth.label}
          </Link>
          <Link href="/today" className="orbit-button orbit-button-secondary" style={{ textDecoration: "none" }}>
            Обычный Today
          </Link>
        </div>
      </div>
    </div>
  );
}
