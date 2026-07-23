"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useMemo, useState } from "react";
import { LoadingSpinner } from "@/components/orbit";
import {
  BirthProfileIntakeFields,
  type BirthProfileIntakeValues,
} from "@/components/intake/BirthProfileIntakeFields";
import { RELATIONSHIP_CONTEXT_OPTIONS, type RelationshipContextId } from "@/lib/compatibilityRelationshipContext";
import {
  buildCompatibilityCheckKey,
  canGuestAccessCompatibility,
  guestCompatibilityRemaining,
  isGuestCompatibilityLimitReached,
} from "@/lib/guestAccessStore";
import { writeGuestCompatPair } from "@/lib/guestCompatPair";
import { GuestAccessLimitGate } from "@/components/guest/GuestAccessLimitGate";
import { GUEST_ACCESS_COPY } from "@/components/guest/guestAccessCopy";
import { ProductPageScreen } from "@/components/product-ui/ProductPageScreen";
import pl from "@/design-system/layouts/productPageLayout.module.css";

function readinessLabel(withTime: number, withCities: number) {
  if (withTime === 2 && withCities >= 1) return "Достаточно данных для точного слоя.";
  if (withTime >= 1 || withCities >= 1) return "Можно открыть разбор.";
  return "Нужны две даты.";
}

function PairReadiness({
  form1,
  form2,
  precisionNote,
}: {
  form1: BirthProfileIntakeValues;
  form2: BirthProfileIntakeValues;
  precisionNote: string;
}) {
  const people = [
    { title: "Ты", label: form1.label || "Без подписи", date: form1.birth_date },
    { title: "Партнёр", label: form2.label || "Без подписи", date: form2.birth_date },
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

const EMPTY_PERSON = (label: string): BirthProfileIntakeValues => ({
  label,
  birth_date: "",
  birth_time: "",
  time_unknown: true,
  location_name: "",
  latitude: null,
  longitude: null,
});

export default function CompatibilityBirthdatesPage() {
  const router = useRouter();
  const [form1, setForm1] = useState<BirthProfileIntakeValues>(EMPTY_PERSON("Я"));
  const [form2, setForm2] = useState<BirthProfileIntakeValues>(EMPTY_PERSON("Партнёр"));
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [relationshipContext, setRelationshipContext] = useState<RelationshipContextId | "">("");
  const [limitBlocked, setLimitBlocked] = useState(false);

  const canContinue = Boolean(form1.birth_date && form2.birth_date);
  const compatCheckKey = buildCompatibilityCheckKey({
    mode: "precise",
    birth_date_1: form1.birth_date,
    birth_date_2: form2.birth_date,
    relationship_context: relationshipContext || undefined,
  });
  const compatRemaining = guestCompatibilityRemaining();

  const precisionNote = useMemo(() => {
    const withTime =
      Number(Boolean(!form1.time_unknown && form1.birth_time)) +
      Number(Boolean(!form2.time_unknown && form2.birth_time));
    const withCities = Number(Boolean(form1.location_name)) + Number(Boolean(form2.location_name));
    return readinessLabel(withTime, withCities);
  }, [form1, form2]);

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

    writeGuestCompatPair({
      version: 1,
      person_a: {
        label: form1.label.trim() || "Я",
        birth_date: form1.birth_date,
        birth_time: form1.time_unknown ? null : form1.birth_time || null,
        time_unknown: form1.time_unknown,
        location_name: form1.location_name.trim() || null,
        latitude: form1.latitude,
        longitude: form1.longitude,
      },
      person_b: {
        label: form2.label.trim() || "Партнёр",
        birth_date: form2.birth_date,
        birth_time: form2.time_unknown ? null : form2.birth_time || null,
        time_unknown: form2.time_unknown,
        location_name: form2.location_name.trim() || null,
        latitude: form2.latitude,
        longitude: form2.longitude,
      },
      relationship_context: relationshipContext || null,
      preview_seen_at: null,
      save_ready_at: null,
    });

    router.push("/compatibility/birthdates/result");
  };

  return (
    <ProductPageScreen
      testId="compat-birthdates-page"
      title="Персональная совместимость"
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
                  <Link href="/compatibility/signs" className="compat-analyze-back">
                    Игровая по знакам →
                  </Link>
                </div>
              </div>

              {compatRemaining < 4 ? (
                <p className="orbit-body-sm" style={{ margin: 0, color: "var(--orbit-color-muted, #6b6560)" }}>
                  {GUEST_ACCESS_COPY.remainingCompat(compatRemaining)}
                </p>
              ) : null}

              <div>
                <p className="compat-hero-eyebrow">Совместимость · два профиля</p>
                <h1 className="orbit-display" style={{ margin: "0.35rem 0 0" }}>
                  Персональная совместимость двух людей
                </h1>
                <p className="orbit-body compat-desktop-muted" style={{ margin: "0.85rem 0 0", maxWidth: "36rem" }}>
                  Две даты создают черновики профилей. После email оба закрепятся в аккаунте. Знаки-only игра — отдельно, без
                  durable-профилей.
                </p>
              </div>

              <PairReadiness form1={form1} form2={form2} precisionNote={precisionNote} />

              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "repeat(auto-fit, minmax(290px, 1fr))",
                  gap: "1rem",
                }}
              >
                <div className="compat-desktop-card">
                  <BirthProfileIntakeFields title="Первый человек" values={form1} onChange={setForm1} />
                </div>
                <div className="compat-desktop-card">
                  <BirthProfileIntakeFields title="Второй человек" values={form2} onChange={setForm2} />
                </div>
              </div>

              <section className="compat-desktop-card">
                <p
                  className="orbit-body-xs"
                  style={{ margin: "0 0 0.65rem", color: "#8b7355", textTransform: "uppercase", letterSpacing: "0.08em" }}
                >
                  Что сейчас между вами?
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

              {error ? (
                <p className="orbit-body-sm" style={{ margin: 0, color: "#b42318" }}>
                  {error}
                </p>
              ) : null}

              <div className="compat-desktop-card" style={{ display: "grid", gap: "0.8rem" }}>
                <button
                  type="submit"
                  className="orbit-button orbit-button-primary"
                  disabled={!canContinue || loading}
                  style={{ width: "100%", opacity: canContinue && !loading ? 1 : 0.56 }}
                  data-testid="compat-birthdates-submit"
                >
                  {loading ? <LoadingSpinner size="sm" /> : canContinue ? "Открыть разбор" : "Нужны две даты"}
                </button>
                <Link
                  href="/compatibility/signs"
                  className="orbit-button orbit-button-secondary"
                  style={{ textDecoration: "none", textAlign: "center" }}
                >
                  Сначала игровая проверка по знакам
                </Link>
              </div>
            </div>
          </form>
        </section>
      )}
    </ProductPageScreen>
  );
}
