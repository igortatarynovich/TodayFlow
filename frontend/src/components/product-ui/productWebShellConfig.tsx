"use client";

import {
  createContext,
  useContext,
  useLayoutEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import type { CoreProfile } from "@/lib/types";

export type ProductWebShellConfig = {
  testId?: string;
  displayName?: string | null;
  profileMeta?: string | null;
  coreProfile?: CoreProfile | null;
  rail?: ReactNode;
  sidebar?: ReactNode;
  theme?: "light" | "dark";
  mainWide?: boolean;
  /** Page draws its own internal columns (profile v2): main spans both grid tracks. */
  fullMain?: boolean;
};

const EMPTY_CONFIG: ProductWebShellConfig = {};

type ProductWebShellConfigContextValue = {
  config: ProductWebShellConfig;
  setConfig: (config: ProductWebShellConfig) => void;
};

const ProductWebShellConfigContext = createContext<ProductWebShellConfigContextValue | null>(null);

export function ProductWebShellConfigProvider({ children }: { children: ReactNode }) {
  const [config, setConfig] = useState<ProductWebShellConfig>(EMPTY_CONFIG);
  const value = useMemo(() => ({ config, setConfig }), [config]);
  return (
    <ProductWebShellConfigContext.Provider value={value}>{children}</ProductWebShellConfigContext.Provider>
  );
}

export function useProductWebShellConfigState(): ProductWebShellConfig {
  const ctx = useContext(ProductWebShellConfigContext);
  return ctx?.config ?? EMPTY_CONFIG;
}

/** Per-page shell options (rail, mainWide, profile chip) — consumed by layout-level ProductWebAppShell. */
export function ProductWebShellConfigBridge({ config }: { config: ProductWebShellConfig }) {
  const ctx = useContext(ProductWebShellConfigContext);
  useLayoutEffect(() => {
    if (!ctx) return;
    ctx.setConfig(config);
    return () => ctx.setConfig(EMPTY_CONFIG);
  }, [ctx, config]);
  return null;
}
