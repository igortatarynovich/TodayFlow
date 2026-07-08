"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { DsBody, DsButton } from "@/design-system";
import { ProductPageScreen } from "@/components/product-ui/ProductPageScreen";
import pl from "@/design-system/layouts/productPageLayout.module.css";
import { TarotJourneyPanel } from "@/components/tarot/TarotJourneyPanel";
import { getLocale } from "@/lib/i18n";
import { buildTarotMapObservation, buildTarotMapShareLine } from "@/lib/tarotMapModel";
import { tarotMapCopy } from "@/lib/tarotMapCopy";
import { copyMapShareLine } from "@/lib/mapShareCard";
import { shouldShowTarotJourney } from "@/lib/tarotJourneyStore";

export default function TarotMapPage() {
  const locale = getLocale() === "ru" ? "ru" : "en";
  const copy = tarotMapCopy(locale);
  const [shareCopied, setShareCopied] = useState(false);

  const hasJourney = shouldShowTarotJourney();
  const observation = useMemo(() => buildTarotMapObservation(locale), [locale]);
  const shareLine = useMemo(() => buildTarotMapShareLine(locale), [locale]);

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
      testId="tarot-map-page"
      eyebrow={copy.eyebrow}
      title={copy.title}
      subtitle={hasJourney ? copy.lead : copy.emptyLead}
      contentClassName={`${pl.content} ${pl.legacyHost}`}
    >
      <nav className={pl.toolbar} aria-label="Maps">
        <Link href="/tarot" className={pl.textLink}>{copy.linkTarot}</Link>
        <Link href="/tarot/journey" className={pl.textLink}>{copy.linkJourney}</Link>
        <Link href="/profile" className={pl.textLink}>{copy.linkProfile}</Link>
      </nav>

      {hasJourney ? <div className={pl.panel}><TarotJourneyPanel /></div> : null}

      {observation ? (
        <section className={pl.panel}>
          <DsBody>{observation}</DsBody>
        </section>
      ) : null}

      {shareLine ? (
        <DsButton variant="secondary" onClick={onShare}>
          {shareCopied ? copy.shareCopied : copy.shareCta}
        </DsButton>
      ) : null}
    </ProductPageScreen>
  );
}
