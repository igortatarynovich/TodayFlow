"use client";

import { useEffect, useState } from "react";
import type { ProfileV0SocialMirrorCard } from "@/lib/profilePage/buildProfileV0SphereCards";
import styles from "./profileV0.module.css";

type MirrorFacetKey = "firstImpression" | "broadcast" | "blindSpot";

const MIRROR_FACETS: { key: MirrorFacetKey; label: string }[] = [
  { key: "firstImpression", label: "Первое впечатление" },
  { key: "broadcast", label: "Что транслируешь" },
  { key: "blindSpot", label: "Слепая зона" },
];

export function ProfileV0SocialMirrorBlock({ mirror }: { mirror: ProfileV0SocialMirrorCard }) {
  const [expanded, setExpanded] = useState(false);
  const [activeFacet, setActiveFacet] = useState<MirrorFacetKey | null>(null);

  const facets = MIRROR_FACETS.map(({ key, label }) => ({
    key,
    label,
    body: mirror.expand[key],
  })).filter((f) => f.body?.trim());

  useEffect(() => {
    if (!expanded) setActiveFacet(null);
  }, [expanded]);

  const activeDetail = facets.find((f) => f.key === activeFacet);

  return (
    <section className={styles.nameCodeBlock} aria-label="Как тебя видят другие">
      <div className={styles.nameCodeRule} aria-hidden />

      <div className={styles.nameCodeInner}>
        <p className={styles.nameCodeLabel}>Как тебя видят</p>

        <div className={styles.nameCodeHeadline}>
          <p className={styles.nameCodeMeaning}>{mirror.lead}</p>
        </div>

        {mirror.observations.length ? (
          <ul className={styles.nameCodeQualities}>
            {mirror.observations.map((observation) => (
              <li key={observation} className={styles.nameCodeQuality}>
                {observation}
              </li>
            ))}
          </ul>
        ) : null}

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
          <div className={styles.nameCodeFacetRow}>
            {facets.map((facet) => (
              <button
                key={facet.key}
                type="button"
                className={`${styles.nameCodeFacetBtn} ${
                  activeFacet === facet.key ? styles.nameCodeFacetBtnActive : ""
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
          <div className={styles.nameCodeDetailPanel} role="region" aria-live="polite">
            <p className={styles.nameCodeDetailCaption}>{activeDetail.label}</p>
            <p className={styles.nameCodeDetailBody}>{activeDetail.body}</p>
          </div>
        ) : null}
      </div>
    </section>
  );
}
