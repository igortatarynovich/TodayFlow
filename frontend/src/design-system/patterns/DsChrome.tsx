import Link from "next/link";
import { usePathname } from "next/navigation";
import type { ComponentType, ReactNode, SVGProps } from "react";
import { DsButton } from "@/design-system/primitives/DsButton";
import { IconOrbitalGlyph, IconSettings } from "@/design-system/icons/DsIcons";
import { buildAppNavItems } from "@/lib/appNavConfig";
import { isNavRouteActive } from "@/lib/navRoutes";
import { NAV_PATHS } from "@/lib/navRoutes";
import { DsPill } from "@/design-system/primitives/DsTypography";
import p from "@/design-system/patterns/dsPatterns.module.css";

type NavItem = { href: string; label: string; icon?: ComponentType<SVGProps<SVGSVGElement>> };

export function DsMarketingNav({
  logoHref = "/",
  links,
  ctaHref,
  ctaLabel,
}: {
  logoHref?: string;
  links: NavItem[];
  ctaHref: string;
  ctaLabel: string;
}) {
  return (
    <header className={p.marketingNav}>
      <Link href={logoHref} className={p.logo}>
        TodayFlow
      </Link>
      <nav className={p.navLinks} aria-label="Основная навигация">
        {links.map((item) => (
          <Link key={item.href} href={item.href} className={p.navLink}>
            {item.label}
          </Link>
        ))}
      </nav>
      <DsButton href={ctaHref} size="sm">
        {ctaLabel}
      </DsButton>
    </header>
  );
}

export function DsAppSidebar({
  displayName,
  profileMeta,
  avatarInitial,
  navItems,
  settingsLabel = "Настройки",
}: {
  displayName: string;
  profileMeta?: string | null;
  avatarInitial: string;
  navItems?: NavItem[];
  settingsLabel?: string;
}) {
  const pathname = usePathname();
  const items = navItems ?? buildAppNavItems("ru", "authenticated");

  return (
    <aside className={p.sidebar} aria-label="Навигация">
      <div className={p.sidebarTop}>
        <Link href={NAV_PATHS.today} className={p.logoGroup}>
          <IconOrbitalGlyph className={p.logoGlyph} />
          <span className={p.logoText}>TodayFlow</span>
        </Link>

        <div className={p.profileBlock}>
          <div className={p.avatarRing}>
            <div className={p.avatar} aria-hidden>
              {avatarInitial}
            </div>
          </div>
          <div>
            <p className={p.profileName}>{displayName}</p>
            {profileMeta ? <p className={p.profileMeta}>{profileMeta}</p> : null}
          </div>
        </div>

        <nav className={p.navList}>
          {items.map((item) => {
            const active = isNavRouteActive(pathname, item.href);
            const Icon = item.icon;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`${p.navItem} ${active ? p.navItemActive : ""}`}
              >
                {active ? <span className={p.navActiveBar} aria-hidden /> : null}
                <span className={p.navContent}>
                  {Icon ? <Icon className={p.navIcon} /> : null}
                  <span className={p.navLabel}>{item.label}</span>
                </span>
              </Link>
            );
          })}
        </nav>
      </div>

      <div className={p.sidebarFooter}>
        <Link href={NAV_PATHS.accountSettings} className={p.settingsLink}>
          <IconSettings className={p.navIcon} />
          {settingsLabel}
        </Link>
        <div className={p.themeToggle} aria-hidden />
      </div>
    </aside>
  );
}

export function DsPageHeader({
  title,
  subtitle,
  dateLabel,
  dateIcon,
}: {
  title: string;
  subtitle?: string;
  dateLabel: string;
  dateIcon?: ReactNode;
}) {
  return (
    <div className={p.pageHeader}>
      <div>
        <h1 className={p.themeTitle} style={{ color: "var(--tf-ink)", fontSize: "clamp(1.75rem, 3vw, 2.25rem)" }}>
          {title}
        </h1>
        {subtitle ? <p className={p.profileMeta}>{subtitle}</p> : null}
      </div>
      <DsPill>{dateIcon}{dateLabel}</DsPill>
    </div>
  );
}
