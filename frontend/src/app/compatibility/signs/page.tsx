"use client";

import { DsButton } from "@/design-system";

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
    <section className="compat-desktop-section">
      <p className="compat-section-kicker">{title}</p>
      <div style={{ display: "flex", gap: "0.55rem", flexWrap: "wrap" }}>
        {GENDER_OPTIONS.map((item) => {
          const active = value === item.id;
          return (
            <button
              key={item.id}
              type="button"
              onClick={() => onChange(item.id)}
              className={active ? "compat-chip is-active" : "compat-chip"}
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
    <section className="compat-desktop-card" style={{ display: "grid", gap: "0.85rem" }}>
      <p className="compat-section-kicker" style={{ marginBottom: 0 }}>
        {title}
      </p>
      <div className="compat-sign-grid">
        {ZODIAC_SIGNS.map((sign) => {
          const active = value === sign.id;
          return (
            <button
              key={sign.id}
              type="button"
              onClick={() => onChange(sign.id)}
              className={active ? "compat-sign-tile is-active" : "compat-sign-tile"}
            >
              <div className="compat-sign-glyph">{sign.glyph}</div>
              <div className="orbit-body" style={{ fontWeight: 600 }}>
                {sign.name}
              </div>
              <div className="orbit-body-sm" style={{ color: "var(--tf-caption)" }}>
                {sign.nameEn}
              </div>
            </button>
          );
        })}
      </div>
    </section>
  );
}

function PairPreview({ signFrom, signTo }: { signFrom: string; signTo: string }) {
  const from = signMetaById(signFrom);
  const to = signMetaById(signTo);

  return (
    <div className="compat-readiness">
      <div className="compat-readiness-row">
        {[from, to].map((sign, index) => (
          <div
            key={index}
            className={sign ? "compat-readiness-chip" : "compat-readiness-chip is-empty"}
            style={{ display: "flex", alignItems: "center", gap: "0.65rem" }}
          >
            <div className="compat-sign-glyph" style={{ margin: 0 }}>
              {sign?.glyph || "?"}
            </div>
            <div style={{ minWidth: 0 }}>
              <p className="compat-section-kicker" style={{ marginBottom: 0 }}>
                {index === 0 ? "Твой знак" : "Знак партнёра"}
              </p>
              <p className="orbit-body-sm" style={{ margin: "0.18rem 0 0", fontWeight: 700, color: "var(--tf-ink)" }}>
                {sign?.name || "Не выбран"}
              </p>
            </div>
          </div>
        ))}
      </div>
      <p className="compat-section-lead" style={{ marginBottom: 0 }}>
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
      subtitle="Быстрый вход по знакам — затем разбор динамики: эмоции, конфликт, роли и что делать."
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
            testId="guest-compat-signs-limit"
          />
        </section>
      ) : (
        <section className="compat-flow-section">
          <div className="compat-desktop-shell compat-desktop-stack">
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

            <PairPreview signFrom={signFrom} signTo={signTo} />

            {compatRemaining < 4 ? (
              <p className="compat-section-lead" style={{ marginBottom: 0 }}>
                {GUEST_ACCESS_COPY.remainingCompat(compatRemaining)}
              </p>
            ) : null}

            <div className="compat-form-grid">
              <GenderPicker title="Ты (пол по желанию)" value={fromGender} onChange={setFromGender} />
              <GenderPicker title="Партнёр (пол по желанию)" value={toGender} onChange={setToGender} />
            </div>

            <SignPicker title="Твой знак" value={signFrom} onChange={setSignFrom} />
            <SignPicker title="Знак партнёра" value={signTo} onChange={setSignTo} />

            <section className="compat-desktop-section">
              <p className="compat-section-kicker">Что сейчас между вами?</p>
              <p className="compat-section-lead">
                От этого меняется тон текста и акценты в практических шагах. Можно пропустить — тогда разбор нейтральнее.
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
              {selectedPair ? (
                <p className="compat-section-lead" style={{ marginBottom: 0 }}>
                  Пара: <strong style={{ color: "var(--tf-ink)" }}>{selectedPair}</strong>
                </p>
              ) : null}
              <DsButton
                variant="primary"
                size="block"
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
                style={{ opacity: canContinue ? 1 : 0.56 }}
              >
                {canContinue ? "Посмотреть совместимость" : "Выбери оба знака"}
              </DsButton>
              <DsButton href="/compatibility" variant="secondary">
                Совместимость по профилям
              </DsButton>
              <Link href="/compatibility/birthdates" className="compat-analyze-back" style={{ textAlign: "center" }}>
                Точный разбор по датам
              </Link>
            </div>
          </div>
        </section>
      )}
    </ProductPageScreen>
  );
}
