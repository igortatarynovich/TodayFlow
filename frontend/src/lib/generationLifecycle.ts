/** Shared C1 generation lifecycle statuses (Compatibility + Today). */

export type GenerationLifecycleStatus =
  | "baseline_ready"
  | "enrichment_pending"
  | "enriched"
  | "enrichment_failed"
  | "stale";

export type GenerationLifecycle = {
  contract_version?: string;
  status: GenerationLifecycleStatus;
  job_id?: number | null;
  fingerprint?: string | null;
  source?: string;
  is_fully_personal?: boolean;
  error?: string | null;
};

export function parseGenerationLifecycle(raw: unknown): GenerationLifecycle | null {
  if (!raw || typeof raw !== "object") return null;
  const o = raw as Record<string, unknown>;
  const status = String(o.status || "");
  if (
    status !== "baseline_ready" &&
    status !== "enrichment_pending" &&
    status !== "enriched" &&
    status !== "enrichment_failed" &&
    status !== "stale"
  ) {
    return null;
  }
  return {
    contract_version: typeof o.contract_version === "string" ? o.contract_version : undefined,
    status,
    job_id: typeof o.job_id === "number" ? o.job_id : null,
    fingerprint: typeof o.fingerprint === "string" ? o.fingerprint : null,
    source: typeof o.source === "string" ? o.source : undefined,
    is_fully_personal: Boolean(o.is_fully_personal),
    error: typeof o.error === "string" ? o.error : null,
  };
}

export function lifecycleStatusLabel(status: GenerationLifecycleStatus, locale = "ru"): string {
  const ru = !locale.startsWith("en");
  switch (status) {
    case "enrichment_pending":
      return ru ? "Дополняем разбор…" : "Enriching…";
    case "enriched":
      return ru ? "Полный разбор готов" : "Full reading ready";
    case "enrichment_failed":
      return ru ? "Не удалось дополнить — можно повторить" : "Enrichment failed — retry available";
    case "stale":
      return ru ? "Обновляем под новые данные…" : "Updating for new inputs…";
    default:
      return ru ? "Базовый разбор" : "Baseline reading";
  }
}
