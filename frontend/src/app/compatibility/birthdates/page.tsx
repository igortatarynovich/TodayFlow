"use client";

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
      <div>
        <p className="orbit-body-xs" style={{ margin: 0, color: "#8b7355", textTransform: "uppercase", letterSpacing: "0.08em" }}>
          {title}
        </p>
      </div>

      <label style={{ display: "grid", gap: "0.35rem" }}>
        <span className="orbit-body-sm">Имя или подпись</span>
        <input
          type="text"
          value={form.label}
          onChange={(event) => setForm({ ...form, label: event.target.value })}
          placeholder="Например: Я, Партнер, Анна"
        />
      </label>

      <label style={{ display: "grid", gap: "0.35rem" }}>
        <span className="orbit-body-sm">Дата рождения</span>
        <input
          type="date"
          value={form.date}
          onChange={(event) => setForm({ ...form, date: event.target.value })}
          required
        />
      </label>

      <div style={{ display: "grid", gap: "0.6rem" }}>
        <label style={{ display: "grid", gap: "0.35rem" }}>
          <span className="orbit-body-sm">Время рождения</span>
          <input
            type="time"
            value={form.time}
            onChange={(event) => setForm({ ...form, time: event.target.value })}
            disabled={form.timeUnknown}
          />
        </label>
        <label style={{ display: "flex", alignItems: "center", gap: "0.55rem" }}>
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

      <div style={{ display: "grid", gap: "0.35rem" }}>
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
    <div className="compat-desktop-card" style={{ display: "grid", gap: "0.8rem" }}>
      <div style={{ display: "flex", gap: "0.7rem", flexWrap: "wrap" }}>
        {people.map((person) => (
          <div
            key={person.title}
            style={{
              minWidth: "148px",
              padding: "0.7rem 0.8rem",
              borderRadius: "18px",
              background: person.date ? "rgba(255,248,237,0.96)" : "rgba(247,242,234,0.72)",
              border: person.date ? "1px solid rgba(195, 167, 114, 0.22)" : "1px dashed rgba(195, 167, 114, 0.3)",
            }}
          >
            <p className="orbit-body-xs" style={{ margin: 0, color: "#8b7355", textTransform: "uppercase", letterSpacing: "0.06em" }}>
              {person.title}
            </p>
            <p className="orbit-body-sm" style={{ margin: "0.18rem 0 0", color: "#0f172a", fontWeight: 700 }}>
              {person.label}
            </p>
            <p className="orbit-body-xs" style={{ margin: "0.22rem 0 0", color: "#64748b" }}>
              {person.date || "Дата не выбрана"}
            </p>
          </div>
        ))}
      </div>
      <p className="orbit-body-sm" style={{ margin: 0, color: "#5f4930", lineHeight: 1.7 }}>
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
      hideHeader
      mainWide
      contentClassName={`${pl.content} ${pl.legacyHost}`}
    >
      {limitBlocked ? (
        <section className="tf-shell" style={{ paddingTop: "2rem", paddingBottom: "4.5rem" }}>
          <GuestAccessLimitGate
            title={GUEST_ACCESS_COPY.compatLimitTitle}
            body={GUEST_ACCESS_COPY.compatLimitBody}
            secondaryHref="/compatibility"
            secondaryLabel="← К совместимости"
            testId="guest-compat-birthdates-limit"
          />
        </section>
      ) : (
      <section className="tf-shell" style={{ paddingTop: "2rem", paddingBottom: "4.5rem" }}>
        <form
          onSubmit={handleSubmit}
          className="tf-surface"
          style={{
            position: "relative",
            overflow: "hidden",
            display: "grid",
            gap: "1rem",
            padding: "clamp(1.2rem, 4vw, 2.2rem)",
          }}
        >
          <div
            aria-hidden="true"
            style={{
              position: "absolute",
              inset: 0,
              background:
                "radial-gradient(circle at top left, rgba(246, 233, 206, 0.44), transparent 32%), radial-gradient(circle at bottom right, rgba(221, 234, 219, 0.3), transparent 28%), linear-gradient(180deg, rgba(255,250,244,0.72), rgba(255,255,255,0.94))",
              pointerEvents: "none",
            }}
          />

          <div className="compat-desktop-shell compat-desktop-stack" style={{ position: "relative", zIndex: 1 }}>
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

            {compatRemaining < 4 ? (
              <p className="orbit-body-sm" style={{ margin: 0, color: "var(--orbit-color-muted, #6b6560)" }}>
                {GUEST_ACCESS_COPY.remainingCompat(compatRemaining)}
              </p>
            ) : null}

            <div
              style={{
                display: "grid",
                gridTemplateColumns: "minmax(0, 1.45fr) minmax(280px, 0.85fr)",
                gap: "1rem",
                alignItems: "start",
              }}
              className="compat-signs-hero-grid"
            >
              <div>
                <p className="compat-hero-eyebrow">Совместимость · по датам</p>
                <h1 className="orbit-display" style={{ margin: "0.35rem 0 0" }}>
                  Разобрать совместимость
                </h1>
                <p className="orbit-body compat-desktop-muted" style={{ margin: "0.85rem 0 0", maxWidth: "34rem" }}>
                  Две даты рождения — точнее, чем только знаки. Время и город по желанию для следующего слоя.
                </p>
              </div>

              <div className="compat-desktop-card">
                <p className="orbit-body-xs" style={{ margin: 0, color: "#8b7355", textTransform: "uppercase", letterSpacing: "0.08em" }}>
                  Минимум
                </p>
                <div style={{ marginTop: "0.7rem", display: "grid", gap: "0.45rem" }}>
                  <p className="orbit-body-sm" style={{ margin: 0 }}>
                    1. Две даты рождения.
                  </p>
                  <p className="orbit-body-sm" style={{ margin: 0 }}>
                    2. Остальное по желанию.
                  </p>
                </div>
              </div>
            </div>

            <PairReadiness form1={form1} form2={form2} precisionNote={precisionNote} />

            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(290px, 1fr))",
                gap: "1rem",
              }}
            >
              <PersonCard title="Твои данные" form={form1} setForm={setForm1} />
              <PersonCard title="Данные партнёра" form={form2} setForm={setForm2} />
            </div>

            <section className="compat-desktop-card">
            <p className="orbit-body-xs" style={{ margin: "0 0 0.65rem", color: "#8b7355", textTransform: "uppercase", letterSpacing: "0.08em" }}>
              Что сейчас между вами?
            </p>
            <p className="orbit-body-sm" style={{ margin: "0 0 0.75rem", color: "var(--orbit-color-muted)", lineHeight: 1.65 }}>
              Необязательно, но сильно улучшает персонализацию разбора и советов.
            </p>
            <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem" }}>
              {RELATIONSHIP_CONTEXT_OPTIONS.map((opt) => {
                const active = relationshipContext === opt.id;
                return (
                  <button
                    key={opt.id}
                    type="button"
                    className="orbit-button orbit-button-secondary orbit-button-sm"
                    onClick={() => setRelationshipContext(active ? "" : opt.id)}
                    style={{
                      borderColor: active ? "rgba(167, 123, 55, 0.88)" : undefined,
                      background: active ? "rgba(242, 220, 181, 0.32)" : undefined,
                      textAlign: "left",
                    }}
                  >
                    {opt.label}
                  </button>
                );
              })}
            </div>
            </section>

            <div
              style={{
                display: "grid",
                gridTemplateColumns: "minmax(0, 1.1fr) minmax(280px, 0.9fr)",
                gap: "1rem",
                alignItems: "start",
              }}
              className="compat-signs-footer-grid"
            >
              <div className="compat-desktop-card">
                <p className="orbit-body-xs" style={{ margin: 0, color: "#8b7355", textTransform: "uppercase", letterSpacing: "0.08em" }}>
                  Что получишь
                </p>
                <p className="orbit-body-sm" style={{ margin: "0.55rem 0 0", color: "var(--orbit-color-muted)", lineHeight: 1.65 }}>
                  Тон пары и зоны напряжения — в результате.
                </p>
              </div>

              <div className="compat-desktop-card" style={{ display: "grid", gap: "0.8rem" }}>
                <button
                  type="submit"
                  className="orbit-button orbit-button-primary"
                  disabled={!canContinue || loading}
                  style={{ width: "100%", opacity: canContinue && !loading ? 1 : 0.56 }}
                >
                  {loading ? <LoadingSpinner size="sm" /> : canContinue ? "Разбор" : "Две даты"}
                </button>
                <Link href="/compatibility" className="orbit-button orbit-button-secondary" style={{ textDecoration: "none", textAlign: "center" }}>
                  Совместимость по профилям
                </Link>
                <Link href="/compatibility/signs" className="compat-analyze-back" style={{ textAlign: "center" }}>
                  К знакам
                </Link>
                {error ? (
                  <p
                    className="orbit-body-sm"
                    style={{
                      margin: 0,
                      color: "#8c2f2f",
                      background: "rgba(210, 123, 93, 0.1)",
                      borderRadius: "14px",
                      padding: "0.8rem 0.95rem",
                    }}
                  >
                    {error}
                  </p>
                ) : null}
              </div>
            </div>
          </div>
        </form>
      </section>
      )}
    </ProductPageScreen>
  );
}
