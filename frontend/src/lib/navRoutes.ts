/** Canonical web nav paths — Header, Footer, deep links. */

export const NAV_PATHS = {
  today: "/today",
  flow: "/flow",
  flowCalendar: "/tracking/calendar",
  profile: "/profile",
  compatibility: "/compatibility",
  tarot: "/tarot",
  practices: "/practices",
  tarotJourney: "/tarot/journey",
  accountProfiles: "/account/profiles",
  accountSettings: "/account/settings",
  help: "/help",
  authLogin: "/auth?mode=login",
  journal: "/journal",
} as const;

export type NavPathKey = keyof typeof NAV_PATHS;

/** Flow alias: `/flow` re-exports calendar. */
export function isFlowRoute(pathname: string | null | undefined): boolean {
  if (!pathname) return false;
  return pathname === NAV_PATHS.flow || pathname.startsWith(NAV_PATHS.flowCalendar);
}

export function isNavRouteActive(pathname: string | null | undefined, href: string): boolean {
  if (!pathname) return false;
  if (href === NAV_PATHS.flow) return isFlowRoute(pathname);
  return pathname === href || (href !== "/" && pathname.startsWith(href));
}
