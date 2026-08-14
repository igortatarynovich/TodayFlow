"use client";

import { useState } from "react";
import { CelestialMoon } from "@/components/celestial/CelestialMoon";

/**
 * Dev harness: prove free lunar texture + light + glow can reach premium CGI class.
 * Production builds show a stub only.
 */
export default function CelestialMoonPreviewPage() {
  const [phase, setPhase] = useState(0.5);
  const [glow, setGlow] = useState(1);
  const [spin, setSpin] = useState(0.035);
  const [size, setSize] = useState(360);
  const [longitude, setLongitude] = useState(0);

  // Intentionally reachable on the live stack for owner visual QA of the method.
  // Not linked from product chrome; remove or re-gate after the experiment.

  return (
    <main
      data-testid="celestial-moon-preview"
      style={{
        minHeight: "100vh",
        position: "relative",
        isolation: "isolate",
        color: "#e8e4dc",
        padding: "1.5rem clamp(0.75rem, 3vw, 2.5rem) 3rem",
        fontFamily: "ui-sans-serif, system-ui, sans-serif",
        backgroundColor: "#04060c",
        backgroundImage: [
          "radial-gradient(ellipse at 50% 36%, rgba(4,8,18,0.15) 0%, rgba(2,4,10,0.72) 48%, rgba(0,0,0,0.88) 100%)",
          "image-set(url('/images/celestial/nasa_starfield.jpg') 1x, url('/images/celestial/nasa_starfield.jpg') 2x)",
        ].join(", "),
        backgroundSize: "cover, cover",
        backgroundPosition: "center, center",
        backgroundRepeat: "no-repeat, no-repeat",
        backgroundAttachment: "fixed, fixed",
      }}
    >
      <header style={{ maxWidth: 720, margin: "0 auto 1.75rem" }}>
        <p style={{ margin: 0, opacity: 0.55, letterSpacing: "0.14em", fontSize: 11, textTransform: "uppercase" }}>
          Celestial prototype
        </p>
        <h1 style={{ margin: "0.35rem 0 0.5rem", fontSize: "clamp(1.4rem, 3vw, 1.85rem)", fontWeight: 600 }}>
          Луна из текстуры + света
        </h1>
        <p style={{ margin: 0, opacity: 0.7, lineHeight: 1.5, fontSize: 14, maxWidth: 52 * 8 }}>
          Не stock-картинка. Sphere + NASA-derived map + soft terminator + rim + CSS bloom. Крути фазу —
          это уже свой объект, не один PNG.
        </p>
      </header>

      <div
        style={{
          display: "grid",
          placeItems: "center",
          minHeight: "min(62vh, 560px)",
          marginBottom: "1.75rem",
        }}
      >
        <CelestialMoon phase={phase} glow={glow} spin={spin} size={size} longitude={longitude} />
      </div>

      <section
        style={{
          maxWidth: 520,
          margin: "0 auto",
          display: "grid",
          gap: "0.9rem",
          padding: "1rem 1.1rem",
          borderRadius: 16,
          background: "rgba(6,10,18,0.72)",
          border: "1px solid rgba(255,255,255,0.1)",
          backdropFilter: "blur(10px)",
          WebkitBackdropFilter: "blur(10px)",
        }}
      >
        <label style={{ display: "grid", gap: 6, fontSize: 13 }}>
          <span style={{ display: "flex", justifyContent: "space-between" }}>
            Longitude <em style={{ fontStyle: "normal", opacity: 0.55 }}>{longitude.toFixed(2)}</em>
          </span>
          <input
            type="range"
            min={-Math.PI}
            max={Math.PI}
            step={0.01}
            value={longitude}
            onChange={(e) => setLongitude(Number(e.target.value))}
            data-testid="moon-longitude"
          />
        </label>
        <label style={{ display: "grid", gap: 6, fontSize: 13 }}>
          <span style={{ display: "flex", justifyContent: "space-between" }}>
            Phase <em style={{ fontStyle: "normal", opacity: 0.55 }}>{phase.toFixed(2)}</em>
          </span>
          <input
            type="range"
            min={0}
            max={1}
            step={0.01}
            value={phase}
            onChange={(e) => setPhase(Number(e.target.value))}
            data-testid="moon-phase"
          />
        </label>
        <label style={{ display: "grid", gap: 6, fontSize: 13 }}>
          <span style={{ display: "flex", justifyContent: "space-between" }}>
            Glow <em style={{ fontStyle: "normal", opacity: 0.55 }}>{glow.toFixed(2)}</em>
          </span>
          <input
            type="range"
            min={0.2}
            max={1.6}
            step={0.05}
            value={glow}
            onChange={(e) => setGlow(Number(e.target.value))}
            data-testid="moon-glow"
          />
        </label>
        <label style={{ display: "grid", gap: 6, fontSize: 13 }}>
          <span style={{ display: "flex", justifyContent: "space-between" }}>
            Spin <em style={{ fontStyle: "normal", opacity: 0.55 }}>{spin.toFixed(3)}</em>
          </span>
          <input
            type="range"
            min={0}
            max={0.2}
            step={0.005}
            value={spin}
            onChange={(e) => setSpin(Number(e.target.value))}
            data-testid="moon-spin"
          />
        </label>
        <label style={{ display: "grid", gap: 6, fontSize: 13 }}>
          <span style={{ display: "flex", justifyContent: "space-between" }}>
            Size <em style={{ fontStyle: "normal", opacity: 0.55 }}>{size}px</em>
          </span>
          <input
            type="range"
            min={180}
            max={480}
            step={10}
            value={size}
            onChange={(e) => setSize(Number(e.target.value))}
            data-testid="moon-size"
          />
        </label>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 8, marginTop: 4 }}>
          {[
            { label: "New", v: 0 },
            { label: "Waxing", v: 0.25 },
            { label: "Full", v: 0.5 },
            { label: "Waning", v: 0.75 },
          ].map((p) => (
            <button
              key={p.label}
              type="button"
              onClick={() => setPhase(p.v)}
              style={{
                padding: "0.4rem 0.75rem",
                borderRadius: 999,
                border: "1px solid rgba(255,255,255,0.16)",
                background: Math.abs(phase - p.v) < 0.02 ? "rgba(255,255,255,0.14)" : "transparent",
                color: "inherit",
                cursor: "pointer",
                fontSize: 12,
              }}
            >
              {p.label}
            </button>
          ))}
        </div>
      </section>

      <p
        style={{
          maxWidth: 520,
          margin: "1.25rem auto 0",
          fontSize: 12,
          opacity: 0.45,
          lineHeight: 1.45,
        }}
      >
        Moon: <code>moon_lro_2k.jpg</code> (sphere · axial Y-spin) · Sky: <code>nasa_starfield.jpg</code>{" "}
        (NASA WISE PIA15417) · see ATTRIBUTION.md.
      </p>
    </main>
  );
}
