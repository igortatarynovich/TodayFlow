"use client";

import { useEffect, useMemo, useState } from "react";
import { ritualEntryImagePublicPaths } from "@/lib/todayRitualEntryIllustration";

type Props = {
  dateISO: string;
  energyScore: number;
};

/**
 * Показывает первый успешно загрузившийся файл из цепочки путей
 * `ritualEntryImagePublicPaths` (локальное время берётся после mount, чтобы не
 * расходиться с SSR).
 */
export function RitualEntryHeroIllustration({ dateISO, energyScore }: Props) {
  const [mounted, setMounted] = useState(false);
  useEffect(() => {
    setMounted(true);
  }, []);

  const candidates = useMemo(() => {
    if (!mounted) return [] as string[];
    return ritualEntryImagePublicPaths(dateISO, energyScore, new Date());
  }, [dateISO, energyScore, mounted]);

  const [idx, setIdx] = useState(0);

  useEffect(() => {
    setIdx(0);
  }, [candidates]);

  if (!mounted || candidates.length === 0) {
    return (
      <div
        aria-hidden
        style={{
          width: "100%",
          aspectRatio: "2 / 1",
          maxHeight: 360,
          minHeight: 160,
          background: "linear-gradient(180deg, rgba(255,250,245,0.95) 0%, rgba(252,232,214,0.65) 55%, rgba(238,210,188,0.35) 100%)",
        }}
      />
    );
  }

  if (idx >= candidates.length) {
    return (
      <div
        aria-hidden
        style={{
          width: "100%",
          aspectRatio: "2 / 1",
          maxHeight: 360,
          minHeight: 160,
          background: "linear-gradient(180deg, rgba(255,250,245,0.95) 0%, rgba(252,232,214,0.65) 55%, rgba(238,210,188,0.35) 100%)",
        }}
      />
    );
  }

  const src = candidates[idx];

  return (
    <div
      aria-hidden
      style={{
        position: "relative",
        width: "100%",
        aspectRatio: "2 / 1",
        maxHeight: 360,
        minHeight: 160,
        background: "rgba(255,252,248,0.5)",
      }}
    >
      {/* eslint-disable-next-line @next/next/no-img-element -- динамический перебор локальных путей из public */}
      <img
        src={src}
        alt=""
        onError={() => setIdx((i) => (i + 1 < candidates.length ? i + 1 : candidates.length))}
        style={{
          position: "absolute",
          inset: 0,
          width: "100%",
          height: "100%",
          objectFit: "cover",
          objectPosition: "center",
          display: "block",
        }}
      />
    </div>
  );
}
