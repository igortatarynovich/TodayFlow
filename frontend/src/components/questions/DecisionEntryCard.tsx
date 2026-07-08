"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { LoadingSpinner } from "@/components/orbit";
import { useToast } from "@/components/ToastProvider";
import { postJson } from "@/lib/api";
import type { DecisionAnswerResponse } from "@/lib/types";
import { useMeaningRuntime } from "@/hooks/useMeaningRuntime";
import { GuidanceResultCard } from "@/components/guidance/GuidanceResultCard";

type DecisionEntryCardProps = {
  eyebrow?: string;
  title: string;
  body: string;
  questionPlaceholder: string;
  optionAPlaceholder: string;
  optionBPlaceholder: string;
  primaryLabel?: string;
  secondaryHref?: string;
  secondaryLabel?: string;
  initialQuestion?: string;
  scenarios?: readonly string[];
  surfaceId?: string;
};

export function DecisionEntryCard({
  eyebrow = "Decision OS",
  title,
  body,
  questionPlaceholder,
  optionAPlaceholder,
  optionBPlaceholder,
  primaryLabel = "Разобрать решение",
  secondaryHref,
  secondaryLabel,
  initialQuestion = "",
  scenarios = [],
  surfaceId,
}: DecisionEntryCardProps) {
  const router = useRouter();
  const toast = useToast();
  const { trackMeaningEvent } = useMeaningRuntime();
  const [question, setQuestion] = useState(initialQuestion);
  const [optionA, setOptionA] = useState("");
  const [optionB, setOptionB] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<DecisionAnswerResponse | null>(null);
  const [feedbackSignal, setFeedbackSignal] = useState<"answer_helpful" | "still_unclear" | null>(null);
  const memoryHistory = result?.memory_context?.history || [];

  useEffect(() => {
    setQuestion(initialQuestion);
  }, [initialQuestion]);

  const submit = async () => {
    const cleanQuestion = question.trim();
    if (cleanQuestion.length < 3) {
      toast.error("Сформулируй решение чуть конкретнее");
      return;
    }

    try {
      setLoading(true);
      const response = await postJson<DecisionAnswerResponse>("/questions/decision", {
        question: cleanQuestion,
        option_a: optionA.trim() || null,
        option_b: optionB.trim() || null,
      });
      setResult(response);
      setFeedbackSignal(null);
      trackMeaningEvent({
        event_type: "guidance_ask",
        event_source: "insight",
        payload: {
          lane: "decision",
          question: cleanQuestion,
          has_option_a: Boolean(optionA.trim()),
          has_option_b: Boolean(optionB.trim()),
        },
      });
    } catch (error) {
      console.error("Failed to answer decision question", error);
      toast.error("Не удалось собрать разбор. Проверь сеть и попробуй еще раз.");
    } finally {
      setLoading(false);
    }
  };

  const handleSuggestedRoute = async () => {
    if (!result) return;
    const hrefObject = new URL(result.suggested_route.href, window.location.origin);

    if (result.generation_log_id) {
      try {
        await postJson("/learning/feedback", {
          generation_log_id: result.generation_log_id,
          signal: "route_opened",
          metadata: {
            source_surface: surfaceId || "decision_entry",
            lane: "decision",
            route_href: hrefObject.pathname,
            route_label: result.suggested_route.label,
            option_a: result.option_a || null,
            option_b: result.option_b || null,
          },
        });
      } catch (error) {
        console.error("Failed to log decision route feedback", error);
      }

      hrefObject.searchParams.set("jtbd_log_id", String(result.generation_log_id));
      hrefObject.searchParams.set("jtbd_signal", "route_completed");
      hrefObject.searchParams.set("jtbd_lane", "decision");
      hrefObject.searchParams.set("jtbd_surface", surfaceId || "decision_entry");
      hrefObject.searchParams.set("jtbd_route", hrefObject.pathname);
    }

    router.push(`${hrefObject.pathname}${hrefObject.search}`);
  };

  const handleAnswerFeedback = async (signal: "answer_helpful" | "still_unclear") => {
    if (!result?.generation_log_id || feedbackSignal === signal) return;

    try {
      await postJson("/learning/feedback", {
        generation_log_id: result.generation_log_id,
        signal,
        metadata: {
          source_surface: surfaceId || "decision_entry",
          lane: "decision",
          question: result.question,
          option_a: result.option_a || null,
          option_b: result.option_b || null,
        },
      });
      setFeedbackSignal(signal);
      toast.success(signal === "answer_helpful" ? "Сигнал сохранён" : "Отметил, что ответу не хватило ясности");
    } catch (error) {
      console.error("Failed to log decision answer feedback", error);
      toast.error("Не удалось сохранить feedback");
    }
  };

  return (
    <section
      className="orbit-card"
      style={{
        padding: "1rem",
        background: "linear-gradient(180deg, rgba(255,250,244,0.95), rgba(255,255,255,0.97))",
        border: "1px solid rgba(195,154,92,0.22)",
        display: "grid",
        gap: "1rem",
      }}
    >
      <div>
        <p className="orbit-body-xs" style={{ margin: 0, color: "#8f6e43", letterSpacing: "0.08em", textTransform: "uppercase" }}>
          {eyebrow}
        </p>
        <h2 className="orbit-display-sm" style={{ margin: "0.35rem 0 0.55rem", color: "#5f4323" }}>
          {title}
        </h2>
        <p className="orbit-body" style={{ color: "#7a6140", margin: 0, lineHeight: 1.7 }}>
          {body}
        </p>
      </div>

      <section style={{ display: "grid", gap: "var(--orbit-space-lg)", gridTemplateColumns: scenarios.length ? "1.05fr 0.95fr" : "1fr" }}>
        <section className="orbit-card" style={{ padding: "1rem", background: "rgba(255,255,255,0.74)" }}>
          <label className="orbit-body" style={{ display: "block", marginBottom: "0.55rem", color: "#352515", fontWeight: 600 }}>
            Решение, которое нужно принять
          </label>
          <textarea
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder={questionPlaceholder}
            style={{ width: "100%", minHeight: "120px", padding: "0.95rem 1rem", border: "1px solid #e5ded2", borderRadius: "18px", background: "#fffdf9", color: "#334155", resize: "vertical", outline: "none" }}
          />

          <div style={{ display: "grid", gap: "0.75rem", marginTop: "1rem" }}>
            <div>
              <label className="orbit-body-sm" style={{ display: "block", marginBottom: "0.35rem", color: "#6a5132" }}>
                Вариант A
              </label>
              <input
                value={optionA}
                onChange={(event) => setOptionA(event.target.value)}
                placeholder={optionAPlaceholder}
                style={{ width: "100%", padding: "0.85rem 0.95rem", border: "1px solid #e5ded2", borderRadius: "16px", background: "#fffdf9", color: "#334155", outline: "none" }}
              />
            </div>
            <div>
              <label className="orbit-body-sm" style={{ display: "block", marginBottom: "0.35rem", color: "#6a5132" }}>
                Вариант B
              </label>
              <input
                value={optionB}
                onChange={(event) => setOptionB(event.target.value)}
                placeholder={optionBPlaceholder}
                style={{ width: "100%", padding: "0.85rem 0.95rem", border: "1px solid #e5ded2", borderRadius: "16px", background: "#fffdf9", color: "#334155", outline: "none" }}
              />
            </div>
          </div>

          <div style={{ display: "flex", gap: "0.6rem", flexWrap: "wrap", marginTop: "1rem" }}>
            <button type="button" className="orbit-button orbit-button-primary" disabled={loading} onClick={() => void submit()}>
              {loading ? (
                <>
                  <LoadingSpinner size="sm" />
                  Собираю разбор...
                </>
              ) : (
                primaryLabel
              )}
            </button>
            {secondaryHref && secondaryLabel ? (
              <Link href={secondaryHref} className="orbit-button orbit-button-secondary" style={{ textDecoration: "none" }}>
                {secondaryLabel}
              </Link>
            ) : null}
          </div>
        </section>

        {scenarios.length ? (
          <section className="orbit-card" style={{ padding: "1rem", background: "rgba(255,255,255,0.74)" }}>
            <p className="orbit-body-xs" style={{ margin: 0, color: "#8f6e43", textTransform: "uppercase", letterSpacing: "0.08em" }}>
              Когда использовать
            </p>
            <div style={{ display: "grid", gap: "0.7rem", marginTop: "0.75rem" }}>
              {scenarios.map((text) => (
                <div key={text} style={{ padding: "0.85rem", borderRadius: "16px", background: "#fffdf9", border: "1px solid #ece4d8" }}>
                  <p className="orbit-body-sm" style={{ margin: 0, color: "#334155", lineHeight: 1.7 }}>
                    {text}
                  </p>
                </div>
              ))}
            </div>
          </section>
        ) : null}
      </section>

      {result ? (
        <section style={{ display: "grid", gap: "var(--orbit-space-lg)", gridTemplateColumns: "1.08fr 0.92fr" }}>
          <div style={{ display: "grid", gap: "var(--orbit-space-lg)" }}>
            <GuidanceResultCard
              modeLabel="Decision"
              title={result.question}
              currentFocus={result.editorial?.current_focus || result.answer.window}
              manifestation={result.answer.best_next_step}
              caution={result.answer.risk}
              nextStepText={result.editorial?.next_step || result.answer.check_before_deciding}
              nextStepLabel={result.suggested_route.label}
              onNextStep={() => void handleSuggestedRoute()}
            />
            <section className="orbit-card" style={{ padding: "1rem", background: "rgba(255,255,255,0.8)" }}>
              <h3 className="orbit-heading-2" style={{ marginBottom: "0.65rem", fontSize: "1.02rem" }}>
                Детальный разбор решения
              </h3>
              <div style={{ display: "grid", gap: "0.8rem" }}>
                {[
                  ["Окно решения", result.answer.window],
                  ["Риск ошибки", result.answer.risk],
                  ["Лучший следующий шаг", result.answer.best_next_step],
                  ["Что проверить", result.answer.check_before_deciding],
                  ["Когда пересмотреть", result.answer.revisit_when],
                ].map(([blockTitle, text]) => (
                  <div key={blockTitle} style={{ padding: "0.9rem 0.95rem", borderRadius: "16px", background: "#fffdf9", border: "1px solid #ece4d8" }}>
                    <p className="orbit-body-xs" style={{ margin: 0, color: "#8a6f49", textTransform: "uppercase", letterSpacing: "0.08em" }}>
                      {blockTitle}
                    </p>
                    <p className="orbit-body-sm" style={{ margin: "0.35rem 0 0", color: "#334155", lineHeight: 1.75 }}>
                      {text}
                    </p>
                  </div>
                ))}
              </div>
            </section>
          </div>

          <section style={{ display: "grid", gap: "var(--orbit-space-lg)", alignContent: "start" }}>
            <section
              className="orbit-card"
              style={{
                padding: "1rem",
                background: "linear-gradient(165deg, rgba(255,255,255,0.96) 0%, rgba(255,246,232,0.9) 100%)",
                border: "1px dashed rgba(201,168,115,0.45)",
              }}
            >
              <p className="orbit-body-xs" style={{ margin: 0, color: "#a67c3a", textTransform: "uppercase", letterSpacing: "0.08em", fontWeight: 700 }}>
                Partial answer
              </p>
              <h3 className="orbit-heading-2" style={{ margin: "0.35rem 0 0.45rem", fontSize: "1.02rem" }}>
                Видишь свой паттерн решения?
              </h3>
              <p className="orbit-body-sm" style={{ margin: 0, color: "#6a5132", lineHeight: 1.65 }}>
                Unlock full clarity: приоритеты на 7 дней, личные риски и более точный decision plan с учетом твоего профиля.
              </p>
              <div style={{ display: "flex", gap: "0.55rem", flexWrap: "wrap", marginTop: "0.75rem" }}>
                <Link href="/pricing" className="orbit-button orbit-button-primary" style={{ textDecoration: "none" }}>
                  Unlock full clarity
                </Link>
                <Link href="/tarot/journey" className="orbit-button orbit-button-secondary" style={{ textDecoration: "none" }}>
                  История раскладов
                </Link>
              </div>
            </section>

            <section className="orbit-card" style={{ padding: "1rem", background: "rgba(255,255,255,0.8)" }}>
              <p className="orbit-body-xs" style={{ margin: 0, color: "#8f6e43", textTransform: "uppercase", letterSpacing: "0.08em" }}>
                Следующий шаг
              </p>
              <h3 className="orbit-heading-2" style={{ margin: "0.35rem 0 0.45rem", fontSize: "1.08rem" }}>
                {result.suggested_route.label}
              </h3>
              <p className="orbit-body-sm" style={{ margin: 0, color: "#334155", lineHeight: 1.7 }}>
                {result.editorial?.next_step || result.suggested_route.reason}
              </p>
              <button
                type="button"
                onClick={() => void handleSuggestedRoute()}
                className="orbit-button orbit-button-primary"
                style={{ marginTop: "0.9rem", justifyContent: "center" }}
              >
                {result.suggested_route.label}
              </button>
            </section>

            {memoryHistory.length || result.memory_context?.focus_hint || result.memory_context?.prior_summary ? (
              <section className="orbit-card" style={{ padding: "1rem", background: "rgba(255,255,255,0.8)" }}>
                <p className="orbit-body-xs" style={{ margin: 0, color: "#8f6e43", textTransform: "uppercase", letterSpacing: "0.08em" }}>
                  Что важно не потерять
                </p>
                {result.memory_context?.focus_hint ? (
                  <p className="orbit-body-sm" style={{ margin: "0.45rem 0 0", color: "#6b4f2c", lineHeight: 1.7 }}>
                    {result.memory_context.focus_hint}
                  </p>
                ) : null}
                {result.memory_context?.prior_summary ? (
                  <p className="orbit-body-sm" style={{ margin: "0.45rem 0 0", color: "#334155", lineHeight: 1.7 }}>
                    {result.memory_context.prior_summary}
                  </p>
                ) : null}
                <div style={{ display: "grid", gap: "0.65rem", marginTop: "0.75rem" }}>
                  {memoryHistory.slice(0, 3).map((item, index) => (
                    <div key={`${index}-${item.question}`} style={{ padding: "0.85rem", borderRadius: "16px", background: "#fffdf9", border: "1px solid #ece4d8" }}>
                      <p className="orbit-body-sm" style={{ margin: 0, color: "#352515", lineHeight: 1.65, fontWeight: 600 }}>
                        {item.question}
                      </p>
                      {item.thesis ? (
                        <p className="orbit-body-xs" style={{ margin: "0.35rem 0 0", color: "#475569", lineHeight: 1.65 }}>
                          {item.thesis}
                        </p>
                      ) : null}
                    </div>
                  ))}
                </div>
              </section>
            ) : null}

            <section className="orbit-card" style={{ padding: "1rem", background: "rgba(255,255,255,0.8)" }}>
              <p className="orbit-body-xs" style={{ margin: 0, color: "#8f6e43", textTransform: "uppercase", letterSpacing: "0.08em" }}>
                Этот разбор помог?
              </p>
              <div style={{ display: "flex", gap: "0.65rem", flexWrap: "wrap", marginTop: "0.75rem" }}>
                <button
                  type="button"
                  className="orbit-button orbit-button-secondary"
                  onClick={() => void handleAnswerFeedback("answer_helpful")}
                  disabled={feedbackSignal === "answer_helpful"}
                >
                  {feedbackSignal === "answer_helpful" ? "Помогло" : "Да, это помогло"}
                </button>
                <button
                  type="button"
                  className="orbit-button orbit-button-secondary"
                  onClick={() => void handleAnswerFeedback("still_unclear")}
                  disabled={feedbackSignal === "still_unclear"}
                >
                  {feedbackSignal === "still_unclear" ? "Отмечено" : "Нет, ещё неясно"}
                </button>
              </div>
            </section>
          </section>
        </section>
      ) : null}
    </section>
  );
}
