"use client";

import { PlanetIcon, type PlanetIconProps } from "@/components/visualIdentity/PlanetIcon";

/** DS-only planet sphere entrypoint (Form Kit visual contract). */
export function DsPlanet(props: PlanetIconProps) {
  return <PlanetIcon {...props} fit={props.fit ?? "cover"} />;
}
