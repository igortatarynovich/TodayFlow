"use client";

import Link from "next/link";
import Image from "next/image";
import { useRouter } from "next/navigation";
import { useEffect, useMemo, useState } from "react";
import { TAROT_HUB_SPREADS } from "@/components/shell/tarotShellStepper";
import s from "@/components/shell/tarotShell.module.css";
import { getJson } from "@/lib/api";
import { useAuth } from "@/lib/useAuth";
import {
  buildTarotRitualHref,
  composeTarotQuestion,
  TAROT_SPREAD_OFFERS,
} from "@/lib/tarotQuestionFlowCanon";
import {
  createTarotQuestionSession,
  patchTarotQuestionSession,
  readTarotQuestionSession,
} from "@/lib/tarotQuestionSession";
import type { TarotDailyDraw } from "@/lib/types";
import { tarotCardFaceSrc } from "@/lib/tarotCardAssets";

export function TarotHubMain() {
  const router = useRouter();
  const { isAuthenticated } = useAuth();
  const [cardOfDay, setCardOfDay] = useState<TarotDailyDraw | null>(null);
  const [selectedSpreadId, setSelectedSpreadId] = useState<string | null>(null);

  useEffect(() => {
    const endpoint = isAuthenticated ? "/tarot/daily" : "/tarot/daily/public";
    void getJson<TarotDailyDraw>(endpoint)
      .then(setCardOfDay)
      .catch(() => setCardOfDay(null));
  }, [isAuthenticated]);

  const cardName = cardOfDay?.card?.name ?? "Звезда XVII";
  const cardId = cardOfDay?.card?.id ?? 17;
  const cardSrc = tarotCardFaceSrc(cardId);

  const continueHref = useMemo(() => {
    const session = readTarotQuestionSession();
    if (!session?.spreadId) return "/tarot/question";
    const question = composeTarotQuestion({
      concernDomain: session.concernDomain,
      refinementId: session.refinementId,
      customQuestion: session.customQuestion,
    });
    return buildTarotRitualHref({
      spreadId: session.spreadId,
      question,
      concernDomain: session.concernDomain,
      refinementId: session.refinementId,
    });
  }, []);

  const handleSpreadPick = (spreadId: string) => {
    setSelectedSpreadId(spreadId);
    const base = readTarotQuestionSession() ?? createTarotQuestionSession();
    patchTarotQuestionSession({ ...base, spreadId, step: "spread" });
    router.push("/tarot/question");
  };

  const recommended = TAROT_SPREAD_OFFERS.find((o) => o.spreadId === "three_cards");

  return (
    <>
      <header className={s.hubHeader}>
        <p className={s.hubEyebrow}>Tarot / Immersive Hub</p>
        <div className={s.hubPills}>
          <span className={s.hubPill}>☾ Тёмный режим</span>
          <span className={s.hubPill}>3 расклада</span>
          <span className={s.hubPill}>Сегодня: {cardName}</span>
        </div>
      </header>

      <section className={s.hubHeroRow}>
        <div className={s.hubHeroCard}>
          <h1 className={s.hubHeroTitle}>Задайте вопрос дню.</h1>
          <p className={s.hubHeroLead}>
            Таро в TodayFlow — это не предсказание, а ритуал ясности. Выберите расклад,
            сформулируйте намерение и получите историю, которая связывает сегодняшний контекст с
            вашим следующим шагом.
          </p>
          <div className={s.hubHeroActions}>
            <Link href="/tarot/question" className={s.hubBtnPrimary}>
              Начать расклад
            </Link>
            <Link href={continueHref} className={s.hubBtnSecondary}>
              Продолжить прошлый вопрос
            </Link>
          </div>
        </div>

        <Link
          href="/tarot/question?spread=three_cards"
          className={s.hubRitualCard}
          aria-label={recommended?.title ?? "Recommended ritual"}
        >
          <div className={s.hubRitualCardImage} aria-hidden />
          <div className={s.hubRitualOverlay}>
            <p className={s.hubRitualEyebrow}>Recommended ritual</p>
            <p className={s.hubRitualTitle}>Три карты: контекст · тень · действие</p>
          </div>
        </Link>
      </section>

      <section className={s.hubBottomRow}>
        <div className={s.hubSpreadPanel}>
          <div className={s.hubSpreadHeader}>
            <div>
              <p className={s.hubRitualEyebrow}>Выберите формат</p>
              <h2 className={s.hubSpreadTitle}>Расклады для решения</h2>
            </div>
            <span className={s.hubPill}>4–7 мин</span>
          </div>
          <div className={s.hubSpreadGrid}>
            {TAROT_HUB_SPREADS.map((spread) => (
              <button
                key={spread.spreadId}
                type="button"
                className={`${s.hubSpreadCard} ${selectedSpreadId === spread.spreadId ? s.hubSpreadCardSelected : ""}`.trim()}
                onClick={() => handleSpreadPick(spread.spreadId)}
              >
                <span className={s.hubSpreadCount}>{spread.count}</span>
                <div>
                  <p className={s.hubSpreadCardTitle}>{spread.title}</p>
                  <p className={s.hubSpreadCardDesc}>{spread.description}</p>
                </div>
              </button>
            ))}
          </div>
        </div>

        <div className={s.hubCodPanel}>
          <p className={s.hubRitualEyebrow}>Карта дня</p>
          <div className={s.hubCodGrid}>
            <div className={s.hubCodImage}>
              {cardSrc ? (
                <Image
                  src={cardSrc}
                  alt={cardName}
                  fill
                  sizes="115px"
                  style={{ objectFit: "contain" }}
                />
              ) : null}
            </div>
            <div>
              <h3 className={s.hubCodName}>{cardName}</h3>
              <p className={s.hubCodText}>
                {cardOfDay?.card?.keywords?.[0]
                  ? `Фокус дня — «${cardOfDay.card.keywords[0]}».`
                  : "Доверие к тихому курсу. Сегодня ясность появляется не через контроль, а через мягкое возвращение к себе."}
              </p>
            </div>
          </div>
          <div className={s.hubStarterBox}>
            <p className={s.hubStarterEyebrow}>Вопрос для старта</p>
            <p className={s.hubStarterText}>
              Какой следующий шаг сделает сегодняшний день честнее и легче?
            </p>
          </div>
        </div>
      </section>
    </>
  );
}
