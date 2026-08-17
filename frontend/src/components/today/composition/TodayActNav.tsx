"use client";

import { DsChip, DsChipCluster, DsSurface } from "@/design-system";
import layout from "@/design-system/compositions/dsCompositions.module.css";
import { joinClass } from "@/design-system/utils/joinClass";

export type TodayActNavItem = {
  step: number;
  label: string;
  /** Optional legacy hash — ignored when onSelect is provided. */
  href?: string;
};

type Props = {
  items: TodayActNavItem[];
  /** Controlled active index (ScreenFlow). */
  activeIndex?: number;
  /** When set, nav uses buttons + onSelect instead of scrollIntoView. */
  onSelect?: (index: number) => void;
};

/**
 * @deprecated Product Today does not mount this strip (SCREEN_FLOW_V1 §1.5).
 * Progress chrome = ScreenFlow dots + swipe. Kept for fixtures / possible reuse.
 * Form Kit: sticky glass + chips (FOUNDATION_UI §15.8).
 */
export function TodayActNav({ items, activeIndex, onSelect }: Props) {
  if (items.length === 0) return null;

  const controlled = typeof onSelect === "function";

  const scrollToHref = (href?: string) => {
    const id = (href || "").replace(/^#/, "");
    const el = document.getElementById(id);
    if (!el) return;
    el.scrollIntoView({ behavior: "smooth", block: "start" });
    if (typeof window !== "undefined" && window.history?.replaceState && href) {
      window.history.replaceState(null, "", href);
    }
  };

  return (
    <DsSurface
      as="nav"
      tone="glass"
      className={joinClass(layout.stickyTop, layout.navStrip)}
      aria-label="Экраны дня"
      testId="today-act-nav"
    >
      <DsChipCluster className={layout.chipScroll}>
        {items.map((item, index) => {
          const isActive = controlled ? activeIndex === item.step : index === 0;
          return (
            <DsChip
              key={controlled ? `${item.label}-${item.step}` : item.href ?? `${item.label}-${item.step}`}
              selected={isActive}
              testId={`today-act-nav-${item.step}`}
              onClick={() => {
                if (controlled) onSelect(item.step);
                else scrollToHref(item.href);
              }}
            >
              {item.label}
            </DsChip>
          );
        })}
      </DsChipCluster>
    </DsSurface>
  );
}
