import type { TodayFourArea } from "@/components/today/todayFourAreas";
import { RITUAL_COPY, textsSemanticallyRedundant } from "@/components/today/todayRitualCopy";

export type SphereTriadRow = {
  area: "work" | "love" | "money";
  stance: "up" | "down" | "neutral";
  line: string;
};

function narrativeString(payload: Record<string, unknown> | null | undefined, key: string): string | null {
  if (!payload || typeof payload !== "object") return null;
  const v = payload[key];
  return typeof v === "string" && v.trim() ? v.trim() : null;
}

export function parseCoreMessageFromGuide(payload: Record<string, unknown> | null | undefined): string | null {
  const raw = payload?.["core_message"];
  if (raw && typeof raw === "object" && !Array.isArray(raw)) {
    const o = raw as Record<string, unknown>;
    const body =
      (typeof o.body === "string" && o.body.trim()) ||
      (typeof o.main_text === "string" && o.main_text.trim()) ||
      (typeof o.message === "string" && o.message.trim()) ||
      "";
    if (body) {
      const parts: string[] = [body];
      const risk = (typeof o.risk === "string" && o.risk.trim()) || (typeof o.main_risk === "string" && o.main_risk.trim()) || "";
      const move =
        (typeof o.best_move === "string" && o.best_move.trim()) ||
        (typeof o.first_move === "string" && o.first_move.trim()) ||
        "";
      if (risk) parts.push(`Риск: ${risk}`);
      if (move) parts.push(`Лучший ход: ${move}`);
      return parts.join("\n\n");
    }
  }
  const flat = narrativeString(payload, "core_message");
  return flat || null;
}

/** Объект `core_message` из API (предпочтительный контракт) или разбор строки. */
export type ParsedCoreMessageForUi =
  | {
      kind: "structured";
      headline?: string;
      body: string;
      risk?: string;
      best_move?: string;
    }
  | { kind: "paragraphs"; paragraphs: string[] };

export function parseCoreMessageForUi(payload: Record<string, unknown> | null | undefined): ParsedCoreMessageForUi | null {
  const raw = payload?.["core_message"];
  if (raw && typeof raw === "object" && !Array.isArray(raw)) {
    const o = raw as Record<string, unknown>;
    const body =
      (typeof o.body === "string" && o.body.trim()) ||
      (typeof o.main_text === "string" && o.main_text.trim()) ||
      (typeof o.message === "string" && o.message.trim()) ||
      "";
    if (body) {
      let headline =
        (typeof o.headline === "string" && o.headline.trim()) || (typeof o.title === "string" && o.title.trim()) || undefined;
      let risk =
        (typeof o.risk === "string" && o.risk.trim()) || (typeof o.main_risk === "string" && o.main_risk.trim()) || undefined;
      let best_move =
        (typeof o.best_move === "string" && o.best_move.trim()) ||
        (typeof o.first_move === "string" && o.first_move.trim()) ||
        (typeof o.action_hint === "string" && o.action_hint.trim()) ||
        undefined;
      if (headline && textsSemanticallyRedundant(headline, body)) headline = undefined;
      if (risk && textsSemanticallyRedundant(risk, body)) risk = undefined;
      if (best_move && textsSemanticallyRedundant(best_move, body)) best_move = undefined;
      if (risk && best_move && textsSemanticallyRedundant(risk, best_move)) risk = undefined;
      if (best_move && headline && textsSemanticallyRedundant(best_move, headline)) best_move = undefined;
      return { kind: "structured", headline, body, risk, best_move };
    }
  }
  const flat = narrativeString(payload, "core_message");
  if (!flat) return null;
  const paragraphs = flat
    .split(/\n\s*\n/)
    .map((p) => p.trim())
    .filter(Boolean)
    .slice(0, 4);
  return paragraphs.length ? { kind: "paragraphs", paragraphs } : null;
}

export type TodayGuideActionOption = {
  title: string;
  reason?: string;
  estimated_minutes?: number;
  entity_kind?: string;
};

function narrativeStringFromUnknown(v: unknown): string | null {
  return typeof v === "string" && v.trim() ? v.trim() : null;
}

export function parseActionOptionsRich(payload: Record<string, unknown> | null | undefined): TodayGuideActionOption[] {
  if (!payload || typeof payload !== "object") return [];
  const raw = payload["action_options"];
  if (!Array.isArray(raw)) return [];
  const out: TodayGuideActionOption[] = [];
  for (const x of raw) {
    if (typeof x === "string") {
      const t = x.trim();
      if (t) out.push({ title: t });
    } else if (x && typeof x === "object" && !Array.isArray(x)) {
      const o = x as Record<string, unknown>;
      const title =
        narrativeStringFromUnknown(o.title) ||
        narrativeStringFromUnknown(o.label) ||
        narrativeStringFromUnknown(o.text);
      if (title) {
        out.push({
          title,
          reason: narrativeStringFromUnknown(o.reason) || narrativeStringFromUnknown(o.why) || undefined,
          estimated_minutes:
            typeof o.estimated_minutes === "number" && Number.isFinite(o.estimated_minutes)
              ? o.estimated_minutes
              : typeof o.minutes === "number" && Number.isFinite(o.minutes)
                ? o.minutes
                : undefined,
          entity_kind:
            typeof o.entity_kind === "string"
              ? o.entity_kind
              : typeof o.creates === "string"
                ? o.creates
                : undefined,
        });
      }
    }
    if (out.length >= 3) break;
  }
  return out;
}

export function parseActionOptionsFromGuide(payload: Record<string, unknown> | null | undefined): string[] {
  return parseActionOptionsRich(payload).map((o) => o.title);
}

function doItemsFromGuidePayload(payload: Record<string, unknown> | null | undefined): string[] {
  if (!payload || typeof payload !== "object") return [];
  const raw = payload["do_items"];
  if (!Array.isArray(raw)) return [];
  return raw.map((x) => (typeof x === "string" ? x.trim() : "")).filter(Boolean).slice(0, 6);
}

/**
 * O9: один канонический «главный шаг» для UI — `best_move` → первый `action_options` → первый `do_items`.
 * Паритет iOS `TodayGuideActionable.guideCanonicalPrimaryStepLine`.
 */
export function guideCanonicalPrimaryStepLine(
  payload: Record<string, unknown> | null | undefined,
  doItemsFallback: readonly string[],
  literalFallback: string,
): string {
  const core = parseCoreMessageForUi(payload);
  if (core?.kind === "structured") {
    const bm = core.best_move?.trim();
    if (bm) return bm;
  }
  const opts = parseActionOptionsRich(payload);
  if (opts.length > 0 && opts[0].title.trim()) return opts[0].title.trim();
  const dos = doItemsFromGuidePayload(payload);
  if (dos.length > 0) return dos[0].trim();
  for (const x of doItemsFallback) {
    const t = String(x || "").trim();
    if (t) return t;
  }
  return literalFallback.trim() || RITUAL_COPY.guidePrimaryDoFallback;
}

export function parseSupportHooksFromGuide(payload: Record<string, unknown> | null | undefined): string[] {
  if (!payload || typeof payload !== "object") return [];
  const raw = payload["support_hooks"];
  if (!Array.isArray(raw)) return [];
  return raw.map((x) => (typeof x === "string" ? x.trim() : "")).filter(Boolean).slice(0, 3);
}

/** O2: паритет бэка `narrative_hierarchy` в guide payload. */
export type NarrativeHierarchyForUi = {
  contractVersion: "narrative_hierarchy_v0";
  primaryAnchorKey: "day_engine_brief";
};

export function parseNarrativeHierarchyFromGuide(
  payload: Record<string, unknown> | null | undefined,
): NarrativeHierarchyForUi | null {
  if (!payload || typeof payload !== "object") return null;
  const raw = payload["narrative_hierarchy"];
  if (!raw || typeof raw !== "object" || Array.isArray(raw)) return null;
  const h = raw as Record<string, unknown>;
  if (h.contract_version !== "narrative_hierarchy_v0") return null;
  if (h.primary_anchor !== "day_engine_brief") return null;
  return { contractVersion: "narrative_hierarchy_v0", primaryAnchorKey: "day_engine_brief" };
}

/** DE-13 v5: паритет бэка `guide_pipeline` в guide payload (`guide_contract_v2`). */
export type GuidePipelineForUi = {
  contractVersion: "guide_pipeline_v0";
  generationMode: "funnel" | "monolith";
  coreSource?: string;
};

export function parseGuidePipelineFromGuide(
  payload: Record<string, unknown> | null | undefined,
): GuidePipelineForUi | null {
  if (!payload || typeof payload !== "object") return null;
  if (payload.contract_version !== "guide_contract_v2") return null;
  const raw = payload["guide_pipeline"];
  if (!raw || typeof raw !== "object" || Array.isArray(raw)) return null;
  const p = raw as Record<string, unknown>;
  if (p.contract_version !== "guide_pipeline_v0") return null;
  const mode = p.generation_mode;
  if (mode !== "funnel" && mode !== "monolith") return null;
  const steps = p.steps;
  let coreSource: string | undefined;
  if (steps && typeof steps === "object" && !Array.isArray(steps)) {
    const core = (steps as Record<string, unknown>).core_text;
    if (core && typeof core === "object" && !Array.isArray(core)) {
      const src = (core as Record<string, unknown>).source;
      if (typeof src === "string" && src.trim()) coreSource = src.trim();
    }
  }
  return { contractVersion: "guide_pipeline_v0", generationMode: mode, coreSource };
}

/** Паритет с `day_engine_brief` в payload guide. */
export type DayEngineBriefForUi = {
  anchor: string;
  hints: string[];
};

export function parseDayEngineBriefFromGuide(payload: Record<string, unknown> | null | undefined): DayEngineBriefForUi | null {
  if (!payload || typeof payload !== "object") return null;
  const raw = payload["day_engine_brief"];
  if (!raw || typeof raw !== "object" || Array.isArray(raw)) return null;
  const b = raw as Record<string, unknown>;
  const anchor = typeof b.anchor_summary === "string" ? b.anchor_summary.trim() : "";
  if (!anchor) return null;
  const hints = (["do_hint", "avoid_hint", "tempo_hint"] as const)
    .map((k) => (typeof b[k] === "string" ? (b[k] as string).trim() : ""))
    .filter(Boolean);
  return { anchor, hints };
}

/** Паритет с `day_model_v0` в payload guide / DayContext.layers.day_model. */
export type DayModelBriefForUi = {
  contractVersion: string;
  oneFocus: string;
  vectorSummary?: string;
  tensionSummary?: string;
  riskSummary?: string;
  tempoLabel?: string;
};

function nestedString(o: unknown, path: [string, string]): string | undefined {
  if (!o || typeof o !== "object" || Array.isArray(o)) return undefined;
  const inner = (o as Record<string, unknown>)[path[0]];
  if (!inner || typeof inner !== "object" || Array.isArray(inner)) return undefined;
  const v = (inner as Record<string, unknown>)[path[1]];
  return typeof v === "string" && v.trim() ? v.trim() : undefined;
}

export function parseDayModelBriefFromGuide(payload: Record<string, unknown> | null | undefined): DayModelBriefForUi | null {
  if (!payload || typeof payload !== "object") return null;
  const raw = payload["day_model"];
  if (!raw || typeof raw !== "object" || Array.isArray(raw)) return null;
  const dm = raw as Record<string, unknown>;
  if (dm["contract_version"] !== "day_model_v0") return null;
  const oneFocus = nestedString(dm, ["strategy", "one_focus"]);
  if (!oneFocus) return null;
  const vectorSummary = nestedString(dm, ["vector", "summary"]);
  const tensionSummary = nestedString(dm, ["tension", "summary"]);
  const riskSummary = nestedString(dm, ["risk", "summary"]);
  const scales = dm["scales"];
  let tempoLabel: string | undefined;
  if (scales && typeof scales === "object" && !Array.isArray(scales)) {
    const t = (scales as Record<string, unknown>)["tempo"];
    if (typeof t === "string" && t.trim()) tempoLabel = t.trim();
  }
  return {
    contractVersion: "day_model_v0",
    oneFocus,
    vectorSummary,
    tensionSummary,
    riskSummary,
    tempoLabel,
  };
}

function isTriadRow(x: unknown): x is SphereTriadRow {
  if (!x || typeof x !== "object") return false;
  const r = x as Record<string, unknown>;
  const area = String(r.area || "").toLowerCase();
  const stance = String(r.stance || "").toLowerCase();
  const line = String(r.line || "").trim();
  return (area === "work" || area === "love" || area === "money") && (stance === "up" || stance === "down" || stance === "neutral") && line.length > 4;
}

export function parseSphereTriadFromGuide(payload: Record<string, unknown> | null | undefined): SphereTriadRow[] | null {
  if (!payload || typeof payload !== "object") return null;
  const raw = payload["sphere_triad"];
  if (!Array.isArray(raw) || raw.length !== 3) return null;
  const rows = raw.map((x) => (isTriadRow(x) ? x : null)).filter((x): x is SphereTriadRow => x != null);
  if (rows.length !== 3) return null;
  const areas = new Set(rows.map((r) => r.area));
  if (areas.size !== 3) return null;
  return rows;
}

/** Если в payload нет sphere_triad — строим из трёх сфер по score (сильная / слабая / нейтральная). */
export function sphereTriadFallbackFromAreas(areas: TodayFourArea[], relationshipLabel: string): SphereTriadRow[] {
  const pick = (id: "work" | "love" | "money") => areas.find((a) => a.id === id);
  const triple = [
    { id: "work" as const, a: pick("work") },
    { id: "love" as const, a: pick("love") },
    { id: "money" as const, a: pick("money") },
  ].filter((x) => x.a) as { id: "work" | "love" | "money"; a: TodayFourArea }[];
  if (triple.length !== 3) return [];
  const sorted = [...triple].sort((x, y) => y.a.score - x.a.score);
  const strong = sorted[0]!;
  const weak = sorted[2]!;
  const mid = sorted[1]!;
  const label = (id: "work" | "love" | "money", a: TodayFourArea) => (id === "love" ? relationshipLabel : a.label);
  const line = (id: "work" | "love" | "money", a: TodayFourArea, stance: SphereTriadRow["stance"]) => {
    const head = label(id, a);
    const tail = a.todayHeadline?.trim() || a.insight?.trim() || "";
    if (stance === "up") return tail ? `${head} — сейчас лучшее место для движения: ${tail}` : `${head} — сейчас лучшее место для движения.`;
    if (stance === "down")
      return tail ? `${head} — аккуратно, не дави: ${tail}` : `${head} — аккуратно, не дави — лучше сказать прямо, чем угадывать.`;
    return tail ? `${head} — нейтрально: ${tail}` : `${head} — нейтрально, без лишнего импульса.`;
  };
  return [
    { area: strong.id, stance: "up", line: line(strong.id, strong.a, "up") },
    { area: weak.id, stance: "down", line: line(weak.id, weak.a, "down") },
    { area: mid.id, stance: "neutral", line: line(mid.id, mid.a, "neutral") },
  ];
}
