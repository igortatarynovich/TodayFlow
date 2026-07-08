"use client";

import Link from "next/link";
import { Suspense, useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useSearchParams } from "next/navigation";
import { LoadingSpinner } from "@/components/orbit";
import { DsButton } from "@/design-system";
import shell from "@/components/shell/tarotShell.module.css";
import { TarotWebResult } from "@/components/product-ui/TarotWebResult";
import s from "@/components/product-ui/productWebScreens.module.css";
import { tarotSpreadResultChromeBundle } from "@/components/tarot/tarotSpreadResultChrome";
import type { FlowPracticesChromeLocale } from "@/components/today/flowPracticesMainTabChrome";
import { buildTarotReadingStoryFromAnswer, buildTarotReadingStoryFromSpread } from "@/lib/buildTarotReadingStoryModel";
import type { TarotFollowUpChip } from "@/lib/buildTarotReadingStoryModel";
import type { TarotAnswerV1 } from "@/lib/tarotAnswerContract";
import type { TarotConcernDomain } from "@/lib/tarotQuestionFlowCanon";
import { tarotFlowEventKey } from "@/lib/tarotQuestionFlowEvents";
import {
  appendTarotJourneyEntry,
} from "@/lib/tarotJourneyStore";
import { useMeaningRuntime } from "@/hooks/useMeaningRuntime";
import { getJson, postJson } from "@/lib/api";
import { getLocale } from "@/lib/i18n";
import type { CoreProfile, TarotCard } from "@/lib/types";
import { useAuth } from "@/lib/useAuth";
import {
  canGuestAccessTarotSpread,
  isGuestTarotLimitReached,
  tryConsumeGuestTarotSpread,
} from "@/lib/guestAccessStore";
import { GuestAccessLimitGate } from "@/components/guest/GuestAccessLimitGate";
import { GUEST_ACCESS_COPY } from "@/components/guest/guestAccessCopy";

type TarotResult = {
  spread_id: string;
  title?: string;
  description?: string | null;
  cards: Array<{
    card: TarotCard;
    orientation: "upright" | "reversed";
    position:
      | string
      | {
          id: string;
          title: string;
          prompt?: string;
        };
    meaning: string;
  }>;
};

type TarotConsistency = {
  focus?: string;
  do_focus?: string;
  avoid_focus?: string;
  tone?: string;
};

type TarotSpreadWithContext = {
  spread: TarotResult;
  core_profile?: CoreProfile | null;
  consistency?: TarotConsistency | null;
  generation_log_id?: number | null;
  reading?: {
    meaning?: string;
    manifestation?: string;
    caution?: string;
    next_step?: string;
    synthesis_why?: string | null;
    actions_today?: string[] | null;
    self_question?: string | null;
    profile_lens?: string | null;
    profile_lens_applied?: boolean | null;
    insight_holding?: string | null;
    insight_shifting?: string | null;
    insight_attention?: string | null;
    today_suggestion?: string | null;
    follow_up_prompt?: string | null;
    follow_up_chips?: Array<{ id: string; label: string }> | null;
    card_insights?: Array<{
      position_label: string;
      card_name_ru: string;
      card_id: number;
      orientation: string;
      line: string;
    }> | null;
  } | null;
  tarot_answer_v1?: TarotAnswerV1 | null;
};

function todayDayKey(): string {
  return new Date().toISOString().slice(0, 10);
}

function tarotScreenBackLabel(): string {
  const locale: FlowPracticesChromeLocale = getLocale() === "ru" ? "ru" : "en";
  return tarotSpreadResultChromeBundle(locale).tarotSpreadResultModeLabel;
}

type SelectedCardPayload = {
  card_id: number;
  orientation: "upright" | "reversed";
};

function TarotResultContent() {
  const searchParams = useSearchParams();
  const { isAuthenticated } = useAuth();
  const { trackMeaningEvent } = useMeaningRuntime();
  const locale: FlowPracticesChromeLocale = getLocale() === "ru" ? "ru" : "en";
  const tc = useMemo(() => tarotSpreadResultChromeBundle(locale), [locale]);
  const spreadId = searchParams?.get("spread") || "one_card";
  const question = searchParams?.get("question")?.trim() || "";
  const concernDomain = (searchParams?.get("domain") as TarotConcernDomain | null) || null;
  const selected = searchParams?.get("selected")?.trim() || "";
  const sessionKey = `${spreadId}:${question}:${selected}`;

  const guestBlocked =
    !isAuthenticated && isGuestTarotLimitReached() && !canGuestAccessTarotSpread(sessionKey);

  const [loading, setLoading] = useState(true);
  const [result, setResult] = useState<TarotResult | null>(null);
  const [coreProfile, setCoreProfile] = useState<CoreProfile | null>(null);
  const [reading, setReading] = useState<TarotSpreadWithContext["reading"]>(null);
  const [tarotAnswer, setTarotAnswer] = useState<TarotAnswerV1 | null>(null);
  const [generationLogId, setGenerationLogId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const synthesisTrackedRef = useRef(false);
  const journeyEntryIdRef = useRef<string | null>(null);

  const mapSpreadId = (value: string) => value.trim() || "one_card";

  const parseSelectedCards = (value: string): SelectedCardPayload[] => {
    if (!value) return [];
    return value
      .split(",")
      .map((item) => item.trim())
      .filter(Boolean)
      .map((item) => {
        const [rawId, rawOrientation] = item.split(":");
        const cardId = Number(rawId);
        const orientation = rawOrientation === "reversed" ? "reversed" : "upright";
        if (!Number.isFinite(cardId)) return null;
        return { card_id: cardId, orientation };
      })
      .filter((item): item is SelectedCardPayload => item !== null);
  };

  useEffect(() => {
    if (guestBlocked) {
      setLoading(false);
      return;
    }

    const loadResult = async () => {
      try {
        const endpoint = isAuthenticated ? "/tarot/spread/context" : "/tarot/spread/context/public";
        const response = await postJson<TarotSpreadWithContext>(endpoint, {
          spread_id: mapSpreadId(spreadId),
          question: question || null,
          concern_domain: concernDomain,
          selected_cards: parseSelectedCards(selected),
        });
        setResult(response.spread);
        setCoreProfile(response.core_profile || null);
        setReading(response.reading || null);
        setTarotAnswer(response.tarot_answer_v1 || null);
        setGenerationLogId(response.generation_log_id ?? null);
        if (!isAuthenticated) {
          tryConsumeGuestTarotSpread(sessionKey);
        }
      } catch (err) {
        console.error("Failed to load result", err);
        setError(tc.tarotSpreadResultErrorLoadFailed);
      } finally {
        setLoading(false);
      }
    };

    void loadResult();
  }, [selected, spreadId, question, concernDomain, tc, isAuthenticated, sessionKey, guestBlocked]);

  useEffect(() => {
    synthesisTrackedRef.current = false;
    journeyEntryIdRef.current = null;
  }, [sessionKey]);

  useEffect(() => {
    if (!result || journeyEntryIdRef.current) return;
    const entry = appendTarotJourneyEntry({
      question: question || "Твой вопрос",
      concernDomain,
      spreadId: result.spread_id || spreadId,
      spreadTitle: result.title || spreadId,
      cardIds: result.cards.map((c) => c.card.id),
      cardNames: result.cards.map((c) => c.card.name),
    });
    journeyEntryIdRef.current = entry.id;
  }, [result, question, concernDomain, spreadId]);

  useEffect(() => {
    if (loading || !result || synthesisTrackedRef.current) return;
    synthesisTrackedRef.current = true;
    trackMeaningEvent({
      event_type: "first_synthesis_viewed",
      event_source: "flow",
      local_date: todayDayKey(),
      idempotency_key: tarotFlowEventKey(sessionKey, "synthesis-viewed"),
      payload: {
        spread_id: result.spread_id || spreadId,
        question_text: question || null,
        concern_domain: concernDomain,
        generation_id: generationLogId,
      },
    });
    trackMeaningEvent({
      event_type: "tarot_spread_done",
      event_source: "flow",
      local_date: todayDayKey(),
      idempotency_key: tarotFlowEventKey(sessionKey, "spread-done"),
      payload: {
        spread_id: result.spread_id || spreadId,
        question_text: question || null,
        concern_domain: concernDomain,
        generation_id: generationLogId,
      },
    });
  }, [loading, result, sessionKey, spreadId, question, concernDomain, generationLogId, trackMeaningEvent]);

  const handleFollowUpTracked = useCallback(
    (chip: TarotFollowUpChip) => {
      trackMeaningEvent({
        event_type: "tarot_reading_follow_up",
        event_source: "flow",
        local_date: todayDayKey(),
        idempotency_key: tarotFlowEventKey(sessionKey, `follow-up-${chip.id}`),
        payload: {
          chip_id: chip.id,
          chip_label: chip.label,
          spread_id: result?.spread_id || spreadId,
          question_text: question || null,
          concern_domain: concernDomain,
          generation_id: generationLogId,
        },
      });
    },
    [trackMeaningEvent, sessionKey, result?.spread_id, spreadId, question, concernDomain, generationLogId],
  );

  useEffect(() => {
    if (!isAuthenticated) return;
    getJson<{ favorites: number[] }>("/tarot/favorites").catch(() => undefined);
  }, [isAuthenticated]);

  const leadCard = result?.cards?.[0] || null;
  const leadCardId = leadCard?.card?.id || null;
  const journalHref = leadCardId ? `/journal?tarot_card_id=${leadCardId}` : "/journal";

  const storyModel = useMemo(() => {
    if (!result) return null;
    const identity = coreProfile?.interpretation?.identity || "";
    const spreadInput = {
      question: question || null,
      spreadTitle: result.title || tc.tarotSpreadResultDefaultSpreadTitle,
      cards: result.cards.map((cardData) => ({
        cardId: cardData.card.id,
        englishName: cardData.card.name,
        orientation: cardData.orientation,
        position: cardData.position,
        meaning: cardData.meaning,
        uprightText: cardData.card.upright,
        reversedText: cardData.card.reversed,
      })),
      reading,
      profileIdentity: identity || null,
      concernDomain,
      locale,
      saveHref: journalHref,
    };
    if (tarotAnswer?.main_answer?.trim()) {
      return buildTarotReadingStoryFromAnswer({ ...spreadInput, tarotAnswer });
    }
    return buildTarotReadingStoryFromSpread(spreadInput);
  }, [result, question, reading, tarotAnswer, coreProfile, concernDomain, locale, tc, journalHref]);

  if (guestBlocked) {
    return (
      <>
        <Link href="/tarot" className={shell.shellBack}>
          ← {tc.tarotSpreadResultModeLabel}
        </Link>
        <GuestAccessLimitGate
          title={GUEST_ACCESS_COPY.tarotLimitTitle}
          body={GUEST_ACCESS_COPY.tarotLimitBody}
          secondaryHref="/tarot"
          secondaryLabel={tc.tarotSpreadResultBackToTarot}
          testId="guest-tarot-result-limit"
        />
      </>
    );
  }

  if (loading) {
    return (
      <>
        <Link href="/tarot" className={shell.shellBack}>
          ← {tc.tarotSpreadResultModeLabel}
        </Link>
        <div className={s.tarotWebLoading}>
          <LoadingSpinner size="lg" />
        </div>
      </>
    );
  }

  if (error || !result || !storyModel) {
    return (
      <>
        <Link href="/tarot" className={shell.shellBack}>
          ← {tc.tarotSpreadResultModeLabel}
        </Link>
        <div className={s.tarotWebError}>
          <h1 className={s.tarotWebErrorTitle}>{error || tc.tarotSpreadResultErrorNotFound}</h1>
          <Link href="/tarot">
            <DsButton variant="secondary">{tc.tarotSpreadResultBackToTarot}</DsButton>
          </Link>
        </div>
      </>
    );
  }

  return (
    <>
      <Link href="/tarot" className={shell.shellBack}>
        ← {tc.tarotSpreadResultModeLabel}
        {result.title ? ` · ${result.title}` : ""}
      </Link>
      <TarotWebResult
        locale={locale}
        model={storyModel}
        spreadTitle={result.title || undefined}
        extraActions={
          <div className={s.tarotWebActions}>
            <Link href="/tarot">
              <DsButton variant="secondary" size="sm">
                {tc.tarotSpreadResultBackToTarot}
              </DsButton>
            </Link>
            <Link
              href={`/tarot/spread/${encodeURIComponent(result.spread_id || spreadId)}${question ? `?question=${encodeURIComponent(question)}` : ""}`}
            >
              <DsButton variant="secondary" size="sm">
                {tc.tarotSpreadResultReturnSpreadOneCard}
              </DsButton>
            </Link>
          </div>
        }
      />
    </>
  );
}

export default function TarotResultPage() {
  return (
    <Suspense
      fallback={
        <>
          <Link href="/tarot" className={shell.shellBack}>
            ← {tarotScreenBackLabel()}
          </Link>
          <div className={s.tarotWebLoading}>
            <LoadingSpinner size="lg" />
          </div>
        </>
      }
    >
      <TarotResultContent />
    </Suspense>
  );
}
