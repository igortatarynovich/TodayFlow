"use client";

import { Suspense, useState, useEffect, useMemo } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { DsBody, DsButton } from "@/design-system";
import { ProductPageScreen } from "@/components/product-ui/ProductPageScreen";
import pl from "@/design-system/layouts/productPageLayout.module.css";
import v2 from "@/design-system/layouts/productV2Surface.module.css";
import {
  flowTrackerChromeBundle,
  type FlowPracticesChromeLocale,
} from "@/components/today/flowPracticesMainTabChrome";
import { getJson, postJson } from "@/lib/api";
import { getLocale } from "@/lib/i18n";
import { useToast } from "@/components/ToastProvider";
import { useAuth } from "@/lib/useAuth";

function tpl(s: string, vars: Record<string, string | number>) {
  return s.replace(/\{\{(\w+)\}\}/g, (_, k) => String(vars[k] ?? ""));
}

function parseDateParam(v: string | null): string | null {
  if (!v || !/^\d{4}-\d{2}-\d{2}$/.test(v)) return null;
  const d = new Date(v + "T12:00:00");
  return isNaN(d.getTime()) ? null : v;
}

type ProgressEntry = {
  id: number;
  date: string;
  asceticism_id: string | null;
  affirmation_id: string | null;
  completed: boolean;
  state: string | null;
  state_scale: number | null;
  note: string | null;
  created_at: string;
  updated_at: string;
};

type Affirmation = {
  id: string;
  text: string;
  title?: string;
};

function AffirmationsTrackerContent() {
  const searchParams = useSearchParams();
  const dateParam = parseDateParam(searchParams.get("date"));
  const locale: FlowPracticesChromeLocale = getLocale() === "ru" ? "ru" : "en";
  const fc = useMemo(() => flowTrackerChromeBundle(locale), [locale]);
  const dateLocaleTag = locale === "ru" ? "ru-RU" : "en-US";

  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const toast = useToast();
  const [loading, setLoading] = useState(true);
  const [entries, setEntries] = useState<ProgressEntry[]>([]);
  const [affirmations, setAffirmations] = useState<Affirmation[]>([]);
  const [selectedDate, setSelectedDate] = useState(dateParam ?? new Date().toISOString().split("T")[0]);
  const [selectedAffirmation, setSelectedAffirmation] = useState<string>("");
  const [completed, setCompleted] = useState(false);
  const [state, setState] = useState<string>("");
  const [stateScale, setStateScale] = useState<number | null>(null);
  const [note, setNote] = useState<string>("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (!isAuthenticated) return;

    const loadData = async () => {
      try {
        setLoading(true);
        const [entriesData, affirmationsData] = await Promise.all([
          getJson<ProgressEntry[]>(
            `/tracking/progress?from_date=${selectedDate}&to_date=${selectedDate}`,
          ),
          getJson<Affirmation[]>("/practices/affirmations"),
        ]);
        const affirmationOnly = (entriesData || []).filter((e) => e.affirmation_id != null);
        setEntries(affirmationOnly);
        setAffirmations(affirmationsData || []);
      } catch (err) {
        console.error("Error loading affirmations tracker:", err);
        setEntries([]);
        setAffirmations([]);
      } finally {
        setLoading(false);
      }
    };

    void loadData();
  }, [isAuthenticated, selectedDate]);

  const handleSave = async () => {
    if (!selectedAffirmation) {
      toast.error(fc.affirmationsTrackerToastPickAffirmation);
      return;
    }

    try {
      setSaving(true);
      await postJson("/tracking/progress", {
        date: selectedDate,
        asceticism_id: null,
        affirmation_id: selectedAffirmation,
        completed,
        state: state || null,
        state_scale: stateScale ?? null,
        note: note || null,
      });

      const entriesData = await getJson<ProgressEntry[]>(
        `/tracking/progress?from_date=${selectedDate}&to_date=${selectedDate}`,
      );
      const affirmationOnly = (entriesData || []).filter((e) => e.affirmation_id != null);
      setEntries(affirmationOnly);

      setSelectedAffirmation("");
      setCompleted(false);
      setState("");
      setStateScale(null);
      setNote("");
    } catch (err) {
      console.error("Error saving entry:", err);
      toast.error(fc.trackingDiarySaveError);
    } finally {
      setSaving(false);
    }
  };

  const entriesHeadingDate = useMemo(
    () => new Date(selectedDate + "T12:00:00").toLocaleDateString(dateLocaleTag),
    [selectedDate, dateLocaleTag],
  );

  if (authLoading || loading) {
    return (
      <ProductPageScreen
        testId="affirmations-tracker-page"
        title={fc.affirmationsLibraryLinkTracker}
        loading
        loadingLabel={fc.saveDiarySaving}
      />
    );
  }

  if (!isAuthenticated) {
    return (
      <ProductPageScreen
        testId="affirmations-tracker-page"
        title={fc.affirmationsLibraryLinkTracker}
        guest={{
          message: fc.affirmationsTrackerLoginPrompt,
          ctaHref: "/auth?redirect=/affirmations/tracker",
          ctaLabel: fc.trackingProgressHubLoginCta,
        }}
      />
    );
  }

  const textById = Object.fromEntries(affirmations.map((a) => [a.id, a.text || a.title || a.id]));

  return (
    <ProductPageScreen
      testId="affirmations-tracker-page"
      title={fc.affirmationsLibraryLinkTracker}
      subtitle={fc.affirmationsTrackerPageLead}
      contentClassName={pl.content}
    >
      <Link href="/affirmations" className={pl.textLink}>
        {fc.affirmationsTrackerBackToCatalog}
      </Link>

      <div className={pl.fieldRow}>
        <label className={pl.fieldLabel} htmlFor="affirmations-tracker-date">
          {fc.trackingFormDateLabel}
        </label>
        <input
          id="affirmations-tracker-date"
          type="date"
          value={selectedDate}
          onChange={(e) => setSelectedDate(e.target.value)}
          className={pl.fieldInput}
          style={{ maxWidth: "18rem" }}
        />
      </div>

      <section className={pl.panel}>
        <h2 className={v2.sectionTitle}>{fc.affirmationsTrackerNewEntryTitle}</h2>
        <div className={pl.formStack} style={{ marginTop: "1rem" }}>
          <div className={pl.fieldRow}>
            <label className={pl.fieldLabel} htmlFor="affirmations-tracker-select">
              {fc.affirmationsTrackerSelectLabel}
            </label>
            <select
              id="affirmations-tracker-select"
              value={selectedAffirmation}
              onChange={(e) => setSelectedAffirmation(e.target.value)}
              className={pl.fieldInput}
            >
              <option value="">{fc.affirmationsTrackerSelectPlaceholder}</option>
              {affirmations.map((a) => (
                <option key={a.id} value={a.id}>
                  {a.text || a.title || a.id}
                </option>
              ))}
            </select>
          </div>

          <label style={{ display: "flex", alignItems: "center", gap: "0.5rem", cursor: "pointer" }}>
            <input type="checkbox" checked={completed} onChange={(e) => setCompleted(e.target.checked)} />
            <span className={pl.fieldLabel} style={{ margin: 0 }}>
              {fc.affirmationsTrackerUsedLabel}
            </span>
          </label>

          <div className={pl.fieldRow}>
            <label className={pl.fieldLabel} htmlFor="affirmations-tracker-state">
              {fc.affirmationsTrackerStateLabel}
            </label>
            <input
              id="affirmations-tracker-state"
              type="text"
              value={state}
              onChange={(e) => setState(e.target.value)}
              placeholder={fc.affirmationsTrackerStatePlaceholder}
              className={pl.fieldInput}
            />
          </div>

          <div className={pl.fieldRow}>
            <label className={pl.fieldLabel} htmlFor="affirmations-tracker-scale">
              {fc.affirmationsTrackerScaleLabel}
            </label>
            <input
              id="affirmations-tracker-scale"
              type="number"
              min={1}
              max={5}
              value={stateScale ?? ""}
              onChange={(e) => setStateScale(e.target.value ? parseInt(e.target.value, 10) : null)}
              className={pl.fieldInput}
              style={{ maxWidth: "9rem" }}
            />
          </div>

          <div className={pl.fieldRow}>
            <label className={pl.fieldLabel} htmlFor="affirmations-tracker-note">
              {fc.affirmationsTrackerNoteLabel}
            </label>
            <textarea
              id="affirmations-tracker-note"
              value={note}
              onChange={(e) => setNote(e.target.value)}
              placeholder={fc.affirmationsTrackerNotePlaceholder}
              rows={3}
              className={pl.fieldInput}
            />
          </div>

          <DsButton onClick={handleSave} disabled={saving}>
            {saving ? fc.saveDiarySaving : fc.actionSave}
          </DsButton>
        </div>
      </section>

      <section className={pl.panel}>
        <h2 className={v2.sectionTitle}>
          {tpl(fc.trackingDiaryEntriesHeading, { date: entriesHeadingDate })}
        </h2>
        {entries.length === 0 ? (
          <DsBody size="sm" className={pl.bodyMtSm}>
            {fc.affirmationsTrackerNoEntriesForDate}
          </DsBody>
        ) : (
          <div className={pl.formStack} style={{ marginTop: "1rem" }}>
            {entries.map((entry) => (
              <article key={entry.id} className={pl.hubCard}>
                <div className={pl.flexRowCenter} style={{ justifyContent: "space-between", alignItems: "flex-start" }}>
                  <span className={pl.hubCardTitle}>
                    {entry.affirmation_id ? textById[entry.affirmation_id] ?? entry.affirmation_id : "—"}
                  </span>
                  <DsBody size="sm" muted>
                    {entry.completed ? fc.affirmationsTrackerEntryUsed : fc.affirmationsTrackerEntryNotUsed}
                  </DsBody>
                </div>
                {entry.state && (
                  <DsBody size="sm" className={pl.bodyMtXs} muted>
                    {fc.affirmationsTrackerEntryStateLabel} {entry.state}
                    {entry.state_scale != null ? ` (${entry.state_scale}/5)` : ""}
                  </DsBody>
                )}
                {entry.note && (
                  <DsBody size="sm" className={`${pl.bodyMtXs} ${pl.bodyItalic}`} muted>
                    {entry.note}
                  </DsBody>
                )}
              </article>
            ))}
          </div>
        )}
      </section>

      <Link href="/flow" className={pl.textLink}>
        {fc.affirmationsTrackerBackToAllTrackers}
      </Link>
    </ProductPageScreen>
  );
}

export default function AffirmationsTrackerPage() {
  return (
    <Suspense
      fallback={
        <ProductPageScreen
          testId="affirmations-tracker-page"
          title="Affirmations"
          loading
          loadingLabel="…"
        />
      }
    >
      <AffirmationsTrackerContent />
    </Suspense>
  );
}
