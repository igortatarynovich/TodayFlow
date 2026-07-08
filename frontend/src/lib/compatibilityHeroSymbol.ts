import { createElement, type ReactNode } from "react";
import { ArchetypeSymbol } from "@/components/visualIdentity/ArchetypeSymbol";
import { CompatibilityOrbitSymbol } from "@/components/visualIdentity/CompatibilityOrbitSymbol";
import { ZodiacIcon } from "@/components/visualIdentity/ZodiacIcon";

const HERO_SMALL_SYMBOL = 48;

export function compatibilityHubSymbol(): ReactNode {
  return createElement(CompatibilityOrbitSymbol, { size: HERO_SMALL_SYMBOL, stroke: "currentColor" });
}

export function compatibilityScenarioSymbol(scenarioId: string): ReactNode {
  const seed = scenarioId.trim() || "unknown";
  return createElement(ArchetypeSymbol, { seed, size: HERO_SMALL_SYMBOL, stroke: "currentColor" });
}

export function compatibilityPairSymbol(fromSign?: string | null, toSign?: string | null): ReactNode {
  if (fromSign?.trim() && toSign?.trim()) {
    return createElement(
      "div",
      {
        style: {
          display: "inline-flex",
          alignItems: "center",
          gap: "0.15rem",
          width: HERO_SMALL_SYMBOL,
          height: HERO_SMALL_SYMBOL,
          justifyContent: "center",
        },
      },
      createElement(ZodiacIcon, { sign: fromSign, size: 22, stroke: "currentColor" }),
      createElement(ZodiacIcon, { sign: toSign, size: 22, stroke: "currentColor" }),
    );
  }
  return compatibilityHubSymbol();
}

/** Parses `Овен × Телец` style labels when explicit signs are unavailable. */
export function parsePairSignsFromDisplay(pairDisplay: string): { fromSign?: string; toSign?: string } {
  const parts = pairDisplay.split("×").map((part) => part.replace(/[^\p{L}\s-]/gu, "").trim());
  if (parts.length < 2) return {};
  return { fromSign: parts[0], toSign: parts[1] };
}

export function compatibilityPairSymbolFromDisplay(pairDisplay: string): ReactNode {
  const { fromSign, toSign } = parsePairSignsFromDisplay(pairDisplay);
  return compatibilityPairSymbol(fromSign, toSign);
}
