# Today — Welcome glass · Progress · Make yours (SoT)

**Status:** ACTIVE · 2026-08-09  
**Presentation:** [TODAY_SCREEN_SCENARIO_V3](./TODAY_SCREEN_SCENARIO_V3.md) v3.3 handoff  
**Rule:** FE may **compose** existing signals; may **not invent** calm/product copy on empty or transport failure.

---

## 1. Priority (product note)

Handoff prototype step «Приоритет» = **6 two-line cards** (label + sub-label, 2-col, single-select).  
Live product = **`TODAY_FOCUS_TOPICS`** (8 single-line chips) in morning dialogue — SoT for focus id remains engagement `focusTopicId` + meaning `head_topic_selected`.  
Layout upgrade to 6 two-line cards is **FE-only** and optional; meaning contract unchanged.

---

## 2. Welcome glass — signal map

UI: 2 mood pills · 1 reason line · ≤3 activity («good for») chips · CTA.

| UI slot | Source of truth | How composed | Where it goes / affects |
|---------|-----------------|--------------|-------------------------|
| **Mood pills (2)** | `contract.day_atmosphere.visual_mode` (Day Atmosphere SoT) | Closed map `visual_mode → [adj1, adj2]` in `buildHandoffWelcomeGlass` — presentation labels only, **not** a second mood engine | Display only on Welcome; does **not** write engagement or change Atmosphere |
| **Reason line** | Morning celestial lunar: `morningRitualData.celestial_events.lunar_phase` (`name` / `phase_name`, `themes`, `guidance`) | Prefer `name — firstSentence(themes\|guidance)`; omit if empty | Display only; lunar identity remains symbols/day_foundation |
| **Activity tags (≤3)** | Day action nouns already on contract: `day_story.do[]` short lines **or** morning `daily_recommendations.priorities[]` (≤18 chars) | Dedupe, trim, max 3; **omit** if none — never invent «Планирование/Финансы» | Display only on Welcome |
| **CTA** | ScreenFlow index advance | `go(priority)` | Starts handoff setup cluster |

**Not used as SoT for glass:** vibe_strokes, interpretive_chorus prose (those feed energy/plot frames). Chorus may later feed reason **only** if lunar empty — product decision TBD; current rule = lunar-only for reason.

**Backend gap (P0, tracked):** optional nest `welcome_glass: { mood_tags, reason, good_for }` on `/today/contract` so FE stops mapping. Until then FE compose above is SoT.

---

## 3. Progress tracker — SoT and links

**FE composer (single):** `loadTodayGrowthTrackers` → `progressRows[]`.

| Kind | Active entity SoT | Streak SoT | 7-day dots SoT | Mark today |
|------|-------------------|------------|----------------|------------|
| **Habit** | First `GET /habits` with `is_active` | `GET /habits/overview/summary` → `current_streak_days` | `GET /tracking/calendar` `habit_tracks[].completed_dates` (fallback habit entries) | `POST /habits/{id}/entries` |
| **Ascetic** | First `GET /tracking/ascetic-contracts?status_filter=active` | Contract `streak_days` | Calendar `ascetic_tracks[].entries` | `POST …/checkin` |
| **Practice** | `GET /practices/current` title (or history name) | `GET /practices/progress` `current_streak_days` | `GET /practices/history` dates | `POST /practices/{id}/complete` |

**Not yet in progressRows:** affirmations, mantras, weekly goals — shown as **propose** cards on Make yours until they have streak/history SoT equivalent.

**Backend gap (P0):** unified `today_progress` DTO (3–6 rows + `bool[7]`) — FE composer remains until that ships.

---

## 4. Make yours — product rules

Categories (user): **практики · аскезы · аффирмации · мантры · привычки · цели**.

1. **If user already has** an active entity in that family → show it in **Твой прогресс** (tracker) when streak/dots exist; otherwise show as «стоит» row without inventing history.
2. **If missing** → **propose set/create** from day + user signals (table below). CTA deep-links existing create/catalog surfaces — no fake entities.
3. Day promise stays on **Promise** step; Make yours may mirror a goal propose from the same day signals.

| Empty slot | Propose from (existing only) | Action |
|------------|------------------------------|--------|
| Practice | `day_story.practice_recommendation` if kind practice · else `/practices/current` title | Link `/practices` or gift practice step |
| Ascetic | `practice_recommendation` kind ascetic · else ascetic catalog filters | Link `/tracking/calendar?create=ascetic` or Practices ascetics |
| Affirmation | `practice_recommendation` kind affirmation · text | Link `/affirmations` or Практика XOR slot |
| Mantra | Skip invent; link `/affirmations` / reference mantras only if API returns rows | Link catalog |
| Habit | Soft title from `today_move` / first `do` / habit templates — **as propose label**, create via wizard | `?create=habit` / calendar wizard |
| Goal | `buildTodayPromiseSuggestions` / `primary_action` / weekly-goal templates | Promise step or `/tracking/calendar?create=goal` |

Honest empty: if no signal and no entity → short links to Практики / Календарь without invented calm rows or mechanism labels («Предложить из дня» и т.п. — запрещены).

---

## 5. Number / Card

**Keep live ritual UX:** existing number flower/ring + tarot deck/open card (`RitualNumberPickExperience` / `RitualTarotPickExperience`). Do **not** replace with handoff 9 blank slots / 3 card-backs.
