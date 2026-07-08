"use client";

import { useState, useEffect, useMemo } from "react";
import { useAuth } from "@/lib/useAuth";
import { DsButton } from "@/design-system";
import { getJson, postJson } from "@/lib/api";
import { useToast } from "@/components/ToastProvider";
import { getLocale } from "@/lib/i18n";
import { flowTrackerChromeBundle } from "@/components/today/flowPracticesMainTabChrome";
import { ProductAuxWebScreen } from "@/components/product-ui/ProductAuxWebScreen";
import pl from "@/design-system/layouts/productPageLayout.module.css";
import v2 from "@/design-system/layouts/productV2Surface.module.css";

type DiaryEntry = {
  id: number;
  date: string;
  noticed: string;
  hardest: string;
  easier_than_expected: string;
  created_at: string;
  updated_at: string;
};

function tpl(s: string, vars: Record<string, string | number>): string {
  return s.replace(/\{\{(\w+)\}\}/g, (_, k) => String(vars[k] ?? ""));
}

export default function ObservationDiaryPage() {
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const toast = useToast();
  const [loading, setLoading] = useState(true);
  const [entries, setEntries] = useState<DiaryEntry[]>([]);
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split("T")[0]);
  const [whatNoticed, setWhatNoticed] = useState("");
  const [whereDifficult, setWhereDifficult] = useState("");
  const [whatEasier, setWhatEasier] = useState("");
  const [saving, setSaving] = useState(false);

  const locale = getLocale() === "ru" ? "ru" : "en";
  const fc = useMemo(() => flowTrackerChromeBundle(locale), [locale]);
  const dateLocaleTag = locale === "ru" ? "ru-RU" : "en-US";

  const entriesHeading = useMemo(
    () =>
      tpl(fc.trackingDiaryEntriesHeading, {
        date: new Date(`${selectedDate}T12:00:00`).toLocaleDateString(dateLocaleTag),
      }),
    [fc, selectedDate, dateLocaleTag],
  );

  useEffect(() => {
    if (!isAuthenticated) return;

    const loadEntries = async () => {
      try {
        setLoading(true);
        const data = await getJson<DiaryEntry[]>(`/tracking/diary?date=${selectedDate}`);
        setEntries(data);

        if (data.length > 0) {
          const entry = data[0];
          setWhatNoticed(entry.noticed || "");
          setWhereDifficult(entry.hardest || "");
          setWhatEasier(entry.easier_than_expected || "");
        } else {
          setWhatNoticed("");
          setWhereDifficult("");
          setWhatEasier("");
        }
      } catch (err) {
        console.error("Error loading entries:", err);
      } finally {
        setLoading(false);
      }
    };

    loadEntries();
  }, [isAuthenticated, selectedDate]);

  const handleSave = async () => {
    if (!whatNoticed && !whereDifficult && !whatEasier) {
      toast.error(fc.trackingDiaryFillAtLeastOne);
      return;
    }

    try {
      setSaving(true);
      await postJson("/tracking/diary", {
        date: selectedDate,
        noticed: whatNoticed || "",
        hardest: whereDifficult || "",
        easier_than_expected: whatEasier || "",
      });

      const data = await getJson<DiaryEntry[]>(`/tracking/diary?date=${selectedDate}`);
      setEntries(data);
    } catch (err) {
      console.error("Error saving entry:", err);
      toast.error(fc.trackingDiarySaveError);
    } finally {
      setSaving(false);
    }
  };

  if (authLoading || loading) {
    return <ProductAuxWebScreen title={fc.diaryTitle} loading loadingLabel={fc.trackingDiaryPageIntro} />;
  }

  if (!isAuthenticated) {
    return (
      <ProductAuxWebScreen
        title={fc.diaryTitle}
        guest={{
          message: fc.trackingDiaryLoginPrompt,
          ctaHref: "/auth?redirect=/tracking/diary",
          ctaLabel: locale === "ru" ? "Войти" : "Sign in",
        }}
      />
    );
  }

  return (
    <ProductAuxWebScreen
      testId="tracking-diary-page"
      title={fc.diaryTitle}
      subtitle={fc.trackingDiaryPageIntro}
      railTitle={locale === "ru" ? "Дневник наблюдений" : "Observation diary"}
      railHint={
        locale === "ru"
          ? "Три коротких поля — что заметил, где было сложно, что оказалось легче."
          : "Three short fields — noticed, hardest, easier than expected."
      }
    >
      <div className={pl.fieldRow}>
        <div style={{ flex: "1 1 12rem", maxWidth: "20rem" }}>
          <label className={pl.fieldLabel} htmlFor="diary-date">
            {fc.trackingFormDateLabel}
          </label>
          <input
            id="diary-date"
            type="date"
            className={pl.fieldInput}
            value={selectedDate}
            onChange={(e) => setSelectedDate(e.target.value)}
          />
        </div>
      </div>

      <section className={pl.panel}>
        <h2 className={v2.sectionTitle}>{fc.trackingDiaryEntryFormTitle}</h2>
        <div className={pl.formStack} style={{ marginTop: "1.25rem" }}>
          <div>
            <label className={pl.fieldLabel} htmlFor="diary-noticed">
              {fc.trackingDiaryNoticedFieldLabel}
            </label>
            <textarea
              id="diary-noticed"
              className={pl.fieldTextarea}
              value={whatNoticed}
              onChange={(e) => setWhatNoticed(e.target.value)}
              placeholder={fc.diaryNoticedPlaceholder}
              rows={3}
            />
          </div>

          <div>
            <label className={pl.fieldLabel} htmlFor="diary-hardest">
              {fc.trackingDiaryHardestFieldLabel}
            </label>
            <textarea
              id="diary-hardest"
              className={pl.fieldTextarea}
              value={whereDifficult}
              onChange={(e) => setWhereDifficult(e.target.value)}
              placeholder={fc.diaryHardestPlaceholder}
              rows={3}
            />
          </div>

          <div>
            <label className={pl.fieldLabel} htmlFor="diary-easier">
              {fc.trackingDiaryEasierFieldLabel}
            </label>
            <textarea
              id="diary-easier"
              className={pl.fieldTextarea}
              value={whatEasier}
              onChange={(e) => setWhatEasier(e.target.value)}
              placeholder={fc.diaryEasierPlaceholder}
              rows={3}
            />
          </div>

          <DsButton onClick={handleSave} disabled={saving}>
            {saving ? fc.saveDiarySaving : fc.actionSave}
          </DsButton>
        </div>
      </section>

      {entries.length > 0 ? (
        <section className={pl.panel}>
          <h2 className={v2.sectionTitle}>{entriesHeading}</h2>
          <div className={pl.formStack} style={{ marginTop: "1rem" }}>
            {entries.map((entry) => (
              <article key={entry.id}>
                {entry.noticed ? (
                  <div style={{ marginBottom: "1rem" }}>
                    <strong>{fc.trackingDiaryReadoutNoticed}</strong>
                    <p className={v2.bodyLead} style={{ marginTop: "0.5rem" }}>
                      {entry.noticed}
                    </p>
                  </div>
                ) : null}
                {entry.hardest ? (
                  <div style={{ marginBottom: "1rem" }}>
                    <strong>{fc.trackingDiaryReadoutHardest}</strong>
                    <p className={v2.bodyLead} style={{ marginTop: "0.5rem" }}>
                      {entry.hardest}
                    </p>
                  </div>
                ) : null}
                {entry.easier_than_expected ? (
                  <div>
                    <strong>{fc.trackingDiaryReadoutEasier}</strong>
                    <p className={v2.bodyLead} style={{ marginTop: "0.5rem" }}>
                      {entry.easier_than_expected}
                    </p>
                  </div>
                ) : null}
              </article>
            ))}
          </div>
        </section>
      ) : null}
    </ProductAuxWebScreen>
  );
}
