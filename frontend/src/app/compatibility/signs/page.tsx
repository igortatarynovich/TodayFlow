"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useMemo, useState } from "react";
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

const ZODIAC_SIGNS = [
  { id: "aries", name: "Овен", nameEn: "Aries", glyph: "Ar" },
  { id: "taurus", name: "Телец", nameEn: "Taurus", glyph: "Ta" },
  { id: "gemini", name: "Близнецы", nameEn: "Gemini", glyph: "Ge" },
  { id: "cancer", name: "Рак", nameEn: "Cancer", glyph: "Ca" },
  { id: "leo", name: "Лев", nameEn: "Leo", glyph: "Le" },
  { id: "virgo", name: "Дева", nameEn: "Virgo", glyph: "Vi" },
  { id: "libra", name: "Весы", nameEn: "Libra", glyph: "Li" },
  { id: "scorpio", name: "Скорпион", nameEn: "Scorpio", glyph: "Sc" },
  { id: "sagittarius", name: "Стрелец", nameEn: "Sagittarius", glyph: "Sg" },
  { id: "capricorn", name: "Козерог", nameEn: "Capricorn", glyph: "Cp" },
  { id: "aquarius", name: "Водолей", nameEn: "Aquarius", glyph: "Aq" },
  { id: "pisces", name: "Рыбы", nameEn: "Pisces", glyph: "Pi" },
];

const GENDER_OPTIONS = [
  { id: "unknown", label: "Не указывать" },
  { id: "female", label: "Женщина" },
  { id: "male", label: "Мужчина" },
] as const;

function signMetaById(id: string) {
  return ZODIAC_SIGNS.find((item) => item.id === id) || null;
}

function GenderPicker({
  title,
  value,
  onChange,
}: {
  title: string;
  value: string;
  onChange: (id: string) => void;
}) {
  return (
    <section className="compat-desktop-card">
      <p className="orbit-body-xs" style={{ margin: "0 0 0.7rem", color: "#8b7355", textTransform: "uppercase", letterSpacing: "0.08em" }}>
        {title}
      </p>
      <div style={{ display: "flex", gap: "0.55rem", flexWrap: "wrap" }}>
        {GENDER_OPTIONS.map((item) => {
          const active = value === item.id;
          return (
            <button
              key={item.id}
              type="button"
              onClick={() => onChange(item.id)}
              className="orbit-button orbit-button-secondary orbit-button-sm"
              style={{
                borderColor: active ? "rgba(167, 123, 55, 0.88)" : undefined,
                background: active ? "rgba(242, 220, 181, 0.32)" : undefined,
              }}
            >
              {item.label}
            </button>
          );
        })}
      </div>
    </section>
  );
}

function SignPicker({
  title,
  value,
  onChange,
}: {
  title: string;
  value: string;
  onChange: (id: string) => void;
}) {
  return (
    <section className="compat-desktop-card">
      <div style={{ display: "grid", gap: "0.85rem" }}>
        <div>
          <p className="orbit-body-xs" style={{ margin: 0, color: "#8b7355", textTransform: "uppercase", letterSpacing: "0.08em" }}>
            {title}
          </p>
        </div>
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(118px, 1fr))",
            gap: "0.65rem",
          }}
        >
          {ZODIAC_SIGNS.map((sign) => {
            const active = value === sign.id;

            return (
              <button
                key={sign.id}
                type="button"
                onClick={() => onChange(sign.id)}
                style={{
                  padding: "0.9rem 0.85rem",
                  borderRadius: "20px",
                  border: active
                    ? "1px solid rgba(167, 123, 55, 0.88)"
                    : "1px solid rgba(195, 167, 114, 0.22)",
                  background: active
                    ? "linear-gradient(135deg, rgba(242, 220, 181, 0.95), rgba(255, 248, 237, 0.98))"
                    : "rgba(255,255,255,0.82)",
                  cursor: "pointer",
                  opacity: 1,
                  textAlign: "center",
                  transition: "transform 160ms ease, box-shadow 160ms ease, border-color 160ms ease",
                  boxShadow: active ? "0 16px 36px rgba(191, 155, 96, 0.18)" : "none",
                  minHeight: "112px",
                }}
              >
                <div
                  style={{
                    width: "2.2rem",
                    height: "2.2rem",
                    borderRadius: "999px",
                    display: "inline-flex",
                    alignItems: "center",
                    justifyContent: "center",
                    margin: "0 auto 0.55rem",
                    background: active ? "rgba(167, 123, 55, 0.14)" : "rgba(15, 23, 42, 0.05)",
                    color: "var(--orbit-color-ink)",
                    fontWeight: 700,
                    fontSize: "0.84rem",
                  }}
                >
                  {sign.glyph}
                </div>
                <div className="orbit-body" style={{ fontWeight: 600 }}>
                  {sign.name}
                </div>
                <div className="orbit-body-sm" style={{ color: "var(--orbit-color-muted)" }}>
                  {sign.nameEn}
                </div>
              </button>
            );
          })}
        </div>
      </div>
    </section>
  );
}

function PairPreview({ signFrom, signTo }: { signFrom: string; signTo: string }) {
  const from = signMetaById(signFrom);
  const to = signMetaById(signTo);

  return (
    <div className="compat-desktop-card" style={{ display: "grid", gap: "0.75rem" }}>
      <div style={{ display: "flex", alignItems: "center", gap: "0.7rem", flexWrap: "wrap" }}>
        {[from, to].map((sign, index) => (
          <div
            key={index}
            style={{
              minWidth: "132px",
              padding: "0.7rem 0.8rem",
              borderRadius: "18px",
              background: sign ? "rgba(255,248,237,0.96)" : "rgba(247,242,234,0.72)",
              border: sign ? "1px solid rgba(195, 167, 114, 0.22)" : "1px dashed rgba(195, 167, 114, 0.3)",
              display: "flex",
              alignItems: "center",
              gap: "0.65rem",
            }}
          >
            <div
              style={{
                width: "2rem",
                height: "2rem",
                borderRadius: "999px",
                background: sign ? "rgba(167, 123, 55, 0.12)" : "rgba(15,23,42,0.05)",
                display: "inline-flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: "0.78rem",
                fontWeight: 700,
                color: "#3f2e17",
              }}
            >
              {sign?.glyph || "?"}
            </div>
            <div style={{ minWidth: 0 }}>
              <p className="orbit-body-xs" style={{ margin: 0, color: "#8b7355", textTransform: "uppercase", letterSpacing: "0.06em" }}>
                {index === 0 ? "Твой знак" : "Знак партнёра"}
              </p>
              <p className="orbit-body-sm" style={{ margin: "0.18rem 0 0", color: "#0f172a", fontWeight: 700 }}>
                {sign?.name || "Не выбран"}
              </p>
            </div>
          </div>
        ))}
      </div>
      <p className="orbit-body-sm" style={{ margin: 0, color: "#5f4930", lineHeight: 1.65 }}>
        {from && to ? "Можно открыть разбор." : "Выбери оба знака."}
      </p>
    </div>
  );
}

export default function CompatibilitySignsPage() {
  const router = useRouter();
  const [signFrom, setSignFrom] = useState("");
  const [signTo, setSignTo] = useState("");
  const [fromGender, setFromGender] = useState<string>("unknown");
  const [toGender, setToGender] = useState<string>("unknown");
  const [relationshipContext, setRelationshipContext] = useState<RelationshipContextId | "">("");
  const [limitBlocked, setLimitBlocked] = useState(false);

  const selectedPair = useMemo(() => {
    const from = signMetaById(signFrom);
    const to = signMetaById(signTo);
    if (!from || !to) return null;
    return `${from.name} × ${to.name}`;
  }, [signFrom, signTo]);

  const canContinue = Boolean(signFrom && signTo);
  const compatCheckKey = buildCompatibilityCheckKey({
    mode: "signs",
    from: signFrom,
    to: signTo,
    relationship_context: relationshipContext || undefined,
  });
  const compatRemaining = guestCompatibilityRemaining();

  return (
    <ProductPageScreen
      testId="compat-signs-page"
      title="Совместимость по знакам"
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
            testId="guest-compat-signs-limit"
          />
        </section>
      ) : (
      <section className="tf-shell" style={{ paddingTop: "2rem", paddingBottom: "4.5rem" }}>
        <div
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
                "radial-gradient(circle at top right, rgba(248, 229, 191, 0.45), transparent 34%), radial-gradient(circle at bottom left, rgba(219, 232, 214, 0.28), transparent 28%), linear-gradient(180deg, rgba(255,250,244,0.72), rgba(255,255,255,0.94))",
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
                <Link href="/compatibility/birthdates" className="compat-analyze-back">
                  По датам →
                </Link>
              </div>
            </div>

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
                <p className="compat-hero-eyebrow">Совместимость · по знакам</p>
                <h1 className="orbit-display" style={{ margin: "0.35rem 0 0" }}>
                  Разобрать совместимость
                </h1>
                <p className="orbit-body compat-desktop-muted" style={{ margin: "0.85rem 0 0", maxWidth: "34rem" }}>
                  Быстрый вход по знакам — затем честный разбор динамики: эмоции, конфликт, сексуальность, роли и что делать.
                </p>
              </div>

              <div className="compat-desktop-card">
                <p className="orbit-body-xs" style={{ margin: 0, color: "#8b7355", textTransform: "uppercase", letterSpacing: "0.08em" }}>
                  Шаги
                </p>
                <div style={{ marginTop: "0.7rem", display: "grid", gap: "0.45rem" }}>
                  <p className="orbit-body-sm" style={{ margin: 0 }}>
                    Знаки и контекст → разбор
                  </p>
                </div>
              </div>
            </div>

            <PairPreview signFrom={signFrom} signTo={signTo} />

            {compatRemaining < 4 ? (
              <p className="orbit-body-sm" style={{ margin: 0, color: "var(--orbit-color-muted, #6b6560)" }}>
                {GUEST_ACCESS_COPY.remainingCompat(compatRemaining)}
              </p>
            ) : null}

            <div style={{ display: "grid", gap: "1rem" }}>
              <div style={{ display: "grid", gap: "0.75rem", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))" }}>
                <GenderPicker title="Ты (пол по желанию)" value={fromGender} onChange={setFromGender} />
                <GenderPicker title="Партнёр (пол по желанию)" value={toGender} onChange={setToGender} />
              </div>
              <SignPicker title="Твой знак" value={signFrom} onChange={setSignFrom} />
              <SignPicker title="Знак партнёра" value={signTo} onChange={setSignTo} />
            </div>

            <section className="compat-desktop-card">
            <p className="orbit-body-xs" style={{ margin: "0 0 0.65rem", color: "#8b7355", textTransform: "uppercase", letterSpacing: "0.08em" }}>
              Что сейчас между вами?
            </p>
            <p className="orbit-body-sm" style={{ margin: "0 0 0.75rem", color: "var(--orbit-color-muted)", lineHeight: 1.65 }}>
              От этого меняется тон текста и акценты в практических шагах. Можно пропустить — тогда разбор нейтральнее.
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
                  Выбор пары
                </p>
                <h2 className="orbit-heading-2" style={{ margin: "0.45rem 0 0" }}>
                  {selectedPair || "Пока не выбрана"}
                </h2>
                <p className="orbit-body-sm" style={{ margin: "0.65rem 0 0", color: "var(--orbit-color-muted)" }}>
                  Разбор ниже по кнопке.
                </p>
              </div>

              <div className="compat-desktop-card" style={{ display: "grid", gap: "0.8rem" }}>
                <button
                  type="button"
                  className="orbit-button orbit-button-primary"
                  disabled={!canContinue}
                  onClick={() => {
                    if (!canContinue) return;
                    if (isGuestCompatibilityLimitReached() && !canGuestAccessCompatibility(compatCheckKey)) {
                      setLimitBlocked(true);
                      return;
                    }
                    const params = new URLSearchParams({
                      from: signFrom,
                      to: signTo,
                      from_gender: fromGender,
                      to_gender: toGender,
                    });
                    if (relationshipContext) {
                      params.set("ctx", relationshipContext);
                    }
                    router.push(`/compatibility/signs/result?${params.toString()}`);
                  }}
                  style={{ width: "100%", opacity: canContinue ? 1 : 0.56 }}
                >
                  {canContinue ? "Посмотреть совместимость" : "Выбери оба знака"}
                </button>
                <Link href="/compatibility" className="orbit-button orbit-button-secondary" style={{ textDecoration: "none", textAlign: "center" }}>
                  Совместимость по профилям
                </Link>
                <Link href="/compatibility/birthdates" className="compat-analyze-back" style={{ textAlign: "center" }}>
                  Точный разбор по датам
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>
      )}
    </ProductPageScreen>
  );
}
