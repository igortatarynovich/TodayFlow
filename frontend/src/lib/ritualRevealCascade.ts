"use client";

import { useEffect, useState } from "react";

/** Handoff: value immediate → «Значение» +700ms → context +1500ms. */
export const RITUAL_REVEAL_MEANING_MS = 700;
export const RITUAL_REVEAL_CONTEXT_MS = 1500;

export function useRitualRevealStages(active: boolean, reduceMotion: boolean) {
  const [showMeaning, setShowMeaning] = useState(false);
  const [showContext, setShowContext] = useState(false);

  useEffect(() => {
    if (!active) {
      setShowMeaning(false);
      setShowContext(false);
      return;
    }
    if (reduceMotion) {
      setShowMeaning(true);
      setShowContext(true);
      return;
    }
    setShowMeaning(false);
    setShowContext(false);
    const t1 = window.setTimeout(() => setShowMeaning(true), RITUAL_REVEAL_MEANING_MS);
    const t2 = window.setTimeout(() => setShowContext(true), RITUAL_REVEAL_CONTEXT_MS);
    return () => {
      window.clearTimeout(t1);
      window.clearTimeout(t2);
    };
  }, [active, reduceMotion]);

  return { showMeaning, showContext };
}

/** When to show the continue CTA given optional cascade layers. */
export function ritualRevealCtaReady(input: {
  showMeaning: boolean;
  showContext: boolean;
  hasMeaning: boolean;
  hasContext: boolean;
}): boolean {
  if (input.hasContext) return input.showContext;
  if (input.hasMeaning) return input.showMeaning;
  return true;
}
