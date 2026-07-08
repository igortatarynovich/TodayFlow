import type { TodayContractV1 } from "@/lib/todayContract";

export function hasAuthoritativeDayStory(contract: TodayContractV1): boolean {
  const ds = contract.day_story;
  if (!ds) return false;
  return Boolean(
    (ds.story && ds.story.trim()) ||
      (ds.theme && ds.theme.trim()) ||
      (ds.direction && ds.direction.trim()),
  );
}

export function dayStoryHeadline(contract: TodayContractV1): string | null {
  const ds = contract.day_story;
  if (!ds) return null;
  const theme = (ds.theme || "").trim();
  if (theme) return theme;
  const story = (ds.story || "").trim();
  if (!story) return null;
  const first = story.match(/^[^.!?]+[.!?]?/);
  return (first?.[0] ?? story.slice(0, 120)).trim();
}

export function dayStoryPrimaryAction(contract: TodayContractV1): string | null {
  const move = (contract.day_story?.today_move || "").trim();
  if (move) return move;
  const action = (contract.primary_action || "").trim();
  return action || null;
}

export function dayStoryParagraphs(contract: TodayContractV1): string[] {
  const story = (contract.day_story?.story || "").trim();
  if (!story) return [];
  return story
    .split(/\n+/)
    .flatMap((block) => block.split(/(?<=[.!?])\s+/))
    .map((s) => s.trim())
    .filter((s) => s.length > 12);
}

export function dayStoryDoItems(contract: TodayContractV1): string[] {
  const items = contract.day_story?.do;
  return Array.isArray(items) ? items.map((x) => String(x).trim()).filter(Boolean) : [];
}

export function dayStoryAvoidItems(contract: TodayContractV1): string[] {
  const items = contract.day_story?.avoid;
  return Array.isArray(items) ? items.map((x) => String(x).trim()).filter(Boolean) : [];
}

/** Web Today: один канонический голос — только `contract.day_story`, без overlay guide/spheres/evening. */
export function usesDayStorySingleVoice(contract: TodayContractV1 | null | undefined): boolean {
  if (!contract) return false;
  return hasAuthoritativeDayStory(contract);
}

export function parseContractGenerationId(contract: TodayContractV1 | null | undefined): number | null {
  const raw = contract?.generation_id?.trim();
  if (!raw) return null;
  const n = Number(raw);
  return Number.isFinite(n) && n > 0 ? Math.trunc(n) : null;
}

export function dayStoryPulseLine(contract: TodayContractV1): string | null {
  const direction = contract.day_story?.direction?.trim();
  if (direction && direction.length >= 12) {
    return direction.endsWith(".") ? direction : `${direction}.`;
  }
  const advantage = contract.day_story?.advantage?.trim();
  if (advantage && advantage.length >= 12) {
    return advantage.endsWith(".") ? advantage : `${advantage}.`;
  }
  return null;
}

export function dayStoryEveningPrompt(contract: TodayContractV1): string | null {
  const note = contract.day_story?.symbolic_note?.trim();
  if (note) return note;
  const abstain = contract.day_story?.abstain?.trim();
  if (abstain) return `Перед сном: ${abstain.replace(/[.!?]+$/, "")}.`;
  return null;
}

export function dayStoryLeadParagraph(contract: TodayContractV1): string | null {
  const paragraphs = dayStoryParagraphs(contract);
  return paragraphs[0] ?? null;
}

export function dayStoryWhyLines(contract: TodayContractV1): string[] {
  const paragraphs = dayStoryParagraphs(contract);
  if (paragraphs.length >= 2) {
    return paragraphs.slice(1, 4);
  }
  const lines: string[] = [];
  const doItems = dayStoryDoItems(contract);
  const avoidItems = dayStoryAvoidItems(contract);
  if (doItems.length) lines.push(`Сегодня усилить: ${doItems.slice(0, 2).join("; ")}.`);
  if (avoidItems.length) lines.push(`Лучше не дожимать: ${avoidItems.slice(0, 2).join("; ")}.`);
  return lines;
}

export function dayStoryActionTitles(contract: TodayContractV1): string[] {
  const primary = dayStoryPrimaryAction(contract);
  const fromDo = dayStoryDoItems(contract);
  const out: string[] = [];
  if (primary) out.push(primary);
  for (const item of fromDo) {
    if (!out.includes(item)) out.push(item);
  }
  if (!out.length && contract.primary_action?.trim()) {
    out.push(contract.primary_action.trim());
  }
  return out.slice(0, 3);
}

export function dayStoryEveningPayload(contract: TodayContractV1): Record<string, unknown> | null {
  const prompt = dayStoryEveningPrompt(contract);
  return prompt ? { closure_invitation: prompt } : null;
}
