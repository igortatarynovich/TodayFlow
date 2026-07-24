"use client";

/**
 * Guest Showcase (FOUNDATION_UI §10) — blur-preview of product content behind the gate card.
 * Reuses static Today-promise copy from the landing (no personal data).
 */
import type { ReactNode } from "react";
import { PRODUCT_WEB_LANDING_TODAY_PROMISE } from "@/components/product-ui/productWebLandingContent";
import styles from "@/components/product-ui/ProductGuestShowcase.module.css";

type ProductGuestShowcaseProps = {
  children: ReactNode;
  testId?: string;
};

export function ProductGuestShowcase({
  children,
  testId = "product-guest-showcase",
}: ProductGuestShowcaseProps) {
  const promise = PRODUCT_WEB_LANDING_TODAY_PROMISE;

  return (
    <div className={styles.root} data-testid={testId}>
      <div className={styles.preview} aria-hidden="true">
        <div className={styles.previewPanel}>
          <p className={styles.previewEyebrow}>{promise.eyebrow}</p>
          <p className={styles.previewTitle}>{promise.title}</p>
          <div className={styles.previewTags}>
            {promise.tags.map((tag) => (
              <span key={tag} className={styles.previewTag}>
                {tag}
              </span>
            ))}
          </div>
          <div className={styles.previewCards}>
            {promise.cards.map((card) => (
              <div key={card.id} className={styles.previewCard}>
                <span className={styles.previewCardLabel}>{card.label}</span>
                <span className={styles.previewCardValue}>{card.value}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
      <div className={styles.gate}>{children}</div>
    </div>
  );
}
