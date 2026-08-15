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
import { inSign, positionLabel, type TodaySkyStripModel } from "@/lib/todaySkyToday";

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
      {sign ? <DsZodiac sign={sign} size={Math.round(size * 0.86)} variant="illustration" /> : null}
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

  const positions = model.positions.length ? model.positions : [model.moon];

  return (
    <DsOverlaySheet
      testId="today-sky-sheet"
      titleId={titleId}
      title={copy.skySheetTitle}
      kicker={copy.skyStripKicker}
      closeLabel={copy.sheetClose}
      onClose={onClose}
    >
      <DsListPanel tone="solid" title={copy.skySheetPositions} testId="today-sky-sheet-positions">
        {positions.map((row) => (
          <DsListRow
            key={row.body}
            testId={`today-sky-sheet-body-${row.body}`}
            leading={<BodyInSign body={row.body} sign={row.sign} size={32} />}
            title={positionLabel(row)}
          />
        ))}
      </DsListPanel>
      {model.aspects.length ? (
        <DsListPanel tone="solid" title={copy.skySheetAspects} testId="today-sky-sheet-aspects">
          {model.aspects.map((row) => (
            <DsListRow
              key={row.id}
              testId={`today-sky-sheet-aspect-${row.id}`}
              leading={
                <span className={layout.skyPair}>
                  <DsPlanet planet={row.planet_a} size={28} fit="cover" />
                  <DsPlanet planet={row.planet_b} size={28} fit="cover" />
                </span>
              }
              title={row.title_ru}
              subtitle={
                inSign(row.planet_a_ru, row.sign_a_ru) && inSign(row.planet_b_ru, row.sign_b_ru)
                  ? `${inSign(row.planet_a_ru, row.sign_a_ru)} · ${inSign(row.planet_b_ru, row.sign_b_ru)}`
                  : undefined
              }
            />
          ))}
        </DsListPanel>
      ) : null}
    </DsOverlaySheet>
  );
}

export function TodaySkyStrip({ model }: { model: TodaySkyStripModel }) {
  const [open, setOpen] = useState(false);
  const openSheet = useCallback(() => setOpen(true), []);
  const closeSheet = useCallback(() => setOpen(false), []);

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
          <BodyInSign body={model.moon.body} sign={model.moon.sign} />
          <span className={layout.skyStripCopy}>
            <DsBody size="sm">
              <span data-testid="today-sky-strip-moon">{model.moonLabel}</span>
            </DsBody>
            {model.headlineLabel ? (
              <DsCaption>
                <span data-testid="today-sky-strip-headline">{model.headlineLabel}</span>
              </DsCaption>
            ) : null}
          </span>
          {model.headline ? (
            <span className={layout.skyStripHeadlineArt} aria-hidden>
              <BodyInSign body={model.headline.planet_a} sign={model.headline.sign_a} size={24} />
              <BodyInSign body={model.headline.planet_b} sign={model.headline.sign_b} size={24} />
            </span>
          ) : null}
        </span>
      </button>
      {open ? <TodaySkySheet model={model} onClose={closeSheet} /> : null}
    </>
  );
}
