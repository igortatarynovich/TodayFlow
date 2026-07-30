import Link from "next/link";
import { GUEST_TODAY_DEMO as demo } from "@/lib/guestTodayDemoContent";
import styles from "@/components/product-ui/ProductGuestShowcase.module.css";
import { VALUE_FIRST_PATHS } from "@/lib/guestProfileDraft";

/** Server-readable demo Today — crawlers see Theme/Focus/Practice/Memory without CSR bailout. */
export function GuestTodayDemoSsr() {
  return (
    <section className={styles.readableRoot} data-testid="demo-today-ssr">
      <div className={styles.readablePanel}>
        <p className={styles.previewEyebrow}>{demo.eyebrow}</p>
        <h1 className={styles.previewTitle}>{demo.title}</h1>
        <p className={styles.readableLead}>{demo.lead}</p>
        <div className={styles.previewCards}>
          <div className={styles.previewCard}>
            <span className={styles.previewCardLabel}>{demo.themeLabel}</span>
            <span className={styles.previewCardValue}>
              <strong>{demo.themeTitle}. </strong>
              {demo.themeBody}
            </span>
          </div>
          <div className={styles.previewCard}>
            <span className={styles.previewCardLabel}>{demo.focusLabel}</span>
            <span className={styles.previewCardValue}>{demo.focusBody}</span>
          </div>
          <div className={styles.previewCard}>
            <span className={styles.previewCardLabel}>{demo.practiceLabel}</span>
            <span className={styles.previewCardValue}>{demo.practiceBody}</span>
          </div>
          <div className={styles.previewCard}>
            <span className={styles.previewCardLabel}>{demo.memoryLabel}</span>
            <span className={styles.previewCardValue}>{demo.memoryBody}</span>
          </div>
        </div>
        <p className={styles.readableNeeds}>{demo.note}</p>
        <div className={styles.readableCtas}>
          <Link href={VALUE_FIRST_PATHS.invite} className={styles.ssrCtaPrimary} data-testid="demo-today-cta">
            {demo.ctaPrimary}
          </Link>
          <Link href="/" className={styles.ssrCtaSecondary}>
            {demo.ctaSecondary}
          </Link>
        </div>
      </div>
    </section>
  );
}
