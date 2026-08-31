"use client";

import Link from "next/link";
import { useMemo } from "react";
import s from "@/components/shell/tarotShell.module.css";
import { ProductJourneyScene } from "@/components/product-ui/ProductJourneyScene";
import journeyStyles from "@/components/product-ui/ProductJourneyScene.module.css";
import {
  buildTarotRitualHref,
  composeTarotQuestion,
  TAROT_SPREAD_OFFERS,
} from "@/lib/tarotQuestionFlowCanon";
import { readTarotQuestionSession } from "@/lib/tarotQuestionSession";

/**
 * Таро — один launch-flow: вопрос → расклад → чтение.
 * Выбор формата живёт внутри /tarot/question; отдельной сцены «Направление» на хабе нет.
 * Дневной ритуал живёт в разделе «Сегодня», не здесь.
 */
export function TarotHubMain() {
  const continueHref = useMemo(() => {
    const session = readTarotQuestionSession();
    if (!session) return null;
    const hasProgress =
      Boolean(session.spreadId) ||
      Boolean(session.concernDomain) ||
      Boolean(session.customQuestion?.trim()) ||
      Boolean(session.refinementId);
    if (!hasProgress) return null;
    if (!session.spreadId) return "/tarot/question";
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

  const recommended = TAROT_SPREAD_OFFERS.find((o) => o.spreadId === "three_cards");

  return (
    <div className={s.hubQuietRoot} data-testid="tarot-hub-main-journey">
      <ProductJourneyScene
        variant="flat" step={1}
        title="Вопрос"
        lead="Сформулируйте чуткий запрос — не просто «что будет»."
        motif="tarot"
        plate="tarot_cards"
        testId="tarot-hub-main-question"
      >
        <p className={journeyStyles.pairSub}>
          Здесь вы задаёте вопрос и выбираете формат чтения. Ритуал дня — в разделе «Сегодня».
        </p>
        <div className={journeyStyles.actionRow}>
          <Link href="/tarot/question" className={s.hubBtnPrimary}>
            Задать вопрос
          </Link>
          {continueHref ? (
            <Link href={continueHref} className={s.hubBtnSecondary}>
              Продолжить прошлый вопрос
            </Link>
          ) : null}
          {recommended ? (
            <Link href="/tarot/question?spread=three_cards" className={journeyStyles.bridgeLink}>
              → {recommended.title}: хороший старт
            </Link>
          ) : null}
        </div>
      </ProductJourneyScene>
    </div>
  );
}
