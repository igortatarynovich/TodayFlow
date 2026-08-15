"use client";

import { useCallback, useEffect, useId, useState } from "react";
import {
  DsBody,
  DsCallout,
  DsListPanel,
  DsListRow,
  DsNumber,
  DsOverlaySheet,
  DsTarotFace,
} from "@/design-system";
import { TODAY_COMPOSITION_COPY as copy } from "@/components/today/composition/todayCompositionCopy";
import layout from "@/design-system/compositions/dsCompositions.module.css";

type SheetState = {
  title: string;
  kicker: string;
  catalog?: string | null;
  lens?: string | null;
} | null;

type Props = {
  cardTitle: string;
  cardFaceSrc?: string | null;
  cardCatalog?: string | null;
  cardLens?: string | null;
  numberDisplay: string;
  numberTitle?: string | null;
  numberCatalog?: string | null;
  numberLens?: string | null;
};

/**
 * Ritual state C — compact result cards. Tap → catalog base, then today's lens.
 * Canon: docs/today/TODAY_PRODUCT_FLOW_V1.md §2. Kit only. No invent.
 */
export function TodayRitualLensPair({
  cardTitle,
  cardFaceSrc = null,
  cardCatalog = null,
  cardLens = null,
  numberDisplay,
  numberTitle = null,
  numberCatalog = null,
  numberLens = null,
}: Props) {
  const [sheet, setSheet] = useState<SheetState>(null);
  const openCard = useCallback(() => {
    setSheet({
      title: cardTitle,
      kicker: copy.ritualCardLabel,
      catalog: cardCatalog,
      lens: cardLens,
    });
  }, [cardCatalog, cardLens, cardTitle]);
  const openNumber = useCallback(() => {
    setSheet({
      title: numberTitle || numberDisplay,
      kicker: copy.ritualNumberLabel,
      catalog: numberCatalog,
      lens: numberLens,
    });
  }, [numberCatalog, numberDisplay, numberLens, numberTitle]);

  return (
    <>
      <div className={layout.pairGrid} data-testid="today-ritual-result">
        <div data-testid="today-frame-card">
          <DsListPanel tone="glass" testId="today-ritual-lens-card-panel">
            <DsListRow
              testId="today-ritual-lens-card"
              leading={
                cardFaceSrc ? (
                  <DsTarotFace src={cardFaceSrc} alt={cardTitle} testId="today-ritual-lens-card-face" />
                ) : undefined
              }
              title={cardTitle}
              subtitle={copy.ritualCardLabel}
              onClick={openCard}
            />
          </DsListPanel>
        </div>
        <div data-testid="today-frame-number">
          <DsListPanel tone="glass" testId="today-ritual-lens-number-panel">
            <DsListRow
              testId="today-ritual-lens-number"
              leading={<DsNumber value={numberDisplay} size={44} alt={numberDisplay} />}
              title={numberTitle || numberDisplay}
              subtitle={copy.ritualNumberLabel}
              onClick={openNumber}
            />
          </DsListPanel>
        </div>
      </div>
      <RitualLensSheet sheet={sheet} onClose={() => setSheet(null)} />
    </>
  );
}

function RitualLensSheet({ sheet, onClose }: { sheet: SheetState; onClose: () => void }) {
  const titleId = useId();
  useEffect(() => {
    if (!sheet) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    const prev = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      window.removeEventListener("keydown", onKey);
      document.body.style.overflow = prev;
    };
  }, [sheet, onClose]);

  if (!sheet) return null;

  const catalog = String(sheet.catalog || "").trim();
  const lens = String(sheet.lens || "").trim();

  return (
    <DsOverlaySheet
      testId="today-ritual-lens-sheet"
      titleId={titleId}
      title={sheet.title}
      kicker={sheet.kicker}
      closeLabel={copy.sheetClose}
      onClose={onClose}
    >
      {catalog ? (
        <DsListPanel tone="subtle" testId="today-ritual-lens-catalog">
          <DsListRow title={copy.ritualCatalogLabel} subtitle={catalog} />
        </DsListPanel>
      ) : null}
      {lens ? (
        <DsCallout tone="insight" label="main" title={copy.ritualLensTodayLabel} testId="today-ritual-lens-today">
          <DsBody size="sm">{lens}</DsBody>
        </DsCallout>
      ) : null}
    </DsOverlaySheet>
  );
}
