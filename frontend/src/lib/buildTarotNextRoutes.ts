import type { TarotConcernDomain } from "@/lib/tarotQuestionFlowCanon";
import type { TarotStoryAction } from "@/lib/buildTarotReadingStoryModel";

export function buildTarotNextRoutes(params: {
  locale: "ru" | "en";
  concernDomain?: TarotConcernDomain | string | null;
  saveHref?: string | null;
}): TarotStoryAction[] {
  const { locale, concernDomain, saveHref = "/journal" } = params;
  const isRu = locale === "ru";
  const domain = (concernDomain || "").toLowerCase();

  const routes: TarotStoryAction[] = [
    {
      id: "today",
      label: isRu ? "Открыть Today" : "Open Today",
      description: isRu ? "Посмотри, как тема дня перекликается с твоим вопросом." : "See how today's theme connects.",
      href: "/today",
    },
  ];

  if (domain === "relationships" || domain === "love") {
    routes.push({
      id: "compatibility",
      label: isRu ? "Проверить совместимость" : "Check compatibility",
      description: isRu ? "Если вопрос про конкретного человека — посмотри динамику пары." : "Explore pair dynamics.",
      href: "/compatibility",
    });
  }

  routes.push(
    {
      id: "goal",
      label: isRu ? "Поставить цель" : "Set a goal",
      description: isRu ? "Перенеси один вывод расклада в конкретную цель на ближайшие дни." : "Turn one insight into a goal.",
      href: "/growth",
    },
    {
      id: "practice",
      label: isRu ? "Начать практику" : "Start a practice",
      description: isRu ? "Короткая практика поможет закрепить состояние, а не только мысль." : "A short practice to anchor the insight.",
      href: "/practices",
    },
    {
      id: "save",
      label: isRu ? "Сохранить вывод" : "Save this reading",
      description: isRu ? "Зафиксируй мысль, пока она свежая." : "Capture while it's fresh.",
      href: saveHref || "/journal",
    },
    {
      id: "return",
      label: isRu ? "Вернуться завтра" : "Come back tomorrow",
      description: isRu ? "Иногда одного дня достаточно, чтобы картина стала яснее." : "Sometimes a day brings clarity.",
      href: "/tarot",
    },
  );

  return routes;
}
