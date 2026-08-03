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

/** Today domain `work` — briefcase (FOUNDATION_UI §16.6). Same stroke family as wallet/heart/activity. */
export function IconBriefcase({ className }: IconProps) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden>
      <rect x="3" y="8" width="18" height="12" rx="2" stroke="currentColor" strokeWidth="1.5" />
      <path d="M9 8V6a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v2" stroke="currentColor" strokeWidth="1.5" />
      <path d="M3 14h18" stroke="currentColor" strokeWidth="1.5" />
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

export function IconStar({ className }: IconProps) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden>
      <path
        d="M12 3.5 13.8 9H20l-5 3.6 1.9 5.9L12 15.2 7.1 18.5 9 12.6 4 9h6.2L12 3.5Z"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinejoin="round"
      />
    </svg>
  );
}

export function IconRefresh({ className }: IconProps) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden>
      <path
        d="M20 12a8 8 0 1 1-2.3-5.6"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
      />
      <path d="M20 4v5h-5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

export function IconGem({ className }: IconProps) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden>
      <path d="M12 21 4 10l3-5h10l3 5-8 11Z" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round" />
      <path d="M4 10h16M9 5l-2 5 5 11 5-11-2-5" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round" />
    </svg>
  );
}

export function IconPalette({ className }: IconProps) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden>
      <path
        d="M12 3a9 9 0 0 0-1.2 17.9c.7.1 1.2-.4 1.2-1.1 0-.6.2-1.1.6-1.4.3-.3.8-.4 1.3-.3A6.5 6.5 0 0 0 12 3Z"
        stroke="currentColor"
        strokeWidth="1.5"
      />
      <circle cx="8.5" cy="10" r="1" fill="currentColor" />
      <circle cx="12" cy="7.5" r="1" fill="currentColor" />
      <circle cx="15.5" cy="10" r="1" fill="currentColor" />
    </svg>
  );
}

export function IconHash({ className }: IconProps) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden>
      <path d="M9 5 7 19M17 5l-2 14M5 9h14M4 15h14" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
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

export const DS_NAV_ICON_MAP = {
  sun: IconSun,
  map: IconMap,
  users: IconUsers,
  "wallet-cards": IconWalletCards,
  activity: IconActivity,
} as const;

/**
 * Today domain → icon (FOUNDATION_UI §16.6). Keyed against `DomainKey`
 * (`@/lib/todayDomainVerdicts`) — the type the actual consumer
 * (`TodayVerdictStripSlot`) uses, not `TodayContractDomainId`.
 * `satisfies` checks completeness without exporting a new component type.
 */
export const TODAY_DOMAIN_ICON_MAP = {
  work: IconBriefcase,
  money: IconWalletCards,
  relationships: IconHeart,
  energy: IconActivity,
} satisfies Record<"work" | "money" | "relationships" | "energy", typeof IconHeart>;
