"use client";

import { useEffect, useState } from "react";
import styles from "@/components/today/composition/TodayActNav.module.css";

export type TodayActNavItem = {
  step: number;
  label: string;
  href: string;
};

type Props = {
  items: TodayActNavItem[];
};

export function TodayActNav({ items }: Props) {
  const [active, setActive] = useState<string | null>(items[0]?.href ?? null);

  useEffect(() => {
    if (typeof window === "undefined" || items.length === 0) return;
    const nodes = items
      .map((item) => document.getElementById(item.href.replace(/^#/, "")))
      .filter((n): n is HTMLElement => Boolean(n));
    if (nodes.length === 0) return;

    const observer = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter((e) => e.isIntersecting)
          .sort((a, b) => b.intersectionRatio - a.intersectionRatio);
        const top = visible[0];
        if (top?.target?.id) setActive(`#${top.target.id}`);
      },
      { rootMargin: "-30% 0px -45% 0px", threshold: [0.15, 0.35, 0.55] },
    );
    nodes.forEach((n) => observer.observe(n));
    return () => observer.disconnect();
  }, [items]);

  if (items.length === 0) return null;

  return (
    <nav className={styles.nav} aria-label="Экраны дня" data-testid="today-act-nav">
      <ul className={styles.list}>
        {items.map((item) => {
          const isActive = active === item.href;
          return (
            <li key={item.href}>
              <a
                href={item.href}
                className={isActive ? styles.linkActive : styles.link}
                aria-current={isActive ? "true" : undefined}
                onClick={(e) => {
                  const id = item.href.replace(/^#/, "");
                  const el = document.getElementById(id);
                  if (!el) return;
                  e.preventDefault();
                  el.scrollIntoView({ behavior: "smooth", block: "start" });
                  setActive(item.href);
                  if (typeof window !== "undefined" && window.history?.replaceState) {
                    window.history.replaceState(null, "", item.href);
                  }
                }}
              >
                <span className={styles.step}>{item.step}</span>
                <span className={styles.label}>{item.label}</span>
              </a>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
