"use client";

import Link from "next/link";
import { guestSignupHref } from "@/lib/guestAccessStore";
import styles from "@/components/compatibility/CompatibilityAccessDisclosure.module.css";

export type CompatibilityAccessDisclosureMeta = {
  contract_version?: string;
  tier?: "guest" | "registered" | "paid" | string;
  locked_layers?: string[];
  upsell?: {
    title?: string;
    body?: string;
    cta_register?: string;
    cta_subscribe?: string;
  } | null;
  guidance?: {
    yes_no?: { answer?: string; framing?: string };
    do?: string[];
    dont?: string[];
    how?: string[];
  } | null;
};

type Props = {
  access: CompatibilityAccessDisclosureMeta | null | undefined;
};

export function CompatibilityAccessDisclosure({ access }: Props) {
  if (!access?.tier) return null;

  const guidance = access.guidance;
  const upsell = access.upsell;
  const showGuidance =
    access.tier === "paid" &&
    Boolean(
      guidance?.yes_no?.answer ||
        (guidance?.do && guidance.do.length) ||
        (guidance?.dont && guidance.dont.length) ||
        (guidance?.how && guidance.how.length),
    );

  return (
    <section className={styles.root} data-testid="compat-access-disclosure" data-tier={access.tier}>
      {showGuidance && guidance ? (
        <div className={styles.guidance}>
          <p className={styles.eyebrow}>Ясный план</p>
          {guidance.yes_no?.answer ? (
            <div className={styles.yesNo}>
              <p className={styles.yesNoAnswer}>{guidance.yes_no.answer}</p>
              {guidance.yes_no.framing ? <p className={styles.yesNoFrame}>{guidance.yes_no.framing}</p> : null}
            </div>
          ) : null}
          <div className={styles.triad}>
            {guidance.do?.length ? (
              <div className={styles.triadCard}>
                <p className={styles.triadLabel}>Что делать</p>
                <ul>
                  {guidance.do.map((line) => (
                    <li key={line}>{line}</li>
                  ))}
                </ul>
              </div>
            ) : null}
            {guidance.dont?.length ? (
              <div className={`${styles.triadCard} ${styles.triadDont}`}>
                <p className={styles.triadLabel}>Чего не делать</p>
                <ul>
                  {guidance.dont.map((line) => (
                    <li key={line}>{line}</li>
                  ))}
                </ul>
              </div>
            ) : null}
            {guidance.how?.length ? (
              <div className={`${styles.triadCard} ${styles.triadHow}`}>
                <p className={styles.triadLabel}>Как делать</p>
                <ul>
                  {guidance.how.map((line) => (
                    <li key={line}>{line}</li>
                  ))}
                </ul>
              </div>
            ) : null}
          </div>
        </div>
      ) : null}

      {upsell?.title ? (
        <div className={styles.upsell}>
          <p className={styles.upsellTitle}>{upsell.title}</p>
          {upsell.body ? <p className={styles.upsellBody}>{upsell.body}</p> : null}
          <div className={styles.upsellActions}>
            {access.tier === "guest" && upsell.cta_register ? (
              <Link href={guestSignupHref()} className={styles.ctaPrimary}>
                {upsell.cta_register}
              </Link>
            ) : null}
            {upsell.cta_subscribe ? (
              <Link
                href="/account/subscription"
                className={access.tier === "guest" ? styles.ctaSecondary : styles.ctaPrimary}
              >
                {upsell.cta_subscribe}
              </Link>
            ) : null}
          </div>
        </div>
      ) : null}
    </section>
  );
}
