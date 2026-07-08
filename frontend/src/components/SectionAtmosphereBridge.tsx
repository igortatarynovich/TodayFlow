"use client";

import { useEffect } from "react";
import { usePathname } from "next/navigation";
import { resolveSectionAtmosphere, SECTION_THEME_COLORS } from "@/lib/sectionAtmosphere";

/** Syncs `data-atmosphere` + theme-color with the active route. */
export function SectionAtmosphereBridge() {
  const pathname = usePathname();
  const atmosphere = resolveSectionAtmosphere(pathname);

  useEffect(() => {
    document.documentElement.setAttribute("data-atmosphere", atmosphere);
    const color = SECTION_THEME_COLORS[atmosphere];
    const meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.setAttribute("content", color);
  }, [atmosphere]);

  return null;
}
