import type { CSSProperties, ReactNode } from "react";
import { DsBody, DsEyebrow, DsTag } from "@/design-system/primitives/DsTypography";
import p from "@/design-system/patterns/dsPatterns.module.css";

export type DsOrbitalNode = {
  id: string;
  label: string;
  icon: ReactNode;
  style: CSSProperties;
};

export function DsOrbitalViz({ nodes, testId }: { nodes: DsOrbitalNode[]; testId?: string }) {
  return (
    <div className={p.orbitViz} data-testid={testId} aria-hidden>
      {[1, 2, 3, 4, 5].map((ring) => (
        <span key={ring} className={p.orbitRing} />
      ))}
      <span className={p.orbitCenter} />
      {nodes.map((node) => (
        <span key={node.id} className={p.orbitNode} style={node.style}>
          <span className={p.orbitNodeIcon}>{node.icon}</span>
          {node.label}
        </span>
      ))}
    </div>
  );
}

export function DsThemeViz() {
  return (
    <div className={p.themeViz} aria-hidden>
      <span className={p.themeRing} />
      <span className={p.themeRing} />
      <span className={p.themeRing} />
      <span className={p.themeCore} />
    </div>
  );
}

type DsThemePanelProps = {
  eyebrow: string;
  title: string;
  tags?: string[];
  body?: string;
  aside?: ReactNode;
  variant?: "compact" | "marketing";
  titleId?: string;
};

export function DsThemePanel({
  eyebrow,
  title,
  tags = [],
  body,
  aside,
  variant = "compact",
  titleId,
}: DsThemePanelProps) {
  const isMarketing = variant === "marketing";
  return (
    <section
      className={`${p.themePanel} ${isMarketing ? p.themePanelMarketing : p.themePanelCompact}`}
      aria-labelledby={titleId}
    >
      <DsThemeViz />
      <div className={p.themeContent}>
        <DsEyebrow onDark>{eyebrow}</DsEyebrow>
        <h2 id={titleId} className={`${p.themeTitle} ${isMarketing ? p.themeTitleMarketing : ""}`}>
          {title}
        </h2>
        {tags.length > 0 ? (
          <div className={p.themeTags}>
            {tags.map((tag) => (
              <DsTag key={tag} onDark>
                {tag}
              </DsTag>
            ))}
          </div>
        ) : null}
        {body ? (
          <DsBody size="sm" onDark muted>
            {body}
          </DsBody>
        ) : null}
      </div>
      {aside ? <div className={p.themeAside}>{aside}</div> : null}
    </section>
  );
}
