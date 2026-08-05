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
 * Таро — вопрос и формат расклада.
 * Карта / число дня живут в ритуале «Сегодня», не здесь.
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
        variant="flat" step={1}
        title="Вопрос"
        lead="Сформулируйте чуткий запрос — не просто «что будет»."
        motif="tarot"
        plate="tarot_cards"
        testId="tarot-hub-main-question"
      >
        <p className={journeyStyles.pairSub}>
          Здесь вы задаёте вопрос и выбираете формат чтения. Карта и число дня — в разделе «Сегодня».
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
        variant="flat" step={2}
        title="Направление"
        lead="Выберите формат расклада: сколько карт и на чём фокус."
        motif="tarot"
        plate="tarot_quiet"
        testId="tarot-hub-main-direction"
      >
        <ol className={s.hubSpreadStepList} aria-label="Расклады для решения">
          {TAROT_HUB_SPREADS.map((spread, index) => {
            const active = selectedSpreadId === spread.spreadId;
            return (
              <li key={spread.spreadId}>
                <button
                  type="button"
                  className={`${s.hubSpreadStep} ${active ? s.hubSpreadStepActive : ""}`.trim()}
                  onClick={() => handleSpreadPick(spread.spreadId)}
                >
                  <span className={s.hubSpreadStepIndex}>{index + 1}</span>
                  <span className={s.hubSpreadStepBody}>
                    <span className={s.hubSpreadStepTitle}>
                      {spread.title}
                      <span className={s.hubSpreadStepMeta}>
                        {" "}
                        · {spread.count}{" "}
                        {spread.count === 1 ? "карта" : spread.count >= 2 && spread.count <= 4 ? "карты" : "карт"}
                      </span>
                    </span>
                    <span className={s.hubSpreadStepDesc}>{spread.description}</span>
                  </span>
                </button>
              </li>
            );
          })}
        </ol>
      </ProductJourneyScene>
    </div>
  );
}
