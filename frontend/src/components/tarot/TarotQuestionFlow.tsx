"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useMeaningRuntime } from "@/hooks/useMeaningRuntime";
import {
  TAROT_CONCERN_OPTIONS,
  TAROT_QUESTION_FLOW_COPY,
  TAROT_REFINEMENTS,
  buildTarotRitualHref,
  composeTarotQuestion,
  rankSpreadOffersForConcern,
  type TarotConcernDomain,
  type TarotFlowStep,
} from "@/lib/tarotQuestionFlowCanon";
import { tarotFlowEventKey } from "@/lib/tarotQuestionFlowEvents";
import {
  clearTarotQuestionSession,
  createTarotQuestionSession,
  patchTarotQuestionSession,
  readTarotQuestionSession,
  type TarotQuestionSession,
} from "@/lib/tarotQuestionSession";
import { TarotWebHub } from "@/components/product-ui/TarotWebHub";
import hubStyles from "@/components/product-ui/productWebScreens.module.css";
import { applyTarotEntryPrefill } from "@/lib/tarotEntryPrefill";
import { useAuth } from "@/lib/useAuth";
import {
  canGuestAccessTarotSpread,
  guestTarotRemaining,
  isGuestTarotLimitReached,
} from "@/lib/guestAccessStore";
import { GuestAccessLimitGate } from "@/components/guest/GuestAccessLimitGate";
import { GUEST_ACCESS_COPY } from "@/components/guest/guestAccessCopy";

function todayDayKey(): string {
  return new Date().toISOString().slice(0, 10);
}

const FLOW_STEPS: TarotFlowStep[] = ["hero", "concern", "refine", "spread"];

function healTarotQuestionSession(raw: TarotQuestionSession): TarotQuestionSession {
  let next = { ...raw };
  if (!FLOW_STEPS.includes(next.step)) {
    next.step = "hero";
  }
  if (next.step === "refine") {
    const domain = next.concernDomain;
    const refs =
      domain && domain !== "other" ? TAROT_REFINEMENTS[domain as TarotConcernDomain] : [];
    if (!refs.length) next.step = "spread";
  }
  if (next.step !== "hero" && !next.concernDomain && !next.customQuestion.trim()) {
    next.step = "concern";
  }
  return next;
}

export function TarotQuestionFlow() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { isAuthenticated } = useAuth();
  const entryPrefillApplied = useRef(false);
  const { trackMeaningEvent } = useMeaningRuntime();
  const [session, setSession] = useState<TarotQuestionSession | null>(null);
  const [customQuestion, setCustomQuestion] = useState("");
  const [selectedSpreadId, setSelectedSpreadId] = useState<string | null>(null);

  useEffect(() => {
    if (entryPrefillApplied.current) return;
    entryPrefillApplied.current = true;

    const existing = readTarotQuestionSession();
    let base = existing ? healTarotQuestionSession(existing) : createTarotQuestionSession();
    const withPrefill = applyTarotEntryPrefill(base, searchParams);
    patchTarotQuestionSession(withPrefill);
    setSession(withPrefill);
    setCustomQuestion(withPrefill.customQuestion);
    setSelectedSpreadId(withPrefill.spreadId);
  }, [searchParams]);

  const writeSession = useCallback((next: TarotQuestionSession) => {
    patchTarotQuestionSession(next);
    setSession(next);
  }, []);

  const step: TarotFlowStep = session?.step ?? "hero";

  const composedQuestion = useMemo(
    () =>
      composeTarotQuestion({
        concernDomain: session?.concernDomain ?? null,
        refinementId: session?.refinementId ?? null,
        customQuestion,
      }),
    [session?.concernDomain, session?.refinementId, customQuestion],
  );

  const spreadOffers = useMemo(
    () => rankSpreadOffersForConcern(session?.concernDomain ?? null),
    [session?.concernDomain],
  );

  const trackFlow = useCallback(
    (
      event_type:
        | "tarot_session_started"
        | "tarot_question_domain_selected"
        | "tarot_question_refined"
        | "tarot_spread_selected"
        | "tarot_question_submitted",
      payload: Record<string, unknown>,
      suffix: string,
    ) => {
      if (!session?.sessionId) return;
      trackMeaningEvent({
        event_type,
        event_source: "flow",
        local_date: todayDayKey(),
        idempotency_key: tarotFlowEventKey(session.sessionId, suffix),
        payload: { session_id: session.sessionId, ...payload },
      });
    },
    [session?.sessionId, trackMeaningEvent],
  );

  const goToStep = (nextStep: TarotFlowStep, patch: Partial<TarotQuestionSession> = {}) => {
    if (!session) return;
    writeSession({ ...session, ...patch, step: nextStep });
  };

  const handleConcernSelect = (domain: TarotConcernDomain) => {
    if (!session) return;
    if (session.step === "hero") {
      trackFlow("tarot_session_started", { surface: "tarot_hub" }, "started");
    }
    trackFlow("tarot_question_domain_selected", { concern_domain: domain }, `domain-${domain}`);
    writeSession({
      ...session,
      step: domain === "other" ? "spread" : "refine",
      concernDomain: domain,
      refinementId: null,
    });
  };

  const handleRefineSelect = (refinementId: string) => {
    if (!session) return;
    trackFlow(
      "tarot_question_refined",
      {
        concern_domain: session.concernDomain,
        refinement_id: refinementId,
      },
      `refine-${refinementId}`,
    );
    goToStep("spread", { refinementId });
  };

  const handleSkipRefine = () => {
    goToStep("spread");
  };

  const handleSpreadPick = (spreadId: string) => {
    setSelectedSpreadId(spreadId);
    if (!session) return;
    trackFlow(
      "tarot_spread_selected",
      {
        spread_id: spreadId,
        concern_domain: session.concernDomain,
        question_text: composedQuestion,
      },
      `spread-${spreadId}`,
    );
    writeSession({ ...session, spreadId });
  };

  const handleBeginRitual = () => {
    if (!session || !selectedSpreadId) return;

    const href = buildTarotRitualHref({
      spreadId: selectedSpreadId,
      question: composedQuestion,
      concernDomain: session.concernDomain,
      refinementId: session.refinementId,
    });
    const previewKey = href.includes("?") ? href.split("?")[1] ?? href : href;

    if (
      !isAuthenticated &&
      isGuestTarotLimitReached() &&
      !canGuestAccessTarotSpread(previewKey)
    ) {
      return;
    }

    trackFlow(
      "tarot_question_submitted",
      {
        concern_domain: session.concernDomain,
        refinement_id: session.refinementId,
        question_text: composedQuestion,
        spread_id: selectedSpreadId,
      },
      "question-submitted",
    );
    router.push(href);
  };

  const guestTarotBlocked =
    !isAuthenticated && isGuestTarotLimitReached() && guestTarotRemaining() <= 0;

  const handleResetFlow = () => {
    clearTarotQuestionSession();
    const fresh = createTarotQuestionSession();
    patchTarotQuestionSession(fresh);
    setSession(fresh);
    setCustomQuestion("");
    setSelectedSpreadId(null);
  };

  if (!session) {
    return <TarotWebHub />;
  }

  const refinements =
    session.concernDomain && session.concernDomain !== "other"
      ? TAROT_REFINEMENTS[session.concernDomain]
      : [];

  const hubSpreads = spreadOffers.slice(0, 3).map((offer, index) => ({
    id: offer.spreadId,
    countLabel: String(offer.cardCount),
    title: offer.title,
    description: offer.subtitle,
    recommended:
      session.concernDomain != null && offer.recommendedFor.includes(session.concernDomain) && index < 3,
  }));

  const flowContent = (
    <>
      {guestTarotBlocked ? (
        <GuestAccessLimitGate
          title={GUEST_ACCESS_COPY.tarotLimitTitle}
          body={GUEST_ACCESS_COPY.tarotLimitBody}
          secondaryHref="/"
          secondaryLabel="На главную"
          testId="guest-tarot-hub-limit"
        />
      ) : null}
      {step === "refine" && refinements.length ? (
        <section className={hubStyles.tarotRefineSection}>
          <h2 className={hubStyles.practicesRailEyebrow}>{TAROT_QUESTION_FLOW_COPY.refineStep}</h2>
          <p className={hubStyles.tarotHubSubtitle} style={{ margin: 0 }}>
            {TAROT_QUESTION_FLOW_COPY.refineTitle}
          </p>
          <div className={hubStyles.tarotDomainChips}>
            {refinements.map((option) => {
              const selected = session.refinementId === option.id;
              return (
                <button
                  key={option.id}
                  type="button"
                  className={`${hubStyles.tarotDomainChip} ${selected ? hubStyles.tarotDomainChipActive : ""}`}
                  onClick={() => handleRefineSelect(option.id)}
                >
                  {option.label}
                </button>
              );
            })}
          </div>
          {composedQuestion ? (
            <p className={hubStyles.tarotHubSubtitle} style={{ fontStyle: "italic" }}>
              «{composedQuestion}»
            </p>
          ) : null}
          <button type="button" className={hubStyles.tarotLastQuestionLink} onClick={handleSkipRefine}>
            {TAROT_QUESTION_FLOW_COPY.skipRefine}
          </button>
        </section>
      ) : null}
      {session.concernDomain || selectedSpreadId ? (
        <p style={{ margin: "0.5rem 0 0", textAlign: "center" }}>
          <button type="button" className={hubStyles.tarotLastQuestionLink} onClick={handleResetFlow}>
            {TAROT_QUESTION_FLOW_COPY.resetFlow}
          </button>
        </p>
      ) : null}
    </>
  );

  return (
    <TarotWebHub
      customQuestion={customQuestion}
      onCustomQuestionChange={(value) => {
        setCustomQuestion(value);
        patchTarotQuestionSession({ customQuestion: value });
      }}
      questionPlaceholder={TAROT_QUESTION_FLOW_COPY.concernCustomPlaceholder}
      domainChips={TAROT_CONCERN_OPTIONS.map((option) => ({ id: option.id, label: option.label }))}
      selectedDomainId={session.concernDomain}
      onDomainSelect={(domainId) => handleConcernSelect(domainId as TarotConcernDomain)}
      spreads={hubSpreads}
      selectedSpreadId={selectedSpreadId}
      onSpreadSelect={handleSpreadPick}
      onSubmitQuestion={handleBeginRitual}
      submitDisabled={!selectedSpreadId || guestTarotBlocked}
      submitLabel={TAROT_QUESTION_FLOW_COPY.submitRitual}
      flowContent={flowContent}
      hideSpreadSection={step === "refine"}
    />
  );
}
