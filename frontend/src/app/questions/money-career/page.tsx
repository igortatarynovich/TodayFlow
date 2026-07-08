"use client";

import { useEffect, useState } from "react";
import { QuestionEntryCard } from "@/components/questions/QuestionEntryCard";
import { ProductPageScreen } from "@/components/product-ui/ProductPageScreen";
import pl from "@/design-system/layouts/productPageLayout.module.css";
import { getJson } from "@/lib/api";
import { buildAdaptiveQuestionSurface } from "@/lib/questionsHub";
import type { QuestionsHubContextResponse } from "@/lib/types";

const MONEY_CAREER_PROMPTS = [
  "Почему мои доходы не растут, хотя я много делаю?",
  "Стоит ли мне принимать этот оффер?",
  "На чем мне сейчас лучше строить карьерный рост?",
  "Это временная просадка или мне пора менять траекторию?",
] as const;

export default function MoneyCareerQuestionsPage() {
  const [hubContext, setHubContext] = useState<QuestionsHubContextResponse | null>(null);
  const adaptive = buildAdaptiveQuestionSurface(
    "money_career",
    {
      title: "Вход для вопросов про деньги и карьеру",
      body: "Этот слой нужен, когда вопрос уже про роль, доход, рост, оффер, проект или цену твоих усилий. Он собирает ответ через реальность, рычаг и следующий карьерный ход.",
      placeholder: "Например: стоит ли мне сейчас брать этот оффер или сначала пересобрать позиционирование и доходную модель на текущем месте?",
      quickPrompts: MONEY_CAREER_PROMPTS,
    },
    hubContext,
  );

  useEffect(() => {
    getJson<QuestionsHubContextResponse>("/questions/context")
      .then(setHubContext)
      .catch((error) => console.error("Failed to load money/career questions context", error));
  }, []);

  return (
    <ProductPageScreen
      testId="questions-money-career-page"
      title={adaptive.title || "Вход для вопросов про деньги и карьеру"}
      hideHeader
      contentClassName={`${pl.content} ${pl.legacyHost}`}
    >
      <QuestionEntryCard
        eyebrow="Money / Career OS"
        title={adaptive.title || "Вход для вопросов про деньги и карьеру"}
        body={adaptive.body || ""}
        placeholder={adaptive.placeholder || ""}
        quickPrompts={adaptive.quickPrompts || MONEY_CAREER_PROMPTS}
        primaryLabel="Разобрать вопрос о деньгах и карьере"
        secondaryHref="/questions"
        secondaryLabel="Назад к Questions"
        preferredLane="money_career"
        surfaceId="money_career_os_page"
      />
    </ProductPageScreen>
  );
}
