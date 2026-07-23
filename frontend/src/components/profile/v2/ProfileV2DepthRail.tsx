"use client";

import { useEffect, useState } from "react";
import {
  PROFILE_V2_DEPTH_NAV,
  PROFILE_V2_EXPLORE_NAV,
  type ProfileV2ZoneId,
} from "@/components/profile/v2/profileV2SystemCopy";
import styles from "@/components/profile/v2/profileV2System.module.css";

function zoneDomId(zone: ProfileV2ZoneId): string {
  return `profile-v2-${zone}`;
}

const ALL_NAV_IDS: ProfileV2ZoneId[] = [
  ...PROFILE_V2_DEPTH_NAV.map((i) => i.id),
  ...PROFILE_V2_EXPLORE_NAV.map((i) => i.id),
];

function scrollToZone(zone: ProfileV2ZoneId) {
  const el = document.getElementById(zoneDomId(zone));
  if (!el) return;
  const reduce =
    typeof window !== "undefined" &&
    window.matchMedia?.("(prefers-reduced-motion: reduce)")?.matches;
  el.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "start" });
}

/** Right-rail journey jump — Explore/natal after the five steps. */
export function ProfileV2DepthRail() {
  const [activeZone, setActiveZone] = useState<ProfileV2ZoneId>("recognition");

  useEffect(() => {
    if (typeof IntersectionObserver === "undefined") return;

    const nodes = ALL_NAV_IDS.map((id) => document.getElementById(zoneDomId(id))).filter(
      (node): node is HTMLElement => Boolean(node),
    );
    if (!nodes.length) return;

    const observer = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter((entry) => entry.isIntersecting)
          .sort((a, b) => b.intersectionRatio - a.intersectionRatio);
        const id = visible[0]?.target.id?.replace(/^profile-v2-/, "") as ProfileV2ZoneId | undefined;
        if (id && ALL_NAV_IDS.includes(id)) {
          setActiveZone(id);
        }
      },
      { rootMargin: "-20% 0px -55% 0px", threshold: [0.15, 0.35, 0.55] },
    );

    nodes.forEach((node) => observer.observe(node));
    return () => observer.disconnect();
  }, []);

  return (
    <nav className={styles.railDepthNav} aria-label="Путешествие профиля" data-testid="profile-v2-depth-rail">
      <p className={styles.railDepthEyebrow}>Твоя история в 5 шагах</p>
      <ol className={styles.railDepthList}>
        {PROFILE_V2_DEPTH_NAV.map((item) => {
          const active = activeZone === item.id;
          return (
            <li key={item.id}>
              <a
                href={`#${zoneDomId(item.id)}`}
                className={`${styles.railDepthStep} ${active ? styles.railDepthStepActive : ""}`.trim()}
                aria-current={active ? "true" : undefined}
                onClick={(event) => {
                  event.preventDefault();
                  setActiveZone(item.id);
                  scrollToZone(item.id);
                }}
              >
                <span className={styles.railDepthBadge}>{item.step}</span>
                <span className={styles.railDepthCopy}>
                  <span className={styles.railDepthTitle}>{item.title}</span>
                  <span className={styles.railDepthHint}>{item.hint}</span>
                </span>
              </a>
            </li>
          );
        })}
      </ol>
      <div className={styles.railExploreBlock}>
        <p className={styles.railDepthEyebrow}>Исследовать</p>
        <ul className={styles.railDepthList}>
          {PROFILE_V2_EXPLORE_NAV.map((item) => {
            const active = activeZone === item.id;
            return (
              <li key={item.id}>
                <a
                  href={`#${zoneDomId(item.id)}`}
                  className={`${styles.railDepthStep} ${active ? styles.railDepthStepActive : ""}`.trim()}
                  aria-current={active ? "true" : undefined}
                  onClick={(event) => {
                    event.preventDefault();
                    setActiveZone(item.id);
                    scrollToZone(item.id);
                  }}
                >
                  <span className={styles.railDepthCopy}>
                    <span className={styles.railDepthTitle}>{item.title}</span>
                    <span className={styles.railDepthHint}>{item.hint}</span>
                  </span>
                </a>
              </li>
            );
          })}
        </ul>
      </div>
    </nav>
  );
}

/** Compact in-main jump strip when the shell rail is hidden (narrow viewports). */
export function ProfileV2MobileDepthJump() {
  return (
    <nav className={styles.mobileDepthJump} aria-label="Путешествие профиля" data-testid="profile-v2-depth-jump">
      {PROFILE_V2_DEPTH_NAV.map((item) => (
        <a
          key={item.id}
          href={`#${zoneDomId(item.id)}`}
          className={styles.mobileDepthChip}
          onClick={(event) => {
            event.preventDefault();
            scrollToZone(item.id);
          }}
        >
          {item.title}
        </a>
      ))}
      <a
        href={`#${zoneDomId("explore")}`}
        className={styles.mobileDepthChip}
        onClick={(event) => {
          event.preventDefault();
          scrollToZone("explore");
        }}
      >
        Детали
      </a>
    </nav>
  );
}
