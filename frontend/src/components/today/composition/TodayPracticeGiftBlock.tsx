"use client";

import Link from "next/link";
import {
  DsActionCard,
  DsBody,
  DsButton,
  DsCaption,
  DsChip,
  DsHeroBlock,
} from "@/design-system";
import { TODAY_COMPOSITION_COPY as copy } from "@/components/today/composition/todayCompositionCopy";
import { resolveTodayStoryFrameArt } from "@/lib/todayStoryFrameArt";
import layout from "@/design-system/compositions/dsCompositions.module.css";

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
 * Move «Практика дня» — Form Kit Hero + Action (bleed photo).
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
    <section className={layout.stack} data-testid="today-zone-practice-gift">
      <DsHeroBlock
        tone="solid"
        eyebrow={copy.practiceGiftEyebrow}
        title={title}
        body={instructions || undefined}
        bleed={
          // eslint-disable-next-line @next/next/no-img-element -- story-frame public art
          <img src={photoSrc} alt="" style={{ width: "100%", height: "auto", display: "block" }} />
        }
      />

      {practiceCompleted ? (
        <DsChip variant="status" testId="today-practice-gift-done">
          {copy.practiceCompleted}
        </DsChip>
      ) : (
        <DsActionCard
          tone="accent"
          title={practiceStarted ? "Практика начата" : startCtaLabel(duration)}
          body={practiceStarted ? undefined : undefined}
          action={
            <div className={layout.stack}>
              {!practiceStarted ? (
                <DsButton
                  type="button"
                  variant="primary"
                  data-testid="today-tool-practice"
                  disabled={practiceCompleting}
                  onClick={() => void onPracticeAction()}
                >
                  {startCtaLabel(duration)}
                </DsButton>
              ) : (
                <>
                  <DsCaption>
                    <span data-testid="today-practice-gift-started">Практика начата</span>
                  </DsCaption>
                  <DsButton
                    type="button"
                    variant="primary"
                    data-testid="today-tool-practice-complete"
                    disabled={practiceCompleting}
                    onClick={() => void onPracticeAction()}
                  >
                    {copy.practiceComplete}
                  </DsButton>
                </>
              )}
              <DsBody size="sm">
                <Link href={practiceHref} data-testid="today-setup-practices-link">
                  {practiceId ? "Открыть практику →" : `${copy.setupPracticesLink} →`}
                </Link>
              </DsBody>
            </div>
          }
        />
      )}
    </section>
  );
}
