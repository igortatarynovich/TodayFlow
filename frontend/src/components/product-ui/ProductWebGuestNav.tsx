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
  /**
   * Full nav replacement (landing: all in-page anchors).
   * When omitted, guest links point at `/#tarot` and `/#compatibility`.
   */
  links?: ProductWebGuestNavLink[];
  /** Currently active href for scroll-spy / route highlight. */
  activeHref?: string | null;
};

function hrefMatchesActive(href: string, activeHref: string | null): boolean {
  if (!activeHref) return false;
  if (href === activeHref) return true;
  const normalize = (value: string) => (value.startsWith("/#") ? value.slice(1) : value);
  return normalize(href) === normalize(activeHref);
}

/** Guest marketing nav — landing-section anchors, not direct product routes. */
export function ProductWebGuestNav({
  ctaHref,
  ctaLabel,
  locale,
  logoHref = "/",
  links: linksOverride,
  activeHref = null,
}: ProductWebGuestNavProps) {
  const resolvedLocale: FlowPracticesChromeLocale =
    locale ?? (getLocale() === "ru" ? "ru" : "en");
  const links = useMemo(() => {
    const base = linksOverride ?? buildAppNavLinks(resolvedLocale, "guest");
    return base.map((link) => ({
      ...link,
      active: hrefMatchesActive(link.href, activeHref),
    }));
  }, [resolvedLocale, linksOverride, activeHref]);

  return (
    <DsMarketingNav
      logoHref={logoHref}
      links={links}
      ctaHref={ctaHref}
      ctaLabel={ctaLabel}
    />
  );
}
