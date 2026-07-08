type IconProps = { className?: string };

export function IconCompass({ className }: IconProps) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden>
      <circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="1.5" />
      <path d="M12 3v4M12 17v4M3 12h4M17 12h4" stroke="currentColor" strokeWidth="1.5" />
      <path d="m14.5 9.5-5 2 2 5 5-2-2-5Z" stroke="currentColor" strokeWidth="1.5" />
    </svg>
  );
}

export function IconCircleX({ className }: IconProps) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden>
      <circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="1.5" />
      <path d="m9 9 6 6M15 9l-6 6" stroke="currentColor" strokeWidth="1.5" />
    </svg>
  );
}

export function IconWaves({ className }: IconProps) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden>
      <path d="M3 14c2-2 4-2 6 0s4 2 6 0 4-2 6 0" stroke="currentColor" strokeWidth="1.5" />
      <path d="M3 10c2-2 4-2 6 0s4 2 6 0 4-2 6 0" stroke="currentColor" strokeWidth="1.5" />
    </svg>
  );
}

export function IconSun({ className }: IconProps) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden>
      <circle cx="12" cy="12" r="4" stroke="currentColor" strokeWidth="1.5" />
      <path d="M12 2v2M12 20v2M2 12h2M20 12h2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" stroke="currentColor" strokeWidth="1.5" />
    </svg>
  );
}

export function IconMoon({ className }: IconProps) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden>
      <path d="M20 14.5A8.5 8.5 0 0 1 9.5 4 10 10 0 1 0 20 14.5Z" stroke="currentColor" strokeWidth="1.5" />
    </svg>
  );
}

export function IconRoute({ className }: IconProps) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden>
      <path d="M4 19c3-6 13-6 16-12" stroke="currentColor" strokeWidth="1.5" />
      <circle cx="4" cy="19" r="2" fill="currentColor" />
      <circle cx="20" cy="7" r="2" fill="currentColor" />
    </svg>
  );
}

export function IconSparkles({ className }: IconProps) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden>
      <path d="M12 3l1.2 4.8L18 9l-4.8 1.2L12 15l-1.2-4.8L6 9l4.8-1.2L12 3Z" stroke="currentColor" strokeWidth="1.5" />
    </svg>
  );
}

export function IconMountain({ className }: IconProps) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden>
      <path d="m4 18 8-12 8 12H4Z" stroke="currentColor" strokeWidth="1.5" />
    </svg>
  );
}

export function IconTarot({ className }: IconProps) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden>
      <rect x="5" y="3" width="14" height="18" rx="2" stroke="currentColor" strokeWidth="1.5" />
      <path d="M9 8h6M9 12h6" stroke="currentColor" strokeWidth="1.5" />
    </svg>
  );
}

export function IconCalendar({ className }: IconProps) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden>
      <rect x="4" y="5" width="16" height="16" rx="2" stroke="currentColor" strokeWidth="1.5" />
      <path d="M8 3v4M16 3v4M4 10h16" stroke="currentColor" strokeWidth="1.5" />
    </svg>
  );
}

export function IconMapPin({ className }: IconProps) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden>
      <path d="M12 21s7-4.5 7-11a7 7 0 1 0-14 0c0 6.5 7 11 7 11Z" stroke="currentColor" strokeWidth="1.5" />
      <circle cx="12" cy="10" r="2.5" stroke="currentColor" strokeWidth="1.5" />
    </svg>
  );
}

/** Figma nav canon: folded map (Моя карта). */
export function IconMap({ className }: IconProps) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden>
      <path d="M9 6 3 4v14l6 2 6-2 6 2V4l-6 2-6-2Z" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round" />
      <path d="M9 6v14M15 4v14" stroke="currentColor" strokeWidth="1.5" />
    </svg>
  );
}

/** Figma nav canon: two profiles (Совместимость). */
export function IconUsers({ className }: IconProps) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden>
      <circle cx="9" cy="8" r="3" stroke="currentColor" strokeWidth="1.5" />
      <path d="M3 20c0-3.3 2.7-5 6-5s6 1.7 6 5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
      <circle cx="17" cy="9" r="2.5" stroke="currentColor" strokeWidth="1.5" />
      <path d="M15 20c.3-2.2 1.8-3.5 4-3.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
    </svg>
  );
}

/** Figma nav canon: wallet-cards (Таро). */
export function IconWalletCards({ className }: IconProps) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden>
      <rect x="3" y="5" width="14" height="16" rx="2" stroke="currentColor" strokeWidth="1.5" />
      <path d="M7 5V3a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2h-2" stroke="currentColor" strokeWidth="1.5" />
      <path d="M7 11h6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
    </svg>
  );
}

/** Figma nav canon: activity pulse (Практики). */
export function IconActivity({ className }: IconProps) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden>
      <path
        d="M4 12h3l2-5 4 10 2-5h5"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

export function IconHeart({ className }: IconProps) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden>
      <path d="M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.5A4 4 0 0 1 19 10c0 5.6-7 10-7 10Z" stroke="currentColor" strokeWidth="1.5" />
    </svg>
  );
}

export function IconEye({ className }: IconProps) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden>
      <path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7-10-7-10-7Z" stroke="currentColor" strokeWidth="1.5" />
      <circle cx="12" cy="12" r="2.5" stroke="currentColor" strokeWidth="1.5" />
    </svg>
  );
}

export function IconSettings({ className }: IconProps) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden>
      <circle cx="12" cy="12" r="3" stroke="currentColor" strokeWidth="1.5" />
      <path d="M12 2v2M12 20v2M4.2 4.2l1.4 1.4M18.4 18.4l1.4 1.4M2 12h2M20 12h2M4.2 19.8l1.4-1.4M18.4 5.6l1.4-1.4" stroke="currentColor" strokeWidth="1.5" />
    </svg>
  );
}

export function IconOrbitalGlyph({ className }: IconProps) {
  return (
    <svg className={className} viewBox="0 0 28 28" fill="none" aria-hidden>
      <circle cx="14" cy="14" r="12" stroke="currentColor" strokeWidth="1.2" />
      <circle cx="14" cy="14" r="4" fill="currentColor" />
      <circle cx="22" cy="10" r="2" fill="currentColor" />
    </svg>
  );
}

const FEATURE_ICONS = {
  compass: IconCompass,
  circle: IconCircleX,
  waves: IconWaves,
} as const;

export function DsFeatureIcon({ name, className }: { name: keyof typeof FEATURE_ICONS; className?: string }) {
  const Cmp = FEATURE_ICONS[name];
  return <Cmp className={className} />;
}

/**
 * @deprecated Use `dsAppNavItemsRu()` from `@/components/product-ui/productWebShellChrome`
 * or `buildAppNavItems()` from `@/lib/appNavConfig`.
 */
export const DS_APP_NAV = [
  { href: "/today", label: "Сегодня", icon: IconSun },
  { href: "/profile", label: "Моя карта", icon: IconMap },
  { href: "/compatibility", label: "Совместимость", icon: IconUsers },
  { href: "/tarot", label: "Таро", icon: IconWalletCards },
  { href: "/practices", label: "Практики", icon: IconActivity },
] as const;

export const DS_NAV_ICON_MAP = {
  sun: IconSun,
  map: IconMap,
  users: IconUsers,
  "wallet-cards": IconWalletCards,
  activity: IconActivity,
} as const;
