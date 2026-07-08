import type { ReactElement, ReactNode } from "react";
import type { SymbolicIconProps } from "./iconProps";
import { STROKE } from "./iconProps";
import type { PlanetSlug } from "@/lib/visualIdentity/registry";

function IconSvg({ size = 28, className, stroke = "currentColor", children }: SymbolicIconProps & { children: ReactNode }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 56 56"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
      aria-hidden
    >
      <g stroke={stroke} strokeWidth={STROKE} strokeLinecap="round" strokeLinejoin="round">
        {children}
      </g>
    </svg>
  );
}

function SunIcon(props: SymbolicIconProps) {
  return (
    <IconSvg {...props}>
      <circle cx="28" cy="28" r="12" />
      <circle cx="28" cy="28" r="4" />
    </IconSvg>
  );
}

function MoonIcon(props: SymbolicIconProps) {
  return (
    <IconSvg {...props}>
      <path d="M34 18a12 12 0 1 0 0 20a10 10 0 1 1 0-20" />
    </IconSvg>
  );
}

function MercuryIcon(props: SymbolicIconProps) {
  return (
    <IconSvg {...props}>
      <circle cx="28" cy="26" r="10" />
      <path d="M22 16v6M34 16v6" />
      <path d="M28 36v8M24 42h8" />
    </IconSvg>
  );
}

function VenusIcon(props: SymbolicIconProps) {
  return (
    <IconSvg {...props}>
      <circle cx="28" cy="24" r="10" />
      <path d="M28 34v10M24 42h8" />
    </IconSvg>
  );
}

function MarsIcon(props: SymbolicIconProps) {
  return (
    <IconSvg {...props}>
      <circle cx="24" cy="32" r="10" />
      <path d="M32 24 42 14M38 14h4v4" />
    </IconSvg>
  );
}

function JupiterIcon(props: SymbolicIconProps) {
  return (
    <IconSvg {...props}>
      <path d="M34 16v16M22 28h12" />
      <path d="M22 20v16" />
    </IconSvg>
  );
}

function SaturnIcon(props: SymbolicIconProps) {
  return (
    <IconSvg {...props}>
      <path d="M22 40V20M34 40V20" />
      <path d="M18 28h20" />
      <path d="M24 40v6M32 40v6" />
    </IconSvg>
  );
}

function UranusIcon(props: SymbolicIconProps) {
  return (
    <IconSvg {...props}>
      <path d="M22 38V18M34 38V18" />
      <path d="M18 28h20" />
      <circle cx="28" cy="14" r="5" />
    </IconSvg>
  );
}

function NeptuneIcon(props: SymbolicIconProps) {
  return (
    <IconSvg {...props}>
      <path d="M28 42V22" />
      <path d="M20 22v8l8-8 8 8v-8" />
    </IconSvg>
  );
}

function PlutoIcon(props: SymbolicIconProps) {
  return (
    <IconSvg {...props}>
      <circle cx="24" cy="26" r="9" />
      <path d="M33 26h8" />
      <path d="M37 22v8" />
    </IconSvg>
  );
}

const ICONS: Record<PlanetSlug, (props: SymbolicIconProps) => ReactElement> = {
  sun: SunIcon,
  moon: MoonIcon,
  mercury: MercuryIcon,
  venus: VenusIcon,
  mars: MarsIcon,
  jupiter: JupiterIcon,
  saturn: SaturnIcon,
  uranus: UranusIcon,
  neptune: NeptuneIcon,
  pluto: PlutoIcon,
};

export function InlinePlanetIcon({ slug, ...props }: SymbolicIconProps & { slug: PlanetSlug }) {
  const Icon = ICONS[slug];
  return Icon(props);
}
