"use client";

import { useCallback, useEffect, useMemo, useState, type CSSProperties } from "react";
import { ApiError, getJson, postJson } from "@/lib/api";
import { useToast } from "@/components/ToastProvider";
import { getWeekStart } from "@/components/today/todayPageUtils";
import { addDaysIsoLocal, monthAnchorIso } from "./calendarHeatmapModel";
import { type TrackerEntityKind, filterAsceticismsByCategory } from "./trackerEntityCatalog";
import {
  getAsceticCategoryFilters,
  getGoalTemplateGroups,
  getHabitTemplateGroups,
} from "@/components/today/trackerEntityTemplateCatalog";
import { getLocale } from "@/lib/i18n";
import { flowTrackerChromeBundle, type FlowPracticesChromeLocale } from "@/components/today/flowPracticesMainTabChrome";

function templateReplace(s: string, vars: Record<string, string | number>) {
  return Object.keys(vars).reduce((acc, k) => acc.replaceAll(`{{${k}}}`, String(vars[k])), s);
}

type AsceticismDto = { id: string; title: string; description: string };

type Step = 1 | 2 | 3;

const panelStyle: CSSProperties = {
  borderRadius: "14px",
  border: "1px solid rgba(198, 166, 119, 0.38)",
  background: "linear-gradient(165deg, rgba(255,252,248,0.99) 0%, rgba(255,244,228,0.92) 100%)",
};

const btnGhost: CSSProperties = {
  padding: "0.4rem 0.75rem",
  borderRadius: "10px",
  border: "1px solid rgba(195, 154, 92, 0.45)",
  background: "rgba(255,250,242,0.95)",
  color: "#6d4f29",
  fontWeight: 600,
  fontSize: "0.82rem",
  cursor: "pointer",
};

const btnPrimary: CSSProperties = {
  ...btnGhost,
  background: "linear-gradient(120deg,#d3b178,#bf975f)",
  color: "#fff8ee",
  border: "1px solid rgba(155, 118, 70, 0.55)",
};

type Props = {
  open: boolean;
  onClose: () => void;
  todayIso: string;
  onCreated: () => void | Promise<void>;
  goalCountWeek: number;
  goalCountMonth: number;
  initialKind?: TrackerEntityKind | null;
};

export function EntityCreateWizard({
  open,
  onClose,
  todayIso,
  onCreated,
  goalCountWeek,
  goalCountMonth,
  initialKind = null,
}: Props) {
  const toast = useToast();
  const locale: FlowPracticesChromeLocale = getLocale() === "ru" ? "ru" : "en";
  const fc = flowTrackerChromeBundle(locale);
  const [step, setStep] = useState<Step>(1);
  const [kind, setKind] = useState<TrackerEntityKind | null>(null);
  const [categoryId, setCategoryId] = useState<string | null>(null);
  const [pickedTitle, setPickedTitle] = useState("");
  const [customTitle, setCustomTitle] = useState("");
  const [goalScope, setGoalScope] = useState<"week" | "month">("week");
  const [habitCadence, setHabitCadence] = useState<"daily" | "weekly">("daily");
  const [habitWeeklyN, setHabitWeeklyN] = useState(4);
  const [asceticDuration, setAsceticDuration] = useState<"open" | "7" | "14" | "21" | "30">("14");
  const [asceticStart, setAsceticStart] = useState(todayIso);
  const [asceticList, setAsceticList] = useState<AsceticismDto[]>([]);
  const [asceticLoading, setAsceticLoading] = useState(false);
  const [selectedAsceticId, setSelectedAsceticId] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const reset = useCallback(() => {
    setStep(1);
    setKind(null);
    setCategoryId(null);
    setPickedTitle("");
    setCustomTitle("");
    setGoalScope("week");
    setHabitCadence("daily");
    setHabitWeeklyN(4);
    setAsceticDuration("14");
    setAsceticStart(todayIso);
    setAsceticList([]);
    setSelectedAsceticId(null);
    setSubmitting(false);
  }, [todayIso]);

  useEffect(() => {
    if (!open) {
      reset();
      return;
    }
    setAsceticStart(todayIso);
    if (initialKind) {
      setKind(initialKind);
      setCategoryId(initialKind === "ascetic" ? "all" : null);
      setStep(2);
    }
  }, [open, initialKind, reset, todayIso]);

  useEffect(() => {
    if (!open || kind !== "ascetic" || step !== 2) return;
    let cancelled = false;
    (async () => {
      try {
        setAsceticLoading(true);
        const data = await getJson<AsceticismDto[]>("/practices/asceticisms");
        if (!cancelled) setAsceticList(Array.isArray(data) ? data : []);
      } catch {
        if (!cancelled) {
          setAsceticList([]);
          toast.error(fc.trackingEntityWizardAsceticCatalogLoadError);
        }
      } finally {
        if (!cancelled) setAsceticLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [open, kind, step, toast, locale, fc]);

  const templateGroups = useMemo(() => {
    if (kind === "goal") return getGoalTemplateGroups(locale);
    if (kind === "habit") return getHabitTemplateGroups(locale);
    return null;
  }, [kind, locale]);

  const asceticCategoryFilters = useMemo(() => getAsceticCategoryFilters(locale), [locale]);

  useEffect(() => {
    if (templateGroups && !categoryId) {
      setCategoryId(templateGroups[0]?.category.id ?? null);
    }
  }, [templateGroups, categoryId]);

  const activeTemplateGroup = useMemo(() => {
    if (!templateGroups || !categoryId) return null;
    return templateGroups.find((g) => g.category.id === categoryId) ?? templateGroups[0];
  }, [templateGroups, categoryId]);

  const asceticFilter = useMemo(() => {
    const f =
      asceticCategoryFilters.find((x) => x.category.id === categoryId) ?? asceticCategoryFilters[0];
    return f;
  }, [asceticCategoryFilters, categoryId]);

  const filteredAscetics = useMemo(() => {
    return filterAsceticismsByCategory(asceticList, asceticFilter.keywords);
  }, [asceticList, asceticFilter]);

  const selectedAscetic = useMemo(
    () => asceticList.find((a) => a.id === selectedAsceticId) ?? null,
    [asceticList, selectedAsceticId],
  );

  const finalTitle = (customTitle.trim() || pickedTitle).trim();
  const weekStart = getWeekStart(todayIso);
  const monthStart = monthAnchorIso(todayIso);

  const goalBlocked =
    kind === "goal" && (goalScope === "week" ? goalCountWeek >= 3 : goalCountMonth >= 3);

  const canProceedFrom2 =
    kind === "ascetic"
      ? !!selectedAsceticId && !!selectedAscetic
      : !!finalTitle && finalTitle.length >= 2;

  const asceticEndIso =
    asceticDuration === "open"
      ? null
      : addDaysIsoLocal(asceticStart, parseInt(asceticDuration, 10) - 1);

  const handleSubmit = async () => {
    if (!kind || goalBlocked) return;
    if (kind !== "ascetic" && finalTitle.length < 2) {
      toast.error(fc.trackingEntityWizardNeedTitleOrPick);
      return;
    }
    try {
      setSubmitting(true);
      if (kind === "goal") {
        const ws = goalScope === "week" ? weekStart : monthStart;
        await postJson("/tracking/weekly-goals", {
          week_start: ws,
          title: finalTitle,
          scope: goalScope,
        });
        toast.success(fc.trackingEntityWizardGoalCreatedSuccess);
      } else if (kind === "habit") {
        await postJson("/habits", {
          name: finalTitle,
          category: activeTemplateGroup?.category.label ?? null,
          target_frequency: habitCadence,
          target_per_period: habitCadence === "daily" ? 1 : habitWeeklyN,
        });
        toast.success(fc.trackingEntityWizardHabitCreatedSuccess);
      } else if (kind === "ascetic" && selectedAscetic) {
        await postJson("/tracking/ascetic-contracts", {
          title: selectedAscetic.title.trim(),
          asceticism_id: selectedAscetic.id,
          intention: selectedAscetic.description?.slice(0, 500) || null,
          start_date: asceticStart,
          end_date: asceticEndIso,
        });
        toast.success(fc.trackingEntityWizardAsceticCreatedSuccess);
      }
      await onCreated();
      onClose();
      reset();
    } catch (e: unknown) {
      const msg = e instanceof ApiError ? e.message : "";
      toast.error(msg || fc.trackingEntityWizardSaveFailed);
    } finally {
      setSubmitting(false);
    }
  };

  if (!open) return null;

  return (
    <div
      role="dialog"
      aria-modal
      aria-labelledby="entity-wizard-title"
      style={{
        position: "fixed",
        inset: 0,
        zIndex: 80,
        background: "rgba(40, 32, 24, 0.48)",
        display: "grid",
        placeItems: "center",
        padding: "1rem",
      }}
      onClick={onClose}
    >
      <div
        className="orbit-card todayflow-panel"
        style={{
          ...panelStyle,
          maxWidth: "440px",
          width: "100%",
          maxHeight: "min(92vh, 720px)",
          overflow: "hidden",
          display: "flex",
          flexDirection: "column",
          padding: "1.05rem 1.1rem",
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: "0.5rem" }}>
          <div>
            <p className="orbit-body-xs" style={{ margin: 0, color: "#8f6e43", letterSpacing: "0.06em", textTransform: "uppercase" }}>
              {templateReplace(fc.trackingEntityWizardStepProgress, { step })}
            </p>
            <h2 id="entity-wizard-title" className="orbit-body" style={{ margin: "0.35rem 0 0", color: "#5f4323", fontWeight: 800 }}>
              {step === 1
                ? fc.trackingEntityWizardStepPickKind
                : step === 2
                  ? fc.trackingEntityWizardStepPickVariant
                  : fc.trackingEntityWizardStepTimingsCreate}
            </h2>
          </div>
          <button type="button" aria-label={fc.close} onClick={onClose} style={{ ...btnGhost, padding: "0.35rem 0.55rem" }}>
            ✕
          </button>
        </div>

        <div style={{ flex: 1, overflowY: "auto", marginTop: "0.85rem", paddingRight: "0.15rem" }}>
          {step === 1 ? (
            <div style={{ display: "grid", gap: "0.55rem" }}>
              {(
                [
                  { id: "goal" as const, t: fc.trackingEntityWizardGoalKindTitle, d: fc.trackingEntityWizardGoalKindDesc },
                  { id: "habit" as const, t: fc.trackingEntityWizardHabitKindTitle, d: fc.trackingEntityWizardHabitKindDesc },
                  { id: "ascetic" as const, t: fc.trackingEntityWizardAsceticKindTitle, d: fc.trackingEntityWizardAsceticKindDesc },
                ] as const
              ).map((row) => (
                <button
                  key={row.id}
                  type="button"
                  onClick={() => {
                    setKind(row.id);
                    setCategoryId(null);
                    setPickedTitle("");
                    setCustomTitle("");
                    setSelectedAsceticId(null);
                    setStep(2);
                  }}
                  style={{
                    textAlign: "left",
                    padding: "0.75rem 0.85rem",
                    borderRadius: "12px",
                    border: "1px solid rgba(195, 154, 92, 0.4)",
                    background: "rgba(255,252,247,0.98)",
                    cursor: "pointer",
                  }}
                >
                  <span className="orbit-body-sm" style={{ fontWeight: 700, color: "#5f4323", display: "block" }}>
                    {row.t}
                  </span>
                  <span className="orbit-body-xs" style={{ color: "#7a6242", lineHeight: 1.45, display: "block", marginTop: "0.25rem" }}>
                    {row.d}
                  </span>
                </button>
              ))}
            </div>
          ) : null}

          {step === 2 && kind && kind !== "ascetic" && activeTemplateGroup ? (
            <div>
              <p className="orbit-body-xs" style={{ margin: "0 0 0.45rem", color: "#7a6242" }}>{fc.trackingEntityWizardCategoryLabel}</p>
              <div style={{ display: "flex", flexWrap: "wrap", gap: "0.35rem", marginBottom: "0.65rem" }}>
                {templateGroups!.map((g) => (
                  <button
                    key={g.category.id}
                    type="button"
                    onClick={() => {
                      setCategoryId(g.category.id);
                      setPickedTitle("");
                    }}
                    style={{
                      padding: "0.32rem 0.6rem",
                      borderRadius: "999px",
                      border:
                        categoryId === g.category.id ? "1px solid rgba(155, 118, 70, 0.75)" : "1px solid rgba(195, 154, 92, 0.35)",
                      background: categoryId === g.category.id ? "linear-gradient(120deg,#d3b178,#bf975f)" : "rgba(255,250,242,0.95)",
                      color: categoryId === g.category.id ? "#fff8ee" : "#6d4f29",
                      fontWeight: 600,
                      fontSize: "0.76rem",
                      cursor: "pointer",
                    }}
                  >
                    {g.category.label}
                  </button>
                ))}
              </div>
              <p className="orbit-body-xs" style={{ margin: "0 0 0.35rem", color: "#8a7760" }}>{activeTemplateGroup.category.description}</p>
              <div style={{ display: "grid", gap: "0.4rem", marginBottom: "0.65rem" }}>
                {activeTemplateGroup.items.map((it) => (
                  <button
                    key={it.title}
                    type="button"
                    onClick={() => {
                      setPickedTitle(it.title);
                      setCustomTitle("");
                    }}
                    style={{
                      textAlign: "left",
                      padding: "0.55rem 0.65rem",
                      borderRadius: "10px",
                      border:
                        pickedTitle === it.title && !customTitle.trim()
                          ? "1px solid rgba(155, 118, 70, 0.75)"
                          : "1px solid rgba(201, 168, 115, 0.28)",
                      background: pickedTitle === it.title && !customTitle.trim() ? "rgba(201, 166, 108, 0.18)" : "rgba(255,255,255,0.65)",
                      cursor: "pointer",
                    }}
                  >
                    <span className="orbit-body-sm" style={{ color: "#5f4323", fontWeight: 600, display: "block" }}>
                      {it.title}
                    </span>
                    {it.hint ? (
                      <span className="orbit-body-xs" style={{ color: "#8a7760", display: "block", marginTop: "0.2rem" }}>
                        {it.hint}
                      </span>
                    ) : null}
                  </button>
                ))}
              </div>
              <label className="orbit-body-xs" style={{ color: "#7a6242", display: "block", marginBottom: "0.3rem" }}>
                {fc.trackingEntityWizardCustomVariantLabel}
              </label>
              <textarea
                value={customTitle}
                onChange={(e) => {
                  setCustomTitle(e.target.value);
                  if (e.target.value.trim()) setPickedTitle("");
                }}
                placeholder={fc.trackingEntityWizardPlaceholderCustomTitle}
                rows={3}
                style={{
                  width: "100%",
                  resize: "vertical",
                  borderRadius: "10px",
                  border: "1px solid rgba(195, 154, 92, 0.4)",
                  padding: "0.5rem 0.6rem",
                  fontFamily: "inherit",
                  fontSize: "0.9rem",
                  color: "#5f4323",
                  background: "#fffdf9",
                }}
              />
            </div>
          ) : null}

          {step === 2 && kind === "ascetic" ? (
            <div>
              <p className="orbit-body-xs" style={{ margin: "0 0 0.45rem", color: "#7a6242" }}>{fc.trackingEntityWizardAsceticDirectionLabel}</p>
              <div style={{ display: "flex", flexWrap: "wrap", gap: "0.35rem", marginBottom: "0.55rem" }}>
                {asceticCategoryFilters.map((g) => (
                  <button
                    key={g.category.id}
                    type="button"
                    onClick={() => {
                      setCategoryId(g.category.id);
                      setSelectedAsceticId(null);
                    }}
                    style={{
                      padding: "0.32rem 0.55rem",
                      borderRadius: "999px",
                      border:
                        asceticFilter.category.id === g.category.id
                          ? "1px solid rgba(155, 118, 70, 0.75)"
                          : "1px solid rgba(195, 154, 92, 0.35)",
                      background:
                        asceticFilter.category.id === g.category.id ? "linear-gradient(120deg,#d3b178,#bf975f)" : "rgba(255,250,242,0.95)",
                      color: asceticFilter.category.id === g.category.id ? "#fff8ee" : "#6d4f29",
                      fontWeight: 600,
                      fontSize: "0.74rem",
                      cursor: "pointer",
                    }}
                  >
                    {g.category.label}
                  </button>
                ))}
              </div>
              {asceticLoading ? (
                <p className="orbit-body-sm" style={{ color: "#8a7760" }}>{fc.trackingEntityWizardLoadingAsceticCatalog}</p>
              ) : filteredAscetics.length === 0 ? (
                <p className="orbit-body-sm" style={{ color: "#a65c2e" }}>{fc.trackingEntityWizardAsceticEmptyCategoryHint}</p>
              ) : (
                <div style={{ display: "grid", gap: "0.4rem", maxHeight: "280px", overflowY: "auto" }}>
                  {filteredAscetics.map((a) => (
                    <button
                      key={a.id}
                      type="button"
                      onClick={() => setSelectedAsceticId(a.id)}
                      style={{
                        textAlign: "left",
                        padding: "0.55rem 0.65rem",
                        borderRadius: "10px",
                        border:
                          selectedAsceticId === a.id ? "1px solid rgba(155, 118, 70, 0.75)" : "1px solid rgba(201, 168, 115, 0.28)",
                        background: selectedAsceticId === a.id ? "rgba(201, 166, 108, 0.18)" : "rgba(255,255,255,0.65)",
                        cursor: "pointer",
                      }}
                    >
                      <span className="orbit-body-sm" style={{ color: "#5f4323", fontWeight: 700, display: "block" }}>
                        {a.title}
                      </span>
                      <span className="orbit-body-xs" style={{ color: "#7a6242", lineHeight: 1.45, display: "block", marginTop: "0.25rem" }}>
                        {a.description}
                      </span>
                    </button>
                  ))}
                </div>
              )}
            </div>
          ) : null}

          {step === 3 && kind ? (
            <div style={{ display: "grid", gap: "0.75rem" }}>
              {kind === "goal" ? (
                <>
                  <p className="orbit-body-sm" style={{ margin: 0, color: "#5f4323", fontWeight: 700 }}>
                    «{finalTitle || "…"}»
                  </p>
                  {goalBlocked ? (
                    <p className="orbit-body-sm" style={{ color: "#a65c2e", margin: 0 }}>
                      {fc.goalLimitReached}
                    </p>
                  ) : null}
                  <div>
                    <p className="orbit-body-xs" style={{ margin: "0 0 0.35rem", color: "#7a6242" }}>{fc.trackingEntityWizardPeriodLabel}</p>
                    <div style={{ display: "flex", flexWrap: "wrap", gap: "0.4rem" }}>
                      <button
                        type="button"
                        onClick={() => setGoalScope("week")}
                        style={{
                          ...btnGhost,
                          background: goalScope === "week" ? "rgba(201, 166, 108, 0.22)" : btnGhost.background,
                        }}
                      >
                        {templateReplace(fc.trackingEntityWizardWeekFrom, { date: weekStart })}
                      </button>
                      <button
                        type="button"
                        onClick={() => setGoalScope("month")}
                        style={{
                          ...btnGhost,
                          background: goalScope === "month" ? "rgba(201, 166, 108, 0.22)" : btnGhost.background,
                        }}
                      >
                        {templateReplace(fc.trackingEntityWizardMonthFrom, { date: monthStart })}
                      </button>
                    </div>
                  </div>
                </>
              ) : null}

              {kind === "habit" ? (
                <>
                  <p className="orbit-body-sm" style={{ margin: 0, color: "#5f4323", fontWeight: 700 }}>
                    «{finalTitle || "…"}»
                  </p>
                  <div>
                    <p className="orbit-body-xs" style={{ margin: "0 0 0.35rem", color: "#7a6242" }}>{fc.trackingEntityWizardRhythmLabel}</p>
                    <div style={{ display: "flex", flexWrap: "wrap", gap: "0.4rem" }}>
                      <button
                        type="button"
                        onClick={() => setHabitCadence("daily")}
                        style={{
                          ...btnGhost,
                          background: habitCadence === "daily" ? "rgba(201, 166, 108, 0.22)" : btnGhost.background,
                        }}
                      >
                        {fc.habitDaily}
                      </button>
                      <button
                        type="button"
                        onClick={() => setHabitCadence("weekly")}
                        style={{
                          ...btnGhost,
                          background: habitCadence === "weekly" ? "rgba(201, 166, 108, 0.22)" : btnGhost.background,
                        }}
                      >
                        {fc.habitWeekly}
                      </button>
                    </div>
                  </div>
                  {habitCadence === "weekly" ? (
                    <label className="orbit-body-xs" style={{ color: "#7a6242", display: "grid", gap: "0.25rem" }}>
                      {fc.trackingEntityWizardHabitWeeklyTargetLabel}
                      <select
                        value={habitWeeklyN}
                        onChange={(e) => setHabitWeeklyN(Number(e.target.value))}
                        style={{
                          borderRadius: "10px",
                          border: "1px solid rgba(195, 154, 92, 0.4)",
                          padding: "0.4rem",
                          color: "#5f4323",
                          background: "#fffdf9",
                        }}
                      >
                        {[3, 4, 5, 6, 7].map((n) => (
                          <option key={n} value={n}>
                            {templateReplace(fc.trackingEntityWizardHabitWeeklyTimes, { n })}
                          </option>
                        ))}
                      </select>
                    </label>
                  ) : null}
                </>
              ) : null}

              {kind === "ascetic" && selectedAscetic ? (
                <>
                  <p className="orbit-body-sm" style={{ margin: 0, color: "#5f4323", fontWeight: 700 }}>
                    {selectedAscetic.title}
                  </p>
                  <label className="orbit-body-xs" style={{ color: "#7a6242", display: "grid", gap: "0.25rem" }}>
                    {fc.trackingEntityWizardStartLabel}
                    <input
                      type="date"
                      value={asceticStart}
                      onChange={(e) => setAsceticStart(e.target.value || todayIso)}
                      style={{
                        borderRadius: "10px",
                        border: "1px solid rgba(195, 154, 92, 0.4)",
                        padding: "0.4rem",
                        color: "#5f4323",
                        background: "#fffdf9",
                      }}
                    />
                  </label>
                  <div>
                    <p className="orbit-body-xs" style={{ margin: "0 0 0.35rem", color: "#7a6242" }}>{fc.trackingEntityWizardAsceticDurationContractLabel}</p>
                    <div style={{ display: "flex", flexWrap: "wrap", gap: "0.35rem" }}>
                      {(
                        [
                          ["open", fc.trackingEntityWizardAsceticDurationOpen],
                          ["7", fc.trackingEntityWizardAsceticDurationDays7],
                          ["14", fc.trackingEntityWizardAsceticDurationDays14],
                          ["21", fc.trackingEntityWizardAsceticDurationDays21],
                          ["30", fc.trackingEntityWizardAsceticDurationDays30],
                        ] as const
                      ).map(([id, lab]) => (
                        <button
                          key={id}
                          type="button"
                          onClick={() => setAsceticDuration(id)}
                          style={{
                            ...btnGhost,
                            fontSize: "0.76rem",
                            background: asceticDuration === id ? "rgba(201, 166, 108, 0.22)" : btnGhost.background,
                          }}
                        >
                          {lab}
                        </button>
                      ))}
                    </div>
                  </div>
                  {asceticEndIso ? (
                    <p className="orbit-body-xs" style={{ margin: 0, color: "#8a7760" }}>
                      {templateReplace(fc.trackingEntityWizardAsceticEndUntil, { date: asceticEndIso })}
                    </p>
                  ) : (
                    <p className="orbit-body-xs" style={{ margin: 0, color: "#8a7760" }}>
                      {fc.trackingEntityWizardAsceticEndOpenHint}
                    </p>
                  )}
                </>
              ) : null}
            </div>
          ) : null}
        </div>

        <div style={{ display: "flex", flexWrap: "wrap", gap: "0.45rem", marginTop: "0.85rem", paddingTop: "0.65rem", borderTop: "1px solid rgba(201, 168, 115, 0.22)" }}>
          {step > 1 ? (
            <button
              type="button"
              onClick={() => {
                if (step === 2) {
                  setStep(1);
                  setKind(null);
                  setCategoryId(null);
                  setPickedTitle("");
                  setCustomTitle("");
                  setSelectedAsceticId(null);
                  return;
                }
                setStep(2);
              }}
              style={btnGhost}
            >
              {fc.trackingEntityWizardBack}
            </button>
          ) : (
            <span style={{ flex: 1 }} />
          )}
          {step === 2 ? (
            <button type="button" disabled={!canProceedFrom2} onClick={() => setStep(3)} style={{ ...btnPrimary, opacity: canProceedFrom2 ? 1 : 0.45 }}>
              {fc.trackingEntityWizardNextTimings}
            </button>
          ) : null}
          {step === 3 ? (
            <button
              type="button"
              disabled={submitting || goalBlocked || (kind !== "ascetic" && finalTitle.length < 2)}
              onClick={() => void handleSubmit()}
              style={{
                ...btnPrimary,
                opacity: submitting || goalBlocked || (kind !== "ascetic" && finalTitle.length < 2) ? 0.45 : 1,
              }}
            >
              {submitting ? fc.trackingEntityWizardSaving : fc.trackingEntityWizardCreateCta}
            </button>
          ) : null}
        </div>
      </div>
    </div>
  );
}
