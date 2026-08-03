"use client";

import styles from "@/components/today/composition/TodayActNav.module.css";

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

export function TodayActNav({ items, activeIndex, onSelect }: Props) {
  if (items.length === 0) return null;

  const controlled = typeof onSelect === "function";

  return (
    <nav className={styles.nav} aria-label="Экраны дня" data-testid="today-act-nav">
      <ul className={styles.list}>
        {items.map((item, index) => {
          const isActive = controlled ? activeIndex === item.step : index === 0;
          if (controlled) {
            return (
              <li key={`${item.label}-${item.step}`}>
                <button
                  type="button"
                  className={isActive ? styles.linkActive : styles.link}
                  aria-current={isActive ? "true" : undefined}
                  data-testid={`today-act-nav-${item.step}`}
                  onClick={() => onSelect(item.step)}
                >
                  <span className={styles.dot} aria-hidden />
                  <span className={styles.label}>{item.label}</span>
                </button>
              </li>
            );
          }
          return (
            <li key={item.href ?? `${item.label}-${item.step}`}>
              <a
                href={item.href}
                className={isActive ? styles.linkActive : styles.link}
                aria-current={isActive ? "true" : undefined}
                onClick={(e) => {
                  const id = (item.href || "").replace(/^#/, "");
                  const el = document.getElementById(id);
                  if (!el) return;
                  e.preventDefault();
                  el.scrollIntoView({ behavior: "smooth", block: "start" });
                  if (typeof window !== "undefined" && window.history?.replaceState) {
                    window.history.replaceState(null, "", item.href);
                  }
                }}
              >
                <span className={styles.dot} aria-hidden />
                <span className={styles.label}>{item.label}</span>
              </a>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
