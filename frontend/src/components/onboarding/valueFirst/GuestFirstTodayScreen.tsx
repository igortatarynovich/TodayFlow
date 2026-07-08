"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { TodayCompositionSurface } from "@/components/today/composition/TodayCompositionSurface";
import { emptyMorningRitualData, buildGuestFirstTodayPayload } from "@/lib/buildGuestFirstTodayPayload";
import type { GuestProfileDraft } from "@/lib/guestProfileDraft";
import { patchGuestProfileDraft, VALUE_FIRST_PATHS } from "@/lib/guestProfileDraft";
import { markFirstTodayCompleted } from "@/lib/firstTodayState";
import { VALUE_FIRST_COPY as copy } from "@/components/onboarding/valueFirst/valueFirstOnboardingCopy";
import { ConversationThread } from "@/components/conversation/ConversationThread";
import { ConversationTurn } from "@/components/conversation/ConversationTurn";
import styles from "@/components/onboarding/valueFirst/valueFirstOnboarding.module.css";

type Props = {
  draft: GuestProfileDraft;
};

export function GuestFirstTodayScreen({ draft }: Props) {
  const payload = useMemo(() => buildGuestFirstTodayPayload(draft), [draft]);
  const [showSavePrompt, setShowSavePrompt] = useState(false);

  useEffect(() => {
    patchGuestProfileDraft({ first_today_started_at: new Date().toISOString() });
  }, []);

  return (
    <main className="orbit-page todayflow-serene todayflow-shell" style={{ background: "#f3efe8", minHeight: "100dvh" }}>
      <section className="orbit-hero-content-block profile-editorial-route" style={{ paddingTop: "0.35rem", paddingBottom: "2.5rem" }}>
        <div className="orbit-hero-content-container profile-editorial-route-container">
          <TodayCompositionSurface
            variant="firstToday"
            dateISO={payload.dateISO}
            displayDate={payload.displayDate}
            todayData={payload.todayData}
            morningRitualData={emptyMorningRitualData()}
            contract={payload.contract}
            cardName={payload.cardName}
            cardMeaning={payload.cardMeaning}
            numerologyValue={payload.numerologyValue}
            numerologyMeaning={payload.numerologyMeaning}
            guideNarrativeLoading={false}
            guideNarrativePayload={payload.guideNarrativePayload}
            coreProfile={payload.coreProfile}
            onDayClosed={() => {
              markFirstTodayCompleted(payload.dateISO);
              patchGuestProfileDraft({ save_ready_at: new Date().toISOString() });
              setShowSavePrompt(true);
            }}
          />
          {showSavePrompt ? (
            <ConversationThread testId="onboarding-thread-save-invite">
              <ConversationTurn
                turnId="save_invite"
                message={
                  <>
                    <h2>{copy.guestClosed.title}</h2>
                    <p>{copy.guestClosed.lead}</p>
                  </>
                }
                response={
                  <div className={styles.ctaRow}>
                    <Link href={VALUE_FIRST_PATHS.save} className="orbit-button orbit-button-primary" data-testid="guest-save-prompt">
                      {copy.guestClosed.cta}
                    </Link>
                  </div>
                }
              />
            </ConversationThread>
          ) : null}
        </div>
      </section>
    </main>
  );
}
