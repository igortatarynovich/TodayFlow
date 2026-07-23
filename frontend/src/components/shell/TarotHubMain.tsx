"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useMemo, useState } from "react";
import { TAROT_HUB_SPREADS } from "@/components/shell/tarotShellStepper";
import s from "@/components/shell/tarotShell.module.css";
import { ProductJourneyScene } from "@/components/product-ui/ProductJourneyScene";
import journeyStyles from "@/components/product-ui/ProductJourneyScene.module.css";
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

/**
 * Таро — только расклады и вопросы.
 * Дневные символы (карта / число) живут исключительно в ритуале «Сегодня».
 * Одна композиция: вопрос → направление (формат) как шаги, не стена карт.
 */
export function TarotHubMain() {
  const router = useRouter();
  const [selectedSpreadId, setSelectedSpreadId] = useState<string | null>(null);

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

  const handleSpreadPick = (spreadId: string) => {
    setSelectedSpreadId(spreadId);
    const base = readTarotQuestionSession() ?? createTarotQuestionSession();
    patchTarotQuestionSession({ ...base, spreadId, step: "spread" });
    router.push("/tarot/question");
  };

  const recommended = TAROT_SPREAD_OFFERS.find((o) => o.spreadId === "three_cards");

  return (
    <div className={s.hubQuietRoot} data-testid="tarot-hub-main-journey">
      <ProductJourneyScene
        step={1}
        title="Вопрос"
        lead="Спроси о том, что сейчас важно — не прогноз «что будет», а зеркало следующего шага."
        motif="today"
        testId="tarot-hub-main-question"
      >
        <p className={journeyStyles.pairTitle}>Спроси о том, что сейчас важно.</p>
        <p className={journeyStyles.pairSub}>
          Дневные символы открываются только в «Сегодня». Здесь — твой вопрос и направление чтения.
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

      <ProductJourneyScene
        step={2}
        title="Направление"
        lead="Расклад как шаги формата — сколько карт и какой фокус, без стены карточек."
        motif="insight"
        testId="tarot-hub-main-direction"
      >
        <ol className={s.hubSpreadStepList} aria-label="Расклады для решения">
          {TAROT_HUB_SPREADS.map((spread, index) => {
            const selected = selectedSpreadId === spread.spreadId;
            return (
              <li key={spread.spreadId}>
                <button
                  type="button"
                  className={`${s.hubSpreadStep} ${selected ? s.hubSpreadStepSelected : ""}`.trim()}
                  onClick={() => handleSpreadPick(spread.spreadId)}
                  aria-pressed={selected}
                >
                  <span className={s.hubSpreadStepIndex} aria-hidden>
                    {index + 1}
                  </span>
                  <span className={s.hubSpreadStepCount}>{spread.count}</span>
                  <div className={s.hubSpreadStepBody}>
                    <p className={s.hubSpreadCardTitle}>{spread.title}</p>
                    <p className={s.hubSpreadCardDesc}>{spread.description}</p>
                  </div>
                </button>
              </li>
            );
          })}
        </ol>
      </ProductJourneyScene>
    </div>
  );
}
