"use client";

import { useEffect, useState } from "react";
import { QuestionEntryCard } from "@/components/questions/QuestionEntryCard";
import { ProductPageScreen } from "@/components/product-ui/ProductPageScreen";
import pl from "@/design-system/layouts/productPageLayout.module.css";
import { getJson } from "@/lib/api";
import { buildAdaptiveQuestionSurface } from "@/lib/questionsHub";
import type { QuestionsHubContextResponse } from "@/lib/types";

const LOVE_PROMPTS = [
  "Что на самом деле происходит между нами?",
  "Стоит ли мне выходить на контакт первой?",
  "Есть ли здесь шанс на сближение или я держусь за иллюзию?",
  "Почему эта связь так сильно меня цепляет?",
] as const;

export default function LoveQuestionsPage() {
  const [hubContext, setHubContext] = useState<QuestionsHubContextResponse | null>(null);
  const adaptive = buildAdaptiveQuestionSurface(
    "love",
    {
      title: "Вход для вопросов про отношения",
      body: "Этот слой нужен, когда главный вопрос не про абстрактную совместимость, а про живую динамику: чувства, контакт, дистанцию, шанс на сближение и реальность связи.",
      placeholder: "Например: стоит ли мне сейчас снова открываться этому человеку или связь держится только на моей надежде?",
      quickPrompts: LOVE_PROMPTS,
    },
    hubContext,
  );

  useEffect(() => {
    getJson<QuestionsHubContextResponse>("/questions/context")
      .then(setHubContext)
      .catch((error) => console.error("Failed to load love questions context", error));
  }, []);

  return (
    <ProductPageScreen
      testId="questions-love-page"
      title={adaptive.title || "Вход для вопросов про отношения"}
      hideHeader
      contentClassName={`${pl.content} ${pl.legacyHost}`}
    >
      <QuestionEntryCard
        eyebrow="Love OS"
        title={adaptive.title || "Вход для вопросов про отношения"}
        body={adaptive.body || ""}
        placeholder={adaptive.placeholder || ""}
        quickPrompts={adaptive.quickPrompts || LOVE_PROMPTS}
        primaryLabel="Разобрать вопрос об отношениях"
        secondaryHref="/questions"
        secondaryLabel="Назад к Questions"
        preferredLane="love"
        surfaceId="love_os_page"
      />
    </ProductPageScreen>
  );
}
