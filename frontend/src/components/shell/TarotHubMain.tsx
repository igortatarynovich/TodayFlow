"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useMemo, useState } from "react";
import { TAROT_HUB_SPREADS } from "@/components/shell/tarotShellStepper";
import s from "@/components/shell/tarotShell.module.css";
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
 * Карта дня и число дня живут исключительно в ритуале «Сегодня».
 */
export function TarotHubMain() {
  const router = useRouter();
  const [selectedSpreadId, setSelectedSpreadId] = useState<string | null>(null);

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
        <p className={s.hubEyebrow}>Таро</p>
        <div className={s.hubPills}>
          <span className={s.hubPill}>Ритуал ясности</span>
          <span className={s.hubPill}>Вопрос → расклад → шаг</span>
        </div>
      </header>

      <section className={s.hubHeroRow}>
        <div className={s.hubHeroCard}>
          <h1 className={s.hubHeroTitle}>Спроси о том, что сейчас важно.</h1>
          <p className={s.hubHeroLead}>
            Не прогноз «что будет», а зеркало: где ты сейчас, что мешает и какой следующий шаг
            выглядит честнее. Карта дня открывается только в «Сегодня» — здесь только твой вопрос.
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
          aria-label={recommended?.title ?? "Три карты"}
        >
          <div className={s.hubRitualCardImage} aria-hidden />
          <div className={s.hubRitualOverlay}>
            <p className={s.hubRitualEyebrow}>Хороший старт</p>
            <p className={s.hubRitualTitle}>Три карты: контекст · тень · действие</p>
          </div>
        </Link>
      </section>

      <section className={s.hubBottomRow}>
        <div className={s.hubSpreadPanel} style={{ gridColumn: "1 / -1" }}>
          <div className={s.hubSpreadHeader}>
            <div>
              <p className={s.hubRitualEyebrow}>Выбери формат</p>
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
      </section>
    </>
  );
}
