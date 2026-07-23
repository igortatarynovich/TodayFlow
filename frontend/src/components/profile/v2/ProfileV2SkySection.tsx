"use client";

import type { NatalChartPreview } from "@/components/profile/profilePanelTypes";
import type { ProfileFrameworkAnchor, ProfileFrameworkCard } from "@/lib/profilePage/buildProfileQuickMapData";
import styles from "@/components/profile/v2/profileV2System.module.css";
import { PROFILE_V2_COPY } from "@/components/profile/v2/profileV2SystemCopy";

export type ProfileV2SkySectionProps = {
  natalPreview: NatalChartPreview | null;
  previewError: string | null;
  onReloadPreview: () => void;
  frameworkAnchors: ProfileFrameworkAnchor[];
  frameworkCards?: ProfileFrameworkCard[];
};

type SourceKind = "sun" | "moon" | "rising" | "mc" | "lp" | "other";

type SourceNode = {
  id: string;
  kind: SourceKind;
  label: string;
  hint: string | null;
  weight: "primary" | "secondary" | "satellite";
};

function roleForAnchor(id: string, cards: ProfileFrameworkCard[]): string | null {
  const card = cards.find((item) => item.id === id);
  const body = card?.body?.trim();
  if (!body) return null;
  const first = body.split(/[.!?]/)[0]?.trim();
  if (!first) return null;
  return first.length > 120 ? `${first.slice(0, 117)}…` : first;
}

function classifyAnchor(id: string): SourceKind {
  const key = id.toLowerCase();
  if (key === "sun") return "sun";
  if (key === "moon") return "moon";
  if (key === "rising" || key === "asc" || key === "ascendant") return "rising";
  if (key === "mc" || key === "midheaven") return "mc";
  if (key === "lp" || key === "life_path" || key.includes("path")) return "lp";
  return "other";
}

function weightFor(kind: SourceKind): SourceNode["weight"] {
  if (kind === "sun") return "primary";
  if (kind === "moon" || kind === "rising") return "secondary";
  return "satellite";
}

function stripArchetypePrefix(label: string): string {
  return label.replace(/^Архетип\s+/i, "").trim() || label;
}

/**
 * Personality sources as a causal constellation converging on the archetype —
 * not an equal card grid.
 */
export function ProfileV2SkySection({
  natalPreview,
  previewError,
  onReloadPreview,
  frameworkAnchors,
  frameworkCards = [],
}: ProfileV2SkySectionProps) {
  const copy = PROFILE_V2_COPY.zones.sources;

  const archetypeAnchor = frameworkAnchors.find((a) => a.id === "archetype");
  const archetypeCard = frameworkCards.find((c) => c.id === "archetype");
  const archetypeName = stripArchetypePrefix(
    archetypeAnchor?.label || archetypeCard?.title || copy.archetypeFallback,
  );

  const sourceAnchors = frameworkAnchors.filter((a) => a.id !== "archetype");
  const nodes: SourceNode[] = (sourceAnchors.length
    ? sourceAnchors
    : natalPreview
      ? [{ id: "natal", label: "Натальная карта рассчитана" }]
      : []
  ).map((anchor) => {
    const kind = classifyAnchor(anchor.id);
    return {
      id: anchor.id,
      kind,
      label: anchor.label,
      hint: roleForAnchor(anchor.id, frameworkCards),
      weight: weightFor(kind),
    };
  });

  // Stable visual order: sun → moon → rising → mc → lp → other
  const order: SourceKind[] = ["sun", "moon", "rising", "mc", "lp", "other"];
  nodes.sort((a, b) => order.indexOf(a.kind) - order.indexOf(b.kind));

  return (
    <div className={styles.constellationShell} data-testid="profile-v2-sky-section">
      <p className={styles.constellationEyebrow}>{copy.sourcesLabel}</p>

      {nodes.length ? (
        <div className={styles.constellationStage} data-testid="profile-v2-sources-constellation">
          <ul className={styles.constellationRing} role="list">
            {nodes.map((node) => (
              <li
                key={node.id}
                className={[
                  styles.constellationNode,
                  styles[`constellationNode_${node.kind}`] || styles.constellationNode_other,
                  node.weight === "primary" ? styles.constellationNodePrimary : "",
                  node.weight === "satellite" ? styles.constellationNodeSatellite : "",
                ]
                  .filter(Boolean)
                  .join(" ")}
                data-source-kind={node.kind}
              >
                <span className={styles.constellationGlyph} aria-hidden />
                <span className={styles.constellationLabel}>{node.label}</span>
                {node.hint ? <span className={styles.constellationHint}>{node.hint}</span> : null}
              </li>
            ))}
          </ul>

          <div className={styles.constellationHub} data-testid="profile-v2-sources-archetype">
            <p className={styles.constellationBornFrom}>{copy.bornFrom}</p>
            <p className={styles.constellationArchetype}>{archetypeName}</p>
          </div>
        </div>
      ) : (
        <div className={styles.skyEmpty}>
          <p className={styles.skyAspectBody}>
            Сигнатуры появятся после сохранения данных рождения. Полная карта — за «Исследовать глубже».
          </p>
          <button type="button" className={styles.skyReloadBtn} onClick={onReloadPreview}>
            Обновить карту
          </button>
        </div>
      )}

      <p className={styles.constellationFootnote}>{copy.exploreHint}</p>

      {previewError ? <p className={styles.skyError}>{previewError}</p> : null}
    </div>
  );
}
