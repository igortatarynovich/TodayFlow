"use client";

import { useMemo } from "react";
import { DsMarketingNav } from "@/design-system";
import type { FlowPracticesChromeLocale } from "@/components/today/flowPracticesMainTabChrome";
import { buildAppNavLinks } from "@/lib/appNavConfig";
import { getLocale } from "@/lib/i18n";

export type ProductWebGuestNavProps = {
  ctaHref: string;
  ctaLabel: string;
  locale?: FlowPracticesChromeLocale;
  logoHref?: string;
};

/** Guest marketing nav — same links as pre-auth product shell. */
export function ProductWebGuestNav({
  ctaHref,
  ctaLabel,
  locale,
  logoHref = "/",
}: ProductWebGuestNavProps) {
  const resolvedLocale: FlowPracticesChromeLocale =
    locale ?? (getLocale() === "ru" ? "ru" : "en");
  const links = useMemo(
    () => buildAppNavLinks(resolvedLocale, "guest"),
    [resolvedLocale],
  );

  return (
    <DsMarketingNav
      logoHref={logoHref}
      links={links}
      ctaHref={ctaHref}
      ctaLabel={ctaLabel}
    />
  );
}
