/**
 * Phase C2 — Today story chapters from day_scenario (Level 1) + interpretive_chorus (Level 2).
 *
 * Prefer when scenario is ready; otherwise caller falls back to Day Map / legacy narrative.
 * Legacy expect/trap/do slots are not read as meaning here — only scenario nests + soft vibe.
 *
 * Canon: docs/DAY_SCENARIO_V1.md · docs/audits/DAY_SCENARIO_CHAPTERS_C2.md
 */

import type { TodayContractV1 } from "@/lib/todayContract";
import type { TodayDayColorGuide } from "@/lib/todayDayColorGuide";
import type { TodayDayNarrativeChapter } from "@/lib/todayDayNarrative";

function clean(text: string | null | undefined): string {
  return (text ?? "").replace(/\s+/g, " ").trim();
}

/** Strip mashed "A или B — пока <fact…>" / calendar glue from cached short_name / theme. */
export function sanitizeConflictLabel(text: string | null | undefined): string {
  let t = clean(text);
  if (!t) return "";
  const mashed = t.match(/^(.+?\s+или\s+.+?)\s+[—–-]\s+(?:пока\s+|календарн)/iu);
  if (mashed?.[1]) t = mashed[1].trim();
  if (/\sили\s/iu.test(t) && /\s+[—–-]\s+/.test(t)) {
    const [before, after = ""] = t.split(/\s+[—–-]\s+/);
    if (
      before &&
      /\sили\s/iu.test(before) &&
      (/^пока\s/iu.test(after) || /календарн/iu.test(after) || after.includes("…"))
    ) {
      t = before.trim();
    }
  }
  if (t.includes("…") && /\sили\s/iu.test(t)) {
    const before = t.split(/\s+[—–-]\s+/)[0]?.trim();
    if (before && /\sили\s/iu.test(before)) t = before;
  }
  return t.replace(/[.!?]+$/u, "").trim();
}

function isKitchenNatalLead(text: string): boolean {
  return /Firdaria|ZR\s*Fortune|ZR\s*Spirit|Лоты\s*soft|Vimshottari|BaZi|HD\s*soft|Variables\s*soft|Solar\s*return|time[_\s-]?lords|управител|нет\s+ASC/i.test(
    text,
  );
}

/** Calendar DOY — date already in greeting chrome; never user-facing day prose. */
export function isCalendarKitchenFact(text: string | null | undefined): boolean {
  return /календарн\w*\s+день|\d+-й\s+день\s+года|день\s+года\s+\d+|calendar-doy/i.test(
    clean(text),
  );
}

/** Decorative chip hex — mirrors todayDayNarrative.colorHexForDayName (no runtime import cycle). */
function colorHexForDayName(name: string | null | undefined): string | null {
  const n = (name ?? "").trim().toLowerCase();
  if (!n) return null;
  const map: Array<[RegExp, string]> = [
    [/лазур|azure|голуб/, "#5B8FA8"],
    [/глубок.*син|deep.*blue/, "#1E3A5F"],
    [/индиго|indigo/, "#3F3D7A"],
    [/изумруд|emerald|зелён|зелен/, "#2F6B4F"],
    [/янтар|amber/, "#C9893A"],
    [/коралл|coral/, "#E07A6A"],
    [/бордов|burgundy|винн/, "#7A2E3C"],
    [/перламутр|pearl/, "#D8D2C8"],
    [/золот|gold/, "#C9A96E"],
    [/серебр|silver/, "#A8B0B8"],
    [/син|blue/, "#3D6E9C"],
    [/красн|red/, "#A83C3C"],
    [/фиолет|violet|purple/, "#6B4C8A"],
    [/розов|pink/, "#C97A9A"],
    [/оранж|orange/, "#D4783A"],
    [/бел|white|cream|слонов/, "#F4EFE6"],
    [/чёрн|черн|black/, "#2A2520"],
  ];
  for (const [re, hex] of map) {
    if (re.test(n)) return hex;
  }
  return "#8B6A3E";
}

function nearDuplicate(a: string, b: string): boolean {
  const x = a.toLowerCase().replace(/\s+/g, " ").trim();
  const y = b.toLowerCase().replace(/\s+/g, " ").trim();
  if (!x || !y) return false;
  if (x === y) return true;
  if (x.length >= 24 && y.includes(x.slice(0, Math.min(48, x.length)))) return true;
  if (y.length >= 24 && x.includes(y.slice(0, Math.min(48, y.length)))) return true;
  return false;
}

function pushDistinct(out: string[], used: string[], line: string | null | undefined): void {
  const t = clean(line);
  if (!t) return;
  const key = t.toLowerCase();
  if (used.some((u) => u.toLowerCase() === key || nearDuplicate(u, t))) return;
  used.push(t);
  out.push(t);
}

/** Scenario ready for C2 chapters: conflict + ≥1 scene, not unavailable. */
export function isDayScenarioReadyForChapters(contract: TodayContractV1): boolean {
  const story = contract.day_story;
  if (!story) return false;
  if (String(story.interpretation_status || "").trim() === "unavailable") return false;
  const scenario = story.day_scenario;
  if (!scenario || typeof scenario !== "object") return false;
  if (scenario.ready === false) return false;
  const conflict = scenario.conflict;
  const scenes = Array.isArray(scenario.scenes) ? scenario.scenes : [];
  const hasConflict = Boolean(clean(conflict?.short_name) || clean(conflict?.why_arose));
  return hasConflict && scenes.length > 0;
}

/**
 * Five product chapters:
 * 1 opening — Что изменилось сегодня
 * 2 chorus — Почему именно так
 * 3 scenes — Где это проявится
 * 4 supports — Что поможет пройти день
 * 5 vibe — Чем закончится день
 */
export type ScenarioSymbolImpact = {
  title?: string | null;
  headline?: string | null;
  body?: string | null;
};

export function buildScenarioStoryChapters(input: {
  contract: TodayContractV1;
  colorGuide?: TodayDayColorGuide | null;
  /** Revealed ritual overlay — complements chorus; day_story is not reassembled. */
  tarotImpact?: ScenarioSymbolImpact | null;
  numberImpact?: ScenarioSymbolImpact | null;
}): TodayDayNarrativeChapter[] | null {
  if (!isDayScenarioReadyForChapters(input.contract)) return null;

  const dayStory = input.contract.day_story!;
  const scenario = dayStory.day_scenario!;
  const conflict = scenario.conflict ?? {};
  const scenes = (scenario.scenes ?? []).filter((s) => s && typeof s === "object");
  const props = scenario.props ?? {};
  const chorus = dayStory.interpretive_chorus;
  const used: string[] = [];
  const chapters: TodayDayNarrativeChapter[] = [];
  const tarotImpact = input.tarotImpact ?? null;
  const numberImpact = input.numberImpact ?? null;
  const hasLiveSymbols = Boolean(
    (tarotImpact && (clean(tarotImpact.title) || clean(tarotImpact.body))) ||
      (numberImpact && (clean(numberImpact.title) || clean(numberImpact.body))),
  );

  const title =
    sanitizeConflictLabel(conflict.short_name) ||
    sanitizeConflictLabel(dayStory.theme) ||
    sanitizeConflictLabel(dayStory.primary_conflict);
  const whyArose = clean(conflict.why_arose);
  const whyPersonal = clean(conflict.why_personal);
  const forces = conflict.opposing_forces;
  const forceLine =
    clean(forces?.a) && clean(forces?.b)
      ? `Натяжение между «${clean(forces?.a)}» и «${clean(forces?.b)}».`
      : "";

  // 1 — Что изменилось сегодня
  const openingParas: string[] = [];
  if (title) pushDistinct(openingParas, used, title);
  if (whyArose && !isCalendarKitchenFact(whyArose) && !nearDuplicate(whyArose, title)) {
    pushDistinct(openingParas, used, whyArose);
  }
  if (forceLine) pushDistinct(openingParas, used, forceLine);
  if (
    whyPersonal &&
    !isKitchenNatalLead(whyPersonal) &&
    !nearDuplicate(whyPersonal, whyArose)
  ) {
    pushDistinct(openingParas, used, whyPersonal);
  }
  // Soft factual lead from projection if not already covered (never calendar DOY).
  const eventsLead = clean(dayStory.events_lead);
  if (
    eventsLead &&
    !isCalendarKitchenFact(eventsLead) &&
    !nearDuplicate(eventsLead, whyArose) &&
    !nearDuplicate(eventsLead, title)
  ) {
    pushDistinct(openingParas, used, eventsLead);
  }
  if (openingParas.length) {
    chapters.push({
      id: "opening",
      kicker: "Что изменилось сегодня",
      lead: openingParas[0] ?? null,
      paragraphs: openingParas.slice(1),
      accent: "sky",
      collapseAfter: openingParas.length > 3 ? 2 : undefined,
    });
  }

  // 2 — Почему именно так (chorus)
  if (chorus) {
    const paras: string[] = [];
    const astro = clean(chorus.astrology_lead);
    const astroMeaning = clean(chorus.astrology_meaning);
    if (astro && astroMeaning) {
      pushDistinct(paras, used, `${astro}. ${astroMeaning}`);
    } else if (astro) {
      pushDistinct(paras, used, astro);
    } else if (astroMeaning) {
      pushDistinct(paras, used, astroMeaning);
    }
    // Live reveal beats stale/redacted chorus card·number (DAY_SYMBOL_REVEAL overlay).
    if (!hasLiveSymbols) {
      const card = chorus.day_card;
      if (card?.named) {
        const role = clean(card.role);
        pushDistinct(paras, used, role ? `${clean(card.named)}. ${role}` : clean(card.named));
      }
      const number = chorus.day_number;
      if (number?.named) {
        const tempo = clean(number.for_conflict) || clean(number.tempo);
        pushDistinct(paras, used, tempo ? `${clean(number.named)}. ${tempo}` : clean(number.named));
      }
    }
    const natal = clean(chorus.natal_lead);
    if (natal && !isKitchenNatalLead(natal)) pushDistinct(paras, used, natal);
    if (paras.length) {
      chapters.push({
        id: "chorus",
        kicker: "Почему именно так",
        lead: paras[0] ?? null,
        paragraphs: paras.slice(1),
        accent: "sky",
        collapseAfter: paras.length > 3 ? 2 : undefined,
      });
    }
  }

  // 2b — Открытые символы (после reveal остаются в чтении)
  if (hasLiveSymbols) {
    const symbolParas: string[] = [];
    if (tarotImpact) {
      const title = clean(tarotImpact.title);
      const head = clean(tarotImpact.headline);
      const body = clean(tarotImpact.body);
      if (title || head) {
        pushDistinct(
          symbolParas,
          used,
          title && head ? `Карта дня — ${title}. ${head}` : title ? `Карта дня — ${title}` : head,
        );
      }
      if (body) pushDistinct(symbolParas, used, body);
    }
    if (numberImpact) {
      const title = clean(numberImpact.title);
      const head = clean(numberImpact.headline);
      const body = clean(numberImpact.body);
      if (title || head) {
        pushDistinct(
          symbolParas,
          used,
          title && head ? `Число дня — ${title}. ${head}` : title ? `Число дня — ${title}` : head,
        );
      }
      if (body) pushDistinct(symbolParas, used, body);
    }
    if (symbolParas.length) {
      chapters.push({
        id: "symbols",
        kicker: "Карта и число дня",
        lead: symbolParas[0] ?? null,
        paragraphs: symbolParas.slice(1),
        accent: "default",
        collapseAfter: symbolParas.length > 3 ? 2 : undefined,
      });
    }
  }

  // 3 — Где это проявится (scenes)
  // Conflict axis is already in opening — scenes show lived sphere moments only.
  // Opportunity/trap: once in dual for primary; never paste identical templates under each sphere.
  const primary =
    scenes.find((s) => s.role_in_story === "primary") ?? scenes[0] ?? null;
  const sceneParas: string[] = [];
  const strengthen: string[] = [];
  const soften: string[] = [];

  const looksLikeForcePaste = (text: string | null | undefined): boolean => {
    const t = clean(text);
    if (!t) return false;
    return (
      /^Шанс выбрать «.+» именно здесь/i.test(t) ||
      /тот же выбор — «/i.test(t) ||
      /день упирается в выбор: «/i.test(t) ||
      /^Ловушка — скатиться в «/i.test(t)
    );
  };

  for (const sc of scenes) {
    const label = clean(sc.sphere_label_ru) || clean(sc.sphere) || "Сфера дня";
    const what = clean(sc.what_happens);
    const domestic = clean(sc.domestic_example);
    const opportunity = clean(sc.opportunity);
    const trap = clean(sc.trap);
    // Prefer lived domestic; skip what when it only restates the conflict labels.
    const leadLine = looksLikeForcePaste(what) ? domestic : [what, domestic].filter(Boolean).join(" ");
    if (leadLine && !looksLikeForcePaste(leadLine)) {
      pushDistinct(sceneParas, used, `${label}. ${leadLine}`);
    } else if (domestic) {
      pushDistinct(sceneParas, used, `${label}. ${domestic}`);
    }
    if (sc === primary || sc.role_in_story === "primary") {
      if (opportunity && !looksLikeForcePaste(opportunity) && !nearDuplicate(opportunity, leadLine)) {
        strengthen.push(opportunity);
      }
      if (trap && !looksLikeForcePaste(trap) && !nearDuplicate(trap, leadLine)) {
        soften.push(trap);
      }
    }
  }

  if (sceneParas.length || strengthen.length || soften.length) {
    chapters.push({
      id: "scenes",
      kicker: "Где это проявится",
      lead: sceneParas[0] ?? null,
      paragraphs: sceneParas.slice(1),
      accent: strengthen.length || soften.length ? "dual" : "default",
      dual:
        strengthen.length || soften.length
          ? { strengthen: strengthen.slice(0, 2), soften: soften.slice(0, 2) }
          : null,
      collapseAfter: sceneParas.length > 3 ? 2 : undefined,
    });
  }

  // 4 — Что поможет пройти день
  const supportParas: string[] = [];
  const supportUsed = new Set(used.map((u) => u.toLowerCase()));
  const pushSupport = (line: string | null | undefined) => {
    const t = clean(line);
    if (!t || supportUsed.has(t.toLowerCase()) || nearDuplicate(t, title)) return;
    supportUsed.add(t.toLowerCase());
    used.push(t);
    supportParas.push(t.endsWith(".") || t.endsWith("!") ? t : `${t}.`);
  };

  for (const sc of scenes) {
    pushSupport(sc.recommended_action);
    const avoid = clean(sc.do_not);
    if (avoid) {
      pushSupport(
        avoid.startsWith("Не ") || avoid.startsWith("не ")
          ? avoid
          : `Не ${avoid.replace(/[.!?]+$/, "")}`,
      );
    }
  }

  const goals = Array.isArray(props.goals) ? props.goals : [];
  for (const g of goals.slice(0, 2)) {
    if (g && typeof g === "object") pushSupport(g.text);
  }

  const talisman = dayStory.talisman;
  const colorName =
    clean(input.colorGuide?.name) ||
    clean(props.color?.name) ||
    clean(talisman?.color);
  const colorWhy =
    clean(input.colorGuide?.benefit) ||
    clean(props.color?.link_to_conflict) ||
    clean(talisman?.note);
  if (colorName) {
    pushSupport(colorWhy ? `Цвет дня — ${colorName}. ${colorWhy}` : `Цвет дня — ${colorName}`);
  }
  const avoidColor = clean(talisman?.avoid_color) || clean(props.avoid_color?.name);
  const avoidWhyRaw = clean(talisman?.avoid_why) || clean(props.avoid_color?.why);
  const avoidWhy =
    avoidWhyRaw && avoidWhyRaw.length > 140
      ? `${avoidWhyRaw.slice(0, 137).replace(/\s+\S*$/, "")}…`
      : avoidWhyRaw;
  if (avoidColor) {
    pushSupport(avoidWhy ? `Избегать: ${avoidColor} — ${avoidWhy}` : `Избегать: ${avoidColor}`);
  }

  const affirm = dayStory.practice_recommendation;
  if (affirm?.text) {
    // Show affirmation alone — do not paste trap/reason dumps in parentheses.
    pushSupport(clean(affirm.text));
  } else if (Array.isArray(props.affirmations) && props.affirmations[0]?.text) {
    pushSupport(props.affirmations[0].text);
  }

  if (supportParas.length) {
    chapters.push({
      id: "supports",
      kicker: "Что поможет пройти день",
      lead: supportParas[0] ?? null,
      paragraphs: supportParas.slice(1),
      accent: "support",
      colorHex: colorHexForDayName(colorName),
      colorLabel: colorName || null,
      collapseAfter: supportParas.length > 4 ? 3 : undefined,
    });
  }

  // 5 — Чем закончится день
  const vibeParas: string[] = [];
  const evening = clean(dayStory.evening_closure);
  const vibe = clean(dayStory.vibe_closing);
  const strokes = Array.isArray(dayStory.vibe_strokes)
    ? dayStory.vibe_strokes.map((s) => clean(s)).filter(Boolean)
    : [];
  if (evening) pushDistinct(vibeParas, used, evening);
  if (vibe && !nearDuplicate(vibe, evening)) pushDistinct(vibeParas, used, vibe);
  for (const s of strokes) {
    if (!nearDuplicate(s, evening) && !nearDuplicate(s, vibe)) pushDistinct(vibeParas, used, s);
  }
  if (!vibeParas.length && title) {
    pushDistinct(
      vibeParas,
      used,
      `Если удержали «${title}» — к вечеру яснее, где выбрали осознанно.`,
    );
  }
  if (vibeParas.length) {
    chapters.push({
      id: "vibe",
      kicker: "Чем закончится день",
      lead: vibeParas[0] ?? null,
      paragraphs: vibeParas.slice(1),
      accent: "default",
    });
  }

  return chapters.length ? chapters : null;
}
