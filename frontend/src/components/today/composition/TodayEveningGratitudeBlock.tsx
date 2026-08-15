"use client";

import { useMemo, useState } from "react";
import {
  DsButton,
  DsCallout,
  DsCaption,
  DsListPanel,
  DsListRow,
} from "@/design-system";
import { DsTextField } from "@/design-system/primitives/DsForm";
import { TODAY_COMPOSITION_COPY as copy } from "@/components/today/composition/todayCompositionCopy";
import {
  EVENING_GRATITUDE_CATEGORIES,
  loadEveningGratitude,
  persistEveningGratitude,
} from "@/lib/todayEveningGratitude";
import { todaySlotFailureCopy, type TodaySlotLoadFailure } from "@/lib/todaySlotAvailability";
import layout from "@/design-system/compositions/dsCompositions.module.css";

type Props = {
  dateISO: string;
  manifestVersion?: string | null;
  onSaved?: () => void;
};

export function TodayEveningGratitudeBlock({ dateISO, manifestVersion = null, onSaved }: Props) {
  const existing = useMemo(() => loadEveningGratitude(dateISO), [dateISO]);
  const [categories, setCategories] = useState<string[]>(existing?.categories ?? []);
  const [text, setText] = useState(existing?.text ?? "");
  const [saved, setSaved] = useState(Boolean(existing));
  const [saving, setSaving] = useState(false);
  const [failure, setFailure] = useState<TodaySlotLoadFailure | null>(null);

  const toggle = (id: string) => {
    setSaved(false);
    setFailure(null);
    setCategories((prev) => (prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]));
  };

  const canSave = categories.length > 0 || Boolean(text.trim());

  const onSave = async () => {
    if (!canSave || saving) return;
    setSaving(true);
    setFailure(null);
    const result = await persistEveningGratitude({
      dateISO,
      categories,
      text,
      manifestVersion,
    });
    setSaving(false);
    if (!result.ok) {
      setFailure(result.reason);
      return;
    }
    setSaved(true);
    onSaved?.();
  };

  return (
    <div className={layout.stack} data-testid="today-evening-gratitude">
      {saved ? (
        <DsCallout tone="insight" label="emotions" icon="heart" title={copy.eveningGratitudeSaved} testId="today-evening-gratitude-saved" />
      ) : (
        <DsCaption>{copy.eveningGratitudeLead}</DsCaption>
      )}
      <DsListPanel tone="glass" testId="today-evening-gratitude-categories">
        {EVENING_GRATITUDE_CATEGORIES.map((row) => {
          const selected = categories.includes(row.id);
          return (
            <DsListRow
              key={row.id}
              testId={`today-evening-gratitude-${row.id}`}
              title={row.label}
              subtitle={selected ? copy.eveningGratitudePicked : undefined}
              onClick={() => toggle(row.id)}
            />
          );
        })}
      </DsListPanel>
      <DsTextField
        label={copy.eveningGratitudeOwn}
        value={text}
        onChange={(next) => {
          setSaved(false);
          setFailure(null);
          setText(next);
        }}
        placeholder={copy.eveningGratitudePlaceholder}
        data-testid="today-evening-gratitude-text"
      />
      {failure ? (
        <p data-testid="today-evening-gratitude-error">
          <DsCaption>{todaySlotFailureCopy(failure)}</DsCaption>
        </p>
      ) : null}
      <DsButton
        type="button"
        variant="primary"
        disabled={!canSave || saving}
        data-testid="today-evening-gratitude-save"
        onClick={() => void onSave()}
      >
        {saved ? copy.eveningGratitudeSaved : copy.eveningGratitudeSave}
      </DsButton>
    </div>
  );
}
