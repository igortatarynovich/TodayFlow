"use client";

import { useEffect, useState } from "react";
import type { ProfileV0MoneyCard } from "@/lib/profilePage/buildProfileV0SphereCards";
import { MoneyStructureObject } from "./sphere/MoneyStructureObject";
import styles from "./profileV0.module.css";

type MoneyFacetKey = "motivation" | "risk" | "workStyle";

const MONEY_FACETS: { key: MoneyFacetKey; label: string }[] = [
  { key: "motivation", label: "Мотивация" },
  { key: "risk", label: "Риск" },
  { key: "workStyle", label: "Стиль работы" },
];

export function ProfileV0MoneyObject({ money }: { money: ProfileV0MoneyCard }) {
  const [expanded, setExpanded] = useState(false);
  const [activeFacet, setActiveFacet] = useState<MoneyFacetKey | null>(null);
  const mainLine = money.approach || money.workStyle;

  const facets = MONEY_FACETS.map(({ key, label }) => ({
    key,
    label,
    body: money.expand[key],
  })).filter((f) => f.body?.trim());

  useEffect(() => {
    if (!expanded) setActiveFacet(null);
  }, [expanded]);

  const activeDetail = facets.find((f) => f.key === activeFacet);

  return (
    <article className={styles.dualityMoney} aria-label="Деньги">
      <div className={styles.dualityMoneyAxis} aria-hidden />
      <div className={styles.dualityMoneySymbol}>
        <MoneyStructureObject size={88} />
      </div>

      <p className={styles.dualityMoneyLabel}>Деньги</p>
      <h3 className={styles.dualityMoneyTitle}>Как ты реализуешься</h3>
      <p className={styles.dualityMoneyMain}>{mainLine}</p>

      <div className={styles.dualityMoneySignals}>
        <p className={styles.dualityMoneySignal}>
          <span className={styles.dualityMoneySignalLabel}>Усиливает:</span> {money.helps}
        </p>
        <p className={styles.dualityMoneySignal}>
          <span className={styles.dualityMoneySignalLabel}>Тормозит:</span> {money.blocks}
        </p>
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
              className={`${styles.dualityFacetBtn} ${styles.dualityFacetBtnMoney} ${
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
        <div className={`${styles.dualityDetailPanel} ${styles.dualityDetailPanelMoney}`} role="region" aria-live="polite">
          <p className={styles.dualityDetailCaption}>{activeDetail.label}</p>
          <p className={styles.dualityDetailBody}>{activeDetail.body}</p>
        </div>
      ) : null}
    </article>
  );
}
