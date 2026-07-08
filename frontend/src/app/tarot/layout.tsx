"use client";

import { usePathname } from "next/navigation";
import type { ReactNode } from "react";
import { TarotShell } from "@/components/shell/TarotShell";

function isImmersiveTarotPath(pathname: string): boolean {
  if (pathname === "/tarot") return true;
  if (pathname.startsWith("/tarot/question")) return true;
  if (pathname.startsWith("/tarot/spread/")) return true;
  if (pathname.startsWith("/tarot/result")) return true;
  return false;
}

export default function TarotLayout({ children }: { children: ReactNode }) {
  const pathname = usePathname() ?? "/tarot";
  if (!isImmersiveTarotPath(pathname)) {
    return <>{children}</>;
  }
  return <TarotShell>{children}</TarotShell>;
}
