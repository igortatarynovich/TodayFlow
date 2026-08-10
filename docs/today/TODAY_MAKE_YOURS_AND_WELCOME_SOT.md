# Today — Welcome glass · Progress · Make yours (SoT)

**Status:** ACTIVE · 2026-08-09  
**Presentation:** [TODAY_SCREEN_SCENARIO_V3](./TODAY_SCREEN_SCENARIO_V3.md) v3.3 handoff  
**Rule:** FE may **compose** existing signals; may **not invent** calm/product copy on empty or transport failure.

---

## 0. Frame → background (handoff hybrid)

| ScreenFlow step | Background |
|-----------------|------------|
| Welcome | `ImmersiveArtPlane` photo (`role=greeting`) + glass on photo |
| Priority · Promise · Make yours | Day Atmosphere wash only |
| Поток дня (energy + timeline) | Day Atmosphere wash only — **no** energy photo plane |
| Number · Card · Color · Focus · Recap · Close | Day Atmosphere wash only |
| Practice gift | `ImmersiveArtPlane` photo (`role=practice`) |

**Single-paint rule:** ≤1 full-bleed bitmap per viewport. Active `ImmersiveArtPlane` claims `html[data-day-photo=step]` → shell `--day-bg-art` + `.day-atmosphere-decor` suppressed (`day-atmosphere.css`). Inactive steps keep the plane node but do not decode `--story-art`. Scene motif washes (`[data-profile-atmosphere]`) are hidden under `html[data-day-mode]` — Day Atmosphere owns the frame photo.

Atmosphere tokens (`--day-*` / ink / glass) apply on **all** steps. Handoff SoT: `docs/design/design_handoff_today_flow/README.md`.

---

## 1. Priority (product note)

Handoff = **6 two-line cards** (label + sub-label, 2-col, single-select) from a closed map of `TODAY_FOCUS_TOPICS`.  
SoT for focus id remains engagement `focusTopicId` + meaning `head_topic_selected`. Layout = FE presentation.

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

**Backend (P0, shipped):** nest `welcome_glass: { mood_tags, reason, good_for }` on `/today/contract`. FE compose above remains until FE reads the nest.

---

## 3. Progress tracker — SoT and links

**FE composer (single):** `loadTodayGrowthTrackers` → `progressRows[]`.

| Kind | Active entity SoT | Streak SoT | 7-day dots SoT | Mark today |
|------|-------------------|------------|----------------|------------|
| **Habit** | First `GET /habits` with `is_active` | `GET /habits/overview/summary` → `current_streak_days` | `GET /tracking/calendar` `habit_tracks[].completed_dates` (fallback habit entries) | `POST /habits/{id}/entries` |
| **Ascetic** | First `GET /tracking/ascetic-contracts?status_filter=active` | Contract `streak_days` | Calendar `ascetic_tracks[].entries` | `POST …/checkin` |
| **Practice** | `GET /practices/current` title (or history name) | `GET /practices/progress` `current_streak_days` | `GET /practices/history` dates | `POST /practices/{id}/complete` |

**Not yet in progressRows:** affirmations, mantras, weekly goals — shown as **propose** cards on Make yours until they have streak/history SoT equivalent.

**Backend (P0, shipped):** unified `today_progress: { rows: [{ id, kind, kind_label, name, streak_days, days_bool[7] }] }` on `/today/contract` (distinct from story `progress`). FE composer remains until FE reads the nest.

---

## 4. Make yours — product rules

Categories on this step: **аскезы · аффирмации · мантры · привычки · цели**.  
**Практики сюда не входят** — у них свой ScreenFlow-шаг / страница `/practices`.

1. **If user already has** an active entity in that family → show it in **Твой прогресс** (tracker) when streak/dots exist; otherwise show as «стоит» row without inventing history.
2. **If missing** → **inline pick from real catalogs on this step** (habits/goals templates · `/practices/asceticisms` · `/practices/affirmations` · `/reference/mantras`). CTA may still deep-link calendar/library; **do not** send the user away just to choose.
3. **Never invent** affirmation/habit body from the same `day_story.do` / `today_move` line (that produced duplicate cards). Day `practice_recommendation` may label an ascetic/affirmation propose only when kind matches.
4. Day promise stays on **Promise** step; Make yours may mirror a goal propose from the same day signals.

| Empty slot | Propose / pick from | Action on this step |
|------------|---------------------|---------------------|
| Ascetic | `practice_recommendation` kind ascetic · else `/practices/asceticisms` | Inline list → `POST /tracking/ascetic-contracts` |
| Affirmation | `practice_recommendation` kind affirmation · else `/practices/affirmations` | Inline list → `POST /tracking/progress` |
| Mantra | `/reference/mantras` only (no invent) | Inline list · no fake tracker SoT yet |
| Habit | Habit template catalog only (not day move prose) | Inline list → `POST /habits` |
| Goal | Promise / `primary_action` / goal templates | Inline list → `POST /tracking/weekly-goals` |

Honest empty: if no signal and no entity → short links to Календарь / Аффирмации without invented calm rows or mechanism labels.

---

## 5. Number / Card

**Keep live ritual UX** (`RitualNumberPickExperience` / `RitualTarotPickExperience`). Closed-state polish only:
- Number idle → **9 blank ring** slots (still live pick, not a stub).
- Card idle → **3 stacked backs** (tap opens live deck).

Do **not** replace rituals with static handoff placeholders.

**Tarot × number compose (FE):** after both revealed, personal line may read `При числе дня N (title) эта карта — …` via `formatRitualTarotPersonalToday` — presentation only; meaning SoT stays symbol hooks / impact.

---

## 6. Day promise → Day Connection

Local engagement `dayGoal` remains primary UX store (survives refresh via CUM).  
On set (chip or free-text): also `POST /day-connection/{date}` with `morning_intention` + `morning_completed` (`todayPromiseSync`) — fire-and-forget; transport failure does not invent copy or roll back local promise.

---

## 7. Thin recap (handoff)

Recap frame shows **three** rows only: Приоритет · Обещание · Практика (started/done).  
Number / card are **not** on recap — they live on their ritual steps.

---

## 8. Atmosphere crossfade (P2)

Mode change on product routes: capture `--day-prev-*` wash → hold on frame `::after` → apply new `--day-*` → fade out previous.  
Skip on `prefers-reduced-motion`, lite/touch-narrow, and when document hidden.
