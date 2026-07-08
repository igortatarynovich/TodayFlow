"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { DsBody, DsButton } from "@/design-system";
import { ProductPageScreen } from "@/components/product-ui/ProductPageScreen";
import pl from "@/design-system/layouts/productPageLayout.module.css";
import v2 from "@/design-system/layouts/productV2Surface.module.css";
import { LoadingSpinner } from "@/components/orbit";
import {
  flowTrackerChromeBundle,
  type FlowPracticesChromeLocale,
  type FlowTrackerChromeBundle,
} from "@/components/today/flowPracticesMainTabChrome";
import { getJson } from "@/lib/api";
import { getLocale } from "@/lib/i18n";
import type { Mantra } from "@/lib/types";
import { useAuth } from "@/lib/useAuth";

function tpl(s: string, vars: Record<string, string | number>) {
  return s.replace(/\{\{(\w+)\}\}/g, (_, k) => String(vars[k] ?? ""));
}

type Affirmation = {
  id: string;
  text: string;
  title?: string;
  goal?: string;
  direction?: string;
  tags?: string[];
};

type LibraryKind = "all" | "affirmation" | "mantra";
type FocusKind = "all" | "calm" | "love" | "growth" | "money" | "work" | "support";

type LibraryItem = {
  id: string;
  kind: Exclude<LibraryKind, "all">;
  title: string;
  body: string;
  support?: string;
  tags: string[];
  focus: FocusKind[];
  href: string;
  hrefLabel: string;
};

function personalizedNeedFromFocus(focus: FocusKind): string | null {
  if (focus === "calm") return "calm";
  if (focus === "love") return "love";
  if (focus === "money") return "money";
  if (focus === "work") return "work";
  if (focus === "growth" || focus === "support") return "health";
  return null;
}

function focusRowsFromChrome(fc: FlowTrackerChromeBundle): Array<{ id: FocusKind; title: string; hint: string }> {
  return [
    { id: "all", title: fc.affirmationsFocusAllTitle, hint: fc.affirmationsFocusAllHint },
    { id: "calm", title: fc.affirmationsFocusCalmTitle, hint: fc.affirmationsFocusCalmHint },
    { id: "love", title: fc.affirmationsFocusLoveTitle, hint: fc.affirmationsFocusLoveHint },
    { id: "growth", title: fc.affirmationsFocusGrowthTitle, hint: fc.affirmationsFocusGrowthHint },
    { id: "money", title: fc.affirmationsFocusMoneyTitle, hint: fc.affirmationsFocusMoneyHint },
    { id: "work", title: fc.affirmationsFocusWorkTitle, hint: fc.affirmationsFocusWorkHint },
    { id: "support", title: fc.affirmationsFocusSupportTitle, hint: fc.affirmationsFocusSupportHint },
  ];
}

function uniqueStrings(values: Array<string | undefined | null>): string[] {
  return Array.from(new Set(values.map((item) => String(item || "").trim()).filter(Boolean)));
}

function detectFocus(text: string): FocusKind[] {
  const low = text.toLowerCase();
  const focus = new Set<FocusKind>();

  if (/(споко|баланс|гармон|тише|дых|выдох|мир|устал|восстанов)/.test(low)) focus.add("calm");
  if (/(calm|balance|harmon|quiet|breathe|breath|exhale|peace|tired|recover|rest|ground|steady)/.test(low)) focus.add("calm");
  if (/(люб|отнош|близост|сердц|партнер|нежн|довер)/.test(low)) focus.add("love");
  if (/(love|relationship|closeness|heart|partner|tender|trust|intimacy)/.test(low)) focus.add("love");
  if (/(рост|развив|двига|перемен|смел|раскрыв|учусь)/.test(low)) focus.add("growth");
  if (/(growth|develop|moving|change|courage|open up|learn|learning)/.test(low)) focus.add("growth");
  if (/(деньг|изобил|достат|богат|процвет|ценност|ресурс)/.test(low)) focus.add("money");
  if (/(money|abundan|wealth|prosper|resource|income|finance)/.test(low)) focus.add("money");
  if (/(работ|карьер|дело|роль|результ|успех|проект|реализац)/.test(low)) focus.add("work");
  if (/(work|career|role|result|success|project|job|business)/.test(low)) focus.add("work");
  if (/(поддерж|береж|можно|допустимо|опора|забот|мягк|принима)/.test(low)) focus.add("support");
  if (/(support|gentle|allow|care|soft|accept|inner|recovery|kind to)/.test(low)) focus.add("support");

  if (focus.size === 0) focus.add("support");
  return Array.from(focus);
}

function buildAffirmationItem(item: Affirmation, isAuthenticated: boolean, fc: FlowTrackerChromeBundle): LibraryItem {
  const body = String(item.text || "").replace(/[«»"]/g, "").trim();
  const title =
    String(item.title || "").trim() || body.split(/[.!?]/)[0] || fc.affirmationsDefaultTitleAffirmation;
  const support = item.goal || item.direction;
  const tags = uniqueStrings([item.goal, item.direction, ...(item.tags || [])]);

  return {
    id: item.id,
    kind: "affirmation",
    title,
    body,
    support,
    tags,
    focus: detectFocus([title, body, support, tags.join(" ")].join(" ")),
    href: isAuthenticated ? `/affirmations/tracker?affirmation=${encodeURIComponent(item.id)}` : `/auth?redirect=/affirmations`,
    hrefLabel: isAuthenticated ? fc.affirmationsCtaOpenTracker : fc.affirmationsCtaSignInUse,
  };
}

function buildMantraItem(item: Mantra, isAuthenticated: boolean, fc: FlowTrackerChromeBundle): LibraryItem {
  const mantraId = String(item.id || "").trim();
  const humanText = String(item.notes || "").trim();
  const pronunciation = String(item.pronunciation || "").trim();
  const guidance = String(item.guidance || "").trim();
  const body = String(item.mantra || humanText || guidance || item.intention || "").trim();
  const pronunciationLine = pronunciation ? tpl(fc.affirmationsMantraPronunciationPrefix, { text: pronunciation }) : "";
  const support = [item.intention, guidance, pronunciationLine].filter(Boolean).join(" ");
  const tags = uniqueStrings([...(item.axes || []), ...(item.best_for_phases || []), ...(item.stones || [])]);

  return {
    id: mantraId,
    kind: "mantra",
    title: String(item.title || fc.affirmationsDefaultTitleMantra).trim(),
    body,
    support,
    tags,
    focus: detectFocus([item.title, item.intention, item.guidance, item.notes, item.mantra].join(" ")),
    href: isAuthenticated ? "/today" : "/auth?redirect=/affirmations",
    hrefLabel: isAuthenticated ? fc.affirmationsCtaMoveToday : fc.affirmationsCtaSignInToday,
  };
}

function formatAffirmationsCatalogCount(n: number, locale: FlowPracticesChromeLocale, fc: FlowTrackerChromeBundle): string {
  if (locale === "en") {
    return tpl(n === 1 ? fc.affirmationsCatalogCountEn : fc.affirmationsCatalogCountEnPlural, { n });
  }
  const mod10 = n % 10;
  const mod100 = n % 100;
  if (mod10 === 1 && mod100 !== 11) return tpl(fc.affirmationsCatalogCountRu1, { n });
  if (mod10 >= 2 && mod10 <= 4 && (mod100 < 10 || mod100 >= 20)) return tpl(fc.affirmationsCatalogCountRu24, { n });
  return tpl(fc.affirmationsCatalogCountRuMany, { n });
}

export default function AffirmationsPage() {
  const { isAuthenticated } = useAuth();
  const locale: FlowPracticesChromeLocale = getLocale() === "ru" ? "ru" : "en";
  const fc = useMemo(() => flowTrackerChromeBundle(locale), [locale]);
  const focusRows = useMemo(() => focusRowsFromChrome(fc), [fc]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [affirmations, setAffirmations] = useState<Affirmation[]>([]);
  const [mantras, setMantras] = useState<Mantra[]>([]);
  const [generatedAffirmations, setGeneratedAffirmations] = useState<Affirmation[]>([]);
  const [generating, setGenerating] = useState(false);
  const [kind, setKind] = useState<LibraryKind>("all");
  const [focus, setFocus] = useState<FocusKind>("all");
  const [query, setQuery] = useState("");

  useEffect(() => {
    const bundle = flowTrackerChromeBundle(locale);
    const loadLibrary = async () => {
      try {
        setLoading(true);
        setError(null);
        const [affirmationsData, mantrasData] = await Promise.all([
          getJson<Affirmation[]>("/practices/affirmations"),
          getJson<Mantra[]>("/reference/mantras"),
        ]);
        setAffirmations(Array.isArray(affirmationsData) ? affirmationsData : []);
        setMantras(Array.isArray(mantrasData) ? mantrasData : []);
      } catch (err) {
        console.error("Error loading affirmations library:", err);
        setError(bundle.affirmationsLibraryLoadError);
      } finally {
        setLoading(false);
      }
    };

    void loadLibrary();
  }, [locale]);

  const library = useMemo(() => {
    const items: LibraryItem[] = [
      ...affirmations.map((item) => buildAffirmationItem(item, isAuthenticated, fc)),
      ...mantras.map((item) => buildMantraItem(item, isAuthenticated, fc)),
    ];

    const search = query.trim().toLowerCase();

    return items.filter((item) => {
      if (kind !== "all" && item.kind !== kind) return false;
      if (focus !== "all" && !item.focus.includes(focus)) return false;
      if (!search) return true;
      const haystack = [item.title, item.body, item.support, item.tags.join(" "), item.focus.join(" ")].join(" ").toLowerCase();
      return haystack.includes(search);
    });
  }, [affirmations, mantras, isAuthenticated, kind, focus, query, fc]);

  const featuredItems = useMemo(() => library.slice(0, 3), [library]);
  const generatedNeed = useMemo(() => personalizedNeedFromFocus(focus), [focus]);
  const catalogCountLabel = useMemo(() => formatAffirmationsCatalogCount(library.length, locale, fc), [library.length, locale, fc]);

  useEffect(() => {
    setGeneratedAffirmations([]);
  }, [focus, query, kind]);

  const loadGeneratedAffirmations = async () => {
    if (!generatedNeed || !isAuthenticated) return;
    try {
      setGenerating(true);
      const data = await getJson<Affirmation[]>(`/practices/affirmations?generate=true&needs=${encodeURIComponent(generatedNeed)}`);
      setGeneratedAffirmations(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error("Error generating affirmations:", err);
      setGeneratedAffirmations([]);
    } finally {
      setGenerating(false);
    }
  };

  if (loading) {
    return (
      <ProductPageScreen
        testId="affirmations-library-page"
        title={fc.affirmationsLibraryPageTitle}
        loading
        loadingLabel={locale === "ru" ? "Загрузка библиотеки…" : "Loading library…"}
      />
    );
  }

  if (error) {
    return (
      <ProductPageScreen testId="affirmations-library-page" title={fc.affirmationsLibraryPageTitle} contentClassName={pl.content}>
        <div className={pl.panel}>
          <DsBody>{error}</DsBody>
        </div>
      </ProductPageScreen>
    );
  }

  return (
    <ProductPageScreen
      testId="affirmations-library-page"
      eyebrow={fc.affirmationsLibraryPageEyebrow}
      title={fc.affirmationsLibraryPageTitle}
      subtitle={fc.affirmationsLibraryPageLead}
      contentClassName={`${pl.content} ${pl.legacyHost}`}
    >
      <div style={{ display: "flex", gap: "0.65rem", flexWrap: "wrap" }}>
        <DsButton href="/affirmations/tracker" size="sm">
          {fc.affirmationsLibraryLinkTracker}
        </DsButton>
        <DsButton href="/today" variant="secondary" size="sm">
          {fc.affirmationsCtaOpenToday}
        </DsButton>
      </div>

        <section className={pl.panel}>
          <div style={{ display: "grid", gap: "0.9rem" }}>
            <div style={{ display: "flex", gap: "0.55rem", flexWrap: "wrap" }}>
              {[
                { id: "all" as const, label: fc.affirmationsKindFilterAll },
                { id: "affirmation" as const, label: fc.affirmationsKindFilterAffirmation },
                { id: "mantra" as const, label: fc.affirmationsKindFilterMantra },
              ].map((item) => (
                <button
                  key={item.id}
                  onClick={() => setKind(item.id as LibraryKind)}
                  className={kind === item.id ? "orbit-button orbit-button-primary orbit-button-sm" : "orbit-button orbit-button-secondary orbit-button-sm"}
                >
                  {item.label}
                </button>
              ))}
            </div>

            <input
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder={fc.affirmationsSearchPlaceholder}
              className={pl.fieldInput}
            />

            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: "0.7rem" }}>
              {focusRows.map((item) => (
                <button
                  key={item.id}
                  onClick={() => setFocus(item.id)}
                  className={pl.panel}
                  style={{
                    padding: "0.9rem",
                    textAlign: "left",
                    border: focus === item.id ? "1px solid rgba(186, 148, 92, 0.5)" : "1px solid rgba(236,228,216,1)",
                    background: focus === item.id ? "rgba(255,247,235,0.95)" : "#fffdf9",
                  }}
                >
                  <p className="orbit-body-sm" style={{ margin: 0, fontWeight: 700, color: "#352515" }}>
                    {item.title}
                  </p>
                  <p className="orbit-body-xs" style={{ margin: "0.24rem 0 0", color: "#7a6140", lineHeight: "1.6" }}>
                    {item.hint}
                  </p>
                </button>
              ))}
            </div>
          </div>
        </section>

        {featuredItems.length > 0 ? (
          <section className={pl.panel} style={{ padding: "1rem", background: "rgba(255,255,255,0.96)" }}>
            <h2 className="orbit-heading-2" style={{ marginBottom: "0.7rem", color: "#352515" }}>
              {fc.affirmationsFeaturedSectionTitle}
            </h2>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: "0.8rem" }}>
              {featuredItems.map((item) => (
                <div
                  key={`featured-${item.kind}-${item.id}`}
                  style={{
                    padding: "1rem",
                    borderRadius: "18px",
                    background: item.kind === "mantra" ? "linear-gradient(180deg, rgba(250,245,235,0.96), rgba(255,255,255,0.98))" : "linear-gradient(180deg, rgba(255,249,243,0.98), rgba(255,255,255,0.98))",
                    border: "1px solid rgba(198,166,119,0.2)",
                  }}
                >
                  <p className="orbit-body-xs" style={{ margin: 0, color: "#9b7a4b", textTransform: "uppercase", letterSpacing: "0.08em" }}>
                    {item.kind === "mantra" ? fc.affirmationsKindLabelMantra : fc.affirmationsKindLabelAffirmation}
                  </p>
                  <h3 className="orbit-heading-3" style={{ margin: "0.35rem 0 0.45rem", color: "#352515" }}>
                    {item.title}
                  </h3>
                  <p className="orbit-body-sm" style={{ margin: 0, color: "#5f4930", lineHeight: "1.72" }}>
                    {item.body}
                  </p>
                </div>
              ))}
            </div>
          </section>
        ) : null}

        {isAuthenticated && generatedNeed && kind !== "mantra" ? (
          <section className={pl.panel} style={{ padding: "1rem", background: "rgba(255,255,255,0.96)" }}>
            <div style={{ display: "flex", justifyContent: "space-between", gap: "0.8rem", alignItems: "center", flexWrap: "wrap", marginBottom: "0.8rem" }}>
              <div>
                <h2 className="orbit-heading-2" style={{ margin: 0, color: "#352515" }}>
                  {fc.affirmationsPersonalSectionTitle}
                </h2>
                <p className="orbit-body-sm" style={{ margin: "0.28rem 0 0", color: "#7a6140", lineHeight: "1.65" }}>
                  {fc.affirmationsPersonalSectionBody}
                </p>
              </div>
              <button onClick={() => void loadGeneratedAffirmations()} className="orbit-button orbit-button-secondary orbit-button-sm" disabled={generating}>
                {generating ? fc.affirmationsPersonalGenerating : fc.affirmationsPersonalCta}
              </button>
            </div>

            {generatedAffirmations.length > 0 ? (
              <div style={{ display: "grid", gap: "0.75rem", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))" }}>
                {generatedAffirmations.map((item, index) => (
                  <div
                    key={`${item.id}-${index}`}
                    style={{
                      padding: "1rem",
                      borderRadius: "18px",
                      background: "linear-gradient(180deg, rgba(255,248,240,0.98), rgba(255,255,255,0.98))",
                      border: "1px solid rgba(198,166,119,0.2)",
                    }}
                  >
                    <p className="orbit-body-xs" style={{ margin: 0, color: "#9b7a4b", textTransform: "uppercase", letterSpacing: "0.08em" }}>
                      {fc.affirmationsPersonalBadge}
                    </p>
                    <p className="orbit-body-sm" style={{ margin: "0.4rem 0 0", color: "#5f4930", lineHeight: "1.72" }}>
                      {item.text}
                    </p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="orbit-body-sm" style={{ margin: 0, color: "#7a6140", lineHeight: "1.65" }}>
                {fc.affirmationsPersonalEmptyHint}
              </p>
            )}
          </section>
        ) : null}

        <section className={pl.panel} style={{ padding: "1rem", background: "rgba(255,255,255,0.96)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", gap: "0.8rem", alignItems: "baseline", flexWrap: "wrap", marginBottom: "0.8rem" }}>
            <h2 className="orbit-heading-2" style={{ margin: 0, color: "#352515" }}>
              {fc.affirmationsCatalogSectionTitle}
            </h2>
            <p className="orbit-body-sm" style={{ margin: 0, color: "#7a6140" }}>
              {catalogCountLabel}
            </p>
          </div>

          {library.length === 0 ? (
            <div style={{ padding: "1rem", borderRadius: "16px", background: "#fffaf4", border: "1px solid rgba(198,166,119,0.18)" }}>
              <p className="orbit-body" style={{ margin: 0, color: "#6b4f2b", lineHeight: "1.72" }}>
                {fc.affirmationsEmptyFilterHint}
              </p>
            </div>
          ) : (
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "0.8rem" }}>
              {library.map((item) => (
                <article
                  key={`${item.kind}-${item.id}`}
                  style={{
                    padding: "1rem",
                    borderRadius: "18px",
                    background: "#fffdf9",
                    border: "1px solid rgba(236,228,216,1)",
                    display: "grid",
                    gap: "0.7rem",
                  }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", gap: "0.6rem", alignItems: "flex-start" }}>
                    <div>
                      <p className="orbit-body-xs" style={{ margin: 0, color: "#9b7a4b", textTransform: "uppercase", letterSpacing: "0.08em" }}>
                        {item.kind === "mantra" ? fc.affirmationsKindLabelMantra : fc.affirmationsKindLabelAffirmation}
                      </p>
                      <h3 className="orbit-heading-3" style={{ margin: "0.3rem 0 0", color: "#352515" }}>
                        {item.title}
                      </h3>
                    </div>
                  </div>

                  <p className="orbit-body-sm" style={{ margin: 0, color: "#5f4930", lineHeight: "1.72" }}>
                    {item.body}
                  </p>

                  {item.support ? (
                    <p className="orbit-body-xs" style={{ margin: 0, color: "#7a6140", lineHeight: "1.62" }}>
                      {item.support}
                    </p>
                  ) : null}

                  <div style={{ display: "flex", gap: "0.45rem", flexWrap: "wrap" }}>
                    {item.focus.map((focusId) => {
                      const found = focusRows.find((entry) => entry.id === focusId);
                      return found ? (
                        <span
                          key={focusId}
                          className="todayflow-month-pill"
                          style={{ padding: "0.26rem 0.58rem", fontSize: "0.76rem", color: "#7c5a33" }}
                        >
                          {found.title}
                        </span>
                      ) : null;
                    })}
                    {item.tags.slice(0, 3).map((tag) => (
                      <span
                        key={tag}
                        style={{
                          padding: "0.24rem 0.56rem",
                          borderRadius: "999px",
                          background: "rgba(250,245,235,0.95)",
                          color: "#8f6e43",
                          fontSize: "0.76rem",
                        }}
                      >
                        {tag}
                      </span>
                    ))}
                  </div>

                  <div style={{ display: "flex", gap: "0.55rem", flexWrap: "wrap" }}>
                    <Link href={item.href} className="orbit-button orbit-button-primary orbit-button-sm" style={{ textDecoration: "none" }}>
                      {item.hrefLabel}
                    </Link>
                    {item.kind === "affirmation" ? (
                      <Link href="/flow" className="orbit-button orbit-button-secondary orbit-button-sm" style={{ textDecoration: "none" }}>
                        {fc.affirmationsLibraryLinkAllTrackers}
                      </Link>
                    ) : (
                      <Link href="/practices" className="orbit-button orbit-button-secondary orbit-button-sm" style={{ textDecoration: "none" }}>
                        {fc.affirmationsCtaOpenPractices}
                      </Link>
                    )}
                  </div>
                </article>
              ))}
            </div>
          )}
        </section>
    </ProductPageScreen>
  );
}
