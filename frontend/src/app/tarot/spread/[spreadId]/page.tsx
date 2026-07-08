"use client";

import Link from "next/link";
import { useParams, useRouter, useSearchParams } from "next/navigation";
import { Suspense, useEffect, useMemo, useRef, useState } from "react";
import { LoadingSpinner } from "@/components/orbit";
import { CardVisual } from "@/components/tarot/CardVisual";
import { InteractiveCardDeck } from "@/components/tarot/InteractiveCardDeck";
import shell from "@/components/shell/tarotShell.module.css";
import { DsButton } from "@/design-system";
import s from "@/components/product-ui/productWebScreens.module.css";
import { tarotSpreadResultChromeBundle } from "@/components/tarot/tarotSpreadResultChrome";
import type { FlowPracticesChromeLocale } from "@/components/today/flowPracticesMainTabChrome";
import { getLocale } from "@/lib/i18n";
import { parseTarotAnchorParam } from "@/lib/buildTarotDeepenHref";
import { composeTarotQuestion, getSpreadOffer } from "@/lib/tarotQuestionFlowCanon";
import type { TarotConcernDomain } from "@/lib/tarotQuestionFlowCanon";
import {
  buildTarotDeepenEventPayload,
  tarotDeepenIdempotencyKey,
  TAROT_DEEPEN_EVENT_SOURCE,
} from "@/lib/tarotDeepenEvents";
import { getJson, postJson } from "@/lib/api";
import type { TarotCard } from "@/lib/types";
import { useMeaningRuntime } from "@/hooks/useMeaningRuntime";
import { useAuth } from "@/lib/useAuth";
import {
  canGuestAccessTarotSpread,
  isGuestTarotLimitReached,
} from "@/lib/guestAccessStore";
import { GuestAccessLimitGate } from "@/components/guest/GuestAccessLimitGate";
import { GUEST_ACCESS_COPY } from "@/components/guest/guestAccessCopy";

type SelectedCard = { card: TarotCard; orientation: "upright" | "reversed" };

function TarotSpreadRitualContent() {
  const params = useParams<{ spreadId: string }>();
  const searchParams = useSearchParams();
  const router = useRouter();
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const { trackMeaningEvent } = useMeaningRuntime();

  const spreadId = decodeURIComponent(params?.spreadId || "one_card");
  const offer = getSpreadOffer(spreadId);
  const questionFromUrl = searchParams?.get("question")?.trim() || "";
  const domain = (searchParams?.get("domain") as TarotConcernDomain | null) || null;
  const refinementId = searchParams?.get("refinement")?.trim() || null;
  const anchorParam = parseTarotAnchorParam(searchParams?.get("anchor"));
  const deepenSource = (searchParams?.get("source") as "today" | "card_of_day" | null) || "card_of_day";

  const displayQuestion = useMemo(
    () =>
      questionFromUrl ||
      composeTarotQuestion({
        concernDomain: domain,
        refinementId,
        customQuestion: "",
      }),
    [questionFromUrl, domain, refinementId],
  );

  const requiredCount = offer?.cardCount ?? 1;
  const positionLabels = offer?.positionLabels ?? ["Фокус"];
  const requiredFromDeck = anchorParam ? Math.max(0, requiredCount - 1) : requiredCount;
  const deckSelectionLabels = anchorParam ? positionLabels.slice(1) : positionLabels;

  const [loadingDeck, setLoadingDeck] = useState(true);
  const [deckCards, setDeckCards] = useState<TarotCard[]>([]);
  const [deckPicks, setDeckPicks] = useState<SelectedCard[]>([]);
  const [anchorCard, setAnchorCard] = useState<TarotCard | null>(null);
  const [anchorLoading, setAnchorLoading] = useState(Boolean(anchorParam));
  const deepenTrackedRef = useRef(false);

  const selectedCards = useMemo(() => {
    if (!anchorParam || !anchorCard) return deckPicks;
    return [{ card: anchorCard, orientation: anchorParam.orientation }, ...deckPicks];
  }, [anchorParam, anchorCard, deckPicks]);

  useEffect(() => {
    if (!isAuthenticated) {
      return;
    }

    const deckSize = Math.max(requiredFromDeck + 5, 8);
    const loadDeck = async () => {
      try {
        setLoadingDeck(true);
        const data = await postJson<TarotCard[]>("/tarot/deck/draw", { count: deckSize });
        setDeckCards(Array.isArray(data) ? data : []);
      } catch (error) {
        console.error("Failed to load tarot deck", error);
        setDeckCards([]);
      } finally {
        setLoadingDeck(false);
      }
    };

    void loadDeck();
  }, [isAuthenticated, requiredFromDeck]);

  useEffect(() => {
    if (!anchorParam) {
      setAnchorCard(null);
      setAnchorLoading(false);
      return;
    }

    let cancelled = false;
    const loadAnchor = async () => {
      try {
        setAnchorLoading(true);
        const card = await getJson<TarotCard>(`/tarot/cards/${anchorParam.cardId}`);
        if (!cancelled) setAnchorCard(card);
      } catch (error) {
        console.error("Failed to load anchor card", error);
        if (!cancelled) setAnchorCard(null);
      } finally {
        if (!cancelled) setAnchorLoading(false);
      }
    };

    void loadAnchor();
    return () => {
      cancelled = true;
    };
  }, [anchorParam]);

  useEffect(() => {
    if (!anchorParam || !anchorCard || deepenTrackedRef.current) return;
    deepenTrackedRef.current = true;
    trackMeaningEvent({
      event_type: "tarot_deepen_started",
      event_source: TAROT_DEEPEN_EVENT_SOURCE,
      payload: buildTarotDeepenEventPayload({
        cardId: anchorParam.cardId,
        orientation: anchorParam.orientation,
        source: deepenSource,
        spreadId,
      }),
      idempotency_key: tarotDeepenIdempotencyKey({
        cardId: anchorParam.cardId,
        source: deepenSource,
      }),
      refreshRings: false,
    });
  }, [anchorParam, anchorCard, deepenSource, spreadId, trackMeaningEvent]);

  const selectedParam = useMemo(
    () => selectedCards.map((item) => `${item.card.id}:${item.orientation}`).join(","),
    [selectedCards],
  );

  const guestSessionKey = useMemo(() => {
    const paramsOut = new URLSearchParams({ spread: spreadId, selected: selectedParam || "pending" });
    if (displayQuestion) paramsOut.set("question", displayQuestion);
    if (domain) paramsOut.set("domain", domain);
    if (refinementId) paramsOut.set("refinement", refinementId);
    return paramsOut.toString();
  }, [spreadId, selectedParam, displayQuestion, domain, refinementId]);

  useEffect(() => {
    if (isAuthenticated || authLoading) return;

    const deckSize = Math.max(requiredFromDeck + 5, 8);
    const loadDeck = async () => {
      try {
        setLoadingDeck(true);
        const data = await postJson<TarotCard[]>("/tarot/deck/draw/public", { count: deckSize });
        setDeckCards(Array.isArray(data) ? data : []);
      } catch (error) {
        console.error("Failed to load guest tarot deck", error);
        setDeckCards([]);
      } finally {
        setLoadingDeck(false);
      }
    };

    void loadDeck();
  }, [isAuthenticated, authLoading, requiredFromDeck]);

  const locale: FlowPracticesChromeLocale = getLocale() === "ru" ? "ru" : "en";
  const tc = tarotSpreadResultChromeBundle(locale);

  const handleOpenResult = () => {
    if (!selectedParam) return;
    const paramsOut = new URLSearchParams({ spread: spreadId, selected: selectedParam });
    if (displayQuestion) paramsOut.set("question", displayQuestion);
    if (domain) paramsOut.set("domain", domain);
    if (refinementId) paramsOut.set("refinement", refinementId);
    router.push(`/tarot/result?${paramsOut.toString()}`);
  };

  if (authLoading) {
    return (
      <div className={s.tarotRitualLoader}>
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (!isAuthenticated) {
    if (isGuestTarotLimitReached() && !canGuestAccessTarotSpread(guestSessionKey)) {
      return (
        <>
          <Link href="/tarot/question" className={shell.shellBack}>
            ← {tc.tarotSpreadResultModeLabel}
          </Link>
          <GuestAccessLimitGate
            title={GUEST_ACCESS_COPY.tarotLimitTitle}
            body={GUEST_ACCESS_COPY.tarotLimitBody}
            secondaryHref="/tarot"
            secondaryLabel="← Назад к Таро"
            testId="guest-tarot-spread-limit"
          />
        </>
      );
    }
  }

  if (!offer) {
    return (
      <>
        <Link href="/tarot" className={shell.shellBack}>
          ← {tc.tarotSpreadResultModeLabel}
        </Link>
        <div className={s.tarotWebError}>
          <h1 className={s.tarotWebErrorTitle}>Расклад не найден.</h1>
          <Link href="/tarot">
            <DsButton variant="secondary">{tc.tarotSpreadResultBackToTarot}</DsButton>
          </Link>
        </div>
      </>
    );
  }

  return (
    <>
      <Link href="/tarot/question" className={shell.shellBack}>
        ← {tc.tarotSpreadResultModeLabel} · {offer.title}
      </Link>
      <div className={s.tarotRitualContent}>
        <header className={s.tarotRitualIntro}>
          <p className={s.tarotRitualEyebrow}>Ритуал</p>
          <h1 className={s.tarotRitualTitle}>{offer.title}</h1>
          <p className={s.tarotRitualLead}>{offer.answersQuestions}</p>
          {displayQuestion ? <p className={s.tarotRitualQuestion}>«{displayQuestion}»</p> : null}
        </header>

        <div className={s.tarotRitualLayout}>
          <aside className={s.tarotRitualSide}>
            <p className={s.tarotRitualLead} style={{ margin: 0, fontSize: "0.875rem" }}>
              {anchorParam && anchorCard
                ? `Первая карта уже на месте — добери ещё ${requiredFromDeck === 1 ? "одну" : requiredFromDeck}.`
                : `Выбери ${requiredCount === 1 ? "одну карту" : `${requiredCount} карты`} — не спеши. После выбора карта перевернётся.`}
            </p>
            {anchorParam && anchorCard ? (
              <div className={s.tarotRitualAnchor}>
                <p className={s.tarotRitualEyebrow}>{positionLabels[0] || "Якорь"}</p>
                <CardVisual card={anchorCard} orientation={anchorParam.orientation} size="sm" showName />
              </div>
            ) : null}
            <div className={s.tarotRitualActions}>
              <DsButton
                variant="primary"
                onClick={handleOpenResult}
                disabled={
                  selectedCards.length !== requiredCount ||
                  Boolean(anchorParam && (anchorLoading || !anchorCard))
                }
              >
                Получить толкование →
              </DsButton>
              <Link href="/tarot" style={{ textDecoration: "none" }}>
                <DsButton variant="secondary">← Назад</DsButton>
              </Link>
            </div>
          </aside>

          <section className={s.tarotRitualDeck}>
            {loadingDeck || (anchorParam && anchorLoading) ? (
              <div className={s.tarotRitualLoader}>
                <LoadingSpinner size="lg" />
              </div>
            ) : (
              <InteractiveCardDeck
                cards={deckCards}
                requiredCount={requiredFromDeck}
                onCardsSelected={setDeckPicks}
                spreadTitle={offer.title}
                selectionLabels={deckSelectionLabels}
                ritualIntro={
                  anchorParam
                    ? "Добери карты к якорю — это продолжение разговора с днём."
                    : "Медленно выбери карты — это часть ответа."
                }
                variant="dark"
              />
            )}
          </section>
        </div>
      </div>
    </>
  );
}

export default function TarotSpreadRitualPage() {
  return (
    <Suspense
      fallback={
        <div className={s.tarotRitualLoader}>
          <LoadingSpinner size="lg" />
        </div>
      }
    >
      <TarotSpreadRitualContent />
    </Suspense>
  );
}
