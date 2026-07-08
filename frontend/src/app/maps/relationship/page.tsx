"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { DsBody, DsButton } from "@/design-system";
import { ProductPageScreen } from "@/components/product-ui/ProductPageScreen";
import pl from "@/design-system/layouts/productPageLayout.module.css";
import v2 from "@/design-system/layouts/productV2Surface.module.css";
import { getLocale } from "@/lib/i18n";
import {
  buildRelationshipCircleStory,
  buildRelationshipMapObservation,
  buildRelationshipShareLine,
  relationshipCircleRadius,
  scanRelationshipMapCircles,
  type RelationshipCircleRecord,
} from "@/lib/relationshipMapModel";
import { relationshipMapCopy } from "@/lib/relationshipMapCopy";
import { relationshipCirclePosition } from "@/lib/relationshipMapStore";
import { copyMapShareLine } from "@/lib/mapShareCard";

export default function RelationshipMapPage() {
  const locale = getLocale() === "ru" ? "ru" : "en";
  const copy = relationshipMapCopy(locale);

  const [circles, setCircles] = useState<RelationshipCircleRecord[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [shareCopied, setShareCopied] = useState(false);

  useEffect(() => {
    const next = scanRelationshipMapCircles();
    setCircles(next);
    if (next[0]) setSelectedId(next[0].id);
  }, []);

  const selected = useMemo(
    () => circles.find((c) => c.id === selectedId) ?? circles[0] ?? null,
    [circles, selectedId],
  );
  const observation = useMemo(() => buildRelationshipMapObservation(circles, locale), [circles, locale]);
  const selectedStory = selected ? buildRelationshipCircleStory(selected, locale) : null;
  const shareLine = useMemo(() => buildRelationshipShareLine(circles, locale), [circles, locale]);

  const onShare = async () => {
    if (!shareLine) return;
    const ok = await copyMapShareLine(shareLine);
    if (ok) {
      setShareCopied(true);
      window.setTimeout(() => setShareCopied(false), 2000);
    }
  };

  return (
    <ProductPageScreen
      testId="relationship-map-page"
      eyebrow={copy.eyebrow}
      title={copy.title}
      subtitle={circles.length > 0 ? copy.lead : copy.emptyLead}
      contentClassName={`${pl.content} ${pl.legacyHost}`}
    >
      <nav className={pl.toolbar} aria-label="Maps">
        <Link href="/compatibility" className={pl.textLink}>{copy.linkCompat}</Link>
        <Link href="/profile" className={pl.textLink}>{copy.linkProfile}</Link>
      </nav>

      <section
        className={pl.panel}
          style={{
            padding: "1.1rem",
            minHeight: "260px",
            position: "relative",
            background: "#fffdf9",
            border: "1px solid #ece4d8",
          }}
          aria-label={copy.title}
        >
          {circles.length === 0 ? (
            <p className="orbit-body-sm" style={{ margin: 0, color: "#9a8468" }}>{copy.emptyLead}</p>
          ) : (
            circles.map((circle, index) => {
              const pos = relationshipCirclePosition(index, circles.length);
              const active = selected?.id === circle.id;
              const size = relationshipCircleRadius(circle.visitCount);
              return (
                <button
                  key={circle.id}
                  type="button"
                  onClick={() => setSelectedId(circle.id)}
                  title={circle.label}
                  style={{
                    position: "absolute",
                    left: `${pos.x}%`,
                    top: `${pos.y}%`,
                    transform: "translate(-50%, -50%)",
                    width: `${size}px`,
                    height: `${size}px`,
                    borderRadius: "50%",
                    border: active ? "2px solid rgba(91, 67, 53, 0.65)" : "1px solid rgba(180, 120, 100, 0.25)",
                    background: "rgba(214, 179, 122, 0.35)",
                    cursor: "pointer",
                    padding: 0,
                    fontSize: "0.65rem",
                    color: "#5b4335",
                    overflow: "hidden",
                  }}
                >
                  <span style={{ display: "block", padding: "0.35rem", lineHeight: 1.2, textAlign: "center" }}>
                    {circle.label.length > 18 ? `${circle.label.slice(0, 16)}…` : circle.label}
                  </span>
                </button>
              );
            })
          )}
        </section>

        {observation ? (
          <section className={pl.panel}>
            <p className={v2.eyebrow}>{copy.observationEyebrow}</p>
            <DsBody className={pl.bodyMtSm}>{observation}</DsBody>
          </section>
        ) : null}

        <section className={pl.panel}>
          <p className={v2.eyebrow}>{copy.selectedEyebrow}</p>
          <DsBody className={pl.bodyMtMd}>{selectedStory ?? copy.selectedEmpty}</DsBody>
        </section>

        {shareLine ? (
          <DsButton variant="secondary" onClick={onShare}>
            {shareCopied ? copy.shareCopied : copy.shareCta}
          </DsButton>
        ) : null}

        <section className={pl.panel}>
          <h2 className={v2.sectionTitle}>{copy.howToReadTitle}</h2>
          <DsBody size="sm" muted className={pl.bodyMtSm}>{copy.howToRead}</DsBody>
        </section>
    </ProductPageScreen>
  );
}
