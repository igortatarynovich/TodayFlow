"use client";

import { Suspense, useState, useEffect } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { DsBody, DsButton } from "@/design-system";
import { ProductPageScreen } from "@/components/product-ui/ProductPageScreen";
import pl from "@/design-system/layouts/productPageLayout.module.css";
import v2 from "@/design-system/layouts/productV2Surface.module.css";
import { useAuth } from "@/lib/useAuth";
import { getJson, postJson } from "@/lib/api";
import { useToast } from "@/components/ToastProvider";

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

type Asceticism = {
  id: string;
  title: string;
  description: string;
};

function AsceticismsTrackerContent() {
  const searchParams = useSearchParams();
  const dateParam = parseDateParam(searchParams.get("date"));
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const toast = useToast();
  const [loading, setLoading] = useState(true);
  const [entries, setEntries] = useState<ProgressEntry[]>([]);
  const [asceticisms, setAsceticisms] = useState<Asceticism[]>([]);
  const [selectedDate, setSelectedDate] = useState(dateParam ?? new Date().toISOString().split("T")[0]);
  const [selectedAsceticism, setSelectedAsceticism] = useState<string>("");
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
        const [entriesData, asceticismsData] = await Promise.all([
          getJson<ProgressEntry[]>(`/tracking/progress?from_date=${selectedDate}&to_date=${selectedDate}`),
          getJson<Asceticism[]>("/practices/asceticisms"),
        ]);
        const asceticismOnly = (entriesData || []).filter((e) => e.asceticism_id != null);
        setEntries(asceticismOnly);
        setAsceticisms(asceticismsData || []);
      } catch (err) {
        console.error("Error loading asceticisms tracker:", err);
        setEntries([]);
        setAsceticisms([]);
      } finally {
        setLoading(false);
      }
    };

    void loadData();
  }, [isAuthenticated, selectedDate]);

  const handleSave = async () => {
    if (!selectedAsceticism) {
      toast.error("Выберите аскезу");
      return;
    }

    try {
      setSaving(true);
      await postJson("/tracking/progress", {
        date: selectedDate,
        asceticism_id: selectedAsceticism,
        affirmation_id: null,
        completed,
        state: state || null,
        state_scale: stateScale ?? null,
        note: note || null,
      });

      const entriesData = await getJson<ProgressEntry[]>(
        `/tracking/progress?from_date=${selectedDate}&to_date=${selectedDate}`,
      );
      const asceticismOnly = (entriesData || []).filter((e) => e.asceticism_id != null);
      setEntries(asceticismOnly);

      setSelectedAsceticism("");
      setCompleted(false);
      setState("");
      setStateScale(null);
      setNote("");
    } catch (err) {
      console.error("Error saving entry:", err);
      toast.error("Ошибка при сохранении");
    } finally {
      setSaving(false);
    }
  };

  if (authLoading || loading) {
    return (
      <ProductPageScreen
        testId="asceticisms-tracker-page"
        title="Карта аскез"
        loading
        loadingLabel="Загрузка…"
      />
    );
  }

  if (!isAuthenticated) {
    return (
      <ProductPageScreen
        testId="asceticisms-tracker-page"
        title="Карта аскез"
        guest={{
          message: "Войдите, чтобы открыть карту аскез.",
          ctaHref: "/auth?redirect=/asceticisms/tracker",
          ctaLabel: "Войти",
        }}
      />
    );
  }

  const titleById = Object.fromEntries(asceticisms.map((a) => [a.id, a.title]));

  return (
    <ProductPageScreen
      testId="asceticisms-tracker-page"
      title="Карта аскез"
      subtitle="Осознанные ограничения — история дня за днём. Выбери аскезу и отметь, как прошёл этот день на карте."
      contentClassName={pl.content}
    >
      <Link href="/asceticisms" className={pl.textLink}>
        ← Каталог аскез
      </Link>

      <div className={pl.fieldRow}>
        <label className={pl.fieldLabel} htmlFor="ascetic-tracker-date">
          Дата
        </label>
        <input
          id="ascetic-tracker-date"
          type="date"
          value={selectedDate}
          onChange={(e) => setSelectedDate(e.target.value)}
          className={pl.fieldInput}
          style={{ maxWidth: "18rem" }}
        />
      </div>

      <section className={pl.panel}>
        <h2 className={v2.sectionTitle}>Новая запись</h2>
        <div className={pl.formStack} style={{ marginTop: "1rem" }}>
          <div className={pl.fieldRow}>
            <label className={pl.fieldLabel} htmlFor="ascetic-tracker-select">
              Аскеза (осознанное ограничение)
            </label>
            <select
              id="ascetic-tracker-select"
              value={selectedAsceticism}
              onChange={(e) => setSelectedAsceticism(e.target.value)}
              className={pl.fieldInput}
            >
              <option value="">Выберите аскезу</option>
              {asceticisms.map((a) => (
                <option key={a.id} value={a.id}>
                  {a.title}
                </option>
              ))}
            </select>
          </div>

          <label style={{ display: "flex", alignItems: "center", gap: "0.5rem", cursor: "pointer" }}>
            <input type="checkbox" checked={completed} onChange={(e) => setCompleted(e.target.checked)} />
            <span className={pl.fieldLabel} style={{ margin: 0 }}>
              Выполнено
            </span>
          </label>

          <div className={pl.fieldRow}>
            <label className={pl.fieldLabel} htmlFor="ascetic-tracker-state">
              Состояние (1–2 слова)
            </label>
            <input
              id="ascetic-tracker-state"
              type="text"
              value={state}
              onChange={(e) => setState(e.target.value)}
              placeholder="например: спокойно, напряжённо"
              className={pl.fieldInput}
            />
          </div>

          <div className={pl.fieldRow}>
            <label className={pl.fieldLabel} htmlFor="ascetic-tracker-scale">
              Шкала состояния (1–5)
            </label>
            <input
              id="ascetic-tracker-scale"
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
            <label className={pl.fieldLabel} htmlFor="ascetic-tracker-note">
              Заметка (опционально)
            </label>
            <textarea
              id="ascetic-tracker-note"
              value={note}
              onChange={(e) => setNote(e.target.value)}
              placeholder="Короткая заметка…"
              rows={3}
              className={pl.fieldTextarea}
            />
          </div>

          <DsButton onClick={handleSave} disabled={saving}>
            {saving ? "Сохранение…" : "Сохранить"}
          </DsButton>
        </div>
      </section>

      <section className={pl.panel}>
        <h2 className={v2.sectionTitle}>
          Записи за {new Date(`${selectedDate}T12:00:00`).toLocaleDateString("ru-RU")}
        </h2>
        {entries.length === 0 ? (
          <DsBody size="sm" muted className={pl.bodyMtLg}>
            Нет записей за эту дату
          </DsBody>
        ) : (
          <div className={pl.formStack} style={{ marginTop: "0.75rem" }}>
            {entries.map((entry) => (
              <div key={entry.id} className={pl.panel} style={{ padding: "1rem" }}>
                <div style={{ display: "flex", justifyContent: "space-between", gap: "0.75rem", flexWrap: "wrap" }}>
                  <DsBody size="sm">
                    {entry.asceticism_id ? (titleById[entry.asceticism_id] ?? entry.asceticism_id) : "—"}
                  </DsBody>
                  <DsBody size="sm" muted>
                    {entry.completed ? "✓ День отмечен" : "○ Без отметки"}
                  </DsBody>
                </div>
                {entry.state ? (
                  <DsBody size="sm" muted className={pl.bodyMtSm}>
                    Состояние: {entry.state}
                    {entry.state_scale != null && ` (${entry.state_scale}/5)`}
                  </DsBody>
                ) : null}
                {entry.note ? (
                  <DsBody size="sm" muted className={`${pl.bodyMtSm} ${pl.bodyItalic}`}>
                    {entry.note}
                  </DsBody>
                ) : null}
              </div>
            ))}
          </div>
        )}
      </section>

      <Link href="/flow" className={pl.textLink}>
        ← Мои карты
      </Link>
    </ProductPageScreen>
  );
}

export default function AsceticismsTrackerPage() {
  return (
    <Suspense
      fallback={
        <ProductPageScreen testId="asceticisms-tracker-page" title="Карта аскез" loading />
      }
    >
      <AsceticismsTrackerContent />
    </Suspense>
  );
}
