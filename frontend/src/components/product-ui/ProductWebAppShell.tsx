"use client";

import { usePathname } from "next/navigation";
import type { ReactNode } from "react";
import { useMemo } from "react";
import {
  DsAppShell,
  DsAppSidebar,
  DsMobileTabBar,
} from "@/design-system";
import { dsAppNavItems, productWebShellChromeBundle } from "@/components/product-ui/productWebShellChrome";
import type { FlowPracticesChromeLocale } from "@/components/today/flowPracticesMainTabChrome";
import { getLocale } from "@/lib/i18n";
import type { CoreProfile } from "@/lib/types";
import {
  productWebDisplayName,
  productWebProfileMeta,
  productWebUserInitial,
} from "@/lib/productWebUser";
import l from "@/design-system/layouts/dsLayouts.module.css";

export type ProductWebAppShellProps = {
  testId?: string;
  displayName?: string | null;
  profileMeta?: string | null;
  coreProfile?: CoreProfile | null;
  locale?: FlowPracticesChromeLocale;
  main: ReactNode;
  rail?: ReactNode;
  sidebar?: ReactNode;
  theme?: "light" | "dark";
  /** Wider horizontal padding for profile v2 canvas (Figma px-24). */
  mainWide?: boolean;
  /** Page draws its own internal columns (profile v2): main spans both grid tracks. */
  fullMain?: boolean;
};

export function ProductWebAppShell({
  testId,
  displayName,
  profileMeta,
  coreProfile,
  locale,
  main,
  rail,
  sidebar,
  theme = "light",
  mainWide = false,
  fullMain = false,
}: ProductWebAppShellProps) {
  const pathname = usePathname() ?? "/today";
  const resolvedLocale: FlowPracticesChromeLocale =
    locale ?? (getLocale() === "ru" ? "ru" : "en");
  // In-app sidebar always shows the full nav (Today / My map / Compatibility / Tarot /
  // Practices) per Figma. Guest-reduced nav is only for landing/marketing surfaces;
  // guests hitting Today/Profile see the login/onboarding state on those screens.
  const navItems = useMemo(
    () => dsAppNavItems(resolvedLocale),
    [resolvedLocale],
  );
  const shell = useMemo(() => productWebShellChromeBundle(resolvedLocale), [resolvedLocale]);
  const resolvedName = productWebDisplayName(coreProfile, displayName);
  const resolvedMeta = profileMeta ?? productWebProfileMeta(coreProfile);

  return (
    <div className={l.productWebFrame} data-testid={testId} data-theme={theme}>
      <DsAppShell
        sidebar={
          sidebar ?? (
            <DsAppSidebar
              displayName={resolvedName}
              profileMeta={resolvedMeta}
              avatarInitial={productWebUserInitial(coreProfile, displayName)}
              navItems={navItems}
              settingsLabel={shell.navSettings}
            />
          )
        }
        main={
          <div className={`${l.productWebMain} ${mainWide ? l.productWebMainProfileV2 : ""}`.trim()}>
            {main}
          </div>
        }
        rail={rail}
        fullMain={fullMain}
      />
      <div className={l.mobileTabBarWrap}>
        <DsMobileTabBar
          items={navItems.map((item) => ({
            href: item.href,
            label: item.label,
            icon: <item.icon />,
          }))}
          activeHref={pathname}
        />
      </div>
    </div>
  );
}
