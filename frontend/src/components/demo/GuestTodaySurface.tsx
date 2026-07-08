"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { buildGuestTodayPackage } from "@/lib/demoTodayPackage";
import { buildAuthHref } from "@/lib/authRedirect";

type GuestTodaySurfaceProps = {
  showAuthenticatedBanner?: boolean;
};

function formatDisplayDate(): string {
  return new Intl.DateTimeFormat("ru-RU", {
    weekday: "long",
    day: "numeric",
    month: "long",
  }).format(new Date());
}

export function GuestTodaySurface({ showAuthenticatedBanner = false }: GuestTodaySurfaceProps) {
  const pkg = useMemo(() => buildGuestTodayPackage(), []);
  const [actionDone, setActionDone] = useState(false);
  const signupHref = buildAuthHref("signup", "/onboarding/core");

  return (
    <div style={{ maxWidth: "640px", margin: "0 auto", width: "100%" }}>
      {showAuthenticatedBanner ? (
        <div
          className="orbit-card"
          style={{
            padding: "0.75rem 0.9rem",
            marginBottom: "0.85rem",
            borderRadius: "14px",
            background: "rgba(236, 253, 245, 0.92)",
            border: "1px solid rgba(52, 211, 153, 0.24)",
          }}
        >
          <p className="orbit-body-sm" style={{ margin: 0, color: "#166534", lineHeight: 1.55 }}>
            Ты уже в аккаунте.{" "}
            <Link href="/today" style={{ color: "#15803d", fontWeight: 700 }}>
              Открыть свой Today →
            </Link>
          </p>
        </div>
      ) : null}

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
          Демо · Today
        </p>
        <h1 className="orbit-heading-2" style={{ margin: "0.35rem 0 0", lineHeight: 1.2, color: "#37281a" }}>
          Как может выглядеть твой день
        </h1>
        <p className="orbit-body-sm" style={{ margin: "0.45rem 0 0", color: "#64748b", lineHeight: 1.6 }}>
          {formatDisplayDate()} · без email и без карты рождения
        </p>
      </header>

      <div style={{ display: "flex", flexDirection: "column", gap: "0.65rem" }}>
        <section className="orbit-card todayflow-inset" style={{ padding: "0.9rem 1rem", borderRadius: "16px" }}>
          <p className="todayflow-eyebrow" style={{ margin: "0 0 0.45rem" }}>
            Тема дня
          </p>
          <p className="orbit-body-sm" style={{ margin: 0, fontWeight: 700, color: "#3f3428", lineHeight: 1.5 }}>
            {pkg.theme.headline}
          </p>
          <p className="orbit-body-sm" style={{ margin: "0.45rem 0 0", color: "#5f4930", lineHeight: 1.55 }}>
            {pkg.theme.body}
          </p>
        </section>

        <section
          className="orbit-card"
          style={{
            padding: "0.75rem 0.9rem",
            borderRadius: "14px",
            background: "rgba(255, 251, 243, 0.95)",
            border: "1px solid rgba(201, 168, 115, 0.22)",
          }}
        >
          <p className="orbit-body-xs" style={{ margin: 0, color: "#8f7756", fontWeight: 600 }}>
            {pkg.progress.statusLabel}
          </p>
          <p className="orbit-body-xs" style={{ margin: "0.3rem 0 0", color: "#5f4930", lineHeight: 1.55 }}>
            {pkg.progress.hint}
          </p>
        </section>

        <section className="orbit-card todayflow-inset" style={{ padding: "0.9rem 1rem", borderRadius: "16px" }}>
          <p className="todayflow-eyebrow" style={{ margin: "0 0 0.45rem" }}>
            {pkg.insight.label}
          </p>
          <p className="orbit-body-sm" style={{ margin: 0, color: "#5f4930", lineHeight: 1.55 }}>
            {pkg.insight.body}
          </p>
        </section>

        <section className="orbit-card todayflow-inset" style={{ padding: "0.9rem 1rem", borderRadius: "16px" }}>
          <p className="todayflow-eyebrow" style={{ margin: "0 0 0.45rem" }}>
            Главный шаг
          </p>
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
          {actionDone ? (
            <p className="orbit-body-xs" style={{ margin: "0.45rem 0 0", color: "#166534", lineHeight: 1.55 }}>
              {pkg.action.afterComplete}
            </p>
          ) : (
            <button
              type="button"
              className="orbit-button orbit-button-secondary orbit-button-sm"
              style={{ marginTop: "0.65rem" }}
              onClick={() => setActionDone(true)}
            >
              Отметить шаг
            </button>
          )}
        </section>
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
          Собрать свой день за ~30 секунд
        </h2>
        <p className="orbit-body-sm" style={{ margin: "0 0 0.85rem", color: "#475569", lineHeight: 1.6 }}>
          После регистрации — имя, дата и город; затем два коротких выбора. Персональный Today без лишних экранов.
        </p>
        <div style={{ display: "flex", flexWrap: "wrap", gap: "0.55rem" }}>
          <Link href={signupHref} className="orbit-button orbit-button-primary" style={{ textDecoration: "none" }}>
            Начать бесплатно
          </Link>
          <Link href="/" className="orbit-button orbit-button-secondary" style={{ textDecoration: "none" }}>
            На главную
          </Link>
        </div>
      </div>
    </div>
  );
}
