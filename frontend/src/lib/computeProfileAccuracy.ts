import type { CoreProfile } from "@/lib/types";
import type { RewardsSnapshot } from "@/lib/rewards";

export type ProfileAccuracySummary = {
  percent: number;
  hints: string[];
};

export function computeProfileAccuracy(args: {
  core: CoreProfile | null;
  rewards: RewardsSnapshot | null;
  circleCount: number;
}): ProfileAccuracySummary {
  const hints: string[] = [];
  let score = 0;

  const astro = args.core?.astro;
  if (astro?.birth_date) score += 12;
  else hints.push("добавить дату рождения");

  if (astro?.time_unknown === false && astro?.birth_time) score += 18;
  else hints.push("добавить время рождения — так точнее Луна и дома");

  if (astro?.location_name?.trim()) score += 10;
  else hints.push("уточнить место рождения");

  const gender = args.core?.person?.gender;
  if (gender && gender !== "unspecified") score += 5;

  const signals = args.core?.living?.signal_profile?.signals_days ?? 0;
  if (signals >= 10) score += 18;
  else if (signals >= 3) score += 12;
  else if (signals >= 1) score += 6;
  else hints.push("чаще отвечать в Today — так растёт поведенческий слой");

  const reflection = args.rewards?.scores?.reflection ?? 0;
  if (reflection >= 12) score += 12;
  else if (reflection >= 4) score += 6;
  else hints.push("сделать несколько вечерних фиксаций подряд");

  if (args.circleCount >= 2) score += 12;
  else hints.push("добавить важного человека в круг");

  const discipline = args.rewards?.scores?.discipline ?? 0;
  if (discipline >= 10) score += 8;
  else if (discipline >= 3) score += 4;
  else hints.push("отмечать сработавшие советы и маленькие шаги");

  return { percent: Math.min(100, Math.round(score)), hints: hints.slice(0, 6) };
}
