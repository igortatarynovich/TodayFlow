"use client";

import type { TodayFlowTab } from "@/components/today/todayPageUtils";
import { TODAY_FLOW_TABS } from "@/components/today/todayPageUtils";
import { RITUAL_COPY } from "@/components/today/todayRitualCopy";

export function TodayFlowTabs({
  active,
  onChange,
}: {
  active: TodayFlowTab;
  onChange: (tab: TodayFlowTab) => void;
}) {
  return (
    <nav
      aria-label={RITUAL_COPY.todayFlowTabsNavAriaLabel}
      className="todayflow-tabs-nav"
      style={{
        position: "sticky",
        top: 0,
        zIndex: 15,
        marginBottom: "0.85rem",
        padding: "0.35rem 0",
        background: "linear-gradient(180deg, rgba(247,242,234,0.98) 0%, rgba(247,242,234,0.92) 70%, transparent 100%)",
        backdropFilter: "blur(8px)",
      }}
    >
      <style jsx>{`
        .todayflow-tabs-list {
          display: flex;
          gap: 0.28rem;
          flex-wrap: wrap;
          justify-content: flex-start;
          padding: 0.25rem;
          border-radius: 14px;
          border: 1px solid rgba(201, 168, 115, 0.35);
          background: rgba(255, 252, 247, 0.95);
          box-shadow: 0 6px 20px rgba(122, 92, 48, 0.08);
        }

        .todayflow-tabs-button {
          flex: 1 1 auto;
          min-width: min(100%, 108px);
          font-weight: 600;
          font-size: 0.78rem;
          padding: 0.4rem 0.5rem;
        }

        @media (max-width: 768px) {
          .todayflow-tabs-nav {
            margin-left: -0.2rem;
            margin-right: -0.2rem;
          }

          .todayflow-tabs-list {
            flex-wrap: nowrap;
            overflow-x: auto;
            scrollbar-width: none;
            -ms-overflow-style: none;
            padding: 0.22rem;
            scroll-snap-type: x proximity;
          }

          .todayflow-tabs-list::-webkit-scrollbar {
            display: none;
          }

          .todayflow-tabs-button {
            flex: 0 0 auto;
            min-width: 96px;
            scroll-snap-align: start;
            white-space: nowrap;
            font-size: 0.74rem;
            padding: 0.38rem 0.48rem;
          }
        }
      `}</style>
      <div
        role="tablist"
        className="todayflow-tabs-list"
      >
        {TODAY_FLOW_TABS.map((t, i) => {
          const selected = active === t.id;
          return (
            <button
              key={t.id}
              type="button"
              role="tab"
              aria-selected={selected}
              aria-label={`${i + 1}. ${t.label}: ${t.description}`}
              onClick={() => onChange(t.id)}
              className={`orbit-button orbit-button-sm todayflow-tabs-button ${selected ? "orbit-button-primary" : "orbit-button-secondary"}`}
              style={{ fontWeight: selected ? 700 : 600 }}
            >
              <span style={{ opacity: 0.72, marginRight: "0.2rem" }}>{i + 1}</span>
              {t.label}
            </button>
          );
        })}
      </div>
    </nav>
  );
}
