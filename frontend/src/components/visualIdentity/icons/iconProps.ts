export type SymbolicIconProps = {
  size?: number;
  className?: string;
  stroke?: string;
};

/** Default stroke for zodiac / element / archetype inline marks (Foundation UI §2). */
export const STROKE = 1.5;

/** Planet seal stroke — readable on natal discs (~12–18px), asset SVGs use the same weight. */
export const PLANET_STROKE = 2.75;
