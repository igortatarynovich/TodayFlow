import Link from "next/link";
import {
  GUEST_PROFILE_PITCH,
  GUEST_TODAY_PITCH,
} from "@/components/product-ui/guestProductPitches";
import styles from "@/components/product-ui/ProductGuestShowcase.module.css";

type Pitch = typeof GUEST_TODAY_PITCH | typeof GUEST_PROFILE_PITCH;

/** Server-safe pitch HTML for crawlers (no client hooks / no CSR bailout). */
export function GuestProductPitchSsr({
  pitch,
  testId,
}: {
  pitch: Pitch;
  testId: string;
}) {
  return (
    <section className={styles.readableRoot} data-testid={testId}>
      <div className={styles.readablePanel}>
        <p className={styles.previewEyebrow}>{pitch.eyebrow}</p>
        <h1 className={styles.previewTitle}>{pitch.title}</h1>
        <p className={styles.readableLead}>{pitch.lead}</p>
        <div className={styles.previewCards}>
          {pitch.parts.map((part) => (
            <div key={part.id} className={styles.previewCard}>
              <span className={styles.previewCardLabel}>{part.label}</span>
              <span className={styles.previewCardValue}>{part.body}</span>
            </div>
          ))}
        </div>
        {"needs" in pitch && pitch.needs ? (
          <p className={styles.readableNeeds}>{pitch.needs}</p>
        ) : null}
        <div className={styles.readableCtas}>
          <Link href={pitch.ctaPrimaryHref} className={styles.ssrCtaPrimary}>
            {pitch.ctaPrimary}
          </Link>
          <Link href={pitch.ctaSecondaryHref} className={styles.ssrCtaSecondary}>
            {pitch.ctaSecondary}
          </Link>
        </div>
      </div>
    </section>
  );
}

export function GuestTodayPitchSsr() {
  return <GuestProductPitchSsr pitch={GUEST_TODAY_PITCH} testId="today-guest-pitch-ssr" />;
}

export function GuestProfilePitchSsr() {
  return <GuestProductPitchSsr pitch={GUEST_PROFILE_PITCH} testId="profile-guest-pitch-ssr" />;
}
