import type { CoreProfile } from "@/lib/types";

export const ONBOARDING_CORE_PATH = "/onboarding/core";

export type CoreSetupPayload = {
  first_name: string;
  last_name?: string | null;
  label: string;
  birth_date: string;
  birth_time?: string | null;
  time_unknown: boolean;
  location_name: string;
  latitude?: number | null;
  longitude?: number | null;
  gender: string;
};

export type CoreSetupResponse = {
  status: string;
  core_profile: CoreProfile;
};

export type CoreSetupBuildStage = "idle" | "saving" | "building" | "done";

export const CORE_SETUP_BUILD_COPY: Record<
  Exclude<CoreSetupBuildStage, "idle">,
  { eyebrow: string; title: string; description: string; steps: string[] }
> = {
  saving: {
    eyebrow: "Core Setup",
    title: "Сохраняем основу",
    description: "Сначала фиксируем имя, дату, время и место рождения, чтобы персональные рекомендации были точными с первого дня.",
    steps: ["Проверяем личные данные", "Уточняем место рождения", "Готовим основу профиля"],
  },
  building: {
    eyebrow: "Life Map Build",
    title: "Собираем карту жизни",
    description: "На этом этапе объединяем натальную карту, число пути и архетип в единый личный профиль.",
    steps: ["Собираем личный профиль", "Строим натальную карту", "Связываем жизненные сферы"],
  },
  done: {
    eyebrow: "Profile Ready",
    title: "Карта собрана",
    description: "Теперь система будет использовать её в Today, Guidance и Compatibility. Чем больше ты отвечаешь и фиксируешь действия, тем точнее будут подсказки.",
    steps: ["Профиль готов", "Карта построена", "Можно открыть портрет"],
  },
};

export function createEmptyCoreSetupForm(): CoreSetupPayload {
  return {
    first_name: "",
    last_name: "",
    label: "Я",
    birth_date: "",
    birth_time: "",
    time_unknown: false,
    location_name: "",
    latitude: null,
    longitude: null,
    gender: "unspecified",
  };
}

export function mergeCoreSetupFormFromAccount(
  prev: CoreSetupPayload,
  profile: { first_name?: string | null; last_name?: string | null; gender?: string | null } | null,
  core: CoreProfile | null,
): CoreSetupPayload {
  return {
    ...prev,
    first_name: profile?.first_name || core?.person?.first_name || "",
    last_name: profile?.last_name || "",
    label: core?.astro?.label || "Я",
    birth_date: core?.astro?.birth_date || "",
    birth_time: core?.astro?.birth_time || "",
    time_unknown: core?.astro?.time_unknown || false,
    location_name: core?.astro?.location_name || "",
    latitude: null,
    longitude: null,
    gender: profile?.gender || core?.person?.gender || prev.gender || "unspecified",
  };
}
