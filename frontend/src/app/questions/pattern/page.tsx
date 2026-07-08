"use client";

import { useEffect, useState } from "react";
import { QuestionEntryCard } from "@/components/questions/QuestionEntryCard";
import { ProductPageScreen } from "@/components/product-ui/ProductPageScreen";
import pl from "@/design-system/layouts/productPageLayout.module.css";
import { getJson } from "@/lib/api";
import { buildAdaptiveQuestionSurface } from "@/lib/questionsHub";
import type { QuestionsHubContextResponse } from "@/lib/types";

const PATTERN_PROMPTS = [
  "Почему я снова попадаю в один и тот же сценарий?",
  "Где запускается мой повторяющийся паттерн?",
  "Почему я снова выбираю не тех людей или проекты?",
  "Как заметить этот цикл раньше, чем он снова меня затянет?",
] as const;

export default function PatternQuestionsPage() {
  const [hubContext, setHubContext] = useState<QuestionsHubContextResponse | null>(null);
  const adaptive = buildAdaptiveQuestionSurface(
    "pattern",
    {
      title: "Вход для вопросов про повторяющиеся сценарии",
      body: "Этот слой нужен, когда проблема не выглядит случайной. Он помогает развернуть повторяющуюся связку: триггер, привычную реакцию, цену этого сценария и точку, где цикл можно заметить раньше.",
      placeholder: "Например: почему я снова оказываюсь в одном и том же сценарии, хотя каждый раз обещаю себе больше туда не заходить?",
      quickPrompts: PATTERN_PROMPTS,
    },
    hubContext,
  );

  useEffect(() => {
    getJson<QuestionsHubContextResponse>("/questions/context")
      .then(setHubContext)
      .catch((error) => console.error("Failed to load pattern questions context", error));
  }, []);

  return (
    <ProductPageScreen
      testId="questions-pattern-page"
      title={adaptive.title || "Вход для вопросов про повторяющиеся сценарии"}
      hideHeader
      contentClassName={`${pl.content} ${pl.legacyHost}`}
    >
      <QuestionEntryCard
        eyebrow="Pattern OS"
        title={adaptive.title || "Вход для вопросов про повторяющиеся сценарии"}
        body={adaptive.body || ""}
        placeholder={adaptive.placeholder || ""}
        quickPrompts={adaptive.quickPrompts || PATTERN_PROMPTS}
        primaryLabel="Разобрать повторяющийся паттерн"
        secondaryHref="/questions"
        secondaryLabel="Назад к Questions"
        preferredLane="pattern"
        surfaceId="pattern_os_page"
      />
    </ProductPageScreen>
  );
}
