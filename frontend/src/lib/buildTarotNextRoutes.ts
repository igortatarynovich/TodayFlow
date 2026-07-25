import type { TarotConcernDomain } from "@/lib/tarotQuestionFlowCanon";
import type { TarotStoryAction } from "@/lib/buildTarotReadingStoryModel";

export function buildTarotNextRoutes(params: {
  locale: "ru" | "en";
  concernDomain?: TarotConcernDomain | string | null;
  saveHref?: string | null;
  /** Primary CTA from reading next step — e.g. fix decision criteria. */
  primaryAction?: { id: TarotStoryAction["id"]; label: string; description?: string; href: string } | null;
  compact?: boolean;
}): TarotStoryAction[] {
  const { locale, concernDomain, saveHref = "/journal", primaryAction, compact = true } = params;
  const isRu = locale === "ru";
  const domain = (concernDomain || "").toLowerCase();

  const routes: TarotStoryAction[] = [];

  if (primaryAction) {
    routes.push({
      id: primaryAction.id,
      label: primaryAction.label,
      description: primaryAction.description,
      href: primaryAction.href,
    });
  } else if (domain === "work" || domain === "decision") {
    routes.push({
      id: "save",
      label: isRu ? "Зафиксировать условия решения" : "Capture decision criteria",
      description: isRu
        ? "Запиши, что должно измениться здесь и какой первый шаг к другому варианту."
        : "Write what must change here and the first step toward the other path.",
      href: saveHref || "/journal",
    });
  } else {
    routes.push({
      id: "today",
      label: isRu ? "Открыть Today" : "Open Today",
      description: isRu ? "Посмотри, как тема дня перекликается с твоим вопросом." : "See how today's theme connects.",
      href: "/today",
    });
  }

  if (domain === "relationships" || domain === "love") {
    routes.push({
      id: "compatibility",
      label: isRu ? "Проверить совместимость" : "Check compatibility",
      description: isRu ? "Если вопрос про конкретного человека — посмотри динамику пары." : "Explore pair dynamics.",
      href: "/compatibility",
    });
  }

  // Secondary only — not a product menu as the main ending.
  if (!routes.some((r) => r.id === "save")) {
    routes.push({
      id: "save",
      label: isRu ? "Сохранить расклад" : "Save this reading",
      description: isRu ? "Зафиксируй вывод, пока он свежий." : "Capture while it's fresh.",
      href: saveHref || "/journal",
    });
  }

  if (!compact) {
    routes.push(
      {
        id: "goal",
        label: isRu ? "Поставить цель" : "Set a goal",
        href: "/growth",
      },
      {
        id: "practice",
        label: isRu ? "Начать практику" : "Start a practice",
        href: "/practices",
      },
      {
        id: "return",
        label: isRu ? "К таро" : "Back to tarot",
        href: "/tarot",
      },
    );
  }

  return routes;
}
