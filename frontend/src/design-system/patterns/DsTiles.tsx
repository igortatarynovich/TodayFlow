import type { ReactNode } from "react";
import { DsCheckbox } from "@/design-system/primitives/DsForm";
import { DsBody, DsEyebrow, DsIconBadge, DsSurface, DsTag } from "@/design-system/primitives/DsTypography";
import p from "@/design-system/primitives/dsPrimitives.module.css";
import pat from "@/design-system/patterns/dsPatterns.module.css";

export function DsFeatureTile({
  icon,
  title,
  body,
  testId,
}: {
  icon: ReactNode;
  title: string;
  body: string;
  testId?: string;
}) {
  return (
    <DsSurface variant="outline" as="article" className={pat.featureTile} testId={testId}>
      <DsIconBadge size="lg">
        <span className={p.iconSvg}>{icon}</span>
      </DsIconBadge>
      <div>
        <h2 className={p.displaySm}>{title}</h2>
        <DsBody muted className={p.bodyMd}>
          {body}
        </DsBody>
      </div>
    </DsSurface>
  );
}

export function DsInsightTile({
  label,
  title,
  body,
  visual,
}: {
  label: string;
  title: string;
  body?: string;
  visual: ReactNode;
}) {
  return (
    <DsSurface className={pat.insightTile}>
      <div className={pat.insightVisual}>{visual}</div>
      <div>
        <p className={pat.insightLabel}>{label}</p>
        <h3 className={pat.insightTitle}>{title}</h3>
        {body ? <DsBody size="sm" muted>{body}</DsBody> : null}
      </div>
    </DsSurface>
  );
}

export function DsQuoteTile({ quote, name, role }: { quote: string; name: string; role: string }) {
  return (
    <DsSurface variant="elevated" as="article" className={pat.quoteTile}>
      <p className={pat.quoteText}>&ldquo;{quote}&rdquo;</p>
      <div>
        <p className={p.bodySm} style={{ fontWeight: 700, margin: 0 }}>
          {name}
        </p>
        <DsEyebrow className={p.bodySm}>{role}</DsEyebrow>
      </div>
    </DsSurface>
  );
}

export function DsThemeAsideRow({
  icon,
  label,
  value,
  testId,
}: {
  icon: ReactNode;
  label: string;
  value: string;
  testId?: string;
}) {
  return (
    <DsSurface variant="glass" className={pat.themeAsideRow} testId={testId}>
      <DsIconBadge>
        <span className={p.iconSvg}>{icon}</span>
      </DsIconBadge>
      <div>
        <DsEyebrow onDark>{label}</DsEyebrow>
        <p className={pat.insightTitle} style={{ color: "var(--tf-on-dark)" }}>
          {value}
        </p>
      </div>
    </DsSurface>
  );
}

export function DsPracticeRow({
  title,
  durationLabel,
  completed,
}: {
  title: string;
  durationLabel?: string;
  completed?: boolean;
}) {
  return (
    <DsSurface className={pat.practiceRow}>
      <DsCheckbox checked={completed} disabled aria-label={`Практика: ${title}`} />
      <div>
        {durationLabel ? <p className={pat.practiceDuration}>{durationLabel}</p> : null}
        <p className={pat.practiceTitle}>{title}</p>
      </div>
    </DsSurface>
  );
}

export function DsTagRow({ tags, onDark, outline }: { tags: string[]; onDark?: boolean; outline?: boolean }) {
  return (
    <>
      {tags.map((tag) => (
        <DsTag key={tag} onDark={onDark} outline={outline}>
          {tag}
        </DsTag>
      ))}
    </>
  );
}
