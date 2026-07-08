import type { ComponentType, SVGProps } from "react";
import type { FlowPracticesChromeLocale } from "@/components/today/flowPracticesMainTabChrome";
import {
  appNavChromeBundle,
  buildAppNavItems,
  type AppNavItemId,
} from "@/lib/appNavConfig";

export type ProductWebShellChrome = {
  navToday: string;
  navProfile: string;
  navCompatibility: string;
  navTarot: string;
  navPractices: string;
  navSettings: string;
  tarotBackLabel: string;
  practicesBackLabel: string;
};

export type DsAppNavItem = {
  id?: AppNavItemId;
  href: string;
  label: string;
  icon: ComponentType<SVGProps<SVGSVGElement>>;
};

export function productWebShellChromeBundle(locale: FlowPracticesChromeLocale): ProductWebShellChrome {
  return appNavChromeBundle(locale);
}

export function dsAppNavItems(
  locale: FlowPracticesChromeLocale,
  options?: { guest?: boolean },
): DsAppNavItem[] {
  const mode = options?.guest ? "guest" : "authenticated";
  return buildAppNavItems(locale, mode);
}

/** RU-default nav for design-system catalog (Figma parity). */
export function dsAppNavItemsRu(): DsAppNavItem[] {
  return dsAppNavItems("ru");
}
