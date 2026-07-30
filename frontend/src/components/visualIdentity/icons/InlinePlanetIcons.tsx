import type { ReactElement, ReactNode } from "react";
import type { SymbolicIconProps } from "./iconProps";
import { PLANET_STROKE } from "./iconProps";
import type { PlanetSlug } from "@/lib/visualIdentity/registry";

/**
 * Inline planet seals — parity with `public/images/icons/planets/*.svg` (asset mode).
 * Optical mass tuned for ~12–18px natal discs (not sparse unicode decoration).
 */
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
      <g stroke={stroke} strokeWidth={PLANET_STROKE} strokeLinecap="round" strokeLinejoin="round">
        {children}
      </g>
    </svg>
  );
}

function SunIcon(props: SymbolicIconProps) {
  const stroke = props.stroke ?? "currentColor";
  return (
    <IconSvg {...props}>
      <circle cx="28" cy="28" r="13.5" />
      <circle cx="28" cy="28" r="5" fill={stroke} stroke="none" />
    </IconSvg>
  );
}

function MoonIcon(props: SymbolicIconProps) {
  const stroke = props.stroke ?? "currentColor";
  return (
    <svg
      width={props.size ?? 28}
      height={props.size ?? 28}
      viewBox="0 0 56 56"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={props.className}
      aria-hidden
    >
      <path d="M35.5 15.5a14 14 0 1 0 0 25 11.5 11.5 0 1 1 0-25z" fill={stroke} />
    </svg>
  );
}

function MercuryIcon(props: SymbolicIconProps) {
  return (
    <IconSvg {...props}>
      <circle cx="28" cy="25" r="10.5" />
      <path d="M20.5 14.5v7.5M35.5 14.5v7.5" />
      <path d="M28 35.5v12M22.5 43h11" />
    </IconSvg>
  );
}

function VenusIcon(props: SymbolicIconProps) {
  return (
    <IconSvg {...props}>
      <circle cx="28" cy="22.5" r="11" />
      <path d="M28 33.5v14M21.5 42.5h13" />
    </IconSvg>
  );
}

function MarsIcon(props: SymbolicIconProps) {
  return (
    <IconSvg {...props}>
      <circle cx="23.5" cy="32.5" r="11" />
      <path d="M32 24 43.5 12.5" />
      <path d="M35.5 12.5h8v8" />
    </IconSvg>
  );
}

function JupiterIcon(props: SymbolicIconProps) {
  return (
    <IconSvg {...props}>
      <path d="M18 20c0-7 10-9 14-4v26" />
      <path d="M17.5 31h18" />
    </IconSvg>
  );
}

function SaturnIcon(props: SymbolicIconProps) {
  return (
    <IconSvg {...props}>
      <path d="M28 12v18" />
      <path d="M20 20h16" />
      <path d="M18 30c2 12 18 12 20 0" />
      <path d="M22.5 42.5v6M33.5 42.5v6" />
    </IconSvg>
  );
}

function UranusIcon(props: SymbolicIconProps) {
  const stroke = props.stroke ?? "currentColor";
  return (
    <IconSvg {...props}>
      <path d="M20.5 42V20M35.5 42V20" />
      <path d="M16.5 31h23" />
      <circle cx="28" cy="14.5" r="5.5" />
      <circle cx="28" cy="14.5" r="2.25" fill={stroke} stroke="none" />
    </IconSvg>
  );
}

function NeptuneIcon(props: SymbolicIconProps) {
  return (
    <IconSvg {...props}>
      <path d="M28 46V24" />
      <path d="M18 22v10l10-10 10 10V22" />
      <path d="M21.5 40.5h13" />
    </IconSvg>
  );
}

function PlutoIcon(props: SymbolicIconProps) {
  const stroke = props.stroke ?? "currentColor";
  return (
    <IconSvg {...props}>
      <circle cx="23.5" cy="26" r="10.5" />
      <path d="M34 26h12" />
      <path d="M40 19.5v13" />
      <circle cx="23.5" cy="26" r="3.25" fill={stroke} stroke="none" />
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
