"use client";

import { useEffect, useState } from "react";

/**
 * Client media query — `defaultValue` used until mount (SSR / first paint).
 * Prefer mobile-first defaults that match CSS (`display:none` until min-width).
 */
export function useMediaQuery(query: string, defaultValue = false): boolean {
  const [matches, setMatches] = useState(defaultValue);

  useEffect(() => {
    const mq = window.matchMedia(query);
    const apply = () => setMatches(mq.matches);
    apply();
    mq.addEventListener("change", apply);
    return () => mq.removeEventListener("change", apply);
  }, [query]);

  return matches;
}

/** Product shell breakpoint — keep in sync with dsLayouts / dsPatterns `64rem`. */
export const PRODUCT_SHELL_DESKTOP_MQ = "(min-width: 64rem)";

export function useProductShellDesktop(): boolean {
  return useMediaQuery(PRODUCT_SHELL_DESKTOP_MQ, false);
}
