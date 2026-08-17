"use client";

import { useCallback, useEffect, useId, useState } from "react";
import { TODAY_COMPOSITION_COPY as copy } from "@/components/today/composition/todayCompositionCopy";
import {
  DsBody,
  DsCaption,
  DsEyebrow,
  DsListPanel,
  DsListRow,
  DsOverlaySheet,
  DsPlanet,
  DsZodiac,
} from "@/design-system";
import layout from "@/design-system/compositions/dsCompositions.module.css";
import type { TodaySkyStripModel } from "@/lib/todaySkyToday";
import { joinSkyMeta } from "@/lib/todaySkyToday";

function BodyInSign({
  body,
  sign,
  size = 28,
}: {
  body: string;
  sign?: string | null;
  size?: number;
}) {
  return (
    <span className={layout.skyPair}>
      <DsPlanet planet={body} size={size} fit="cover" />
      {sign ? <DsZodiac sign={sign} size={Math.round(size * 0.86)} /> : null}
    </span>
  );
}

function TodaySkySheet({
  model,
  onClose,
}: {
  model: TodaySkyStripModel;
  onClose: () => void;
}) {
  const titleId = useId();
  useEffect(() => {
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
  }, [onClose]);

  const lead = model.headlineLabel || model.moonLabel || copy.skySheetTitle;

  return (
    <DsOverlaySheet
      testId="today-sky-sheet"
      titleId={titleId}
      title={lead}
      kicker={copy.skyStripKicker}
      closeLabel={copy.sheetClose}
      onClose={onClose}
    >
      <DsListPanel tone="solid" title={copy.skySheetShared} testId="today-sky-sheet-shared">
        {model.headline && model.headlineLabel ? (
          <DsListRow
            testId="today-sky-sheet-headline"
            leading={
              <span className={layout.skyPair}>
                <BodyInSign body={model.headline.planet_a} sign={model.headline.sign_a} size={32} />
                <BodyInSign body={model.headline.planet_b} sign={model.headline.sign_b} size={32} />
              </span>
            }
            title={model.headlineLabel}
            subtitle={joinSkyMeta([model.headlineWhen, model.headlineOrb, model.sharedStory]) || undefined}
          />
        ) : null}
        {model.moon && model.moonLabel ? (
          <DsListRow
            testId="today-sky-sheet-moon"
            leading={<BodyInSign body={model.moon.body} sign={model.moon.sign} size={32} />}
            title={joinSkyMeta([model.moonLabel, model.moonDegree]) || model.moonLabel}
            subtitle={model.moonWhen ? `с ${model.moonWhen}` : undefined}
          />
        ) : null}
        {model.windowLabel ? (
          <DsListRow testId="today-sky-sheet-window" title={copy.skySheetWindow} subtitle={model.windowLabel} />
        ) : null}
      </DsListPanel>
      {model.personalLine ? (
        <DsListPanel tone="solid" title={copy.skySheetPersonal} testId="today-sky-sheet-personal">
          <DsListRow testId="today-sky-sheet-personal-line" title={model.personalLine} />
        </DsListPanel>
      ) : null}
    </DsOverlaySheet>
  );
}

export function TodaySkyStrip({ model }: { model: TodaySkyStripModel }) {
  const [open, setOpen] = useState(false);
  const openSheet = useCallback(() => setOpen(true), []);
  const closeSheet = useCallback(() => setOpen(false), []);

  const leadLabel = model.headlineLabel || model.moonLabel;
  if (!leadLabel) return null;
  const leadLine = model.headlineLabel
    ? joinSkyMeta([model.headlineLabel, model.headlineWhen]) || model.headlineLabel
    : joinSkyMeta([model.moonLabel, model.moonDegree, model.moonWhen ? `с ${model.moonWhen}` : null]) || leadLabel;

  return (
    <>
      <button
        type="button"
        className={layout.skyStrip}
        data-testid="today-sky-strip"
        onClick={openSheet}
        aria-label={copy.skyStripOpen}
      >
        <DsEyebrow>{copy.skyStripKicker}</DsEyebrow>
        <span className={layout.skyStripRow}>
          {model.headline ? (
            <span className={layout.skyStripHeadlineArt} aria-hidden>
              <BodyInSign body={model.headline.planet_a} sign={model.headline.sign_a} />
              <BodyInSign body={model.headline.planet_b} sign={model.headline.sign_b} />
            </span>
          ) : null}
          <span className={layout.skyStripCopy}>
            <DsBody size="sm">
              <span data-testid="today-sky-strip-headline">{leadLine}</span>
            </DsBody>
            {model.headlineLabel && model.moonLabel ? (
              <DsCaption>
                <span data-testid="today-sky-strip-moon">
                  {joinSkyMeta([
                    model.moonLabel,
                    model.moonDegree,
                    model.moonWhen ? `с ${model.moonWhen}` : null,
                  ])}
                </span>
              </DsCaption>
            ) : null}
          </span>
        </span>
      </button>
      {open ? <TodaySkySheet model={model} onClose={closeSheet} /> : null}
    </>
  );
}
