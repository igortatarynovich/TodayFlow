"use client";

import { useMemo } from "react";
import { DsMarketingNav } from "@/design-system";
import type { FlowPracticesChromeLocale } from "@/components/today/flowPracticesMainTabChrome";
import { buildAppNavLinks } from "@/lib/appNavConfig";
import { getLocale } from "@/lib/i18n";

export type ProductWebGuestNavLink = {
  href: string;
  label: string;
};

export type ProductWebGuestNavProps = {
  ctaHref: string;
  ctaLabel: string;
  locale?: FlowPracticesChromeLocale;
  logoHref?: string;
  /** Extra links (e.g. landing anchors) after guest product links. */
  extraLinks?: ProductWebGuestNavLink[];
  /** Currently active href for scroll-spy / route highlight. */
  activeHref?: string | null;
};

/** Guest marketing nav — same links as pre-auth product shell. */
export function ProductWebGuestNav({
  ctaHref,
  ctaLabel,
  locale,
  logoHref = "/",
  extraLinks,
  activeHref = null,
}: ProductWebGuestNavProps) {
  const resolvedLocale: FlowPracticesChromeLocale =
    locale ?? (getLocale() === "ru" ? "ru" : "en");
  const links = useMemo(() => {
    const base = buildAppNavLinks(resolvedLocale, "guest");
    const merged = [...base, ...(extraLinks ?? [])];
    return merged.map((link) => ({
      ...link,
      active: Boolean(activeHref && activeHref === link.href),
    }));
  }, [resolvedLocale, extraLinks, activeHref]);

  return (
    <DsMarketingNav
      logoHref={logoHref}
      links={links}
      ctaHref={ctaHref}
      ctaLabel={ctaLabel}
    />
  );
}
