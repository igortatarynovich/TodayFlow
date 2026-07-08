"use client";

import styles from "@/components/landing/landing.module.css";

/** Decorative abstract life map — orbits, points, soft lines. */
export function PersonalMapIllustration() {
  return (
    <div className={styles.mapIllustration} aria-hidden data-testid="landing-map-illustration">
      <svg viewBox="0 0 520 560" className={styles.mapSvg} role="presentation">
        <defs>
          <radialGradient id="landingMapGlow" cx="48%" cy="42%" r="62%">
            <stop offset="0%" stopColor="#c9a873" stopOpacity="0.28" />
            <stop offset="45%" stopColor="#e8dcc8" stopOpacity="0.12" />
            <stop offset="100%" stopColor="#f3efe8" stopOpacity="0" />
          </radialGradient>
          <linearGradient id="landingMapLine" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#c9a873" stopOpacity="0.45" />
            <stop offset="100%" stopColor="#7ba3c9" stopOpacity="0.32" />
          </linearGradient>
          <filter id="landingSoftGlow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="2" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        <rect width="520" height="560" fill="url(#landingMapGlow)" rx="28" />

        <circle cx="260" cy="268" r="210" fill="none" stroke="url(#landingMapLine)" strokeWidth="1" opacity="0.32" />
        <circle cx="260" cy="268" r="168" fill="none" stroke="#c9a873" strokeWidth="1.1" opacity="0.26" />
        <circle cx="260" cy="268" r="126" fill="none" stroke="#c9a873" strokeWidth="1.35" opacity="0.38" />
        <circle cx="260" cy="268" r="84" fill="none" stroke="#7ba3c9" strokeWidth="1.15" opacity="0.34" />
        <circle cx="260" cy="268" r="44" fill="none" stroke="#c9a873" strokeWidth="1" opacity="0.22" />

        <ellipse cx="260" cy="268" rx="210" ry="78" fill="none" stroke="#c9a873" strokeWidth="0.85" opacity="0.16" transform="rotate(16 260 268)" />
        <ellipse cx="260" cy="268" rx="210" ry="78" fill="none" stroke="#7ba3c9" strokeWidth="0.85" opacity="0.14" transform="rotate(-28 260 268)" />
        <ellipse cx="260" cy="268" rx="168" ry="52" fill="none" stroke="#c9a873" strokeWidth="0.75" opacity="0.18" transform="rotate(48 260 268)" />

        {[
          [260, 58],
          [418, 148],
          [445, 278],
          [350, 448],
          [170, 448],
          [75, 278],
          [102, 148],
          [260, 478],
        ].map(([x, y], i) => (
          <g key={i} filter="url(#landingSoftGlow)">
            <line x1="260" y1="268" x2={x} y2={y} stroke="url(#landingMapLine)" strokeWidth="0.85" opacity="0.24" />
            <circle cx={x} cy={y} r="8" fill="#fffdf9" stroke="#c9a873" strokeWidth="1.15" opacity="0.92" />
            <circle cx={x} cy={y} r="3.5" fill="#c9a873" opacity="0.7" />
          </g>
        ))}

        {[
          [195, 195],
          [325, 210],
          [315, 340],
          [190, 325],
          [260, 210],
          [280, 268],
        ].map(([x, y], i) => (
          <circle key={`inner-${i}`} cx={x} cy={y} r="5" fill="#7ba3c9" fillOpacity="0.42" />
        ))}

        <circle cx="260" cy="268" r="13" fill="#fffdf9" stroke="#c9a873" strokeWidth="1.7" />
        <circle cx="260" cy="268" r="5.5" fill="#c9a873" opacity="0.88" />

        <path
          d="M 130 400 Q 195 355 260 372 T 390 400"
          fill="none"
          stroke="#c9a873"
          strokeWidth="1"
          opacity="0.22"
          strokeDasharray="4 7"
        />
        <path
          d="M 95 235 Q 175 190 260 202 T 425 235"
          fill="none"
          stroke="#7ba3c9"
          strokeWidth="1"
          opacity="0.2"
          strokeDasharray="3 6"
        />
        <path
          d="M 140 120 Q 200 160 260 145 T 380 120"
          fill="none"
          stroke="#c9a873"
          strokeWidth="0.9"
          opacity="0.15"
          strokeDasharray="5 8"
        />
      </svg>
    </div>
  );
}
