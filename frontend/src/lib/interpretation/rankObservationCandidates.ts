import { normText, textSimilarity } from "@/lib/interpretation/formatRecognitionText";
import type { ObservationCandidate } from "@/lib/interpretation/onboardingRecognitionTypes";
import {
  LENS_SELECTION_ORDER,
  MIN_RECOGNITION_SCORE,
  TARGET_RECOGNITION_COUNT,
} from "@/lib/interpretation/onboardingRecognitionTypes";

function distinctiveness(candidate: ObservationCandidate, selected: ObservationCandidate[]): number {
  if (selected.length === 0) return candidate.score;
  const maxSim = Math.max(...selected.map((s) => textSimilarity(s.text, candidate.text)), 0);
  return candidate.score * (1 - maxSim * 0.65);
}

export function rankObservationCandidates(candidates: ObservationCandidate[]): ObservationCandidate[] {
  const eligible = candidates.filter(
    (c) => c.score >= MIN_RECOGNITION_SCORE && c.evidence.length > 0 && c.text.trim().length >= 18,
  );

  const byScore = [...eligible].sort((a, b) => b.score - a.score || a.id.localeCompare(b.id));

  const selected: ObservationCandidate[] = [];
  const usedIds = new Set<string>();

  for (const lens of LENS_SELECTION_ORDER) {
    const best = byScore
      .filter((c) => c.lens === lens && !usedIds.has(c.id))
      .sort((a, b) => distinctiveness(b, selected) - distinctiveness(a, selected))[0];
    if (best) {
      selected.push(best);
      usedIds.add(best.id);
    }
  }

  const pool = byScore.filter((c) => !usedIds.has(c.id));
  while (selected.length < TARGET_RECOGNITION_COUNT && pool.length > 0) {
    pool.sort((a, b) => distinctiveness(b, selected) - distinctiveness(a, selected));
    const next = pool.shift();
    if (!next) break;
    if (selected.some((s) => normText(s.text) === normText(next.text))) continue;
    selected.push(next);
    usedIds.add(next.id);
  }

  return selected.slice(0, TARGET_RECOGNITION_COUNT);
}
