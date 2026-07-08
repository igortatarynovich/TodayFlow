"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { buildAuthHref } from "@/lib/authRedirect";
import { signOut } from "@/lib/authSession";
import { usePathname, useRouter } from "next/navigation";
import { useAuth } from "@/lib/useAuth";
import type { AccountProfile } from "@/lib/types";
import dynamic from "next/dynamic";
import { getLocale, t } from "@/lib/i18n";
import { REWARD_RINGS_COPY } from "@/lib/rewardRings";
import { isNavRouteActive, NAV_PATHS } from "@/lib/navRoutes";
import { isProductWebFullPageRoute } from "@/lib/productWebShell";
import { buildAppNavItems } from "@/lib/appNavConfig";

const LocaleSwitcher = dynamic(() => import("@/components/LocaleSwitcher"), { 
  ssr: false,
  loading: () => <span className="orbit-text-muted">...</span>
});

interface NavLinkProps {
  href: string;
  children: React.ReactNode;
  className?: string;
  prefetch?: boolean;
}

function NavLink({ href, children, className = "", prefetch = true }: NavLinkProps) {
  const pathname = usePathname();
  const isActive = isNavRouteActive(pathname, href);
  
  return (
    <Link 
      href={href} 
      prefetch={prefetch}
      className={`orbit-nav__link ${isActive ? "orbit-nav__link--active" : ""} ${className}`}
    >
      {children}
    </Link>
  );
}

export function Header() {
  const locale = getLocale();
  const chromeLocale = locale === "ru" ? "ru" : "en";
  const router = useRouter();
  const profileMenuLinks = [
    { href: NAV_PATHS.tarotJourney, label: t("nav.tarot.journey", "Tarot journey", undefined, locale) },
    { href: NAV_PATHS.accountProfiles, label: t("nav.link.peopleCircle", "Circle of people", undefined, locale) },
    { href: NAV_PATHS.journal, label: t("nav.link.journal", "Journal", undefined, locale) },
  ] as const;

  const {
    isAuthenticated,
    profile: authProfile,
    warningMessage,
    networkDegraded,
    lastValidatedAt,
    lastSnapshotSavedAt,
  } = useAuth();
  const primaryNav = buildAppNavItems(chromeLocale, isAuthenticated ? "authenticated" : "guest");

  /** Account menu — no duplicates of primary nav; Growth via Flow. */
  const [profile, setProfile] = useState<AccountProfile | null>(null);
  const [showProfileMenu, setShowProfileMenu] = useState(false);
  const [showMobileMenu, setShowMobileMenu] = useState(false);
  const profileMenuRef = useRef<HTMLDivElement>(null);
  const profileCloseTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const pathname = usePathname();
  const hideProductWebShell = isProductWebFullPageRoute(pathname);
  const handleSignOut = async () => {
    await signOut();
    router.replace("/auth?mode=login");
  };
  const statusDateFormatter = new Intl.DateTimeFormat(locale === "ru" ? "ru-RU" : "en-US", {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  });
  const validatedAtText = lastValidatedAt
    ? statusDateFormatter.format(new Date(lastValidatedAt))
    : t("nav.status.noData", "No data", undefined, locale);
  const snapshotSavedAtText = lastSnapshotSavedAt
    ? statusDateFormatter.format(new Date(lastSnapshotSavedAt))
    : t("nav.status.noData", "No data", undefined, locale);

  useEffect(() => {
    if (isAuthenticated && authProfile) {
      setProfile(authProfile);
    } else {
      setProfile(null);
    }
  }, [isAuthenticated, authProfile]);

  // Close mobile menu on route change
  useEffect(() => {
    setShowMobileMenu(false);
    setShowProfileMenu(false);
  }, [pathname]);

  useEffect(() => {
    if (!showProfileMenu) return;
    const onPointerDown = (event: MouseEvent) => {
      if (profileMenuRef.current?.contains(event.target as Node)) return;
      setShowProfileMenu(false);
    };
    document.addEventListener("mousedown", onPointerDown);
    return () => document.removeEventListener("mousedown", onPointerDown);
  }, [showProfileMenu]);

  if (hideProductWebShell) return null;

  const openProfileMenu = () => {
    if (profileCloseTimerRef.current) {
      clearTimeout(profileCloseTimerRef.current);
      profileCloseTimerRef.current = null;
    }
    setShowProfileMenu(true);
  };

  const scheduleCloseProfileMenu = () => {
    if (profileCloseTimerRef.current) clearTimeout(profileCloseTimerRef.current);
    profileCloseTimerRef.current = setTimeout(() => {
      setShowProfileMenu(false);
      profileCloseTimerRef.current = null;
    }, 180);
  };

  return (
    <header className="orbit-nav">
      {isAuthenticated && networkDegraded && warningMessage ? (
        <div
          style={{
            background: "rgba(245, 158, 11, 0.14)",
            borderBottom: "1px solid rgba(217, 119, 6, 0.26)",
            color: "#7c2d12",
            padding: "0.5rem 1rem",
            fontSize: "0.82rem",
          }}
        >
          <div style={{ maxWidth: "1200px", margin: "0 auto" }}>
            {t("nav.network.degradedDetail", "", { warning: warningMessage, validatedAt: validatedAtText, snapshotAt: snapshotSavedAtText }, locale)}
          </div>
        </div>
      ) : null}
      <div className="orbit-nav__container">
        {/* Logo */}
        <Link href="/" prefetch className="orbit-nav__logo">
          TodayFlow
        </Link>

        {/* Mobile Menu Button */}
        <button
          className="orbit-nav__mobile-toggle"
          onClick={() => setShowMobileMenu(!showMobileMenu)}
          aria-label={t("nav.toggleMenu", "Toggle menu", undefined, locale)}
        >
          <span className={showMobileMenu ? "orbit-nav__mobile-toggle--active" : ""} />
          <span className={showMobileMenu ? "orbit-nav__mobile-toggle--active" : ""} />
          <span className={showMobileMenu ? "orbit-nav__mobile-toggle--active" : ""} />
        </button>

        {/* Main Navigation */}
        <nav className={`orbit-nav__menu ${showMobileMenu ? "orbit-nav__menu--open" : ""}`}>
          {isAuthenticated ? (
            <>
              {primaryNav.map((item) => (
                <NavLink key={item.href} href={item.href}>
                  {item.label}
                </NavLink>
              ))}
            </>
          ) : (
            <>
              <NavLink href={buildAuthHref("login")}>{t("nav.login", "Log in", undefined, locale)}</NavLink>
            </>
          )}
        </nav>

        {/* Auth Actions */}
        <div className="orbit-nav__actions">
          {isAuthenticated ? (
            <div
              ref={profileMenuRef}
              className="orbit-nav__profile"
              onMouseEnter={openProfileMenu}
              onMouseLeave={scheduleCloseProfileMenu}
            >
              <button
                type="button"
                className="orbit-nav__avatar"
                aria-expanded={showProfileMenu}
                aria-haspopup="menu"
                aria-label={t("nav.profileMenu", "Account menu", undefined, locale)}
                onClick={() => setShowProfileMenu((open) => !open)}
              >
                {profile?.email ? (
                  <span>{profile.email.charAt(0).toUpperCase()}</span>
                ) : (
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                    <circle cx="12" cy="7" r="4"/>
                  </svg>
                )}
              </button>
              {showProfileMenu && (
                <div className="orbit-nav__profile-menu" role="menu">
                  {profileMenuLinks.map((item) => (
                    <Link
                      key={item.href}
                      href={item.href}
                      prefetch
                      className="orbit-nav__profile-item"
                      role="menuitem"
                      onClick={() => setShowProfileMenu(false)}
                    >
                      {item.label}
                    </Link>
                  ))}
                  <div className="orbit-nav__profile-divider" />
                  <Link href={NAV_PATHS.help} prefetch={false} className="orbit-nav__profile-item" role="menuitem" onClick={() => setShowProfileMenu(false)}>
                    {REWARD_RINGS_COPY.helpNavLabel}
                  </Link>
                  <Link href={NAV_PATHS.accountSettings} prefetch={false} className="orbit-nav__profile-item" role="menuitem" onClick={() => setShowProfileMenu(false)}>
                    {t("nav.settings", "Settings", undefined, locale)}
                  </Link>
                  <div className="orbit-nav__profile-divider" />
                  <button
                    type="button"
                    className="orbit-nav__profile-item"
                    role="menuitem"
                    onClick={() => {
                      setShowProfileMenu(false);
                      void handleSignOut();
                    }}
                  >
                    {t("nav.logout", "Log out", undefined, locale)}
                  </button>
                </div>
              )}
            </div>
          ) : (
            <Link href={buildAuthHref("login")} prefetch={false} className="orbit-button orbit-button-primary orbit-button-xs">
              {t("nav.login", "Log in", undefined, locale)}
            </Link>
          )}
          <LocaleSwitcher />
        </div>
      </div>
      {showMobileMenu ? (
        <>
          <div className="orbit-nav__sheet-backdrop" onClick={() => setShowMobileMenu(false)} />
          <div className="orbit-nav__sheet">
            <div className="orbit-nav__sheet-header">
              <div>
                <p className="orbit-body-xs orbit-text-muted" style={{ margin: 0 }}>
                  {t("nav.sheet.title", "Navigation", undefined, locale)}
                </p>
                <p className="orbit-body-sm" style={{ margin: "0.25rem 0 0", fontWeight: 700 }}>
                  {t("nav.sheet.subtitle", "Where to go next", undefined, locale)}
                </p>
              </div>
              <button type="button" className="orbit-nav__sheet-close" onClick={() => setShowMobileMenu(false)}>
                ✕
              </button>
            </div>

            <div className="orbit-nav__sheet-group">
              <p className="orbit-nav__sheet-label">{t("nav.sheet.main", "Main sections", undefined, locale)}</p>
              {primaryNav.map((item) => (
                <NavLink key={item.href} href={item.href} className="orbit-nav__sheet-link">
                  {item.label}
                </NavLink>
              ))}
            </div>

            {isAuthenticated ? (
              <>
                <div className="orbit-nav__sheet-group">
                  <p className="orbit-nav__sheet-label">{t("nav.sheet.quick", "More", undefined, locale)}</p>
                  {profileMenuLinks.map((item) => (
                    <NavLink key={item.href} href={item.href} className="orbit-nav__sheet-link">
                      {item.label}
                    </NavLink>
                  ))}
                </div>

                <div className="orbit-nav__sheet-group">
                  <p className="orbit-nav__sheet-label">{t("nav.sheet.help", "Help & account", undefined, locale)}</p>
                  <NavLink href={NAV_PATHS.help} className="orbit-nav__sheet-link">
                    {REWARD_RINGS_COPY.helpNavLabel}
                  </NavLink>
                  <NavLink href={NAV_PATHS.accountSettings} className="orbit-nav__sheet-link">
                    {t("nav.sheet.accountSettings", "Account settings", undefined, locale)}
                  </NavLink>
                  <button
                    className="orbit-nav__sheet-link orbit-nav__sheet-link--button"
                    onClick={() => {
                      void handleSignOut();
                    }}
                  >
                    {t("nav.logout", "Log out", undefined, locale)}
                  </button>
                </div>
              </>
            ) : (
              <div className="orbit-nav__sheet-group">
                <p className="orbit-nav__sheet-label">{t("nav.sheet.signIn", "Sign in", undefined, locale)}</p>
                <NavLink href={buildAuthHref("login")} className="orbit-nav__sheet-link">
                  {t("nav.login", "Log in", undefined, locale)}
                </NavLink>
              </div>
            )}
          </div>
        </>
      ) : null}
    </header>
  );
}
