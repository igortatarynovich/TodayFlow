"use client";

import Link from "next/link";
import { DsButton } from "@/design-system";
import { TODAY_COMPOSITION_COPY as copy } from "@/components/today/composition/todayCompositionCopy";
import { resolveTodayStoryFrameArt } from "@/lib/todayStoryFrameArt";
import styles from "@/components/today/composition/TodayPracticeGiftBlock.module.css";

type Props = {
  title: string;
  detail?: string | null;
  duration?: string | null;
  reason?: string | null;
  practiceId?: string | null;
  practiceStarted: boolean;
  practiceCompleted: boolean;
  practiceCompleting?: boolean;
  onPracticeAction: () => void;
  setupHref?: string;
};

function startCtaLabel(duration: string | null | undefined): string {
  const d = String(duration ?? "").trim();
  if (d) return `${copy.practiceStart} · ${d}`;
  return copy.practiceStart;
}

/**
 * Move «Практика дня» — gift framing.
 * Primary CTA marks started on this step (handoff); open practice page is secondary.
 */
export function TodayPracticeGiftBlock({
  title,
  detail = null,
  duration = null,
  reason = null,
  practiceId = null,
  practiceStarted,
  practiceCompleted,
  practiceCompleting = false,
  onPracticeAction,
  setupHref = "/practices",
}: Props) {
  const photoSrc = resolveTodayStoryFrameArt("practice");
  const instructions = String(detail || reason || "").trim() || null;
  const practiceHref = practiceId ? `/practices/${practiceId}` : setupHref;

  return (
    <section className={styles.root} data-testid="today-zone-practice-gift">
      <div className={styles.photoWrap}>
        <img className={styles.photo} src={photoSrc} alt="" />
        <div className={styles.photoScrim} aria-hidden />
        <p className={styles.eyebrow}>{copy.practiceGiftEyebrow}</p>
      </div>

      <div className={styles.body}>
        <h3 className={styles.title}>{title}</h3>
        {instructions ? <p className={styles.instructions}>{instructions}</p> : null}

        {practiceCompleted ? (
          <p className={styles.confirmed} data-testid="today-practice-gift-done">
            {copy.practiceCompleted}
          </p>
        ) : (
          <div className={styles.actions}>
            {!practiceStarted ? (
              <DsButton
                type="button"
                variant="primary"
                className={styles.cta}
                data-testid="today-tool-practice"
                disabled={practiceCompleting}
                onClick={() => void onPracticeAction()}
              >
                {startCtaLabel(duration)}
              </DsButton>
            ) : (
              <>
                <p className={styles.confirmed} data-testid="today-practice-gift-started">
                  Практика начата
                </p>
                <DsButton
                  type="button"
                  variant="primary"
                  className={styles.cta}
                  data-testid="today-tool-practice-complete"
                  disabled={practiceCompleting}
                  onClick={() => void onPracticeAction()}
                >
                  {copy.practiceComplete}
                </DsButton>
              </>
            )}
            <p className={styles.setup}>
              <Link href={practiceHref} data-testid="today-setup-practices-link">
                {practiceId ? "Открыть практику →" : `${copy.setupPracticesLink} →`}
              </Link>
            </p>
          </div>
        )}
      </div>
    </section>
  );
}
