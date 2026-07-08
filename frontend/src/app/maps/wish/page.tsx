"use client";

import Link from "next/link";
import { FormEvent, useEffect, useMemo, useState } from "react";
import { DsBody, DsButton } from "@/design-system";
import { ProductPageScreen } from "@/components/product-ui/ProductPageScreen";
import pl from "@/design-system/layouts/productPageLayout.module.css";
import v2 from "@/design-system/layouts/productV2Surface.module.css";
import { getJson } from "@/lib/api";
import { useAuth } from "@/lib/useAuth";
import { getLocale } from "@/lib/i18n";
import {
  buildWishAnchorStory,
  buildWishAnchors,
  buildWishMapObservation,
  buildWishShareLine,
  type WishGoalIn,
} from "@/lib/wishMapModel";
import { wishMapCopy } from "@/lib/wishMapCopy";
import { copyMapShareLine } from "@/lib/mapShareCard";
import { saveLocalWishAnchor, wishConstellationPosition, type WishAnchorRecord } from "@/lib/wishMapStore";

type CalendarPayload = { goal_tracks?: WishGoalIn[] };

export default function WishMapPage() {
  const locale = getLocale() === "ru" ? "ru" : "en";
  const copy = wishMapCopy(locale);
  const { isAuthenticated } = useAuth();

  const [anchors, setAnchors] = useState<WishAnchorRecord[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [draft, setDraft] = useState("");
  const [shareCopied, setShareCopied] = useState(false);

  const reload = async () => {
    let goals: WishGoalIn[] = [];
    if (isAuthenticated) {
      goals = (await getJson<CalendarPayload>("/tracking/calendar").catch(() => ({ goal_tracks: [] }))).goal_tracks ?? [];
    }
    const next = buildWishAnchors(goals);
    setAnchors(next);
    if (!selectedId && next[0]) setSelectedId(next[0].id);
  };

  useEffect(() => {
    void reload();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAuthenticated]);

  const selected = useMemo(
    () => anchors.find((a) => a.id === selectedId) ?? anchors[0] ?? null,
    [anchors, selectedId],
  );
  const observation = useMemo(() => buildWishMapObservation(anchors, locale), [anchors, locale]);
  const selectedStory = selected ? buildWishAnchorStory(selected, locale) : null;
  const shareLine = useMemo(() => buildWishShareLine(anchors, locale), [anchors, locale]);

  const onAdd = (event: FormEvent) => {
    event.preventDefault();
    const trimmed = draft.trim();
    if (!trimmed) return;
    saveLocalWishAnchor(trimmed);
    setDraft("");
    void reload();
  };

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
      testId="wish-map-page"
      eyebrow={copy.eyebrow}
      title={copy.title}
      subtitle={anchors.length > 0 ? copy.lead : copy.emptyLead}
      contentClassName={`${pl.content} ${pl.legacyHost}`}
    >
      <nav className={pl.toolbar} aria-label="Maps">
        <Link href="/today" className={pl.textLink}>{copy.linkToday}</Link>
        <Link href="/profile" className={pl.textLink}>{copy.linkProfile}</Link>
        <Link href="/tracking/calendar?create=goal" className={pl.textLink}>{copy.linkRhythm}</Link>
      </nav>

      <section
        className={pl.panel}
          style={{
            padding: "1.1rem",
            minHeight: "220px",
            position: "relative",
            background: "radial-gradient(420px 180px at 50% 40%, rgba(248, 242, 255, 0.55), rgba(255, 253, 249, 0.96))",
            border: "1px solid rgba(166, 124, 58, 0.16)",
          }}
          aria-label={copy.title}
        >
          {anchors.length === 0 ? (
            <p className="orbit-body-sm" style={{ margin: 0, color: "#9a8468" }}>{copy.emptyLead}</p>
          ) : (
            anchors.map((anchor, index) => {
              const pos = wishConstellationPosition(anchor.id, index);
              const active = selected?.id === anchor.id;
              return (
                <button
                  key={anchor.id}
                  type="button"
                  onClick={() => setSelectedId(anchor.id)}
                  title={anchor.title}
                  style={{
                    position: "absolute",
                    left: `${pos.x}%`,
                    top: `${pos.y}%`,
                    transform: "translate(-50%, -50%)",
                    width: active ? "1.1rem" : "0.85rem",
                    height: active ? "1.1rem" : "0.85rem",
                    borderRadius: "50%",
                    border: active ? "2px solid rgba(91, 67, 53, 0.65)" : "1px solid rgba(166, 124, 58, 0.2)",
                    background: (anchor.stepCount ?? 0) > 0 ? "rgba(214, 179, 122, 0.95)" : "rgba(236, 228, 214, 0.75)",
                    cursor: "pointer",
                    padding: 0,
                  }}
                />
              );
            })
          )}
        </section>

        <form onSubmit={onAdd} style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
          <input
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            placeholder={copy.addPlaceholder}
            className={pl.fieldInput}
            style={{ flex: "1 1 200px" }}
          />
          <DsButton type="submit" variant="secondary">
            {copy.addCta}
          </DsButton>
        </form>

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
