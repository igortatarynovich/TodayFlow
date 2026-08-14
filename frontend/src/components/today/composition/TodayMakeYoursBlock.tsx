"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";
import { ApiError, getJson, postJson } from "@/lib/api";
import { TodayProgressTracker } from "@/components/today/composition/TodayProgressTracker";
import {
  getAsceticCategoryFilters,
  getGoalTemplateGroups,
  getHabitTemplateGroups,
} from "@/components/today/trackerEntityTemplateCatalog";
import { filterAsceticismsByCategory } from "@/app/tracking/calendar/trackerEntityCatalog";
import { getWeekStart } from "@/components/today/todayPageUtils";
import type { TodayProgressRow } from "@/lib/todayGrowthTrackers";
import type { MakeYoursCategoryId, MakeYoursProposal } from "@/lib/todayMakeYoursProposals";
import { useToast } from "@/components/ToastProvider";
import {
  DsBody,
  DsCaption,
  DsChip,
  DsChipCluster,
  DsContentCard,
  DsListPanel,
  DsListRow,
} from "@/design-system";
import layout from "@/design-system/compositions/dsCompositions.module.css";

type CatalogItem = { id: string; title: string; hint?: string | null };

type AffirmationRow = { id: string; text?: string; title?: string };
type MantraRow = {
  id?: string;
  title?: string;
  mantra?: string;
  notes?: string;
  pronunciation?: string;
  intention?: string;
};
type AsceticismDto = { id: string; title: string; description: string };

const CATEGORY_CHIPS: { id: MakeYoursCategoryId; label: string }[] = [
  { id: "ascetic", label: "Аскеза" },
  { id: "affirmation", label: "Аффирмация" },
  { id: "mantra", label: "Мантра" },
  { id: "habit", label: "Привычка" },
  { id: "goal", label: "Цель" },
];

const PICK_COPY: Record<MakeYoursCategoryId, { lead: string; cta: string }> = {
  ascetic: { lead: "Выбери ограничение на сегодня", cta: "Поставить" },
  affirmation: { lead: "Выбери аффирмацию", cta: "Взять" },
  mantra: { lead: "Выбери мантру", cta: "Взять" },
  habit: { lead: "Закрепи привычку", cta: "Поставить" },
  goal: { lead: "Поставь цель", cta: "Поставить" },
};

type Props = {
  dateISO: string;
  progressRows: TodayProgressRow[];
  proposals: MakeYoursProposal[];
  occupiedCategoryIds: string[];
  onChanged?: () => void | Promise<void>;
};

/**
 * Make yours — Form Kit chips + list picks (TODAY_MAKE_YOURS_AND_WELCOME_SOT).
 */
export function TodayMakeYoursBlock({
  dateISO,
  progressRows,
  proposals,
  occupiedCategoryIds,
  onChanged,
}: Props) {
  const toast = useToast();
  const occupied = useMemo(() => new Set(occupiedCategoryIds), [occupiedCategoryIds]);
  const [active, setActive] = useState<MakeYoursCategoryId | null>(null);
  const [items, setItems] = useState<CatalogItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [savingId, setSavingId] = useState<string | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);

  const habitTemplates = useMemo(() => {
    const groups = getHabitTemplateGroups("ru");
    const out: CatalogItem[] = [];
    for (const g of groups) {
      for (const it of g.items.slice(0, 2)) {
        out.push({ id: `habit:${g.category.id}:${it.title}`, title: it.title, hint: it.hint });
      }
      if (out.length >= 8) break;
    }
    return out.slice(0, 8);
  }, []);

  const goalTemplates = useMemo(() => {
    const groups = getGoalTemplateGroups("ru");
    const out: CatalogItem[] = [];
    for (const g of groups.slice(0, 3)) {
      for (const it of g.items.slice(0, 2)) {
        out.push({ id: `goal:${g.category.id}:${it.title}`, title: it.title, hint: it.hint });
      }
    }
    return out.slice(0, 6);
  }, []);

  const loadCatalog = useCallback(
    async (category: MakeYoursCategoryId) => {
      setLoading(true);
      setLoadError(null);
      setItems([]);
      try {
        if (category === "habit") {
          setItems(habitTemplates);
          return;
        }
        if (category === "goal") {
          setItems(goalTemplates);
          return;
        }
        if (category === "affirmation") {
          const data = await getJson<AffirmationRow[]>("/practices/affirmations");
          const rows = Array.isArray(data) ? data : [];
          setItems(
            rows.slice(0, 8).map((r) => ({
              id: r.id,
              title: String(r.title || r.text || "").trim() || r.id,
              hint: r.text && r.title ? String(r.text).trim() : null,
            })),
          );
          return;
        }
        if (category === "mantra") {
          const data = await getJson<MantraRow[]>("/reference/mantras");
          const rows = Array.isArray(data) ? data : [];
          setItems(
            rows.slice(0, 8).map((r, i) => {
              const id = String(r.id || `mantra-${i}`).trim();
              const title =
                String(r.title || r.mantra || r.notes || r.intention || "").trim() || id;
              return {
                id,
                title,
                hint: r.pronunciation ? String(r.pronunciation).trim() : null,
              };
            }),
          );
          return;
        }
        if (category === "ascetic") {
          const data = await getJson<AsceticismDto[]>("/practices/asceticisms");
          const rows = (Array.isArray(data) ? data : []).map((r) => ({
            ...r,
            description: r.description ?? "",
          }));
          const filter = getAsceticCategoryFilters("ru")[0];
          const filtered = filterAsceticismsByCategory(rows, filter?.keywords ?? []);
          const list = (filtered.length ? filtered : rows).slice(0, 8);
          setItems(
            list.map((r) => ({
              id: r.id,
              title: r.title,
              hint: r.description ? String(r.description).slice(0, 80) : null,
            })),
          );
        }
      } catch {
        setLoadError("Не удалось загрузить.");
        setItems([]);
      } finally {
        setLoading(false);
      }
    },
    [goalTemplates, habitTemplates],
  );

  useEffect(() => {
    if (!active) return;
    void loadCatalog(active);
  }, [active, loadCatalog]);

  const onSelectCategory = (id: string) => {
    const cat = id as MakeYoursCategoryId;
    if (!CATEGORY_CHIPS.some((c) => c.id === cat)) return;
    setActive((prev) => (prev === cat ? null : cat));
  };

  const onPick = async (item: CatalogItem) => {
    if (!active || savingId) return;
    setSavingId(item.id);
    try {
      if (active === "habit") {
        await postJson("/habits", {
          name: item.title,
          category: null,
          target_frequency: "daily",
          target_per_period: 1,
        });
        toast.success("Привычка поставлена");
      } else if (active === "goal") {
        await postJson("/tracking/weekly-goals", {
          week_start: getWeekStart(dateISO),
          title: item.title,
          scope: "week",
        });
        toast.success("Цель поставлена");
      } else if (active === "ascetic") {
        await postJson("/tracking/ascetic-contracts", {
          title: item.title.trim(),
          asceticism_id: item.id,
          intention: item.hint?.slice(0, 500) || null,
          start_date: dateISO,
          end_date: null,
        });
        toast.success("Аскеза поставлена");
      } else if (active === "affirmation") {
        await postJson("/tracking/progress", {
          date: dateISO,
          asceticism_id: null,
          affirmation_id: item.id,
          completed: false,
          state: null,
          state_scale: null,
          note: null,
        });
        toast.success("Аффирмация выбрана");
      } else if (active === "mantra") {
        toast.success(`Мантра: ${item.title}`);
      }
      setActive(null);
      await onChanged?.();
    } catch (e: unknown) {
      const msg = e instanceof ApiError ? e.message : "";
      toast.error(msg || "Не удалось сохранить.");
    } finally {
      setSavingId(null);
    }
  };

  const proposalForActive = active
    ? proposals.find((p) => p.categoryId === active) ?? null
    : null;

  const pickedLabel = (id: MakeYoursCategoryId): string | null => {
    if (occupied.has(id)) return "есть";
    const prop = proposals.find((p) => p.categoryId === id);
    return prop?.title ?? null;
  };

  return (
    <div className={layout.stack} data-testid="today-make-yours">
      <DsChipCluster testId="today-make-yours-categories">
        {CATEGORY_CHIPS.map((c) => {
          const label = pickedLabel(c.id);
          return (
            <DsChip
              key={c.id}
              selected={active === c.id}
              testId={`today-make-yours-cat-${c.id}`}
              onClick={() => onSelectCategory(c.id)}
            >
              {c.label}
              {label ? ` · ${label}` : ""}
            </DsChip>
          );
        })}
      </DsChipCluster>

      {active ? (
        <DsContentCard
          tone="glass"
          testId={`today-make-yours-pick-${active}`}
          eyebrow={PICK_COPY[active].lead}
          body={proposalForActive?.title || undefined}
          chips={
            <div className={layout.stack}>
              {loading ? <DsCaption>…</DsCaption> : null}
              {loadError ? <DsCaption>{loadError}</DsCaption> : null}
              {!loading && !loadError && items.length === 0 ? (
                <DsCaption>Пока пусто в каталоге.</DsCaption>
              ) : null}
              <DsListPanel tone="subtle">
                {items.slice(0, 3).map((it) => (
                  <DsListRow
                    key={it.id}
                    title={it.title}
                    subtitle={
                      it.hint
                        ? `${it.hint} · ${savingId === it.id ? "…" : PICK_COPY[active].cta}`
                        : savingId === it.id
                          ? "…"
                          : PICK_COPY[active].cta
                    }
                    testId={`today-make-yours-item-${it.id}`}
                    onClick={() => {
                      if (!savingId) void onPick(it);
                    }}
                  />
                ))}
              </DsListPanel>
            </div>
          }
        />
      ) : null}

      {progressRows.length > 0 ? (
        <TodayProgressTracker rows={progressRows} title="Твой прогресс" />
      ) : null}

      {progressRows.length === 0 && proposals.length === 0 && !active ? (
        <DsBody size="sm">
          <span data-testid="today-make-yours-empty">
            Выбери категорию выше — или открой <Link href="/tracking/calendar">календарь</Link>
            {" · "}
            <Link href="/affirmations">аффирмации</Link>
          </span>
        </DsBody>
      ) : null}
    </div>
  );
}
