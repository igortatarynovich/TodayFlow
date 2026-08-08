"use client";

import { DsButton } from "@/design-system";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useMemo, useState } from "react";
import { LoadingSpinner } from "@/components/orbit";
import { CityAutocompleteInput } from "@/components/CityAutocompleteInput";
import { RELATIONSHIP_CONTEXT_OPTIONS, type RelationshipContextId } from "@/lib/compatibilityRelationshipContext";
import {
  buildCompatibilityCheckKey,
  canGuestAccessCompatibility,
  guestCompatibilityRemaining,
  isGuestCompatibilityLimitReached,
} from "@/lib/guestAccessStore";
import { GuestAccessLimitGate } from "@/components/guest/GuestAccessLimitGate";
import { GUEST_ACCESS_COPY } from "@/components/guest/guestAccessCopy";
import { ProductPageScreen } from "@/components/product-ui/ProductPageScreen";
import pl from "@/design-system/layouts/productPageLayout.module.css";

type PersonForm = {
  label: string;
  date: string;
  time: string;
  location: string;
  timeUnknown: boolean;
};

function readinessLabel(withTime: number, withCities: number) {
  if (withTime === 2 && withCities >= 1) return "Достаточно данных для точного слоя.";
  if (withTime >= 1 || withCities >= 1) return "Можно открыть разбор.";
  return "Нужны две даты.";
}

function PersonCard({
  title,
  form,
  setForm,
}: {
  title: string;
  form: PersonForm;
  setForm: (updater: PersonForm) => void;
}) {
  return (
    <section className="compat-desktop-card" style={{ display: "grid", gap: "0.85rem" }}>
      <p className="compat-section-kicker" style={{ marginBottom: 0 }}>
        {title}
      </p>

      <label className="compat-field">
        <span className="orbit-body-sm">Имя или подпись</span>
        <input
          type="text"
          value={form.label}
          onChange={(event) => setForm({ ...form, label: event.target.value })}
          placeholder="Например: Я, Партнер, Анна"
        />
      </label>

      <label className="compat-field">
        <span className="orbit-body-sm">Дата рождения</span>
        <input
          type="date"
          value={form.date}
          onChange={(event) => setForm({ ...form, date: event.target.value })}
          required
        />
      </label>

      <div style={{ display: "grid", gap: "0.6rem" }}>
        <label className="compat-field">
          <span className="orbit-body-sm">Время рождения</span>
          <input
            type="time"
            value={form.time}
            onChange={(event) => setForm({ ...form, time: event.target.value })}
            disabled={form.timeUnknown}
          />
        </label>
        <label className="compat-field-check">
          <input
            type="checkbox"
            checked={form.timeUnknown}
            onChange={(event) =>
              setForm({
                ...form,
                timeUnknown: event.target.checked,
                time: event.target.checked ? "" : form.time,
              })
            }
          />
          <span className="orbit-body-sm">Точное время неизвестно</span>
        </label>
      </div>

      <div className="compat-field">
        <span className="orbit-body-sm">Город рождения</span>
        <CityAutocompleteInput
          value={form.location}
          onChange={(value) => setForm({ ...form, location: value })}
          onSelect={(item) => setForm({ ...form, location: item.display_name || item.local_name || item.name })}
          placeholder="Варшава, Москва, New York"
        />
      </div>
    </section>
  );
}

function PairReadiness({
  form1,
  form2,
  precisionNote,
}: {
  form1: PersonForm;
  form2: PersonForm;
  precisionNote: string;
}) {
  const people = [
    { title: "Ты", label: form1.label || "Без подписи", date: form1.date },
    { title: "Партнёр", label: form2.label || "Без подписи", date: form2.date },
  ];

  return (
    <div className="compat-readiness">
      <div className="compat-readiness-row">
        {people.map((person) => (
          <div
            key={person.title}
            className={person.date ? "compat-readiness-chip" : "compat-readiness-chip is-empty"}
          >
            <p className="compat-section-kicker" style={{ marginBottom: 0 }}>
              {person.title}
            </p>
            <p className="orbit-body-sm" style={{ margin: "0.18rem 0 0", fontWeight: 700, color: "var(--tf-ink)" }}>
              {person.label}
            </p>
            <p className="orbit-body-xs" style={{ margin: "0.22rem 0 0", color: "var(--tf-caption)" }}>
              {person.date || "Дата не выбрана"}
            </p>
          </div>
        ))}
      </div>
      <p className="compat-section-lead" style={{ marginBottom: 0 }}>
        {precisionNote}
      </p>
    </div>
  );
}

export default function CompatibilityBirthdatesPage() {
  const router = useRouter();
  const [form1, setForm1] = useState<PersonForm>({
    label: "Я",
    date: "",
    time: "",
    location: "",
    timeUnknown: false,
  });
  const [form2, setForm2] = useState<PersonForm>({
    label: "Партнёр",
    date: "",
    time: "",
    location: "",
    timeUnknown: false,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [relationshipContext, setRelationshipContext] = useState<RelationshipContextId | "">("");
  const [limitBlocked, setLimitBlocked] = useState(false);

  const canContinue = Boolean(form1.date && form2.date);
  const compatCheckKey = buildCompatibilityCheckKey({
    mode: "precise",
    birth_date_1: form1.date,
    birth_date_2: form2.date,
    relationship_context: relationshipContext || undefined,
  });
  const compatRemaining = guestCompatibilityRemaining();

  const precisionNote = useMemo(() => {
    const withTime = Number(Boolean(form1.time || form1.timeUnknown)) + Number(Boolean(form2.time || form2.timeUnknown));
    const withCities = Number(Boolean(form1.location)) + Number(Boolean(form2.location));
    return readinessLabel(withTime, withCities);
  }, [form1.time, form1.timeUnknown, form1.location, form2.time, form2.timeUnknown, form2.location]);

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    if (!canContinue) {
      setError("Нужно заполнить обе даты рождения.");
      return;
    }

    if (isGuestCompatibilityLimitReached() && !canGuestAccessCompatibility(compatCheckKey)) {
      setLimitBlocked(true);
      return;
    }

    setLoading(true);
    setError(null);

    const ctxPart = relationshipContext ? `&ctx=${encodeURIComponent(relationshipContext)}` : "";
    router.push(
      `/compatibility/birthdates/result?date1=${encodeURIComponent(form1.date)}&date2=${encodeURIComponent(form2.date)}&time1=${encodeURIComponent(form1.time || "")}&time2=${encodeURIComponent(form2.time || "")}&loc1=${encodeURIComponent(form1.location)}&loc2=${encodeURIComponent(form2.location)}&label1=${encodeURIComponent(form1.label || "Я")}&label2=${encodeURIComponent(form2.label || "Партнёр")}${ctxPart}`,
    );
  };

  return (
    <ProductPageScreen
      testId="compat-birthdates-page"
      title="Совместимость по датам"
      subtitle="Две даты — тон пары и зоны напряжения. Время и город уточняют слой."
      quietHeader
      mainWide
      contentClassName={pl.content}
    >
      {limitBlocked ? (
        <section className="compat-flow-section">
          <GuestAccessLimitGate
            title={GUEST_ACCESS_COPY.compatLimitTitle}
            body={GUEST_ACCESS_COPY.compatLimitBody}
            secondaryHref="/compatibility"
            secondaryLabel="← К совместимости"
            testId="guest-compat-birthdates-limit"
          />
        </section>
      ) : (
        <section className="compat-flow-section">
          <form onSubmit={handleSubmit} className="compat-desktop-shell compat-desktop-stack">
            <div className="compat-analyze-topbar">
              <Link href="/compatibility" className="compat-analyze-back">
                ← Все уровни
              </Link>
              <div style={{ display: "flex", gap: "0.65rem", flexWrap: "wrap", alignItems: "center" }}>
                <Link href="/compatibility/analyze" className="compat-analyze-back">
                  Единый экран
                </Link>
                <Link href="/compatibility/signs" className="compat-analyze-back">
                  По знакам →
                </Link>
              </div>
            </div>

            <PairReadiness form1={form1} form2={form2} precisionNote={precisionNote} />

            {compatRemaining < 4 ? (
              <p className="compat-section-lead" style={{ marginBottom: 0 }}>
                {GUEST_ACCESS_COPY.remainingCompat(compatRemaining)}
              </p>
            ) : null}

            <div className="compat-form-grid">
              <PersonCard title="Твои данные" form={form1} setForm={setForm1} />
              <PersonCard title="Данные партнёра" form={form2} setForm={setForm2} />
            </div>

            <section className="compat-desktop-section">
              <p className="compat-section-kicker">Что сейчас между вами?</p>
              <p className="compat-section-lead">
                Необязательно, но сильно улучшает персонализацию разбора и советов.
              </p>
              <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem" }}>
                {RELATIONSHIP_CONTEXT_OPTIONS.map((opt) => {
                  const active = relationshipContext === opt.id;
                  return (
                    <button
                      key={opt.id}
                      type="button"
                      className={active ? "compat-chip is-active" : "compat-chip"}
                      onClick={() => setRelationshipContext(active ? "" : opt.id)}
                      style={{ textAlign: "left" }}
                    >
                      {opt.label}
                    </button>
                  );
                })}
              </div>
            </section>

            <div className="compat-actions-stack">
              <DsButton
                type="submit"
                variant="primary"
                size="block"
                disabled={!canContinue || loading}
                style={{ opacity: canContinue && !loading ? 1 : 0.56 }}
              >
                {loading ? <LoadingSpinner size="sm" /> : canContinue ? "Разбор" : "Две даты"}
              </DsButton>
              <DsButton href="/compatibility" variant="secondary">
                Совместимость по профилям
              </DsButton>
              <Link href="/compatibility/signs" className="compat-analyze-back" style={{ textAlign: "center" }}>
                К знакам
              </Link>
              {error ? <p className="compat-inline-error">{error}</p> : null}
            </div>
          </form>
        </section>
      )}
    </ProductPageScreen>
  );
}
