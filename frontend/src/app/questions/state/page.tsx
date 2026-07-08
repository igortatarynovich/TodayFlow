"use client";

import { useEffect, useState } from "react";
import { QuestionEntryCard } from "@/components/questions/QuestionEntryCard";
import { ProductPageScreen } from "@/components/product-ui/ProductPageScreen";
import pl from "@/design-system/layouts/productPageLayout.module.css";
import { getJson } from "@/lib/api";
import { buildAdaptiveQuestionSurface } from "@/lib/questionsHub";
import type { QuestionsHubContextResponse } from "@/lib/types";

const STATE_PROMPTS = [
  "Почему мне сейчас так тяжело и как вернуть опору?",
  "Это просто усталость или я уже в перегрузе?",
  "Как пройти этот период без дальнейшего разрушения ресурса?",
  "На что мне сейчас опереться, если сил почти нет?",
] as const;

export default function StateQuestionsPage() {
  const [hubContext, setHubContext] = useState<QuestionsHubContextResponse | null>(null);
  const adaptive = buildAdaptiveQuestionSurface(
    "state",
    {
      title: "Вход для вопросов про состояние и стабилизацию",
      body: "Этот слой нужен, когда вопрос уже не про модуль и не про далекое будущее, а про перегрузку, тревогу, истощение, потерю опоры и способ пройти сложный период без саморазрушения.",
      placeholder: "Например: я очень устал и не понимаю, это временная перегрузка или мне уже нужно менять ритм и снижать нагрузку всерьёз?",
      quickPrompts: STATE_PROMPTS,
    },
    hubContext,
  );

  useEffect(() => {
    getJson<QuestionsHubContextResponse>("/questions/context")
      .then(setHubContext)
      .catch((error) => console.error("Failed to load state questions context", error));
  }, []);

  return (
    <ProductPageScreen
      testId="questions-state-page"
      title={adaptive.title || "Вход для вопросов про состояние и стабилизацию"}
      hideHeader
      contentClassName={`${pl.content} ${pl.legacyHost}`}
    >
      <QuestionEntryCard
        eyebrow="State OS"
        title={adaptive.title || "Вход для вопросов про состояние и стабилизацию"}
        body={adaptive.body || ""}
        placeholder={adaptive.placeholder || ""}
        quickPrompts={adaptive.quickPrompts || STATE_PROMPTS}
        primaryLabel="Разобрать вопрос о состоянии"
        secondaryHref="/questions"
        secondaryLabel="Назад к Questions"
        preferredLane="state"
        surfaceId="state_os_page"
      />
    </ProductPageScreen>
  );
}
