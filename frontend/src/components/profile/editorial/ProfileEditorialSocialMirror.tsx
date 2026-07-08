"use client";

import { useEffect, useState } from "react";
import type { ProfileV0SocialMirrorCard } from "@/lib/profilePage/buildProfileV0SphereCards";
import styles from "./profileEditorial.module.css";

type MirrorFacetKey = "firstImpression" | "broadcast" | "blindSpot";

const MIRROR_FACETS: { key: MirrorFacetKey; label: string }[] = [
  { key: "firstImpression", label: "Первое впечатление" },
  { key: "broadcast", label: "Что транслируешь" },
  { key: "blindSpot", label: "Слепая зона" },
];

export function ProfileEditorialSocialMirror({ mirror }: { mirror: ProfileV0SocialMirrorCard }) {
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
    <section className={styles.socialMirror} aria-label="Как tебя видят">
      <p id="profile-social-mirror" className={styles.sectionLabel}>
        Как тебя видят
      </p>

      <blockquote className={styles.socialMirrorLead}>
        <p>{mirror.lead}</p>
      </blockquote>

      {mirror.observations.length ? (
        <ul className={styles.socialMirrorList}>
          {mirror.observations.map((observation) => (
            <li key={observation} className={styles.socialMirrorItem}>
              {observation}
            </li>
          ))}
        </ul>
      ) : null}

      {facets.length ? (
        <button
          type="button"
          className={styles.linkBtn}
          aria-expanded={expanded}
          onClick={() => setExpanded((v) => !v)}
        >
          {expanded ? "Свернуть" : "Подробнее"}
        </button>
      ) : null}

      {expanded && facets.length ? (
        <div className={styles.socialMirrorFacets}>
          {facets.map((facet) => (
            <button
              key={facet.key}
              type="button"
              className={`${styles.socialMirrorFacetBtn} ${
                activeFacet === facet.key ? styles.socialMirrorFacetBtnActive : ""
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
        <div className={styles.socialMirrorDetail} role="region" aria-live="polite">
          <p className={styles.socialMirrorDetailLabel}>{activeDetail.label}</p>
          <p className={styles.socialMirrorDetailBody}>{activeDetail.body}</p>
        </div>
      ) : null}
    </section>
  );
}
