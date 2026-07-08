/**
 * Unified product navigation — single source of truth.
 * Consumed by: ProductWebAppShell, landing, legacy Header/Footer, design-system catalog.
 */
import type { ComponentType, SVGProps } from "react";
import {
  IconActivity,
  IconMap,
  IconSun,
  IconUsers,
  IconWalletCards,
} from "@/design-system/icons/DsIcons";
import type { FlowPracticesChromeLocale } from "@/components/today/flowPracticesMainTabChrome";
import { t } from "@/lib/i18n";
import { NAV_PATHS } from "@/lib/navRoutes";

export type AppNavItemId = "today" | "profile" | "compatibility" | "tarot" | "practices";

export type AppNavItemDef = {
  id: AppNavItemId;
  href: string;
  icon: ComponentType<SVGProps<SVGSVGElement>>;
  labelKey: string;
  defaultRu: string;
  defaultEn: string;
};

/** Canonical nav items — order defined by APP_NAV_*_ORDER arrays. */
export const APP_NAV_ITEM_DEFS: Record<AppNavItemId, AppNavItemDef> = {
  today: {
    id: "today",
    href: NAV_PATHS.today,
    icon: IconSun,
    labelKey: "nav.today",
    defaultRu: "Сегодня",
    defaultEn: "Today",
  },
  profile: {
    id: "profile",
    href: NAV_PATHS.profile,
    icon: IconMap,
    labelKey: "nav.profile",
    defaultRu: "Моя карта",
    defaultEn: "My map",
  },
  compatibility: {
    id: "compatibility",
    href: NAV_PATHS.compatibility,
    icon: IconUsers,
    labelKey: "nav.compatibility",
    defaultRu: "Совместимость",
    defaultEn: "Compatibility",
  },
  tarot: {
    id: "tarot",
    href: NAV_PATHS.tarot,
    icon: IconWalletCards,
    labelKey: "nav.tarot",
    defaultRu: "Таро",
    defaultEn: "Tarot",
  },
  practices: {
    id: "practices",
    href: NAV_PATHS.practices,
    icon: IconActivity,
    labelKey: "nav.practices",
    defaultRu: "Практики",
    defaultEn: "Practices",
  },
};

/** Authenticated product shell — sidebar + mobile tab bar. */
export const APP_NAV_PRIMARY_ORDER: AppNavItemId[] = [
  "today",
  "profile",
  "compatibility",
  "tarot",
  "practices",
];

/** Pre-auth: guest trials on landing, auth, marketing surfaces. */
export const APP_NAV_GUEST_ORDER: AppNavItemId[] = ["tarot", "compatibility", "practices"];

export type AppNavMode = "authenticated" | "guest";

export type AppNavItem = {
  id: AppNavItemId;
  href: string;
  label: string;
  icon: ComponentType<SVGProps<SVGSVGElement>>;
};

export type AppNavLink = {
  href: string;
  label: string;
};

function resolveLocale(locale: FlowPracticesChromeLocale): "ru" | "en" {
  return locale === "ru" ? "ru" : "en";
}

export function resolveAppNavLabel(id: AppNavItemId, locale: FlowPracticesChromeLocale): string {
  const def = APP_NAV_ITEM_DEFS[id];
  const loc = resolveLocale(locale);
  return t(def.labelKey, loc === "ru" ? def.defaultRu : def.defaultEn, undefined, loc);
}

export function buildAppNavItems(
  locale: FlowPracticesChromeLocale,
  mode: AppNavMode = "authenticated",
): AppNavItem[] {
  const order = mode === "guest" ? APP_NAV_GUEST_ORDER : APP_NAV_PRIMARY_ORDER;
  return order.map((id) => {
    const def = APP_NAV_ITEM_DEFS[id];
    return {
      id,
      href: def.href,
      icon: def.icon,
      label: resolveAppNavLabel(id, locale),
    };
  });
}

/** Text-only links for DsMarketingNav (landing, auth header). */
export function buildAppNavLinks(
  locale: FlowPracticesChromeLocale,
  mode: AppNavMode = "guest",
): AppNavLink[] {
  return buildAppNavItems(locale, mode).map(({ href, label }) => ({ href, label }));
}

/** Shell chrome strings shared across product surfaces. */
export function appNavChromeBundle(locale: FlowPracticesChromeLocale) {
  const loc = resolveLocale(locale);
  const tr = (key: string, defaultRu: string, defaultEn?: string) =>
    t(key, loc === "ru" ? defaultRu : (defaultEn ?? defaultRu), undefined, loc);

  return {
    navToday: resolveAppNavLabel("today", locale),
    navProfile: resolveAppNavLabel("profile", locale),
    navCompatibility: resolveAppNavLabel("compatibility", locale),
    navTarot: resolveAppNavLabel("tarot", locale),
    navPractices: resolveAppNavLabel("practices", locale),
    navSettings: tr("nav.settings", "Настройки", "Settings"),
    tarotBackLabel: resolveAppNavLabel("tarot", locale),
    practicesBackLabel: resolveAppNavLabel("practices", locale),
  };
}
