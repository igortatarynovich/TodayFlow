"use client";

import { CelestialMoon, type CelestialMoonProps } from "@/components/celestial/CelestialMoon";

/** DS visual entrypoint for lunar sphere (Form Kit §15.8 import contract). */
export function DsCelestialMoon(props: CelestialMoonProps) {
  return <CelestialMoon {...props} />;
}
