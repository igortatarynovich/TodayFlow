import type { ObservationEvidence } from "@/lib/interpretation/onboardingRecognitionTypes";
import type { PortraitDimensionId } from "@/lib/interpretation/portraitDimensions";
import type { DomainWhyContext } from "@/lib/interpretation/resolveBirthMetadata";
import { polishRussianCopy } from "@/lib/interpretation/polishRussianCopy";

const ELEMENT_INSTRUMENTAL: Record<string, string> = {
  Огонь: "огненной",
  Земля: "земной",
  Воздух: "воздушной",
  Вода: "водной",
};

function elementWithStikhiya(elementRu: string | null): string | null {
  if (!elementRu) return null;
  const adj = ELEMENT_INSTRUMENTAL[elementRu];
  return adj ? `${adj} стихией` : `${elementRu.toLowerCase()} стихией`;
}

function hasSource(evidence: ObservationEvidence[], token: string): boolean {
  return evidence.some((e) => e.source.includes(token) || e.referenceKey.includes(token));
}

export function buildGlobalWhySummary(ctx: DomainWhyContext): string {
  const parts: string[] = [];
  if (ctx.sunSignRu) parts.push(ctx.sunSignRu);
  if (ctx.lifePath != null) parts.push(`число пути ${ctx.lifePath}`);
  const element = elementWithStikhiya(ctx.elementRu);
  if (element) parts.push(element);
  if (ctx.chineseAnimalRu) parts.push(`восточный знак ${ctx.chineseAnimalRu}`);

  if (parts.length === 0) return "На это указывают первые слои твоей карты.";
  if (parts.length === 1) return polishRussianCopy(`На это указывает ${parts[0]}.`);
  if (parts.length === 2) return polishRussianCopy(`На это указывают ${parts[0]} и ${parts[1]}.`);
  return polishRussianCopy(
    `На это указывают ${parts.slice(0, -1).join(", ")} и ${parts[parts.length - 1]}.`,
  );
}

export function buildDimensionWhyExplanation(
  dimensionId: PortraitDimensionId,
  evidence: ObservationEvidence[],
  ctx: DomainWhyContext,
): string {
  const element = elementWithStikhiya(ctx.elementRu);

  switch (dimensionId) {
    case "decisions": {
      const bits = [element, ctx.lifePath != null ? `числа пути ${ctx.lifePath}` : null].filter(Boolean);
      if (bits.length >= 2) {
        return polishRussianCopy(`Здесь особенно заметно влияние ${bits[0]} и ${bits[1]}.`);
      }
      if (element) return polishRussianCopy(`Здесь особенно заметно влияние ${element}.`);
      if (ctx.modalityRu) {
        return polishRussianCopy(`Такой способ решений часто связан с ${ctx.modalityRu.toLowerCase()} модальностью карты.`);
      }
      break;
    }
    case "energy_drain": {
      if (hasSource(evidence, "chinese") || ctx.chineseAnimalRu) {
        return polishRussianCopy(
          `Это часто проявляется, когда внутренний ритм ${ctx.chineseAnimalRu ? `(${ctx.chineseAnimalRu})` : ""} сталкивается с давлением извне.`,
        );
      }
      return polishRussianCopy(
        "Это часто проявляется у людей, в карте которых сильна потребность в свободе выбора и собственном темпе.",
      );
    }
    case "strength_zone": {
      if (ctx.birthSeasonRu) {
        return polishRussianCopy(
          `Среда и ритм (${ctx.birthSeasonRu}, ${ctx.modalityRu?.toLowerCase() ?? "модальность"}) здесь важнее, чем один только солнечный знак.`,
        );
      }
      if (ctx.rulerRu) {
        return polishRussianCopy(`Здесь сказывается линия ${ctx.rulerRu} — как ты действуешь, когда есть пространство.`);
      }
      break;
    }
    case "balance": {
      if (ctx.chineseAnimalRu) {
        return polishRussianCopy(`Восточный знак ${ctx.chineseAnimalRu} добавляет здесь тему восстановления через тишину и наблюдение.`);
      }
      if (ctx.lifePath != null) {
        return polishRussianCopy(`Число пути ${ctx.lifePath} часто ищет равновесие через смысл, а не через контроль.`);
      }
      break;
    }
    case "growth": {
      if (ctx.lifePath != null) {
        return polishRussianCopy(`Такой способ развития хорошо согласуется с твоим числом пути ${ctx.lifePath}.`);
      }
      if (ctx.personalYear != null) {
        return polishRussianCopy(`Личный год ${ctx.personalYear} сейчас поддерживает именно этот вектор роста.`);
      }
      break;
    }
    case "social_perception": {
      if (ctx.sunSignRu) {
        return polishRussianCopy(`Здесь сильнее ощущается влияние ${ctx.sunSignRu}${ctx.birthWeekdayRu ? ` и дня недели рождения (${ctx.birthWeekdayRu})` : ""}.`);
      }
      break;
    }
    default:
      break;
  }

  if (hasSource(evidence, "personal_year") && ctx.personalYear != null) {
    return polishRussianCopy(`Сейчас на это накладывается личный год ${ctx.personalYear} — поэтому акцент особенно заметен.`);
  }

  return buildGlobalWhySummary(ctx);
}

/** Dominant trait — unique framing */
export function buildDominantWhyExplanation(ctx: DomainWhyContext): string {
  if (ctx.lifePathEntry?.pattern && ctx.elementRu) {
    const element = elementWithStikhiya(ctx.elementRu);
    return polishRussianCopy(
      `Главная линия карты складывается из ${element ?? ctx.elementRu.toLowerCase()} и жизненного сценария числа ${ctx.lifePath} — отсюда и этот акцент.`,
    );
  }
  return buildGlobalWhySummary(ctx);
}
