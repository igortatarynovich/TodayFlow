"use client";

import Link from "next/link";

export type ProfileWhatNextItem = {
  title: string;
  body: string;
  href: string;
  cta: string;
};

export function ProfileWhatNextCard({ routes }: { routes: ProfileWhatNextItem[] }) {
  if (!routes.length) return null;
  return (
    <div
      className="todayflow-panel"
      style={{
        borderRadius: "22px",
        padding: "0.95rem 1rem",
        border: "1px solid rgba(201, 168, 115, 0.24)",
        background: "linear-gradient(145deg, rgba(255,253,249,0.98) 0%, rgba(252,246,236,0.93) 100%)",
      }}
    >
      <p className="orbit-body-xs" style={{ margin: 0, color: "#8f7756", textTransform: "uppercase", letterSpacing: "0.08em", fontWeight: 700 }}>
        Что дальше?
      </p>
      <p className="orbit-body-xs" style={{ margin: "0.4rem 0 0", color: "#5c4426", lineHeight: 1.65 }}>
        Выбери, что сделать с этим дальше.
      </p>
      <div style={{ display: "grid", gap: "0.55rem", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", marginTop: "0.75rem" }}>
        {routes.map((route) => (
          <Link
            key={route.href}
            href={route.href}
            style={{
              textDecoration: "none",
              color: "inherit",
              borderRadius: "16px",
              padding: "0.75rem 0.85rem",
              border: "1px solid rgba(201, 168, 115, 0.18)",
              background: "rgba(255,255,255,0.88)",
              display: "grid",
              gap: "0.3rem",
            }}
          >
            <p className="orbit-body-sm" style={{ margin: 0, color: "#37281a", fontWeight: 700, lineHeight: 1.5 }}>
              {route.title}
            </p>
            <p className="orbit-body-xs" style={{ margin: 0, color: "#6b5b48", lineHeight: 1.55 }}>
              {route.body}
            </p>
            <p className="orbit-body-xs" style={{ margin: "0.1rem 0 0", color: "#a67c3a", fontWeight: 700 }}>
              {route.cta}
            </p>
          </Link>
        ))}
      </div>
    </div>
  );
}
