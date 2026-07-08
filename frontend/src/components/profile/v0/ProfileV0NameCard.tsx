"use client";

import { useEffect, useState } from "react";
import type { ProfileV0Header } from "@/lib/profilePage/buildProfileV0Data";
import type { ProfileV0SocialMirrorCard } from "@/lib/profilePage/buildProfileV0SphereCards";
import styles from "./profileV0.module.css";

type NameFacetKey = "firstImpression" | "broadcast" | "blindSpot";

const NAME_FACETS: { key: NameFacetKey; label: string }[] = [
  { key: "firstImpression", label: "Первое впечатление" },
  { key: "broadcast", label: "Что транслируешь" },
  { key: "blindSpot", label: "Слепая зона" },
];

function nameInitial(displayName: string): string {
  const trimmed = displayName.trim();
  return trimmed ? trimmed.charAt(0).toUpperCase() : "•";
}

function keywordLine(mirror: ProfileV0SocialMirrorCard): string | null {
  const parts = mirror.observations
    .map((line) => line.split(/[.,!?]/)[0]?.trim())
    .filter(Boolean)
    .slice(0, 3);
  return parts.length ? parts.join(" · ") : null;
}

export function ProfileV0NameCard({
  header,
  mirror,
}: {
  header: ProfileV0Header;
  mirror: ProfileV0SocialMirrorCard;
}) {
  const [expanded, setExpanded] = useState(false);
  const [activeFacet, setActiveFacet] = useState<NameFacetKey | null>(null);

  const facets = NAME_FACETS.map(({ key, label }) => ({
    key,
    label,
    body: mirror.expand[key],
  })).filter((f) => f.body?.trim());

  useEffect(() => {
    if (!expanded) setActiveFacet(null);
  }, [expanded]);

  const activeDetail = facets.find((f) => f.key === activeFacet);
  const keywords = keywordLine(mirror);
  const listItems = mirror.lead
    ? [mirror.lead, ...mirror.observations].slice(0, 3)
    : mirror.observations.slice(0, 3);

  return (
    <section className={`${styles.profileCard} ${styles.profileNameCard}`} aria-label="Имя">
      <p className={styles.profileCardLabel}>Имя</p>

      <div className={styles.profileNameCardHero}>
        <span className={styles.profileNameCardGlyph} aria-hidden>
          {nameInitial(header.displayName)}
        </span>
        <div>
          <h3 className={styles.profileNameCardTitle}>{header.displayName}</h3>
          {keywords ? <p className={styles.profileNameCardKeywords}>{keywords}</p> : null}
        </div>
      </div>

      {listItems.length ? (
        <ul className={styles.profileNameCardList}>
          {listItems.map((item) => (
            <li key={item} className={styles.profileNameCardItem}>
              <span className={styles.profileNameCardBullet} aria-hidden />
              <span>{item}</span>
            </li>
          ))}
        </ul>
      ) : null}

      {facets.length ? (
        <button
          type="button"
          className={styles.profileCardCta}
          aria-expanded={expanded}
          onClick={() => setExpanded((v) => !v)}
        >
          {expanded ? "Свернуть" : "Подробнее об имени"}
          {!expanded ? (
            <span className={styles.profileCardCtaArrow} aria-hidden>
              →
            </span>
          ) : null}
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
    </section>
  );
}
