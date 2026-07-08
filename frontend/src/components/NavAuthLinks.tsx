"use client";

import Link from "next/link";
import { t } from "@/lib/i18n";
import { useAuth } from "@/lib/useAuth";
import { NAV_PATHS } from "@/lib/navRoutes";

/** Legacy nav slot — kept for layout parity; routes match Header primary nav. */
export function NavAuthLinks() {
  const { isAuthenticated } = useAuth();

  if (!isAuthenticated) {
    return null;
  }

  return (
    <>
      <Link href={NAV_PATHS.today} className="orbit-nav__link">
        {t("nav.header.today", "Today")}
      </Link>
      <Link href={NAV_PATHS.profile} className="orbit-nav__link">
        {t("nav.header.profile", "Profile")}
      </Link>
      <Link href={NAV_PATHS.accountSettings} className="orbit-nav__link">
        {t("nav.settings", "Settings")}
      </Link>
    </>
  );
}
