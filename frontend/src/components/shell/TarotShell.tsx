"use client";

import type { ReactNode } from "react";
import { useMemo } from "react";
import { usePathname } from "next/navigation";
import { ProductWebShellConfigBridge, type ProductWebShellConfig } from "@/components/product-ui/productWebShellConfig";
import { TarotRail } from "@/components/shell/TarotRail";
import { tarotShellStepFromPath } from "@/components/shell/tarotShellStepper";
import s from "@/components/shell/tarotShell.module.css";

export type TarotShellProps = {
  children: ReactNode;
};

export function TarotShell({ children }: TarotShellProps) {
  const pathname = usePathname() ?? "/tarot";
  const activeStep = tarotShellStepFromPath(pathname);

  const shellConfig = useMemo((): ProductWebShellConfig => {
    const rail = activeStep < 0 ? null : <TarotRail activeStep={activeStep} />;
    return {
      testId: "tarot-immersive-shell",
      theme: "dark",
      mainWide: true,
      fullMain: false,
      rail,
    };
  }, [activeStep]);

  return (
    <>
      <ProductWebShellConfigBridge config={shellConfig} />
      <div className={s.shellMain}>{children}</div>
    </>
  );
}
