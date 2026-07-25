"use client";

import { useMemo } from "react";
import { CardVisual } from "@/components/tarot/CardVisual";
import { guidanceResultChromeBundle } from "@/components/guidance/guidanceResultChrome";
import type { FlowPracticesChromeLocale } from "@/components/today/flowPracticesMainTabChrome";
import { getLocale } from "@/lib/i18n";
import type { TarotSpreadCard } from "@/lib/types";
import { tarotCardBackPicture } from "@/lib/tarotCardAssets";
import { TarotPicture } from "@/components/tarot/TarotPicture";

type GuidanceSpreadStripProps = {
  spreadTitle?: string;
  cards: TarotSpreadCard[];
  revealed: boolean[];
  onReveal: (index: number) => void;
};

function TarotDeckBackButton({ onOpen, revealHint }: { onOpen: () => void; revealHint: string }) {
  const back = tarotCardBackPicture();
  return (
    <button type="button" onClick={onOpen} className="guidance-tarot-back-btn">
      <span className="guidance-tarot-back-btn__frame">
        <TarotPicture sources={back} sizes="168px" className="guidance-tarot-back-btn__img" />
      </span>
      <span className="guidance-tarot-back-btn__hint">{revealHint}</span>
    </button>
  );
}

export function GuidanceSpreadStrip({ spreadTitle, cards, revealed, onReveal }: GuidanceSpreadStripProps) {
  const locale: FlowPracticesChromeLocale = getLocale() === "ru" ? "ru" : "en";
  const gr = useMemo(() => guidanceResultChromeBundle(locale), [locale]);

  return (
    <div className="guidance-spread-strip">
      {spreadTitle ? <p className="guidance-spread-strip__title">{spreadTitle}</p> : null}
      <div className="guidance-spread-strip__grid">
        {cards.map((item, index) => {
          const isRev = item.orientation === "reversed";
          const positionLabel =
            typeof item.position === "object" && item.position?.title ? item.position.title : gr.guidanceStripPositionFallback;
          const open = Boolean(revealed[index]);
          return (
            <div key={`${item.card.id}-${index}`} className="guidance-spread-slot">
              <p className="guidance-spread-slot__pos">{positionLabel}</p>
              {open ? (
                <>
                  <CardVisual
                    card={item.card}
                    orientation={isRev ? "reversed" : "upright"}
                    size="md"
                    showName
                  />
                  <p className="orbit-body-xs" style={{ margin: 0, color: "#475569", lineHeight: 1.55, textAlign: "center" }}>
                    {item.meaning}
                  </p>
                </>
              ) : (
                <TarotDeckBackButton onOpen={() => onReveal(index)} revealHint={gr.guidanceStripRevealHint} />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
