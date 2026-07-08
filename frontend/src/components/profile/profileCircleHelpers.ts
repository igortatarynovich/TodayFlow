import { buildPairCompatibilityRoute, type CompatibilityProfileLike } from "@/lib/compatibilityRoutes";

export function profileCircleRoleLabel(item: CompatibilityProfileLike): string {
  if (item.is_primary || item.relation === "self") return "Личный профиль";
  if (item.relation === "partner") return "Партнер / супруг";
  if (item.relation === "child") return "Ребенок";
  return "Близкий человек";
}

export function profileCircleRoleHint(item: CompatibilityProfileLike): string {
  if (item.is_primary || item.relation === "self") {
    return "Это центр системы: через этот профиль читаются Today, прогнозы, таро и все сравнения с другими людьми.";
  }
  if (item.relation === "partner") {
    return "Эту связь лучше читать через совместимость и сценарии контакта, а не только через общий профиль.";
  }
  if (item.relation === "child") {
    return "Этот профиль нужен для семейной оптики: как лучше поддерживать, объяснять и не усиливать напряжение в контакте.";
  }
  return "Этот человек остается частью твоего круга: его можно быстро открыть в совместимости и в вопросах про отношения.";
}

export function profileCircleRoute(
  item: CompatibilityProfileLike,
  primaryProfileId?: number | null,
): { href: string; label: string } {
  if (item.is_primary || item.relation === "self") {
    return { href: "/today", label: "Открыть мой день" };
  }
  return buildPairCompatibilityRoute(item, primaryProfileId);
}
