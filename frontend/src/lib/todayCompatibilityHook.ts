import {
  buildQuickCompatibilityRoute,
  getCoreProfileCircle,
  getPrimaryProfileIdFromCore,
} from "@/lib/compatibilityRoutes";
import type { CoreProfile } from "@/lib/types";

export type TodayCompatibilityHookModel = {
  title: string;
  body: string;
  cta: string;
  href: string;
  hasSavedPerson: boolean;
};

export const TODAY_COMPATIBILITY_HOOK_COPY = {
  title: "Совместимость",
  body: "Добавь человека и посмотри, как вы взаимодействуете в любви, быту, работе и конфликтах.",
  ctaNew: "Проверить совместимость",
  ctaReturn: "Вернуться к совместимости",
  href: "/compatibility",
} as const;

/** True when user has a primary profile and at least one saved non-self person. */
export function hasSavedCompatibilityPerson(coreProfile: CoreProfile | null | undefined): boolean {
  const profiles = getCoreProfileCircle(coreProfile);
  const primaryProfileId = getPrimaryProfileIdFromCore(coreProfile);
  const route = buildQuickCompatibilityRoute({
    profiles,
    primaryProfileId,
    preferred: "any",
  });
  return route.href.startsWith("/compatibility");
}

export function buildTodayCompatibilityHook(
  coreProfile: CoreProfile | null | undefined,
): TodayCompatibilityHookModel {
  const hasSavedPerson = hasSavedCompatibilityPerson(coreProfile);
  return {
    title: TODAY_COMPATIBILITY_HOOK_COPY.title,
    body: TODAY_COMPATIBILITY_HOOK_COPY.body,
    cta: hasSavedPerson ? TODAY_COMPATIBILITY_HOOK_COPY.ctaReturn : TODAY_COMPATIBILITY_HOOK_COPY.ctaNew,
    href: TODAY_COMPATIBILITY_HOOK_COPY.href,
    hasSavedPerson,
  };
}
