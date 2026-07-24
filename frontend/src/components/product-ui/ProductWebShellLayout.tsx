"use client";

import type { ReactNode } from "react";
import { usePathname } from "next/navigation";
import { ProductWebAppShell } from "@/components/product-ui/ProductWebAppShell";
import { useProductWebShellConfigState } from "@/components/product-ui/productWebShellConfig";
import { usesProductWebAppShell } from "@/lib/productWebShell";

export function ProductWebShellLayout({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const config = useProductWebShellConfigState();

  if (!usesProductWebAppShell(pathname)) {
    return <>{children}</>;
  }

  return (
    <ProductWebAppShell
      testId={config.testId}
      displayName={config.displayName}
      profileMeta={config.profileMeta}
      coreProfile={config.coreProfile}
      rail={config.rail}
      sidebar={config.sidebar}
      theme={config.theme}
      mood={config.mood}
      mainWide={config.mainWide}
      fullMain={config.fullMain}
      main={children}
    />
  );
}
