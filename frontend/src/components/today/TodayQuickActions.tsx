"use client";

import { useEffect, useState } from "react";
import { getJson, postJson } from "@/lib/api";
import { useToast } from "@/components/ToastProvider";
import { useMeaningRuntime } from "@/hooks/useMeaningRuntime";
import { RITUAL_COPY } from "@/components/today/todayRitualCopy";

export type StateCheckPhase = "morning" | "day" | "evening";

type StateCheckInRow = {
  id: number;
  checkin_date: string;
  phase: string;
  mood_scale: number | null;
  energy_scale: number | null;
  stress_scale: number | null;
  note: string | null;
  tags: unknown;
  updated_at: string;
};

export function PhaseStateCheckIn({
  date,
  phase,
  title,
  hint,
  onSaved,
}: {
  date: string;
  phase: StateCheckPhase;
  title: string;
  hint?: string;
  onSaved?: () => void;
}) {
  const toast = useToast();
  const [moodScale, setMoodScale] = useState<number | null>(null);
  const [energyScale, setEnergyScale] = useState<number | null>(null);
  const [stressScale, setStressScale] = useState<number | null>(null);
  const [note, setNote] = useState("");
  const [saving, setSaving] = useState(false);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    let cancelled = false;
    getJson<StateCheckInRow[]>(`/tracking/state-check-in/${date}`)
      .then((rows) => {
        if (cancelled) return;
        const row = rows.find((r) => r.phase === phase);
        if (row) {
          setMoodScale(row.mood_scale ?? null);
          setEnergyScale(row.energy_scale ?? null);
          setStressScale(row.stress_scale ?? null);
          setNote(row.note || "");
        }
        setLoaded(true);
      })
      .catch(() => setLoaded(true));
    return () => {
      cancelled = true;
    };
  }, [date, phase]);

  const handleSave = async () => {
    if (moodScale === null && energyScale === null && stressScale === null && !note.trim()) {
      toast.error(RITUAL_COPY.quickStateCheckNeedScaleOrNote);
      return;
    }
    try {
      setSaving(true);
      await postJson(`/tracking/state-check-in/${date}`, {
        phase,
        mood_scale: moodScale,
        energy_scale: energyScale,
        stress_scale: stressScale,
        note: note.trim() || null,
      });
      toast.success(RITUAL_COPY.quickStateCheckSavedToast);
      onSaved?.();
    } catch (e) {
      console.error(e);
      toast.error(RITUAL_COPY.quickStateCheckSaveErrorToast);
    } finally {
      setSaving(false);
    }
  };

  if (!loaded) {
    return (
      <div className="orbit-body-xs" style={{ color: "#8a6f49", padding: "0.5rem 0" }}>
        {RITUAL_COPY.quickStateCheckLoading}
      </div>
    );
  }

  return (
    <div
      style={{
        padding: "var(--orbit-space-md)",
        background: "rgba(255, 252, 247, 0.96)",
        borderRadius: "12px",
        border: "1px solid rgba(202, 177, 137, 0.32)",
        marginBottom: "var(--orbit-space-md)",
      }}
    >
      <p className="orbit-body-sm" style={{ margin: 0, color: "#5f4323", fontWeight: 700 }}>
        {title}
      </p>
      {hint ? (
        <p className="orbit-body-xs" style={{ margin: "0.35rem 0 0", color: "#7a6242", lineHeight: 1.55 }}>
          {hint}
        </p>
      ) : null}
      <div style={{ marginTop: "0.65rem" }}>
        <p className="orbit-body-xs" style={{ margin: "0 0 0.35rem", color: "#8a6f49", fontWeight: 600 }}>
          {RITUAL_COPY.quickStateCheckMoodLabel}
        </p>
        <div style={{ display: "flex", gap: "0.35rem", flexWrap: "wrap" }}>
          {[1, 2, 3, 4, 5].map((n) => (
            <button
              key={n}
              type="button"
              className={`orbit-button orbit-button-sm ${moodScale === n ? "orbit-button-primary" : "orbit-button-secondary"}`}
              onClick={() => setMoodScale(n)}
            >
              {n}
            </button>
          ))}
        </div>
      </div>
      <div style={{ marginTop: "0.65rem" }}>
        <p className="orbit-body-xs" style={{ margin: "0 0 0.35rem", color: "#8a6f49", fontWeight: 600 }}>
          {RITUAL_COPY.quickStateCheckEnergyLabel}
        </p>
        <div style={{ display: "flex", gap: "0.35rem", flexWrap: "wrap" }}>
          {[1, 2, 3, 4, 5].map((n) => (
            <button
              key={n}
              type="button"
              className={`orbit-button orbit-button-sm ${energyScale === n ? "orbit-button-primary" : "orbit-button-secondary"}`}
              onClick={() => setEnergyScale(n)}
            >
              {n}
            </button>
          ))}
        </div>
      </div>
      <div style={{ marginTop: "0.65rem" }}>
        <p className="orbit-body-xs" style={{ margin: "0 0 0.35rem", color: "#8a6f49", fontWeight: 600 }}>
          {RITUAL_COPY.quickStateCheckStressLabel}
        </p>
        <div style={{ display: "flex", gap: "0.35rem", flexWrap: "wrap" }}>
          {[1, 2, 3, 4, 5].map((n) => (
            <button
              key={n}
              type="button"
              className={`orbit-button orbit-button-sm ${stressScale === n ? "orbit-button-primary" : "orbit-button-secondary"}`}
              onClick={() => setStressScale(n)}
            >
              {n}
            </button>
          ))}
        </div>
      </div>
      <textarea
        value={note}
        onChange={(e) => setNote(e.target.value)}
        placeholder={RITUAL_COPY.quickStateCheckNotePlaceholder}
        style={{
          width: "100%",
          minHeight: "56px",
          marginTop: "0.65rem",
          padding: "var(--orbit-space-sm)",
          borderRadius: "8px",
          border: "1px solid #e0e0e0",
          fontFamily: "inherit",
          fontSize: "0.9rem",
        }}
      />
      <button
        type="button"
        className="orbit-button orbit-button-primary orbit-button-sm"
        style={{ marginTop: "0.65rem", width: "100%" }}
        disabled={saving}
        onClick={() => void handleSave()}
      >
        {saving ? RITUAL_COPY.quickStateCheckSavingCta : RITUAL_COPY.quickStateCheckSaveCta}
      </button>
    </div>
  );
}

export function QuickJournalEntry({ date, onEntryCreated }: { date: string; onEntryCreated: () => void }) {
  const toast = useToast();
  const { trackMeaningEvent } = useMeaningRuntime();
  const [showForm, setShowForm] = useState(false);
  const [entryType, setEntryType] = useState<"observation" | "gratitude" | "insight">("observation");
  const [content, setContent] = useState("");
  const [saving, setSaving] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!content.trim()) return;

    try {
      setSaving(true);
      await postJson("/journal/entries", {
        type: entryType,
        content: content.trim(),
        day: date,
      });
      trackMeaningEvent({
        event_type: "diary_entry",
        event_source: "today",
        local_date: date,
        payload: { entry_type: entryType, source: "quick_journal_entry" },
      });
      setContent("");
      setShowForm(false);
      onEntryCreated();
    } catch (err) {
      console.error("Error creating journal entry:", err);
      toast.error(RITUAL_COPY.quickJournalEntryErrorToast);
    } finally {
      setSaving(false);
    }
  };

  if (!showForm) {
    return (
      <button onClick={() => setShowForm(true)} className="orbit-button orbit-button-secondary" style={{ width: "100%", marginBottom: "var(--orbit-space-sm)" }}>
        {RITUAL_COPY.quickJournalOpenCta}
      </button>
    );
  }

  return (
    <div
      style={{
        padding: "var(--orbit-space-md)",
        background: "#f8f9fa",
        borderRadius: "8px",
        marginBottom: "var(--orbit-space-sm)",
      }}
    >
      <div style={{ display: "flex", gap: "var(--orbit-space-xs)", marginBottom: "var(--orbit-space-sm)" }}>
        {(["observation", "gratitude", "insight"] as const).map((type) => (
          <button
            key={type}
            onClick={() => setEntryType(type)}
            className={`orbit-button orbit-button-sm ${entryType === type ? "orbit-button-primary" : "orbit-button-secondary"}`}
            style={{ flex: 1 }}
          >
            {type === "observation"
              ? RITUAL_COPY.quickJournalTabObservation
              : type === "gratitude"
                ? RITUAL_COPY.quickJournalTabGratitude
                : RITUAL_COPY.quickJournalTabInsight}
          </button>
        ))}
      </div>
      <form onSubmit={handleSubmit}>
        <textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder={
            entryType === "observation"
              ? RITUAL_COPY.quickJournalPlaceholderObservation
              : entryType === "gratitude"
                ? RITUAL_COPY.quickJournalPlaceholderGratitude
                : RITUAL_COPY.quickJournalPlaceholderInsight
          }
          style={{
            width: "100%",
            minHeight: "80px",
            padding: "var(--orbit-space-sm)",
            borderRadius: "6px",
            border: "1px solid #e0e0e0",
            fontFamily: "inherit",
            fontSize: "0.9375rem",
            resize: "vertical",
            marginBottom: "var(--orbit-space-sm)",
          }}
          autoFocus
        />
        <div style={{ display: "flex", gap: "var(--orbit-space-sm)" }}>
          <button type="submit" disabled={saving || !content.trim()} className="orbit-button orbit-button-primary orbit-button-sm" style={{ flex: 1 }}>
            {saving ? RITUAL_COPY.formSavingShort : RITUAL_COPY.formSaveCta}
          </button>
          <button
            type="button"
            onClick={() => {
              setShowForm(false);
              setContent("");
            }}
            className="orbit-button orbit-button-secondary orbit-button-sm"
          >
            {RITUAL_COPY.formCancelCta}
          </button>
        </div>
      </form>
    </div>
  );
}

export function QuickStateTracker({ date, onTrackerCreated }: { date: string; onTrackerCreated: () => void }) {
  const toast = useToast();
  const [showForm, setShowForm] = useState(false);
  const [state, setState] = useState("");
  const [stateScale, setStateScale] = useState<number | null>(null);
  const [saving, setSaving] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!state.trim() && stateScale === null) return;

    try {
      setSaving(true);
      await postJson("/tracking/progress", {
        date,
        state: state.trim() || null,
        state_scale: stateScale,
        completed: true,
      });
      setState("");
      setStateScale(null);
      setShowForm(false);
      onTrackerCreated();
    } catch (err) {
      console.error("Error creating state tracker:", err);
      toast.error(RITUAL_COPY.quickTrackerEntryErrorToast);
    } finally {
      setSaving(false);
    }
  };

  if (!showForm) {
    return (
      <button onClick={() => setShowForm(true)} className="orbit-button orbit-button-secondary" style={{ width: "100%", marginBottom: "var(--orbit-space-sm)" }}>
        {RITUAL_COPY.quickTrackerOpenCta}
      </button>
    );
  }

  return (
    <div
      style={{
        padding: "var(--orbit-space-md)",
        background: "#f8f9fa",
        borderRadius: "8px",
        marginBottom: "var(--orbit-space-sm)",
      }}
    >
      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: "var(--orbit-space-sm)" }}>
          <p className="orbit-body-sm" style={{ marginBottom: "var(--orbit-space-xs)" }}>
            {RITUAL_COPY.quickTrackerHowYouFeelPrompt}
          </p>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: "var(--orbit-space-xs)", marginBottom: "var(--orbit-space-sm)" }}>
            {[1, 2, 3, 4, 5].map((num) => (
              <button
                key={num}
                type="button"
                onClick={() => setStateScale(num)}
                className={`orbit-button orbit-button-sm ${stateScale === num ? "orbit-button-primary" : "orbit-button-secondary"}`}
              >
                {num}
              </button>
            ))}
          </div>
        </div>

        <textarea
          value={state}
          onChange={(e) => setState(e.target.value)}
          placeholder={RITUAL_COPY.quickTrackerNotePlaceholder}
          style={{
            width: "100%",
            minHeight: "60px",
            padding: "var(--orbit-space-sm)",
            borderRadius: "6px",
            border: "1px solid #e0e0e0",
            fontFamily: "inherit",
            fontSize: "0.9375rem",
            resize: "vertical",
            marginBottom: "var(--orbit-space-sm)",
          }}
        />

        <div style={{ display: "flex", gap: "var(--orbit-space-sm)" }}>
          <button type="submit" disabled={saving || (!state.trim() && stateScale === null)} className="orbit-button orbit-button-primary orbit-button-sm" style={{ flex: 1 }}>
            {saving ? RITUAL_COPY.formSavingShort : RITUAL_COPY.formSaveCta}
          </button>
          <button
            type="button"
            onClick={() => {
              setShowForm(false);
              setState("");
              setStateScale(null);
            }}
            className="orbit-button orbit-button-secondary orbit-button-sm"
          >
            {RITUAL_COPY.formCancelCta}
          </button>
        </div>
      </form>
    </div>
  );
}
