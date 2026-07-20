"use client";

import { Suspense, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { LoadingSpinner } from "@/components/orbit";
import { CardVisual } from "@/components/tarot/CardVisual";
import { useAuth } from "@/lib/useAuth";
import { getJson, postJson } from "@/lib/api";
import { useToastContext } from "@/components/ToastProvider";
import { t } from "@/lib/i18n";
import { buildTarotDeepenHref } from "@/lib/buildTarotDeepenHref";
import {
  buildTarotDeepenEventPayload,
  tarotDeepenIdempotencyKey,
  TAROT_DEEPEN_EVENT_SOURCE,
} from "@/lib/tarotDeepenEvents";
import { useMeaningRuntime } from "@/hooks/useMeaningRuntime";
import type { TarotDailyDraw } from "@/lib/types";
import type { DailyTask } from "@/lib/dashboardTypes";
import cardOfDayStyles from "@/components/tarot/TarotCardOfDayScreen.module.css";

function splitTextToParagraphs(value?: string | null) {
  if (!value) return [];

  return value
    .split(/\n+/)
    .map((item) => item.trim())
    .filter(Boolean);
}

function hasSelectedCard(draw: TarotDailyDraw | null | undefined): draw is TarotDailyDraw & { card: NonNullable<TarotDailyDraw["card"]> } {
  return Boolean(draw?.card && (draw.selection_status ?? "selected") === "selected");
}

function buildCardFocus(card: TarotDailyDraw | null) {
  if (!hasSelectedCard(card)) return null;

  const topKeyword = card.card.keywords?.[0];
  const mantraTitle = card.mantra?.title;
  const ritualTitle = card.ritual?.title;

  if (card.orientation === "reversed") {
    return topKeyword
      ? `Перевёрнутая карта: заметить перекос по теме «${topKeyword}», не ускоряться.`
      : "Перевёрнутая карта: замедлиться, меньше шума.";
  }

  if (mantraTitle && ritualTitle) {
    return `Линия дня: «${mantraTitle}» и практика «${ritualTitle}».`;
  }

  if (topKeyword) {
    return `Фокус дня: «${topKeyword}» — один якорь, без распыления.`;
  }

  return "Один спокойный фокус на день.";
}

function buildCardCare(card: TarotDailyDraw | null) {
  if (!hasSelectedCard(card)) return null;

  if (card.orientation === "reversed") {
    return "Без резких выводов из усталости — сначала тело и дыхание.";
  }

  if (card.ritual?.title) {
    return `Коротко: «${card.ritual.title}» для опоры в ритме.`;
  }

  return "Спокойный темп и паузы.";
}

function buildActionList(card: TarotDailyDraw | null, isAuthenticated: boolean) {
  const actions: string[] = [];

  if (card?.mantra?.title) {
    actions.push(`Аффирмация: «${card.mantra.title}».`);
  }
  if (card?.ritual?.title) {
    actions.push(`Практика: «${card.ritual.title}».`);
  }
  if (card?.card?.keywords?.[0]) {
    actions.push(`Заметить «${card.card.keywords[0]}» в делах и настроении.`);
  }
  if (isAuthenticated) {
    actions.push("Одно главное дело на сегодня.");
  }

  return actions.slice(0, 3);
}

function CardOfDaySkeleton() {
  return (
    <main className={`orbit-page ${cardOfDayStyles.page}`}>
      <div className={cardOfDayStyles.center}>
        <LoadingSpinner size="lg" />
      </div>
    </main>
  );
}

function CardOfDayContent() {
  const { isAuthenticated } = useAuth();
  const [loading, setLoading] = useState(true);
  const [showContent, setShowContent] = useState(false);
  const [revealed, setRevealed] = useState(false);
  const [tarotCard, setTarotCard] = useState<TarotDailyDraw | null>(null);
  const [dailyTasks, setDailyTasks] = useState<DailyTask[]>([]);
  const [detailsOpen, setDetailsOpen] = useState(false);
  const toast = useToastContext();
  const { trackMeaningEvent } = useMeaningRuntime();

  useEffect(() => {
    const bootstrap = async () => {
      try {
        if (isAuthenticated) {
          const [cardData, practice] = await Promise.all([
            // May be not_selected — never auto-assign via GET.
            getJson<TarotDailyDraw>("/tarot/daily").catch(() => null),
            getJson<{ id: string; title: string; duration_minutes?: number }>("/practices/current").catch(() => null),
          ]);

          setTarotCard(cardData);
          if (hasSelectedCard(cardData)) {
            setRevealed(true);
          }

          const tasks: DailyTask[] = [];
          if (practice) {
            tasks.push({
              id: "practice",
              title: practice.title,
              duration: `${practice.duration_minutes || 3} мин`,
              completed: false,
            });
          }
          tasks.push({
            id: "gratitude",
            title: t("dashboard.tasks.gratitudeJournal", "Дневник благодарностей"),
            completed: false,
          });
          tasks.push({
            id: "states",
            title: t("dashboard.tasks.statesJournal", "Дневник состояний"),
            completed: false,
          });
          setDailyTasks(tasks);
        } else {
          // Guests: do not load card identity from Tarot module — Today ritual only.
          setTarotCard({ date: new Date().toISOString().slice(0, 10), selection_status: "not_selected", card: null });
        }
      } catch (err) {
        console.error("Failed to load card of day", err);
        toast.error(t("dashboard.errors.failedToLoadCard", "Не удалось загрузить карту дня"));
      } finally {
        setLoading(false);
        setTimeout(() => setShowContent(true), 80);
      }
    };

    bootstrap();
  }, [isAuthenticated, toast]);

  const handleReveal = async () => {
    if (!isAuthenticated) {
      toast.error(t("dashboard.errors.authRequired", "Откройте карту дня в ритуале «Сегодня»"));
      return;
    }
    try {
      const revealedDraw = await postJson<TarotDailyDraw>("/tarot/daily/reveal", {});
      setTarotCard(revealedDraw);
      setRevealed(true);
    } catch (err) {
      console.error("Failed to reveal card of day", err);
      toast.error(t("dashboard.errors.failedToLoadCard", "Не удалось открыть карту дня"));
    }
  };

  useEffect(() => {
    if (!revealed) {
      setDetailsOpen(false);
    }
  }, [revealed]);

  useEffect(() => {
    if (!isAuthenticated) return;

    setDailyTasks((prev) => {
      const shouldHaveAffirmation = revealed && Boolean(tarotCard?.mantra);
      const hasAffirmation = prev.some((item) => item.id === "affirmation");

      if (shouldHaveAffirmation && !hasAffirmation) {
        const practiceIndex = prev.findIndex((item) => item.id === "practice");
        const insertAt = practiceIndex >= 0 ? practiceIndex + 1 : 0;
        const affirmation: DailyTask = {
          id: "affirmation",
          title: t("dashboard.tasks.repeatAffirmation", "Повторить аффирмацию"),
          duration: t("dashboard.tasks.duration30sec", "30 сек"),
          completed: false,
        };
        return [...prev.slice(0, insertAt), affirmation, ...prev.slice(insertAt)];
      }

      if (!shouldHaveAffirmation && hasAffirmation) {
        return prev.filter((item) => item.id !== "affirmation");
      }

      return prev;
    });
  }, [isAuthenticated, revealed, tarotCard?.mantra]);

  const toggleTask = async (taskId: string) => {
    if (!isAuthenticated) {
      toast.error(t("dashboard.errors.authRequired", "Необходима авторизация"));
      return;
    }

    try {
      const task = dailyTasks.find((item) => item.id === taskId);
      if (!task) return;

      setDailyTasks((prev) =>
        prev.map((item) =>
          item.id === taskId ? { ...item, completed: !item.completed } : item,
        ),
      );

      await getJson(`/challenges/tasks/${taskId}/toggle`).catch(() => {
        setDailyTasks((prev) =>
          prev.map((item) =>
            item.id === taskId ? { ...item, completed: !item.completed } : item,
          ),
        );
      });
    } catch (err) {
      console.error("Failed to toggle task", err);
    }
  };

  const completedTasksCount = dailyTasks.filter((task) => task.completed).length;
  const effectiveCard = revealed ? tarotCard : null;
  const keywords = effectiveCard?.card?.keywords?.slice(0, 3) ?? [];
  const interpretationParagraphs = useMemo(() => {
    if (!hasSelectedCard(tarotCard) || !revealed) return [];
    const source =
      tarotCard.orientation === "reversed" && tarotCard.card.reversed
        ? tarotCard.card.reversed
        : tarotCard.card.upright;
    return splitTextToParagraphs(source);
  }, [tarotCard, revealed]);
  const focusText = useMemo(() => buildCardFocus(effectiveCard), [effectiveCard]);
  const careText = useMemo(() => {
    if (effectiveCard) return buildCardCare(effectiveCard);
    return "Открой карту слева: пока она закрыта, мы не подставляем смысл дня в рекомендации и задачи.";
  }, [effectiveCard]);
  const actionList = useMemo(() => {
    if (effectiveCard) return buildActionList(effectiveCard, isAuthenticated);
    const generic: string[] = ["Открой карту — появятся конкретные шаги дня."];
    if (isAuthenticated) generic.push("Одно главное дело на сегодня.");
    return generic.slice(0, 3);
  }, [effectiveCard, isAuthenticated]);

  const deepenHref = useMemo(() => {
    if (!revealed || !tarotCard?.card?.id) return null;
    const orientation = (tarotCard.orientation === "reversed" ? "reversed" : "upright") as
      | "upright"
      | "reversed";
    return buildTarotDeepenHref({
      cardId: tarotCard.card.id,
      orientation,
      source: "card_of_day",
    });
  }, [revealed, tarotCard]);

  const trackDeepenStart = () => {
    if (!tarotCard?.card?.id) return;
    const orientation = (tarotCard.orientation === "reversed" ? "reversed" : "upright") as
      | "upright"
      | "reversed";
    trackMeaningEvent({
      event_type: "tarot_deepen_started",
      event_source: TAROT_DEEPEN_EVENT_SOURCE,
      payload: buildTarotDeepenEventPayload({
        cardId: tarotCard.card.id,
        orientation,
        source: "card_of_day",
      }),
      idempotency_key: tarotDeepenIdempotencyKey({
        cardId: tarotCard.card.id,
        source: "card_of_day",
        localDate: tarotCard.date,
      }),
      refreshRings: false,
    });
  };

  if (loading) {
    return <CardOfDaySkeleton />;
  }

  return (
    <main className={`orbit-page ${cardOfDayStyles.page}`}>
      <section style={{ padding: "clamp(1.1rem, 3vw, 2rem) 0 0" }}>
        <div className={cardOfDayStyles.shell}>
          <div
            className={`${cardOfDayStyles.heroPanel} todayflow-reveal`}
            style={{
              padding: "clamp(1.1rem, 3.5vw, 1.8rem)",
              opacity: showContent ? 1 : 0,
              transform: showContent ? "translateY(0)" : "translateY(18px)",
              transition: "opacity 360ms ease, transform 360ms ease",
            }}
          >
            <div style={{ display: "flex", flexWrap: "wrap", gap: "0.75rem", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
              <div style={{ display: "flex", flexWrap: "wrap", gap: "0.55rem" }}>
                <Link href="/today" className="orbit-button orbit-button-secondary orbit-button-sm" style={{ textDecoration: "none" }}>
                  ← Я сегодня
                </Link>
                <Link href="/tarot" className="orbit-button orbit-button-secondary orbit-button-sm" style={{ textDecoration: "none" }}>
                  Ещё таро
                </Link>
              </div>
              <div style={{ display: "flex", flexWrap: "wrap", gap: "0.45rem" }}>
                <span
                  style={{
                    display: "inline-flex",
                    alignItems: "center",
                    padding: "0.45rem 0.8rem",
                    borderRadius: "999px",
                    background: "rgba(255, 248, 236, 0.94)",
                    border: "1px solid rgba(195, 154, 92, 0.32)",
                    fontSize: "0.84rem",
                    fontWeight: 600,
                    color: "#7c5a33",
                  }}
                >
                  {tarotCard?.date ?? new Date().toISOString().slice(0, 10)}
                </span>
                {revealed ? (
                  <span
                    style={{
                      display: "inline-flex",
                      alignItems: "center",
                      padding: "0.45rem 0.8rem",
                      borderRadius: "999px",
                      background: tarotCard?.orientation === "reversed" ? "rgba(254, 242, 242, 0.96)" : "rgba(240, 253, 244, 0.96)",
                      border: tarotCard?.orientation === "reversed" ? "1px solid rgba(248, 113, 113, 0.26)" : "1px solid rgba(74, 222, 128, 0.25)",
                      fontSize: "0.84rem",
                      fontWeight: 600,
                      color: tarotCard?.orientation === "reversed" ? "#9f1239" : "#166534",
                    }}
                  >
                    {tarotCard?.orientation === "reversed" ? "Перевёрнутая карта" : "Прямая карта"}
                  </span>
                ) : (
                  <span
                    style={{
                      display: "inline-flex",
                      alignItems: "center",
                      padding: "0.45rem 0.8rem",
                      borderRadius: "999px",
                      background: "rgba(255, 255, 255, 0.9)",
                      border: "1px solid rgba(195, 154, 92, 0.2)",
                      fontSize: "0.84rem",
                      fontWeight: 600,
                      color: "#7c5a33",
                    }}
                  >
                    Сначала открой
                  </span>
                )}
              </div>
            </div>

            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
                gap: "1rem",
                alignItems: "stretch",
              }}
            >
              <div
                style={{
                  borderRadius: "24px",
                  border: "1px solid rgba(198, 166, 119, 0.28)",
                  background:
                    "radial-gradient(circle at top, rgba(214, 184, 129, 0.18), transparent 42%), linear-gradient(180deg, rgba(255,255,255,0.98) 0%, rgba(255,249,239,0.92) 100%)",
                  padding: "clamp(1rem, 3vw, 1.4rem)",
                  display: "flex",
                  flexDirection: "column",
                  justifyContent: "space-between",
                  minHeight: "100%",
                }}
              >
                <div
                  style={{
                    display: "grid",
                    gap: "0.8rem",
                    placeItems: "center",
                    marginBottom: "1rem",
                  }}
                >
                  <div
                    style={{
                      width: "208px",
                      minHeight: "364px",
                      display: "grid",
                      placeItems: "center",
                      transition: "transform 320ms ease, opacity 320ms ease",
                      transform: revealed ? "translateY(0) scale(1)" : "translateY(8px) scale(0.98)",
                      opacity: revealed ? 1 : 0.98,
                    }}
                  >
                    {tarotCard?.card ? (
                      revealed ? (
                        <CardVisual
                          card={tarotCard.card}
                          orientation={(tarotCard.orientation as "upright" | "reversed") || "upright"}
                          size="md"
                          showName={false}
                        />
                      ) : (
                        <button
                          type="button"
                          onClick={() => void handleReveal()}
                          style={{
                            width: "100%",
                            minHeight: "364px",
                            borderRadius: "22px",
                            border: "1px solid rgba(195,154,92,0.32)",
                            background:
                              "radial-gradient(circle at top, rgba(214, 184, 129, 0.22), transparent 42%), linear-gradient(180deg, rgba(124,90,51,0.96), rgba(76,53,31,0.98))",
                            boxShadow: "0 18px 40px rgba(95, 67, 35, 0.16)",
                            color: "#fff7ed",
                            cursor: "pointer",
                            display: "grid",
                            placeItems: "center",
                            padding: "1.2rem",
                            textAlign: "center",
                          }}
                        >
                          <div style={{ display: "grid", gap: "0.55rem" }}>
                            <p className="orbit-body-xs" style={{ margin: 0, textTransform: "uppercase", letterSpacing: "0.12em", color: "rgba(255,247,237,0.78)" }}>
                              Карта дня
                            </p>
                            <div style={{ fontSize: "1.75rem", lineHeight: 1, color: "rgba(255,247,237,0.85)" }}>◆</div>
                            <p className="orbit-body-sm" style={{ margin: 0, lineHeight: 1.65, color: "#fff7ed" }}>
                              Нажми, чтобы открыть.
                            </p>
                          </div>
                        </button>
                      )
                    ) : (
                      <div className="orbit-body-sm" style={{ color: "#7c5a33" }}>
                        Карта пока недоступна
                      </div>
                    )}
                  </div>

                </div>

                <div style={{ textAlign: "center" }}>
                  <h1 className="orbit-display-xs" style={{ marginBottom: "0.45rem" }}>
                    {revealed ? tarotCard?.card?.name ?? "Дневной аркан" : "Главный аркан дня"}
                  </h1>
                  {revealed ? (
                    <p className="orbit-body-sm" style={{ color: "#6a5132", lineHeight: 1.65, maxWidth: "28rem", margin: "0 auto" }}>
                      {focusText ?? null}
                    </p>
                  ) : null}
                </div>
              </div>

              <div style={{ display: "flex", flexDirection: "column", gap: "0.9rem" }}>
                <div
                  style={{
                    borderRadius: "22px",
                    border: "1px solid rgba(198, 166, 119, 0.26)",
                    background: "rgba(255, 252, 247, 0.94)",
                    padding: "1rem 1rem 0.95rem",
                  }}
                >
                  <p className="orbit-body-sm" style={{ margin: 0, color: "#5f4930", lineHeight: 1.75 }}>
                    {careText}
                  </p>
                </div>

                {keywords.length > 0 ? (
                  <div
                    style={{
                      borderRadius: "22px",
                      border: "1px solid rgba(198, 166, 119, 0.26)",
                      background: "rgba(255, 255, 255, 0.9)",
                      padding: "1rem",
                    }}
                  >
                    <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem" }}>
                      {keywords.map((keyword) => (
                        <span
                          key={keyword}
                          style={{
                            display: "inline-flex",
                            alignItems: "center",
                            padding: "0.5rem 0.8rem",
                            borderRadius: "999px",
                            background: "rgba(248, 240, 225, 0.94)",
                            border: "1px solid rgba(195, 154, 92, 0.24)",
                            color: "#7c5a33",
                            fontSize: "0.88rem",
                            fontWeight: 600,
                          }}
                        >
                          {keyword}
                        </span>
                      ))}
                    </div>
                  </div>
                ) : null}

                <div
                  style={{
                    borderRadius: "22px",
                    border: "1px solid rgba(198, 166, 119, 0.26)",
                    background: "linear-gradient(180deg, rgba(242, 250, 245, 0.96) 0%, rgba(255, 253, 250, 0.92) 100%)",
                    padding: "1rem",
                  }}
                >
                  <div style={{ display: "grid", gap: "0.65rem" }}>
                    {actionList.length > 0 ? (
                      actionList.map((action, index) => (
                        <div
                          key={`${index}-${action}`}
                          style={{
                            display: "flex",
                            gap: "0.65rem",
                            alignItems: "flex-start",
                            padding: "0.75rem 0.8rem",
                            borderRadius: "16px",
                            background: "rgba(255,255,255,0.78)",
                            border: "1px solid rgba(195, 154, 92, 0.16)",
                          }}
                        >
                          <span
                            style={{
                              flex: "0 0 auto",
                              width: "1.6rem",
                              height: "1.6rem",
                              display: "grid",
                              placeItems: "center",
                              borderRadius: "999px",
                              background: "rgba(208, 174, 120, 0.18)",
                              color: "#8a6f49",
                              fontSize: "0.82rem",
                              fontWeight: 700,
                            }}
                          >
                            {index + 1}
                          </span>
                          <p className="orbit-body-sm" style={{ margin: 0, color: "#5f4930", lineHeight: 1.6 }}>
                            {action}
                          </p>
                        </div>
                      ))
                    ) : (
                      <p className="orbit-body-sm" style={{ margin: 0, color: "#6a5132", lineHeight: 1.65 }}>
                        Загрузка карты…
                      </p>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "minmax(0, 1fr)",
              gap: "1rem",
              marginTop: "1rem",
              opacity: showContent ? 1 : 0,
              transform: showContent ? "translateY(0)" : "translateY(18px)",
              transition: "opacity 420ms ease 80ms, transform 420ms ease 80ms",
            }}
          >
            <div className="todayflow-panel" style={{ borderRadius: "24px", padding: "1rem" }}>
              <button
                type="button"
                disabled={!revealed}
                onClick={() => {
                  if (!revealed) return;
                  setDetailsOpen((prev) => !prev);
                }}
                className="orbit-button orbit-button-secondary"
                style={{ width: "100%", justifyContent: "space-between", opacity: revealed ? 1 : 0.65, cursor: revealed ? "pointer" : "not-allowed" }}
                aria-label={revealed ? "Полная интерпретация карты" : "Сначала открой карту — затем откроется полная интерпретация"}
              >
                <span>{revealed ? "Полная интерпретация карты" : "Полная интерпретация — после открытия карты"}</span>
                <span>{detailsOpen && revealed ? "−" : "+"}</span>
              </button>

              <div className={`todayflow-advanced-shell ${detailsOpen && revealed ? "is-open" : ""}`} style={{ marginTop: "0.85rem" }}>
                <div className="todayflow-advanced-shell__inner">
                  <div style={{ display: "grid", gap: "0.9rem" }}>
                    <div
                      style={{
                        borderRadius: "20px",
                        border: "1px solid rgba(198, 166, 119, 0.22)",
                        background: "rgba(255, 252, 247, 0.94)",
                        padding: "1rem",
                      }}
                    >
                      <div style={{ display: "grid", gap: "0.7rem" }}>
                        {!revealed ? (
                          <p className="orbit-body-sm" style={{ margin: 0, lineHeight: 1.7, color: "#6a5132" }}>
                            Открой карту в блоке слева — тогда появятся текст аркана и сопутствующие практики.
                          </p>
                        ) : interpretationParagraphs.length > 0 ? (
                          interpretationParagraphs.map((paragraph, index) => (
                            <p key={`${index}-${paragraph.slice(0, 20)}`} className="orbit-body-sm" style={{ margin: 0, lineHeight: 1.75, color: "#5f4930" }}>
                              {paragraph}
                            </p>
                          ))
                        ) : (
                          <p className="orbit-body-sm" style={{ margin: 0, lineHeight: 1.7, color: "#6a5132" }}>
                            Интерпретация временно недоступна.
                          </p>
                        )}
                      </div>
                    </div>

                    {revealed && (tarotCard?.mantra || tarotCard?.ritual) ? (
                      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "0.9rem" }}>
                        {tarotCard?.mantra ? (
                          <div
                            style={{
                              borderRadius: "20px",
                              border: "1px solid rgba(198, 166, 119, 0.22)",
                              background: "rgba(255, 252, 247, 0.94)",
                              padding: "1rem",
                            }}
                          >
                            <p className="orbit-body-xs" style={{ margin: "0 0 0.45rem", textTransform: "uppercase", letterSpacing: "0.12em", color: "#a17d4c" }}>
                              Аффирмация
                            </p>
                            <h3 className="orbit-heading-3" style={{ marginBottom: "0.4rem" }}>
                              {tarotCard.mantra.title}
                            </h3>
                            <p className="orbit-body-sm" style={{ margin: 0, color: "#5f4930", lineHeight: 1.7 }}>
                              {tarotCard.mantra.mantra}
                            </p>
                          </div>
                        ) : null}

                        {tarotCard?.ritual ? (
                          <div
                            style={{
                              borderRadius: "20px",
                              border: "1px solid rgba(198, 166, 119, 0.22)",
                              background: "rgba(255, 252, 247, 0.94)",
                              padding: "1rem",
                            }}
                          >
                            <p className="orbit-body-xs" style={{ margin: "0 0 0.45rem", textTransform: "uppercase", letterSpacing: "0.12em", color: "#a17d4c" }}>
                              Практика
                            </p>
                            <h3 className="orbit-heading-3" style={{ marginBottom: "0.4rem" }}>
                              {tarotCard.ritual.title}
                            </h3>
                            <p className="orbit-body-sm" style={{ margin: 0, color: "#5f4930", lineHeight: 1.7 }}>
                              {tarotCard.ritual.intention}
                            </p>
                          </div>
                        ) : null}
                      </div>
                    ) : null}
                  </div>
                </div>
              </div>
            </div>

            {isAuthenticated && dailyTasks.length > 0 ? (
              <div className="todayflow-panel" style={{ borderRadius: "24px", padding: "1rem" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", gap: "0.75rem", marginBottom: "0.8rem", flexWrap: "wrap" }}>
                  <div>
                    <h2 className="orbit-heading-2" style={{ margin: 0 }}>
                      Задачи дня
                    </h2>
                  </div>
                  <span className="todayflow-month-pill" style={{ padding: "0.45rem 0.75rem", fontSize: "0.84rem", fontWeight: 600, color: "#7c5a33" }}>
                    {completedTasksCount} из {dailyTasks.length}
                  </span>
                </div>

                <div style={{ display: "grid", gap: "0.65rem" }}>
                  {dailyTasks.map((task) => (
                    <label
                      key={task.id}
                      style={{
                        display: "flex",
                        alignItems: "center",
                        gap: "0.8rem",
                        padding: "0.9rem 0.95rem",
                        borderRadius: "18px",
                        border: "1px solid rgba(198, 166, 119, 0.18)",
                        background: task.completed ? "rgba(240, 253, 244, 0.84)" : "rgba(255, 255, 255, 0.82)",
                        cursor: "pointer",
                      }}
                    >
                      <input
                        type="checkbox"
                        checked={task.completed}
                        onChange={() => toggleTask(task.id)}
                        style={{ width: "18px", height: "18px", cursor: "pointer" }}
                      />
                      <div style={{ flex: 1, minWidth: 0 }}>
                        <p className="orbit-body-sm" style={{ margin: 0, color: "#5f4930", textDecoration: task.completed ? "line-through" : "none", opacity: task.completed ? 0.65 : 1 }}>
                          {task.title}
                        </p>
                        {task.duration ? (
                          <p className="orbit-body-xs" style={{ margin: "0.18rem 0 0", color: "#8a6f49" }}>
                            {task.duration}
                          </p>
                        ) : null}
                      </div>
                    </label>
                  ))}
                </div>
              </div>
            ) : null}

            <div style={{ display: "flex", flexWrap: "wrap", gap: "0.75rem", justifyContent: "center", marginTop: "0.25rem" }}>
              {deepenHref ? (
                <Link
                  href={deepenHref}
                  className="orbit-button orbit-button-primary"
                  style={{ textDecoration: "none" }}
                  onClick={trackDeepenStart}
                >
                  Исследовать глубже →
                </Link>
              ) : null}
              <Link
                href="/today"
                className={`orbit-button ${deepenHref ? "orbit-button-secondary" : "orbit-button-primary"}`}
                style={{ textDecoration: "none" }}
              >
                Вернуться в Today
              </Link>
              <Link href="/tarot" className="orbit-button orbit-button-secondary" style={{ textDecoration: "none" }}>
                Ещё таро
              </Link>
              <Link href="/profile" className="orbit-button orbit-button-secondary" style={{ textDecoration: "none" }}>
                Сверить с Profile
              </Link>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}

export function TarotCardOfDayScreen() {
  return (
    <Suspense fallback={<CardOfDaySkeleton />}>
      <CardOfDayContent />
    </Suspense>
  );
}
