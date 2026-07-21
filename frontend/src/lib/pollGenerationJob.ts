import { getJson } from "@/lib/api";
import {
  parseGenerationLifecycle,
  type GenerationLifecycle,
  type GenerationLifecycleStatus,
} from "@/lib/generationLifecycle";

const TERMINAL: GenerationLifecycleStatus[] = ["enriched", "enrichment_failed", "stale"];

export type CompatibilityJobPollResult = {
  lifecycle: GenerationLifecycle;
  product_surface?: unknown;
  generation_source?: string | null;
  score?: number | null;
  summary?: string | null;
  access_disclosure?: unknown;
};

/**
 * Poll Compatibility or Today job until terminal status or timeout.
 * Never blocks first paint — call after baseline is already shown.
 */
export async function pollCompatibilityJob(
  jobId: number,
  options?: { intervalMs?: number; maxMs?: number; signal?: AbortSignal },
): Promise<CompatibilityJobPollResult | null> {
  const intervalMs = options?.intervalMs ?? 1500;
  const maxMs = options?.maxMs ?? 90_000;
  const started = Date.now();

  while (Date.now() - started < maxMs) {
    if (options?.signal?.aborted) return null;
    const data = await getJson<{
      job: Record<string, unknown>;
      product_surface?: unknown;
      generation_source?: string | null;
      score?: number | null;
      summary?: string | null;
      access_disclosure?: unknown;
    }>(`/compatibility/dynamics/jobs/${jobId}`);
    const lifecycle = parseGenerationLifecycle(data.job);
    if (!lifecycle) return null;
    if (TERMINAL.includes(lifecycle.status)) {
      return {
        lifecycle,
        product_surface: data.product_surface,
        generation_source: data.generation_source,
        score: data.score,
        summary: data.summary,
        access_disclosure: data.access_disclosure,
      };
    }
    await new Promise((r) => setTimeout(r, intervalMs));
  }
  return null;
}

export async function pollTodayJob(
  jobId: number,
  options?: { intervalMs?: number; maxMs?: number; signal?: AbortSignal },
): Promise<{ lifecycle: GenerationLifecycle; contract?: unknown } | null> {
  const intervalMs = options?.intervalMs ?? 1500;
  const maxMs = options?.maxMs ?? 90_000;
  const started = Date.now();

  while (Date.now() - started < maxMs) {
    if (options?.signal?.aborted) return null;
    const data = await getJson<{ job: Record<string, unknown>; contract?: unknown }>(
      `/today/jobs/${jobId}`,
    );
    const lifecycle = parseGenerationLifecycle(data.job);
    if (!lifecycle) return null;
    if (TERMINAL.includes(lifecycle.status)) {
      return { lifecycle, contract: data.contract };
    }
    await new Promise((r) => setTimeout(r, intervalMs));
  }
  return null;
}

export async function retryCompatibilityJob(jobId: number): Promise<GenerationLifecycle | null> {
  const { postJson } = await import("@/lib/api");
  const data = await postJson<{ job: Record<string, unknown> }>(
    `/compatibility/dynamics/jobs/${jobId}/retry`,
    {},
  );
  return parseGenerationLifecycle(data.job);
}
