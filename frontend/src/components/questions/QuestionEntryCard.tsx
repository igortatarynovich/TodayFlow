"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { LoadingSpinner } from "@/components/orbit";
import { useToast } from "@/components/ToastProvider";
import { postJson } from "@/lib/api";
import type { JTBDLane, QuestionAnswerResponse } from "@/lib/types";
import { useMeaningRuntime } from "@/hooks/useMeaningRuntime";
import { GuidanceResultCard } from "@/components/guidance/GuidanceResultCard";

type QuestionEntryCardProps = {
  eyebrow?: string;
  title: string;
  body: string;
  placeholder: string;
  quickPrompts?: readonly string[];
  primaryLabel?: string;
  secondaryHref?: string;
  secondaryLabel?: string;
  initialQuestion?: string;
  preferredLane?: JTBDLane;
  hubLaneHint?: JTBDLane;
  surfaceId?: string;
};

const LANE_BADGES: Record<string, string> = {
  love: "Отношения",
  money_career: "Деньги и карьера",
  self: "Самопонимание",
  future: "Будущее",
  decision: "Решение",
  daily: "Сегодня",
  state: "Состояние",
  pattern: "Паттерны",
};

export function QuestionEntryCard({
  eyebrow = "Question-First",
  title,
  body,
  placeholder,
  quickPrompts = [],
  primaryLabel = "Получить ответ",
  secondaryHref,
  secondaryLabel,
  initialQuestion = "",
  preferredLane,
  hubLaneHint,
  surfaceId,
}: QuestionEntryCardProps) {
  const router = useRouter();
  const toast = useToast();
  const { trackMeaningEvent } = useMeaningRuntime();
  const [question, setQuestion] = useState(initialQuestion);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<QuestionAnswerResponse | null>(null);
  const [feedbackSignal, setFeedbackSignal] = useState<"answer_helpful" | "still_unclear" | null>(null);
  const memoryHistory = result?.memory_context?.history || [];

  const submit = async (nextQuestion?: string) => {
    const value = (nextQuestion ?? question).trim();
    if (value.length < 3) {
      toast.error("Сформулируй вопрос чуть конкретнее");
      return;
    }

    try {
      setLoading(true);
      const response = await postJson<QuestionAnswerResponse>("/questions/answer", {
        question: value,
        preferred_lane: preferredLane ?? null,
        hub_lane_hint: hubLaneHint ?? null,
      });
      setQuestion(value);
      setResult(response);
      setFeedbackSignal(null);
      trackMeaningEvent({
        event_type: "guidance_ask",
        event_source: "insight",
        payload: {
          lane: response.lane,
          question: value,
          has_memory_context: Boolean(response.memory_context),
        },
      });
    } catch (error) {
      console.error("Failed to answer question", error);
      toast.error("Не удалось собрать ответ. Проверь сеть и попробуй еще раз.");
    } finally {
      setLoading(false);
    }
  };

  const handleSuggestedRoute = async () => {
    if (!result) return;
    const baseHref = result.lane === "decision" ? `/questions/decision?question=${encodeURIComponent(result.question)}` : result.suggested_route.href;
    const hrefObject = new URL(baseHref, window.location.origin);
    const hrefParams = hrefObject.searchParams;
    const hrefPath = `${hrefObject.pathname}${hrefObject.search}`;

    if (result.generation_log_id) {
      try {
        await postJson("/learning/feedback", {
          generation_log_id: result.generation_log_id,
          signal: "route_opened",
          metadata: {
            source_surface: surfaceId || "question_entry",
            lane: result.lane,
            preferred_lane: preferredLane || null,
            hub_lane_hint: hubLaneHint || null,
            route_href: hrefPath,
            route_label: result.suggested_route.label,
          },
        });
      } catch (error) {
        console.error("Failed to log question route feedback", error);
      }

      hrefParams.set("jtbd_log_id", String(result.generation_log_id));
      hrefParams.set("jtbd_signal", "route_completed");
      hrefParams.set("jtbd_lane", result.lane);
      hrefParams.set("jtbd_surface", surfaceId || "question_entry");
      hrefParams.set("jtbd_route", hrefObject.pathname);
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
          source_surface: surfaceId || "question_entry",
          lane: result.lane,
          preferred_lane: preferredLane || null,
          hub_lane_hint: hubLaneHint || null,
          question: result.question,
        },
      });
      setFeedbackSignal(signal);
      toast.success(signal === "answer_helpful" ? "Сигнал сохранён" : "Отметил, что ответу не хватило ясности");
    } catch (error) {
      console.error("Failed to log question answer feedback", error);
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

      <div style={{ display: "grid", gap: "var(--orbit-space-lg)", gridTemplateColumns: quickPrompts.length ? "1.05fr 0.95fr" : "1fr" }}>
        <section className="orbit-card" style={{ padding: "1rem", background: "rgba(255,255,255,0.74)" }}>
          <label className="orbit-body" style={{ display: "block", marginBottom: "0.55rem", color: "#352515", fontWeight: 600 }}>
            Твой вопрос
          </label>
          <textarea
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder={placeholder}
            style={{
              width: "100%",
              minHeight: "132px",
              padding: "0.95rem 1rem",
              border: "1px solid #e5ded2",
              borderRadius: "18px",
              background: "#fffdf9",
              color: "#334155",
              resize: "vertical",
              outline: "none",
            }}
          />
          <div style={{ display: "flex", gap: "0.6rem", flexWrap: "wrap", marginTop: "1rem" }}>
            <button type="button" className="orbit-button orbit-button-primary" disabled={loading} onClick={() => void submit()}>
              {loading ? (
                <>
                  <LoadingSpinner size="sm" />
                  Собираю ответ...
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

        {quickPrompts.length ? (
          <section className="orbit-card" style={{ padding: "1rem", background: "rgba(255,255,255,0.74)" }}>
            <p className="orbit-body-xs" style={{ margin: 0, color: "#8f6e43", textTransform: "uppercase", letterSpacing: "0.08em" }}>
              Быстрые входы
            </p>
            <div style={{ display: "grid", gap: "0.65rem", marginTop: "0.8rem" }}>
              {quickPrompts.map((prompt) => (
                <button
                  key={prompt}
                  type="button"
                  onClick={() => void submit(prompt)}
                  className="orbit-button orbit-button-secondary"
                  style={{ justifyContent: "flex-start", textAlign: "left" }}
                >
                  {prompt}
                </button>
              ))}
            </div>
          </section>
        ) : null}
      </div>

      {result ? (
        <section style={{ display: "grid", gap: "var(--orbit-space-lg)", gridTemplateColumns: "1.1fr 0.9fr" }}>
          <div style={{ display: "grid", gap: "var(--orbit-space-lg)" }}>
            <GuidanceResultCard
              modeLabel={LANE_BADGES[result.lane] || result.lane_title}
              title={result.question}
              currentFocus={result.editorial?.current_focus || result.answer.clarity}
              manifestation={result.answer.explanation}
              caution={result.answer.forecast}
              nextStepText={result.editorial?.next_step || result.answer.today}
              nextStepLabel={result.suggested_route.label}
              onNextStep={() => void handleSuggestedRoute()}
              profileHint={!result.profile_ready ? "Ответ пока без полного профиля" : null}
            />
            <section className="orbit-card" style={{ padding: "1rem", background: "rgba(255,255,255,0.8)" }}>
              <h3 className="orbit-heading-2" style={{ marginBottom: "0.65rem", fontSize: "1.02rem" }}>
                Полная структура ответа
              </h3>
              <div style={{ display: "grid", gap: "0.8rem" }}>
                {[
                  ["Ясность", result.answer.clarity],
                  ["Объяснение", result.answer.explanation],
                  ["Прогноз", result.answer.forecast],
                  ["Решение", result.answer.decision],
                  ["Сегодня", result.answer.today],
                ].map(([blockTitle, text]) => (
                  <div
                    key={blockTitle}
                    style={{
                      padding: "0.9rem 0.95rem",
                      borderRadius: "16px",
                      background: "#fffdf9",
                      border: "1px solid #ece4d8",
                    }}
                  >
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
                Уже похоже на твою ситуацию?
              </h3>
              <p className="orbit-body-sm" style={{ margin: 0, color: "#6a5132", lineHeight: 1.65 }}>
                Unlock full clarity: что делать прямо сейчас, чего избегать и какой шаг даст лучший результат в ближайшие 7 дней.
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
                Этот ответ помог?
              </p>
              <div style={{ display: "flex", gap: "0.65rem", flexWrap: "wrap", marginTop: "0.75rem" }}>
                <button
                  type="button"
                  className="orbit-button orbit-button-secondary"
                  onClick={() => void handleAnswerFeedback("answer_helpful")}
                  disabled={feedbackSignal === "answer_helpful"}
                >
                  {feedbackSignal === "answer_helpful" ? "Помогло" : "Да, это дало ясность"}
                </button>
                <button
                  type="button"
                  className="orbit-button orbit-button-secondary"
                  onClick={() => void handleAnswerFeedback("still_unclear")}
                  disabled={feedbackSignal === "still_unclear"}
                >
                  {feedbackSignal === "still_unclear" ? "Отмечено" : "Пока не хватает ясности"}
                </button>
              </div>
            </section>
          </section>
        </section>
      ) : null}
    </section>
  );
}
