import {
  Caveat,
  Cormorant_Garamond,
  Inter,
  Instrument_Serif,
  Lora,
  Manrope,
  Playfair_Display,
} from "next/font/google";

// Self-hosted at build time instead of the old CSS @import to Google Fonts / rsms.me.
// Each export exposes a CSS variable consumed by --tf-font-*/--orbit-font-* in
// todayflow-foundation.css and styles/globals/01-tokens-base.css.

export const instrumentSerif = Instrument_Serif({
  subsets: ["latin"],
  weight: "400",
  style: ["normal", "italic"],
  variable: "--font-instrument-serif",
  display: "swap",
});

export const playfairDisplay = Playfair_Display({
  subsets: ["latin", "cyrillic"],
  weight: ["500", "600", "700"],
  variable: "--font-playfair-display",
  display: "swap",
});

export const cormorantGaramond = Cormorant_Garamond({
  subsets: ["latin"],
  weight: ["500", "600", "700"],
  variable: "--font-cormorant-garamond",
  display: "swap",
});

export const lora = Lora({
  subsets: ["latin", "cyrillic"],
  weight: ["400", "500", "600"],
  variable: "--font-lora",
  display: "swap",
});

export const manrope = Manrope({
  subsets: ["latin", "cyrillic"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-manrope",
  display: "swap",
});

export const inter = Inter({
  subsets: ["latin", "cyrillic"],
  variable: "--font-inter",
  display: "swap",
});

export const caveat = Caveat({
  subsets: ["latin"],
  weight: ["400", "500", "600"],
  variable: "--font-caveat",
  display: "swap",
});

export const fontVariables = [
  instrumentSerif.variable,
  playfairDisplay.variable,
  cormorantGaramond.variable,
  lora.variable,
  manrope.variable,
  inter.variable,
  caveat.variable,
].join(" ");
