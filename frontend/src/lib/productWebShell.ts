/** Routes that use the full-page Product UI shell (no global Header/Footer). */

const PRODUCT_WEB_CHROME_PREFIXES = [
  "/today",
  "/profile",
  "/compatibility",
  "/tarot",
  "/practices",
  "/onboarding",
  "/auth",
  "/account",
  "/tracking",
  "/weekly",
  "/journal",
  "/affirmations",
  "/asceticisms",
  "/cycle",
  "/habits",
  "/flow",
  "/dashboard",
  "/discover",
  "/maps",
  "/lunar",
  "/numerology",
  "/horoscope",
  "/horoscopes",
  "/reports",
  "/challenges",
  "/natal-chart",
  "/birth-chart",
  "/calendar",
  "/growth",
  "/morning-ritual",
  "/forecast",
  "/forecasts",
  "/questions",
  "/help",
  "/library",
  "/app",
  "/signup",
  "/login",
] as const;

const PRODUCT_WEB_CHROME_EXACT = ["/"] as const;

/** Marketing / legal — keep legacy Header/Footer, no product sidebar.
 *  `/pricing` is draft/wave-2 (placeholder tariffs) — not a launch product decision;
 *  see docs/TODAYFLOW_PRODUCT_CANON_UNIFIED.md §7. Keep route for deep links/checkout redirects. */
const LEGACY_MARKETING_PREFIXES = [
  "/terms",
  "/privacy",
  "/pricing",
  "/catalog",
  "/checkout",
  "/billing",
  "/design-system",
  "/admin",
  "/dev",
  "/demo",
  "/generate",
] as const;

function matchesPrefix(pathname: string, prefixes: readonly string[]): boolean {
  return prefixes.some((prefix) => pathname === prefix || pathname.startsWith(`${prefix}/`));
}

export function isLegacyMarketingRoute(pathname: string | null | undefined): boolean {
  if (!pathname) return false;
  return matchesPrefix(pathname, LEGACY_MARKETING_PREFIXES);
}

export function isProductWebFullPageRoute(pathname: string | null | undefined): boolean {
  if (!pathname) return false;
  if (isLegacyMarketingRoute(pathname)) return false;
  if ((PRODUCT_WEB_CHROME_EXACT as readonly string[]).includes(pathname)) return true;
  return matchesPrefix(pathname, PRODUCT_WEB_CHROME_PREFIXES);
}

/** Sidebar + mobile tab bar — same nav on every in-app screen (not landing/auth/onboarding). */
export function usesProductWebAppShell(pathname: string | null | undefined): boolean {
  if (!pathname) return false;
  if (!isProductWebFullPageRoute(pathname)) return false;
  if (pathname === "/") return false;
  if (pathname.startsWith("/auth")) return false;
  if (pathname.startsWith("/onboarding")) return false;
  return true;
}
