import type { CombinedPlanetaryProfile } from "@/components/profile/profilePanelTypes";

export function aspectCategoryLabel(category: CombinedPlanetaryProfile["aspectInsights"][number]["category"]) {
  if (category === "fusion") return "Цельность";
  if (category === "tension") return "Конфликт";
  if (category === "polarity") return "Крайность";
  if (category === "strength") return "Естественная сила";
  return "Потенциал";
}
