"use client";

/**
 * Readable guest pitch + CTA — for crawlers and first-time visitors.
 * Unlike blur showcase, content is in the accessibility tree and SSR HTML.
 */
import { DsButton } from "@/design-system";
import styles from "@/components/product-ui/ProductGuestShowcase.module.css";
import { VALUE_FIRST_PATHS } from "@/lib/guestProfileDraft";

export type GuestPitchPart = {
  id: string;
  label: string;
  body: string;
};

export type GuestProductPitchProps = {
  testId?: string;
  eyebrow: string;
  title: string;
  lead: string;
  parts: readonly GuestPitchPart[];
  needs?: string;
  primaryHref?: string;
  primaryLabel: string;
  secondaryHref?: string;
  secondaryLabel?: string;
};

export function GuestProductPitch({
  testId = "guest-product-pitch",
  eyebrow,
  title,
  lead,
  parts,
  needs,
  primaryHref = `${VALUE_FIRST_PATHS.welcome}?fresh=1`,
  primaryLabel,
  secondaryHref = "/auth?mode=login",
  secondaryLabel,
}: GuestProductPitchProps) {
  return (
    <div className={styles.readableRoot} data-testid={testId}>
      <div className={styles.readablePanel}>
        <p className={styles.previewEyebrow}>{eyebrow}</p>
        <h1 className={styles.previewTitle}>{title}</h1>
        <p className={styles.readableLead}>{lead}</p>
        <div className={styles.previewCards}>
          {parts.map((part) => (
            <div key={part.id} className={styles.previewCard}>
              <span className={styles.previewCardLabel}>{part.label}</span>
              <span className={styles.previewCardValue}>{part.body}</span>
            </div>
          ))}
        </div>
        {needs ? <p className={styles.readableNeeds}>{needs}</p> : null}
        <div className={styles.readableCtas}>
          <DsButton href={primaryHref}>{primaryLabel}</DsButton>
          {secondaryHref && secondaryLabel ? (
            <DsButton href={secondaryHref} variant="secondary">
              {secondaryLabel}
            </DsButton>
          ) : null}
        </div>
      </div>
    </div>
  );
}
