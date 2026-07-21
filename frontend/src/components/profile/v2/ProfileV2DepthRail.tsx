"use client";

import { useEffect, useState } from "react";
import {
  PROFILE_V2_DEPTH_NAV,
  type ProfileV2ZoneId,
} from "@/components/profile/v2/profileV2SystemCopy";
import styles from "@/components/profile/v2/profileV2System.module.css";

function zoneDomId(zone: ProfileV2ZoneId): string {
  return `profile-v2-${zone}`;
}

/** Right-rail section jump for Profile v2 — keeps the main column for content. */
export function ProfileV2DepthRail() {
  const [activeZone, setActiveZone] = useState<ProfileV2ZoneId>("identity");

  useEffect(() => {
    const nodes = PROFILE_V2_DEPTH_NAV.map((item) => document.getElementById(zoneDomId(item.id))).filter(
      (node): node is HTMLElement => Boolean(node),
    );
    if (!nodes.length) return;

    const observer = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter((entry) => entry.isIntersecting)
          .sort((a, b) => b.intersectionRatio - a.intersectionRatio);
        const id = visible[0]?.target.id?.replace(/^profile-v2-/, "") as ProfileV2ZoneId | undefined;
        if (id && PROFILE_V2_DEPTH_NAV.some((item) => item.id === id)) {
          setActiveZone(id);
        }
      },
      { rootMargin: "-20% 0px -55% 0px", threshold: [0.15, 0.35, 0.55] },
    );

    nodes.forEach((node) => observer.observe(node));
    return () => observer.disconnect();
  }, []);

  return (
    <nav className={styles.railDepthNav} aria-label="Разделы профиля" data-testid="profile-v2-depth-rail">
      <p className={styles.railDepthEyebrow}>По профилю</p>
      <ol className={styles.railDepthList}>
        {PROFILE_V2_DEPTH_NAV.map((item) => {
          const active = activeZone === item.id;
          return (
            <li key={item.id}>
              <a
                href={`#${zoneDomId(item.id)}`}
                className={`${styles.railDepthStep} ${active ? styles.railDepthStepActive : ""}`.trim()}
                aria-current={active ? "true" : undefined}
                onClick={() => setActiveZone(item.id)}
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
    </nav>
  );
}

/** Compact in-main jump strip when the shell rail is hidden (narrow viewports). */
export function ProfileV2MobileDepthJump() {
  return (
    <nav className={styles.mobileDepthJump} aria-label="Разделы профиля" data-testid="profile-v2-depth-jump">
      {PROFILE_V2_DEPTH_NAV.map((item) => (
        <a key={item.id} href={`#${zoneDomId(item.id)}`} className={styles.mobileDepthChip}>
          {item.title}
        </a>
      ))}
    </nav>
  );
}
