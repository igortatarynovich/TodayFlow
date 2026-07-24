"use client";

import { usePathname } from "next/navigation";
import type { ReactNode } from "react";
import { useEffect, useMemo, useRef } from "react";
import {
  DsAppShell,
  DsAppSidebar,
  DsMobileTabBar,
} from "@/design-system";
import { dsAppNavItems, productWebShellChromeBundle } from "@/components/product-ui/productWebShellChrome";
import type { FlowPracticesChromeLocale } from "@/components/today/flowPracticesMainTabChrome";
import { resolveIsFirstDay } from "@/lib/firstTodayState";
import { getLocale } from "@/lib/i18n";
import type { CoreProfile } from "@/lib/types";
import {
  productWebDisplayName,
  productWebProfileMeta,
  productWebUserInitial,
} from "@/lib/productWebUser";
import type { ProductMood } from "@/lib/productMoodTheme";
import { useProductMoodTheme } from "@/lib/useProductDayNightTheme";
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
  /** Optional override; default from useProductMoodTheme. */
  mood?: ProductMood;
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
  theme: themeProp,
  mood: moodProp,
  mainWide = false,
  fullMain = false,
}: ProductWebAppShellProps) {
  const pathname = usePathname() ?? "/today";
  // Same isFirstDay signal as SectionAtmosphereBridge (html-level mood), read from
  // window.location instead of useSearchParams() — avoids forcing every consumer
  // route into a Suspense boundary just for the `?first=1` override.
  const isFirstDay = resolveIsFirstDay(
    pathname,
    typeof window !== "undefined" ? new URLSearchParams(window.location.search) : null,
  );
  const { mood: hookMood, theme: hookTheme } = useProductMoodTheme({ isFirstDay });
  const theme = themeProp ?? hookTheme;
  const mood = moodProp ?? hookMood;
  // data-theme/data-mood depend on clock + localStorage, which SSR can't see —
  // rendering them as JSX props bakes a value at SSR time that then mismatches the
  // client's real value. React logs a hydration warning and (for this element) never
  // repaints the attribute afterwards, so the shell gets stuck on the wrong palette.
  // Setting them imperatively post-mount (same approach as SectionAtmosphereBridge on
  // <html>) sidesteps the mismatch entirely instead of fighting it.
  const frameRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    frameRef.current?.setAttribute("data-theme", theme);
    frameRef.current?.setAttribute("data-mood", mood);
  }, [theme, mood]);
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
    <div ref={frameRef} className={l.productWebFrame} data-testid={testId}>
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
