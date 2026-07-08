"use client";

import type { TodayUnifiedSynthesis } from "@/lib/todayUnifiedSynthesis";

type Props = {
  model: TodayUnifiedSynthesis;
  loading?: boolean;
};

export function TodaySynthesisBlock({ model, loading = false }: Props) {
  return (
    <section
      className="todayflow-surface-primary todayflow-inset"
      data-testid="today-synthesis-block"
      style={{
        padding: "1.1rem 1rem",
        borderRadius: 18,
        border: "1px solid rgba(201,168,115,0.28)",
        background: "rgba(255,255,255,0.94)",
      }}
    >
      <p className="todayflow-eyebrow" style={{ margin: 0 }}>{model.eyebrow}</p>
      {loading ? (
        <div
          className="today-experience-shimmer"
          style={{ height: "1.5rem", marginTop: "0.5rem", borderRadius: 8 }}
          aria-hidden
        />
      ) : (
        <>
          <h2 className="orbit-heading-2" style={{ margin: "0.35rem 0 0", lineHeight: 1.35, color: "#1f1a16" }}>
            {model.headline}
          </h2>
          {model.paragraphs.map((para) => (
            <p
              key={para}
              className="orbit-body-sm"
              style={{ margin: "0.55rem 0 0", lineHeight: 1.58, color: "#3d3228" }}
            >
              {para}
            </p>
          ))}
        </>
      )}
    </section>
  );
}
