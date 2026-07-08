import Link from "next/link";
import type { ReactNode } from "react";
import styles from "./TodayFlowScene.module.css";

export function PageShell({ children, className = "" }: { children: ReactNode; className?: string }) {
  return <div className={`${styles.pageShell} ${className}`.trim()}>{children}</div>;
}

export function SceneStack({ children }: { children: ReactNode }) {
  return <div className={styles.sceneStack}>{children}</div>;
}

export function SceneHeader({
  eyebrow,
  title,
  lead,
  markers = [],
}: {
  eyebrow: string;
  title: string;
  lead?: string | null;
  markers?: Array<{ label: string; value: string }>;
}) {
  return (
    <header className={styles.sceneHeader}>
      <div className={styles.sceneHeaderInner}>
        <p className={styles.caption}>{eyebrow}</p>
        <h1 className={styles.title}>{title}</h1>
        {lead ? <p className={styles.lead}>{lead}</p> : null}
        {markers.length ? (
          <div className={styles.markerRow}>
            {markers.map((marker) => (
              <span key={`${marker.label}-${marker.value}`} className={styles.marker}>
                {marker.label}: <strong>{marker.value}</strong>
              </span>
            ))}
          </div>
        ) : null}
      </div>
    </header>
  );
}

export function ActionObject({
  eyebrow,
  title,
  body,
  children,
}: {
  eyebrow: string;
  title: string;
  body?: string | null;
  children?: ReactNode;
}) {
  return (
    <section className={styles.actionObject} aria-labelledby="todayflow-action-title">
      <p className={styles.caption}>{eyebrow}</p>
      <h2 id="todayflow-action-title" className={styles.actionTitle}>
        {title}
      </h2>
      {body ? <p className={styles.actionBody}>{body}</p> : null}
      {children ? <div className={styles.actionControls}>{children}</div> : null}
    </section>
  );
}

export function ProgressLine({
  active,
  primary,
  secondary,
}: {
  active: boolean;
  primary: string;
  secondary?: string | null;
}) {
  return (
    <section className={styles.progressLine} aria-label="Прогресс">
      <span className={`${styles.progressDot} ${active ? styles.progressDotActive : ""}`} aria-hidden />
      <div>
        <p className={styles.progressText}>{primary}</p>
        {secondary ? <p className={styles.progressSub}>{secondary}</p> : null}
      </div>
    </section>
  );
}

export function DisclosureLine({ summary, children }: { summary: string; children: ReactNode }) {
  return (
    <details className={styles.disclosure}>
      <summary className={styles.disclosureSummary}>{summary}</summary>
      <div className={styles.disclosureBody}>{children}</div>
    </details>
  );
}

export function PortalPreview({
  eyebrow,
  facts,
  links,
}: {
  eyebrow: string;
  facts: Array<{ label: string; value: string }>;
  links: Array<{ href: string; label: string }>;
}) {
  if (!facts.length && !links.length) return null;
  return (
    <section className={styles.portalPreview} aria-label={eyebrow}>
      <div className={styles.portalSurface}>
        <p className={styles.caption}>{eyebrow}</p>
        {facts.length ? (
          <ul className={styles.portalFacts}>
            {facts.map((fact) => (
              <li key={`${fact.label}-${fact.value}`} className={styles.portalFact}>
                <strong>{fact.label}:</strong> {fact.value}
              </li>
            ))}
          </ul>
        ) : null}
        {links.length ? (
          <nav className={styles.portalLinks} aria-label="Углубление TodayFlow">
            {links.map((link) => (
              <Link key={link.href} href={link.href} className={styles.portalLink}>
                {link.label}
              </Link>
            ))}
          </nav>
        ) : null}
      </div>
    </section>
  );
}

export const todayFlowSceneStyles = styles;
