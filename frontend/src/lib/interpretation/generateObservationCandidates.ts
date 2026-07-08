import {
  frameForLens,
  normText,
  signNarrativeToYou,
  splitSentences,
  textSimilarity,
  toSecondPerson,
} from "@/lib/interpretation/formatRecognitionText";
import { polishRussianCopy } from "@/lib/interpretation/polishRussianCopy";
import type {
  ObservationCandidate,
  ObservationEvidence,
  ObservationSource,
  OnboardingRecognitionLens,
} from "@/lib/interpretation/onboardingRecognitionTypes";
import { SOURCE_WEIGHT } from "@/lib/interpretation/onboardingRecognitionTypes";
import type { BirthSignalContext } from "@/lib/interpretation/resolveBirthSignals";

type RawCandidate = {
  id: string;
  lens: OnboardingRecognitionLens;
  text: string;
  source: ObservationSource;
  referenceKey: string;
  strength?: number;
};

function evidenceKey(source: ObservationSource, referenceKey: string): string {
  return `${source}::${referenceKey}`;
}

function buildEvidence(
  source: ObservationSource,
  referenceKey: string,
  strength = 1,
): ObservationEvidence {
  const weight = SOURCE_WEIGHT[source];
  return {
    source,
    referenceKey,
    weight,
    contribution: weight * strength,
  };
}

function pushRaw(out: RawCandidate[], seen: Set<string>, candidate: RawCandidate): void {
  const key = `${candidate.lens}::${normText(candidate.text)}`;
  if (seen.has(key)) return;
  seen.add(key);
  out.push(candidate);
}

function pushFromTexts(
  out: RawCandidate[],
  seen: Set<string>,
  texts: string[],
  meta: Omit<RawCandidate, "id" | "text">,
  idPrefix: string,
): void {
  texts.forEach((text, index) => {
    const trimmed = text.trim();
    if (!trimmed || trimmed.length < 12) return;
    pushRaw(out, seen, {
      ...meta,
      id: `${idPrefix}-${index}`,
      text: trimmed,
    });
  });
}

function composeTensionFromPhrases(phrases: string[]): string | null {
  const clean = phrases.map((p) => p.trim()).filter(Boolean);
  if (clean.length === 0) return null;

  const lowered = clean.map((p) => p.toLowerCase());
  const hasFreedom = lowered.some((p) => p.includes("свобод") || p.includes("огранич") || p.includes("контрол"));
  const hasFramework = lowered.some((p) => p.includes("рамк") || p.includes("как надо") || p.includes("стандарт"));

  if (hasFreedom && hasFramework) {
    return "Сложнее всего бывает, когда приходится выбирать между стабильностью и свободой.";
  }

  if (clean.length === 1) {
    return `Сложнее всего бывает, когда включается ${clean[0].toLowerCase()}.`;
  }

  return `Сложнее всего бывает, когда одновременно включаются ${clean[0].toLowerCase()} и ${clean[1].toLowerCase()}.`;
}

export function generateObservationCandidates(ctx: BirthSignalContext): ObservationCandidate[] {
  const raw: RawCandidate[] = [];
  const seen = new Set<string>();

  pushFromTexts(
    raw,
    seen,
    ctx.sunEntry?.bullets ?? [],
    { lens: "noticed_by_others", source: "natal.sun", referenceKey: "sun.bullets" },
    "sun-bullet",
  );

  if (ctx.signEntry?.communication) {
    pushRaw(raw, seen, {
      id: "sign-communication",
      lens: "noticed_by_others",
      text: toSecondPerson(ctx.signEntry.communication),
      source: "natal.sign",
      referenceKey: "sign.communication",
    });
  }

  if (ctx.signEntry?.conflict) {
    pushRaw(raw, seen, {
      id: "sign-conflict",
      lens: "noticed_by_others",
      text: toSecondPerson(ctx.signEntry.conflict),
      source: "natal.sign",
      referenceKey: "sign.conflict",
    });
  }

  if (ctx.signEntry?.work) {
    pushFromTexts(
      raw,
      seen,
      splitSentences(ctx.signEntry.work).map(toSecondPerson),
      { lens: "strengthens", source: "natal.sign", referenceKey: "sign.work" },
      "sign-work",
    );
  }

  if (ctx.signEntry?.decisions) {
    pushRaw(raw, seen, {
      id: "sign-decisions-strength",
      lens: "strengthens",
      text: toSecondPerson(ctx.signEntry.decisions),
      source: "natal.sign",
      referenceKey: "sign.decisions",
    });
  }

  if (ctx.lpEntry?.driver) {
    pushRaw(raw, seen, {
      id: "lp-driver",
      lens: "strengthens",
      text: ctx.lpEntry.driver,
      source: "numerology.life_path",
      referenceKey: "life_path.driver",
    });
  }

  if (ctx.lpEntry?.pattern) {
    pushRaw(raw, seen, {
      id: "lp-pattern",
      lens: "strengthens",
      text: ctx.lpEntry.pattern,
      source: "numerology.life_path",
      referenceKey: "life_path.pattern",
    });
  }

  if (ctx.lpEntry?.life_theme) {
    pushRaw(raw, seen, {
      id: "lp-life-theme",
      lens: "noticed_by_others",
      text: ctx.lpEntry.life_theme,
      source: "numerology.life_path",
      referenceKey: "life_path.life_theme",
    });
  }

  if (ctx.lpEntry?.essence) {
    pushRaw(raw, seen, {
      id: "lp-essence",
      lens: "noticed_by_others",
      text: ctx.lpEntry.essence,
      source: "numerology.life_path",
      referenceKey: "life_path.essence",
      strength: 0.9,
    });
  }

  pushFromTexts(
    raw,
    seen,
    ctx.lpEntry?.plus_side ?? [],
    { lens: "strengthens", source: "numerology.life_path", referenceKey: "life_path.plus_side", strength: 0.85 },
    "lp-plus",
  );

  pushFromTexts(
    raw,
    seen,
    ctx.lpEntry?.money_work?.slice(0, 2) ?? [],
    { lens: "strengthens", source: "numerology.life_path", referenceKey: "life_path.money_work" },
    "lp-money",
  );

  pushFromTexts(
    raw,
    seen,
    ctx.lpEntry?.minus_side ?? [],
    { lens: "tension", source: "numerology.life_path", referenceKey: "life_path.minus_side" },
    "lp-minus",
  );

  if (ctx.lpEntry?.main_fear) {
    pushRaw(raw, seen, {
      id: "lp-main-fear",
      lens: "tension",
      text: ctx.lpEntry.main_fear,
      source: "numerology.life_path",
      referenceKey: "life_path.main_fear",
    });
  }

  pushFromTexts(
    raw,
    seen,
    ctx.lpEntry?.relationships?.slice(2, 3) ?? [],
    { lens: "tension", source: "numerology.life_path", referenceKey: "life_path.relationships" },
    "lp-rel-tension",
  );

  const signTension = composeTensionFromPhrases([
    ...(ctx.signEntry?.dislikes?.slice(0, 2) ?? []),
    ...(ctx.signEntry?.watchouts?.slice(0, 1) ?? []),
  ]);
  if (signTension) {
    pushRaw(raw, seen, {
      id: "sign-tension-composed",
      lens: "tension",
      text: signTension,
      source: "natal.sign",
      referenceKey: "sign.dislikes",
    });
  }

  if (ctx.signEntry?.hurts?.length) {
    const hurtsTension = composeTensionFromPhrases(ctx.signEntry.hurts.slice(0, 2));
    if (hurtsTension) {
      pushRaw(raw, seen, {
        id: "sign-hurts-tension",
        lens: "tension",
        text: hurtsTension,
        source: "natal.sign",
        referenceKey: "sign.hurts",
      });
    }
  }

  if (ctx.lpEntry?.growth) {
    pushRaw(raw, seen, {
      id: "lp-growth",
      lens: "recovery",
      text: ctx.lpEntry.growth,
      source: "numerology.life_path",
      referenceKey: "life_path.growth",
    });
  }

  if (ctx.lpEntry?.lesson) {
    pushRaw(raw, seen, {
      id: "lp-lesson",
      lens: "recovery",
      text: ctx.lpEntry.lesson,
      source: "numerology.life_path",
      referenceKey: "life_path.lesson",
      strength: 0.9,
    });
  }

  if (ctx.signEntry?.support) {
    pushRaw(raw, seen, {
      id: "sign-support",
      lens: "recovery",
      text: ctx.signEntry.support,
      source: "natal.sign",
      referenceKey: "sign.support",
    });
  }

  if (ctx.signEntry?.growth) {
    pushRaw(raw, seen, {
      id: "sign-growth",
      lens: "recovery",
      text: signNarrativeToYou(ctx.signEntry.growth, ctx.signEntry.ruName),
      source: "natal.sign",
      referenceKey: "sign.growth",
    });
  }

  pushFromTexts(
    raw,
    seen,
    (ctx.lpEntry?.reading ?? []).map((line) => line.trim().replace(/^и\s+/i, "")),
    { lens: "today_focus", source: "numerology.life_path", referenceKey: "life_path.reading" },
    "lp-reading",
  );

  pushFromTexts(
    raw,
    seen,
    ctx.lpEntry?.watchouts?.slice(0, 2).map((w) => `не распыляться на ${w.toLowerCase()}`) ?? [],
    { lens: "today_focus", source: "numerology.life_path", referenceKey: "life_path.watchouts", strength: 0.75 },
    "lp-watchout-today",
  );

  if (ctx.signEntry?.decisions) {
    const decisions = toSecondPerson(ctx.signEntry.decisions).replace(/^Ты\s+/i, "");
    pushRaw(raw, seen, {
      id: "sign-decisions-today",
      lens: "today_focus",
      text: `не решать на эмоциях — ${decisions.charAt(0).toLowerCase()}${decisions.slice(1)}`,
      source: "natal.sign",
      referenceKey: "sign.decisions.today",
      strength: 0.7,
    });
  }

  const withEvidence: ObservationCandidate[] = raw.map((item) => {
    const evidence = [buildEvidence(item.source, item.referenceKey, item.strength ?? 1)];
    return {
      id: item.id,
      lens: item.lens,
      text: polishRussianCopy(frameForLens(item.lens, item.text)),
      evidence,
      score: evidence.reduce((sum, e) => sum + e.contribution, 0),
    };
  });

  return mergeReinforcedCandidates(withEvidence, ctx);
}

function mergeReinforcedCandidates(
  candidates: ObservationCandidate[],
  ctx: BirthSignalContext,
): ObservationCandidate[] {
  const merged: ObservationCandidate[] = [];

  for (const candidate of candidates) {
    const existing = merged.find((m) => m.lens === candidate.lens && textSimilarity(m.text, candidate.text) >= 0.42);
    if (!existing) {
      merged.push({ ...candidate, evidence: [...candidate.evidence] });
      continue;
    }

    for (const ev of candidate.evidence) {
      const dup = existing.evidence.some((e) => evidenceKey(e.source, e.referenceKey) === evidenceKey(ev.source, ev.referenceKey));
      if (!dup) existing.evidence.push(ev);
    }

    if (candidate.text.length > existing.text.length) {
      existing.text = candidate.text;
    }
    existing.score = scoreFromEvidence(existing.evidence);
  }

  return applyCycleReinforcement(merged, ctx);
}

function scoreFromEvidence(evidence: ObservationEvidence[]): number {
  const bySource = new Map<ObservationSource, number>();
  for (const item of evidence) {
    const prev = bySource.get(item.source) ?? 0;
    bySource.set(item.source, Math.max(prev, item.contribution));
  }
  return Array.from(bySource.values()).reduce((sum, v) => sum + v, 0);
}

function applyCycleReinforcement(
  candidates: ObservationCandidate[],
  ctx: BirthSignalContext,
): ObservationCandidate[] {
  if (ctx.personalYear == null && ctx.personalDay == null) return candidates;

  return candidates.map((candidate) => {
    const extra: ObservationEvidence[] = [];

    if (ctx.personalYear != null && candidate.lens === "today_focus") {
      extra.push(buildEvidence("numerology.personal_year", `numerology.personal_year.${ctx.personalYear}`, 0.85));
    }

    if (ctx.personalDay != null && candidate.lens === "today_focus") {
      extra.push(buildEvidence("calendar.personal_day", `calendar.personal_day.${ctx.personalDay}`, 0.9));
    }

    if (ctx.personalYear != null && ctx.lpEntry?.number === ctx.personalYear) {
      extra.push(buildEvidence("numerology.personal_year", "numerology.personal_year.resonance", 1));
    }

    if (extra.length === 0) return candidate;

    const evidence = [...candidate.evidence];
    for (const ev of extra) {
      if (!evidence.some((e) => evidenceKey(e.source, e.referenceKey) === evidenceKey(ev.source, ev.referenceKey))) {
        evidence.push(ev);
      }
    }

    return {
      ...candidate,
      evidence,
      score: scoreFromEvidence(evidence),
    };
  });
}
