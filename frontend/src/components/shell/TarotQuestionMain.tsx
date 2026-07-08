"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useCallback, useEffect, useMemo, useRef, useState } from "react";
import s from "@/components/shell/tarotShell.module.css";
import { GuestAccessLimitGate } from "@/components/guest/GuestAccessLimitGate";
import { GUEST_ACCESS_COPY } from "@/components/guest/guestAccessCopy";
import { useMeaningRuntime } from "@/hooks/useMeaningRuntime";
import {
  canGuestAccessTarotSpread,
  guestTarotRemaining,
  isGuestTarotLimitReached,
} from "@/lib/guestAccessStore";
import { applyTarotEntryPrefill } from "@/lib/tarotEntryPrefill";
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
import { useAuth } from "@/lib/useAuth";

const FLOW_STEPS: TarotFlowStep[] = ["hero", "concern", "refine", "spread"];

function healTarotQuestionSession(raw: TarotQuestionSession): TarotQuestionSession {
  let next = { ...raw };
  if (!FLOW_STEPS.includes(next.step)) next.step = "concern";
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

function todayDayKey(): string {
  return new Date().toISOString().slice(0, 10);
}

function TarotQuestionMainContent() {
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
    base = { ...base, step: base.step === "hero" ? "concern" : base.step };
    const withPrefill = applyTarotEntryPrefill(base, searchParams);
    const presetSpread = searchParams?.get("spread");
    if (presetSpread) withPrefill.spreadId = presetSpread;
    patchTarotQuestionSession(withPrefill);
    setSession(withPrefill);
    setCustomQuestion(withPrefill.customQuestion);
    setSelectedSpreadId(withPrefill.spreadId);
  }, [searchParams]);

  const writeSession = useCallback((next: TarotQuestionSession) => {
    patchTarotQuestionSession(next);
    setSession(next);
  }, []);

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

  const handleConcernSelect = (domain: TarotConcernDomain) => {
    if (!session) return;
    trackFlow("tarot_session_started", { surface: "tarot_question" }, "started");
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
      { concern_domain: session.concernDomain, refinement_id: refinementId },
      `refine-${refinementId}`,
    );
    writeSession({ ...session, step: "spread", refinementId });
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

  const guestBlocked =
    !isAuthenticated && isGuestTarotLimitReached() && guestTarotRemaining() <= 0;

  const handleReset = () => {
    clearTarotQuestionSession();
    const fresh = createTarotQuestionSession();
    fresh.step = "concern";
    patchTarotQuestionSession(fresh);
    setSession(fresh);
    setCustomQuestion("");
    setSelectedSpreadId(null);
  };

  if (!session) return null;

  const refinements =
    session.concernDomain && session.concernDomain !== "other"
      ? TAROT_REFINEMENTS[session.concernDomain]
      : [];

  const showRefine = session.step === "refine" && refinements.length > 0;
  const showSpread = session.step === "spread" || session.concernDomain === "other";

  return (
    <>
      <Link href="/tarot" className={s.shellBack}>
        ← Таро
      </Link>

      <section className={s.questionSection}>
        <h1 className={s.questionTitle}>{TAROT_QUESTION_FLOW_COPY.concernTitle}</h1>
        <p className={s.questionLead}>{TAROT_QUESTION_FLOW_COPY.concernBody}</p>

        {guestBlocked ? (
          <GuestAccessLimitGate
            title={GUEST_ACCESS_COPY.tarotLimitTitle}
            body={GUEST_ACCESS_COPY.tarotLimitBody}
            secondaryHref="/tarot"
            secondaryLabel="← Назад к Таро"
            testId="guest-tarot-question-limit"
          />
        ) : null}

        <textarea
          className={s.questionTextarea}
          value={customQuestion}
          onChange={(e) => {
            setCustomQuestion(e.target.value);
            patchTarotQuestionSession({ customQuestion: e.target.value });
          }}
          placeholder={TAROT_QUESTION_FLOW_COPY.concernCustomPlaceholder}
          rows={3}
        />

        <div className={s.domainChips}>
          {TAROT_CONCERN_OPTIONS.map((option) => {
            const active = session.concernDomain === option.id;
            return (
              <button
                key={option.id}
                type="button"
                className={`${s.domainChip} ${active ? s.domainChipActive : ""}`.trim()}
                onClick={() => handleConcernSelect(option.id)}
              >
                {option.label}
              </button>
            );
          })}
        </div>

        {showRefine ? (
          <>
            <p className={s.hubRitualEyebrow}>{TAROT_QUESTION_FLOW_COPY.refineStep}</p>
            <p className={s.questionLead}>{TAROT_QUESTION_FLOW_COPY.refineTitle}</p>
            <div className={s.domainChips}>
              {refinements.map((option) => {
                const active = session.refinementId === option.id;
                return (
                  <button
                    key={option.id}
                    type="button"
                    className={`${s.domainChip} ${active ? s.domainChipActive : ""}`.trim()}
                    onClick={() => handleRefineSelect(option.id)}
                  >
                    {option.label}
                  </button>
                );
              })}
            </div>
            <button type="button" className={s.questionLink} onClick={() => writeSession({ ...session, step: "spread" })}>
              {TAROT_QUESTION_FLOW_COPY.skipRefine}
            </button>
          </>
        ) : null}

        {composedQuestion ? (
          <p className={s.questionPreview}>«{composedQuestion}»</p>
        ) : null}

        {showSpread ? (
          <>
            <p className={s.hubRitualEyebrow}>{TAROT_QUESTION_FLOW_COPY.spreadStep}</p>
            <p className={s.questionLead}>{TAROT_QUESTION_FLOW_COPY.spreadTitle}</p>
            <div className={s.spreadPickList}>
              {spreadOffers.slice(0, 6).map((offer) => {
                const selected = selectedSpreadId === offer.spreadId;
                return (
                  <button
                    key={offer.spreadId}
                    type="button"
                    className={`${s.spreadPickRow} ${selected ? s.spreadPickRowSelected : ""}`.trim()}
                    onClick={() => handleSpreadPick(offer.spreadId)}
                  >
                    <span className={s.hubSpreadCount}>{offer.cardCount}</span>
                    <div className={s.spreadPickMeta}>
                      <h3>{offer.title}</h3>
                      <p>{offer.answersQuestions}</p>
                    </div>
                  </button>
                );
              })}
            </div>
          </>
        ) : null}

        <div className={s.questionActions}>
          {selectedSpreadId ? (
            <button type="button" className={s.hubBtnPrimary} onClick={handleBeginRitual}>
              {TAROT_QUESTION_FLOW_COPY.submitRitual}
            </button>
          ) : null}
          <button type="button" className={s.questionLink} onClick={handleReset}>
            {TAROT_QUESTION_FLOW_COPY.resetFlow}
          </button>
        </div>
      </section>
    </>
  );
}

export function TarotQuestionMain() {
  return (
    <Suspense fallback={null}>
      <TarotQuestionMainContent />
    </Suspense>
  );
}
