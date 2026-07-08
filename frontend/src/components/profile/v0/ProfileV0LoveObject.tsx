"use client";

import { useEffect, useState } from "react";
import type { ProfileV0LoveCard } from "@/lib/profilePage/buildProfileV0SphereCards";
import { LoveOrbitObject } from "./sphere/LoveOrbitObject";
import styles from "./profileV0.module.css";

type LoveFacetKey = "needs" | "mistakes" | "redFlags";

const LOVE_FACETS: { key: LoveFacetKey; label: string }[] = [
  { key: "needs", label: "Потребность" },
  { key: "mistakes", label: "Ошибка" },
  { key: "redFlags", label: "Red flag" },
];

export function ProfileV0LoveObject({ love }: { love: ProfileV0LoveCard }) {
  const [expanded, setExpanded] = useState(false);
  const [activeFacet, setActiveFacet] = useState<LoveFacetKey | null>(null);

  const facets = LOVE_FACETS.map(({ key, label }) => ({
    key,
    label,
    body: love.expand[key],
  })).filter((f) => f.body?.trim());

  useEffect(() => {
    if (!expanded) setActiveFacet(null);
  }, [expanded]);

  const activeDetail = facets.find((f) => f.key === activeFacet);

  return (
    <article className={styles.dualityLove} aria-label="Любовь">
      <div className={styles.dualityLoveOrbitDecor} aria-hidden />
      <div className={styles.dualityLoveSymbol}>
        <LoveOrbitObject size={92} />
      </div>

      <p className={styles.dualityLoveLabel}>Любовь</p>
      <h3 className={styles.dualityLoveTitle}>Как ты строишь близость</h3>
      <p className={styles.dualityLoveMain}>{love.style}</p>

      <div className={styles.dualityLoveSignals}>
        {love.strength ? (
          <p className={styles.dualityLoveSignal}>
            <span className={styles.dualityLoveSignalLabel}>Сильная сторона:</span> {love.strength}
          </p>
        ) : null}
        {love.whatMatters ? (
          <p className={styles.dualityLoveSignal}>
            <span className={styles.dualityLoveSignalLabel}>Важно:</span> {love.whatMatters}
          </p>
        ) : null}
        {love.watchout ? (
          <p className={styles.dualityLoveSignalMuted}>
            <span className={styles.dualityLoveSignalLabel}>Мешает:</span> {love.watchout}
          </p>
        ) : null}
      </div>

      {facets.length ? (
        <button
          type="button"
          className={styles.cardCtaLink}
          aria-expanded={expanded}
          onClick={() => setExpanded((v) => !v)}
        >
          {expanded ? "Свернуть" : "Подробнее"}
        </button>
      ) : null}

      {expanded && facets.length ? (
        <div className={styles.dualityFacetRow}>
          {facets.map((facet) => (
            <button
              key={facet.key}
              type="button"
              className={`${styles.dualityFacetBtn} ${styles.dualityFacetBtnLove} ${
                activeFacet === facet.key ? styles.dualityFacetBtnActive : ""
              }`}
              aria-expanded={activeFacet === facet.key}
              onClick={() => setActiveFacet((prev) => (prev === facet.key ? null : facet.key))}
            >
              {facet.label}
            </button>
          ))}
        </div>
      ) : null}

      {activeDetail ? (
        <div className={`${styles.dualityDetailPanel} ${styles.dualityDetailPanelLove}`} role="region" aria-live="polite">
          <p className={styles.dualityDetailCaption}>{activeDetail.label}</p>
          <p className={styles.dualityDetailBody}>{activeDetail.body}</p>
        </div>
      ) : null}
    </article>
  );
}
