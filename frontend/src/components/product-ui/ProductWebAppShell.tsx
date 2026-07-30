"use client";

import { usePathname } from "next/navigation";
import type { ReactNode } from "react";
import { useEffect, useMemo, useRef, useState } from "react";
import {
  DsAppShell,
  DsAppSidebar,
  DsMobileTabBar,
} from "@/design-system";
import { dsAppNavItems, productWebShellChromeBundle } from "@/components/product-ui/productWebShellChrome";
import type { FlowPracticesChromeLocale } from "@/components/today/flowPracticesMainTabChrome";
import { VALUE_FIRST_PATHS } from "@/lib/guestProfileDraft";
import { resolveIsFirstDay } from "@/lib/firstTodayState";
import { getLocale } from "@/lib/i18n";
import type { CoreProfile } from "@/lib/types";
import { useAuth } from "@/lib/useAuth";
import { useProductShellDesktop } from "@/lib/useMediaQuery";
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

const GUEST_SHELL_NAME = "Гость";
const GUEST_SHELL_META = "Картина твоего дня";

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
  const { isAuthenticated } = useAuth();
  // Prefer guest chrome until auth is positively confirmed.
  // Waiting on authLoading forced SSR/crawlers (and first paint) into full
  // «Путник» + Today/Profile nav — the bug confirmed on live practice pages.
  const guestShell = !isAuthenticated;
  const isDesktop = useProductShellDesktop();
  const [navHydrated, setNavHydrated] = useState(false);
  useEffect(() => {
    setNavHydrated(true);
  }, []);
  // Before hydration keep both (CSS hides one); mark CSS-hidden nav for a11y.
  // After: unmount inactive → clean tab-order / screen readers.
  const showSidebar = !navHydrated || isDesktop;
  const showMobileTabBar = !navHydrated || !isDesktop;
  // Mobile-first until matchMedia: hide sidebar from AT on first paint.
  const sidebarAriaHidden = !navHydrated ? true : undefined;
  const mobileAriaHidden = navHydrated && isDesktop ? true : undefined;
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
  const navItems = useMemo(
    () => dsAppNavItems(resolvedLocale, guestShell ? { guestProduct: true } : undefined),
    [resolvedLocale, guestShell],
  );
  const shell = useMemo(() => productWebShellChromeBundle(resolvedLocale), [resolvedLocale]);
  const resolvedName = guestShell
    ? GUEST_SHELL_NAME
    : productWebDisplayName(coreProfile, displayName);
  const resolvedMeta = guestShell
    ? GUEST_SHELL_META
    : (profileMeta ?? productWebProfileMeta(coreProfile));
  const avatarInitial = guestShell ? "·" : productWebUserInitial(coreProfile, displayName);
  const logoHref = guestShell ? "/" : "/today";
  const footerHref = guestShell ? VALUE_FIRST_PATHS.invite : undefined;
  const footerLabel = guestShell ? "Собрать мой Today" : shell.navSettings;

  const sidebarNode =
    sidebar ??
    (showSidebar ? (
      <div aria-hidden={sidebarAriaHidden || undefined}>
        <DsAppSidebar
          displayName={resolvedName}
          profileMeta={resolvedMeta}
          avatarInitial={avatarInitial}
          navItems={navItems}
          settingsLabel={footerLabel}
          logoHref={logoHref}
          footerHref={footerHref}
        />
      </div>
    ) : null);

  return (
    <div
      ref={frameRef}
      className={l.productWebFrame}
      data-testid={testId}
      data-guest-shell={guestShell ? "true" : undefined}
    >
      <DsAppShell
        sidebar={sidebarNode}
        main={
          <div className={`${l.productWebMain} ${mainWide ? l.productWebMainProfileV2 : ""}`.trim()}>
            {main}
          </div>
        }
        rail={rail}
        fullMain={fullMain}
      />
      {showMobileTabBar ? (
        <div className={l.mobileTabBarWrap} aria-hidden={mobileAriaHidden || undefined}>
          <DsMobileTabBar
            items={navItems.map((item) => ({
              href: item.href,
              label: item.label,
              icon: <item.icon />,
            }))}
            activeHref={pathname}
          />
        </div>
      ) : null}
    </div>
  );
}
