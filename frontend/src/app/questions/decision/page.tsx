"use client";

import { useSearchParams } from "next/navigation";
import { Suspense, useEffect, useState } from "react";
import { DecisionEntryCard } from "@/components/questions/DecisionEntryCard";
import { ProductPageScreen } from "@/components/product-ui/ProductPageScreen";
import pl from "@/design-system/layouts/productPageLayout.module.css";
import { getJson } from "@/lib/api";
import { buildAdaptiveQuestionSurface } from "@/lib/questionsHub";
import type { QuestionsHubContextResponse } from "@/lib/types";

export default function DecisionQuestionsPage() {
  return (
    <Suspense fallback={<DecisionQuestionsFallback />}>
      <DecisionQuestionsContent />
    </Suspense>
  );
}

function DecisionQuestionsContent() {
  const searchParams = useSearchParams();
  const questionParam = searchParams.get("question") ?? "";
  const [hubContext, setHubContext] = useState<QuestionsHubContextResponse | null>(null);
  const adaptive = buildAdaptiveQuestionSurface(
    "decision",
    {
      title: "Слой для решений, а не для гадания",
      body: "Здесь вопрос разбирается как решение: какое окно сейчас открыто, в чем реальный риск ошибки, какой следующий шаг уменьшит неопределенность и когда стоит пересмотреть выбор.",
      placeholder: "Например: стоит ли мне принимать этот оффер или остаться в текущей роли?",
      scenarios: [
        "Когда выбор уже назрел, но ты боишься ошибки.",
        "Когда нужно понять, ускоряться сейчас или подождать.",
        "Когда есть два варианта и нужно снизить эмоциональный шум.",
      ],
    },
    hubContext,
  );

  useEffect(() => {
    getJson<QuestionsHubContextResponse>("/questions/context")
      .then(setHubContext)
      .catch((error) => console.error("Failed to load decision questions context", error));
  }, []);

  return (
    <ProductPageScreen
      testId="questions-decision-page"
      title={adaptive.title || "Слой для решений, а не для гадания"}
      hideHeader
      contentClassName={`${pl.content} ${pl.legacyHost}`}
    >
      <DecisionEntryCard
        eyebrow="Decision OS"
        title={adaptive.title || "Слой для решений, а не для гадания"}
        body={adaptive.body || ""}
        questionPlaceholder={adaptive.placeholder || ""}
        optionAPlaceholder="Например: принять оффер"
        optionBPlaceholder="Например: остаться еще на квартал"
        primaryLabel="Разобрать решение"
        secondaryHref="/questions"
        secondaryLabel="Назад к Questions"
        initialQuestion={questionParam}
        surfaceId="decision_os_page"
        scenarios={adaptive.scenarios || []}
      />
    </ProductPageScreen>
  );
}

function DecisionQuestionsFallback() {
  return (
    <ProductPageScreen
      testId="questions-decision-page"
      title="Decision OS"
      loading
      loadingLabel="Загрузка…"
    />
  );
}
