"use client";

import { useEffect } from "react";
import { usePathname } from "next/navigation";
import { isProductWebFullPageRoute } from "@/lib/productWebShell";

export function ProductWebShellBridge() {
  const pathname = usePathname();

  useEffect(() => {
    const enabled = isProductWebFullPageRoute(pathname);
    if (enabled) {
      document.documentElement.setAttribute("data-product-web-shell", "true");
    } else {
      document.documentElement.removeAttribute("data-product-web-shell");
    }
    return () => document.documentElement.removeAttribute("data-product-web-shell");
  }, [pathname]);

  return null;
}
