import { frameForLens } from "@/lib/interpretation/formatRecognitionText";
import { polishRussianCopy } from "@/lib/interpretation/polishRussianCopy";
import type {
  ObservationCandidate,
  ObservationEvidence,
  ObservationSource,
} from "@/lib/interpretation/onboardingRecognitionTypes";
import { SOURCE_WEIGHT } from "@/lib/interpretation/onboardingRecognitionTypes";
import type { OnboardingRecognitionLens } from "@/lib/interpretation/onboardingRecognitionTypes";
import type { BirthMetadata } from "@/lib/interpretation/resolveBirthMetadata";
import type { PortraitCardType } from "@/lib/interpretation/portraitDimensions";

function evidence(source: ObservationSource, referenceKey: string, strength = 1): ObservationEvidence {
  const weight = SOURCE_WEIGHT[source];
  return { source, referenceKey, weight, contribution: weight * strength };
}

function candidate(
  id: string,
  lens: OnboardingRecognitionLens,
  raw: string,
  source: ObservationSource,
  referenceKey: string,
  strength = 1,
): ObservationCandidate {
  const text = polishRussianCopy(frameForLens(lens, raw));
  const ev = [evidence(source, referenceKey, strength)];
  return { id, lens, text, evidence: ev, score: ev[0].contribution };
}

export function generateBirthMetadataCandidates(meta: BirthMetadata): ObservationCandidate[] {
  const out: ObservationCandidate[] = [];

  if (meta.modalityRu && meta.elementRu) {
    out.push(
      candidate(
        "meta-modality-env",
        "strengthens",
        `тебе проще раскрываться там, где есть ${meta.modalityRu.toLowerCase()} ритм и пространство для ${meta.elementRu === "Воздух" ? "идей" : meta.elementRu === "Огонь" ? "инициативы" : meta.elementRu === "Земля" ? "опоры" : "глубины"}`,
        "natal.modality",
        "metadata.modality",
      ),
    );
  }

  if (meta.birthSeasonRu) {
    out.push(
      candidate(
        "meta-season",
        "strengthens",
        `рождение в ${meta.birthSeasonRu === "зима" ? "зиму" : meta.birthSeasonRu === "весна" ? "весну" : meta.birthSeasonRu === "лето" ? "лето" : "осень"} часто даёт внутренний ритм ${meta.birthSeasonRu === "зима" ? "сбора и глубины" : meta.birthSeasonRu === "весна" ? "обновления и старта" : meta.birthSeasonRu === "лето" ? "выхода наружу" : "завершения и смысла"}`,
        "calendar.birth_season",
        "metadata.season",
        0.85,
      ),
    );
  }

  if (meta.birthWeekdayRu) {
    out.push(
      candidate(
        "meta-weekday",
        "noticed_by_others",
        `люди, рождённые в ${meta.birthWeekdayRu}, часто производят впечатление человека с собственным темпом — не обязательно громким, но запоминающимся`,
        "calendar.birth_weekday",
        "metadata.weekday",
        0.8,
      ),
    );
  }

  if (meta.chineseAnimalRu) {
    out.push(
      candidate(
        "meta-chinese-balance",
        "recovery",
        `восточный знак ${meta.chineseAnimalRu} добавляет терпение и умение восстанавливаться через наблюдение, а не через суету`,
        "culture.chinese_zodiac",
        "metadata.chinese",
      ),
    );
    out.push(
      candidate(
        "meta-chinese-paradox",
        "tension",
        `одновременно стремишься к свободе и можешь долго держать дистанцию, даже когда близость уже возможна`,
        "culture.chinese_zodiac",
        "metadata.chinese.paradox",
        0.75,
      ),
    );
  }

  if (meta.personalYear != null) {
    out.push(
      candidate(
        "meta-personal-year",
        "today_focus",
        `в личном году ${meta.personalYear} полезнее выбирать меньше направлений, но доводить их до конца`,
        "numerology.personal_year",
        `numerology.personal_year.${meta.personalYear}`,
        0.9,
      ),
    );
  }

  if (meta.rulerRu) {
    out.push(
      candidate(
        "meta-ruler",
        "strengthens",
        `управитель ${meta.rulerRu} в карте усиливает тему ${meta.rulerRu === "Уран" ? "нестандартных решений" : meta.rulerRu === "Сатурн" ? "структуры и границ" : "личного стиля действия"}`,
        "natal.sign",
        "metadata.ruler",
        0.7,
      ),
    );
  }

  return out;
}

export function frameForCardType(cardType: PortraitCardType, body: string): string {
  const t = body.trim().replace(/[.!?…]+$/, "");
  const lower = t.charAt(0).toLowerCase() + t.slice(1);

  switch (cardType) {
    case "question":
      if (/^ты замечал/i.test(t)) return polishRussianCopy(`${t}.`);
      return polishRussianCopy(`Ты замечал, что ${lower}?`);
    case "recommendation":
      if (/^тебе особенно/i.test(t) || /^сложнее всего/i.test(t)) return polishRussianCopy(`${t}.`);
      return polishRussianCopy(`Тебе особенно полезно ${lower}.`);
    case "fact":
      if (/^люди обычно/i.test(t)) return polishRussianCopy(`${t}.`);
      if (/^ты /i.test(t)) return polishRussianCopy(`Люди обычно воспринимают тебя как человека, который ${lower.replace(/^ты\s+/i, "")}.`);
      return polishRussianCopy(`Люди обычно замечают: ${lower}.`);
    case "paradox":
      return polishRussianCopy(`${t}.`);
    default:
      return polishRussianCopy(`${t}.`);
  }
}
