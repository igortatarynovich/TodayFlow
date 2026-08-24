# TodayFlow Product Execution Tracker

Last updated: 2026-08-22
Owner: Product + Engineering
Status: Active working document

## Architecture impact — One product shell chrome on every in-app page (2026-08-17)

- **SoT before:** Pages could pass `theme`/`mood` into `ProductWebAppShell`; Tarot section atmosphere still painted ritual void (`#07080c`); `data-product-web-shell` also fired on `/` and `/auth`.
- **SoT after:** Chrome (sidebar, tab bar, type, ink, frame bg) is identical on every `usesProductWebAppShell` route. Pages may set rail / `fullMain` / main content only. Day Atmosphere still tints the shared wash; it does not fork a per-section shell.
- **Public contract changed?** no
- **Migration required?** no — FE chrome only
- **Canon updated?** yes — `docs/TODAYFLOW_FOUNDATION_UI.md` §7 · §11.1
- **Backward compatible?** yes; marketing `/` `/auth*` `/onboarding*` stay outside App Shell

## Architecture impact — Login must not paint First Today fallback (2026-08-17)

- **SoT before:** Post-auth used localStorage `hasCompletedFirstToday()`; missing flag → `/today?first=1` chip gate. Missing `/today/contract` → FE invented `buildFallbackTodayContract` (First Today package) as live paint.
- **SoT after:** Login home = `/today`. First Today (`?first=1`) only from explicit onboarding routes. Contract miss → wait / «Нет соединения.» / «Не удалось загрузить.» — no invented day.
- **Public contract changed?** no
- **Migration required?** no — client routing + paint only
- **Canon updated?** yes — `docs/FIRST_DAY_EXPERIENCE.md` §2 post-auth
- **Backward compatible?** yes; onboarding still `router.replace(FIRST_TODAY_PATH)`

**NOW (OPS / LLM, 2026-08-18):** **AI COGS instrumentation** — K2.6 stays. `llm_usage_v1` now has `operation_id`, `trigger` (user|prewarm|eval|script|background), retry metadata, billed output ≠ reasoning double-count. Report: feature×trigger×model×retry_reason + top-20 operation_id. Next: 24h data, then hard budgets.

## Architecture impact — AI COGS llm_usage_v1 (2026-08-18)

- **SoT before:** Nebius invoice only; no per-request tokens/cost. Streaming Kimi discarded usage + `reasoning_content`. AMLL token/cost fields were backlog.
- **SoT after:** Each `chat.completions.create` emits `llm_usage_v1` with `operation_id`, `trigger`, retry metadata. Cost uses billed `completion_tokens` only (`reasoning_tokens` is breakdown). Prices = observed Token Factory rates (K2.6 $0.95/$4 per 1M). Optional `LLM_USAGE_LOG_PATH`. Generation text SoT unchanged.
- **Public contract changed?** no
- **Migration required?** no — additive logs
- **Canon updated?** yes — [LLM_QUALITY_AND_PROMPT_EVOLUTION.md](./LLM_QUALITY_AND_PROMPT_EVOLUTION.md) AI COGS · [API_MEMORY_AND_LEARNING_LAYER.md](./API_MEMORY_AND_LEARNING_LAYER.md) §3/§14 (token/cost 🟡)
- **Backward compatible?** yes. `include_usage` on streams; retry without `stream_options` if the provider rejects it.

**DONE (CODE, 2026-08-18):** **Today unavailable honesty** — MY DAY no longer mixes «Не удалось загрузить.» with leftover focus title, catalog/morning color, or independent natal timeline. `color_guide` null when interpretation unavailable; Global Day Engine stays on the contract (I0). Canon: TODAY_PRODUCT_FLOW_V1 §3.

## Architecture impact — Today unavailable MY DAY (2026-08-18)

- **SoT before:** unavailable shell copy in period/growth/action; leftover scenario color + morning catalog still became «цвет дня»; MY DAY fetched `day_facts` clocks independently; leftover `conflict.short_name` counted as authoritative story.
- **SoT after:** `color_guide=null` on unavailable; MY DAY = one honest status, omit color/natal timeline/leftover focus; `global_day` still attached (Engine, not Personal interpretation).
- **Public contract changed?** yes — `color_guide` null on unavailable; `global_day` present on unavailable.
- **Migration required?** no version bump; next GET + FE rebuild.
- **Canon updated?** yes — `docs/today/TODAY_PRODUCT_FLOW_V1.md` §3.
- **Backward compatible?** failure copy still used for navigational slots; clients expecting a color swatch on a failed Personal Day lose that invent.

**NOW (MOTION / MOON, 2026-08-17):** FOUNDATION_UI v0.7 — animation explains state or day mood; else delete. Surface budget: landing 7/10 · app 2–3/10 · share 5/10. No stars / particles / flying zodiac. Moon = live astronomical object (`DsCelestialMoon`, real phase). Today moon is static (no idle spin). Stack: CSS + Framer; WebGL only for the moon. SoT: FOUNDATION_UI §2.7 · §18.

## Architecture impact — Motion budget + live Moon (2026-08-17)

- **SoT before:** Day Atmosphere allowed particles; Today moon idly spun; no product-wide motion budget; starfield still in natal/profile CSS (transitional).
- **SoT after:** Motion must explain UI state or amplify day mood. Astrology-site décor forbidden. Moon is information (phase/terminator), not décor. App nearly still; landing may have slow pointer/scroll on the same sphere. Natal starfield remains debt until §2.6 package — do not add more.
- **Public contract changed?** no
- **Migration required?** no JSON. Today moon `animated=false` / `spin=0`. Idle `MotionDrift` in Profile/HeroLarge is over-budget; do not add new instances.
- **Canon updated?** yes — FOUNDATION_UI v0.7 §2.7 · §18 · §11.4 · TODAY_MOTION_PILOT pointer · README
- **Backward compatible?** yes — visuals quieter on Today moon
- **Next:** do not pull Three.js; do not split planet restyle from §2.6. Landing moon signature is CODE.

**NOW (BRAND / LANDING, 2026-08-17):** Landing rebuilt as Trust Layer brand surface (Co-Star principle: manifesto first). H1 = locked three beats. Moon = hero signature (real phase). Thesis `#trust` before Today / Compatibility / Tarot. Dual hero CTA and `#why` retired. Guest path demo→invite unchanged. SoT: [TODAYFLOW_TRUST_LAYER.md](./content/TODAYFLOW_TRUST_LAYER.md) §5. **Next:** about/press if needed; do not put NASA/Canon into Today/Profile body. Do not overclaim IL-1. Do not say Horizons is live.

## Architecture impact — Trust Layer landing as brand (2026-08-17)

- **SoT before:** Guest Story P0 landing = continuity slogan + dual primary CTAs; Trust Layer was a `#trust` kicker after tools.
- **SoT after:** Landing **is** the brand. Locked line is H1. Order: hero → trust thesis → today → compatibility → tarot/practices → cta. Moon is the signature object (FOUNDATION_UI §2.7). Compatibility stays a full chapter, not hero co-CTA.
- **Public contract changed?** no JSON/generation. Marketing H1 / meta description / landing section order yes.
- **Migration required?** no runtime. Dual hero CTA retired. `#why` removed (no invented testimonials).
- **Canon updated?** yes — Trust Layer v1.2 §5 · Guest Story P0 landing-narrative supersession · WEB_LAUNCH pointer · FOUNDATION_UI §2.7 landing CODE.
- **Backward compatible?** old bookmarks `#why` 404-in-page. Guest in-app nav unchanged.
- **Next:** about/press if needed. Do not overclaim IL-1. Do not say Horizons is live.

**NOW (BRAND / COPY, 2026-08-17):** **Trust Layer locked.** Ads brief in Trust Layer §6. SoT: `docs/content/TODAYFLOW_TRUST_LAYER.md`. Landing copy lives in `productWebLandingContent.ts`.

## Architecture impact — Trust Layer / brand language (2026-08-17)

- **SoT before:** provenance and “not one averaged astrology” lived only in Interpretation Library §6. NASA/JPL was a runtime footnote; Horizons unwired. Landing copy did not carry the two trust pillars.
- **SoT after:** [TODAYFLOW_TRUST_LAYER.md](./content/TODAYFLOW_TRUST_LAYER.md) is public brand/copy SoT. Astronomy claims bounded to live Swiss/DE431 (Foundation §1.4.1). IL remains meaning lookup; Voice Canon §0 still bans self-reference *inside* product UI.
- **Public contract changed?** no JSON/generation. Marketing language yes.
- **Migration required?** no runtime. Copy slice: landing · ads · about.
- **Canon updated?** yes — Trust Layer v1.0 · Voice Canon §0.08 v1.9 · Unified §0 v1.11 · Foundation §1.4.1 · IL pointer 1.3.7 · README · explainability indexes.
- **Backward compatible?** yes
- **Next:** about/press if needed. Landing copy is in `productWebLandingContent`. Do not overclaim IL-1 drafts as a finished public catalog. Do not say Horizons is live.

**NOW (VISUAL LANGUAGE, 2026-08-17):** FOUNDATION_UI §2 v0.5 — ten-layer language + two registers (information glyphs vs identity planet images) + natal as branded composition of the same primitives (not a traditional wheel). Cross-surface literacy: `♀ → ♉︎ → VII → △ → ♄` in Profile / Today / Compat / chart. Next DS (not this commit): planet restyle · glyph set · natal rebuild from atoms. Profile viewport 1 unchanged.

## Architecture impact — Natal visual language v0.5 (2026-08-17)

- **SoT before:** §2 v0.4 = two glyph tiers + families; natal wheel still a separate decorated object (starfield, jewels, photo discs, zodiac orbs). Planet photos used as icons.
- **SoT after:** Ten layers. Information vs identity registers must not share a slot. Natal chart = thin geometry assembled from layers 1–7; no constellations/ornament. Planet images = XL/share only, unified style (not NASA crop). Extra points (Chiron/Lilith/PoF) stay out until product canon lock. Screens stop inventing per-page illustrations once the set exists.
- **Public contract changed?** no
- **Migration required?** no runtime; DS later. Transitional: `DsPlanet` photo-as-icon, `DsAngle` badges, `ElementIcon` decorative, `NatalChartWheel` decor.
- **Canon updated?** yes — FOUNDATION_UI v0.5 §2. No new docs file.
- **Backward compatible?** yes — UI unchanged until DS pass
- **Next:** owner asks → primitives + planet restyle + natal rebuild together (chart must not get a third art language). Do not open Profile viewport 2 for this.

**NOW (PROFILE VIEWPORT 1, 2026-08-17):** First `/profile` frame @390 = portrait → name → `recognition_line` → one signal. `identity_core` is disclosure, not the line. Not Today, not environment, not assets.

## Architecture impact — Profile first viewport (2026-08-17)

- **SoT before:** Act 1 preferred `identity_core` as the visible body; step badge «Твоя суть»; name via `clamp()` to 52px. Journey still a document below.
- **SoT after:** First viewport slots = portrait · Hero name · Body `recognition_line` (≤120) · one signal («Почему именно ты»). `identity_core` opens on that signal. Why+ still on scroll, not in the first frame. Locked form Step 1 in PROFILE_PRODUCT_JOURNEY_FORMS_V1.
- **Public contract changed?** no
- **Migration required?** no — FE composition only
- **Canon updated?** no new file — live aligned to existing locked form
- **Backward compatible?** yes; cached cores without `recognition_line` fall back to first sentence of `identity_core`
- **Next:** owner glance @390. Do not open viewport 2 / Today / environment / asset research.

**NOW (FOUNDATION, 2026-08-24):** **Native C1 everyday scene retry 1.3.119 LOCKED** (prompt c5.2 · all-scene lived markers · Global max_attempts 3 · gates unchanged). **Native C1 evidence pack binding 1.3.118 LOCKED**. **Native C1 editorial gate calibration 1.3.117 LOCKED**. **Native C1 I0 generation split 1.3.116 LOCKED**. **Compatibility synastry editorial IL-4 1.3.115 LOCKED**. **Today meaning polish 1.3.114 LOCKED**. **IL-4 editorial consume 1.3.113 LOCKED**. Catalog 38 draft / 0 `active`. **STOP Angles.** Not pair catalog. Not `active`. Boundary: [IL1_HANDOFF.md](./astrology/IL1_HANDOFF.md) §3 · §5 paste.

**PAUSED (TODAY CONTENT, 2026-08-17):** Further Today *meaning/narrative* work beyond chorus bind is owner-directed. I0 + product cycle stay locked. Allowed: transport honesty, routing, visual foundation, DS, bugs, geometry, owner-named polish.

## Architecture impact — IL sequence lock (2026-08-17)

- **SoT before:** IL-0.5 / IL-0.6 / IL-5 / IL-6 numbering; gold combos framed as Today drivers; Swiss phrased as outside IL.
- **SoT after:** IL-0 ✅ · IL-1 ~100 surface-neutral objects · IL-2 composition rules · IL-3 engine · IL-4 expression. Runtime: Swiss/JPL → calc → IL meaning → engine → expression. Only **licensing** is a parallel gate. IL-1 objects map to calc-layer entities. Methodology frozen until IL-1 closes.
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — IL v1.3 Runtime stack · Foundation §1.4
- **Backward compatible?** yes

## Architecture impact — Interpretation Library corpus (2026-08-17)

- **SoT before:** IL-0 named source *classes*; no corpus, no evidence tiers, provenance was thin.
- **SoT after:** claims extracted from a multi-school corpus (classical / traditional / psychological / humanistic / professional); consensus → `core|supported|school_specific|editorial`; no copyrighted dump; astronomy separate (Swiss facts-only). Today Meaning SoT remains the pipeline.
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — IL v1.1 §6 · source_corpus_v1.json · Foundation §1.4 (Swiss license OPEN)
- **Backward compatible?** yes

## Architecture impact — IL-1 1.3.29 source discovery (2026-08-17)

- **SoT before:** author-first Greene+Hand queue; NEED_OWNER(locus) treated as blocking the semantic slot; Rudhyar listed as psychological.
- **SoT after:** school → coverage → best accessible primary. NEED_OWNER ≠ NEED_EVIDENCE. `source_class=humanistic`. New authors allowed until semantic saturation. Rudhyar Venus ingested independently.
- **Public contract changed?** no
- **Migration required?** no — unused `rudhyar_personality`/`lunation` rows stay psychological until dedicated reclass
- **Canon updated?** yes — `docs/astrology/INTERPRETATION_LIBRARY_V1.md` §6.1 · §6.9 · schemas `source_class` enum
- **Backward compatible?** yes — no runtime wiring

## Architecture impact — IL-1 1.3.67 later-interpretive optional (2026-08-21)

- **SoT before:** Layer 2 schema required later-interpretive slots on every `type=sign`, which blocked classification-only drafts.
- **SoT after:** those slots stay in the model and stay unattested; they are optional on IL-1 draft `type=sign`. Classification `mode` / `element` / `orientation` stay required. No 12 objects this pass. Do not fill from Pulse / Lilly QUALITY / Cell C.
- **Public contract changed?** yes — JSON Schema Layer 2 `required` list
- **Migration required?** no — zero live sign objects
- **Canon updated?** yes — IL 1.3.67 §6.21 · `astrology_interpretation_v1.schema.json`
- **Backward compatible?** yes for runtime (nothing `active`); old sign validators that required psych keys will fail a future classification-only draft

## Architecture impact — IL-1 1.3.68 Lilly classification drafts (2026-08-21)

- **SoT before:** later-interpretive optional; 0 `type=sign` objects; classification only in claims.
- **SoT after:** twelve `draft` `type=sign` objects. Object `mode`/`element`/`orientation` = Lilly CA I.16 school_specific (masculine→`positive`, feminine→`negative`). Later-interpretive omitted. QUALITY personality adjectives not copied. Collisions remain claims. `theme_clusters=["timing"]` is year-span clustering, not Pulse. Nothing `active`. CORE not scored.
- **Public contract changed?** yes — catalog now has 12 sign records (`draft` only)
- **Migration required?** no — runtime must keep ignoring `draft`
- **Canon updated?** yes — IL 1.3.68 §6.22 · `objects_v1.json`
- **Backward compatible?** yes for runtime if it only reads `status=active`

## Architecture impact — IL-1 1.3.69 Layer 2 close-out (2026-08-21)

- **SoT before:** twelve Lilly drafts existed; Layer 2 could still be read as an open ingest track (Cell C / Pulse Part Two / Hand Ch.10 next).
- **SoT after:** Layer 2 Signs is classification-complete / interpretation-deferred. Audit passed. No ingest. Catalog unchanged. Cell C remains ACCESS_BLOCKED as future evidence, not a Layer 2 blocker. Next Knowledge Core slice is not more sign literature.
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — IL 1.3.69 §6.23 · `docs/astrology/IL1_LAYER2_SIGNS_CLOSEOUT.md`
- **Backward compatible?** yes

## Architecture impact — IL-1 1.3.70 Layer 1 outers definition (2026-08-21)

- **SoT before:** outers withheld because required Layer 1 slots would fake consensus; next hole could be misread as another outer book.
- **SoT after:** definition/readiness (parent steps 1–4). Outer `function` is later-interpretive, not classical elemental quality. Sufficiency: omit meaning keys after named scoped schema impact, or keep withheld. No ingest. No objects. Do not pick Hand. ASC/MC not this pass.
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — IL 1.3.70 §6.24 · `docs/astrology/IL1_LAYER1_OUTERS_DEFINITION.md`
- **Backward compatible?** yes — catalog unchanged; Sun–Saturn `function` untouched

## Architecture impact — IL-1 1.3.71 Knowledge Core V1 Semantic Inventory (2026-08-21)

- **SoT before:** next named IL pass was still a layer slice (outers schema or ASC). Literature could restart from any gap.
- **SoT after:** V1-wide inventory is the **owner-approved** freeze map. New literature only if row X → consumer Y → missing Z. IL-1 done criterion = minimum controlled primitives, not bibliography.
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — IL 1.3.71 §6.25 · `docs/astrology/KNOWLEDGE_CORE_V1_SEMANTIC_INVENTORY.md`
- **Backward compatible?** yes — no catalog/schema change

## Architecture impact — IL-1 1.3.72 Outer Planet Draft Representation (2026-08-21)

- **SoT before:** Layer 1 required meaning keys on every celestial_object, so outers stayed withheld.
- **SoT after:** those keys optional on IL-1 draft Uranus/Neptune/Pluto only. Sun–Saturn unchanged. School packages stay in claims. No objects this pass. Fill waits for TodayFlow Canon (1.3.73).
- **Public contract changed?** yes — JSON Schema Layer 1 requiredness scoped
- **Migration required?** no — 0 outer objects
- **Canon updated?** yes — IL 1.3.72 §6.26 · `docs/astrology/IL1_OUTER_PLANET_DRAFT_REPRESENTATION.md` · `astrology_interpretation_v1.schema.json`
- **Backward compatible?** yes for runtime (`draft` ignored)

## Architecture impact — IL-1 1.3.73 TodayFlow Canon (2026-08-21)

- **SoT before:** product meaning waited on CORE = school-intersection. Next named was outer materialize.
- **SoT after:** TodayFlow Canon is the product-meaning gate. CORE is research metadata, not permission. Criteria: prevalence · recognition · distinctiveness · utility · composability. Next = Sun–Pluto claim audit on the existing ledger. Outer schema 1.3.72 stands; `function` fill waits.
- **Public contract changed?** no JSON this pass. Future IL-3 reads Canon slots, not `evidence_tier=core`.
- **Migration required?** no
- **Canon updated?** yes — IL 1.3.73 §6.27 · `docs/astrology/TODAYFLOW_CANON_V1.md` · parent §4
- **Backward compatible?** yes for runtime. Deprecated as product gate: wait-for-CORE.

## Architecture impact — IL-1 1.3.74 Corpus / Consensus / Canon (2026-08-21)

- **SoT before:** Canon criteria existed; Corpus, Consensus, and Canon could still collapse into one pile; next could look like a long research cycle.
- **SoT after:** three layers distinct. 491 claims = Evidence Corpus (keep). Runtime = Canon → composition → LLM formulates. Next = short corpus pass. Not Outer / ASC / books.
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — IL 1.3.74 §6.28 · TODAYFLOW_CANON_V1.md §0
- **Backward compatible?** yes

## Architecture impact — IL-1 1.3.75 Co–Star teardown freeze (2026-08-21)

- **SoT before:** next named IL pass was a short Evidence Corpus → Semantic Consensus → Canon proposal. Co–Star was landing layout + forbidden IL source.
- **SoT after:** IL architecture frozen. Empirical base = `docs/audits/COSTAR_SEMANTIC_CONTENT_ENGINE_TEARDOWN_V1.md` (Phase 0). Calc must be correct; meaning must be consistent, recognizable, useful. Quality criteria = feels-like-me / specific / noticing / share / return. Do not copy Co–Star. Next = Phase 1 in-app corpus, not Canon scoring.
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — IL 1.3.75 §6.29 · teardown file · inventory execution order · parent 1.3
- **Backward compatible?** yes. Deprecated as next pass: short corpus scoring.

## Architecture impact — IL-1 1.3.91 House Canon fill (2026-08-22)

- **SoT before:** grammar locked one slot; dry-run lemmas were illustrative. Risk: dump 1.3.89 families or write pair interpretations.
- **SoT after:** twelve packs locked with origin tags. Five gates. Destination-noun test. Catalog untouched. Next = storage/materialization.
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — `docs/astrology/HOUSE_CANON_V1.md` · IL 1.3.91 §6.45
- **Backward compatible?** yes. House objects stay `DRAFT_CLASSICAL`.

## Architecture impact — IL-1 1.3.96 Aspect Canon fill (2026-08-22)

- **SoT before:** grammar locked one slot; dry-run lemmas were illustrative. Risk: dump 1.3.94 families, stamp conjunction good/bad, write growth into square, or pretty lemmas for Today copy.
- **SoT after:** five packs locked. Origin `direct` from 1.3.94 include. Five gates. Conjunction mixed-valence is a pack guard, not a lemma. Catalog untouched at fill. Storage — **done 1.3.97.**
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — `docs/astrology/ASPECT_CANON_V1.md` · IL 1.3.96 §6.50
- **Backward compatible?** yes (`draft`). Deprecated: treating 1.3.95 dry-run wording as locked values.

## Architecture impact — IL-1 1.3.97 Aspect Canon storage/materialization (2026-08-22)

- **SoT before:** Aspect Canon lived in a doc. Five aspect drafts were `angle` / `interaction` / `requires_action` only. Schema forbade `canon` on `type=aspect`.
- **SoT after:** `type=aspect` may carry optional `canon` as `$defs.aspect_canon_pack` (`relation` only). Five drafts carry locked 1.3.96 packs. Stored `interaction` unchanged. Combos still omit `canon`. Status `draft`. Runtime unchanged. Stored Planet × Aspect smoke — **done 1.3.98.** **STOP Aspects.** Next = ASC/MC.
- **Public contract changed?** yes — optional aspect `canon` nest; five draft aspects now include `canon`
- **Migration required?** no — nothing `active`
- **Canon updated?** yes — `docs/astrology/ASPECT_CANON_STORAGE_MATERIALIZATION_V1.md` · IL 1.3.97 §6.51 · schema `$defs.aspect_canon_pack` · `objects_v1.json`
- **Backward compatible?** yes for runtime (`draft`)

## Architecture impact — IL-1 1.3.102 Angle Canon fill (2026-08-22)

- **SoT before:** grammar locked one slot; dry-run lemmas were illustrative. Risk: inherit 1.3.101 wording; promote secondary collision-zone; treat personal-facing / public-facing as the pack.
- **SoT after:** two packs locked. Origin `direct` from 1.3.100 include. Five gates. Collision vs House 1/10. Secondary unused. Angle Canon storage/materialization — **done 1.3.103.** Sequence: stored Planet×Angle smoke → STOP Angles → final atomic smoke.
- **Public contract changed?** no (fill)
- **Migration required?** no
- **Canon updated?** yes — `docs/astrology/ANGLE_CANON_V1.md` · IL 1.3.102 §6.56
- **Backward compatible?** yes (`draft`)

## Architecture impact — IL-1 1.3.103 Angle Canon storage/materialization (2026-08-22)

- **SoT before:** two packs locked in a doc. Catalog 36 drafts. No `type=angle`. Layer 1 forced `celestial_object`.
- **SoT after:** `$defs.angle_canon_pack` (`orientation`). Two `type=angle` drafts carry locked 1.3.102 packs. Catalog 38 draft / 0 `active`. House 1/10 packs unchanged. Runtime ignores `draft`. Stored Planet×Angle smoke — **done 1.3.104.**
- **Public contract changed?** yes — `type=angle`; optional angle `canon` nest; two draft objects
- **Migration required?** no — nothing `active`
- **Canon updated?** yes — `docs/astrology/ANGLE_CANON_STORAGE_MATERIALIZATION_V1.md` · IL 1.3.103 §6.57 · schema `$defs.angle_canon_pack` · `objects_v1.json`
- **Backward compatible?** yes for runtime (`draft`)

## Architecture impact — IL-1 1.3.104 stored Planet × Angle composition smoke (2026-08-23)

- **SoT before:** two angle drafts carry locked `orientation`. Risk: House 1/10 as the angle; occupancy = conjunction; planet-on-angle essays.
- **SoT after:** PlanetAtAngle frames read stored `canon.orientation`. Four gates PASS. Mars AT ASC ≠ Mars AT MC ≠ House 1/10. Occupancy ≠ conjunction. Catalog unchanged. **STOP Angles.** Final atomic smoke — **done 1.3.105.** Knowledge Core V1 FREEZE — **done 1.3.106.** Next = IL-2.
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — `docs/astrology/ANGLE_CANON_COMPOSITION_SMOKE_V1.md` · IL 1.3.104 §6.58
- **Backward compatible?** yes (`draft`)

## Architecture impact — IL-1 1.3.105 final atomic smoke (2026-08-23)

- **SoT before:** five family smokes PASS in isolation. Risk: collapse operators into one essay; skip freeze; open IL-2 cookbooks.
- **SoT after:** one diagnostic reads Planet + Sign + House + Aspect + Angle from stored `canon`. Four gates PASS. Operators discriminate. Occupancy ≠ conjunction. Catalog unchanged. Knowledge Core V1 FREEZE — **done 1.3.106.**
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — `docs/astrology/ATOMIC_CANON_COMPOSITION_SMOKE_V1.md` · IL 1.3.105 §6.59
- **Backward compatible?** yes (`draft`)

## Architecture impact — IL-1 1.3.106 Knowledge Core V1 FREEZE (2026-08-23)

- **SoT before:** inventory was the literature freeze map; five stored families smoke-PASS; next named was still “declare V1 frozen,” so IL-2 could start as if 41 gold-set / CORE / outers were gates.
- **SoT after:** Knowledge Core V1 is **frozen on stored primitives**. Five `canon` operators are the V1 atoms. Catalog 38 draft / 0 `active`. Uranus/Neptune/Pluto remain claims. DSC/IC out of V1. CORE unscored (not a gate). Layer 5 = candidates. Later-interpretive signs deferred. Co–Star = recognition check, not source. Next named = **IL-2 composition rules** (not pair catalog).
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — `docs/astrology/KNOWLEDGE_CORE_V1_FREEZE.md` · inventory step 34 · IL 1.3.106 §6.60
- **Backward compatible?** yes (`draft`)

## Architecture impact — Today 1.3.119 Native C1 everyday scene retry (2026-08-24)

- **SoT before:** c5.1 retry named one failing scene; gen 1104 (user 13) traded `SCENE_MISSING_EVERYDAY` from `work_decisions` to `energy_body` across two Global attempts → unavailable. Detectors unchanged.
- **SoT after:** **Native C1 Everyday Scene Retry V1** — prompt `day-scenario-native-c5.2`; retry forbids shortening passing scenes; Global `max_attempts` default 3. C3.1 lived-marker detectors unchanged. Public JSON unchanged.
- **Public contract changed?** no
- **Migration required?** no — force rebuild / refresh picks up c5.2
- **Canon updated?** yes — `docs/today/NATIVE_C1_EVERYDAY_SCENE_RETRY_V1.md` · tracker 1.3.119
- **Backward compatible?** yes — same blocking codes

## Architecture impact — Today 1.3.118 Native C1 evidence pack binding (2026-08-24)

- **SoT before:** `collect_allowed_evidence_ids` missed string `ranked_drivers`/`ambient` and foundation nest-path cites (`ev.foundation.lunar.{beat_id}`). Thin-profile Global (user 4 / gen 1092) failed hard `unknown_evidence` after LLM. Editorial calibration 1.3.117 left this out of scope.
- **SoT after:** **Native C1 Evidence Pack Binding V1** — allowlist binds events pack + foundation beat aliases + interpretation evidence + personalization pack refs. Brief lists canonical ids. `unknown_evidence` still rejects invented ids. Prompt `day-scenario-native-c5.1` unchanged. Public JSON unchanged.
- **Public contract changed?** no
- **Migration required?** no — force rebuild / refresh picks up binding
- **Canon updated?** yes — `docs/today/NATIVE_C1_EVIDENCE_PACK_BINDING_V1.md` · tracker 1.3.118
- **Backward compatible?** yes — same hard marker; closed set larger

## Architecture impact — Today 1.3.117 Native C1 editorial gate calibration (2026-08-23)

- **SoT before:** Native C1 I0 split c5.0; Global gate retries passed code-only strings; production LLM outputs failed `SCENE_MISSING_EVERYDAY` / `SCENE_ABSTRACT` / `ASTRO_JARGON_BARE` without actionable retry coaching.
- **SoT after:** **Native C1 Editorial Gate Calibration V1** — prompt `day-scenario-native-c5.1`; Global retry injects `format_editorial_retry_feedback` (defect messages + targeted hints). C3.1 gate codes unchanged (no semantic weakening). Public JSON unchanged.
- **Public contract changed?** no — fewer `interpretation_status: unavailable` when gates pass after retry
- **Migration required?** no — refresh / force rebuild picks up c5.1
- **Canon updated?** yes — `docs/today/NATIVE_C1_EDITORIAL_GATE_CALIBRATION_V1.md` · `NATIVE_C1_I0_GENERATION_SPLIT_V1.md` (c5.1 ref) · tracker 1.3.117
- **Backward compatible?** yes — same gate semantics; cached unavailable days until regenerate

## Architecture impact — Today 1.3.116 Native C1 I0 split (2026-08-23)

- **SoT before:** One native C1 LLM call produced chorus + conflict + scenes + natal + personalization together — I0 Global/Personal boundary violated in generation.
- **SoT after:** Native C1 I0 Generation Split V1. Global stage (sky/card/number + conflict + scenes); optional Personal overlay stage from `GLOBAL_LOCKED`. Merge overlay-only; personal degrade → Global-only. Prompt `day-scenario-native-c5.0`. IL-4 attach/consume/polish unchanged. Public JSON unchanged.
- **Public contract changed?** no — generation order / internal LLM stages only
- **Migration required?** no — refresh picks up c5.0
- **Canon updated?** yes — `docs/today/NATIVE_C1_I0_GENERATION_SPLIT_V1.md` · inventory step 44 / KC-C-I0-SPLIT · IL §6.70 · TODAY_CONTENT_PIPELINE table · TODAY_MEANING_POLISH
- **Backward compatible?** yes — same day_scenario projection; cached days until regenerate

## Architecture impact — Compatibility 1.3.115 synastry editorial IL-4 (2026-08-23)

- **SoT before:** `compatibility_llm` consumed IL-4 when `chart1` was passed (attach 1.3.112 + consume 1.3.113). Synastry `generate_compatibility_editorial` ignored IL-4 even when charts existed upstream.
- **SoT after:** Synastry editorial accepts optional `chart1` / `chart2`, attaches IL-4 via existing gateway, consumes pack (system augment + protected `IL4_MEANING` prefix + reject-invalid). Prompt `compatibility-editorial-v1.1`. Public `CompatibilityEditorial` contract unchanged. Polish 1.3.114, consume, attach stand.
- **Public contract changed?** no — internal LLM input / editorial gate only
- **Migration required?** no — synastry refresh regenerates editorial
- **Canon updated?** yes — `docs/astrology/COMPAT_SYNASTRY_EDITORIAL_IL4_V1.md` · inventory step 43 / KC-C-COMPAT-EDITORIAL · IL §6.69
- **Backward compatible?** yes — missing charts → previous editorial path

## Architecture impact — Today 1.3.114 meaning polish (2026-08-23)

- **SoT before:** Consume 1.3.113 put IL4_MEANING on LLM input. Native prompt still let `interpretive_chorus.astrology` invent parallel sky meaning from flat facts.
- **SoT after:** Today Meaning Polish V1 binds the astrology chorus voice to IL-4 lemmas when a pack is present. `TODAY_IL4_CHORUS` instruction; reject empty astrology chorus; fill-empty `human_meaning` only. Conflict/scenes stay DRAMATURGY_BRIEF + I0. Prompt `day-scenario-native-c4.2`. Public JSON unchanged. Consume 1.3.113 stands.
- **Public contract changed?** no — internal LLM input / editorial gate
- **Migration required?** no — refresh/force_rebuild picks up c4.2
- **Canon updated?** yes — `docs/today/TODAY_MEANING_POLISH_V1.md` · inventory step 42 / KC-C-TODAY-POLISH · IL §6.68
- **Backward compatible?** yes — missing pack omits polish instruction

## Architecture impact — IL-1 1.3.113 IL-4 editorial consume (2026-08-23)

- **SoT before:** Attach 1.3.112 put `il4_expression_pack` on LLM inputs. Prompts could still treat the model as meaning chooser. Today polish PAUSED until consume.
- **SoT after:** IL-4 Editorial Consume V1. Generation phrases packs (prompt + protected prefix). Fill-empty / reject-invalid. Public JSON unchanged. Day plot SoT remains TODAY_CONTENT_PIPELINE I0. Attach / wire / scale / IL engines stand.
- **Public contract changed?** no — internal LLM input / editorial gate
- **Migration required?** no
- **Canon updated?** yes — `docs/astrology/IL4_EDITORIAL_CONSUME_V1.md` · inventory step 41 / KC-C-CONSUME · IL §6.67
- **Backward compatible?** yes — missing pack omits consume instruction

## Architecture impact — IL-1 1.3.112 IL-4 surface attach (2026-08-23)

- **SoT before:** Wire 1.3.111 live at library layer only. Product LLM paths ignored IL-4. Today meaning polish PAUSED until surfaces read packs.
- **SoT after:** IL-4 Surface Attach V1 locks the product gateway. `il4_expression_pack` on Today / Profile / Compatibility LLM inputs. Meaning still IL-2/3; voice IL-4; prompts not SoT. Public contracts unchanged. Wire / scale / IL engines stand.
- **Public contract changed?** no — internal LLM input only
- **Migration required?** no
- **Canon updated?** yes — `docs/astrology/IL4_SURFACE_ATTACH_V1.md` · inventory step 40 / KC-C-ATTACH · IL §6.66
- **Backward compatible?** yes — missing geometry omits pack

## Architecture impact — IL-1 1.3.111 Calc → IL wire (2026-08-23)

- **SoT before:** Library Scale V1 named the wire (1.3.110) and left it not live. Calc charts and IL engines sat side by side. A pass could still treat Today prompts as meaning SoT or set `active`.
- **SoT after:** Calc → IL Wire V1 is live at the **library layer**. Duck-typed calc snapshot → SkyFact → IL-2 → IL-3 → IL-4. Product surfaces are not attached. Occupancy ≠ conjunction. House 1 ≠ ASC. MC ≠ career. Next named = **attach IL-4 packs to product surfaces** (not `active`). Freeze, IL-2, IL-3, IL-4, and scale stand. Not a canonical v2.
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — `docs/astrology/CALC_IL_WIRE_V1.md` · inventory step 39 / KC-C-WIRE · IL 1.3.111 §6.65
- **Backward compatible?** yes (`draft`)

## Architecture impact — IL-1 1.3.110 Library scale (2026-08-23)

- **SoT before:** IL-4 locked (1.3.109); §7 named finite foundation, but coverage was still “next.” A pass could open a pair catalog or make Today prompts meaning SoT.
- **SoT after:** Library Scale V1 is the coverage SoT. 616 composed cells from stored atoms (0 objects). Outer gold remains candidate. Wire named, not live. Next named = **wire calc → IL** (not `active`). Freeze, IL-2, IL-3, and IL-4 stand. Not a canonical v2.
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — `docs/astrology/LIBRARY_SCALE_V1.md` · inventory step 38 / KC-C-SCALE · IL 1.3.110 §6.64
- **Backward compatible?** yes (`draft`)

## Architecture impact — IL-1 1.3.109 IL-4 Expression (2026-08-23)

- **SoT before:** IL-3 ranked frames; Expression named but unimplemented. LLM / Today prompts could still choose meaning.
- **SoT after:** IL-4 **engine** voices ranked themes by surface (tone / length / focus). Lemmas verbatim. Person-blind. Next named = **library scale**. Freeze, IL-2, and IL-3 stand. Not a canonical v2.
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — `docs/astrology/IL4_EXPRESSION_V1.md` · inventory step 37 / KC-C-EXPR · IL 1.3.109 §6.63
- **Backward compatible?** yes (`draft`)

## Architecture impact — IL-1 1.3.108 IL-3 Interpretation Engine (2026-08-23)

- **SoT before:** IL-2 bag of frames; IL-3 named as sky-internal rank but unimplemented. A next pass could still read CE, start Relevance, or write pair essays as themes.
- **SoT after:** IL-3 **engine** ranks composed frames by sky band (transit before natal; input order inside a band). Person-blind. Missing atoms dropped. Five jobs stay partitioned. Next named = **IL-4** expression. Freeze and IL-2 stand. Not a canonical v2.
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — `docs/astrology/IL3_INTERPRETATION_ENGINE_V1.md` · inventory step 36 / KC-C-ENGINE · IL 1.3.108 §6.62
- **Backward compatible?** yes (`draft`)

## Architecture impact — IL-1 1.3.107 IL-2 composition rules (2026-08-23)

- **SoT before:** atoms frozen (1.3.106); ACM §3 was a machine-vector sketch; KC-C-RULES deferred; Layer 5 gold = candidates. Compose could still become a pair catalog, collapse House 1 into ASC, or wait on CORE / gold-set 41.
- **SoT after:** IL-2 **rules** (role weights, conflict, merge) are the lemma-compose SoT. Five jobs stay five jobs. Layer 5 gold rows with stored atoms are **composed** (0 objects). Outer-planet gold rows stay candidates (missing atom). Next named = **IL-3** engine. Freeze stands. Not a canonical v2.
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — `docs/astrology/IL2_COMPOSITION_RULES_V1.md` · inventory step 35 / KC-C-RULES · IL 1.3.107 §6.61
- **Backward compatible?** yes (`draft`)

## Architecture impact — IL-1 1.3.101 Angle Canon grammar (2026-08-22)

- **SoT before:** 1.3.100 locked include/secondary/exclude. Slot count unnamed. Risk: copy `arena`; promote appearance / career from the collision-zone; treat personal vs public as a second atom; write planet-on-angle essays.
- **SoT after:** one required slot (`orientation`). Include-first. Secondary stays collision-zone. Facing as own slot surplus. Arena copy forbidden. Catalog untouched. Angle Canon fill — **done 1.3.102.** Sequence: storage → stored Planet×Angle smoke → STOP Angles → final atomic smoke.
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — `docs/astrology/ANGLE_CANON_GRAMMAR_V1.md` · IL 1.3.101 §6.55
- **Backward compatible?** yes (`draft`)

## Architecture impact — IL-1 1.3.100 Mainstream Angle Semantic Map (2026-08-22)

- **SoT before:** 1.3.99 locked orientation loci. Risk: skip the map and invent an operator; paste House 1 / House 10; treat angular = louder as meaning; ingest planet-conjunct-ASC/MC recipes.
- **SoT after:** same panel. ASC + MC territories + include/secondary/exclude. House 1/10 vocabulary is not proof. Angular prominence is not meaning. Planet-on-angle cookbooks are out. Catalog untouched. Angle Canon grammar — **done 1.3.101.** Sequence: fill → storage → stored Planet×Angle smoke → STOP Angles → final atomic smoke.
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — `docs/astrology/MAINSTREAM_ANGLE_SEMANTIC_MAP_V1.md` · IL 1.3.100 §6.54
- **Backward compatible?** yes (`draft`)

## Architecture impact — IL-1 1.3.99 Angle Canon model (2026-08-22)

- **SoT before:** KC-ANG-ASC / KC-ANG-MC were `NEED_MODEL`. House Canon forbids `1st = ASC` / `10th = MC`. Risk: copy `arena`, treat angles as routing anchors, or paste mask/career cookbooks.
- **SoT after:** ASC and MC are orientation loci (horizon vs meridian). Routing stays House. Projection-strength stays Foundation. Named Canon slots unspecified. Catalog unchanged. Mainstream Angle map — **done 1.3.100.**
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — `docs/astrology/ANGLE_CANON_MODEL_V1.md` · IL 1.3.99 §6.53
- **Backward compatible?** yes (`draft`). Deprecated as the angle job: House 1 / House 10 substitution; slots by analogy.

## Architecture impact — IL-1 1.3.98 Stored Planet × Aspect composition smoke (2026-08-22)

- **SoT before:** 1.3.82 scored AspectPair PASS from `interaction`. 1.3.97 stored `canon.relation`. Trine and sextile still share `interaction=flow`.
- **SoT after:** live AspectPair frames read `astro.aspect.*.canon.relation`. Four gates PASS. Historical 1.3.82 AspectPair = snapshot. Catalog unchanged. **STOP Aspects.** Angle model — **done 1.3.99.**
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — `docs/astrology/ASPECT_CANON_COMPOSITION_SMOKE_V1.md` · IL 1.3.98 §6.52
- **Backward compatible?** yes (`draft`)

## Architecture impact — IL-1 1.3.95 Aspect Canon grammar (2026-08-22)

- **SoT before:** 1.3.94 locked aspect territory. One-slot vs two-atom Canon undecided. Risk: two atoms because Signs had two or because `requires_action` exists; copy `interaction` as Canon; write pair essays.
- **SoT after:** Aspect = topology/quality of the link, not its meaning. One required slot (`relation`). Effort / participation / `requires_action` surplus. Conjunction stays mixed-valence. Extra slots for a pretty sentence are IL-2, not Canon. Stored `interaction` is classical grain, not this slot. Dry-run only. Catalog untouched. Next = Aspect Canon fill.
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — `docs/astrology/ASPECT_CANON_GRAMMAR_V1.md` · IL 1.3.95 §6.49
- **Backward compatible?** yes (`draft`). Deprecated as grammar source: Foundation §2.4; `requires_action` as a second atom.

## Architecture impact — IL-1 1.3.94 Mainstream Aspect Semantic Map (2026-08-22)

- **SoT before:** Houses closed (1.3.93 PASS). Risk: skip the map because `friction` / `flow` already compose; paste Foundation §2.4; treat square as “challenge causes growth.”
- **SoT after:** same panel as planets/signs/houses. Five major-aspect territories + include/secondary/exclude. Aspect = relation between functions, not a theme. One-slot vs two-atom Canon undecided. Catalog untouched. Next = Aspect Canon grammar.
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — `docs/astrology/MAINSTREAM_ASPECT_SEMANTIC_MAP_V1.md` · IL 1.3.94 §6.48
- **Backward compatible?** yes. Aspect objects stay `DRAFT_CLASSICAL`.

## Architecture impact — IL-1 1.3.93 Planet × House composition smoke (2026-08-22)

- **SoT before:** 1.3.92 stored `canon.arena`. 1.3.82 / 1.3.88 Moon × 4th PARTIAL. Risk: Lilly `domain` as operator, or pair essays to force PASS.
- **SoT after:** PlanetInHouse reads stored `house.canon.arena`. Moon × 4th ≠ Moon × 10th. Same 4th pack on Moon / Mars / Venus. Historical PARTIAL = snapshot. Catalog unchanged. **STOP Houses.**
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — `docs/astrology/HOUSE_CANON_COMPOSITION_SMOKE_V1.md` · IL 1.3.93 §6.47
- **Backward compatible?** yes (`draft`). Deprecated as next step: improving House packs without a named Composition Engine failure.

## Architecture impact — IL-1 1.3.92 House Canon storage + materialization (2026-08-22)

- **SoT before:** House Canon lived in a doc. Twelve house drafts were Lilly `domain` / `people` / `activities` only. Schema forbade `canon` on `type=house`.
- **SoT after:** `type=house` may carry optional `canon` as `$defs.house_canon_pack` (`arena` only). Twelve drafts carry locked 1.3.91 packs. Lilly fields unchanged. Status `draft`. Aspects omit `canon`. ASC/MC not materialized. Runtime still ignores `draft`.
- **Public contract changed?** yes — optional house `canon` nest; twelve draft houses now include `canon`
- **Migration required?** no — nothing `active`
- **Canon updated?** yes — `docs/astrology/HOUSE_CANON_STORAGE_MATERIALIZATION_V1.md` · IL 1.3.92 §6.46 · schema `$defs.house_canon_pack` · `objects_v1.json`
- **Backward compatible?** yes for runtime (`draft`). Clients that only read Lilly `domain` still see CA I.7.

## Architecture impact — IL-1 1.3.90 House Canon grammar (2026-08-22)

- **SoT before:** 1.3.89 locked house territory. Risk: two slots because Signs had two; copy planet.domains; equate House 1 with ASC.
- **SoT after:** House = arena (where). One required slot. planet.domains ≠ house.arena. Dry-run only. Catalog untouched. Next = House Canon fill.
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — `docs/astrology/HOUSE_CANON_GRAMMAR_V1.md` · IL 1.3.90 §6.44
- **Backward compatible?** yes. House objects stay `DRAFT_CLASSICAL`.

## Architecture impact — IL-1 1.3.89 Mainstream House Semantic Map (2026-08-22)

- **SoT before:** 1.3.88 PlanetInSign PASS. Moon × 4th PARTIAL. Risk: paste Lilly, paste Foundation §2.3, equate House 1 with ASC, or derive arenas from natural signs.
- **SoT after:** same panel as planets/signs. Twelve house territories + include/secondary/exclude. House ≠ angle. House ≠ natural sign. Catalog untouched. Next = House Canon grammar.
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — `docs/astrology/MAINSTREAM_HOUSE_SEMANTIC_MAP_V1.md` · IL 1.3.89 §6.43
- **Backward compatible?** yes. House objects stay `DRAFT_CLASSICAL`.

## Architecture impact — IL-1 1.3.88 Planet × Sign composition smoke (2026-08-22)

- **SoT before:** 1.3.82 Venus × Capricorn PARTIAL. Packs on drafts (1.3.87). Risk: classification as operator, or pair essays.
- **SoT after:** PlanetInSign PASS from `sign.canon.manner`. Discrimination / operator / classification-independence PASS. Moon × 4th PARTIAL. Catalog unchanged. STOP Signs. Next = Houses Mainstream.
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — `docs/astrology/SIGN_CANON_COMPOSITION_SMOKE_V1.md` · IL 1.3.88 §6.42
- **Backward compatible?** yes. Runtime still ignores `draft`. 1.3.82 remains historical PARTIAL.

## Architecture impact — IL-1 1.3.87 Sign Canon materialization (2026-08-21)

- **SoT before:** schema nest existed; twelve sign drafts were classification-only.
- **SoT after:** twelve drafts carry locked `canon`. Classification unchanged. Later-interpretive `excess` omitted. Next = 1.3.88 smoke-test (separate gate). **Done 1.3.88.**
- **Public contract changed?** yes — twelve draft signs now include `canon`
- **Migration required?** no
- **Canon updated?** yes — `docs/astrology/SIGN_CANON_MATERIALIZATION_V1.md` · IL 1.3.87 §6.41
- **Backward compatible?** yes. Runtime still ignores `draft`.

## Architecture impact — IL-1 1.3.86 Sign Canon storage (2026-08-21)

- **SoT before:** twelve packs locked in a doc; `canon` on signs had no legal shape.
- **SoT after:** optional `canon` on `type=sign` = `manner` · `excess`. Catalog unchanged. Next = write packs onto sign drafts.
- **Public contract changed?** yes — optional sign `canon` nest
- **Migration required?** no
- **Canon updated?** yes — `docs/astrology/SIGN_CANON_STORAGE_V1.md` · IL 1.3.86 §6.40
- **Backward compatible?** yes. Sign objects stay classification-only until fill.

## Architecture impact — IL-1 1.3.85 Sign Canon fill (2026-08-21)

- **SoT before:** grammar locked two slots; dry-run lemmas were illustrative. Risk: dump all 1.3.83 families, or copy ruler function into sign manner.
- **SoT after:** twelve packs locked with origin tags. Four gates pass. Unused families stay in territory. Next = Sign Canon storage.
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — `docs/astrology/SIGN_CANON_V1.md` · IL 1.3.85 §6.39
- **Backward compatible?** yes. Sign objects stay classification-only.

## Architecture impact — IL-1 1.3.84 Sign Canon grammar (2026-08-21)

- **SoT before:** sign territory locked; next risk was copying planet six slots or dumping all families into Sign Canon.
- **SoT after:** Sign = manner (how). Two slots: `manner` · `excess`. Canon narrower than territory is expected. Next = Sign Canon fill. **Done 1.3.85.**
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — `docs/astrology/SIGN_CANON_GRAMMAR_V1.md` · IL 1.3.84 §6.38
- **Backward compatible?** yes. Sign objects stay classification-only.

## Architecture impact — IL-1 1.3.83 Mainstream Sign Semantic Map (2026-08-21)

- **SoT before:** 1.3.82 named a missing Sign Canon manner operator. Next risk: personality dumps or `earth` → practical.
- **SoT after:** same panel as planets. Include/secondary/exclude locked for 12 signs. Classification is not proof. Trait ≠ manner named, not split. Next = Sign Canon grammar.
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — `docs/astrology/MAINSTREAM_SIGN_SEMANTIC_MAP_V1.md` · IL 1.3.83 §6.37
- **Backward compatible?** yes. Sign objects stay classification-only.

## Architecture impact — IL-1 1.3.82 composition smoke-test (2026-08-21)

- **SoT before:** planet `canon` on seven drafts; next could have been Signs as content.
- **SoT after:** four constructions scored. Aspect PASS. Sign/house PARTIAL. Next = Signs Mainstream as Sign Canon territory.
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — `docs/astrology/PLANET_CANON_COMPOSITION_SMOKE_V1.md` · IL 1.3.82 §6.36
- **Backward compatible?** yes

## Architecture impact — IL-1 1.3.81 Sun–Saturn canon fill (2026-08-21)

- **SoT before:** `canon` nest existed; packs lived in a doc.
- **SoT after:** seven planet drafts have product `canon` separate from classical `function`. Next = 1.3.82 smoke-test, not Signs.
- **Public contract changed?** yes — seven drafts include `canon`
- **Migration required?** no — still `draft`
- **Canon updated?** yes — `docs/astrology/PLANET_CANON_SUN_SATURN_FILL_V1.md` · IL 1.3.81 §6.35 · `objects_v1.json`
- **Backward compatible?** yes for runtime (`draft`)

## Architecture impact — IL-1 1.3.80 Planet Canon storage (2026-08-21)

- **SoT before:** Canon packs lived only in a doc. Risk of stuffing them into `function` / four-key `domains`.
- **SoT after:** optional `canon` nest with six grammar names. Legacy keys not product meaning. Catalog unchanged.
- **Public contract changed?** yes — optional `canon`
- **Migration required?** no
- **Canon updated?** yes — `docs/astrology/PLANET_CANON_STORAGE_V1.md` · IL 1.3.80 §6.34 · schema
- **Backward compatible?** yes for current catalog

## Architecture impact — IL-1 1.3.79 Planet Canon V1 (2026-08-21)

- **SoT before:** grammar locked; dry-run could be promoted without origin control.
- **SoT after:** ten packs locked. Each atom is direct or derived. Four audits. Next = schema pass.
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — `docs/astrology/PLANET_CANON_V1.md` · IL 1.3.79 §6.33
- **Backward compatible?** yes. Catalog unchanged.

## Architecture impact — IL-1 1.3.78 Planet Canon grammar (2026-08-21)

- **SoT before:** next was Canon shape; risk of starting from old JSON keys including `tempo`.
- **SoT after:** six engine slots. `tempo` = Foundation. `needs` ≠ `drive`. Dry-run ≠ fill. Next = 1.3.79 fill from 1.3.77. No schema.
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — `docs/astrology/PLANET_CANON_GRAMMAR_V1.md` · IL 1.3.78 §6.32
- **Backward compatible?** yes. Catalog unchanged.

## Architecture impact — IL-1 1.3.77 Mainstream Planet Semantic Map (2026-08-21)

- **SoT before:** panel #3 unnamed; mainstream could be misread as 2/3 word vote; planet table was a draft.
- **SoT after:** panel = Astrodienst · Cafe Astrology · Astrology.com. Concept families locked. Territory is not Canon and not JSON. Next = Planet Canon shape.
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — `docs/astrology/MAINSTREAM_PLANET_SEMANTIC_MAP_V1.md` · IL 1.3.77 §6.31
- **Backward compatible?** yes. Catalog unchanged.

## Architecture impact — IL-1 1.3.76 Product Canon vs Lenses (2026-08-21)

- **SoT before:** product meaning from school-convergence or the 491-claim ledger; IL unlock waited on Co–Star in-app Phase 1.
- **SoT after:** Mainstream conventions → TodayFlow Canon → runtime. Research corpus → Lenses. CORE not a gate. Co–Star = recognition check. Next = Mainstream planet map. No books. No object rewrite.
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — `docs/astrology/KNOWLEDGE_CORE_V1_PRODUCT_CANON_AND_LENSES.md` · IL 1.3.76 §6.30
- **Backward compatible?** yes. 491 claims kept as lenses.

## Architecture impact — IL-1 1.3.66 Pulse Part One extract (2026-08-18)

- **SoT before:** Pulse Part One shortlisted as humanistic; later-interpretive humanistic cell empty.
- **SoT after:** three humanistic school_specific claims on `astro.sign.classifications`. Part Two out. Required psych slots not filled. No sign objects.
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — IL 1.3.66 §6.20 · claims ledger · corpus `src.humanistic.rudhyar_pulse_of_life`
- **Backward compatible?** yes — Cell C still ACCESS_BLOCKED; planet ledgers untouched

## Architecture impact — IL-1 1.3.65 Cell C ACCESS_BLOCKED (2026-08-18)

- **SoT before:** Cell C was an open discovery cell; map said dedicated readable hunts had not been tried.
- **SoT after:** Layer 2 psychological later-interpretive is `ACCESS_BLOCKED`. Three named loci NEED_OWNER. Discovery for the slot stops. Pulse is not a substitute. No sign objects. No claims this pass.
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — IL 1.3.65 §6.11 · §6.19 · map §3 · shortlist Cell C
- **Backward compatible?** yes — Houlding claims untouched; required psych slots still unattested

## Architecture impact — IL-1 1.3.64 Houlding ontology extract (2026-08-18)

- **SoT before:** shortlist admitted Houlding ontology; classification ledger had Ptolemy/Lilly/Valens only.
- **SoT after:** three traditional school_specific claims on `astro.sign.classifications`. Rulers out. No sign objects. Later-interpretive slots still unattested.
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — IL 1.3.64 §6.18 · claims ledger · corpus `src.traditional.houlding_triplicities`
- **Backward compatible?** yes — planet ledgers untouched; pending Arroyo/Rudhyar unchanged

## Architecture impact — IL-1 1.3.63 Layer 2 shortlist (2026-08-18)

- **SoT before:** criteria locked; map forecast could still be treated as corpus; Cell C could be won by TOC/access.
- **SoT after:** shortlist locked (IL §6.17). Houlding ontology IN; Cell C remains a cell; Pulse Part One IN; Hand Ch.10 later. No ingest. No sign objects.
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — IL 1.3.63 §6.17 · `docs/astrology/IL1_LAYER2_SIGNS_SHORTLIST.md`
- **Backward compatible?** yes — planet ledgers untouched; Houlding/Pulse not extracted

## Architecture impact — IL-1 1.3.62 Layer 2 selection criteria (2026-08-18)

- **SoT before:** literature map existed; next agent could treat map forecast as shortlist, or pick the psychological textbook by readability.
- **SoT after:** selection criteria locked separately from shortlist (IL §6.16). Epistemic ≠ access. Cell C unscored. No ingest. No sign objects.
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — IL 1.3.62 §6.16 · `docs/astrology/IL1_LAYER2_SIGNS_SELECTION_CRITERIA.md`
- **Backward compatible?** yes — planet ledgers untouched; 1.3.61 map remains landscape

## Architecture impact — IL-1 1.3.61 Layer 2 literature map (2026-08-18)

- **SoT before:** schools/source types existed; bibliography could still start from Arroyo/Rudhyar pending IDs.
- **SoT after:** literature map from the school × constituent matrix. Minimal corpus named. No ingest. No shortlist yet. No sign objects.
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — IL 1.3.61 §6.15 · `docs/astrology/IL1_LAYER2_SIGNS_LITERATURE_MAP.md`
- **Backward compatible?** yes — planet ledgers untouched

## Architecture impact — IL-1 1.3.60 Layer 2 schools + source types (2026-08-18)

- **SoT before:** Layer 2 definition existed; school list did not. Sign pending IDs still named Arroyo/Rudhyar as if they were the next authors.
- **SoT after:** IL §6.14 maps existing `source_class` onto classification vs later-interpretive bands. No new enum. Literature map still waits. No ingest. No sign objects.
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — IL 1.3.60 §6.14
- **Backward compatible?** yes — pending Arroyo/Rudhyar rows not promoted

## Architecture impact — IL-1 1.3.59 planet research-stable + Layer 2 definition (2026-08-18)

- **SoT before:** after 1.3.58 the named next task was still an access queue that could reopen planet research; Layer 2 fill-rule waited on Arroyo/Rudhyar (author-first). CORE scoring still tempting as the next planet KPI.
- **SoT after:** planet fill research-stable. No coverage-KPI hunts. Opportunistic named-locus extract only. CORE scoring blocked. Next large step = Layer 2 Signs definition before bibliography (IL §6.13). “Wait for Arroyo/Rudhyar” withdrawn.
- **Public contract changed?** no
- **Migration required?** no — no schema change; 0 sign objects
- **Canon updated?** yes — IL 1.3.59 §6.12 · §6.13
- **Backward compatible?** yes — no runtime wiring; catalog 24 draft unchanged

## Architecture impact — IL-1 1.3.58 live recount (2026-08-18)

- **SoT before:** 1.3.44 dashboard could still be read as live (next = Pluto psychological; Mars empty; CORE=0 as lead).
- **SoT after:** `docs/astrology/IL1_SUN_PLUTO_GAP_AUDIT.md` recomputed from ledgers. Slot statuses COVERED/THIN/DISCOVERED/ACCESS_BLOCKED/EMPTY. Semantic ≠ access. Queue rebuilt. No ingest. No CORE scoring.
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — IL 1.3.58 · gap audit rewrite
- **Backward compatible?** yes — no runtime wiring

## Architecture impact — IL-1 1.3.57 ACCESS_BLOCKED (2026-08-18)

- **SoT before:** empty psych slot stayed open for discovery while NEED_OWNER loci existed; Mars could still trigger a 4th-book hunt after three dedicated unread chapters.
- **SoT after:** `ACCESS_BLOCKED(slot)` — ≥3 quality independent dedicated loci, all access-closed → stop discovery for that slot. NEED_OWNER remains locus-level. Psychological Mars ACCESS_BLOCKED. §6.10 budget closed. Recount allowed. No ingest. No CORE.
- **Public contract changed?** no
- **Migration required?** no — not a schema enum
- **Canon updated?** yes — `docs/astrology/INTERPRETATION_LIBRARY_V1.md` §6.11
- **Backward compatible?** yes — no runtime wiring

## Architecture impact — Knowledge-core research order (2026-08-17)

- **SoT before:** meaning libraries could start from the first strong accessible author (IL-1: Greene/Hand became obligatory).
- **SoT after:** `docs/KNOWLEDGE_CORE_RESEARCH_ORDER_V1.md` — предмет → границы → составляющие → определения → школы → типы источников → карта литературы → критерии → shortlist → ingest. Applies to the next semantic core in any domain. IL-1 planet fill may continue; CORE is not scored from availability. Psychology/medicine evidence hierarchy is a separate axis from IL school-convergence.
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — new doc · IL 1.3.30 · README · AGENTS related canons
- **Backward compatible?** yes

## Architecture impact — Interpretation Library (2026-08-17)

- **SoT before:** TODAY_CONTENT_PIPELINE_V1 step 2 lookup named as a hole; LLM still invents primitive meanings.
- **SoT after:** Interpretation Library = that lookup (atoms first, curated combos only if non-compositional). Cluster + profile relevance change **priority**, not astrological meaning. LLM expresses packs. Today Meaning SoT remains the pipeline (not a second day-canon).
- **Public contract changed?** no (no runtime wiring yet)
- **Migration required?** no until IL-4
- **Canon updated?** yes — `docs/astrology/INTERPRETATION_LIBRARY_V1.md` · pipeline §2 · AMC §2.2 · ACM · Foundation §2 · DAY_SOURCES chain · REFERENCE §2.1/§6
- **Backward compatible?** yes — generators unchanged until Engine consumes packs

**CANON LOCKED (2026-08-15):** **Один Today Meaning SoT** = [TODAY_CONTENT_PIPELINE_V1.md](./today/TODAY_CONTENT_PIPELINE_V1.md). **Один product cycle** = [TODAY_PRODUCT_FLOW_V1.md](./today/TODAY_PRODUCT_FLOW_V1.md) (TODAY → RITUAL → MY DAY → EVENING). SCENARIO_V3 six-block **superseded** as product map. DAY_SCENARIO_V1 / B5 demoted (не канон смысла). DAY_SOURCES = facts only.

## Architecture impact — Today product flow (2026-08-15)

- **SoT before:** presentation = SCENARIO_V3.4 six blocks (1a/1b, color, tasks, loop=promise); timeline could live on Global.
- **SoT after:** TODAY_PRODUCT_FLOW_V1 — four surfaces. Timeline **shown** only on MY DAY. Evening = gratitude. Meaning unchanged (pipeline I0). Card/number remain lenses.
- **Public contract changed?** target yes, phased — ScreenFlow ids; gratitude persist; Global UI without timeline.
- **Migration required?** yes — FE cutover from six/seven steps; evening job.
- **Canon updated?** yes — TODAY_PRODUCT_FLOW_V1 · pipeline § экран · SCENARIO_V3 banner · SCREEN_FLOW §4 · README · capability TS.
- **Backward compatible?** yes API until gratitude/cutover; cached days keep old nests.
- **Next:** FE rebuilt 2026-08-15 (`docker compose … --build --force-recreate frontend`). Live `/today` 200 · image `551d5764`. TODAY Global clock + MY DAY «Ритм дня» from windows when natal empty. Hard-refresh. Gratitude History → Month → Map still later.

## Architecture impact — MY DAY Global rhythm fallback (2026-08-15)

- **SoT before:** MY DAY timeline only if `personalTimeline` (deep) and natal `glance_timeline`. Light users and empty natal saw no clock.
- **SoT after:** Rhythm mounts on any `my_day`. Natal clocks if present («Мой ритм дня»). Else Global windows × driver facts («Ритм дня»).
- **Public contract changed?** no.
- **Migration required?** no.
- **Canon updated?** yes — TODAY_PRODUCT_FLOW_V1 §3 · pipeline § экран.
- **Backward compatible?** yes; untitled windows omit.

## Architecture impact — Global day clock on TODAY (2026-08-15)

- **SoT before:** TODAY hid `windows[]`; one ranked driver; energy = 8-set label; Personal Timeline only on MY DAY.
- **SoT after:** TODAY shows Global clock from existing `global_day.windows[]` + timed transit rows (moon + drivers) + `energy_scores[primary]` as %. Personal Timeline still MY DAY only (natal × windows). Form kit blocks (`DsMetricCard`, `DsWindowCard`, `DsListRow`+`DsPlanet`).
- **Public contract changed?** no — UI reads existing nests.
- **Migration required?** no.
- **Canon updated?** yes — TODAY_PRODUCT_FLOW_V1 §1 · pipeline § экран.
- **Backward compatible?** yes; omit empty scores/windows.

## Architecture impact — Content pipeline + I0 (2026-08-15)

- **SoT before:** I1–I8 = один DayScenario Meaning SoT.
- **SoT after:** I0 + pipeline. Ownership-таблица (один decision owner на поле). Downstream non-mutation (enrich/verbalize only). Цепочка: Небо → Global Day → Natal Overlay → Ritual → Personal → Presentation. UX reveal (GLOBAL → RITUAL → PERSONAL) отдельно от authority. LLM только формулирует persist-once. Карта/число не определяют день.
- **Public contract changed?** target yes, phased — lock-only no wire bump.
- **Migration required?** yes — see pipeline overlay table.
- **Canon updated?** yes — TODAY_CONTENT_PIPELINE_V1 · DAY_SCENARIO_V1 I0/I1 · DAY_SOURCES §0 · DAY_ENGINE banner · SCENARIO_V3 · README.
- **Backward compatible?** yes cached payloads.
- **Next:** deploy when owner asks. Pipeline work order 0–11 landed in code 2026-08-15 (I0 nests, Global Engine, ritual number, manifest, guide read-only, daily_actions, poorer fallback, ScreenFlow capability, D−1 evening enqueue).

- 2026-08-15 | Today / Ritual | **Число дня не открывалось** | **CODE** | ScreenFlow `transform` + `container-type: size` ловили `position: fixed`. `DsOverlaySheet` и pick-оверлеи карты/числа теперь portal в `document.body` (z-index 200). Тесты: gate → overlay, lens → sheet.


**DONE (OPS+CODE, 2026-08-14):** **K2.6 primary · K3 complex-only** — `NEBIUS_MODEL=moonshotai/Kimi-K2.6` for day/prewarm/routine; `NEBIUS_COMPLEX_MODEL=moonshotai/Kimi-K3` + `resolve_complex_chat_model()` only for CE Stage 2–4, profile disclosure funnel, natal decode. Canon: LLM_QUALITY Nebius section.

## Architecture impact — K2.6 primary + K3 complex-only (2026-08-14)

- **SoT before:** Live `NEBIUS_MODEL=moonshotai/Kimi-K3` for all Nebius chat (day + profile).
- **SoT after:** Primary `moonshotai/Kimi-K2.6` (`resolve_default_chat_model`); K3 only via `NEBIUS_COMPLEX_MODEL` on allowlisted complex user ops (CE 2–4, profile funnel, natal decode). Empty complex → same as primary.
- **Public contract changed?** no
- **Migration required?** no — env + resolver; cached day rows keep prior model id in logs
- **Canon updated?** yes — `docs/LLM_QUALITY_AND_PROMPT_EVOLUTION.md` Nebius routing table
- **Backward compatible?** yes for GET cache

**DONE (CODE, 2026-08-10):** **Today Block 1 dashboard + detail sheet (v3.4.2)** — mockup-led cards on `day` (hero · why chips · better · support‖trap · personal); tap opens overlay sheet; CTA → orientation; timeline on orientation. No invent / no public JSON change. Canon: SCENARIO_V3.4.2.

**DONE (CODE, 2026-08-10):** **Today Block 1 = atmosphere + orientation** — page1: date/greeting/atmosphere line/pills/note/expect/timeline; page2: trap/cues/energy; meaningful mood pills; wider layout; no vibe label / no expect dupe. Canon: SCENARIO_V3.4.1.

## Architecture impact — Today day frames (2026-08-10)

- **SoT before:** Block 1 one cramped frame (vibe + trap‖cues + expect/energy).
- **SoT after:** Block 1 two ScreenFlow frames (`day` → `orientation`); pills = concrete visual_mode cues; headline = atmosphere.
- **Public contract changed?** no
- **Migration required?** yes FE step indices (+1 after day)
- **Canon updated?** yes — TODAY_SCREEN_SCENARIO_V3
- **Backward compatible?** yes API

**DONE (CODE, 2026-08-10):** **Day mood = LLM `visual_mode`** — closed 8-set (`DAY_VISUAL_MODES`); native C1 + day_story ask for id; invalid/missing → thesis.mode map fallback. Canon: FOUNDATION_UI §11.5.

## Architecture impact — Day mood via LLM visual_mode (2026-08-10)

- **SoT before:** `day_atmosphere.visual_mode` only from deterministic `thesis.mode` map.
- **SoT after:** LLM picks `visual_mode` from closed 8 (grounded|flow|radiance|momentum|clarity|tension|renewal|depth) on native scenario / day_story; atmosphere nest prefers that id; thesis map = fallback. No sky-geometry engine.
- **Public contract changed?** additive optional `day_story.visual_mode` / `day_scenario.visual_mode` (same enum as nest); `day_atmosphere` shape unchanged.
- **Migration required?** no — cached stories without field keep thesis fallback until regenerate.
- **Canon updated?** yes — FOUNDATION_UI §11.5 · §13.1
- **Backward compatible?** yes

**IN PROGRESS (CODE, 2026-08-10):** **Today six blocks (v3.4+ useful compass)** — Blocks 1·3·5·6; do/avoid = color polarity (no «делать/не делать» labels). Pack editorial voice when generation slots stabilize.

## Architecture impact — Today six blocks (2026-08-10)

- **SoT before:** handoff 12-step ScreenFlow (Welcome…Recap…Close).
- **SoT after:** six product blocks (day · rituals · instruction · color · tasks · loop); content houses v3.1 unchanged.
- **Public contract changed?** no required fields — composition; day brief uses existing `day_story` / welcome_glass / glance.
- **Migration required?** yes FE step indices / deep-links.
- **Canon updated?** yes — SCENARIO_V3.4 · SCREEN_FLOW_V1 §4 · tracker.
- **Backward compatible?** yes API; FE remap.

**PAUSED (RESEARCH):** Human Explanatory Systems Analysis v0.2 — not driving Today UI. Doc remains at `docs/audits/HUMAN_EXPLANATORY_SYSTEMS_ANALYSIS.md`.

**DONE (CODE, 2026-08-10):** **Wave B2 + Atmosphere crossfade + ritual closed-state** — promise → `day-connection.morning_intention`; practice gift start→started→complete; thin recap (priority/promise/practice); tarot idle 3 stacked backs; Atmosphere hold→out wash crossfade (skip lite/reduced-motion). Canon: `docs/today/TODAY_MAKE_YOURS_AND_WELCOME_SOT.md` §5–8.

## Architecture impact — Wave B2 / Atmosphere P2 (2026-08-10)

- **SoT before:** day promise = FE engagement only; recap = 5 tiles incl. number/card; Atmosphere mode change = instant token swap; tarot idle = single back / stackOnly deck.
- **SoT after:** promise also mirrors to Day Connection `morning_intention` (fire-and-forget); recap = 3 handoff rows; Atmosphere two-layer wash via `--day-prev-*` + `data-day-crossfade` hold|out; tarot closed-state = 3 stacked backs (live ritual kept). Practice started remains FE engagement (no new BE field).
- **Public contract changed?** no — reuses existing `POST /day-connection/{date}` fields
- **Migration required?** no
- **Canon updated?** yes — `TODAY_MAKE_YOURS_AND_WELCOME_SOT.md` §5–8
- **Backward compatible?** yes

**DONE (CODE, 2026-08-09):** **Wave B1 P0 nests on `/today/contract`** — `welcome_glass` · `today_progress` · `color_guide`. Canon: `docs/today/TODAY_MAKE_YOURS_AND_WELCOME_SOT.md`.

## Architecture impact — Wave B1 contract nests (2026-08-09)

- **SoT before:** Welcome glass = FE `buildHandoffWelcomeGlass`; progress tracker = FE `loadTodayGrowthTrackers` (N endpoints); color guide = FE `resolveTodayDayColorGuide` from morning/scenario.
- **SoT after:** BE nests on GET `/today/contract`: `welcome_glass` (visual_mode map + lunar reason + `do[]` ≤18), `today_progress.rows[]` (habit|ascetic|practice + `days_bool[7]` — **not** story `progress`), `color_guide` (props.color / talisman / catalog fill-empty). FE may compose until wired; no invent.
- **Public contract changed?** yes — additive optional top-level nests `welcome_glass`, `today_progress`, `color_guide`
- **Migration required?** no — optional fields; old clients ignore
- **Canon updated?** yes — tracker + `TODAY_MAKE_YOURS_AND_WELCOME_SOT.md` backend gap closed
- **Backward compatible?** yes

**DONE (CODE, 2026-08-09):** **Today handoff → 100% (F1+B1+F2)** — hybrid bg (Welcome+Practice photo; Atmosphere elsewhere); ScreenFlow 3-cluster dots + frame arrows + swipe 60; Priority 6 two-line; Make yours accordion (no practice); Focus two glass cards; Close inline outcomes; Number 9 blank ring; FE prefers `welcome_glass` / `today_progress` / `color_guide`. Handoff: `docs/design/design_handoff_today_flow/`.

## Architecture impact — Make yours / Welcome signal map (2026-08-09)

- **SoT before:** Make yours = progress-only or empty copy; welcome activity tags = morning priorities only (ad-hoc); progress = FE `loadTodayGrowthTrackers` undocumented.
- **SoT after:** Make yours = occupied → tracker · empty → **inline catalog pick** (no practice; no invent from `do`/`today_move`); welcome activity = do[] then priorities; greeting art = ImmersiveArtPlane `greeting` photo; Focus deepen menu = `pickTodayDepthMenu` from day scenes (catalog includes family); Поток дня timeout maps to «Не удалось загрузить.» not false «Нет соединения.»
- **Public contract changed?** additive catalog chip `family` in `depth_layer.menu` (BE); FE filters chips by day magnitude
- **Migration required?** no
- **Canon updated?** yes — `docs/today/TODAY_MAKE_YOURS_AND_WELCOME_SOT.md` · SCENARIO_V3 Make yours row
- **Backward compatible?** yes — extra menu topic; clients that dump all chips still work

**IN PROGRESS (CODE, 2026-08-09):** **DS Ritual port from docs/design handoff** — `--tf-ds-glass-*` tokens; `DsGlassCard` / `DsChipGroup` / `DsHabitStreakRow` / `DsMoodBackground`; Welcome + progress on DS (Day Atmosphere SoT, no private welcome hex). Continue pixel-pass remaining handoff steps off page CSS.

## Architecture impact — DS Ritual glass tokens (2026-08-09)

- **SoT before:** Welcome glass = private hex in `TodayStoryDeckFrames.module.css`; `DsCard` glass used raw rgba blur.
- **SoT after:** glass = `--tf-ds-glass-surface/border/blur` (handoff day-atmosphere.css); Today Welcome = `DsGlassCard` + `DsChipGroup` on Day Atmosphere; progress = `DsHabitStreakRow`.
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** tracker; live tokens in foundation + day-atmosphere dark moods
- **Backward compatible?** yes

**IN PROGRESS (CODE, 2026-08-08):** **Today handoff composition A** — ScreenFlow = 12 steps (Welcome glass → … → Close); SCENARIO_V3.3 + SCREEN_FLOW mapping; greeting CTA «Оформим сегодняшний день». Pixel polish vs lost HTML prototype still open — re-upload `design_handoff_today_flow` for parity.

## Architecture impact — Today handoff composition A (2026-08-08)

- **SoT before:** story-deck v3.2 (7 frames); handoff = UX prototype only (decision B).
- **SoT after:** handoff 12-step presentation is SoT (decision A); content houses v3.1 unchanged.
- **Public contract changed?** no
- **Migration required?** no — FE rebuild
- **Canon updated?** yes — `docs/today/TODAY_SCREEN_SCENARIO_V3.md` · `docs/foundation/SCREEN_FLOW_V1.md`
- **Backward compatible?** yes for API; `?step=` indices remap

**DONE (CODE, 2026-08-10):** **Day Atmosphere single-paint / phone heat** — active `ImmersiveArtPlane` suppresses shell `--day-bg-art` + decor; inactive steps skip bitmap decode; `[data-profile-atmosphere]` hidden under `data-day-mode`; mobile/coarse: no `backdrop-filter` on sidebar / `cardGlass` / glass clusters (opaque). Canon: FOUNDATION_UI §13 · TODAY_MAKE_YOURS §0.

## Architecture impact — Day Atmosphere single-paint (2026-08-10)

- **SoT before:** Welcome/Practice could stack frame WebP + ImmersiveArtPlane; ProfileAtmosphere cosmic washes painted under day-mode; mobile still blurred sidebar/`cardGlass` over wash.
- **SoT after:** ≤1 full-bleed bitmap — step photo **or** shell wash (not both); motif washes deferred to Day Atmosphere on product frame; mobile glass = opaque tint, not live blur.
- **Public contract changed?** no — `day_atmosphere` nest unchanged.
- **Migration required?** no — frontend rebuild.
- **Canon updated?** yes — FOUNDATION_UI §13 · `docs/today/TODAY_MAKE_YOURS_AND_WELCOME_SOT.md` §0.
- **Backward compatible?** yes — visual: less stacked atmosphere on Profile/Tarot/Compat under day-mode (motifs off).

**DONE (CODE, 2026-08-08):** **Day Atmosphere mobile lite** — photo wash WebP desktop+`-m` mobile (~12–55 KB vs ~1.5–2.2 MB PNG); PNG seeds → `art-seeds/`; single-paint (frame only); decor = CSS geometry × 16 `data-day-decor`; no ambient drift on mobile/coarse + pause when hidden; tab bar opaque (no backdrop-filter). Canon: FOUNDATION_UI §13.

## Architecture impact — Day Atmosphere mobile lite (2026-08-08)

- **SoT before:** `--day-bg-art` = `public/images/backgrounds/{1–5}.png` (~9 MB total); frame + decor both painted the PNG; decor ignored geometric variants when art present.
- **SoT after:** runtime wash = WebP (`{n}.webp` / `{n}-m.webp`); decor = CSS geometry keyed by `data-day-decor`; PNG = art-seed only (`frontend/art-seeds/day-atmosphere/`).
- **Public contract changed?** no — `day_atmosphere` nest unchanged; delivery of `--day-bg-art` assets only.
- **Migration required?** no — next frontend rebuild; caches of old PNG URLs 404 unless CDN keeps them (URLs changed to `.webp`).
- **Canon updated?** yes — FOUNDATION_UI §13 / §13.4.
- **Backward compatible?** yes for API; clients hardcoding `.png` paths break (only internal FE used them).

**DONE (CODE, 2026-08-08):** **Restore Today story-deck to main/prod** — merge `cursor/ds-task-2.9-semantic-layers` (Greeting→…→Close swipe) which was never on `main`; prod had been serving pre-deck Glance stack.

**DONE (CODE, 2026-08-08):** **Поток дня = Kimi activity windows** — clocks/valence from exact-time geometry (+semisquare/sesquiquadrate); `label_short`/`detail` from Kimi `day_flow_windows_v1` in prewarm (no conflict in prompt); bank fill-empty only; FE time + valence chrome + expand detail; Утро/Вечер chrome without invented body. Canon: WAVE2 §4.

## Architecture impact — Поток дня Kimi activity windows (2026-08-08)

- **SoT before:** `label_short` = bank `today_activation_copy_v1`; pure glance clocks.
- **SoT after:** clocks+valence+driver_id = geometry; **title/detail = Kimi `day_flow_windows_v1`**; bank = fill-empty only.
- **Public contract changed?** yes — additive `detail`, `copy_source`; `label_short` = activity window (Kimi).
- **Migration required?** no — next prewarm; old clients ignore `detail`.
- **Canon updated?** yes — `docs/today/TODAY_WAVE2_CONTRACT_V1.md` §1/§4 + tracker.
- **Backward compatible?** yes — bank titles if no Kimi cache.

**DONE (CODE, 2026-08-08):** **Stop day invent hardcodes** — FE Поток дня = pure `glance_timeline` only (no Утро/Вечер/Ночь bank); BE `_SCENE_BEATS` retired from runtime (scenes = native LLM only); projector no filler do/avoid/evening; unavailable/not_ready shells = honest «Не удалось загрузить.» / lifecycle status, not DOMAIN_FALLBACKS calm invent. Canon: WAVE2 §4 · B5 · AGENTS transport rule.

## Architecture impact — stop day invent hardcodes (2026-08-08)

- **SoT before:** FE `todayStoryDayFlow` invented morning/day/evening/night; BE `_SCENE_BEATS` + heal filled expect/trap/do/avoid on deterministic/serve; projector appended filler do/avoid/evening; unavailable contract used DOMAIN_FALLBACKS calm prose.
- **SoT after:** Поток дня = glance_timeline rows only; meaning scenes = native LLM C1 only; no scenes → facts_only_unavailable; unavailable shell = «Не удалось загрузить.»; not_ready domains absent.
- **Public contract changed?** semantics — empty meaning / honest unavailable instead of invented calm; do/avoid may be length 1
- **Migration required?** no version bump; next prewarm/native rebuild; old bank caches heal clears templates without refill
- **Canon updated?** tracker + aligns WAVE2 §4 / B5 (no invent)
- **Backward compatible?** yes for field presence; clients that expected always-filled arc/domains see honest empty/unavailable

**DONE (LIVE, 2026-08-05):** **Profile UX pack** — full identity body (no dupe/collapse); drop portrait_why honesty; unclipped tension; house person-theses; natal decode = one-shot holistic story (persist by fingerprint, no re-generate CTA); canary users 1/2 `trialing`. Canon: PROFILE_NATAL_DECODE_DEPTH_V1 one-shot.

**DONE (CODE, 2026-08-05):** **Поток дня ← real glance_timeline** — story pane uses timed `day_facts.glance_timeline` again (no invented phase copy); labels name lived use (not «Окно: …»); max rows 3→5; symbols keep card/number when `networkDegraded`. Canon: TODAY_WAVE2_CONTRACT_V1 §4.
**DONE (CODE, 2026-08-05):** **Today story anchors polish** — distinct art pools; `StoryBlockCue` (in-step scroll) + `StoryNextAnchor` (foreshadow); block orders Energy/Symbols/Attributes/Insight/Close. Canon: FOUNDATION_UI §16.1 · SCENARIO_V3. Presentation only.
**DONE (CODE, 2026-08-05):** **Today Story Deck art + ↓ cues** — Greeting/Energy/Practice immersive photos (existing ritual-entry/cosmic/bg); other frames = Day Atmosphere theme; ↓ between multi-block sections. Canon: FOUNDATION_UI §16.1 · SCENARIO_V3 changelog.
**DONE (CODE, 2026-08-05):** **Today Story Deck v3.2** — ScreenFlow cuts Greeting→Energy+Flow→Symbols→Attributes→Practice→Insight→Close; color presentation→Attributes; card face kept on Symbols; overlap fix via one-job frames. Canon: SCENARIO_V3 + FOUNDATION_UI §16. Architecture impact: composition pipeline presentation.
**DONE (CODE, 2026-08-05):** **Today Story Frames** — composition presentation: ScreenFlow acts as full-bleed story frames (typography-first; glass only on interactive clusters); `layout=composition` strips dashboard header/rail; Glance scrollable=false. Jobs/houses unchanged (SCENARIO_V3). Canon: FOUNDATION_UI §16. Zone still open under 6-axis DoD (screenshot review).
**IN PROGRESS (2026-08-05):** **Task 2.9b Compatibility result** — exploration / funnel / analyze·signs personalized → `DsCallout`/`DsQuote`. Zone still open under 6-axis DoD.
**DONE (CODE, 2026-08-05):** **Task 2.9b Tarot result** — answer / next_step / A·B / confidence / why → `DsCallout`/`DsQuote`. Zone still open under 6-axis DoD.
**DONE (CODE, 2026-08-05):** **Task 2.9b Today Reading** — dual/opportunity·trap · soft-why · move if/then · vibe quote → `DsCallout`/`DsQuote`. Zone still open under 6-axis DoD.
**DONE (CODE, 2026-08-05):** **Task 2.9 foundation (PR1)** — semantic meaning layers: §5 type ladder + 5 ink colors + `DsCallout`/`DsQuote`/`DsCapsule` + catalog + `TodayDayLogicCallout` pilot. **Does not close Today or any zone.** Zone rollout = Task **2.9b+** under the same 6-axis DoD as Task 2.7 / 3.
**IN PROGRESS (2026-08-05):** **DS unification** — Practices / Profile / Compatibility still **IN PROGRESS** (not DONE). Wave 1+2 code live. Live column check @1920: Practices/Profile/Compatibility/Tarot content = **832px** (`--tf-shell-max`). Owner screenshot parity still required before zone DONE / Onboarding.
**layout DoD ✅ (2026-08-05):** Task 2.7 — hub wrappers → `--tf-shell-max`; Practices/Profile/Compatibility/Tarot column literals tokenized; width rule in `check_ds_style_gate.py`. Zones still **IN PROGRESS**.
**Wave 2 code ✅ (2026-08-05):** Task 2.6 rgba/color-mix gate + Compatibility local cards → `--day-*`/`--tf-*`; Task 2.6b ~382 font-size → `--tf-type-*` on three zones + Tarot. Baseline rewritten (v2). Screenshot review still required for zone DONE.
**DONE (2026-08-04):** DS Task 2 — Weekly + Challenges DsCard pilot + `--day-*` decorative (Task 1.5 folded). PR #9 merged. Screenshots: `docs/audits/ds-task2-screenshots/`.  
**PARTIAL (2026-08-04):** DS Task 3 — Today composition wave (`DsButton` CTAs + day-tint). PR #10 merged — color/CTA only; layout+type still open under DS unification.  
**IN PROGRESS (reopened):** DS Task 3 — Practices wave — PR #11 color/CTA landed; layout / rgba honesty / typography / screenshots pending.  
**IN PROGRESS (reopened):** DS Task 3 — Profile wave — PR #12 color/CTA landed; same reopen.  
**IN PROGRESS (reopened):** DS Task 3 — Compatibility wave — PR #13 color/CTA landed; rgba local cards still present; same reopen.
**DONE (2026-08-04):** Day shell chrome — day-mode on all product routes; evening phase no longer recolors shell; sidebar stretch fix. PR #14 merged + frontend rebuild.
**DONE (2026-08-04):** DS Task 1 — style gate merged PR #8 (`scripts/check_ds_style_gate.py` · Jest in `npm test` · PR checklist). Separate CI workflow job **not** required.  
**DONE (2026-08-04):** DS Task 0 — `design/profile-journey-premium` promoted → `main` (FF, PR #7). Deploy SoT: `docker compose -f docker-compose.prod.yml up -d --build` on this host.  
**DONE (2026-08-04):** Today Screen fix pack — Daily Focus · nearest→practice · chorus energy · plot beats · seasonal color · trap≠avoid · hook variants.  
**DONE (2026-08-04):** Glance P0 — **Daily Focus** replaces «Сферы дня» chips; dead `TodayLifeSpheresSection` removed (V1 R15–R17).  
**DONE (2026-08-03):** ScreenFlow content jobs **v3.1** — P0+P1+P2 gap plan closed on branch (seed-kill · domain4 · Plot wash · serve heal · LLM hard-gate · native opaque `serves_conflict`).  
**IN PROGRESS:** **Reading why-step** — `scene.why` / `domain_verdicts.why_short` before narrative; progressive expand for scene+dual. Glance/Plot/clip slice shipped. Soft-heal canary + v3.1b concreteness continue.  
**ALSO IN PROGRESS:** **Soft-heal one-field gates** — `healed:<rule>` for conflict_link / incomplete forces / broken props / scenes_too_many; seed-kill + structural + scenes_too_few stay hard.  
Prior: card_base_v1 cutover live · editorial polish minors ongoing.

### DS zone Definition of Done (6 axes — 2026-08-05)

A product zone is **DONE** only when **all** are true:

1. **Color / hex+CTA** — existing DS style gate clean for the zone  
2. **Color / rgba honesty** — no hardcoded `rgba()`/`color-mix()` paints under zone-local vars; surfaces → `--tf-*` / `--day-*` (Task 2.6)  
3. **Typography** — Foundation roles Display / Hero / Section / Subtitle / Body / Comment / Label (+ portal-title); no private `font-size` scale (Task 2.6b); ink quintet + semantic blocks when Task 2.9b applies  
4. **Day Atmosphere** — product route under day-mode; phase clock does not recolor shell when mode pinned  
5. **Shell / layout** — `--tf-shell-max` / `--tf-shell-readable`; no phone-column / random px; no double-shell (Task 2.7)  
6. **Screenshot parity** — side-by-side reads as one system (owner review)

**Process:** After Wave 1 alone → `layout DoD ✅`, zones stay **IN PROGRESS**. Real DONE only after Wave 1 + Wave 2 + screenshot review. Onboarding after that. Task 3.5 Atmosphere picker on `/design-system` = between later waves, non-blocking. **Task 2.9 foundation ≠ zone DONE**; Task **2.9b+** (Today / Tarot / Compatibility / Profile / Practices) uses this same 6-axis DoD.

## Architecture impact — Profile UX pack (identity / trap / houses / natal decode one-shot) (2026-08-05)

- **SoT before:** CE portrait + mid-word clips (`_MAX_CORE`/`_MAX_TRAP`); recognition_line = short duplicate; portrait_why honesty meta; houses = encyclopedia tags; natal decode re-POST LLM each click/reload.
- **SoT after:** CE unchanged as personality SoT; full identity body; unclipped trap/insight (prose_clip); houses = person theses; natal decode = richer CE-grounded life story (planets + numerology), **persisted one-shot** per fingerprint.
- **Public contract changed?** yes (additive/soft) — GET natal-decode may return ready artifact; POST idempotent when cached; portrait_why drops title/honesty.
- **Migration required?** no — re-publish canary + one ops decode; trial ops for users 1/2.
- **Canon updated?** yes — PROFILE_NATAL_DECODE_DEPTH_V1 one-shot + fingerprint invalidation.
- **Backward compatible?** yes — old clients re-POST get cached body.

## Architecture impact — Glance timeline max 5 + actionable labels (2026-08-05)

- **SoT before:** `glance_timeline` ≤3; minor harmonics often rendered as opaque «Окно: импульс/слова»; story Поток дня briefly used invented phase copy.
- **SoT after:** `glance_timeline` ≤5 from same natal activation pool + exact-time; labels name lived use (tasks/dialogues/…); story Поток дня = pure render of glance_timeline; symbols keep local card/number under networkDegraded.
- **Public contract changed?** yes — max glance rows 3→5; `label_short` bank wording (still no planet/aspect jargon)
- **Migration required?** no — regenerates on next day_facts assemble (clear activation TTL / hard refresh)
- **Canon updated?** yes — `docs/today/TODAY_WAVE2_CONTRACT_V1.md` §1 / §4
- **Backward compatible?** yes for old caches with ≤3 rows; FE tolerant

## Architecture impact — Task 2.9 semantic meaning layers (2026-08-05)

- **SoT before:** FOUNDATION_UI §5 at Display 40 / Hero 33 / Section 20 / Body 15 / Caption 10–11; ink via scattered `--tf-ink` / `--tf-body` / `--tf-caption`; meaning blocks ad-hoc (inline styles, local `border-left`, freeform labels).
- **SoT after:** §5 ladder **48–60 / 34 / 24 / 18 / 16 / 14 / 12**; **exactly 5 text colors** (§5.1); `DsCallout` (tone × label) / `DsQuote` / `DsCapsule` as shared semantic blocks; vertical rail primary accent. Primary CTA fill remains gold; action *text* = `--tf-accent-numerology`.
- **Public contract changed?** no
- **Migration required?** no (visual/token only); zone rollouts = Task 2.9b+ under 6-axis DoD
- **Canon updated?** yes — `docs/TODAYFLOW_FOUNDATION_UI.md` §5 / §5.1 / §6 / §15.2
- **Backward compatible?** yes for JSON; visual type sizes jump via `--tf-type-*`

## Architecture impact — Glance Daily Focus replaces sphere chips (2026-08-04)

- **SoT before:** Glance Экран 0 secondary = ≤2 domain chips («Сферы дня») from Reading magnitude; dead `TodayLifeSpheresSection` file still in tree; legacy peak/caution sphere grid on non-product path; legacy `?experience=1` synthesis used title+lines Daily Focus without prioritize/avoid.
- **SoT after:** Glance secondary = one **Фокус дня** (`buildGlanceDailyFocus`: title + prioritize/avoid from `day_story`); no equal sphere chips; `TodayLifeSpheresSection` deleted; legacy context sphere grid gated off; legacy `?experience=1` day_synthesis uses the same Glance Daily Focus model (+ tarot trap only fills empty avoid).
- **Public contract changed?** no — FE composition only
- **Migration required?** no
- **Canon updated?** yes — `docs/today/TODAY_SCREEN_SCENARIO_V3.md` Экран 0 §5 + changelog; aligns `TODAY_SCREEN_V1_CANON.md` §7.7 / R15–R17
- **Backward compatible?** yes — Reading chapters unchanged; chip deep-link to Reading removed

## Architecture impact — Today Screen fix pack P0.2 + P1 + P2 (2026-08-04)

- **SoT before:** Nearest = timed label only; energy = pulse/score path; Plot = conflict why paragraph; color clothing flat; `avoid_color.why` pasted scene trap; opportunity/trap allowed «ярлык: список».
- **SoT after:** Nearest keeps timed signal + tap → `/practices/{id}?run=1` (or Move); Glance energy prefers `interpretive_chorus` effect+cause; Plot renders `scenes[]` as setup/tension/turn beats; color `where_to_use` seasonal warm/cold clothing+accessory by month; avoid why = catalog color psychology (no trap paste); native prompt bans list-label trap/opportunity style; HookRevealShell `variant` tarot|numerology.
- **Public contract changed?** no additive required — props.where_to_use keys unchanged after seasonal pick; avoid.why semantics tightened
- **Migration required?** no — regenerates on next day_scenario build
- **Canon updated?** yes — SCENARIO_V3 Экран 0; tracker
- **Backward compatible?** yes — old caches without seasonal keys still use flat clothing; FE omit-tolerant

## Architecture impact — Tarot answer-first composition (2026-08-04)

- **SoT before:** UI order symbols → story → answer → step; `direct_answer`/`next_step` could carry card jargon.
- **SoT after:** UI order answer → step → A/B → confidence → why (collapsed). Prompt `tarot-interpretation-v1.10` + gate `user_facing_jargon`. Public fields unchanged.
- **Public contract changed?** no (semantics of answer/step tightened)
- **Migration required?** no
- **Canon updated?** yes — `SCREEN_CONTRACTS_V1` §6.5 · `TAROT_INTERPRETATION_ENGINE_V1` §4.1/§5
- **Backward compatible?** yes for old generations; new gens gated

---

## Architecture impact — Reading why-step before narrative (2026-08-03)

- **SoT before:** Reading sphere cards opened on domestic `what_happens` narrative; `scene.why` wire existed but native/v1 always emptied it; progressive expand only for opportunity/trap.
- **SoT after:** Reading step 1 = why this sphere (`scene.why` from native `why_sphere` / bank beat, else `domain_verdicts.why_short`); never Plot `why_arose` paste. Step 2 on expand = narrative + opportunity/trap. Canon TODAY_SCREEN_SCENARIO_V3 Экран 3.
- **Public contract changed?** additive — `scenes[].why` may be non-empty (was present empty); LLM JSON adds `why_sphere`
- **Migration required?** no — FE omit-tolerant; empty why keeps prior narrative-first + dual expand
- **Canon updated?** no new file — aligns SCENARIO_V3 Экран 3 + DAY_SCENARIO Act V; tracker SoT for this slice
- **Backward compatible?** yes — old caches without why still render; domain_verdicts fallback when available

## Architecture impact — unified day sidebar ink (2026-08-03)

- **SoT before:** `SectionAtmosphereBridge` set `html[data-theme]` from system appearance; mood `night` / day-phase evening flipped `--tf-ink` to light; sidebar nav used hardcoded dark rgba + white overrides under `[data-theme=dark]` → dark-on-dark or white-on-day (Profile).
- **SoT after:** no `data-theme` on `<html>`; `html[data-day-mode]` locks readable dark ink + day glass; sidebar nav/meta/settings use `--tf-ink` tokens; dark nav overrides only when day-mode absent.
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — FOUNDATION_UI §11.1
- **Backward compatible?** yes — non-day fixtures keep dark nav fallback

## Architecture impact — app-wide Day Atmosphere + flat Today acts (2026-08-03)

- **SoT before:** Day Atmosphere gated to `/today`; Tarot forced `theme:"dark"` + void section; product frame followed system appearance dark; Plot/Symbols/Reading/Move/Response wrapped in ActShell/motif chrome (nested vs Glance).
- **SoT after:** `data-day-mode` on all product routes; Tarot shell no longer forces dark; product frame defaults to light (day tint owns chrome); section void / tarot aliases yield to day tokens; ScreenFlow acts use flat Block stacks (`ProductJourneyScene chrome={false}`; Plot/Symbols without ActShell; Plot hero = glass Block).
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — FOUNDATION_UI §11.1 · SCREEN_FLOW_V1 §1.5 flat act surface
- **Backward compatible?** yes — non-ScreenFlow journey paths may still use ActShell chrome; explicit `themeProp` still overrides frame light default

## Architecture impact — shell soft-tint from Day Atmosphere (2026-08-03)

- **SoT before:** Product sidebar/rail stayed on static route `section-atmosphere` / glass tokens while main frame used `data-day-mode` art — visual “inset” of one UI in another. Diagnosis sometimes pointed at totem color / `MOOD_CELL_COLORS` as shell drivers (incorrect).
- **SoT after:** On Today only, `html[data-day-mode][data-atmosphere="today"]` aliases `--section-accent*` / glass / sidebar surface to `--day-*` (FOUNDATION_UI §11.1/§11.4). Bridge clears `data-day-mode` off `/today` (Tarot keeps Section dark). Totem color name and heatmap moods remain non-shell. Sidebar wrapper uses `sidebarSlot` stretch so rail is full-height.
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — FOUNDATION_UI §11.1 clarifies Section vs Day Atmosphere vs content color
- **Backward compatible?** yes — off Today / without `data-day-mode`, section presets unchanged

## Architecture impact — Glance energy + day art backgrounds (2026-08-03)

- **SoT before:** Pulse («Энергия дня») on Plot only; Day Atmosphere used CSS geometric decor without `public/images/backgrounds/{1–5}.png` art seeds; live frontend could lag chrome unmount.
- **SoT after:** Glance shows optional pulse Block (SCENARIO_V3 Экран 0); `--day-bg-art` maps visual_mode → art PNGs on product frame (FOUNDATION_UI §13.4 seed wiring); ScreenFlow step titles sr-only by default.
- **Public contract changed?** no
- **Migration required?** no — empty pulse = omit; missing art falls back to wash/base
- **Canon updated?** yes — SCENARIO_V3 Экран 0 energy slot; day-atmosphere.css art map
- **Backward compatible?** yes

## Architecture impact — Response tap → DsButton §17c (2026-08-03)

- **SoT before:** Response `TodayTapWidget` used ad-hoc `.tapBtn` / `.tapBtnSecondary` in module.css.
- **SoT after:** Choices render via `DsButton` (secondary/ghost + selected class); layout/selected only in consumer CSS (FOUNDATION_UI §17c). Jobs/tap API unchanged.
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — FOUNDATION_UI §15.6 / §17c status
- **Backward compatible?** yes — same testids / postTap payload

## Architecture impact — unmount labeled ActNav strip (2026-08-03)

- **SoT before:** Today mounted `TodayActNav` name row (Сводка·Сюжет·Символы·Чтение·Действие·Отклик) above ScreenFlow; ScreenFlow chrome also showed «Назад»/«Далее».
- **SoT after:** Labeled strip not mounted; `showStepControls` default false — progress = ScreenFlow dots + swipe/keyboard (SCREEN_FLOW_V1 §1.5; SCENARIO_V3 Экран 0). Prev/next opt-in on primitive only.
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — SCREEN_FLOW_V1 §1.5/§4 · SCENARIO_V3 Экран 0 chrome wording
- **Backward compatible?** yes — swipe/dots/keyboard remain; fixtures may pass `showStepControls`
## Architecture impact — ActNav / ScreenFlow day-accent chrome (2026-08-03)

- **SoT before:** `TodayActNav` + ScreenFlow dots/controls used fixed peach/gold chrome, independent of `visual_mode`.
- **SoT after:** Nav accent consumes `--day-decor-color` / `--day-accent-soft` / `--day-surface-tint` (FOUNDATION_UI §11.4); gold fallbacks when `--day-*` unset. No ordinals; jobs/order unchanged (SCREEN_FLOW_V1 §1.5).
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — FOUNDATION_UI §11.4 ActNav/ScreenFlow accent note
- **Backward compatible?** yes — CSS fallbacks outside Day Atmosphere

## Architecture impact — Glance/Plot/clip compliance (2026-08-03)

- **SoT before:** Mid-word `_clip` on day_scenario surfaces; avoid catalog names glued with «theme»; Glance printed `short_name`/registry label as uppercase mode tag; sphere chips missing; FE always rendered `Натяжение между A и B` when forces present.
- **SoT after:** Shared `prose_clip_v1` (sentence/word boundary + midword heal) on native/v1/project/personalization/dramaturgy/day_story/hook; catalog + serve + FE strip theme from avoid names; Glance never prints classification/`short_name` (house labels only) + ≤2 Reading chips; Plot leads with `why_arose` only (no invented tension opener; strips baked binary opener); native prompt forbids default X-vs-Y.
- **Public contract changed?** no (presentation + clip quality; opposing_forces still optional in wire)
- **Migration required?** no — serve-heal cleans legacy avoid names / midword `…`; regenerate for fresh native prose
- **Canon updated?** no new canon file — aligns TODAY_SCREEN_SCENARIO_V3 Экран 0/1; tracker SoT for this slice
- **Backward compatible?** yes — FE omit-tolerant; old cached force pairs no longer force binary UI opener

## Architecture impact — Glance house labels (Тема дня / Ближайшее окно) (2026-08-03)

- **SoT before:** Glance texture Block eyebrow = `short_name`/«Сводка дня»; nearest Block = «Сигнал дня».
- **SoT after:** Stable house labels «Тема дня» + «Ближайшее окно» (FOUNDATION_UI §16); texture still tone synthesis (SCENARIO_V3 Экран 0); thesis as detail when ≠ texture; date chrome = «Сегодня» + date line.
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — FOUNDATION_UI §16 nearest/theme house labels
- **Backward compatible?** yes — copy/UI only

## Architecture impact — Glance drop ScreenFlow gauge (2026-08-03)

- **SoT before:** TODAY_SCREEN_SCENARIO_V3 Экран 0 + FOUNDATION_UI §11.9 — Glance hero required ScreenFlow gauge (шаг N/6) as progress chrome inside the act.
- **SoT after:** Progress = bottom ScreenFlow chrome only (dots + labels / swipe per SCREEN_FLOW_V1 §1.5); no gauge widget in Glance hero. Jobs (texture / nearest / teaser / ≤2 chips) unchanged.
- **Public contract changed?** no
- **Migration required?** no
- **Canon updated?** yes — TODAY_SCREEN_SCENARIO_V3 Экран 0 · FOUNDATION_UI §11.9 · this tracker
- **Backward compatible?** yes — FE presentation only

## Architecture impact — soft-heal one-field native/scenario gates (2026-08-03)

- **SoT before:** `HARD_NATIVE_VALIDATE_MARKERS` / `HARD_SCENARIO_VALIDATE_ERRORS` hard-rejected on empty `link_to_conflict`, incomplete `opposing_forces`, any prop missing `origin_scene_id`, and `scenes_too_many` — entire native day dropped (retry → unavailable / keep-prior).
- **SoT after:** Those one-field misses are **auto-healed** before hard reject: opaque `link_to_conflict`/`serves_conflict` = «тон дня» when voice/scene otherwise present; incomplete force pair → clear both; broken props → drop that prop; `scenes_too_many` → trim to 4. Each heal logged as `failure_class=healed:<rule>` (+ `healed_rules[]`) — not silent success. **Still hard:** all seed-kill markers, structural schema, `scenes_too_few`, `scene_missing_setup`.
- **Public contract changed?** no (same scenario shape; more days may accept with optional props omitted)
- **Migration required?** no
- **Canon updated?** no — policy in `day_scenario_gate_maturity_c36.py`; tracker SoT for this slice (aligns DAY_SCENARIO / v3.1 optional opposing_forces)
- **Backward compatible?** yes

## Architecture impact — Kimi-K3 primary + DeepSeek fallback (2026-08-03)

- **SoT before:** Primary `deepseek-ai/DeepSeek-V4-Pro`; provider-fail → Kimi `moonshotai/Kimi-K2.6` once on attempt0; attempt≥1 = Kimi-only (via `nebius_fallback_model`).
- **SoT after:** Primary `moonshotai/Kimi-K3` (voice/metaphor quality); provider-fail → DeepSeek `deepseek-ai/DeepSeek-V4-Pro` once on attempt0; attempt≥1 = **Kimi-only** (primary, `allow_model_fallback=False` — no hop to dry DeepSeek on gate retry). Wall `LLM_BACKGROUND_TIMEOUT_SECONDS=180` unchanged. Keep-last-good / `unavailable_after_llm` / no B5 invent unchanged.
- **Public contract changed?** no
- **Migration required?** no — env/compose swap; force_rebuild canary to taste new voice
- **Canon updated?** yes — `docs/LLM_QUALITY_AND_PROMPT_EVOLUTION.md` Nebius defaults; tracker ops SoT for model chain
- **Backward compatible?** yes for GET cache; old DeepSeek-primary rows remain queryable

## Architecture impact — DeepSeek→Kimi + no B5 invent (2026-08-03)

- **SoT before:** Primary often Qwen; on native fail wire used `allow_deterministic_rebuild=True` → B5 template invent (`deterministic_fallback_after_llm`). Timeout skipped model fallback.
- **SoT after:** Primary `deepseek-ai/DeepSeek-V4-Pro`; provider-fail (incl. timeout) → Kimi `moonshotai/Kimi-K2.6` once on attempt0; attempt≥1 = **Kimi-only**; wall `LLM_BACKGROUND_TIMEOUT_SECONDS=180`. On LLM fail: **keep last good native same `(user, local_date)`** (`generation_source=kept_prior_native`, stale/refresh) else **`unavailable_after_llm`** (strip meaning). **No B5 user-facing invent** after LLM attempt. Kill-switch back to B5 is not allowed.
- **Public contract changed?** no (additive `generation_source` values; progress may stay `stale` when kept prior)
- **Migration required?** no — canary force_rebuild users 1/2 then watch; broader prewarm only if native/kept OK
- **Canon updated?** no (aligns with DAY_SCENARIO critical-fail → unavailable; tracker is ops SoT for model chain)
- **Backward compatible?** yes for GET cache; old `deterministic_fallback_after_llm` rows remain queryable

### Gap plan (native reliability) — update

| Pri | Gap | Notes |
|-----|-----|
| P0 | Instrumentation | **DONE** |
| P0 | No-retry-on-timeout (same model) | **DONE** — attempt0 may still switch primary→fallback once |
| P0 | Product metric native share | **DONE** — also tracks `kept_prior_native` / `unavailable_after_llm` |
| P0 | Kill B5 after LLM + keep-last-good | **THIS SLICE** |
| P0 | Soft-heal one-field gates + `healed:<rule>` | **THIS SLICE** — conflict_link / forces / props / scenes_too_many |
| P1 | Soft-fill `day_card_missing_conflict_link` | **superseded** by soft-heal above |
| P1 | Re-run taxonomy (a) | After canary |
| P1 | **Kimi-K3 primary voice trial** | **THIS SLICE** — swap vs DeepSeek; human tone / metaphor QA |

## Architecture impact — native day_story P0 instrumentation + no-retry-on-timeout (2026-08-03)

- **SoT before:** Native C1 up to 2 identical attempts; `generation_logs` stored `native_scenario_c1` bool only, cleared `model` on fallback, no `failure_class` / attempt durations.
- **SoT after:** Timeout → **immediate deterministic fallback** (no attempt-2 as-is). Gate/parse retries with feedback still allowed. Logs carry `generation_source`, `native_llm_c1_meta` (`failure_class` = `timeout` \| `empty` \| `parse` \| `gate:<primary_rule>` \| `other`; full markers in `reject_reason`; attempts[]; chars; model kept on fallback). Product metric script: `backend/scripts/report_day_story_native_share.py`.
- **Public contract changed?** no
- **Migration required?** no — additive log fields; old rows still queryable via `used_fallback` / bool
- **Canon updated?** no (ops/runtime policy; tracker + script SoT for metric)
- **Backward compatible?** yes

### Gap plan (native reliability)

| Pri | Gap | Notes |
|-----|-----|-------|
| P0 | Instrumentation | **DONE** — `failure_class` = `timeout` \| `empty` \| `parse` \| `gate:<rule>` \| `other`; full list in `reject_reason`. Live proof 2026-08-03: `gate:day_card_missing_conflict_link` (not timeout). |
| P0 | No-retry-on-timeout | **DONE** — `attempt2_policy=skip_identical_on_timeout_immediate_fallback` |
| P0 | Product metric native share | **DONE** — script + structured `day_story_native_metric` log line; alert default <30% among llm_attempted |
| P1 | Re-run taxonomy (a) | After 2–3 days of instrumented logs |
| P1 | Budget / slim prompt (b) | Only after real failure_class shares — not duration heuristics |
| P2 | Attempt-2 alternate strategy | Slim prompt / other model — **not** this P0 |

## Architecture impact — ScreenFlow content jobs v3.1 (2026-08-03)

- **SoT before:** [TODAY_SCREEN_SCENARIO_V3](./today/TODAY_SCREEN_SCENARIO_V3.md) v3.0 — conflict/`opposing_forces` as day spine; color on Symbols; Reading = all scenes + action; Glance ≈ conflict texture.
- **SoT after:** v3.1 — per-act jobs; **no seed leakage**; opposing_forces optional; color house = Move + intensity; Reading ≤2 + no action; Response magnitude trap / honest no-trap; Glance = tone synthesis.
- **Public contract changed?** yes (phased) — omit `opposing_forces`; Reading/DomainLens domains → `work|money|relationships|energy`; color intensity; FE presentation homes; Plot hero wash ← `thesis.mode`.
- **Migration required?** yes — generation gates + FE composition; cached A/B scenarios until regenerate.
- **Canon updated?** yes — TODAY_SCREEN_SCENARIO_V3 · SCREEN_FLOW §4 · DAY_SYMBOL_REVEAL §7–8.
- **Backward compatible?** partial — FE must tolerate omit; old clients keep showing forced conflict until BE ships.

### Gap plan (priority)

| Pri | Gap | Where | Notes |
|-----|-----|-------|-------|
| P0 | Color out of Symbols UI | `TodayCompositionSurface` symbolsBody | **DONE** `0833390` |
| P0 | Reading: drop action/avoid from chapters | `todayScenarioChapters.ts` | **DONE** |
| P0 | Stop inventing opposing_forces + allow omit in gate | `day_scenario_v1.py` · maturity gate | **DONE** |
| P0 | Color `link_to_conflict` без paste force_a/b | `build_scenario_props_v1` | **DONE** |
| P1 | Reading ≤2 by magnitude + progressive reveal | FE Reading + magnitude | **DONE** (expand CTA + irreversibility score) |
| P1 | Color intensity soft/bright in UI + apply copy | catalog/FE Move | **DONE** |
| P1 | Response: no-trap UI; pick trap by magnitude | `TodayTapWidget` | **DONE** |
| P1 | Glance texture = tone not facts/short_name | `todayGlanceTexture` | **DONE** |
| P1 | Symbols: no card/number instruction; fail banner only | HookRevealShell | **DONE** |
| P2 | Domain dictionary unify 3→4 on contract | Wave2 / day_story | **DONE** wire = work\|money\|relationships\|energy |
| P2 | Practice\|affirmation rotation single slot | Move | **DONE** (date hash XOR) |
| P2 | Plot visual tied to classification | FE hero | **DONE** `resolvePlotHeroWash(thesis.mode)` |
| P2 | Chorus/scenes stop quoting short_name A\|B | generation | **DONE** seed-kill + serve heal (`48b589c`) + LLM hard-gate (`b2d8203`) + native opaque serves/why (`fa4d915`); cluster 56/56 |

## Architecture impact — card_base_v1 cutover (explainer / question-tarot) (2026-08-01)

## Architecture impact — card_base_v1 cutover (explainer / question-tarot) (2026-08-01)

- **SoT before:** Public `TarotCard.upright`/`reversed`/spread `meaning` from EN `tarot_full_deck`; explainer `meaning` LLM/template; pack `upright_meaning`/`reversed_meaning` from deck EN.
- **SoT after:** Same fields from RU `card_base_v1` (`prose_sides` / `get_base_meaning`); explainer `tarot-explainer-v4` injects bank `meaning` and does not let LLM overwrite it; `knowledge_v1` stays pack facts only.
- **Public contract changed?** yes — semantics/locale of `upright`/`reversed`/`meaning` on card & spread payloads (EN→RU bank); explainer JSON may omit generative `meaning` (server fills from bank) + additive `meaning_source`.
- **Migration required?** no version bump; clients already display these strings.
- **Canon updated?** yes — [TAROT_CARD_BASE_V1.md](./tarot/TAROT_CARD_BASE_V1.md) §3.
- **Backward compatible?** yes for shape; text language of catalog fields flips to product RU.
- **Server check:** unit `tests/test_card_base_cutover_v1.py` 5/5; BE compose recreate; live `GET /tarot/cards/21` upright matches `card_base_v1` RU prose.

## Architecture impact — Day hooks + Glance overview (2026-08-01)

- **SoT before:** Glance hero = theme + 4 spheres + nearest; card/number meanings from FE major bank + EN deck + LLM explainers; color as talisman prop without hook shell; prebake orientation hardcoded upright.
- **SoT after:** Glance = 2-sec day overview (no VerdictStrip hero); hooks center on Symbols with ritual→reveal→instruction; `card_base_v1` / `number_base_v1` / COLOR_CATALOG = static base; `bridge_to_day` sole SoT = interpretive_chorus / props.color; explainer must not parallel bridge; orientation prebaked upright|reversed from digest.
- **Public contract changed?** yes — additive `hook_reveal` / `color_hook_reveal` on `/today/symbols/*` when revealed; card `meaning` prefers RU `card_base_v1`; Glance presentation (no new required day_facts fields).
- **Migration required?** no forced client bump; old clients ignore new nests. FE major bank becomes non-SoT consumer.
- **Canon updated?** yes — [DAY_SYMBOL_REVEAL_CANON_V1](./audits/DAY_SYMBOL_REVEAL_CANON_V1.md) · [TAROT_CARD_BASE_V1](./tarot/TAROT_CARD_BASE_V1.md) · DAY_SCENARIO · TODAY_WAVE2 §3.4 · TODAY_SCREEN_SCENARIO_V3.
- **Backward compatible?** yes for JSON; Glance UI no longer shows sphere tokens (intentional).
- **Server check (2026-08-01):** `docker compose -f docker-compose.prod.yml up -d --build --force-recreate backend frontend` · SHA `7dc7e8a` · BE healthy + `card_base_v1` 78 in container · live chunk `page-aa3d721a26e1734a.js` has Glance/hook shell markers · guest reveal API: `hook_reveal.base` + `bridge_status=unavailable` + fail copy (no silent empty) · `/today` guest gate blocks ScreenFlow without login (authed UI hard-refresh recommended).

## Architecture impact — Screen scenario v3

- **SoT before:** ScreenFlow steps existed; content dumped into Reading chapters; Glance = label + domains + nearest.
- **SoT after:** [TODAY_SCREEN_SCENARIO_V3.md](./today/TODAY_SCREEN_SCENARIO_V3.md) — composition of existing contract fields per screen job · **updated 2026-08-01** for Glance overview + Symbols hook arc.
- **Public contract changed?** no new required JSON; timeline `label_short` bank more distinct (body+aspect, still no jargon).
- **Migration required?** no.
- **Canon updated?** yes — TODAY_SCREEN_SCENARIO_V3 + SCREEN_FLOW §4 + README.
- **Backward compatible?** yes.
- **Server check:** FE rebuilt+force-recreate; BE restarted earlier for label bank; chunk contains `today-verdict-token` + `today-zone-plot-narrative`. Hard-refresh `/today`.

## 1) Purpose

This file is the single source of truth for:
- product problems, needs, and goals,
- target architecture,
- implementation roadmap,
- progress tracking (done / in progress / next),
- change log.

Rule: every meaningful implementation change must be reflected here.

Important:
- Product canon: [CORE_PRODUCT_CANON.md](archive/CORE_PRODUCT_CANON.md).
- **PIM center:** [PERSONAL_INTELLIGENCE_MODEL_V1.md](pim/PERSONAL_INTELLIGENCE_MODEL_V1.md) · [USER_KNOWLEDGE_MODEL.md](pim/USER_KNOWLEDGE_MODEL.md) · [INTENT_MODEL_V1.md](./INTENT_MODEL_V1.md).
- **Today experience (ACCEPTED):** [TODAY_SCREEN_V1_CANON.md](./TODAY_SCREEN_V1_CANON.md) · [TODAY_LANGUAGE_V1.md](today-language/TODAY_LANGUAGE_V1.md).
- **Practices experience (ACCEPTED):** [practices/PRACTICES_SCREEN_V1.md](./practices/PRACTICES_SCREEN_V1.md) — цикл need→practice→session→check-in→Today; locked need/format IDs.
- **Profile UI:** [PR4_PROFILE_CANON.md](./archive/PR4_PROFILE_CANON.md) (production IA; applies umbrella) · [PROFILE_EXPERIENCE_SCENARIO_V1.md](profile/PROFILE_EXPERIENCE_SCENARIO_V1.md) (**Character Engine** — SoT личности платформы) · [PROFILE_SCREEN_MASTER.md](profile/PROFILE_SCREEN_MASTER.md) (v0 visual) · [TODAYFLOW_FOUNDATION_UI.md](./TODAYFLOW_FOUNDATION_UI.md).
- **Explainable Computation (platform gate):** [EXPLAINABLE_COMPUTATION_AND_INTERPRETATION.md](explainability/EXPLAINABLE_COMPUTATION_AND_INTERPRETATION.md) — выше модулей; конфликт → umbrella.
- **Understanding progress (depth · missing · trial · sub):** [UNDERSTANDING_PROGRESS_AND_DEPTH_CANON.md](./UNDERSTANDING_PROGRESS_AND_DEPTH_CANON.md).
- **Core loop:** [CORE_USER_LOOP.md](./CORE_USER_LOOP.md) · [DAILY_NAVIGATION_MODEL.md](./DAILY_NAVIGATION_MODEL.md).
- **Product model (whole product):** [TODAYFLOW_PRODUCT_MODEL.md](archive/TODAYFLOW_PRODUCT_MODEL.md) — Personal Model, projections (doc №1).  
**Today + First Day:** [TODAY_PRODUCT_MODEL.md](./TODAY_PRODUCT_MODEL.md), [FIRST_DAY_EXPERIENCE.md](./FIRST_DAY_EXPERIENCE.md).
- **Reference Layer (P0 freeze):** [REFERENCE_LAYER_AND_BUILD_ORDER.md](./REFERENCE_LAYER_AND_BUILD_ORDER.md).
- **Platform parity:** [status/IOS_TODAYFLOW_STATUS.md](./status/IOS_TODAYFLOW_STATUS.md).

---

## 2) Extracted From User Discovery (Fixed Context)

### Problems
- Product has strong features, but no strict system architecture.
- The `Today` page is not yet a clear daily magnet in all scenarios.
- UX/visual language is inconsistent across modules.
- Risk of contradictory interpretations between sections.
- Reward mechanics are not yet implemented as a domain system.
- The product still exposes too many parallel surfaces instead of one clear user story. **Mitigation (2026-07-05):** `day_story_v1` — one LLM artifact for Today contract + derived narrative surfaces; profile/tarot single-answer contracts — next.
- The product still thinks in internal modules more than in user jobs to be done.
- The profile page is not yet the user's clear personal map.
- Text generation quality: default **`TODAY_NARRATIVE_QUALITY_MODE=trust_llm`** (2026-07-05) — post-hoc copy gates off; strict mode via env for legacy QA.
- **Acquisition UX (2026-07-05):** no «попадает?» / «это про вас?» / «откликнулось?» validation under content blocks. Product gives orientations; learning via **behavior** (mood, actions, questions text, ritual choices, navigation) per KASP channels B–I. Ritual post-reveal: optional **proximity** chips («Что сейчас ближе?») only — not accuracy checks. No per-block compatibility echo, profile atom confirm spam, or guidance resonance forms.
- **Behavioral questions map (2026-07-05, accepted):** implicit questions → signals (not validation UI). **P1:** `day_promise` + `honest_step` (ritual). **P1:** `guidance_ask` text → CUM `active_themes` semantic top-K. Pattern promotion threshold: **KASP default ≥3/14d** until product review; `behavioral_patterns.works` uses softer ≥2/14d. Full map: mood/head_topic/proximity/spheres/guidance/evening/compat navigation — see chat 2026-07-05 + DE-5 tags.

### Needs
- Core center: `Natal Chart + Numerology Core Profile`.
- Brand and system definition:
  - `TodayFlow` is the brand,
  - `Profile` is the personal map,
  - `Today` is the daily guide.
- Mobile-first product thinking:
  - primary use case is phone,
  - core screens must open fast and read in stacked sections,
  - long information should be hidden behind reveals/expanders instead of shown at once.
- Product IA with implicit JTBD routing plus core interpretation surfaces:
  - `Today`
  - `Profile`
  - `Compatibility`
  - `Tarot`
  - `Growth`
- Unified interpretation pipeline (no contradictions).
- Multi-profile support:
  - self
  - spouse / partner
  - child
- Compatibility in two modes:
  - static sign-to-sign base content (free/paid depth),
  - personalized compatibility using birth data.
- Retention system (streaks, archetypes, seals, evolution index) tied to core profile.
- API-generated high-quality texts for profile/today/tarot/compatibility.

### Goals
- Increase retention to 2-3 sessions/day.
- Make the daily flow clear on one `Today` surface, with light time-of-day emphasis and reminders instead of three separate product modes.
- Keep content coherent across all modules.
- Be monetization-ready with clear gated value.
- Remove excess complexity from screens and make profile + today immediately understandable.
- Move the product from module-first to JTBD-first.
- Reach full coverage of the 4 core JTBD: self, other, decision, today.
- Use `Today` as both a daily decision engine and a learning surface that gathers better personalization signals over time.
- Build weekly and monthly state maps as accumulated user-understanding layers, not as separate product roots.

---

## 3) Architecture Gap Analysis

### Already in place
- Broad feature coverage in backend and frontend (astro, tarot, cycles, habits, practices).
- `Today` already improved and partially merged with morning ritual behavior.
- Menstrual/cycle-related functionality exists in architecture.
- Compatibility backend routes exist.

### Missing / weak points
- **Reference Layer not unified:** astrology/tarot/numerology JSON exists but lacks unified data model, Machine/Content Contract, versioning, and Reference API — blocks clean Daily Engine and new generation work ([REFERENCE_LAYER_AND_BUILD_ORDER.md](./REFERENCE_LAYER_AND_BUILD_ORDER.md)).
- IA/navigation still reflects the older service-first model in places and is not yet fully normalized to the JTBD-first model.
- Main surfaces do not yet infer and answer user intent strongly enough by their structure and CTAs (исключение: **Today narrative** — явный слой **`intent`** в промптах после DE-6).
- No explicit universal `Core Profile Engine` contract used by all modules.
- No formal contradiction-resolution layer for interpretations.
- No durable learning layer for prompt/version/result/feedback analysis across modules.
- **DayContext → narrative** for Today is wired end-to-end including **intent** (DE-6, §4.7); **UI/explainability** по всем слоям канона и «почему вместе» с ритуалом — ещё не полностью выровнены с одним публичным пакетом DayContext.
- Compatibility productization (static library + personalization + gate logic) is incomplete.
- Decision support is present only indirectly through forecasts/tarot, not as a first-class product lane.
- Money/career and state/stabilization JTBD are partially covered in services but weakly packaged in UI.
- Reward domain model is not fully implemented end-to-end.
- Design system is not fully unified (tokens/components/layout consistency).
- Profile page is still not the canonical “my life map” surface.
- Today still contains too much secondary material in the default view.
- Legacy `quality_gate` logic is too influential in shaping generated text.

---

## 4) Target Product Architecture (Canonical)

## Layer 0: Reference Layer (foundation — build first)

Canon: [REFERENCE_LAYER_AND_BUILD_ORDER.md](./REFERENCE_LAYER_AND_BUILD_ORDER.md).

- Unified taxonomy (10 domains) + catalog table §6
- Machine Contract (engine) + Content Contract (LLM/UI)
- Status/version lifecycle (`draft` → `active` only in prod)
- Read API: `GET /reference/v1/{domain}/{code}` (target)

**Blocks until P0 active:** new Today UI, new prompts, split generation pipeline (DE-13), Calendar rhythm filters.

## Layer A: Core Intelligence
- `Core Profile Engine`
  - natal chart summary
  - numerology summary
  - stable archetype baselines
  - profile version/hash
- `Interpretation Orchestrator`
  - combines core profile + transits + cycles + context
  - conflict resolution rules
  - deterministic output envelope for frontend

## Layer B: Domain Modules
- `Today Engine`
- `Forecast Engine`
- `Tarot & Guidance Engine`
- `Compatibility Engine` (static + personalized)
- `Growth Engine` (habits, diary, practices, askesis)
- `Rewards Engine`

## Layer B.1: Canonical User Surfaces
- `Profile`
  - stable personal map
  - natal chart
  - numerology identity
  - signs / houses / strong and weak sides
  - additional profiles
- `Today`
  - only current-day interpretation
  - tarot day card
  - actionable “do / avoid / notice”

## Layer C: Experience/UI
- Unified navigation with implicit JTBD routing and clear core surfaces
- Shared component library + design tokens
- Consistent cards/actions/feedback patterns

## Layer D: Learning Loop
- `Prompt Registry`
  - module
  - version
  - prompt kind
- `Generation Logs`
  - input payload
  - profile snapshot
  - model
  - output
  - fallback/error state
- `Feedback Signals`
  - explicit user feedback
  - future implicit quality signals

Purpose:
- compare prompt versions,
- identify dead or weak outputs,
- prepare curated dataset for future tuning,
- improve prompts without online self-training in production.

---

## 4.6) Daily ritual UX canon (web + iOS parity)

This section locks **packaging** decisions for the daily engine: what the product promises on screen, how dense Today may be, and what must stay aligned across web and native clients.

**Today experience canon (web + iOS + Android):** [TODAY_SCREEN_V1_CANON.md](./TODAY_SCREEN_V1_CANON.md) · [TODAY_LANGUAGE_V1.md](today-language/TODAY_LANGUAGE_V1.md).

### Fixed product decisions

- **Unified engine inputs (north star)**  
  The day layer is assembled from the same family of signals the backend already knows: profile + natal + numerology + tarot-of-day + astro/transit context + **behavioral state** (check-ins, diary, habits, ascetics, answered questions). Delivery can be incremental; **contracts stay stable** so iOS/Android can consume the same envelopes as web.

- **Layered IA (frequency of use)**  
  `Today` = operational 24h surface (what changes today). Stable natal depth and “library” reading live under **Profile / knowledge surfaces**. Compatibility and active tarot/question flows remain **separate hubs**, not collapsed into one Today scroll.

- **Information diet**  
  Show **outcomes and one clear “why” affordance** on Today; rotate which natal/astro facet grounds the copy across days instead of exposing full chart vocabulary by default.

- **Progressive disclosure**  
  Headlines read as guidance (“сегодня уместно…”), not as raw chart rows. Technical astro backing opens in sheet / secondary reveal for users who want proof.

- **Visual direction: tactile esotericism**  
  Sand–pale rose-gold spectrum, **raised cards**, generous whitespace between blocks; separation via depth/shadow rather than heavy divider lines. Fight low-contrast “soap” by anchoring text in graphite/brown ink on matte surfaces.

- **Invisible technology**  
  Do **not** surface LLM/“ИИ” as the source of copy in user-facing UI. The product voice stays interpretive and personal; model plumbing is internal.

- **Today ritual flow parity (web ⇄ iOS)**  
  The block **«Собрать день» / «С чего начнём»** (body + calendar hint + quick chips), **life spheres (сферы)** always visible after the daily ritual spine, with a **pre–check-in hint** when mood is unset — **required on both web and iOS** (`TodayRitualFlow` / `TodayRitualFlowView` + shared copy sources).

- **Ritual spine contract (code parity web ⇄ iOS ⇄ Android scaffold)**  
  One reducer model for the main path (open day → tarot continue → number → mood → check-in): `frontend/src/lib/todayRitualSpineMachine.ts`, `ios/.../TodayRitualStateMachine.swift`, `android/.../TodayRitualSpineMachine.kt`. Illegal transitions return `null` / no-op. Meaning analytics for **number** and **mood** steps are emitted only from **`analyticsHint`** after a valid reducer transition (`executeRitualSpineAnalytics` on web/Android, `applySpineEffects` on iOS). Tests: Jest (`todayRitualSpineMachine.test.ts`), XCTest (`TodayFlowSmokeTests`), Android `ExecuteRitualSpineAnalyticsTest`.

- **iOS Today deck**  
  Card of day → numerology layer → tone/summary presented as a **horizontal page deck** (swipe / pager), reducing vertical wall-of-cards overload while keeping the same narrative order as web.

### Near-term development plan

| Priority | Item | Notes |
|----------|------|--------|
| P1 | **iOS chip deep links** | Done: chips switch to Flow + `pendingTrackerQuickCreate` → привычка (scroll + focus), цель (sheet), аскеза (sheet + `POST /tracking/ascetic-contracts`). |
| P1 | **Narrative fusion contract** | Done: `GET /tracking/fusion/{date}` и `/today/state-map` отдают **`rhythm_context`**; в `POST /today/narrative` полный `fusion` — для **guide** и **day_layer**; компактный `_fusion_slim_for_prompt` (scores + encouragement + recommendations + rhythm_context) — для **spheres**, **evening**, **deepen**. Версия промпта модуля narrative — **`today-narrative-v9`** (DE-5: `behavior_patterns`; DE-6: `intent`; DE-12: `visible_profile` / `internal_profile` в DayContext и user JSON; жёстче анти-абстракция + RU quality gate на guide/spheres). |
| P2 | **Today widget layout (bento)** | Optional user-tunable card grid on Today once baseline ritual + spheres + build-day parity is stable on both platforms. |
| P2 | **Retention loop polish** | Push → open deck → micro-task → check-in → evening close; keep triggers aligned with `DayConnection` and documented in push matrix. |

---

## 4.7) Day Engine & DayContext (coherence + learning)

**Canon:** [DAY_ENGINE_AND_COHERENCE.md](./DAY_ENGINE_AND_COHERENCE.md)

**Goal:** one logical **DayContext** drives narrative generation and explainable UI; chain **cause → interpretation → recommendation**; close the loop **recommended → did → outcome** (evening, tracking).

**Already related in codebase:** `fusion` / `rhythm_context`, `ritual_context` on `POST /today/narrative`, `core_profile`, learning layer, §4.6 ritual UX, [TODAY_PERSONALIZATION_CORE.md](./TODAY_PERSONALIZATION_CORE.md) (events + future JSON contract).

### Execution checklist

| ID | Task | Status | Notes |
|----|------|--------|--------|
| DE-1 | DayContext **v0 spec** (doc fields + optional JSON Schema draft under `docs/schemas/`) | DONE | [DAY_CONTEXT_V0.md](./DAY_CONTEXT_V0.md), `day_context_v0.schema.json`, CI `day-context-schema`, `build_day_context_v0` |
| DE-2 | Backend **DayContext assembler**; single injection point before LLM in `today_narrative` (and same pack for downstream surfaces) | DONE | `build_today_narrative` вызывает `build_day_context_v0` до LLM; guide user JSON из `layers`; `generation_logs.input_payload`: `day_context_sha256`, `day_context_contract_version` |
| DE-3 | Surface **`generation_id`** (+ context version) wherever users give step/outcome feedback | DONE | Web: state для guide/day_layer/spheres/evening; `generation_id` в meaning payload; `POST /learning/feedback` при day_connection (ритуал/вопрос/решение) и вечере; iOS: `generationLogId` в `trackTodaySurfaceEvent` + feedback после `saveEveningReflection` |
| DE-4 | **Feedback loop** on ritual steps: picked / 20m focus / evening ↔ tracking events + learning | DONE | `VALID_EVENT_TYPES` + `RING_EVENT_WEIGHTS` для канонических типов; веб/iOS шлют `sphere_opened`, `tarot_selected`, `mood_selected`, `focus_started`, `evening_reflection_submitted` и др.; `tests/test_meaning_events.py` |
| DE-5 | **Pattern aggregates** from events into learning / profile-facing summaries | DONE | `build_meaning_surface_patterns_v0` → `DayContext.layers.behavior_patterns`, `learning_context.meaning_surface_patterns`, промпты narrative; `stats.meaning_events_28d`; pytest `test_meaning_surface_patterns.py` |
| DE-6 | **Intent**: wire `morning_intention`, head topic, and “what matters” into priority in prompts and UI | DONE | `intent_slice_v0` (`build_intent_layer_v0`) → `DayContext.layers.intent`; `DayConnection` + `head_topic` из `ritual_context` в `build_today_narrative`; промпт `today-narrative-v9` + `intent` в user JSON (guide…deepen); кэш: `intent_context_fp`; API: `RitualContextRequest.head_topic`, `ritual_context` на всех surface; web: `lastRitualNarrativeContextRef` + `head_topic` в ритуале; iOS: `TodayNarrativeRitualContextPayload.head_topic`, last-context для child surfaces; схема `ritual_layer.head_topic`; pytest `test_intent_slice_v0`, `test_day_context_v0` |
| DE-7 | **Flow completion** signals into fusion / DayContext | DONE | v0–v2: флаги `DayConnection` + `guide_action_options_selected_today` + **`guide_meaning_completions_today`** в `GET /tracking/fusion` → DayContext; slim fusion с клампом 0–50; различие с `day_completed` в [DAY_CONTEXT_V0.md](./DAY_CONTEXT_V0.md). **v3 (UI):** под «Главный шаг» на вебе и iOS — eyebrow «Сегодня в Flow», чипы по ненулевым типам и текст пустого состояния, если объект счётчиков есть, но суммы нулевые (`TodayResultView`, `GuideMeaningCompletionsFocusStrip`). Backlog: жёсткая связка текста вариантов шага с событиями. |
| DE-8 | **`depth_level`** quick / normal / deep — contract, settings, prompt branches | DONE | **v0–v2:** как ранее (narrative contract, `user_settings`, тарифный кламп `deep`). **v3 (2026-05-04):** выбор на Today (веб/iOS) + частичный PUT. **v4 (2026-05-04):** meaning-событие `today_narrative_depth_changed` → `/meaning/events` (web `trackMeaningEvent`, iOS `trackTodaySurfaceEvent`), `VALID_EVENT_TYPES` + вес Mind в `RING_EVENT_WEIGHTS`; см. [TODAY_PERSONALIZATION_CORE.md](./TODAY_PERSONALIZATION_CORE.md). |
| DE-9 | **Temporal context** (yesterday, 7-day trend) inside DayContext | **DONE** | **v0–v1.4:** как ранее (fusion scores, UI strip, week summary, meaning signals, `day_model.temporal`). **v1.5 (2026-07-03):** `reflection_excerpt` из `DayConnection` (вечер/дневник/утро, caps); UI-строка `formatFusionDayHistoryReflectionLine*` (web+iOS); промпт-гайды. Эпик закрыт — temporal slice в DayContext, fusion API, UI и LLM. |
| DE-10 | **Health** (sleep, activity) with consent — HealthKit first, Android later | BACKLOG | Privacy review |
| DE-11 | **Journal excerpts** in DayContext under explicit policy (extends diary slice beyond counts) | BACKLOG | With user consent + caps |
| DE-12 | **Visible vs internal profile slices** for prompts (no new tables v0) | DONE | `profile_prompt_slices_v0` → `DayContext.layers.visible_profile` / `internal_profile`; схема `day_context_v0`; `_attach_profile_slices` во все user JSON narrative; системные параграфы RU/EN + `PROMPT_VER` v9; pytest `test_profile_prompt_slices_v0` |
| DE-13 | **Narrative multi-call pipeline** (узкие шаги вместо одного guide на всё) | **DONE** | **v0–v4:** funnel interpretation → core → satellites; per-step cache; child chain; step3 core. **v5 (2026-07-03):** `guide_contract_v2` + `guide_pipeline_v0` в HTTP guide; `guide_funnel_core_source`; preserve LLM core vs `guide_decision`; web/iOS/Android parsers. **v6 (2026-07-20):** quality-first `LLM_QUALITY_MODE=rich` + Nebius/DeepSeek-V4-Pro; child surfaces 2-step funnels; **profile 4-step** portrait funnel (`profile-contract-v3`) + strict/quality gates + forming fallback + lock/cache DoD tests. Canon: [LLM_QUALITY_AND_PROMPT_EVOLUTION.md](./LLM_QUALITY_AND_PROMPT_EVOLUTION.md). **Open:** manual QA 20–30 live profiles. Монолит только fallback. |
| **GE-1** | **Generation Orchestrator** — единый управляющий слой генераций; мета-воронка в логах; связка с [PERSONAL_INTELLIGENCE_LAYER.md](pim/PERSONAL_INTELLIGENCE_LAYER.md) §10.1 / §11 | IN_PROGRESS | **v0.1:** `orchestration` в `generation_logs`. **v0.2 (2026-05-04):** `orchestration.reasoning_trace` (полный `selector_debug` + `selector_resolution` + урезанные `generation_rules`); `POST /today/narrative` → **`run_today_narrative_pipeline`** (`api/today.py`). **v0.3 (2026-07-03):** `ORCHESTRATOR_VERSION` 0.4.0; `reasoning_trace.day_model` (vector/tension/risk/gate); `narrative_outcome` после генерации (funnel/monolith, child chain); guide `merge_pass_steps` ↔ DE-13 funnel + `guide_contract_v2`. **Дальше:** Guidance/Compatibility через тот же фасад; payload между шагами funnel в orchestration; смысловой quality gate. |
| **PS-1** | **Profile Selector v1** — topic life-area excerpts · day_history signals · eval harness | **DONE** | `profile-selector-v1` · `topic_sphere_excerpt` · `selector_eval.py` · DayContext wiring |
| **PM-1** | **Profile vs Personal Map** — убрать дублирование IA и копирайта: натал как **source layer** без Today и без повторяющегося портрета; Profile = портрет + сферы; CTA по смыслу блока; сферы ≠ копия домов | **DONE** | Quick Map dedup · sphere frames (`profileSphereCopy`) · `/profile?view=v0` · life sphere/house audit · iOS builder parity · Portal-only «Карта личности» |
| **DS-2** | **Foundation HeroLarge** — единый hero §1.1 (`88dvh`, symbol 120px, geometry, fade); web `HeroLarge.tsx` + iOS `HeroLargeView` | **DONE** | Quick Map · Editorial · FirstDayTeaser (web+iOS); test `HeroLarge.test.tsx`. |
| **DS-3** | **Profile orbit-card purge** — production `/profile` на Foundation surfaces | **DONE** | `SurfaceInsight` + `ProfileSurface` · route chrome · setup · legacy sections (Synthesis, Pulse, Overview, Circle, …) — **0× `orbit-card` в `components/profile/`** |
| **DS-4** | **Profile motion kit** — CSS-only reveal/stagger/expand; `prefers-reduced-motion` | **DONE** | `--tf-motion-*` tokens · `ProfileMotion.tsx` · HeroLarge · expandable/portal · Quick Map stagger · iOS `ProfileMotion.swift` |
| **DS-1 lite** | **Archetype SVG assets** — `public/images/icons/archetypes/` + `VISUAL_ASSET_MODE=asset` | **DONE** | 12 named + unknown · mask tint · iOS `ArchetypeSymbolView.swift` · `ARCHETYPE_SLUGS` |
| **PM-QA** | **Profile Foundation QA** — Quick Map vs Foundation §9 + shape audit hook | **DONE** | [PROFILE_FOUNDATION_QA.md](./status/PROFILE_FOUNDATION_QA.md) · `NEXT_PUBLIC_PROFILE_SHAPE_AUDIT` · tests pass |
| **DS-FIGMA** | **Foundation Figma file** — `TODAYFLOW_FOUNDATION_UI` (Cover + §8 pages) | **IN DESIGN** | [Cover v1](https://www.figma.com/design/pWdevqQqOi6wvoVc6hFWHa) · living portal composition · **не sign-off** |
| **DS-12** | **Archetype expansion** — 8→12 seeds (seeker · mentor · guardian · visionary · catalyst) | **DONE** | registry aliases (evolution levels) · inline + SVG · iOS paths |
| **DS-5** | **Foundation HeroMedium** — §1.2 Today theme hero (52dvh, 80px symbol) | **DONE** | `HeroMedium.tsx` · Today day-anchor · `todayHeroMedium` · iOS `HeroMediumView.swift` |
| **DS-6** | **Foundation HeroSmall** — §1.3 Compatibility section header (200px, 48px symbol) | **DONE** | `HeroSmall.tsx` · hub · exploration · dynamics · `CompatibilityOrbitSymbol` · iOS `HeroSmallView.swift` |
| **DS-7** | **Planet SVG assets** — 10× `public/images/icons/planets/` + `PlanetIcon` | **DONE** | mask tint · Profile chart table · `InlinePlanetIcons` · iOS `PlanetSymbolView.swift` |
| **DS-8** | **Geometry System** — G1–G5 primitives + Profile / Today / Portal compositions | **DONE** | `FoundationGeometryLayers` · `SacredGeometryBackdrop` preset/tone · portal deep section · iOS `FoundationGeometryView.swift` |
| **DS-9** | **Zodiac SVG assets** — 12× `public/images/icons/zodiac/` + mask tint `ZodiacIcon` | **DONE** | Today pillars · Compatibility orbit · Profile V0 · iOS `ZodiacSymbolView.swift` |
| **DS-10** | **Typography bridge** — `--orbit-text-*` → `--tf-type-*` aliases · `profileV0` tokens | **DONE** | `globals.css` legacy aliases · `profileV0.module.css` on Foundation §5/§6 |
| **DS-11** | **Element SVG assets** — 4× `public/images/icons/elements/` + `ElementIcon` | **DONE** | mask tint · `ElementAtmosphere` pattern tile · iOS `ElementSymbolView.swift` |
| **MP-1** | **Maps canon + Profile IA** — вторая половина продукта: split «Кто я» / «Как меняется жизнь»; §4.10 Product Model · §7 Profile Master · §3.3 PIL | **DONE** | Living Maps band · heatmap/habit weave preview · explore card grid + hub · local cross-map observation (web+iOS) |
| **MP-2** | **Map language migration** — tracker/statistics → карта/история (§5.8); routes/copy web + iOS | DONE | Hub «Мои карты» · heatmap без % · weekly integration story · habits/ascetic/calendar/help/rings · iOS chrome parity · **исключения:** legacy URL `/affirmations/tracker`, `/asceticisms/tracker`; internal `day_trackers` / `planet_tracker` catalog |
| **MP-3** | **Map entities P0** — Mood · Energy · Habit · Promise: heatmap + day drill-down + story copy | DONE | **Web v0** · **iOS v0:** local stores · 4 map screens · Profile preview · mood sync · fusion persist · evening continuity writer · `/maps/*` deep links · Maps hub · batch fusion history |
| **MP-4** | **Map entities P1** — Ascetic journey · Wish · Relationship network · Tarot arc | **DONE** | web `/maps/{ascetic,wish,relationship,tarot}` + share line v0; iOS P1 views + deep links; relationship writer on compat result |
| **MP-5** | **Cycle as context** — Today recommendations only; cycle patterns in Maps observations, never hero | DONE | `cycleMapModel` + Profile Living Maps (web/iOS) · без «день N» · cross-map after 4+ cycles |

**Порядок работ (зафиксировано, см. PIL):** 1) Profile Engine → 2) Profile Selector (расширение + eval) **PS-1 DONE** → 3) Today DayModel + цепочка → 4) Today UI только как проекция → 5) Guidance → 6) Compatibility → 7) Flow. **Maps (MP-*)** — параллельно после MP-1, не блокируя Today spine. Параллельно GE-1 разворачивает **операционный контур** (§10 PIL).

---

## 5) Implementation Roadmap

## Phase 0: Reference Layer (P0 catalog)

**Фаза канона:** [ONTOLOGY_AND_FOUNDATION_PHASES.md](./ONTOLOGY_AND_FOUNDATION_PHASES.md) **Фаза 1** (Canonical Knowledge) + начало **Фазы 2** (DayModel rules). Не путать с PIL output surfaces (фазы 3–5).

Status: `IN_PROGRESS`

Canon: [REFERENCE_LAYER_AND_BUILD_ORDER.md](./REFERENCE_LAYER_AND_BUILD_ORDER.md).

### Tasks
- [x] Fix Reference Layer canon doc + domain catalog table §6.
- [x] DayModel Input Contract + Dependency Map ([DAYMODEL_INPUT_CONTRACT.md](./DAYMODEL_INPUT_CONTRACT.md)).
- [x] Reference Machine Contract JSON Schema v1 + CI ([REFERENCE_MACHINE_CONTRACT_V1.md](./schemas/REFERENCE_MACHINE_CONTRACT_V1.md)).
- [x] P0.3 — editorial draft scores (22 major arcana), each file passes validator (`DATA/reference/tarot/machine/`).
- [x] P0.4 — DayModel v1 aggregation test (loader + tarot-only preview aggregator + pytest).
- [x] Reference system taxonomy + C/D/Co/R classification ([REFERENCE_LAYER_AND_BUILD_ORDER.md](./REFERENCE_LAYER_AND_BUILD_ORDER.md)).
- [x] Data ownership & consumption map ([DATA_OWNERSHIP_AND_CONSUMPTION_MAP.md](./DATA_OWNERSHIP_AND_CONSUMPTION_MAP.md)).
- [x] Ontology & foundation phases canon ([ONTOLOGY_AND_FOUNDATION_PHASES.md](./ONTOLOGY_AND_FOUNDATION_PHASES.md)).
- [x] Data origination & lifecycle canon ([DATA_ORIGINATION_AND_LIFECYCLE.md](./DATA_ORIGINATION_AND_LIFECYCLE.md)).
- [x] Personal Intelligence Layer canon v2 — сквозной learning-aware слой ([PERSONAL_INTELLIGENCE_LAYER.md](pim/PERSONAL_INTELLIGENCE_LAYER.md)).
- [x] User Evolution Model ([USER_MODEL_TARGET_STATE.md](pim/USER_MODEL_TARGET_STATE.md)).
- [x] Gamification & Progress System ([USER_MODEL_TARGET_STATE.md](pim/USER_MODEL_TARGET_STATE.md)).
- [x] Symbolic Asset & Commerce Layer ([REFERENCE_LAYER_AND_BUILD_ORDER.md](./REFERENCE_LAYER_AND_BUILD_ORDER.md)).
- [x] User Model Target State / north star ([USER_MODEL_TARGET_STATE.md](pim/USER_MODEL_TARGET_STATE.md)).
- [x] Interpretation Layer & Reference canon ([INTERPRETATION_LAYER_AND_REFERENCE.md](explainability/INTERPRETATION_LAYER_AND_REFERENCE.md)).
- [x] Knowledge Acquisition & Signal Policy ([KNOWLEDGE_ACQUISITION_AND_SIGNAL_POLICY.md](./KNOWLEDGE_ACQUISITION_AND_SIGNAL_POLICY.md)).
- [x] User Knowledge Model canon ([USER_KNOWLEDGE_MODEL.md](pim/USER_KNOWLEDGE_MODEL.md)).
- [x] API Memory & Learning Layer canon ([API_MEMORY_AND_LEARNING_LAYER.md](./API_MEMORY_AND_LEARNING_LAYER.md)).
- [x] P0.5 — Numerology machine drafts (`DATA/reference/numerology/machine/`, loader, validator, numerology-only preview).
- [x] P0.7 — Astrology Machine Contract canon ([ASTROLOGY_MACHINE_CONTRACT.md](./ASTROLOGY_MACHINE_CONTRACT.md)).
- [x] Astrology Composition Model gate ([ASTROLOGY_COMPOSITION_MODEL.md](./ASTROLOGY_COMPOSITION_MODEL.md)).
- [x] P0.8 — Astrology atomic machine drafts (39: 12 signs, 10 planets, 12 houses, 5 aspects; loader + validator).
- [x] P0.9 — Cross-domain machine validation — PASS → P1.0 unlocked.
- [x] **P1.0** — DayModel v1 multi-source aggregation (`aggregate_day_model_v1`, 15 tests).
- [x] **P1.1** — DayModel Interpretation Rules (`interpret_day_model_v1`, 12 tests).
- [x] **P1.2** — DayModel Content Mapping (`map_day_model_interpretation_to_content_keys`, 13 tests).
- [x] **P1.3** — Content Contract Seed Texts (37 keys, validator, resolver, 13 tests).
- [x] **P1.4** — Deterministic Day Content Assembly (`assemble_day_content_package_v1`, 10 tests).
- [x] **P1.5** — DayModel Package Evaluation (`evaluate_day_content_package_v1`, 10 tests).
- [x] **P1.6** — Deterministic Renderer Contract (`render_day_content_package_v1`, 10 tests).
- [x] **P1.7** — LLM Call Gate for DayModel Content (`decide_day_content_llm_call_v1`, 10 tests).
- [x] **P1.8** — LLM Request Record Contract (pre/post-call builders, 10 tests).
- [x] **P1.9** — Prompt Context Slice Contract (`build_llm_context_slice_v1`, 10 tests).
- [x] **P1.10** — Prompt Template Contract (`build_day_llm_prompt_v1`, 10 tests).
- [x] **P1.11** — LLM Response Contract & Validator (`validate_day_llm_refinement_response_v1`, 12 tests).
- [x] **P1.12** — LLM Response Evaluation & Post-call Integration (`evaluate_day_llm_response_v1`, 10 tests).
- [x] **P1.13** — Final Surface Candidate Selection (`select_day_surface_candidate_v1`, 10 tests).
- [x] **P1.14** — Surface Candidate Audit Record (`build_day_surface_candidate_audit_v1`).
- [x] **P1.15** — User Exposure & Reaction Contract (`build_day_surface_exposure_v1`, `build_day_surface_reaction_v1`, 10 tests).
- [x] **P1.16** — Reaction → Learning Signal Mapping (`build_day_surface_learning_signal_v1`, 12 tests).
- [x] **P1.17** — Pattern Candidate Aggregation (`try_aggregate_pattern_candidate_v1`, 10 tests); [USER_KNOWLEDGE_MODEL.md](pim/USER_KNOWLEDGE_MODEL.md).
- [x] **P1.18** — Pattern Confirmation Gate (`try_confirm_pattern_from_candidate_v1`, 11 tests).
- [x] **P1.19** — Knowledge Candidate (`try_build_knowledge_candidate_from_pattern_v1`, 10 tests).
- [x] **P1.20** — Active Knowledge Confirmation Gate (`try_activate_knowledge_from_candidate_v1`, 12 tests).
- [x] **P1.21** — Active Knowledge Usage Policy (`try_build_active_knowledge_usage_policy_v1`, 12 tests).
- [x] **P1.22** — Active Knowledge Runtime Gate (`try_decide_active_knowledge_runtime_v1`, 11 tests).
- [x] **P1.23** — Active Knowledge Hint Package (`try_build_active_knowledge_hint_package_v1`, 11 tests).
- [x] **P1.24** — Hint Package Application Contract (`try_apply_hint_package_v1`, 11 tests).
- [x] **P1.25** — Hint Application Dataset Policy (`try_build_hint_application_dataset_policy_v1`, 10 tests).
- [x] **P1.26** — Dataset Candidate Promotion Gate (`try_promote_dataset_candidate_v1`, 10 tests).
- [x] **P1.27** — Training Dataset Registry (`try_register_training_example_v1`, 14 tests). **→ STOP:** [API_MEMORY_AND_LEARNING_LAYER.md](./API_MEMORY_AND_LEARNING_LAYER.md)
- [ ] ~~P1.28+ Learning pipeline (Export Gate, training batch, …)~~ — **DEFERRED** until users + own-model roadmap.
- [x] **Branch A** — Knowledge Usage Layer → **architecture closed** (A1.1–A1.8); ops: promotion→DB, log criteria — [status/branch_a_knowledge_usage_layer.md](./status/branch_a_knowledge_usage_layer.md).
- [x] **Branch B** — Evolution Engine → **B1.0–B1.14** ✅ — [status/branch_b_evolution_engine.md](./status/branch_b_evolution_engine.md).
- [x] **Branch C** — Practice System → **C1.0–C1.6** ✅ CD · **C2.0–C2.4** ✅ runtime stack — [status/branch_c_practice_system.md](./status/branch_c_practice_system.md).
- [x] **Branch D** — Symbolic Asset System → **D1.0–D1.5** ✅ — [status/branch_d_symbolic_assets.md](./status/branch_d_symbolic_assets.md). Symbolic foundation complete; Commerce Runtime deferred.
- [x] **Branch E** — Calendar Intelligence → **E1.0–E1.7** ✅ — [status/branch_e_calendar_intelligence.md](./status/branch_e_calendar_intelligence.md).
- [x] **Reference Intelligence Layer** — C1.7 ✅ · C1.8 ✅ · **Next:** FIRST_DAY_DOD_GAP_ANALYSIS.
- [ ] **Surface Layer** — **System map** ✅ · **Reference inventory** ✅ · **S1.1** ✅. **⏸ Today wire-plan paused** until RIL P0 edges (causal map §12).
- [ ] Compact User Model (CUM) implementation.
- [ ] Evolution Calculation Contract → UEM-2 (`evolution_stage` in API only after ECC active + P1.1).
- [ ] Tarot: full 78 cards + Machine Contract scales for DayModel.
- [ ] Numerology: content layer for core numbers + personal day/month/year.
- [ ] Emotional State + Today-critical UI Copy rows → `active`.
- [ ] Reference read API v1 + `reference_version` in generation logs.

**Freeze until Phase 0 P0 rows active:** Today UI redesign, new prompts, DE-13 pipeline split.

---

## Phase 1: Core Architecture Foundation
Status: `IN_PROGRESS`

### Tasks
- [x] Define `Core Profile` schema (backend + frontend DTO).
- [x] Build shared endpoint/service for core profile context.
- [x] Add orchestrator rules for interpretation consistency.
- [x] Refactor key personalized endpoints to consume core context.
- [x] Add integration tests for consistency between modules.
- [x] Split stable profile interpretation from daily interpretation at service contract level.
- [x] Add multi-profile contract to core profile domain.

### Done in this phase
- [x] Product-level architecture and scope documented in this tracker.
- [x] Implemented backend `CoreProfileService` with stable response envelope and `profile_hash`.
- [x] Added `GET /account/core-profile` endpoint for authenticated users.
- [x] Added frontend `CoreProfile` DTO and connected `/today` to consume it.
- [x] Implemented baseline `Interpretation Orchestrator` and wired it into `day-flow`.
- [x] Refactored `today`, `morning-ritual`, and `numerology/daily/explain` to expose `core_profile` + `consistency`.
- [x] Added integration tests for core profile consistency flow (auth + seeded context).
- [x] Added learning layer foundation: prompt versions, generation logs, feedback API, and generator-side best-effort logging.
- [x] Split `core_profile` contract into stable `interpretation` and separate `daily_interpretation`, with snapshot migration for older cached payloads.
- [x] Added explicit multi-profile contract to `core_profile`: `astro.relation`, `profiles.primary/selected/items`, and relation-aware account profile payloads.

---

## Phase 2: IA + Today As Daily Magnet
Status: `IN_PROGRESS`

### Tasks
- [x] Stabilize legacy top-level IA before JTBD pivot.
- [ ] Make `Today` the operational daily center as one surface with light time-of-day framing and reminders.
- [x] Ensure fast loading and remove route flicker across critical pages.
- [x] Remove/redirect duplicate or legacy entry routes.
- [x] Add clear CTA flow for 2-3 daily returns.
- [ ] Make `/profile` the canonical “my map / my face / my orientation” screen.
- [ ] Reduce `/today` default payload to daily-guide essentials only; secondary analytics stay behind reveal.
- [ ] Ensure daily answers and micro-interactions persist across refresh and repeated returns.
- [ ] Make progress tracking and weekly-goal entry visible and natural inside `/today`, including soft empty-state guidance when no goal exists.

### Done in this phase
- [x] `Today` and morning ritual direction aligned conceptually.
- [x] Dedicated weekly dashboard route made accessible via interface (previous request).
- [x] Header IA normalized for the pre-JTBD product model and clear hub aliases.
- [x] Local routing stability improved (SW disabled on localhost + legacy `/app` flow normalized).
- [x] Added explicit return cadence block on `/today` for 2-3 daily sessions.
- [x] Today cleanup pass completed (legacy blocks/anchor flows removed or replaced with slot navigation).
- [x] Today visual polish pass completed (single visual language for stage panels and summary rail).
- [x] `/profile` turned into a single mobile-first entry flow: core setup -> build -> ready profile.
- [x] `/onboarding/core` now redirects into `/profile?setup=core` instead of duplicating a second build flow.
- [x] Ready-state profile is now stacked and expandable for mobile instead of exposing all sections at once.
- [x] `/today` first screen reduced to daily guide essentials: day message, card-of-day entry, next action, progress.
- [x] Secondary analytics remain below and/or behind explicit reveal instead of occupying the first mobile viewport.
- [x] `Today` core-profile CTA now points to `/profile?setup=core`, matching the new single-entry profile flow.
- [x] `Утро / День / Вечер` in `Today` no longer behave as separate gated products; they now work only as optional timing modes inside one daily surface.
- [x] Time-of-day states in `Today` now share one visual system: common headers, common content cards, and soft empty states instead of mixed panel styles.
- [x] Forecast text prompts upgraded to API-first v2: shorter editorial prompts, less mystic-template language, stronger human-readable fallback text.
- [x] Tarot and numerology explanation prompts upgraded to API-first v2: more personal, less dictionary-like, no dead spiritual cliches.
- [x] Core profile now includes API-generated interpretation blocks: identity, strengths, watchouts, and four life areas for Profile surface.
- [x] Profile life areas now route directly into system services: love -> compatibility, career -> horoscopes, money -> forecasts, family -> additional profiles.
- [x] Today now exposes direct guided routes to card of the day, compatibility, profile, and deeper helper layers without forcing users into menu discovery.
- [x] Header and auth nav now point to canonical live routes instead of legacy aliases, with reduced duplication in mobile and profile menus.
- [x] Legacy dashboard reduced to alias behavior: `/dashboard` now redirects to `/today`, and key return CTAs no longer send users into the old dashboard hub.
- [x] Sign-to-sign compatibility flow rebuilt into the same guided system: clean pair selection, concise result, personal next step, and heavy text moved behind a secondary reveal.
- [x] Birthdate compatibility flow rebuilt into the same guided system: clearer pair setup, RU/EN city input, lighter result structure, and a clean bridge into deep profile-based compatibility.
- [x] Dead legacy dashboard archive removed from the frontend codebase: unused old page, old dashboard CSS, and unused dashboard component set deleted so the new IA no longer competes with hidden legacy code.
- [x] Profile interpretation prompt and fallback upgraded to a more human “life map” tone, and `Today` / `Profile` frontend text shaping was rewritten to remove templated phrasing and make actions/readouts clearer.
- [x] Server-side daily guidance upgraded: `day meaning` prompt tightened, morning recommendation generation rewritten in a clearer human tone, and morning forecast summary now returns more readable, action-oriented daily language.
- [x] Forecast generation pipeline tightened further: the daily AI forecast now preserves the main theme as a top insight, weekly AI generation now uses actual user context, and weekly fallback copy was rewritten to be more supportive and usable.
- [x] `Today` now persists lightweight daily answers across refresh (`ritual feedback`, `mini-decision`, `question of the day`) and exposes a visible progress tracker instead of hiding day progress in a minor card.
- [x] `/today` now includes a soft weekly-goal empty state: suggested goals, inline goal creation, and a clear bridge into the weekly focus screen when the user has no active goal.

---

## Phase 3: Forecast + Tarot + Compatibility Productization
Status: `COMPLETED`

### Tasks
- [x] Build single Forecast surface with filters (life domains).
- [x] Implement static compatibility content matrix (free/paid depth).
- [x] Implement personalized compatibility overlay from birth profile.
- [x] Ensure tarot thematic spreads reuse shared interpretation context.
- [x] Add consistency checks between Today/Forecast/Tarot outputs.
- [ ] Reframe these modules in UI as separate services around the user profile, not competing roots.

---

## Phase 4: Growth + Rewards Domain
Status: `COMPLETED`

### Tasks
- [x] Implement streak model (day/week milestones).
- [x] Implement archetype progression model.
- [x] Implement natal-linked seals/energetic rewards.
- [x] Implement weekly `Personal Evolution Index`.
- [x] Integrate rewards feedback into Today/Profile/Practice completion.

---

## Phase 5: Design System Hardening
Status: `IN_PROGRESS`

### Form Kit (2026-08-14) — closed visual SoT
- **Canon:** `TODAYFLOW_FOUNDATION_UI.md` §15.8 — Surface≠Card; compositions; visual import contract; formal DoD; form≠kit colors.
- **Hard rules:** `DsWaveMeter` = semantic value viz; `DsChip` `statusTone` = `--tf-semantic-*` only (no `--day-*`); `DsSectionHeader` = composition only.
- **Code:** `frontend/src/design-system/` primitives + `compositions/` + `visual/` wrappers; catalog `/design-system` = **100% sheet roles specimen**; gate declarative skin bans.
- **Production:** Today day brief wires only roles with real model data; UI imports from `design-system/**` (+ domain data/types). Next stage = zone migration only (Practices…).
- **Zone sequence (absolute no local skin after each):** Today → Profile → Practices → Compatibility → Natal → rest. Allowlist: `scripts/ds_form_kit_zone_allowlist.json`.

### Tasks
- [x] Lock color tokens, typography scale, spacing grid.
- [x] Standardize button/card/input variants.
- [x] Unify icon style and tarot cover style.
- [x] **Form Kit closed set** — §15.8 primitives + compositions + visual contract + gate + **full-sheet catalog specimen** + day-brief data-backed wiring.
- [ ] **Form Kit zones** — Today → Profile → Practices → Compatibility → Natal → rest (zero local skin per closed zone). Allowlist: `scripts/ds_form_kit_zone_allowlist.json`.
  - **Today zone CLOSED** · **Profile zone CLOSED** (2026-08-14): local `*.module.css` moved under `design-system/**`. Next: Practices (5 modules).
  - Today/Profile inventory closed via DS compositions/patterns/layouts/profile skins.
- [x] **Task 2.7 Wave 1** — Shell/layout unification (`--tf-shell-max` / readable; kill phone columns). Practices/Profile/Compatibility + Tarot hub. Exit: `layout DoD ✅`, zones still IN PROGRESS.
- [x] **Task 2.6 Wave 2** — Expand DS gate for `rgba()` / `color-mix()`; rewrite Compatibility local rgba cards to `--tf-*`/`--day-*`.
- [x] **Task 2.6b Wave 2** — Typography on same three zones + Tarot hub → Foundation `--tf-type-*` roles.
- [x] **Task 2.9 foundation (PR1)** — Semantic meaning layers: rewrite §5 ladder (48–60/34/24/18/16/14/12) · 5 ink colors · `DsCallout` (tone × label) · `DsQuote` · `DsCapsule` · linear icons · `/design-system` specimen · pilot `TodayDayLogicCallout`. **Exit: foundation only — zones stay open.**
- [x] **Task 2.9b Today Reading** — dual opportunity/trap · soft-why · move if/then · vibe → `DsCallout`/`DsQuote` (`TodayPersonalizedProductSection`). Zone still needs full 6-axis DoD + screenshots.
- [x] **Task 2.9b Tarot result** — answer / next_step / A·B / confidence / why → `DsCallout`/`DsQuote` (`TarotWebResult`). Zone still needs full 6-axis DoD + screenshots.
- [ ] **Task 2.9b Compatibility result** — exploration main/duals/tips/deep · funnel confidence/today/risk · analyze·signs personalized → `DsCallout`/`DsQuote`. Zone still needs full 6-axis DoD + screenshots.
- [ ] **Task 2.9b+ remaining zones** — Profile editorial · Practices session; each under 6-axis DoD.
- [ ] **Screenshot parity** — owner side-by-side review closes Practices/Profile/Compatibility (6-axis DoD).
- [ ] **Task 3.5** — Day Atmosphere mode picker on `/design-system` (after Onboarding; non-blocking).
- [ ] Audit all key screens for visual/system consistency (screenshot parity = zone close).
- [ ] Mobile + desktop QA pass for primary flows.
- [ ] Normalize Profile and Today into the canonical 2-surface mental model.

---

## Phase 6: JTBD + Question-First Productization
Status: `PLANNED`

### Outcome
- TodayFlow becomes a JTBD-first system instead of a module-first collection.
- The user arrives with a real-life question in mind, and the product answers it through the correct screen structure, CTA, and next route.
- The 4 core JTBD become explicit product lanes, not implicit backend capabilities.

### Tasks
- [x] **Daily Navigation Model** — ICA kernel, Profile→Context→Guidance→Action, daily 4 ([DAILY_NAVIGATION_MODEL.md](./DAILY_NAVIGATION_MODEL.md)).
- [x] **Market attention + screen jobs** — L1–L5 tiers, 5 Today domains, retention loop ([MARKET_ATTENTION_AND_SCREEN_JOBS.md](./MARKET_ATTENTION_AND_SCREEN_JOBS.md)).
- [x] **Need Registry v1** — 28 base needs, surface defaults, inference sources ([INTENT_MODEL_V1.md](./INTENT_MODEL_V1.md)).
- [x] **Intent Registry v1** — intent catalog + need mapping + envelope map ([INTENT_REGISTRY_V1.md](./INTENT_REGISTRY_V1.md)).
- [x] **Answer Contract v1** — need-indexed mandatory answer elements + Assembler role ([SCREEN_CONTRACTS_V1.md](./SCREEN_CONTRACTS_V1.md)).
- [x] **Screen Contracts v1** — mandatory user output per screen ([SCREEN_CONTRACTS_V1.md](./SCREEN_CONTRACTS_V1.md)).
- [x] Screen Contracts gap analysis — [status/TODAY_CANON_VS_CODE_DIFF.md](./status/TODAY_CANON_VS_CODE_DIFF.md).
- [x] **P0.1 (sprint):** iOS read `GET /today/contract` — **DONE (2026-07-05):** `TodayCompositionSurfaceView` default in `TodayView` (foundation from `day_story` + ritual via `TodayRitualFlowView`).
- [ ] **P0.2:** Compatibility `potential_tier` + `potential_conditions` — **UI hero = score ring + tagline** (2026-07); tier — metadata/learning layer.
- [ ] **P1:** Living Profile (`recurring_patterns`, `living_changes`; Calendar → Profile/Today).
- [ ] **P1:** Maps P0 (MP-2…MP-3) — Mood · Energy · Habit · Promise heatmaps + story language; см. [TODAYFLOW_PRODUCT_MODEL.md](archive/TODAYFLOW_PRODUCT_MODEL.md) §4.10.
- [ ] **Engine Projection Specs v1** — **after** P0.1 wire accepted.
- [ ] **Question Registry v1** — Hub / AI only (`explicit_question` → `need_id`).
- [ ] Define need inference contract (surface_open, block, lane, learning_context).
- [ ] Implement shared answer envelope per **need** (not generic lane templates only).
- [ ] Build `Decision OS` as a first-class lane.
- [ ] Repackage `Love OS` around direct relationship questions instead of only compatibility mechanics.
- [ ] Repackage `Money / Career OS` around income, role, and project-decision questions.
- [ ] Build `State OS` for energy, anxiety, and temporary difficult periods.
- [ ] Build `Pattern OS` for recurring scenarios and self-sabotage loops.
- [ ] Expose one best deeper route from each answer into tarot, compatibility, forecasts, or profile.
- [ ] Add learning signals for question intent, chosen route, and completion quality.

### Deliverables
- backend JTBD inference + answer assembler.
- JTBD prompt packs for `love`, `money_career`, `decision`, `state`, `pattern`, `daily`.
- UI structures and CTA patterns that answer latent user questions without requiring free-form input.
- analytics events for inferred JTBD, chosen route, and deeper route opened.

### Definition of Done
- A new user can arrive with a question in mind, not a tool choice.
- The system answers in a single coherent structure.
- The user does not need to understand internal modules to get value.
- The strongest monetization lanes are explicit in the entry flow: relationships, money, decisions.

---

## Phase 6.1: Expanded Product Completion Backlog
Status: `IN_PROGRESS`

This section converts the full current-state audit into one canonical working backlog.

### Critical Product
- [ ] Finalize `Today` as the primary daily engine on one surface, not as separate morning/day/evening products.
- [ ] Ensure `Today` continuously enriches the personalization layer, not only answers the current day.
- [ ] Finalize `Profile` as a true life map, not a form plus utility cards.
- [ ] Build the shared learning LLM layer (canon: [PERSONAL_INTELLIGENCE_LAYER.md](pim/PERSONAL_INTELLIGENCE_LAYER.md)) that turns answers, journals, questions, routes, and feedback into a more accurate psychotype and response model.
- [ ] Enforce one canonical journey for **web launch v1**: [WEB_LAUNCH_EXECUTION_PLAN.md](./status/WEB_LAUNCH_EXECUTION_PLAN.md) (story-first React). Legacy demo path — **reverse**; see Blueprint §Doc cleanup.
- [ ] Remove remaining legacy meanings, routes, and UI logic that contradict the current product canon.

### Web Launch v1 — **PROCESS FROZEN** (2026-07-01)

**Work plan:** [status/WEB_LAUNCH_EXECUTION_PLAN.md](./status/WEB_LAUNCH_EXECUTION_PLAN.md) — DoD · Launch Freeze · Decision Log · stories  
**UX spec:** [WEB_LAUNCH_PRODUCT_BLUEPRINT.md](./status/WEB_LAUNCH_PRODUCT_BLUEPRINT.md)

**Docs complete.** Дальше: story brief → React → story gate → walkthrough → 10 users → v2.

| Phase | Status |
|-------|--------|
| Product docs + **§4 content model** | 🟡 **ACTIVE** |
| React launch path | ⬜ after Today layers agreed |
| Story walkthrough | ⬜ |
| Launch DoD (11) | ⬜ |
| Field test 10 users | ⬜ |
| v2 planning | ⬜ after data |

### Onboarding & Guest (P0 — contract locked 2026-06-23; **web launch supersedes demo**)

Source of truth: [FIRST_DAY_EXPERIENCE.md](./FIRST_DAY_EXPERIENCE.md) §1–§13.

- [x] **P0.1** `/demo/today` — guest Today (Theme/Action/Progress, no auth, no LLM); fix landing CTA off `/today`.
- [x] **P0.2** `/onboarding/core` — core setup screen (not `/profile?setup=core`).
- [x] **P0.3** `/onboarding/intent` + `/onboarding/reality` — 1 chip each; persist + events.
- [x] **P0.4** Post-signup redirect → `/onboarding/core` when `!core_profile.is_ready`.
- [x] **P0.5** First Today `?first=1` — Theme-first, deterministic, Progress empty.
- [x] **P0.6** Profile as portrait **after** First Today (not first post-signup screen).
- [ ] Signup payload: `locale`, `signup_source`, `initial_referrer` (wire when analytics ready).
- [ ] iOS: same route parity (native onboarding, not Profile-as-setup).

### Profile and Core
- [ ] Connect daily signal collection, weekly state map, and monthly state map into one shared personalization model.
- [ ] Turn the personalization model into an evolving psychotype layer, not just a state log:
  - [ ] daily signals
  - [ ] diary entries
  - [ ] explicit user questions / JTBD entries
  - [ ] route choices
  - [ ] feedback on generated answers
  - [ ] learned response preferences and repeated tensions
- [ ] Finalize full core onboarding (see [FIRST_DAY_EXPERIENCE.md](./FIRST_DAY_EXPERIENCE.md) §4):
  - [x] dedicated `/onboarding/core` route (not Profile hub)
  - [ ] RU/EN name input; optional last name
  - [ ] birth date, optional birth time, city search
  - [ ] gender for RU grammar; locale
  - [ ] explanation of why the data matters (one screen, low friction)
- [x] Finalize stable core build flow:
  - [x] loading screen
  - [x] clear build status
  - [x] ready-state without UI jumps
- [x] Expand profile content:
  - [x] strengths
  - [x] weak spots
  - [x] what to strengthen
  - [x] what to avoid
  - [x] love
  - [x] family
  - [x] money
  - [x] career
  - [x] houses and house meaning
- [x] Finalize multi-profile management:
  - [x] primary profile
  - [x] spouse / partner
  - [x] child
  - [x] close people
- [x] Keep numerology inside the core, not as a competing separate service.

### Today
- [x] Reduce the first screen to:
  - [x] one main meaning of the day
  - [x] card of the day
  - [x] one next step
  - [x] one supporting block
  - [x] fast exits to deeper services
- [x] Remove overload from the middle and lower parts of `/today`.
- [x] Audit all Today CTAs:
  - [x] card of day
  - [x] day number
  - [x] forecast
  - [x] practices
  - [x] quick actions
- [x] Finalize daily texts so they:
  - [x] support
  - [x] warn
  - [x] help the user move through the day
  - [x] do not sound generic
- [x] Strengthen `Today <-> Profile` so the day always reads through the user's core.

### Forecasts
- [ ] Remove remaining canon drift around `Forecasts` and `Horoscopes` as separate roots.
- [ ] Keep any surviving forecast-like functionality only as a secondary helper layer around `Profile`, `Compatibility`, or decision support, not as a period-centered product.

### Compatibility
- [x] Review how the new backend compatibility text lands in the UI.
- [x] Strengthen compatibility result surface:
  - [x] core dynamic
  - [x] where it flows easily
  - [x] where conflict appears
  - [x] what helps
  - [x] how to act
- [x] Strengthen fast compatibility entry from:
  - [x] profile
  - [x] today
  - [x] people circle
- [x] Bring sign compatibility and birthdate compatibility to one meaning and text-quality standard.
- [x] **Compatibility Exploration v1 (web):** hub hero + 10 scenario cards (skins/hover FX); `CompatibilityExplorationResult` — ring %, 4 dimensions, narrative, deep journal, return loop; analyze + profile pair surfaces wired.
- [x] **Compatibility scenario tone (API):** `format_id` + `tone_mode` in encyclopedia selection; LLM system prompt + payload `scenario`; 4 playful series (`after_wine`, `home_renovation`, `best_friends`, `rule_breaker`).
- [x] **Compatibility playful format split (web + API + iOS):** `tone_mode=playful` → short stat-card surface; no encyclopedia intro prepend, no funnel; frontend `presentation=playful`.
- [x] **Compatibility scenario metrics (API):** `compatibility_scenario_metrics.py` — theme-scoped subscores + hero %; funnel filtered to 4 domains per `format_id`; per-domain ↑/↓ drivers.
- [x] **Compatibility pair profiles + scenario (web + API + iOS contract):** `POST /compare` + `/synastry` accept `format_id`; `scenario_context` in response; hub cards → `/compatibility?series=` for logged-in pairs; pair result uses theme-scoped metrics + continuation switch.
- [x] **Compatibility pair iOS (native):** hub series → pair compare with `format_id`; `CompatibilityExplorationResultView` for profile result; scenario score labels + carousel switch.
- [x] **Compatibility deep sections by scenario (web):** `compatibilityScenarioDeepSections.ts` — 4 journal blocks with skin labels (dynamics + pair), not generic 5-pack.
- [x] **Compatibility echo → hypothesis (PIM):** `compatibility_echo_knowledge_v0.py` — per-event echo/switch → inferred hypothesis; aggregate patterns in `meaning_derived_knowledge_v0` (3+ echoes / format interest).
- [x] **Compatibility ILR rules v0:** `interpretation_reference_v0` — echo yes/no/partial, conflicts+yes, scenario switch, deep open; secondary payload filter for compound triggers.
- [x] **ILR-2 reference catalog:** `DATA/reference/interpretation/interpretation_rule_registry_v1.json` + loader/validator; engine reads active rules from JSON.
- [x] **Compat-ref-1 scenario metrics:** `DATA/reference/compatibility/compatibility_scenario_metrics_registry_v1.json` — blends/hero/funnel domains; `compatibility_scenario_metrics.py` loads from registry.
- [x] **Import pilot (attachment):** `DATA/reference/psychology/attachment_style_registry_v1.json` (`active`) — 4 styles, deep_block_bias, source license; loader reads `active` only.
- [x] **Attachment → deep blocks:** `compatibility_attachment_reference_v0.py` — echo on communication/conflicts → block reorder + style hints; dynamics `attachment_reference`; pair `scenario_context.deep_block_order`; web pair UI order.
- [x] **Attachment lens confirm chip (web + iOS + BE):** `compatibility_attachment_knowledge_v0.py` — upsert `behavior_hypothesis:attachment_lens_*`; `compatibility_attachment_confirm` + `profile_atom_correction`; chip under hero on exploration result.
- [x] **ILR spawn → attachment lens:** `spawn_hypothesis_ids: ["attachment_lens:v0"]` on compat echo rules; `spawn_attachment_lens_from_ilr_v0` in ILR sync; rule `beh.compat_echo_communication_yes.v1`.
- [x] **Attachment registry review:** `attachment_style_registry_v1.json` — registry **`active`**, 4 styles `active`; engine reads `active` only.
- [x] **Profile CUM — confirmed attachment lens:** `relationship_insights_top_k` in CUM + `ProfileRelationshipInsightsBlock` (web/iOS).
- [x] **Android attachment lens chip:** dynamics result + `compatibility_attachment_confirm` events.
- [x] **Android compatibility ILR chip:** CUM fetch + `IlrInstanceChip` + `interpretation_instance_confirm`.
- [x] **Compatibility ILR instance chip:** `interpretation_instance_confirm` + `CompatibilityIlrInstanceChip` (web/iOS).
- [x] **Profile ILR instance confirm:** non-`beh.compat_*` instances in `ProfileInterpretationInstanceBlock` (web/iOS); event `interpretation_instance_confirm` / `event_source: profile`.
- [x] **ILR spawn `beh.compat_echo_yes.v1` → attachment lens:** `spawn_hypothesis_ids` on echo-yes rule.
- [x] **OpenAPI learning contracts:** `CompatibilityAttachmentReferenceV0`, `CompactUserModelInterpretationInstance`, meaning payload schemas + `GET /meaning/events/learning-payloads`; JSON Schema in `docs/schemas/`.

### Tarot
- [x] **Interpretation Engine v1.1** — Context Pack → LLM → validation → UI; ban «Аркан»; quality gates; honest fallback. Canon [TAROT_INTERPRETATION_ENGINE_V1](./tarot/TAROT_INTERPRETATION_ENGINE_V1.md). Ledger: `fb8cd34` · `c4bbe56` (+ CE scrub `f2ac8c2` · `8c7bd2e`).
- [x] **Interpretation Stack v1 — Architecture Frozen / Editorial Phase** — foundation accepted (KB · Position Semantics · Ontology · single LLM · reliability · live r3 12/12). Full freeze lift **declined**. Allowed: KB · prompt wording · editorial data · eval · timeout/reliability. New layers/contracts/pipeline/LLM stages → **RFC**. Canon [TAROT_INTERPRETATION_ENGINE_V1](./tarot/TAROT_INTERPRETATION_ENGINE_V1.md) · [owner note](./audits/TAROT_STACK_EDITORIAL_PHASE_2026-07-26.md).
- [x] **Tarot Knowledge Base v1** — [TAROT_KNOWLEDGE_BASE_V1](./tarot/TAROT_KNOWLEDGE_BASE_V1.md) · 78 cards in pack.
- [x] **Position Semantics v1** — [TAROT_POSITION_SEMANTICS_V1](./tarot/TAROT_POSITION_SEMANTICS_V1.md).
- [x] **Question Ontology v1** — [TAROT_QUESTION_ONTOLOGY_V1](./tarot/TAROT_QUESTION_ONTOLOGY_V1.md) · prompt v1.4+ · integration set 12.
- [x] **Q1 Editorial deepen minors** — each of 56 = unique psychological archetype (not rank×suit); Q1 profile in KB + pack; `adjacent_distinction` required.
- [x] **Golden Dataset** — fixed scenarios (question/profile/cards/expected type) without scores. Canon [TAROT_GOLDEN_DATASET_V1](./tarot/TAROT_GOLDEN_DATASET_V1.md).
- [x] **Golden Eval harness** — rubric 1–5 · paid-worth heuristic · anti-sameness · CLI. Canon [TAROT_GOLDEN_EVAL_V1](./tarot/TAROT_GOLDEN_EVAL_V1.md).
- [x] **Production reliability** — background timeout · no timeout→plain double-burn · live eval budgets · commit `da03d22` · deployed.
- [x] **Golden Eval live #3** — **12/12 LLM** · `freeze_lift_ready=true`. Audit [TAROT_GOLDEN_EVAL_LIVE_2026-07-26_r3](./audits/TAROT_GOLDEN_EVAL_LIVE_2026-07-26_r3.md).
- [x] **Owner editorial-phase accept** — full architecture lift declined; Editorial Phase allowlist active.
- [ ] **Human Golden Eval v2** — capture CLI + **13 cases** in fixture (1 scored owner + 12 live golden-dataset, unscored). Scorecard [TAROT_HUMAN_EVAL_V2_SCORECARD](./audits/TAROT_HUMAN_EVAL_V2_SCORECARD.md). Owner fills three questions → drive Q3. **← next (owner eyes)**
- [x] **Paid deepen chooser (UI)** — result «Углубить тему» unlocked for paid/trial; guest → signup, free → `/pricing`. Choices: money / intimacy&sex / work / boundaries → `/tarot?source=deepen`. No new engine hop. [Editorial Phase](./audits/TAROT_STACK_EDITORIAL_PHASE_2026-07-26.md).
- [ ] **Tarot UX feedback 2026-07-29** — auth race on guest gate · result load wait · hub/ritual copy · name field contrast · vy-tone soft · theme+question on refine. Partial landed in FE; deploy + live retest needed.
- [x] **Tarot ritual deck (mobile)** — replace fan with table-stack draw (`InteractiveCardDeck`: one tap / «Взять карту»). Usability fix toward Design Language «колода на столе».
- [ ] **Q3+ prompt polish** — wording only under Editorial Phase. `v1.9`: practitioner+friend persona (Voice Canon §1) + analytical voice (`v1.8` solemnity ban). Deploy needed for prod.
- [ ] **Fallback LLM provider** — deferred until owner purchases/connects.
- [ ] **Tarot Design Language v1** — [docs/tarot/TAROT_DESIGN_LANGUAGE_V1.md](./tarot/TAROT_DESIGN_LANGUAGE_V1.md) **DRAFT / PENDING ACCEPT** · **parked under architecture freeze**
  - Канон-объект: колода на столе; формации 1/3/5/2; один reveal-жест; рубашка = фирменный язык
  - До accept: не плодить новые ритуальные UI; после accept → один `TarotDeckExperience` везде
  - Figma formations + код — только после product accept §8
- [x] Audit the entire tarot flow:
  - [x] Tarot Hub
  - [x] One Card
  - [x] Three Cards
  - [x] Tarot Result
- [x] Make every spread read as:
  - [x] meaning
  - [x] manifestation
  - [x] caution
  - [x] next step
- [x] Verify card of the day works and feels like the central ritual of the day.
- [ ] **Tarot Question-First v1** (canon `SCREEN_CONTRACTS_V1` §6.4–§6.8):
  - [x] Canon + event dictionary
  - [x] Phase A web: Hero → concern → refine → spread → ritual (`TarotQuestionFlow`, `/tarot/spread/[spreadId]`)
  - [x] Phase B web: synthesis blocks + 3 today actions + self-question + resonance + next routes (`TarotSpreadReading` v2, `TarotReadingStorySurface`)
  - [x] Phase C web: journey history + Today deepen bridge (`tarotJourneyStore`, anchor spread, `tarot_deepen_started`)
  - [x] iOS Phase C: `TarotJourneyStore`, journey panel на hub, Today «Исследовать глубже» → anchor spread + `tarot_deepen_started`
  - [x] iOS question-first funnel: `TarotQuestionFlowView`, generic `TarotSpreadRitualView`, hub `/tarot`, reading v2 + resonance events
  - [x] Nav cleanup: `/guidance` и `/questions` → `/tarot` (редиректы + удалены legacy pages)
  - [ ] Android паритет воронки · **parked under freeze for content-first**
- [ ] **Tarot Immersive Dark Shell v1 (код)** — после Figma ниже; **parked under architecture freeze**.

- [ ] **Figma: Tarot Immersive Dark Shell — полный web-флоу** (см. spec ниже). **Исполнитель: дизайн в Figma**, не код. Код — отдельный пункт после DoD Figma. **Parked under freeze.**

#### Figma: Tarot Immersive Dark Shell — полный web-флоу (2026-07-06)

**File:** `WxwGUutaPRKpLKEvAICEEC` (TodayFlow Product UI)

**Источник визуала:** `archive · draft-tarot-dark-shell` (`65:2`) — **только** main + rail + tokens (фон, glass, gold, типографика блоков). **Не** копировать кастомный sidebar «ORACLE OS» / «TodayFlow ORACLE OS» из draft.

**Shell (фиксировано, как у остального product web):**

| Колонка | Ширина | Содержание |
|---------|--------|------------|
| Sidebar | 240px | **Стандартный** `DsAppSidebar`: Сегодня · Моя карта · Совместимость · **Таро (active)** · Практики + Настройки внизу — **тот же компонент/стиль**, что `web-compatibility-hub` `40:4`, `web-practices` `55:111` |
| Main | fluid (~880px) | Контент шага воронки |
| Rail | 320px | Общий для всего флоу (см. ниже) |

**Grid:** `240 | minmax(0,1fr) | 320` — как registry product web, **не** sidebar draft `65:4`.

---

**Создать фреймы (именование → route):**

| # | `frame_name` | Route | Stepper rail |
|---|--------------|-------|--------------|
| 1 | `web-tarot-hub` | `/tarot` | neutral (до шага 1) |
| 2 | `web-tarot-question` | `/tarot/question` | **1 · Вопрос** active |
| 3 | `web-tarot-spread-ritual` | `/tarot/spread/[spreadId]` | **2 · Карты** active |
| 4 | `web-tarot-result` | `/tarot/result` | **3 · История** active (+ **4 · Мост** в CTA-блоке) |

**Опционально (отдельные фреймы или variants):** guest limit gate · loading · error · refine-only sub-state на question.

---

**Main — что перенести из `65:2` (hub):**

- Header: eyebrow `TAROT / IMMERSIVE HUB` + status pills (карта дня, счётчик раскладов — placeholder copy)
- Row 1: hero «Задайте вопрос дню» + primary CTA «Начать расклад» + secondary «Продолжить прошлый вопрос»
- Row 1: recommended ritual card (visual + preset spread)
- Row 2: «Расклады для решения» — 3 карточки (**3** / **5** / **1** — copy из draft; product IDs: `three_cards`, `guidance_choice_two`, `one_card`)
- Row 2: «Карта дня» + «Вопрос для старта»

**Main — question (`§6.4` steps 2–3):**

- Домены concern (chips) + textarea своего вопроса
- Refine: варианты по домену + skip
- Spread select (если не на hub) — карточки **по вопросам**, не «1/3/5 карт»
- Те же dark tokens, **не** cream `55:449`

**Main — ritual (`§6.4` step 5):**

- Вопрос пользователя (quote)
- Pick + flip deck / slots; CTA «Получить толкование» disabled → enabled
- Карты **portrait**, не landscape crop

**Main — result (`§6.5`, структура колонок как `29:692`, tokens как hub):**

- Колонка карт (portrait, labels позиций)
- Колонка narrative: вопрос → verdict (Instrument Serif) → «Почему сейчас» → 3 insight rows → action box → follow-up chips → bridge (Today / practice / compat)
- **Запрещено в UI:** wall of card keywords, light theme, второй sidebar

---

**Rail — единый на все 4 экрана (из `65:2` right column):**

1. **Ritual gate** — copy про контекст дня (без LLM UI)
2. **Путь расклада** — stepper 1–4: Вопрос · Карты · История · Мост (highlight по экрану)
3. **Связи дня** — Фокус / Риск / Практика (placeholder chips)

---

**Удалить / архивировать в Figma (чтобы не было двух истин):**

| Frame | node | Действие |
|-------|------|----------|
| `web-tarot-hub` (светлый) | `55:449` | → `archive · web-tarot-hub-light` или удалить после промоции нового hub |
| `archive · draft-tarot-dark-shell` | `65:2` | После промоции: переименовать в `web-tarot-hub` **или** оставить в archive, canonical — новый ряд фреймов |
| Старый `web-tarot-result` | `29:692` | → `archive · web-tarot-result-light-sidebar` если sidebar не product-standard; заменить unified dark result |
| Registry card `11 web-tarot-hub` (0%) | `69:1221` | Обновить статус / удалить дубль |

**Не трогать:** iOS tarot frames (`ios-tarot-*`) — отдельный parity; android-tarot-*.

---

**DoD Figma:**

- [ ] 4 web-фрейма в product grid (240/ fluid /320) со **стандартным** sidebar
- [ ] Один token set (dark immersive) на hub → result
- [ ] Rail + stepper на всех экранах
- [ ] SCREEN REGISTRY обновлён (frame_name \| node_id \| route)
- [ ] `figmaMap.ts` layouts: `web-tarot-hub`, `web-tarot-question`, `web-tarot-spread-ritual`, `web-tarot-result` → node_ids
- [ ] Светлый `55:449` в archive / удалён
- [ ] Link frames в flow diagram (hub → question → ritual → result)

**После DoD Figma → код:** пункт «Tarot Immersive Dark Shell v1 (код)».

#### Tarot Immersive Dark Shell v1 — spec код (2026-07-06)

**Цель:** один связный тёмный Tarot-флоу (hub → question → ritual → result → bridge) по макету Figma **`archive · draft-tarot-dark-shell`** (`node_id` **`65:2`**, file `WxwGUutaPRKpLKEvAICEEC`). Старый светлый hub (`web-tarot-hub` `55:449`) и patchwork `theme="light"|"dark"` **удалить**, чтобы не было двух параллельных «истин».

**Жёсткие ограничения (от заказчика):**
- **Shell и сетка не меняем:** `ProductWebAppShell` → sidebar · main · rail (`DsAppShell`, ~240 / fluid / ~320). Стандартное product-меню (`DsAppSidebar`, те же пункты и routes) — **не** копировать кастомный sidebar «ORACLE OS» из draft.
- **Из draft берём:** визуальный язык (фон `#1a1714`, glass-панели, золото `#c9a96e` / `#d4af37`), типографику блоков, composition **внутри** main + rail.
- **Контракты и data не ломаем:** `SCREEN_CONTRACTS_V1` §6.4–§6.8, `tarot_answer_v1`, `tarotQuestionFlowCanon`, events (`tarot_session_started` … `tarot_reading_follow_up`), guest limits, journey/deepen bridge.

**Figma → продукт (hub `65:2`, main column):**
| Блок draft | Route / step | Примечание |
|---|---|---|
| Hero «Задайте вопрос дню» + CTA | `/tarot` | Primary → question flow; secondary → last session |
| Status pills (расклады / карта дня) | `/tarot` header | Data-driven, не декор |
| Recommended ritual card | `/tarot` | Deeplink в preset spread |
| «Расклады для решения» (3 / 5 / 1 cards) | hub + spread select | **ID раскладов** — существующие API; только UI/copy из draft |
| «Карта дня» + «Вопрос для старта» | hub + `/tarot/card-of-the-day` | Card portrait, `object-fit: contain` |

**Figma → продукт (rail, slot `rail`):**
| Блок draft | Содержание |
|---|---|
| Ritual gate | Контекст дня перед раскладом (Today contract slice) |
| Путь расклада (1–4) | Stepper: Вопрос → Карты → История → Мост; active step по route |
| Связи дня | Focus / Risk / Practice chips из day context |

**Шаги воронки (все экраны — dark shell, один token set):**
1. **Hub** `/tarot` — immersive hub по `65:2`
2. **Question** — domain + refine (inline или step; стиль dark, не cream hub)
3. **Ritual** `/tarot/spread/[spreadId]` — pick/flip; dark panels как в draft
4. **Result** `/tarot/result` — narrative по §6.5; layout можно унаследовать структуру `web-tarot-result` `29:692`, но **только** в tokens dark shell (не второй theme switch)
5. **Bridge** — CTA в Today / practice / compat (§6.6)

**Удалить / заменить (web, после parity нового UI):**
- `TarotWebHub` light layout + light-only CSS в `productWebScreens.module.css` (cream input, spread rows `55:449`)
- Переключатель `TarotWebScreen` `theme="light"` для tarot; единый `TarotDarkShell` или `theme="dark"` by default без light path
- Orphan / legacy UI: `TarotSpreadRitual.module.css`, `TarotHero`, `SpreadSelection` на hub, дубли `/tarot/spread/one-card` · `three-cards` если funnel полностью через `[spreadId]`
- Figma registry: **`web-tarot-hub` → `65:2`** в `figmaMap.ts`; пометить `55:449` archived (не implementation source)

**Не трогать без отдельной задачи:** backend spread API, `tarot_reading_synthesis`, iOS/Android (отдельный parity item после web DoD).

**DoD (web):**
- [ ] `/tarot` визуально соответствует `65:2` в main+rail; sidebar = стандартный product nav
- [ ] Полный путь hub → result без смены «другой темы» посередине
- [ ] Нет импортов удалённых light-tarot компонентов; `npm run build` green
- [ ] Карты не обрезаются (portrait + contain)
- [ ] Events + guest gates сохранены
- [ ] `figmaMap.ts` + строка changelog в этом файле

**Learning Δ (PIM):** те же events; rail Ritual gate может emit `sphere_opened` / context preview — без новых LLM calls.

### Texts and AI Pipeline
- [ ] Fully remove dependency on old meaning-shaping behavior inside `quality_gate`.
- [ ] Finalize generation quality for:
  - [ ] today
  - [ ] forecasts
  - [ ] profile interpretations
  - [ ] tarot
  - [ ] compatibility
- [ ] Lock one text standard:
  - [ ] clear
  - [ ] human
  - [ ] low-noise
  - [ ] no dead cliches
  - [ ] no esoteric filler
- [ ] Continue building the learning layer:
  - [ ] generation logging
  - [ ] feedback
  - [ ] prompt versioning
  - [ ] curated examples
  - [ ] user-level psychotype synthesis from daily answers, journals, questions, routes, and feedback
  - [ ] reusable learned interpretation context for future generations
  - [ ] internal quality memory: answer -> user reaction -> downstream outcome
  - [ ] use this quality memory to separate stronger and weaker response patterns
  - [ ] keep this loop invisible in user-facing language
- [ ] Add offline evaluation later to compare prompt quality with evidence.

### Practices (state cycle — canon locked 2026-07-30)

**Канон:** [practices/PRACTICES_SCREEN_V1.md](./practices/PRACTICES_SCREEN_V1.md) · [practices/_INDEX.md](./practices/_INDEX.md)

**Locked needs (order):** `calm` · `focus` · `recover` · `body` · `understand` · `sleep` — Успокоиться · Собраться · Восстановиться · Почувствовать тело · Понять себя · Уснуть (last).

**Locked formats (order):** `meditation` · `breath` · `yoga` · `stretch` · `visualization` · `affirmation` · `reflection` · `music` · `sleep`. Music chip = standalone practice; music **layer** §5 = accompaniment (both).

- [x] **C0** Canon v1.1 ACCEPTED — axis resolution (body+understand needs; yoga/stretch/music formats; reflection+sleep restored)
- [x] **C0b** UI-паритет need-ленты со скрина [`practices_screen_mockup_v1.png`](./practices/practices_screen_mockup_v1.png): + «Понять себя»; «Уснуть» last; иконки needs; hub music layer
- [x] **P0** Web `/practices` shell: need chips + recommend + Continue + moment + formats + practice of day + conditional my library
- [x] **P1** Session fullscreen + state check-in + «Сохранить в сегодняшний день» — `PracticeLiveSession` · draft → Continue · `?run=1` · meaning `practice_completed`
- [x] **C1** Rich catalog — `need_ids` / `format_id` / `outcome_label` + gap-fill (yoga/stretch/visualization/music/sleep); hub ranks by primary need (`9d770f3`)
- [x] **M0** Music layer UI (С голосом / Только музыка / Без звука + volumes) — FE prefs/panel; audio assets still optional
- [ ] iOS parity after web P0+P1 stable
- [ ] **Deploy** state-cycle `/practices` + C1 catalog freshness to production if backend image lags C1 tags

### UX and Navigation
- [ ] Fully audit mobile navigation.
- [ ] Remove duplicate or conflicting routes.
- [ ] Audit all buttons and links across the product.
- [ ] Ensure the user always understands:
  - [ ] where they are
  - [ ] what this screen is
  - [ ] what to do next
  - [ ] why the next module matters

### Mobile
- [ ] Audit all key screens on mobile width:
  - [ ] profile
  - [ ] today
  - [ ] forecasts
  - [ ] horoscopes
  - [ ] tarot
  - [ ] compatibility
  - [ ] calendar
  - [ ] habits
  - [ ] cycle
- [ ] Check spacing, heights, scroll, sticky layers, and overlays.
- [ ] Ensure menus, modals, and disclosure sections do not break the flow.

### Design
- [ ] Finalize one visual language for:
  - [ ] cards
  - [ ] typography
  - [ ] accents
  - [ ] atmospheric background layers
  - [ ] motion
- [ ] Ensure heavy blocks reveal progressively instead of dumping everything at once.
- [ ] Remove random visual leftovers from older screen generations.

### Data and Input
- [ ] Finalize RU/EN city input.
- [ ] Allow normal name input beyond Latin-only assumptions.
- [ ] Verify geocoding returns stable coordinates.
- [ ] Verify save and rebuild flow when core data changes.

### Performance
- [x] Continue removing duplicate heavy requests (incremental: `/today` supports `light=1` and `/today/opening` for fast first paint; full payload unchanged by default).
- [ ] Audit caching for:
  - [ ] core profile
  - [ ] daily forecast
  - [ ] monthly/yearly forecast
  - [ ] tarot explanation
  - [ ] compatibility
- [ ] Remove unnecessary rerenders and page jitter.
- [ ] Audit speed of `/today`, `/profile`, `/horoscopes`.

### QA and Cleanup
- [ ] Walk all legacy routes and decide which stay as aliases and which get deleted.
- [ ] Check console for `404`, `500`, and runtime warnings.
- [ ] Verify auth redirects and return-to-origin flow.
- [ ] Verify full Docker run scenario.
- [ ] Keep `PRODUCT_EXECUTION_TRACKER.md` as the single working execution point.

---

## 5.1 Text Generation Policy Shift

New rule:
- meaningful user-facing texts should be generated through API-backed interpretation;
- the old `quality_gate` is not the source of meaning anymore.

Operational consequence:
- we now store prompt/version/output traces for `forecast`, `tarot`, and `numerology` generation flows;
- quality improvements must come from prompt/context iteration and reviewed datasets, not from over-aggressive gating.

## 5.2 Learning Layer Status

Status: `IN_PROGRESS`

### Implemented
- [x] Added DB tables for `prompt_versions`, `generation_logs`, `generation_feedback`.
- [x] Added backend `LearningService`.
- [x] Added `POST /learning/feedback`.
- [x] Added admin prompt registry listing.
- [x] Connected forecast/tarot/numerology generators to best-effort logging.

### Next
- [ ] Add implicit feedback signals from UI interactions.
- [ ] Surface generation IDs to frontend where user feedback is collected.
- [ ] Add offline evaluation scripts and curated dataset export.
- [ ] Route `Profile` and `Today` generation through the same logged pipeline.

`quality_gate` may remain only as:
- output sanitation,
- broken payload detection,
- anti-garbage safety layer.

It must not:
- flatten rich text,
- over-template copy,
- replace specific interpretation with dead generic phrases.

## 5.3 Day Engine — execution backlog

Linked canon: [DAY_ENGINE_AND_COHERENCE.md](./DAY_ENGINE_AND_COHERENCE.md). Tracker checklist: **§4.7**.

Ordered work (aligns with canon §7):

1. **UI garbage pass** — duplicates, abstract CTAs, blocks without action (keep §4.6 information diet).
2. **DE-1** — done: [DAY_CONTEXT_V0.md](./DAY_CONTEXT_V0.md) + schema + `build_day_context_v0`; при появлении публичного DTO — сверка типов с iOS.
3. **DE-2** — done: `build_day_context_v0` в `build_today_narrative` до LLM; guide из `DayContext.layers`; hash и версия контракта в `generation_logs.input_payload` (`day_context_sha256`, `day_context_contract_version`).
4. **DE-4** — done: расширены `POST /meaning/events` и веса колец; клиенты (Today web + iOS) переведены на канонические `event_type` где однозначно; см. `TODAY_PERSONALIZATION_CORE`; DE-3 закрыт для Today narrative + learning.
5. **DE-5** — done: агрегаты по `meaning_events` (окно 7–60 дней) в DayContext и learning; подсказки `pattern_hints` в psychotype summary и в user-prompt всех surface Today narrative.
6. **DE-6** — done: intent + head_topic в DayContext и narrative (см. §4.7 DE-6). **DE-7** — done: flow closure в fusion + UI главного шага (см. §4.7 DE-7).
7. **DE-7** — v0–v2: flow closure в fusion / slim (в т.ч. `guide_meaning_completions_today`). **DE-9** — v0: `day_history_v0` в DayContext и `day_history` в user JSON narrative (вчера + 7 дней fusion scores + дельта). **DE-13** — backlog: цепочка узких LLM/артефактов вместо монолитного `surface=guide` (см. [DAY_ENGINE_AND_COHERENCE.md](./DAY_ENGINE_AND_COHERENCE.md) §2.1).
8. **Обязательное продолжение контура (не «опционально»):** **DE-8** (глубина: контракт + управляемая ветвь промпта + UI настройки, когда API v0 готов) и **DE-9** (время: уже в DayContext/промпте — довести **наблюдаемость** для пользователя и при необходимости обогащение смысловыми сигналами по дням). **DE-10 / DE-11** — по согласованию и приватности, после измеримого ядра. **DE-13** — целевая декомпозиция монолитного guide (см. [DAY_ENGINE_AND_COHERENCE.md](./DAY_ENGINE_AND_COHERENCE.md) §2.1); вести как отдельный эпик, не смешивать с косметикой UI.

**Rule:** any merge that touches Today narrative, ritual payload, or learning ingestion should update §4.7 table status or this subsection.

### 5.3.1 Канон пользовательского копирайта Today (web ⇄ iOS)

**Источник формулировок (SoT для текста на экране Today):** `frontend/src/components/today/todayRitualCopy.ts` — объект `RITUAL_COPY` и экспортируемые рядом `format*`; **дословное зеркало:** `ios/TodayFlow/TodayFlow/Design/TodayRitualCopy.swift` (в т.ч. блоки `TodayWeb*`). Experience canon: [TODAY_SCREEN_V1_CANON.md](./TODAY_SCREEN_V1_CANON.md). Логика Day Engine: [DAY_ENGINE_AND_COHERENCE.md](./DAY_ENGINE_AND_COHERENCE.md), [DAY_CONTEXT_V0.md](./DAY_CONTEXT_V0.md).

**Связь с п.1 (UI garbage):** пользовательский русский в `frontend/src/components/today` вне `todayRitualCopy.ts` / каталогов i18n — долг §5.3; правки копирайта сценария Today делаются в каноне и зеркале, а не «в месте вызова».

**Вопрос дня (рабочий слой):** промпты и опции — в `todayRitualCopy.ts` (`RITUAL_QUESTION_OF_DAY_*`, `buildRitualQuestionOfDayDefaultCards`); `buildQuestionOfDay` в `todayPageUtils.ts` только выбирает пул и индекс по дате; зеркало — `TodayWebQuestionOfDayCopy` в `TodayRitualCopy.swift`.

**iOS, компактный «быстрый ответ» в `TodayView`:** шапка, подписи шагов, варианты «да/нет/неясно», контекст «отношения/работа», кнопка сохранения, префиксы баннеров, тост успеха — в `RITUAL_COPY` (`workingLayerCompactQuickAnswer*`, `workingLayerQuickDecision*`, `workingLayerQuestionOfDaySavedContextPrefix`) и `TodayWebWorkingLayerCopy`.

**iOS, нативные композеры на `TodayView` (утро / чек-ин / дневник / вечер):** весь видимый RU — в `RITUAL_COPY` (`todayView*`, общее `todayViewComposerSaving`, промпты типов дневника `dayJournalPrompt*`) и зеркале `TodayWebTodayViewComposerCopy` + `TodayWebDaySectionCopy` / `TodayWebEveningSectionCopy` (подписи шкал чек-ина); форматтеры `formatTodayViewMorningComposerSavedBanner`, `formatTodayViewJournalSavedCountBanner`.

**iOS, основной экран `TodayView` (герой, guide/день/вечер, таро, fusion, фолбэки):** строки в `TODAY_SHELL_COPY` (`shell*` в `todayRitualCopy.ts`) и зеркале `TodayShellCopy` в `TodayRitualCopy.swift`; переиспользуются `TodayWebGuideSectionCopy.guidePanelEyebrowToday`, `TodayRitualCopy.dayEngineBriefEyebrow`, `TodayWebFlowTabsCopy`, `TodayWebWorkingLayerCopy` (да/нет в отклике таро), `TodayWebDaySectionCopy` (типы дневника в ленте); форматтеры `formatShell*` рядом с `TODAY_SHELL_COPY`.

**Четыре сферы + ритуальный поток iOS:** пользовательские фолбэки сфер и энергетического риска — `RITUAL_COPY.fourArea*` в `todayRitualCopy.ts`, логика в `todayFourAreas.ts` (паритет `RitualFourAreaBuilder`); строки экрана `TodayRitualFlowView` (дисклеймер метрик героя, a11y ритма, защита дня, вечерний лоадер, число дня, треугольник сфер, подсказки целей) — `ritualFlow*` и форматтеры `formatFourAreaEnergyRiskChunk`, `formatRitualFlow*` в TS и зеркальные `TodayRitualCopy` / `TodayShellCopy` (подписи орбов героя).

**Продуктовый лейаут `TodayExperienceLayout` (RU/EN):** канон `TODAY_EXPERIENCE_CHROME_RU` / `TODAY_EXPERIENCE_CHROME_EN` и `formatExperience*` / `experienceChromeBundle` в `todayRitualCopy.ts`; зеркало — `TodayExperienceChromeCopy.swift` (включая пресеты «удачного окна» для блока числа дня).

**iOS главный TabView + вкладки Flow и Практики (RU/EN):** канон `TODAY_MAIN_TAB_COPY_*`, `FLOW_TRACKER_CHROME_*`, `PRACTICES_EXPERIENCE_CHROME_*` и хелперы (`flowStreakTitle`, `practicesDaysStreak`, …) в `frontend/src/components/today/flowPracticesMainTabChrome.ts` (реэкспорт из `todayRitualCopy.ts`); зеркало — `FlowPracticesMainTabChromeCopy.swift`; точка входа вида — `FlowTrackerChrome.swift` (`typealias` на `*Copy`).

---

## 6) Current Priorities (Execution Order)

> **Активный фокус (2026-07-26):** **Tarot Interpretation Stack v1 — Architecture Frozen / Editorial Phase.** Foundation accepted (live r3 **12/12** · reliability deploy `da03d22`). Full freeze lift declined. **Next:** human Golden Eval v2 (real questions · 3 post-answer questions). Canon [TAROT_INTERPRETATION_ENGINE_V1](./tarot/TAROT_INTERPRETATION_ENGINE_V1.md) · [owner note](./audits/TAROT_STACK_EDITORIAL_PHASE_2026-07-26.md) · [live r3](./audits/TAROT_GOLDEN_EVAL_LIVE_2026-07-26_r3.md).

### 🔴 Phase 3 — Screen Block Definition (единственный приоритет)

**Канон:** [TODAY_SCREEN_V1_CANON.md](./TODAY_SCREEN_V1_CANON.md) + [PROFILE_SCREEN_MASTER.md](profile/PROFILE_SCREEN_MASTER.md) — build (full internal) vs reveal (L1–L4 UI).

**Порядок P0:** Onboarding (5) → Profile **Identity · Intent · Reality · Direction** → **затем** Today Theme · Action · Progress. Today = проекция Profile, не раньше source.

| Step | Status |
|------|--------|
| Onboarding (5 секций) | 🟡 defined v1.1 — **review** |
| Profile Identity (Facts · Markers · Narrative) | 🟡 v1.3 — **review** |
| Profile I · R · D (non-Identity) | 🟡 v1.2 draft |
| Profile Behavior · Knowledge · Rhythm · Map | ⬜ |
| Today T · A · P | ⏸ blocked |
| Test B / viability | ⏸ blocked |

---

### ⏸ Phase 4 — Core Loop Viability Test (paused)

**Статус:** PAUSED — blocked on Screen Block Definition (Today T→A→P). Instrument `?core_loop=1` = черновик, не канон UI.

| Step | Status |
|------|--------|
| Test A backend | ✅ conditional |
| Instrument (G1-surface web) | ⚠️ draft (needs §2 alignment) |
| Test B pulse 1 | ⏸ |
| Verdict A or B | ⏸ OPEN |

---

### Цель: зацикленный умный сервис (Day Engine) — **после First Day P0**

**Канон:** один логический **DayContext** → генерация narrative → экраны Today → **действия и ответы пользователя** (meaning events, Flow, вечер, feedback с `generation_id`) → агрегаты и следующий DayContext. Это не набор разрозненных экранов, а **сервис с обратной связью**; см. [DAY_ENGINE_AND_COHERENCE.md](./DAY_ENGINE_AND_COHERENCE.md) (вход/выход, §2.1 уровни 5–6, §5 критично добавить).

**Уже в контуре (§4.7):** DE-1…DE-7, DE-12; обучение: события, паттерны, intent, fusion closure в UI.

**Следующие обязательные инкременты (порядок работ):**

0. **DE-8** — **DONE** (§4.7): глубина в профиле + на Today, тарифный кламп, meaning-событие `today_narrative_depth_changed`.
1. **DE-9** — сделать **temporal context** не только в промпте: явный UX/API слой «вчера / неделя» там, где усиливает доверие и решение (веб + iOS, те же контракты).
2. **Learning pipeline (§5.2 Next)** — неявные сигналы из UI, полнота `generation_id` там, где собирается исход, **единый logged pipeline** для Profile и Today narrative (как в чеклисте §5.2).
3. **UI garbage pass (§5.3 п.1)** — убрать дубли и пустые CTA без действия; не опережать смысловую цепочку.
4. Затем — канонический путь продукта: `core build → profile → today → deeper services`; **Profile** как живая карта; **Today** как ежедневный двигатель; JTBD-лейны без разрыва с Day Engine.

5. Качество навигации, копирайт, мобильный QA — непрерывно, но **после** фиксации измеримого ядра контура (п. 0–2).

### 6.2 Branch goal — «Today» 100% (Definition of Done for this branch)

**Смысл «100%» здесь:** экран **Today** (веб + нативный iOS) соответствует канону **§4.6 Daily ritual UX** и **[TODAY_SCREEN_V1_CANON.md](./TODAY_SCREEN_V1_CANON.md)**; цепочка **Day Engine** для дня замкнута на уровне **обязательного minimum** ниже.

**Не входят в эту метрику:** Phase 6 JTBD, DE-10/11/13, полный редизайн Forecast как отдельного сервиса вокруг профиля.

#### Обязательно (DoD ветки)

1. **Контракты и загрузка:** `GET /today`, `GET /tracking/fusion/{date}`, `POST /today/narrative` (guide → day_layer → spheres → evening) корректно обрабатывают ошибки и пустые состояния; после ритуала guide пересобирается с `ritual_context` (веб + iOS).
2. **Ритуал:** карта → число → настроение (+ `head_topic` где задано); пользовательский копирайт ритуала только из `todayRitualCopy` / `TodayRitualCopy` (паритет строк web ⇄ iOS).
3. **Секции канона:** ориентиры, сферы, главный шаг, база дня (четыре опоры), глубина (CTA), вечерняя фиксация — присутствуют и не противоречат TODAY_WEB §3–4.
4. **Сигналы:** канонические `event_type` и payload для meaning-событий **паритет web ⇄ iOS** для чипов карты, числа, главного шага и essentials (см. TODAY_WEB §4.1, §5).
5. **Персонализация narrative:** вход в LLM через сжатый `user_core` / slices без дублирования сырого `profile` в guide JSON (см. `today_narrative` и связанные тесты контракта).
6. **Документация:** при закрытии ветки обновить статус в **§4.7** и **[IOS_TODAYFLOW_STATUS.md](./status/IOS_TODAYFLOW_STATUS.md)** под фактическое состояние.

#### Желательно (не блокер «100%» этой ветки)

- **DE-7** закрыт в §4.7 (v3 UI); дальнейшая **жёсткая связка** текста вариантов шага с событиями — см. backlog в строке DE-7.
- **DE-8:** пользовательская настройка `depth_level` в UI — перенесено в **обязательный** дорожник §6 (п. 0), не «когда-нибудь».
- Динамический набор сфер и отдельные API под фокус дня/вечер (TODAY_WEB §5 — следующие итерации).

#### Явно вне скоупа ветки

- DE-10 Health, DE-11 journal excerpts, DE-13 multi-call narrative pipeline.

---

## 7) Progress Log

Use format:
- `YYYY-MM-DD` | `Area` | `Change` | `Status` | `Notes`

Historical note:
- older entries may mention the legacy `5-section` IA model;
- these entries describe what was implemented at that time and do not override the current question-first product canon.

- 2026-08-24 | Today / Native C1 | **1.3.119 everyday scene retry** | **LOCKED** | Prompt c5.2 + all-scene lived-marker retry; Global max_attempts 3. SCENE_* detectors unchanged. Live 2026-08-24: user **13** gen **1106** PASS; **17** gen **1107** PASS (3 Global, ASTRO_JARGON then accept); **8** gen **1108** PASS; **11** gen **1109** PASS. User **15** still `verbatim_seed_leak` (out of scope). [NATIVE_C1_EVERYDAY_SCENE_RETRY_V1](./today/NATIVE_C1_EVERYDAY_SCENE_RETRY_V1.md).
- 2026-08-24 | Today / Native C1 | **1.3.118 evidence pack binding** | **LOCKED** | `unknown_evidence` allowlist = events pack (string ranked_drivers) + foundation cite aliases (`ev.foundation.lunar.*` gen 1092) + interp evidence + pers pack. Gate not weakened. Prompt c5.1. [NATIVE_C1_EVIDENCE_PACK_BINDING_V1](./today/NATIVE_C1_EVIDENCE_PACK_BINDING_V1.md).
- 2026-08-18 | Ops / LLM | **AI COGS llm_usage_v1** | **CODE** | Per-request feature/model/tokens/cost + operation_id/trigger/retry. Billed output does not double-count reasoning. Report: feature×trigger×model×retry_reason + top-20 ops. Do not switch model until that report. Canon: LLM_QUALITY AI COGS · AMLL token fields 🟡.
- 2026-08-17 | Brand / Copy | **Landing copy: three trust levels** | **CODE** | Точность / глубина / человечность as pillar kickers. Locked H1 unchanged. Rejected: «наука», «не алгоритм», «построить карту» as primary. [Trust Layer](./content/TODAYFLOW_TRUST_LAYER.md) v1.3.
- 2026-08-17 | Brand / Copy | **Trust Layer on landing + ads brief** | **CODE** | Hero `trustLine` · `#trust` three pillars · footer · [Trust Layer](./content/TODAYFLOW_TRUST_LAYER.md) v1.1 §6 ads. No Horizons / no NASA endorsement / no finished IL catalog. Next = about/press if needed.
- 2026-08-17 | Brand / Copy | **Trust Layer locked — two pillars + NASA/JPL bounds** | **CANON** | [TODAYFLOW_TRUST_LAYER.md](./content/TODAYFLOW_TRUST_LAYER.md) v1.0. Canon ≠ averaged astrology; provenance is brand language. Astronomy copy = Swiss/DE431 live, not Horizons. Next = landing + ads. Voice Canon v1.9 acquisition exception.
- 2026-08-15 | Today / Canon | **I2/I3 hygiene** | **CODE** | `primary_scene_id` on native+scenario; gate reject missing/unknown; projector no first-scene pick / no expect concat / do from primary only. Next: I0 contract → Global Engine.
- 2026-08-15 | Today / Canon | **Pipeline ownership + non-mutation** | **LOCKED** | [TODAY_CONTENT_PIPELINE_V1](./today/TODAY_CONTENT_PIPELINE_V1.md): один decision owner на поле; downstream enrich/verbalize only; цепочка Небо → Global Day → Natal Overlay → Ritual → Personal → Presentation; UX reveal ≠ authority. Next: I2/I3 hygiene → I0 contract → Global Engine.
- 2026-08-14 | Design System | **Form Kit full-sheet SoT** | **LIVE (FE)** | Chips statusTone=`--tf-semantic-*` only; `DsLinearProgress` + semantic `DsWaveMeter`; button `lg`; `DsSectionHeader` composition; quote highlight; `/design-system` 100% sheet specimen; DayBrief data-backed only + `DsCelestialMoon`. Next = Practices zone migration.
- 2026-08-14 | Ops / LLM | **K2.6 primary · K3 complex-only** | **CODE→deploy** | `NEBIUS_MODEL=K2.6`; `NEBIUS_COMPLEX_MODEL=K3` for CE 2–4 / profile funnel / natal decode only. Day/prewarm stay on K2.6.
- 2026-08-04 | Design System | **Day shell chrome fix** | **DONE (LIVE)** | PR #14 merged · frontend rebuild. Day-mode = shell routes; evening phase gated; sidebar stretch.
- 2026-08-05 | Design System | **Task 2.9b Compatibility result** | **IN PROGRESS (code)** | Exploration main/duals/tips/deep + funnel confidence/today/risk + analyze/signs personalized → `DsCallout`/`DsQuote`. Not zone DONE — 6-axis DoD + screenshots remain.
- 2026-08-05 | Design System | **Task 2.9b Tarot result** | **DONE (CODE)** | `TarotWebResult` answer/next_step/A·B/confidence/why → `DsCallout`/`DsQuote`. Not zone DONE — 6-axis DoD + screenshots remain.
- 2026-08-05 | Design System | **Task 2.9b Today Reading** | **DONE (CODE)** | Reading duals / soft-why / move if-then / vibe → `DsCallout`/`DsQuote` in `TodayPersonalizedProductSection`. Not zone DONE — 6-axis DoD + screenshots remain.
- 2026-08-05 | Design System | **Task 2.9 foundation (PR1)** | **DONE (CODE)** | Semantic layers SoT: FOUNDATION_UI §5/§5.1; ink quintet; `DsCallout` tone×label; `DsQuote`/`DsCapsule`; type ladder 48–60/34/24/18/16/14/12. Pilot `TodayDayLogicCallout`. Gate fix `ProductJourneyScene` caption hex. Does **not** close zones — 2.9b+ under 6-axis DoD.
- 2026-08-05 | Design System | **Task 2.7 + 2.6 + 2.6b Wave 1–2** | **CODE (layout DoD ✅; zones IN PROGRESS)** | Shell wrappers → `--tf-shell-max`; zone columns tokenized; gate v2 (rgba/color-mix/font-size/max-width); Compatibility cards → `--day-*`/`--tf-*`; ~382 type literals → `--tf-type-*`. Baseline 1964 keys. Screenshot parity still required before zone DONE / Onboarding.
- 2026-08-05 | Design System | **DS unification reopen** | **IN PROGRESS** | Practices/Profile/Compatibility not DONE on color-only gate. 6-axis DoD. Wave 1 = Task 2.7 layout; Wave 2 = Task 2.6 rgba gate + 2.6b type; then screenshots; then Onboarding.
- 2026-08-04 | Design System | **Task 3 Compatibility wave** | **REOPENED (color partial)** | PR #13 merged · Hub/analyze/signs/birthdates → `DsButton`; baseline 495→447. Layout/rgba/type/screenshots pending under DS unification.
- 2026-08-04 | Design System | **Task 3 Profile wave** | **REOPENED (color partial)** | PR #12 merged (`eb4e281`) · Hub/setup CTAs → `DsButton`; `profileV2System` tokenized. Layout/type/screenshots pending.
- 2026-08-04 | Design System | **Task 3 Practices wave** | **REOPENED (color partial)** | PR #11 merged. Hub/session/detail CTAs → `DsButton`; lavender zone killed. Layout/type/screenshots pending.
- 2026-08-04 | Design System | **Task 3 Today wave** | **DONE** | PR #10 merged (`de9dfed`). Composition ScreenFlow CTAs → `DsButton`; pick sheet `--day-surface-tint`.
- 2026-08-03 | Profile / Ops | **Force-publish profile via Kimi-K3** | **LIVE canary** | `force_rebuild_profile_ops.py` users 1/2 · CE publish_portrait · contract+ce `ready` · identity rewritten (Kimi stream). Stage 3–5 still diagnostics-only on this cutover; Stage 2 LLM path used.
- 2026-08-03 | Today / Ops | **Kimi-K3 force_rebuild (stream idle 300s)** | **LIVE canary** | Redeploy env K3 + read=300, no DeepSeek. gen489 user1 / gen490 user2 → `native_llm_c1` model=`moonshotai/Kimi-K3` (~23m / ~2m). Streaming held connection; first attempt via docker exec OOM/137 — used compose run job.
- 2026-08-03 | Today / Ops | **Kimi stream + no DeepSeek hop** | **LIVE canary** | Probe: K3 TTFT **157s** / K2.6 **0.6s** on Nebius. SSE + empty fallback. Primary **Kimi-K2.6**. Force_rebuild: user1 gen487 / user2 gen488 → `native_llm_c1` model=`moonshotai/Kimi-K2.6` (no DeepSeek).
- 2026-08-03 | Today / Ops | **Kimi-K3 primary + DeepSeek fallback** | **SUPERSEDED** | K3 primary impractical on Nebius TTFT; see stream+K2.6 row.
- 2026-08-03 | Content / Voice | **Practitioner persona v1.2 — pro crafts + informal** | **LIVE** | Voice Canon §1 → v1.8 · `llm_practitioner_persona_v1.2` on BE · professional tarot/astro/numerology + friendly informal (emotion · metaphor) · `common_v1` aligned. Force_rebuild to taste new voice.
- 2026-08-03 | Today / Ops | **Soft-heal one-field gates** | **LIVE canary** | BE redeployed. User2 gen480 → `native_llm_c1` clean accept (DeepSeek, 2 scenes, no B5). User1 gen479 → still `unavailable_after_llm` (attempt0 editorial SEED_CHORUS_PASTE/SCENE_*; attempt1 Kimi empty) — heal path not reached. Broader prewarm still held.
- 2026-08-03 | Today / Ops | **DeepSeek→Kimi + no B5 invent** | **LIVE canary** | BE redeployed. Canary rebuild users 1/2 (`2026-08-03`): gen 477/478 → `unavailable_after_llm` (empty/parse on Kimi path); **no B5** («Сделай один короткий шаг» absent; expect/do empty). Broader prewarm **held** until native/kept improves. Soft-fill conflict_link = next slice.
- 2026-08-03 | Today / Ops | **Native day_story P0: instrumentation + no-retry-on-timeout** | **CODE** | Timeout → immediate deterministic fallback (no 2×45s). Logs: `generation_source`, `native_llm_c1_meta` (failure_class/attempts/chars), model kept on fallback, `error_message`. Product metric: `report_day_story_native_share.py` (+ alert <30% among llm_attempted). Attempt-2 slim/alt = later. Test `test_native_llm_no_retry_on_timeout_p0`. Not live until BE deploy.
- 2026-08-03 | Today / Live QA | **Atmosphere paint + Glance chrome + content mash fixes** | **LIVE (deployed)** | Day CSS now beats day-phase peach on `--tf-page-atmosphere`; decor inside product frame; Glance «Шаг n/m» (no SCREENFLOW/TodayFlow brand). Reading stub suppressed (`asScreenFlowSteps`); sphere kickers → DomainLens labels; color clothing only when name matches / props.where_to_use; number voice uses reduced digit; evening CTA gated to Response; lunar pulse skip if already in why; serve-heal marker «проживите день в ключе». Hard-refresh; stale Symbols may need contract refresh for heal.
- 2026-08-03 | Today / Day Atmosphere | **Visible pass + Glance mockup IA** | **LIVE (deployed)** | Auto `day_atmosphere` nest from thesis.mode (BE `day_atmosphere_v1`) · bridge nest+pin · shell `--day-*` + CSS decor · Glance glass-hero + ScreenFlow gauge. Compose rebuild BE+FE · health 200 · mapper smoke `conflict→tension`. Canon FOUNDATION_UI §11.9/§13 · TODAY_SCREEN_SCENARIO_V3 Экран 0. **Architecture impact:** public nest `day_atmosphere`; Glance layout SoT; section wash demoted under `data-day-mode`.
- 2026-08-03 | Today / ScreenFlow | **v3.1b concreteness (meta-leak + tag-dump + color mash)** | **CODE** | Chorus card/number/sky bridges → lived tips; number no longer «темп — / способ —»; color link once (no symbolic×3); avoid why без дубля имени; timeline без «X в трении»; serve-heal markers for generation-meta; FE where_to_use = one tip + benefit dedupe. Canon TODAY_SCREEN_SCENARIO_V3 §0.7–0.8. Not live until deploy.
- 2026-08-03 | Today / ScreenFlow | **Content jobs v3.1 + seed-kill closeout** | **LIVE (deployed)** | Gap plan P0–P2 closed. Seed-kill three layers: generation · native map (`serves_conflict`=`тон дня`, `why`="") · defense (serve heal `48b589c` + hard-gate `b2d8203`/`fa4d915`). Prod compose tip `7a653a0` · health 200 · live DB 17/17 seed_left=0 · user2 Plot/Symbols bridges clean · `serves=['тон дня']`. PR #7 still draft; CI blockers pre-existing (iOS Copy Policy · Validate i18n) — not merge yet. Canon TODAY_SCREEN_SCENARIO_V3 · SCREEN_FLOW §4 · GATE_MATURITY C36.
- 2026-08-01 | Astro / Foundation | **Foundation v1 (единый канон)** | **IN PROGRESS** | DATA pack live; house_rulers+profections → `ruler_classical`; top_driver/activation copy → `aspect_is_*`; FE color guide deprecated. Next: tarot FE→card_base cutover; drop FE color prose; domain magnitude tables. Canon [foundation_v1.md](./foundation_v1.md).
- 2026-08-01 | Today / Hooks | **Bridge machine-id leak** | **LIVE (deployed)** | Reject `conflict.*` / snake slugs in `hook_reveal` bridge + native chorus normalize + FE `isMachineToken`. Regression: `conflict.intensity_without_drama` → bridge unavailable (base kept).
- 2026-08-01 | Astro / Foundation | **Geometry closeout (coords/Swiss/angles)** | **DONE** | Evidence folded into [foundation_v1.md](./foundation_v1.md) §1. Swiss live; TZ+caches; Einstein ≤1′; taps held.
- 2026-08-01 | Astro / Natal | **No civil-as-UT + birth TZ resolve** | **LIVE (deployed)** | Engine 422 `timezone_required` (no silent UT). Backend resolves IANA from city/coords on save; `needs_timezone` on profile. Cache rejects TZ-less precise charts. Blast was **2** precise NULL-TZ profiles (Igor→`Europe/Minsk` ASC Gemini 14.77; Kyiv→`Europe/Kyiv`); caches rewarmed; `today_tap_events` count unchanged (1). Also: sky_drivers out of day_facts contract; quincunx OOS v1; orb≠time bridge constraint; `_longitudes_at`/noon-transit pass TZ.
- 2026-08-01 | Tarot / SoT | **card_base_v1 cutover (explainer + question-tarot)** | **CODE** | `TarotService` upright/reversed/meaning ← `card_base_v1.prose_sides`; interpretation pack catalog strings same; explainer `tarot-explainer-v4` forces `meaning` from bank (LLM = personalization only). Tests `test_card_base_cutover_v1` 5/5. Canon [TAROT_CARD_BASE_V1](./tarot/TAROT_CARD_BASE_V1.md) §3. Next: editorial pass on 156 bank texts; FE `TODAY_TAROT_CARDS_RU` cleanup.
- 2026-08-01 | Today / Hooks | **Glance overview + hook_reveal (base/chorus)** | **LIVE (deployed)** | Compose rebuild BE+FE `7dc7e8a` · live chunk + guest `/today/symbols/*` hook_reveal smoke · Glance/hook markers in prod JS · cutover explainer/question-tarot → row above
- 2026-07-31 | Practices | **C1+ server catalog enrich** | **DONE / DEPLOYING** | Free GENERAL library ~47 tagged practices; `GET /practices?need=&format_id=`; `/practices/state-cycle/coverage`; complete accepts `state_after`. `99d6e85`.
- 2026-07-31 | Practices | **C0b mockup need-лента** | **DONE (FE)** | Visual SoT = [`practices_screen_mockup_v1.png`](./practices/practices_screen_mockup_v1.png). Need icons + canon order (+Понять себя, sleep last); recommend/moment chrome; hub «Музыкальное сопровождение»; formats keep reflection+sleep.
- 2026-07-31 | Practices | **C1 rich catalog (need/format tags)** | **DONE** | Overlay + 12 gap-fill free practices; public optional `need_ids`/`format_id`/`outcome_label`; hub match/rank by tags + outcome card titles. `practice_state_cycle_catalog_v1` · `9d770f3`.
- 2026-07-30 | Practices | **M0 music layer (session)** | **DONE (FE UI)** | Modes С голосом / Только музыка / Без звука · volumes · prefs `localStorage`. Panel in `PracticeLiveSession`. Tracks when URLs present. SSR catalog clipped (`286e7f3`).
- 2026-07-30 | Practices | **P1 live session + check-in + save to Today** | **DONE (FE)** | `PracticeLiveSession`: fullscreen timer/pause · check-in better/same/harder · POST `/complete` + meaning `practice_completed` (`state_after`, `surface=practices_session_p1`) · local draft powers hub Continue · hub links `?run=1`. Tests: PracticeLiveSession + practiceSessionDraft.
- 2026-07-30 | Practices | **P0 web state-cycle shell** | **DONE (FE)** | `/practices` → `PracticesStateCycleScreen`: 6 need chips · recommend · moment rail · 9 format chips · practice of day · conditional my library · desktop Today rail. Client keyword filter until API needs. Images: `/images/praktiki_banner.png` + CSS gradient placeholders. Continue via session draft (P1). Tests: practicesCanon + StateCycleScreen.
- 2026-07-30 | Practices | **Screen v1.1 canon — axis resolution** | **ACCEPTED** | SoT [practices/PRACTICES_SCREEN_V1.md](./practices/PRACTICES_SCREEN_V1.md) v1.1: needs keep **both** «Почувствовать тело» + «Понять себя» (body vs reflective axes); «Уснуть» last. Formats: yoga/stretch/music chips (spec «Телесные» detailed); restore reflection+sleep; music = chip ⊕ layer. **C0b** mockup need-align. No parallel `practices-canon.md`. Next: C0b → P0 → P1; M0 ∥.
- 2026-07-30 | Practices | **Screen v1.0 canon C0 (need/format freeze)** | **SUPERSEDED → v1.1** | v1.0 dropped «Почувствовать тело» and umbrella `body` format; replaced by axis logic in v1.1.
- 2026-07-30 | Today / Content | **Wave 2 Phase D.2b — conflict.driver_ids generation SoT** | **LIVE (MERGED)** | `build_scenario_conflict_v1` + native LLM map: when foundation has `pt-*`, conflict.driver_ids = top-N natal (Strip pool). Pack stays on foundation.ranked_drivers. Stale caches still D.2-gated until regen. [CONTRACT §7](./today/TODAY_WAVE2_CONTRACT_V1.md) · [PLAN D.2b](./today/TODAY_WAVE2_EXECUTION_PLAN.md).
- 2026-07-30 | Today / Content | **Wave 2 Phase D.1–D.2 PR #5** | **MERGED** | day-facts slots + narrative project + `pt-*` ⊆ gate; Act3 demotion reverted. Base `design/profile-journey-premium` @ `2db2c03`.
- 2026-07-30 | Today / Content | **Wave 2 — conflict.driver_ids generation SoT** | **SUPERSEDED → D.2b** | Was BACKLOG; active as D.2b row above.
- 2026-07-30 | Today / Content | **Wave 2 Phase D.2 — day_facts `pt-*` ⊆ gate** | **LIVE** | Project narrative only when all conflict.driver_ids are `pt-*` and ⊆ fresh pool; pack → `partial: true`. Revert Act3 demotion from `69bfa59` (Act3 stays on day_scenario). No trust_ok / no invent. FE today does not read day_facts.conflict/scenes. [CONTRACT §7](./today/TODAY_WAVE2_CONTRACT_V1.md) · [PLAN D.2](./today/TODAY_WAVE2_EXECUTION_PLAN.md).
- 2026-07-30 | Today / Content | **Wave 2 Phase D.1b — narrative on day_facts** | **LIVE** | Project cached `day_scenario` onto `GET /today/day-facts` when gate passes (D.2: `pt-*` ⊆ only). Body-label aliases fix empty activations. thesis=`label_ru`|null; evening_payoff null. Act3 still day_scenario nest. [CONTRACT](./today/TODAY_WAVE2_CONTRACT_V1.md) · [PLAN D.1b](./today/TODAY_WAVE2_EXECUTION_PLAN.md).
- 2026-07-30 | Today / Content | **Wave 2 Phase D.1 — `GET /today/day-facts`** | **LIVE** | Slot envelope: one `assemble_day_facts_v1` → natal_activations + domain_verdicts + glance_timeline + provenance. Interim `/domain-verdicts` + `/glance-timeline` = thin slices. FE `fetchDayFacts` once in GlanceAct; slots prefer parent payload. Superseded narrative gap closed by D.1b row above. [CONTRACT](./today/TODAY_WAVE2_CONTRACT_V1.md) · [PLAN D.1](./today/TODAY_WAVE2_EXECUTION_PLAN.md).
- 2026-07-30 | Web Guest / SEO audit | **Guest Story Surface P0 (item 11)** | **DONE (LIVE)** | Curl: landing dual CTAs · `/demo/today` SSR Theme/Focus/Practice/Memory · `/onboarding/invite` · pitch CTAs · Compat Profile bridge · guest-nav primary Today·Profile·Compatibility. Evening/day-2 = slice 2. Canon [audits/GUEST_STORY_SURFACE_P0_2026-07-30.md](./audits/GUEST_STORY_SURFACE_P0_2026-07-30.md).
- 2026-07-30 | Guest Story Continuity | **Slice 2 evening + day-2 Memory** | **DONE (FE)** | Soft close Получилось/Частично/Не получилось · First Today sticky evening · `today-zone-memory` stub→filled from Day Continuity v0 · demo Memory educational. Out of scope: server persist. Canon [audits/GUEST_STORY_CONTINUITY_SLICE2_2026-07-30.md](./audits/GUEST_STORY_CONTINUITY_SLICE2_2026-07-30.md).
- 2026-07-30 | Web Guest / SEO audit | **/today+/profile SSR pitch body** | **DONE (LIVE)** | Independent sandbox curl: pitch SSR above bailout on /today+/profile; «Собираем стабильное…» = 0. BAILOUT remains on client widgets only. Item 11 story surface → row above.
- 2026-07-31 | Today / ScreenFlow | **no-silent-fallback on acts 2–5 + Glance texture split** | **DONE (FE)** | Reading/Move/Response/Symbols: `data-fallback` + «Нет соединения.» / «Не удалось загрузить.» (not silent empty). Glance meta failure once; Symbols hides ritual gate + timeline under degrade. Glance texture = opposing_forces when why_arose is aspect-bank; Plot keeps full why. **Open:** sticky why_arose = B5 `ranked_drivers.fact_ru` join — generation SoT, needs Architecture impact (not FE polish).
- 2026-07-31 | Today / Generation | **Sticky Sun–Mars why_arose (B5 fact_ru)** | **OPEN** | Same «Связь Солнца и Марса…» across days from deterministic driver bank on normal `/today/contract` (no native LLM). FE only splits Glance short vs Plot full. Fix = regen/LLM gate or stop serving aspect-bank as lived why — Architecture impact required.
- 2026-07-31 | Today / ScreenFlow | **Screen scenario v3 (texture · plot · spheres · bugs)** | **LIVE** | Glance = why_arose texture + sphere tokens + inline nearest; Plot = conflict narrative; Reading = sphere cards; Move += color; Response − cross-sell; readingLead stub fixed; timeline labels body+aspect. Canon [TODAY_SCREEN_SCENARIO_V3](./today/TODAY_SCREEN_SCENARIO_V3.md). Hard-refresh.
- 2026-07-31 | Today / Glance | **Screen 0 compression (thesis · collapse · nearest)** | **SUPERSEDED → v3** | Compression was interim; v3 replaces equal-card strip with tokens + texture.
- 2026-07-31 | Practices | **P1 close-out: no mark-done bypass** | **LIVE** | Detail «Отметить как выполненное» removed — complete only via session check-in → «Сохранить…». Sequence step complete unchanged. Continue fixture asserts `?run=1`.
- 2026-07-31 | Today / Glance | **top_driver_v1 soft-day audit + open/friction contrast** | **DONE** | Live user2 4× open = real soft winners (`mars-trine-sun` / `moon-trine-jupiter` / `sun-sextile-moon`×2), `logic_source=top_driver_v1`; clustered-hard regression still `charged` on Mars square. Open→olive `#6b8f5a`, friction→rust `#b04a2e` for 2s scan.
- 2026-07-30 | Today / Content | **Wave 2 Phase D.4 — Move if/then from scenes** | **LIVE** | Move act shows `recommended_action` / `do_not` from primary (else first) day_scenario scene; omit when empty. No invent. Helper `pickMoveIfThenFromContract`.
- 2026-07-30 | Today / Glance | **Task #8 jargon FE shield + VerdictStrip valence punch** | **DONE (code→deploy)** | BE already experiential; FE scrubs «Венера: трин к Сатурн»; stronger valence bar/tint/sign; removed dead «Память о вчера» stub copy from composition (demo-only remains). Memory slot still filled-only.
- 2026-07-30 | Today / Content | **Wave 2 Phase D.3 — motion retrospective** | **CLOSED** | Decision: **revise Today-only**, do not promote app-wide. Proven: TapWidget attention/completed + reduced-motion; Glance live-now; Verdict idle. Backlog: hero/card/insight `today_ui_state` motion. Canon [TODAY_MOTION_PILOT_V1](./today/TODAY_MOTION_PILOT_V1.md). Next: D.4 optional.
- 2026-07-30 | Today / Glance | **nearest empty + rail → glance_timeline** | **DONE (code→deploy)** | Root: top ranks were biquintile without angle → 0 exact. Fix: quintile/biquintile angles + search ranks 1…12 until ≤3 timed. Rail loads real `glance_timeline` (no DEFAULT_TIMES). Contract §4 updated.
- 2026-07-30 | Today / Glance | **Сводка: identical-open collapse + kill fake rail timeline** | **DONE (code→deploy)** | 4× «открыто/Есть опора» = aspect-class collapse; BE domain-distinct soft/hard why; FE identical-why → unavailable. Rail «Таймлайн дня» used invented DEFAULT_TIMES + jargon titles — return [] until glance_timeline wire.
- 2026-07-30 | Today / Glance | **Сводка content: valence · nearest · teasers · no memory stub** | **DONE (code)** | Hide memory stub; silent-calm bank → «Не удалось загрузить.»; domain-distinct quiet why; VerdictStrip valence bar/sign; nearest empty honesty; teaser hooks.
- 2026-07-30 | Product UI | **ScreenFlow axis lock (x)** | **LIVE** | Today locks `TODAY_SCREEN_FLOW_AXIS=x`; deadzone 24px; overscroll contain. y remains on primitive for fixtures only. Evidence: Playwright harness x/y @390 + swipe deadzone. Canon [SCREEN_FLOW_V1 §2](./foundation/SCREEN_FLOW_V1.md) v1.2.
- 2026-07-30 | Product UI | **ScreenFlow Phase 2b — Reading/Move/Response** | **LIVE** | Split interim Personal bundle into 3 ScreenFlow steps via `actFilter`. ActNav: Чтение·Действие·Отклик. Canon [SCREEN_FLOW_V1 §4](./foundation/SCREEN_FLOW_V1.md) v1.1. Bundle `page-fe43e887cbee4689.js`. Tests: TodayProductScreenFlow indices + composition surface.
- 2026-07-30 | Product UI | **ScreenFlow V1 — proto + Today Glance-first** | **LIVE (redeployed)** | Was code-only: prod image lagged (Docker `npm run build` failed on TS; `tail` masked exit → stale `#today-act-` bundle). Fixed `showSymbols`/`tarotPickedId` types; rebuilt+force-recreate. Live chunk `page-bbb6669e810a4bf7.js` contains `today-screen-flow` + Glance. Hard-refresh to verify transform pager. Phase 2b = split personal; axis lock after real-device.
- 2026-07-30 | Today / Content | **Strip+Glance experiential labels (no jargon)** | **LIVE** | Shared `today_activation_copy_v1`: `why_short` + `label_short` from aspect class only — no planet/aspect names/degrees. Canon [TODAY_WAVE2_CONTRACT_V1 §3.3 §4](./today/TODAY_WAVE2_CONTRACT_V1.md). Restart clears 7m activation TTL.
- 2026-07-30 | Web Auth + Landing | **Landing hash-nav restore after Guest Story P0** | **LIVE** | Guest Story rewrite dropped `landingHashNav`; re-wired instant scrollTop + `<a>` hash clicks (no Next Link / no native smooth).
- 2026-07-30 | Today / Content | **VerdictStrip `why_short` jargon removal** | **SUPERSEDED → Strip+Glance bank** | Earlier strip-only fix folded into shared copy module with GlanceTimeline.
- 2026-07-30 | Web Guest / SEO audit | **Re-audit P0–P2 pack** | **DONE (LIVE)** | Owner curl confirmed: `/` landing+unique meta · `/today` pitch · `/profile` pitch · `/compatibility` guest · `/practices` SSR catalog · LK body · tarot «Три карты». P0/P1/P2 closed except item 11 (hierarchy).
- 2026-07-30 | Web Guest / SEO audit | **Guest shell SSR fix** | **DONE (FE)** | Live check: practice HTML still showed «Путник»+full nav. Cause: `guestShell = !authLoading && !isAuthenticated` → SSR authLoading=true → authed chrome. Fix: `guestShell = !isAuthenticated`. Redeploy required.
- 2026-07-30 | Web Guest / SEO audit | **P0–P2 public audit pack** | **DONE (FE)** | Guest `/today` value-first + showcase; guest shell (tarot/compat/practices, «Гость»); practice hard-404 + unique meta + transport≠not-found; robots/sitemap/noindex policy + segment titles; dual-nav unmount after hydrate; compatibility guest demo. Deploy needs `PUBLIC_WEB_URL` bake for OG. Tests: appNavConfig, publicSeoPolicy, fetchPracticeDetailServer, CompatibilityGuestDemo.
- 2026-07-30 | Web Guest / SEO audit | **P0 guest `/today` + shell** | **DONE (FE)** | Cold `/today`: value-first CTA (создать Today) + showcase, не login-only. Guest shell: nav = tarot/compatibility/practices; identity «Гость»; footer → onboarding; без «Путник» + полного меню. Tests: `appNavConfig`. SEO/a11y/compat demo — next.
- 2026-07-30 | Web Auth + Landing | **Plan closed (v7 + overflow)** | **DONE (LIVE)** | All 7 items closed: anchors, login RU/slots/network/429, mobile nav, section CTAs, themePanel overflow. Owner confirmed 1920; agent CDP confirmed 375/1366 after `7b29cd5`.
- 2026-07-30 | Web Auth + Landing | **Landing mobile overflow (#today themePanel)** | **DONE (FE)** | CDP QA 375/1366: `.themePanel` used content-box → padding blew past viewport (body scrollWidth 419@375 / 1434@1366). Fix `box-sizing:border-box; width/max-width:100%`. Mobile nav two-row visually confirmed @375. 1920 clean.
- 2026-07-30 | Web Auth + Landing | **Plan v7 closed (live)** | **DONE** | All 6 plan items confirmed on prod after `0dcf0aa` network fix. Residual: visual mobile/narrow + non-1920 clipping not eyeballed in agent session (CSS mobile layout confirmed earlier).
- 2026-07-30 | Web Auth + Landing | **Plan v7: login network error fix** | **DONE (FE)** | Broaden transport failure detection (any TypeError / AbortError → ApiError status 0); mapLoginFailure always shows «Не удалось подключиться»; avoid disabled password inputs + focus steal that wiped the error. 429/401 unchanged.
- 2026-07-30 | Web Auth + Landing | **Plan v5: mobile anchor nav** | **DONE (FE)** | Marketing nav always shows section anchors; mobile = logo+CTA row + horizontal scroll chips; desktop row unchanged. CTA `/tarot`/`/compatibility` already in prod bundle. Network/429 copy wired in auth mapLoginFailure (live 401 confirmed earlier).
- 2026-07-29 | Web Auth + Landing | **Landing screens from scenario (anchors)** | **DONE (FE)** | `PRODUCT_WEB_LANDING_SCREENS` Plan v4 order · each section `screen` + `data-landing-screen` · `min-height` 100dvh under sticky nav · scroll-snap proximity + scroll-padding. Redeploy for prod.
- 2026-07-29 | Web Auth + Landing | **Plan v4 SoT: all-anchor nav + login error polish** | **DONE (FE)** | Split `#try` → `#tarot/#compatibility/#practices`; top nav scrolls only; product via section CTA; guest `/#tarot`. Login: keep API 401 detail (fix EN Unauthorized overwrite); reserved error slots; RU map for network/429. No public JSON change.
- 2026-07-29 | Web Auth + Landing | **Login declutter + landing viewport sections** | **DONE (FE)** | `/auth`: removed left «После входа…» panel → form-only; per-field inline errors (empty / invalid email / invalid credentials) with red border. Landing: hero atmosphere bg · `#hero/#try/#today/#why/#cta` min-100dvh screens · anchor nav + scroll-spy. No public JSON / generation contract change.
- 2026-07-29 | Today / Content | **Wave 2 — transit body-id case mismatch** | **FIX (LIVE)** | `_calculate_transits` looked up `Sun`/`North Node`/`Ascendant` while astro chart emits `sun`/`north_node`/`rising` → 0 aspects → 4× calm «Без явного сигнала». Normalize via `index_chart_positions_by_label`. User2 now 50 activations.
- 2026-07-29 | Today / Content | **Wave 2 — ban invent-content transport fallback** | **FIX** | System rule (AGENTS + Wave2): on network fail show «Нет соединения.»; on degraded «Не удалось загрузить.» — never invent 4× calm / “нет сигнала” prose. BE degraded → `domain_verdicts=[]`; FE `orderDomainVerdicts` no fillers.
- 2026-07-29 | Today / Content | **Wave 2 VerdictStrip silent-calm hotfix** | **FIX (code)** | Live prod: Strip showed 4× «спокойно» / «Без явного сигнала». Root cause: (1) `get_personal_transit_service()` not awaited → AttributeError; (2) exception path `put_snapshot([])` then next hit returned `[], False` = silent calm. Fix: await + snapshot stores `degraded` + never cache exceptions. FE: no calm rows until fetch settles. Calib «27.07/24.08 compare» closed as N/A by product construction. Manual smoke after deploy.
- 2026-07-29 | Today / Content | **Wave 2 Phase C — GlanceTimeline** | **LIVE** | `GET /today/glance-timeline` from activations rank 1–3 + exact-time (30m samples + bisect). Act 2 slot; live-now «сейчас» (priority 4). Same pool as Strip. [PLAN C](./today/TODAY_WAVE2_EXECUTION_PLAN.md) · [CONTRACT §4](./today/TODAY_WAVE2_CONTRACT_V1.md).
- 2026-07-29 | Today / Content | **Wave 2 Phase B′ — activation SoT consolidation** | **DONE (code)** | Shared `compute_natal_activations` + 7m TTL snapshot; Strip + morning CE + day_scenario foundation same pool; FE `is_fallback` ≠ calm. Phase D still owns full `day_facts_v1` GET. Manual Act1/3 smoke pending. [PLAN B′](./today/TODAY_WAVE2_EXECUTION_PLAN.md).
- 2026-07-29 | Today / Content | **Wave 2 Phase B — VerdictStrip** | **LIVE** | `GET /today/domain-verdicts` + Act 1 strip (4 domains, `top_driver_v1`). Interim until Phase D `day_facts_v1`. No motion on strip. [PLAN](./today/TODAY_WAVE2_EXECUTION_PLAN.md) · [CONTRACT §3.3](./today/TODAY_WAVE2_CONTRACT_V1.md).
- 2026-07-29 | Today / Content | **Wave 2 Phase 0.5.2 CLOSED** | **DONE** | Full August 31d: domain **sum** freezes work (charged 29/31, 2 flips). **`top_driver_v1`** approved (work 8 / money 2 / rel 3 / energy 6 flips). Dictionary unchanged. Phase B soft-gate lifted. [CONTRACT §3.1c](./today/TODAY_WAVE2_CONTRACT_V1.md).
- 2026-07-29 | Today / Content | **Wave 2 Phase A — TapWidget** | **LIVE** | `POST /today/tap-widget/response` + `GET /today/accuracy-summary` + FE TapWidget. Unaffected by top-driver change.
- 2026-07-29 | Today / Content | **Wave 2 Phase 0.5 pass 2** | **SUPERSEDED → 0.5.2 CLOSED** | Dictionary approved earlier; consecutive August closed with aggregation model change (sum→top-driver).
- 2026-07-29 | Today / Content | **Wave 2 Phase 0.5 pass 1** | **FAILED → pass 2** | Manual `sphere_score_v0` on 8 igor dates: work avoid 8/8, money avoid 6/8. Slow dampen insufficient. Led to per-domain valence + descriptive dictionary.
- 2026-07-29 | Today / Content | **Wave 2 — day_facts_v1 contract + execution plan** | **CONTRACT LOCKED** | Single SoT `day_facts_v1` (slots = views). Order: Tap+accuracy → VerdictStrip → GlanceTimeline. Fixed 4 domains. Motion pilot = TapWidget only. Docs: [TODAY_WAVE2_EXECUTION_PLAN](./today/TODAY_WAVE2_EXECUTION_PLAN.md) · [TODAY_WAVE2_CONTRACT_V1](./today/TODAY_WAVE2_CONTRACT_V1.md) · [TODAY_MOTION_PILOT_V1](./today/TODAY_MOTION_PILOT_V1.md). Next: Phase A code + Architecture impact; Phase 0.5 pass 2 parallel.
- 2026-07-29 | Today / Layout | **Wave 1 — ActShell page scenario** | **LIVE (layout)** | Mobile-first 5-act stack via `TodayActShell` (full-bleed + one gutter); order plot → symbols → reading → move → bridges; dual always vertical; quiet dashboard header; reserved Wave 2 slots `VerdictStrip` / `GlanceTimeline` / `TapWidget` (stubs). CI: Jest act-order + Playwright screenshots 390×844 & 768 (`e2e/today-act-shell-visual.spec.ts`). **Not** “готовым Today” — content/IA pivot is Wave 2.
- 2026-07-29 | Today / Content | **Wave 2 — practical IA in ActShell slots** | **SUPERSEDED → CONTRACT LOCKED** | Replaced by day_facts_v1 contract + phased plan (Tap → Verdict → Glance).
- 2026-07-08 | Web Today narrative | client-side same-day dedup (sessionStorage) | DONE | `fetchTodayNarrativeCached` в `todayNarrativeCache.ts`: ключ date/surface/parent/topic/depth/ritual_fp; hit → без POST; in-flight coalesce; `force` после ритуала. Паритет iOS `cachedNarrative` + переживает remount вкладки. Today page + LifeSpheres deepen.
- 2026-07-08 | Today narrative cache | fix «Сегодня собирается бесконечно» — same-day reuse | DONE | `_load_narrative_cache` / `_load_funnel_step_cache`: `day_context_sha256` = предпочтение свежести, не жёсткий гейт. Причина: `get_daily_fusion_index` дрейфует от внутридневной активности пользователя → каждый заход был cache-miss + повтор LLM-воронки. Теперь переиспользуется свежий лог со стабильным ключом (date/surface/ritual_fp/intent_fp/tier/depth/snapshot), как `day_story_v1`. AMLL: `reason=GATE:cache_hit:same_day_reuse`. Backend-only, паритет web/iOS/Android через тот же REST. См. `DAY_CONTEXT_V0.md` §Промпты narrative.
- 2026-07-08 | Web product UI | CSS convergence: domain layouts → productPageLayout | IN PROGRESS | `todayWebV2` / `tarotWebV2` / `compatibilityWebV2` удалены; Today·Tarot·Compat hub импортируют `productPageLayout.module.css`.
- 2026-07-08 | Web product UI | habits / asceticisms / maps / horoscope → ProductPageScreen | IN PROGRESS | `/habits`, `/asceticisms`, `/asceticisms/tracker`, `/maps/*` (7), `/horoscope/today` + `[sign]` — orbit-page / todayflow-serene убраны; v2 header + pl.panel + toolbar.
- 2026-07-08 | Web product UI | cycle / journal / affirmations / discover / library / lunar → ProductPageScreen | IN PROGRESS | `/cycle`, `/journal`, `/affirmations`, `/affirmations/tracker`, `/discover`, `/library`, `/lunar/today` — orbit-page убран; loading/guest через ProductPageScreen; inner content частично legacyHost.
- 2026-07-08 | Web product UI | questions / numerology / compatibility sub-routes → ProductPageScreen | IN PROGRESS | `/questions/*` (6), `/numerology/*` (7), `/compatibility/analyze`, `/compatibility/signs`, `/compatibility/birthdates` + result pages — orbit-page убран; QuestionEntryCard / compat-desktop / calc forms в legacyHost.
- 2026-07-08 | Web product UI | calendar / profile-summary / subscriptions / discover pattern → ProductPageScreen | IN PROGRESS | `/calendar`, `/profile-summary`, `/subscriptions`, `/discover/pattern/[axis_id]` — orbit-page и hero images убраны; v2 header + pl.panel + legacyHost.
- 2026-07-08 | Web product UI | challenges / reports / help / tarot cards → ProductPageScreen | IN PROGRESS | `/challenges`, `/challenges/[id]`, `/reports/full`, `/reports/thematic`, `/reports/thematic/[theme]`, `/help`, `/help/*`, `/tarot/cards/[slug]` — orbit-page и hero images убраны; metadata help → layout.tsx; inner forms/viewer в legacyHost.
- 2026-07-07 | Web product UI | Today dashboard v2 aligned to Profile reference | IN PROGRESS | Today dashboard на `productPageLayout` + `productV2Surface` tokens; wide canvas `mainWide`; cards/type/spacing match profile v2.
- 2026-08-04 | Tarot | **Answer-first composition** | **DONE** | UI: answer → step → A/B → confidence → why collapsed. Prompt `tarot-interpretation-v1.10` + gate `user_facing_jargon`. Canon SCREEN_CONTRACTS §6.5 · ENGINE §4.1/§5. No new public fields.
- 2026-07-26 | Tarot | **Architecture Frozen / Editorial Phase** | **ACTIVE** | Owner: full freeze lift declined after live r3 12/12. Allow: KB · prompt · editorial · eval · reliability. New layers/contracts/pipeline → RFC. [note](./audits/TAROT_STACK_EDITORIAL_PHASE_2026-07-26.md). Next: human Golden Eval v2.
- 2026-07-26 | Tarot | **Golden Eval live #3 + reliability** | **DONE (12/12)** | Timeout/background fix deployed · commit `da03d22` · **12/12 LLM**. Audit [TAROT_GOLDEN_EVAL_LIVE_2026-07-26_r3](./audits/TAROT_GOLDEN_EVAL_LIVE_2026-07-26_r3.md).
- 2026-07-26 | Tarot | **Golden Eval live #2** | **DONE (gate green)** | 12/12 pack · **11/12 LLM** · anti-sameness OK · `freeze_lift_ready=true`. Fail: `choice_work_leave_or_stay` (`too_long` / quality). Audit [TAROT_GOLDEN_EVAL_LIVE_2026-07-26](./audits/TAROT_GOLDEN_EVAL_LIVE_2026-07-26.md). Next: owner freeze-lift · Q3.
- 2026-07-25 | Tarot | **Interpretation Stack v1 FROZEN (docs)** | **SUPERSEDED → Editorial Phase** | Hard freeze until Golden Eval; now Architecture Frozen / Editorial Phase after owner accept 2026-07-26.
- 2026-07-25 | Tarot | **Knowledge Base v1** | **DONE (data+wire)** | 78 semantic cards → Context Pack (`inner_conflict`, domains, reverse trap, amplify, intensify/soften in-spread). Prompt `tarot-interpretation-v1.2`. Canon [TAROT_KNOWLEDGE_BASE_V1](./tarot/TAROT_KNOWLEDGE_BASE_V1.md). Public contract unchanged. Next: Position Semantics · live text scoring · editorial deepen.
- 2026-07-25 | Tarot | **Question Ontology v1** | **DONE (data+wire)** | question_type/domain/intent/horizon → pack instructions. Prompt v1.4 (single author). Integration set 12. Canon principle: LLM = one story. [TAROT_QUESTION_ONTOLOGY_V1](./tarot/TAROT_QUESTION_ONTOLOGY_V1.md). Public contract unchanged. Next: minors deepen → golden eval.
- 2026-07-25 | Tarot | **Position Semantics v1** | **DONE (data+wire)** | Role library → pack `position_semantics` (purpose / answers_question / extract / do_not / result_type). Prompt `tarot-interpretation-v1.3`. Canon [TAROT_POSITION_SEMANTICS_V1](./tarot/TAROT_POSITION_SEMANTICS_V1.md). Public contract unchanged. Next: Question Ontology · minors deepen · golden eval.
- 2026-07-25 | Tarot | **Architecture freeze + content backlog** | **SUPERSEDED by Stack v1 FROZEN** | See Interpretation Stack v1 FROZEN (docs). Next: Q1 → Dataset → Eval → Q3.
- 2026-07-25 | Tarot | **Interpretation Engine pack+gates v1.1** | **DONE** | Rich meaning ranges · domain profile · prompt bans · quality gates · honest fallback · scenario fixture + `scripts/tarot_interpretation_live_eval.py`. CE scrub commits `f2ac8c2` / `8c7bd2e`.
- 2026-07-25 | Tarot | **Interpretation Engine v1.1 LLM author** | **DONE (web+BE)** | Architecture: Context Pack → LLM → validation → UI. Templates demoted to pack facts / thin fallback. Canon [TAROT_INTERPRETATION_ENGINE_V1](./tarot/TAROT_INTERPRETATION_ENGINE_V1.md). UI: symbols / question story / answer / next step.
- 2026-07-25 | Tarot | **Interpretation Engine v1** | **SUPERSEDED by v1.1** | Full-deck resolve; ban «Аркан»; unresolved gate; first template path replaced by LLM author.
- 2026-07-21 | Today / Story | PR-3 day_story_v1 explainable slice | **IN PROGRESS** | Backend trace+gates; FE domain honesty; soft why from claims; strengthen from practice_recommendation only. [PR3_TODAY_PRODUCTION_SURFACE.md](./archive/PR3_TODAY_PRODUCTION_SURFACE.md)
- 2026-07-21 | Web product UI | PR-3 Today Production Surface | **IN PROGRESS** | Composition = single reading line + optional soft why + optional one strengthen tool. Block gate: why / 10–20s / action.
- 2026-07-21 | Profile | PR-4 Profile Canon (slice 4.1) | **ACCEPTED / CLOSED** | Who-you-are surface; umbrella applied; day/maps out; natal stays on Profile as source (person first). Next: [audits/PROFILE_AS_SOURCE_CONSUMPTION_AUDIT.md](./audits/PROFILE_AS_SOURCE_CONSUMPTION_AUDIT.md). [PR4_PROFILE_CANON.md](./archive/PR4_PROFILE_CANON.md)
- 2026-07-22 | Product | **FULL_USER_PATH = SoT маршрута (после A–E)** | **ACTIVE** | [FULL_USER_PATH_CANON_V1](./audits/FULL_USER_PATH_CANON_V1.md) living again: Preview→Save→Claim→Profile · magic · dual 1A · natal_facts · max_profiles=3. [USER_JOURNEY_CANON](./USER_JOURNEY_CANON.md) → pointer. Next: сверка живого кода экран за экраном по §1.3 / §16.1.
- 2026-07-22 | Product | **Generation Contracts = ядро продукта** | **ACTIVE / DRAFT** | SoT: [PRODUCT_GENERATION_CONTRACTS.md](./PRODUCT_GENERATION_CONTRACTS.md) v0.2 — Contract (schemas · deps · Execution Rules · Quality Rules) ⊕ Implementations (промпты = IP per model). Next: `natal_facts` + `personality` schemas.
- 2026-07-22 | Product | **Capability Contracts (оркестратор)** | **ACTIVE / DRAFT** | SoT: [PRODUCT_CAPABILITY_CONTRACTS.md](./PRODUCT_CAPABILITY_CONTRACTS.md) — TodayFlow не автор астро-расчётов; L1 base / L2 natal / L3 insight; `available_input` · `calculated_facts` · `unavailable_facts` · `allowed_output`. Next: выбрать внешний API-провайдер; JSON Schema; Capability Resolver.
- 2026-07-22 | Product | **Data Intake = ровно 2 способа** | **ACTIVE / DRAFT** | SoT: [PRODUCT_DATA_INTAKE.md](./PRODUCT_DATA_INTAKE.md) — 1A Compat / 1B свой профиль → email bind · 2 добавить профиль. Профили durable; compat по profile ids. **Δ:** public compat сейчас ephemeral. Freeze новых birth-форм вне 1A/1B/2.
- 2026-07-22 | Product | **Availability Matrix = APPROVED (Profile)** | **ACTIVE** | [PRODUCT_AVAILABILITY_MATRIX.md](./PRODUCT_AVAILABILITY_MATRIX.md) v1.0 — слой 1 field→copy · Free=L1+L2 / Trial=Paid L3 · Guest без `/profile` · слоты 3.1 + contract_ids. **Freeze:** не менять Profile/Today IA вне строк 3.1. Next: Capability Resolver + `natal_facts`→`personality` wiring по слотам.
- 2026-07-24 | Design / Web | **Mood/theme layer repair + premium pass 1** | **DONE** | Mood CSS был мёртв (class-vs-module selectors, 5 файлов) · 3 расходящихся `isFirstDay` → общий `resolveIsFirstDay()` · hydration mismatch `data-theme/mood` → imperative ref+effect · dark-варианты `surfaceHero/Panel/Glass/chip` (light-on-light hero на всех product-страницах) · `orbit-button-secondary` dark · fonts → `next/font` self-host (было 7 render-blocking `@import`) · vendor.css-as-script fix в splitChunks · ritual CTA = кнопка · цвет дня + hex swatch · MotionReveal на Today секции · natal wheel U+FE0E (эмодзи-глифы) · compat layer-card overflow · **next:** natal wheel mobile redesign · touch tooltips · emoji→иконки в «Что формирует день»
- 2026-07-21 | Profile | Patterns GENERATION_GATE | **DONE** | Skip `profile.patterns.v1` when `recurring_patterns` not allowed by source_depth; empty patterns in partial Snapshot. Identity/styles/spheres/Voice unchanged.
- 2026-07-21 | Profile | Capture Case A/B report | **DONE** | A: patterns ineligible but ran; B: living used in patterns → Snapshot/UI. Next slice: GENERATION_GATE skip patterns. [PROFILE_CAPTURE_CASE_AB_REPORT.md](./audits/PROFILE_CAPTURE_CASE_AB_REPORT.md)
- 2026-07-21 | Product | Voice: person not system | **ACTIVE** | UI never describes system state; missing CTA = absence · unlock · valued action. [TODAYFLOW_VOICE_CANON.md](./content/TODAYFLOW_VOICE_CANON.md) §0.05–§0.06 · [UNDERSTANDING_PROGRESS_AND_DEPTH_CANON.md](./UNDERSTANDING_PROGRESS_AND_DEPTH_CANON.md)
- 2026-07-21 | Profile | Profile E2E architecture principle | **ACTIVE** | Model = contract executor; block_eligibility before prompt; architectural defects only. [PROFILE_E2E_RECONSTRUCTION.md](profile/PROFILE_E2E_RECONSTRUCTION.md) · [PROFILE_E2E_BLOCK_PASSPORT_TEMPLATE.md](./audits/PROFILE_E2E_BLOCK_PASSPORT_TEMPLATE.md)
- 2026-07-21 | Profile | Profile Production-Faithful Capture Pack | **ACTIVE** | Infra only: capture + eligibility vs ran + Case A/B. No prompt/UI/contract product fixes until packs. [PROFILE_PRODUCTION_CAPTURE_PACK.md](./audits/PROFILE_PRODUCTION_CAPTURE_PACK.md)
- 2026-07-21 | Profile | Profile End-to-End Reconstruction | **ACTIVE** | Architecture-first: passport → gate → prompt → accept → publish. Next: run capture packs, classify defects without MODEL. [PROFILE_E2E_RECONSTRUCTION.md](profile/PROFILE_E2E_RECONSTRUCTION.md)
- 2026-07-21 | Profile | Profile as source (post–PR-4) | **NEXT** | Wire Experiences to Snapshot after E2E map; kill parallel SoI. [audits/PROFILE_AS_SOURCE_CONSUMPTION_AUDIT.md](./audits/PROFILE_AS_SOURCE_CONSUMPTION_AUDIT.md)
- 2026-07-21 | Product | Understanding Progress & Depth canon | **ACCEPTED** | Progress = quality of understanding. Never empty Profile; missing field → what opens + why; subscription = depth not chopped blocks; trial = full experience. [UNDERSTANDING_PROGRESS_AND_DEPTH_CANON.md](./UNDERSTANDING_PROGRESS_AND_DEPTH_CANON.md)
- 2026-07-21 | Content | Voice: TodayFlow не говорит о себе | **ACCEPTED** | Ban «мы/система/ИИ/алгоритм» как субъект; факт в центре. [TODAYFLOW_VOICE_CANON.md](./content/TODAYFLOW_VOICE_CANON.md) §0
- 2026-07-21 | Web product UI | PR-2 App Shell (rail honesty) | **ACCEPTED / CLOSED** | Канон: [PR2_APP_SHELL.md](./PR2_APP_SHELL.md). Один `ProductWebAppShell`; rail = данные; без reserved empty track; Profile структурный эталон. К shell — только багфиксы. Today content → PR-3.
- 2026-07-08 | Web product UI | Product Page Standard v1 (единый продукт) | **ACCEPTED** | Один shell (`ProductWebShellLayout`), один page wrapper (`ProductPageScreen`), tokens (`productV2Surface`) + grids (`productPageLayout`). Запрет: orbit-page / custom hero / локальные карточки на in-app routes. Миграция: Today·Profile·Practices·Tarot·Compat hub — partial; Tracking·Weekly·Account — partial; ~40+ orbit routes — backlog. См. PR-2.
- 2026-07-08 | Web product UI | Account profiles/subscriptions/reports → ProductPageScreen | IN PROGRESS | `/account/profiles`, `/account/subscriptions`, `/account/reports` — orbit hero removed; v2 header + legacyHost panels.
- 2026-07-07 | Web product UI | Today composition embed + full=1 product shell | IN PROGRESS | `rootWebEmbed`/`sectionWebEmbed` v2 panels; `/today?full=1` → `TodayWebDashboard layout=ritual` (unified nav, no orbit main).
- 2026-07-07 | Web product UI | Tarot + Compatibility v2 aligned to Profile reference | IN PROGRESS | `productPageLayout` domain blocks (tarot spreads, compat mode/pair); `mainWide` + `productWebContentV2`; Compatibility hub on v2 tokens.
- 2026-07-07 | Web product UI | Profile v2 as visual reference + productV2Surface tokens | IN PROGRESS | `productV2Surface.module.css` (cards, type, gaps); Practices v2 + history aligned; user chip removed from practices top bar (identity in sidebar only). Next: tracking/account shells, Today composition slot.
- 2026-07-05 | Web Today single voice | legacy TodayRitualFlow deduped | DONE | `?full=1` path uses `usesDayStorySingleVoice`: no guide overlay, no ritual POST, contract do/avoid/why/evening; shared helpers in `todayContractMapper.ts`.
- 2026-07-05 | Web Today single voice | day_story only on composition surface | DONE | Skip POST `/today/narrative` when `contract.day_story`; no guide/spheres/evening overlay; dashboard chrome from day_story; `usesDayStorySingleVoice` policy + tests.
- 2026-07-05 | Phase 2 client parity | Web Profile/Tarot + iOS composition + Android ritual | DONE | Web: Quick Map reads `profile_contract_v1`; Tarot result reads `tarot_answer_v1`; Today story/spine from `contract.day_story` (`todayContractMapper.ts`). iOS: `TodayCompositionSurfaceView` default. Android: `TodayCompositionScreen` + `DayEngagementStore` + spine FSM ritual flow.
- 2026-07-05 | Phase 2 contracts | profile_contract_v1 + tarot_answer_v1 + mobile contract parity | DONE | Profile: `profile_contract_v1.py` replaces monolith interpreter path in `CoreProfileService` (legacy `interpretation` shim); Tarot: `tarot_answer_v1` in `POST /tarot/spread/context`; Today: `day_story` on `GET /today/contract`; iOS: `TodayContractV1` fetch + ritual hero from contract; Android: `GET today/contract` + `TodayContractScreen` tab; pytest `test_phase2_contracts_v1.py`.
- 2026-07-05 | Backend / PIM | DE-5 behavioral signals v0.1 (post-validation) | DONE | `meaning_surface_patterns_v0`: proximity (`sphere_feedback`), guidance_ask, practices, tarot_deepen → `DayContext.behavior_patterns`, CUM `behavioral_patterns` + `current_state.ritual_proximity_*`, derived knowledge hypotheses; pytest extended.
- 2026-07-05 | Backend / AMLL | Today narrative AMLL Gate v1 wired | DONE | `today_narrative_llm_gate_v1`: cache_hit/reuse/template/call_llm/blocked; `build_today_narrative` logs `amll_gate` + `gate_decision`; skip LLM on template; orchestration trace; pytest `test_today_narrative_llm_gate_v1.py`.
- 2026-07-05 | Backend / PIM | DE-5 v0.2 P1: honest_step + day_promise + guidance themes | DONE | `top_honest_step_ids`, `day_promise_sets`, `top_guidance_lanes`/`top_guidance_themes` (keyword semantic, no LLM); CUM `active_themes` merges head_topic + guidance; `current_state.honest_step_id`; `behavioral_patterns.works` day_promise≥2 / honest_step≥2; derived hypotheses; `learning_slim.today_surface_patterns` expanded; pattern gate threshold → KASP default ≥3/14d (product TBD).
- 2026-07-03 | Backend | GE-1 v0.4: Guidance + Compatibility facades | DONE | `run_guidance_answer_pipeline`, `run_compatibility_dynamics_pipeline`; orchestration в guidance/compatibility logs; `funnel_step_handoffs`, `semantic_quality` trace; `api/questions.py`, `api/compatibility.py`; pytest `test_generation_orchestrator.py`.
- 2026-07-03 | Backend Today | GE-1 v0.3: orchestration ↔ DE-13 funnel | DONE | `ORCHESTRATOR_VERSION` 0.4.0; `reasoning_trace.day_model`; `attach_narrative_outcome_to_orchestration` (funnel/monolith, child chain); guide merge_pass plan funnel + `guide_contract_v2`; pytest `test_generation_orchestrator.py`.
- 2026-07-03 | Web + Backend | Tarot result: question-first reading (не энциклопедия) | DONE | `tarot_reading_synthesis.py`; result surface: главный ответ → история → 3 инсайта → 1 шаг сегодня → follow-up chips; RU-only copy; event `tarot_reading_follow_up`; убраны spread line / card list / resonance ○○○ на `/tarot/result`.
- 2026-07-03 | Backend | Tarot synthesis: insight bundles (не биты карт) | DONE | Ответ на вопрос; единая история; конкретные инсайты; мудрый собеседник; chips «Что сейчас кажется самым важным?».
- 2026-07-02 | iOS | Tarot Question-First funnel + ritual v2 | DONE | `TarotQuestionFlowCanon`, `TarotQuestionFlowView`, `TarotSpreadRitualView`; events `tarot_session_started`…`tarot_reading_resonance`; `/tarot` fullScreenCover.
- 2026-07-02 | Web + iOS | Tarot Phase C: journey + Today deepen bridge | DONE | `tarotJourneyStore`, `/tarot/journey`, anchor в ritual, CTA «Исследовать глубже» (Today + card-of-day), `tarot_deepen_started`; iOS: `TarotHubView` по `/tarot`, reading v2 DTO.
- 2026-07-02 | Web + Backend | Tarot Phase B: synthesis contract + resonance + routes | DONE | `TarotSpreadReading` + `generation_log_id`; result surface: why / 3 today / self-Q / ○○○ / Today·goal·practice; events `tarot_reading_resonance`, `tarot_spread_done`, `first_synthesis_viewed`.
- 2026-07-02 | Product + Web | Tarot Question-First canon §6.4–§6.8 + Phase A funnel | DONE | `SCREEN_CONTRACTS_V1`; `tarotQuestionFlowCanon.ts`, `TarotQuestionFlow`, `/tarot/spread/[spreadId]`; events `tarot_session_started`, `tarot_question_domain_selected`, `tarot_question_refined`, `tarot_spread_selected`, `tarot_question_submitted`.
- 2026-02-15 | Product | Created unified execution tracker | DONE | This file initialized as canonical plan.
- 2026-02-15 | Backend | Added Core Profile Engine service | DONE | New service assembles natal + numerology + baseline context.
- 2026-02-15 | Backend API | Added `/account/core-profile` endpoint | DONE | Unified profile contract now available for UI and other modules.
- 2026-02-15 | Frontend Today | Connected core profile contract to `/today` | DONE | Added "Ядро профиля" card and missing-fields visibility.
- 2026-02-15 | Backend Day Flow | Added interpretation orchestrator baseline | DONE | `day-flow` now returns consistency block built from core profile + day context.
- 2026-02-15 | Backend APIs | Refactored key personalization endpoints to core context | DONE | `today`, `morning-ritual`, `numerology/daily/explain` now include unified profile/consistency payload.
- 2026-02-15 | Backend Tests | Added integration consistency suite | DONE | New tests in `backend/tests/integration/test_core_profile_consistency.py` (execution pending env with pytest).
- 2026-02-15 | Frontend IA | Normalized top navigation to 5 sections | DONE | Primary nav now: Today, Profile, Forecast, Tarot&Guidance, Growth.
- 2026-02-15 | Frontend Routing | Added IA hub aliases | DONE | Added `/profile`, `/forecast`, `/guidance`, `/growth` redirects to existing module roots.
- 2026-02-15 | Frontend IA | Synced footer navigation with 5-section model | DONE | Footer now reinforces same top-level IA instead of old fragmented links.
- 2026-02-15 | Frontend PWA | Disabled SW registration for localhost | DONE | Prevents local RSC route conflicts/flicker during testing in production-mode localhost.
- 2026-02-15 | Frontend Routing | Updated legacy `/app` redirect | DONE | `/app` now routes directly to `/today` instead of heavy dashboard hop.
- 2026-02-15 | Frontend Today | Added return-cadence CTA block | DONE | New "Ритм возврата" section guides morning/day/evening return behavior.
- 2026-02-15 | Frontend Today | Removed legacy duplicate sections and stale anchors | DONE | Removed "Маршрут дня", refreshed stale labels/copies, replaced hash anchors with `?slot=` routing.
- 2026-02-15 | Frontend Routing | Migrated old Today anchor links across modules | DONE | Updated key links in numerology/natal flows and ritual redirects to slot-based navigation.
- 2026-02-15 | Frontend Today | Applied visual cohesion pass | DONE | Added atmospheric canvas background, unified chip style, and standardized Morning/Day/Evening panel design.
- 2026-02-15 | Frontend Forecast | Built unified forecast workspace with filters | DONE | Added domain/date filters + personalized overlay from `core_profile` and `day-flow` consistency.
- 2026-02-15 | Backend Compatibility | Added deterministic sign-to-sign endpoint | DONE | New `/compatibility/signs` returns static report, score, free/paid text depth, and optional personalized overlay.
- 2026-02-15 | Frontend Compatibility | Connected signs result to backend API | DONE | Removed placeholder result and now render static matrix + personalized layer + paywall depth logic.
- 2026-02-15 | Backend Tarot | Added spread context endpoint | DONE | New `/tarot/spread/context` returns spread + `core_profile` + `consistency`.
- 2026-02-15 | Frontend Tarot | Connected one-card spread to shared context | DONE | `one-card` now consumes `/tarot/spread/context` and shows aligned focus/do/avoid guidance.
- 2026-02-15 | Backend Today | Added rewards snapshot to `/today` | DONE | Added rewards domain payload: streaks (daily/weekly/habit/ascetic/tarot), archetype level, seals, scores, evolution index, milestones.
- 2026-02-15 | Frontend Today | Switched rewards card to backend domain model | DONE | `/today` now renders archetype/evolution/seals/milestones from backend rewards payload instead of local-only reward mock.
- 2026-02-15 | Frontend Profile | Replaced `/profile` redirect with profile hub | DONE | New profile page now shows core profile summary + rewards contour (archetype, evolution index, streaks, seals, milestones).
- 2026-02-15 | Frontend Practices | Added rewards feedback on completion | DONE | Practice completion screen now loads `/today` rewards snapshot and shows post-completion archetype/evolution/streak/milestone reinforcement.
- 2026-02-15 | Frontend Design System | Added shared rewards DTO + reusable contour component | DONE | Introduced `src/lib/rewards.ts` and `src/components/rewards/RewardsContourCard.tsx` to remove duplicated reward UI logic.
- 2026-02-15 | Frontend Design System | Locked reward visual tokens in global theme | DONE | Added reward-specific tokens in `globals.css` (`--orbit-reward-*`) and shared card surface class for consistent rendering.
- 2026-02-15 | Frontend Today/Profile/Practices | Unified rewards presentation layer | DONE | `/today`, `/profile`, and `/practices/[id]` now render a common rewards component for consistent look and behavior.
- 2026-02-15 | Frontend Design System | Added unified glyph + tarot cover primitives | DONE | Added `SectionGlyph` and `TarotCover` components and applied them to `/today`, `/tarot`, and `/tarot/spread/one-card`.
- 2026-02-15 | Performance Today | Removed duplicated heavy API calls from `/today` | DONE | Frontend no longer performs extra `/morning-ritual/today` and `/account/core-profile` calls after loading `/today`; consumes payload from `/today` response directly.
- 2026-02-15 | Backend Morning Flow | Added fast path for morning ritual in daily cycle | DONE | `/today` now requests `get_morning_ritual(..., fast_mode=True)` to avoid expensive AI generation on page-open while preserving core guidance.
- 2026-02-15 | Backend Day Flow | Enabled lightweight mode by default | DONE | `GET /day-flow` now defaults to `fast=true`, using editorial affirmations instead of per-request AI generation for UI overlays.
- 2026-02-15 | Backend Core Profile | Added in-process TTL cache for stable core payload | DONE | `CoreProfileService` now caches built profile payload by user/profile fingerprint to reduce repeated recomputation and stabilize response latency.
- 2026-02-15 | Backend Quality Gate | Strengthened semantic checks for daily forecasts | DONE | `quality_gate` now rejects template/dead phrasing, duplicate lines, low-information blocks, and micro-actions without explicit action verbs.
- 2026-02-15 | Backend AI Generation | Added semantic validation + grounded fallback blocks | DONE | `ai_client` now validates LLM output for meaning/actionability and replaces weak output with context-aware fallback text.
- 2026-02-15 | Backend Personal Texts | Hardened affirmations/tarot/numerology content quality | DONE | Added anti-template prompt constraints, output sanitization, and meaningful deterministic fallbacks in explainers/generator.
- 2026-02-15 | Backend Morning Ritual | Added quality validation for daily recommendations payload | DONE | LLM recommendations now pass semantic checks before response; invalid payloads use practical fallback.
- 2026-02-15 | Backend Tests | Added text quality regression tests | DONE | New tests in `backend/tests/test_text_quality.py` cover dead-pattern rejection, action checks, and duplicate-line blocking in forecast gate.
- 2026-02-15 | Backend Core Profile | Added persistent core profile snapshots in DB | DONE | New `core_profile_snapshots` storage (migration + model) and `CoreProfileService` now reuses frozen payload by `user_id + profile_hash`, rebuilding only on input changes.
- 2026-02-15 | Backend Core Setup | Added atomic core setup endpoint | DONE | New `POST /account/core-setup` updates name + primary astro profile, invalidates natal cache for changed profile, computes/saves numerology, and returns refreshed `core_profile`.
- 2026-02-15 | Frontend Dashboard | Fixed numerology name source | DONE | `useDashboardData` now uses real user name from `/account/profile` for `/numerology/name` instead of `AstroProfile.label`, preventing wrong core numerology.
- 2026-02-15 | Frontend Profile | Added unified core setup form | DONE | `/profile` now includes a single "Настройка ядра" form bound to `POST /account/core-setup` and redirects to `/today` after successful save without extra hydration calls.
- 2026-02-15 | Frontend Calendar | Fixed broken JSX in month layout | DONE | Restored valid `div/aside` structure in `/calendar` month view; resolved lint/build failures and return route to green build state.
- 2026-02-15 | Frontend Calendar | Added interactive selected-day side panel | DONE | `/calendar` month view now supports date selection with actionable side panel (events, notes, cycle, tracker) instead of passive cells only.
- 2026-02-15 | Frontend Tracking Calendar | Replaced static streak visuals with progress mechanics | DONE | Added per-activity progress rings (completion %), streak milestone progress (7/21/40/90/180/365), and “days to next milestone” indicators.
- 2026-02-15 | Frontend Calendar UX | Closed dead controls on `/calendar` | DONE | Added real content for `day` and `week` modes so mode buttons no longer switch to empty states.
- 2026-02-15 | Frontend Calendar Routing | Connected day deep-link between calendar pages | DONE | `/tracking/calendar` now reads `?date=YYYY-MM-DD` and focuses selected/current date from organizer deeplink.
- 2026-02-15 | Frontend Routing Audit | Closed unresolved route links across app | DONE | Added alias pages for `/login`, `/signup`, `/account/subscription`, `/journal/all`; added legal pages `/terms`, `/privacy`; fixed subscription links in billing success.
- 2026-02-15 | Frontend Today UX | Fixed no-op CTA behavior in daily engine | DONE | `Today` slot actions now open sections directly (morning/day/evening), next-action CTA handles slot navigation interactively, morning refresh has visible loading state, and card-of-day has explicit open actions.
- 2026-02-15 | Frontend Auth Redirects | Preserved query context through auth aliases | DONE | `/login` and `/signup` aliases now forward all query params to `/auth` (including `redirect`) instead of dropping user context.
- 2026-02-15 | Frontend Billing Flow | Fixed malformed unauth redirect URL | DONE | `/billing/success` now encodes `redirect` + optional `session_id` correctly when sending user to login flow.
- 2026-02-15 | Frontend Checkout Flow | Fixed redirect parameter encoding | DONE | `/checkout` now encodes redirect target when routing unauth users to signup/login path.
- 2026-02-15 | Frontend Auth Flow | Enabled return-to-origin after login/signup | DONE | `/auth` now reads and validates `redirect` query and navigates users back to the originating route after successful auth instead of always forcing `/today`.
- 2026-02-15 | Frontend Checkout UX | Removed blocking stub alert flow | DONE | Replaced checkout `alert` no-op with explicit redirect to `/pricing?notice=checkout_unavailable` and added visible explanatory banner on pricing page.
- 2026-02-15 | Frontend Tarot | Removed mock draw logic from three-card spread | DONE | `/tarot/spread/three-cards` now uses real `/tarot/spread/context` response, including aligned focus/do/avoid consistency block.
- 2026-02-15 | Frontend Tarot | Removed mock result generator | DONE | `/tarot/result` now builds result from live `/tarot/spread/context` using `spread` param instead of synthetic card placeholders.
- 2026-02-15 | Frontend Stability | Hardened array handling on critical pages | DONE | Added normalization guards for API arrays in `/today`, `/reports/thematic/[theme]`, and `/account/compatibility` to prevent `.find is not a function` runtime crashes on malformed payloads.
- 2026-02-15 | Frontend Compatibility | Removed mock delay and connected birthdate result to live sign matrix | DONE | `/compatibility/birthdates/result` now derives zodiac signs from dates and calls `/compatibility/signs`; removed synthetic timeout payload.
- 2026-02-15 | Frontend Lunar | Connected lunar page to real celestial endpoint | DONE | `/lunar/today` now reads live `/celestial/moon-phase` data (current phase, themes, guidance, next phase) instead of placeholder response.
- 2026-02-15 | Frontend Horoscope | Removed synthetic network delay on sign page | DONE | `/horoscope/today/[sign]` now renders deterministic sign-specific guidance immediately without artificial `setTimeout` loading.
- 2026-02-15 | Frontend Assets | Patched missing local image placeholders | DONE | Added `/images/Diary.png`, `/images/journal.png`, `/images/self-discovery.png` to prevent Next Image 400 errors from broken local sources.
- 2026-02-15 | Frontend Numerology | Replaced generic result mock with endpoint-backed logic | DONE | `/numerology/result` now resolves by `type` via real numerology endpoints (`/life-path`, `/name`, `/daily`, `/personal-year`) and removed timeout mock.
- 2026-02-15 | Frontend UX Consistency | Replaced blocking alerts with toast feedback across modules | DONE | Removed `alert(...)` from `today`, `dashboard`, `calendar`, `tracking/*`, `journal`, `cycle`, `habits`, `challenges`, `generate/forecast`, and tarot share flows; unified error/info/success feedback via `ToastProvider`.
- 2026-03-25 | Product Canon | Fixed core product model | DONE | Added `CORE_PRODUCT_CANON.md`: TodayFlow is the brand, `Profile` is the personal map, `Today` is the daily guide, separate services exist around the core profile.
- 2026-03-25 | Product Direction | Deprecated legacy gate-first text philosophy | DONE | Tracker now records that API interpretation is the primary text source; `quality_gate` remains safety-only, not meaning-shaping.
- 2026-03-25 | Frontend Profile | Rebuilt `/profile` as the single core-profile flow | DONE | `/profile` now handles guided setup, build state, and stable ready-state in one mobile-first screen; `/onboarding/core` reduced to redirect.
- 2026-03-25 | Frontend Today | Reduced first-screen overload and removed phase locks | DONE | `Today` now opens with essential daily guidance, keeps `Утро / День / Вечер` as optional sections, and no longer blocks later phases behind completion gates.
- 2026-03-25 | Frontend Today | Promoted card of day to a central daily object | DONE | `Today` now treats the tarot card as a primary interactive entry point instead of a secondary info tile.
- 2026-03-25 | Frontend Tarot | Rebuilt `/dashboard/card-of-day` into a mobile-first daily reading screen | DONE | New flow centers on the card, today meaning, 3 concrete actions, expandable interpretation, support practice/affirmation, and clean return routes to `/today` and `/tarot`.
- 2026-03-25 | Frontend Profiles | Rebuilt `/account/profiles` into profile-circle management | DONE | Page now supports fast creation of additional people profiles, clear primary-profile logic, and direct compatibility entry without routing users through legacy account flows.
- 2026-03-25 | Frontend Compatibility | Rebuilt `/compatibility` into a guided pair-selection flow | DONE | Compatibility now reads ready-made profiles, supports deep-linked pair preselection, gives a cleaner result surface, and aligns with mobile-first product flow.
- 2026-03-25 | Frontend Natal Chart | Rebuilt `/natal-chart` as a permanent profile-core screen | DONE | Removed daily-noise blocks, connected core-profile metrics, centered the page around personal map, life areas, personal planets, and aspects in a cleaner layered structure.
- 2026-03-25 | Frontend Profile | Turned `/profile` into the central system hub | DONE | Added explicit service navigation from profile to Today, full natal chart, compatibility, and related profiles while preserving core setup and stable personal summary.
- 2026-03-25 | Frontend Routing | Continued legacy route cleanup across secondary surfaces | DONE | Replaced stale `/app`, `/birth-chart`, `/dashboard/daily`, `/dashboard/explore`, and `/dashboard/birth-chart` links in account, weekly, horoscope, lunar, catalog, billing, compatibility, tarot-detail, dashboard helpers, discover helpers, and home preview components with canonical routes like `/today`, `/profile`, `/profile?setup=core`, `/natal-chart`, `/catalog`, and `/compatibility`.
- 2026-03-25 | Backend Geocode | Added bilingual city suggestions | DONE | Added `/astro/geocode/suggest` and extended geocoder dataset with RU/EN city labels for guided place entry and autofill.
- 2026-03-25 | Frontend Profile | Added city autocomplete and stronger life-map framing | DONE | `/profile` now supports RU/EN city search with coordinates capture and includes clearer “who you are” and life-area sections so the screen feels like a personal map rather than a bare form.
- 2026-03-25 | Frontend Header | Reworked mobile navigation into sheet menu | DONE | Replaced brittle disappearing mobile nav with a stable grouped sheet that keeps main sections, quick access, and tracking routes reachable on phone.
- 2026-03-25 | Frontend Forecasts | Reframed `/forecasts` as guided daily interpretation | DONE | Removed the unclear old “period tape” feeling and rebuilt the page around steps: choose date, choose sphere, understand meaning, take the next action, then branch into Today, horoscopes, profile, tarot, and compatibility.
- 2026-03-25 | Frontend Profile | Added stronger interpretation and next-step guidance | DONE | `/profile` now explains strengths, cautions, life areas, and gives direct next moves into Today, horoscopes, and compatibility so it feels like a life map rather than a static data sheet.
- 2026-03-25 | Frontend Today | Added guided exits from daily engine | DONE | `Today` now gives clearer “where to go next” routes into forecasts, horoscopes, and compatibility, reducing the feeling of isolated blocks and helping the system lead the user through the product.
- 2026-03-25 | Frontend Discover | Removed duplicate “second center” behavior from `/discover` | DONE | Root `/discover` is now a lightweight orientation hub with direct exits into profile, natal chart, forecasts, compatibility, and dominant pattern pages instead of duplicating the profile/natal-map center.
- 2026-03-25 | Frontend Forecasts | Rebuilt `/forecasts` as a guided decision screen | DONE | Forecasts now follow a single mobile-first flow: choose date, choose life layer, read the meaning, then move into the one relevant next service instead of scanning a heavy ribbon of cards.
- 2026-03-25 | Frontend Profile | Strengthened `/profile` as a life-map surface | DONE | Profile now includes a practical “my life map” layer around houses 1/4/7/10 plus a clearer “how to use this map” section so the page feels like a personal guide, not a data container.
- 2026-03-25 | Frontend Today | Reduced CTA noise and rewrote key daily microcopy | DONE | `Today` now prioritizes one main daily route, cleaner action wording, and more human guidance in the hero and morning blocks instead of equal-weight buttons and template-like phrases.
- 2026-03-25 | Frontend Forecast Detail | Rebuilt `/forecasts/[date]` into a clear read-and-act screen | DONE | The detailed forecast page now follows the same guided structure as the list screen: meaning of the day, personal lens, one next step, and secondary materials hidden below instead of a long technical wall of content.
- 2026-03-25 | Frontend Compatibility | Rebuilt `/compatibility` into a quick pair-selection flow | DONE | Compatibility now starts from a simple “me + someone from my circle” guided setup, offers quick person shortcuts, reduces form weight, and frames the result as one clear relationship reading instead of a heavy setup screen.
- 2026-03-26 | Backend Forecasts | Fixed and strengthened monthly AI forecast assembly | DONE | `/reports/monthly-forecast` now uses the same humanized AI merge logic as other daily forecast surfaces, inserts theme/notice into psychological insights, deduplicates actions, and no longer relies on the broken `day_offset` branch inside the AI loop.
- 2026-03-26 | Frontend Tarot | Turned `/tarot/result` into a guided interpretation screen | DONE | Tarot result now uses live `core_profile` and `consistency` context from `/tarot/spread/context` to show the main meaning, how it manifests, caution, personal lens, and one clear next step instead of a plain list of card values.
- 2026-03-26 | Frontend Tarot Flow | Unified tarot spread entry with the canonical result journey | DONE | `/tarot/spread/one-card` and `/tarot/spread/three-cards` now act as clean question-entry screens that route into one shared guided result experience, preserve the asked question in `/tarot/result`, and use the canonical `/tarot/card-of-the-day` path instead of sending users back into legacy dashboard routing.
- 2026-03-26 | Frontend Tarot Routing | Made `/tarot/card-of-the-day` the real primary screen | DONE | The card-of-day UI now lives behind the canonical tarot route, the old `/dashboard/card-of-day` path only redirects there as a legacy alias, and the screen itself was extracted into a shared tarot component so product routing matches the current IA.
- 2026-03-26 | Frontend CTA Cleanup | Removed remaining live `/dashboard` root CTA drift from key screens | DONE | Full report upsell now routes to pricing, report history opens `lite` into profile and general “back/home/day connection” CTAs now lead to `Today` or `Profile` instead of the old dashboard root on reports, thematic reports, pattern pages, pricing, and tarot day-connection entry points.
- 2026-03-26 | Frontend Weekly Routing | Introduced `/weekly` as the new live weekly entry route | DONE | Main weekly navigation from `Today`, auth nav, and service discovery now points to `/weekly` instead of `/dashboard/weekly`, reducing legacy IA language in the active user flow while keeping the existing weekly screen behavior intact.
- 2026-03-26 | Frontend Weekly Alias | Made `/weekly` the real primary weekly screen route | DONE | The weekly screen now renders through a shared component at the canonical `/weekly` path, while `/dashboard/weekly` has been reduced to a legacy redirect alias in the same pattern as other cleaned routes.
- 2026-03-26 | Frontend Weekly UX | Rewrote weekly screen labels into the current product language | DONE | The weekly surface now presents itself as `Недельный фокус` instead of an old dashboard subpage, with cleaner auth/loading/empty copy, renamed transit and planetary sections, clearer next-route navigation, and less legacy dashboard vocabulary in the visible UI.
- 2026-03-26 | Frontend Weekly Integration | Moved weekly integration into the same canonical weekly axis | DONE | The weekly integration screen now lives at `/weekly/integration`, is reachable from the main weekly focus surface, and the old `/tracking/weekly` route has been reduced to a legacy redirect alias so weekly meaning no longer competes across separate roots.
- 2026-03-26 | Frontend Copy Cleanup | Removed another small batch of live dashboard wording from canonical UI | DONE | `Systems` now routes current cycles into `Today`, the catalog hero no longer invites users into an old dashboard concept, the weekly feature copy was renamed to `Weekly Focus`, and cross-section helper semantics were updated from an internal `dashboard` bucket to a `today` bucket.
- 2026-03-26 | Frontend Catalog Copy | Reframed product-detail catalog copy around the current IA | DONE | Catalog product pages no longer describe the system through `Lite / Dashboard / Full`; they now explain services through the real product flow of `Profile`, `Today`, weekly focus, and deeper services, while keeping the same structure and CTAs.
- 2026-03-26 | Frontend Catalog Language | Removed remaining internal orbit vocabulary from product detail screens | DONE | Catalog product pages now present themselves in direct product language instead of internal `Orbit` / `Orientation Rail` terminology, with Russian-first headings, clearer route labels, and simpler explanations of how services fit into the main TodayFlow flow.
- 2026-03-26 | Frontend Catalog Hero | Removed the remaining imported/foreign framing from catalog entry screens | DONE | Catalog index and product metadata no longer describe the experience through `Astro.com matrix`, `best-in-orbit`, or English intake/meta phrasing; they now present the catalog as a direct TodayFlow service map with Russian-first entry language.
- 2026-03-26 | Frontend Catalog Categories | Rewrote category-page fallback copy into product language | DONE | Catalog category screens for free, forecasts, personality, relationships, authors, education, shop, subscriptions, and tools no longer fall back to English placeholders; they now keep readable Russian-first hero, recommendation, and aside copy even when translation keys are missing.
- 2026-03-26 | Frontend Catalog I18n | Rewrote active catalog localization keys into canonical product language | DONE | The live `catalog.*` translations in `app.en.json` and `app.ru.json` no longer override screens with `Orbit / Dashboard / Lite+ / Astro.com matrix` framing on the main catalog, category pages, or shared product-detail sections; they now speak through `TodayFlow`, `Profile`, `Today`, weekly focus, and clear service-task language.
- 2026-03-26 | Frontend Catalog Product I18n | Continued removing legacy framing from deeper product-detail translations | DONE | Additional hidden `catalog.products.*` translation keys for forecasts, psychology, star stories, and numerology no longer describe services through `Orbit`, `Dashboard`, `Loop`, or `Lite+` framing where those products now belong to the canonical TodayFlow IA.
- 2026-03-26 | Frontend Catalog Tail I18n | Removed the remaining legacy catalog language from deep product and category translations | DONE | The remaining hidden `catalog.products.*`, category hero, and catalog CTA keys in `app.en.json` and `app.ru.json` no longer leak `Orbit`, `Lite+`, `Dashboard`, `portal`, or imported product framing into live catalog surfaces; they now describe services through direct TodayFlow product language.
- 2026-03-26 | Frontend Horoscopes | Filled month/year screens with readable period guidance | DONE | `/horoscopes` now renders monthly/yearly payloads as real interpretation surfaces with lead meaning, main themes, focus areas, and supporting recommendations instead of sparse generic blocks.
- 2026-03-26 | Backend Period Texts | Humanized yearly and period descriptions at source | DONE | `personal_transits` now returns readable period descriptions, humanized focus areas, stronger yearly recommendations, richer monthly overview summaries, and cleaner lunar window text instead of generic service-level English placeholders.
- 2026-03-26 | Backend Compatibility Texts | Rewrote relationship summaries and recommendations in human tone | DONE | `synastry` and `psych_compatibility` now produce readable Russian-first strengths, triggers, communication techniques, closeness/boundary advice, and practical relationship rules instead of generic English template phrases.
- 2026-03-26 | Backend Today Texts | Strengthened fast and cached daily meaning assembly | DONE | `morning_ritual` now builds daily summary and focus from actual forecast meaning instead of raw tension fields, and its fast/fallback daily guidance texts are more concrete, supportive, and readable.
- 2026-03-26 | Product Direction | Switched canonical product framing to JTBD-first | DONE | `CORE_PRODUCT_CANON.md` and this tracker now define the main product truth as 5 core user jobs, implicit JTBD routing across the main product surfaces, and dedicated JTBD packs for love, money/career, decisions, patterns, state, and daily guidance.
- 2026-03-26 | Product Backlog | Expanded canonical execution backlog from current-state audit | DONE | Added grouped backlog for critical product, core/profile, today, forecasts, compatibility, tarot, text pipeline, UX, mobile, design, data, performance, and QA so all remaining work now lives in one working tracker.
- 2026-03-26 | Frontend JTBD Entry | Moved question-first routing into the main product surfaces | DONE | Added a shared question-entry layer and embedded it into `/today`, `/profile`, and `/questions`, so JTBD routing now lives inside the core product journey instead of existing only as an isolated separate page.
- 2026-03-26 | Frontend Decision OS | Moved decision routing into the main product surfaces | DONE | Extracted a shared `Decision OS` entry layer and embedded it into `/today`, `/profile`, and `/questions/decision`, so concrete choice-making now lives inside the main product journey instead of only as a separate isolated screen.
- 2026-03-26 | Frontend Love and Career OS | Added explicit relationship and money-career lane entries | DONE | Added dedicated `Love OS` and `Money / Career OS` entry surfaces plus lane-pinned question routing, and embedded both lanes into `/today` and `/profile` so the strongest JTBD paths are now explicit inside the core journey instead of hidden behind generic questions.
- 2026-03-26 | Frontend State and Pattern OS | Added explicit stabilization and recurring-pattern lane entries | DONE | Added dedicated `State OS` and `Pattern OS` entry surfaces and embedded both lanes into `/today` and `/profile`, so overload/stabilization and repeating-scenario questions now have explicit routes inside the main product journey instead of living only in generic question routing.
- 2026-03-26 | JTBD Learning Signals | Started logging real downstream route openings from question flows | DONE | `Question` and `Decision OS` result CTAs now send `route_opened` feedback with lane, source surface, and chosen route metadata before navigation, so the learning layer can see not just the inferred JTBD answer but which deeper route the user actually opened next.
- 2026-03-26 | JTBD Answer Feedback | Added direct helpfulness signals to question and decision answers | DONE | `Question` and `Decision OS` results now let the user mark the answer as helpful or still unclear, and those explicit quality signals are logged into the learning layer with lane and surface metadata instead of only tracking route openings.
- 2026-03-26 | JTBD Route Completion | Started logging actual arrival on destination surfaces after JTBD CTA | DONE | JTBD result CTAs now append a lightweight arrival marker, and a shared app-level route logger records `route_completed` plus cleans the URL on arrival, so the learning layer can distinguish between a clicked CTA and a completed transition into the deeper surface.
- 2026-03-26 | JTBD Downstream Completion | Started logging first real actions on destination surfaces | DONE | After JTBD arrival, the active JTBD context now persists in session storage and real downstream actions like compatibility calculation, practice direction selection, morning intention save, and profile core setup completion are logged back into the learning layer instead of stopping at route arrival.
- 2026-03-26 | JTBD Destination Adaptation | Started adapting destination surfaces from active JTBD context | DONE | `compatibility` and `practices` now read the active JTBD context and preselect the first meaningful state for the destination surface, so the user arrives not just on the right route but closer to the right mode, goal, and direction for the original lane.
- 2026-03-26 | Daily Horoscope Prism | Rebuilt `Today` around profile-based horoscope scenarios | DONE | `morning_ritual` now returns a structured `daily_horoscope` block with a headline, a profile-prism narrative, and separate life scenarios for general, love, family, career, and money; `/today` renders those scenarios as a visible daily-horoscope layer so the day is read through the user profile instead of only through one generic summary.
- 2026-03-26 | Profile Daily Lenses | Turned core profile into the permanent source of daily scenario lenses | DONE | `core_profile.interpretation` now includes stable `daily_lenses` for general, love, family, career, and money, `Profile` renders them as an explicit “how your day usually unfolds” layer, and the daily-horoscope prompt now uses those lenses so `Today` is generated from the profile’s lasting logic instead of only from one-day context.
- 2026-03-26 | Daily Scenario Routing | Connected daily horoscope scenarios to the right next product action | DONE | The scenario cards in `/today` now route love and family into `compatibility`, career and money into the dedicated money-career lane, and the general scenario back into the profile foundation; those scenario CTA clicks are also logged as `daily_horoscope_scenario_opened` so the system can learn which daily line actually turns into the next user move.
- 2026-03-26 | Daily Foundation Framing | Reframed the daily layer from horoscope language to day-foundation language | DONE | The generation prompt for the daily scenario block now explicitly asks for a personal “day spine” built on top of the profile base rather than a horoscope, and `/today` presents that block as `Daily Foundation` / `Стержень дня через базу профиля`, making the product read as a daily support system built from life-profile foundations instead of a horoscope feature.
- 2026-03-26 | Daily Spine Structure | Added an explicit backbone schema for the day foundation | DONE | The daily foundation contract now includes a structured `spine` with `day_axis`, `main_risk`, `best_mode`, `first_move`, and `do_not_enter`, and `/today` surfaces those fields as the first visible layer before scenario cards so the day is built from an explicit support model rather than only from narrative text.
- 2026-03-26 | Semi-Deterministic Day Spine | Anchored the daily backbone to system signals before AI phrasing | DONE | The `spine` layer in `morning_ritual` is now first composed from deterministic product signals like `consistency.focus`, `consistency.do_focus`, `consistency.avoid_focus`, daily summary, recommendation focus, and profile baseline, then passed into the model as a fixed system backbone and merged back on response so the day support layer depends less on free-form generation and more on the actual product state.
- 2026-03-26 | Daily Spine Next Action | Turned the day backbone into an executable next move | DONE | The daily `spine` now includes a structured `next_action` with route, label, and kind derived from deterministic day focus and tone, and `/today` renders that action as a primary CTA with click logging so the top-level day support block can drive the next user move directly instead of only describing it.
- 2026-03-26 | Daily Foundation Feedback Context | Added generation logging and completion context for the day foundation layer | DONE | `morning_ritual` now logs each generated daily foundation and returns `daily_horoscope_generation_log_id`, the top-level day spine CTA now carries that id through arrival params, and the shared frontend feedback context now persists daily-foundation metadata alongside JTBD so downstream completion signals can be attributed back to the actual generated day-support layer instead of existing only as unbound navigation.
- 2026-03-26 | Day Spine Route Completion | Added explicit arrival tracking for executable day-spine actions | DONE | The shared route-arrival logger now emits `day_spine_route_completed` when a top-level daily foundation action lands on its destination, carrying `day_spine_action_kind`, label, target href, and arrived path so the product can compare which generated day-backbone routes actually complete and then correlate that with the existing downstream completion signals on `compatibility`, `practices`, `profile`, and other destinations.
- 2026-03-26 | Today and Profile Stability | Removed avoidable waiting on `/today` and stabilized `/profile` state resolution | DONE | `/today` no longer enforces an artificial initial loading delay and now guards against duplicate in-flight initial loads, while `/profile` now checks real stored astro profiles in addition to `core_profile.is_ready`, so existing users are no longer incorrectly pushed into “create profile” state; the profile hero also now includes simple in-page navigation chips to make the screen’s internal route clearer.
- 2026-03-26 | Questions Surface Separation | Removed explicit question widgets from core profile and day screens | DONE | `/today` and `/profile` no longer embed `QuestionEntryCard` / `DecisionEntryCard` blocks or lane-specific question funnels; both screens now answer implicitly through their own content and only point to `/questions` as a separate explicit question tool, matching the product rule that user questions live in the person’s head while core surfaces respond through structured guidance rather than questionnaires.
- 2026-03-26 | Stored Day Layer | Started reusing saved daily texts and removed internal loading narration | DONE | `core_profile` already reads from a saved snapshot by profile hash, and now `morning_ritual` also reuses saved `daily_recommendation` and `daily_foundation` generations per user/date/profile snapshot instead of regenerating them on every open; `/today` loading states were also rewritten to neutral user-facing copy with no internal system narration.
- 2026-03-26 | Stored Compatibility Layer | Added persisted reuse for compatibility calculations with TTL | DONE | Quick `/compatibility/compare` and deep `/compatibility/synastry` results are now stored in `cached_compatibility` and reused for the same user, pair, relation mode, locale, and unchanged profiles for 7 days, so compatibility does not recompute identical pairs on every open while still invalidating naturally when profile data changes.
- 2026-03-26 | Today Screen Simplification | Removed route-hub behavior from `/today` | DONE | `/today` no longer tries to branch the user through multiple “next layer”, people-question, weekly, and question-surface hubs. The screen now stays focused on the day itself: core meaning, daily foundation, state/progress, and one real next move instead of a cluster of competing navigation exits.
- 2026-03-26 | Today Page Decomposition | Split the `/today` monolith into reusable modules | DONE | `frontend/src/app/today/page.tsx` no longer keeps section primitives, quick-action forms, and pure today-specific helper/type logic inline. These pieces now live in dedicated modules under `frontend/src/components/today`, so the route file is closer to an orchestrator and future section-level extraction can continue without editing one 3000-line file for every change.
- 2026-03-26 | Today Screen Section Extraction | Pulled the first large screen blocks out of `/today/page.tsx` | DONE | The top overview stack and the `Рабочий слой дня` are now rendered through dedicated screen-section components in `frontend/src/components/today/TodayOverviewSection.tsx` and `frontend/src/components/today/TodayWorkingLayerSection.tsx`, so the route file no longer owns all top-level presentation directly and can continue shrinking section by section.
- 2026-03-26 | Today Phase Extraction | Moved the morning, day, and evening flows out of `/today/page.tsx` | DONE | The three main phase surfaces of `/today` now live in `frontend/src/components/today/TodayMorningSection.tsx`, `frontend/src/components/today/TodayDaySection.tsx`, and `frontend/src/components/today/TodayEveningSection.tsx`, leaving the route file responsible mainly for data loading, state orchestration, and cross-section callbacks instead of owning the full UI of every day phase.
- 2026-03-26 | Profile Hero and Setup Extraction | Moved the top profile shell and core-setup flow out of `/profile/page.tsx` | DONE | The main hero entry block and the whole profile core-setup/build surface now live in `frontend/src/components/profile/ProfileHeroSection.tsx` and `frontend/src/components/profile/ProfileSetupSection.tsx`, so the route file no longer directly owns the first large product surfaces of `Profile` and can continue shrinking toward a screen-composition role.
- 2026-03-27 | Core Profile Multi-Profile Contract | Added explicit role-aware profile circle contract to account and core-profile payloads | DONE | `astro_profiles` now store `relation`, account profile APIs return normalized roles, `core_profile` now exposes `astro.relation` plus `profiles.primary/selected/items`, and account/profile-management UI lets users mark a profile as self, partner, child, or close person instead of inferring everything from labels.
- 2026-03-27 | Core Profile Contract Split | Separated stable profile map from daily profile lenses in the core payload | DONE | `core_profile.interpretation` now contains only the lasting profile map (`identity`, `strengths`, `watchouts`, `life_areas`), `daily_lenses` moved into `core_profile.daily_interpretation`, `morning_ritual` now reads daily lenses from the dedicated block, and old core-profile snapshots are migrated on read so saved payloads still work after the contract change.
- 2026-05-03 | Backend / Day Engine | DE-5: агрегаты поверхности Today из `meaning_events` | DONE | `meaning_surface_patterns.py`; `build_day_context_v0(..., behavior_patterns=…)`; `build_today_narrative` подмешивает слой в LLM (guide…deepen); `LearningService` + кэш-маркер `core_profile`; сжатый `today_surface_patterns` в `user_core.learning` для промпта.
- 2026-05-03 | Full-stack | DE-4: канонические `meaning` events + веса колец + клиенты | DONE | Backend: `VALID_EVENT_TYPES`, `RING_EVENT_WEIGHTS`; `TodayResultView` / `TodayRitualFlow` / `today/page` и iOS (`TodayRitualFlowView`, `saveEveningReflection` → `evening_reflection_submitted`); типы в `frontend/src/lib/types.ts`; pytest `test_meaning_events.py`.
- 2026-05-03 | Full-stack | DE-3: `generation_id` в событиях Today + learning feedback | DONE | Web: state для всех narrative surface, `generation_id` в meaning payload (`TodayResultView`), `POST /learning/feedback` при сигналах day_connection и сохранении вечера; iOS: `generationLogId` в `trackTodaySurfaceEvent`, `submitLearningFeedback` после `saveEveningReflection`.
- 2026-05-03 | Backend / Contracts | DE-2: DayContext перед narrative LLM | DONE | `build_today_narrative` → `build_day_context_v0` для всех surface; guide user prompt из `layers`; ленивый импорт в `day_context.py` против цикла с `today_narrative`; лог `input_payload.day_context_sha256` + `day_context_contract_version`.
- 2026-05-03 | Backend / Contracts | DayContext v0: спека, JSON Schema, CI, `build_day_context_v0` | DONE | [DAY_CONTEXT_V0.md](./DAY_CONTEXT_V0.md), `docs/schemas/day_context_v0.schema.json`, `scripts/validate_day_context_contract.py`, job `day-context-schema`; черновик сборки `backend/.../day_context.py` + pytest.
- 2026-05-03 | Product / Architecture | Day Engine зафиксирован в трекере выполнения | DONE | Канон [DAY_ENGINE_AND_COHERENCE.md](./DAY_ENGINE_AND_COHERENCE.md); в трекере добавлены §4.7 (чеклист DE-1…DE-11), §5.3 (порядок работ), приоритет §6 п.0; gap в §3 про отсутствие единого DayContext end-to-end.
- 2026-05-03 | Backend / Narrative | DayModel v0 во все LLM-pack’и narrative + лог | DONE | `day_model` и `day_engine_brief` в user JSON для **day_layer**, **spheres**, **evening**, **deepen** (`_attach_day_logic_slices`); `input_payload.day_model_contract` для всех surface при наличии слоя; промпт **today-narrative-v11** (слайсы RU/EN: day_model в п.1); pytest на day_layer user JSON и `day_model_contract` в логе.
- 2026-05-03 | Frontend | Today: общий блок опоры + логика дня; copy policy | DONE | `TodayDayLogicCallout` (ритуал + `TodayGuideSection`); лоадер ритуала — новый текст без «без воды»; `COMPATIBILITY_GENERATION_LIVE` в `lib/compatibilityDynamicsMode.ts` — убраны вхождения `llm` из сканируемых `app/components`, `userFacingCopyPolicy` зелёный.
- 2026-05-03 | Backend / API + tests | Narrative: контракт ответа guide vs LLM | DONE | `TodayNarrativeResponse` и docstring `post_today_narrative`: в HTTP-ответе `day_model`/`day_engine_brief` только у guide; pytest parametrize `day_layer`/`spheres`/`evening`/`deepen` — user JSON содержит оба слоя.
- 2026-05-03 | Full-stack | DE-6: intent в DayContext и Today narrative | DONE | `intent_slice_v0.py`, `build_day_context_v0(..., intent_slice=…)`, `DayConnection` + `head_topic` в `build_today_narrative`, `intent_context_fp` в кэше narrative, `PROMPT_VER` v7→v8; `RitualContextRequest.head_topic`, `ritual_context` для всех surface; web `lastRitualNarrativeContextRef` + `head_topic` в эффекте ритуала; iOS last-context + `head_topic` + повторный refresh при выборе темы после check-in; [DAY_CONTEXT_V0.md](./DAY_CONTEXT_V0.md) + `day_context_v0.schema.json` (`ritual.head_topic`); pytest `test_intent_slice_v0`, расширен `test_day_context_v0`.
- 2026-05-03 | Backend / Day Engine | DE-7 v0: этапы дня в fusion и slim fusion | DONE | `GET /tracking/fusion/{date}` → `activity_context.morning_completed` / `day_completed` / `evening_completed` из `DayConnection`; `_fusion_slim_for_prompt` переносит только эти три ключа для spheres/evening/deepen; [DAY_CONTEXT_V0.md](./DAY_CONTEXT_V0.md); pytest `test_tracking.py`, `test_today_narrative_contract.py`; docstring `profile_prompt_slices_v0`: DE-7 → DE-12.
- 2026-05-03 | Backend / Day Engine | DE-7 v1: выборы guide action_options в fusion | DONE | `activity_context.guide_action_options_selected_today` = count `meaning_events` (`action_option_selected`, `local_date`); slim fusion кламп 0–50; pytest `test_tracking.py::test_fusion_counts_action_option_selected_meaning_events`, расширен slim-тест в `test_today_narrative_contract.py`.
- 2026-05-03 | Backend / Day Engine | DE-7 v2: «сделано» из meaning_events в fusion | DONE | `guide_flow_signals.guide_meaning_completions_today_counts` → `activity_context.guide_meaning_completions_today` (5 типов); slim `_fusion_slim_for_prompt`; различие с `day_completed` в [DAY_CONTEXT_V0.md](./DAY_CONTEXT_V0.md); pytest `test_tracking.py` (в т.ч. `test_fusion_guide_meaning_completions_today_from_meaning_events`), `test_today_narrative_contract.py::test_fusion_slim_clamps_guide_meaning_completions_today`; iOS `FusionActivityContext.guideMeaningCompletionsToday`.
- 2026-05-03 | Backend / Day Engine | DE-8 v0: `depth_level` в narrative API и DayContext | DONE | `POST /today/narrative.depth_level` (quick/normal/deep); `DayContext.meta.depth_level`; кэш `_load_narrative_cache`; `policy.depth_level` + guide top-level; `_openai_json` max_tokens/temp; `PROMPT_VER` v12; web `todayNarrativeApi` + iOS `TodayNarrativeRequest.depth_level`; pytest кэш по depth; [DAY_CONTEXT_V0.md](./DAY_CONTEXT_V0.md), schema fixture. |
- 2026-05-03 | Backend / Day Engine | DE-9 v0: temporal slice в DayContext + LLM | DONE | `fusion_scores.py` (`build_fusion_scores_for_inputs`, `compute_fusion_scores_map_for_dates`); `history_layer_v0.build_history_layer_v0`; `build_day_context_v0(..., history_slice=…)`; `build_today_narrative` + `_attach_day_history_to_llm_pack` → `day_history`; рефактор `GET /tracking/fusion` на общую формулу scores; pytest `test_fusion_scores.py`, `test_history_layer_v0.py`, [DAY_CONTEXT_V0.md](./DAY_CONTEXT_V0.md). |
- 2026-05-04 | Full-stack | DE-8 v1: глубина narrative из профиля + клиенты без override | DONE | Миграция `today_narrative_depth_level`; `PUT account/profile` + GET; `POST /today/narrative` без `depth_level` → настройка пользователя; веб settings + iOS `AccountSettings` / `ProfileSettingsView`; iOS `fetchTodayNarrative(depthLevel: nil)` и JSON без ключа; web `todayNarrativeApi` уже без поля по умолчанию. |
- 2026-05-04 | Backend + clients | DE-8 v2: тарифный гейт для `deep` | DONE | `_clamp_narrative_depth_for_insight_tier` в `today_narrative` (free → `deep`→`normal`); `PUT account/profile` 400 для free + `deep`; веб settings: `/auth/me` + `insightDepthFromProfile`, скрытие опции; iOS `AuthSession.insightDepthTier`, `resumeSessionIfNeeded` в load настроек, picker без «Глубже» на free; pytest `test_account`, `test_today_narrative_contract`. |
- 2026-05-04 | Full-stack | DE-9 v1: `day_history` в fusion + полоска в ритуале | DONE | `FusionIndexResponse.day_history` + `build_history_layer_v0` в `get_daily_fusion_index`; типы и UI на вебе (`FusionResponse.day_history`, `TodayRitualFlow`); iOS `FusionIndex.dayHistory` + `TodayRitualFlowView`; dev preview mock; pytest `test_tracking.py::test_daily_fusion_index` проверяет контракт `day_history`. |
- 2026-05-03 | Backend / Narrative | Кэш guide по `day_context_sha256` | DONE | `build_day_context_v0` до `_load_narrative_cache`; в кэше требуется совпадение `input_payload.day_context_sha256`; при смене fusion — промах кэша и новый `generation_log`; pytest `test_guide_narrative_cache_hit_when_day_context_unchanged`, `test_guide_narrative_cache_miss_when_fusion_changes_day_context`; [DAY_CONTEXT_V0.md](./DAY_CONTEXT_V0.md).
- 2026-05-03 | Backend / Copy | Narrative: анти-абстракция + RU quality gate | DONE | `today_narrative.py`: усилены `_GUIDE_SYS` / `_SPHERES_SYS` / `_DAY_SYS`; `_guide_payload_concrete`, `_spheres_payload_concrete`, `_ru_narrative_quality_reject`; кэш guide не отдаётся при провале гейта; `temperature` 0.52; web+iOS: подписи сфер без «мы смотрим на записи», `dayMarkerMoon` переименован; pytest расширен `test_today_narrative_contract.py`.
- 2026-04-26 | Product Today UX | Зафиксирован канон ритуала и упаковки Today (web + iOS) | DONE | Добавлен §4.6: north-star входов движка, слоистая IA, information diet, progressive disclosure, тактильная палитра (песок / розовое золото), отсутствие ИИ в пользовательском тексте, паритет «Собрать день» + сферы + подсказка до чекина; iOS — горизонтальный дек карта→число→тон; бэклог: контракт narrative fusion для привычек/дневника/аскез, опциональный bento-виджет Today.
- 2026-04-26 | iOS Today | Deep link чипов «Собрать день» в Flow | DONE | `TrackerQuickCreateKind` + `pendingTrackerQuickCreate`: привычка — скролл к блоку и фокус поля; цель и аскеза — шиты; `TodayFlowStore.createAsceticContract` → `POST /tracking/ascetic-contracts`; каталог через `PracticesClient.fetchAsceticisms`; обработка intent в `onAppear`/`onChange` у `CalendarView`, чтобы сработало при переключении таба с Today.
- 2026-04-26 | iOS Goals | Паритет якорей и лимитов с веб `EntityCreateWizard` | DONE | `week_start`: понедельник недели выбранного дня (`weekStartMonday`), месяц — `monthAnchorIso`; лимит 3 цели на недельный пул и 3 на месячный (`goalSlotCounts` / `canCreateGoal`); формы быстрой цели и `GoalsView`; `createGoal` возвращает `Bool`.

---

## 8) Working Rules

- Any new feature starts as a task update in this file.
- Any completed implementation must update:
  - phase checkbox,
  - progress log,
  - current priorities (if changed).
- If priorities conflict, follow section `6) Current Priorities`.
- 2026-03-25: Пересобран прогнозный слой `/horoscopes` в формате спокойного персонального workspace вокруг ядра профиля. Убраны прямые упоминания ИИ из пользовательского текста, упрощена структура периодов `день / неделя / месяц / год`, добавлены понятные CTA между `/profile`, `/today`, `/forecasts`, `/natal-chart`. Детальный экран `/forecasts/[date]` приведен к той же продуктовой формулировке.
- 2026-03-25: Полностью пересобран `/forecasts` как единый прогнозный календарь: сильный главный блок периода, дата-чипы, доменные переключатели, спокойный персональный слой справа и более чистая лента карточек без ощущения таблицы и техфильтратора.
- 2026-03-25: Пересобран входной экран `/tarot` как единый сервис-хаб: карта дня, быстрый вопрос, глубокий расклад и связь с ядром профиля. Убран разрозненный вход в модуль, добавлены понятные сценарии использования и прямые переходы в `Today`, `Profile` и `Card of the Day`.
- 2026-03-25: Унифицированы экраны `one-card`, `three-cards` и `tarot/result` под один продуктовый сценарий. Теперь это один визуальный язык, единые CTA, более спокойные итоговые экраны и понятный переход между быстрым вопросом, глубоким раскладом и картой дня.
- 2026-03-25: Полностью упрощен `/calendar`. Убраны перегруженные режимы и модальные сценарии, оставлен один month-hub: сетка месяца, выбранный день, быстрые события, запись дня, слой цикла и слой трекеров. Экран теперь читает период сверху вниз и не ощущается как технический органайзер.
- 2026-03-25: Пересобран `/habits` в формате спокойной habit map. Убрана утилитарная “админская” подача, добавлены единый hero, мягкая heatmap-лента по каждой привычке, простой сценарий создания и ясная сводка по стрикам и completion rate.
- 2026-03-25: Пересобран `/cycle` в формат личного слоя ритма. Убраны перегруженные аналитические панели, добавлены hero, дневная фиксация, сценарий дня, короткая сводка и практики под текущее состояние. Экран теперь читается как часть `TodayFlow`, а не отдельный аналитический сервис.
- 2026-03-25: Начата зачистка legacy-навигации. Обновлены живые переходы в `NavAuthLinks`, `Footer`, account-карточках и пересобран `/tracking/progress` как новый хаб трекеров. Старые ссылки на `dashboard/daily`, `dashboard/explore`, `forecast`, `guidance`, `growth` заменяются на канонические маршруты нового продукта.
- 2026-03-27: `Profile` теперь показывает role-aware круг людей как часть канонической личной карты. На экране появился отдельный блок связей с `self / partner / child / close person`, пояснениями зачем нужен каждый профиль и прямыми переходами в `Today`, `compatibility` и `/account/profiles`, поэтому multi-profile больше не живет только в аккаунт-настройках.
- 2026-03-27: Домовой слой `Profile` доведен до практической карты жизни. Блок `Сферы жизни и дома` теперь объясняет не только значение дома, но и где тема проявляется, что усиливать, чего избегать и куда идти дальше по каждому дому, а вместе с уже собранными strengths, cautions и life areas это закрывает расширение контента профиля до канонической “life map” поверхности.
- 2026-03-27: Стабилизирован build flow на `/profile`. Вместо голого спиннера появился отдельный loading-screen, hero и setup-flow теперь живут в одной staged-логике, а после успешной сборки экран не прыгает сразу в ready-state: пользователь сначала видит явное completion-состояние с подтвержденными данными и кнопкой `Перейти к карте`, а уже потом сам переводит экран в постоянный режим профиля.
- 2026-03-27: Убран основной перегруз из средней и нижней части `/today`. `Опора дня` сокращена до одного поддерживающего решения с компактной практикой и недельным вектором вместо конкурирующих карточек и CTA, а `Ход дня` теперь просит всего одну быструю фиксацию, показывает только первые записи за день и уводит в глубину через один спокойный выход вместо набора параллельных сервисных кнопок.
- 2026-03-27: Верхний слой `/today` доведен до одной линии движения и сильнее привязан к `Profile`. На первом экране остались один главный смысл дня, карта дня, один следующий ход и одна supporting card, дублирующие CTA убраны, сценарные и практические переходы стали спокойнее, а блоки `Опора из профиля` и `Как день читается через тебя` теперь читают день через `core_profile`, а не как набор отдельных сервисов.
- 2026-03-27: Дневной язык `Today` доведен до одного product tone. В backend обновлены prompt-версии и fallback-тексты утреннего daily layer, чтобы тексты устойчивее выполняли три функции: поддержать, предупредить и сдвинуть в действие; на фронте переименованы и выровнены пользовательские формулировки вроде `Что поддержит день` / `Что не усиливать` и убраны остатки смешанного англо-сервисного словаря.
- 2026-03-27: Numerology перестала конкурировать с `Profile` как отдельный вход. `Profile` теперь поддерживает фокус `?focus=numerology` и адресует пользователя прямо в numerology-слой общей карты, numerology result/entry screens ведут обратно в этот канонический маршрут, а сохраненные numerology calculations в `/library` тоже открывают numerology уже внутри профиля, а не через отдельные result pages.
- 2026-03-27: Compatibility result surface приведен к канонической структуре смысла. Основной экран `/compatibility` теперь сначала показывает главную динамику связи, затем явно отвечает на пять продуктовых вопросов: где течет легче всего, где возникает трение, что помогает и как действовать дальше; backend `deep_dive` больше не падает в UI россыпью дублирующих карточек, а читается как один собранный relationship lens.
- 2026-03-27: `Sign compatibility` и `birthdate compatibility` приведены к одному смысловому стандарту. Их result pages теперь обе читаются через одну и ту же структуру: главная динамика связи, где течет легче, где возникает трение, что помогает и как действовать дальше; тексты и CTA больше не живут в разных product tones и естественно ведут в глубокую совместимость.
- 2026-03-28: Быстрые входы в `Compatibility` доведены до role-aware маршрутов. `Profile`, `Today` и `Круг людей` теперь не ведут в пустой общий compatibility-flow по generic ссылке, а стараются открыть уже готовую пару `me + someone from my circle`; если нужного второго профиля еще нет, продукт уводит в `/account/profiles`, чтобы сначала собрать реальный круг людей, а уже потом читать связь.
- 2026-03-28: Живой tarot-поток очищен от сервисной подачи и приведен к одной продуктовой логике. `/tarot`, `one-card`, `three-cards`, `tarot/result` и `card-of-the-day` теперь читают карты как слой смысла вокруг `Today` и `Profile`, а не как отдельный “tarot service”; хаб стал вести через центральный ежедневный ритуал, spread-entry screens заранее обещают структуру `meaning / manifestation / caution / next step`, а `card of the day` закреплена как главный tarot-вход дня.
- 2026-03-28: Tarot spreads доведены до явного смыслового контракта. `/tarot/spread/context` теперь возвращает отдельный `reading` блок с `meaning`, `manifestation`, `caution` и `next_step`, а `tarot/result` опирается уже на этот backend-ready слой вместо чисто фронтовой склейки; в итоге и одна карта, и три карты читаются в одном продуктовой формате, а не только выглядят так визуально.
- 2026-03-28: Канон уточнен: TodayFlow не делится на три самостоятельных продукта `утро / день / вечер` и не строится вокруг отдельного `future / period` сервиса. Есть один экран `Today` с мягкой временной логикой и напоминаниями, а будущее как смысловой слой допустимо только внутри `Profile`, `Compatibility`, decision-support и других вторичных интерпретаций, но не как отдельный продуктовый центр.
- 2026-03-28: `Today` дополнительно дочищен под новый канон одного дневного экрана. На живом UI убраны остатки старой фазовой модели вроде `Открываем утро`, `Закрытие дня` и `ритуал`-формулировок там, где они продолжали дробить экран на самостоятельные этапы; weekly-ориентир закреплен как внешний helper, а вечерний смысловой блок свернут в reveal, чтобы экран оставался про один текущий ход, а не про три параллельных режима дня.
- 2026-03-28: В `Today` добавлен явный reminder-layer вместо фазовой навигации. Верх экрана теперь показывает `Ритм возврата` с мягкой подсказкой, когда и за чем лучше вернуться в течение дня, а выбор раскрытого блока больше опирается на незавершенный следующий шаг пользователя, чем на жесткое деление дня по времени суток.
- 2026-03-28: Собран более цельный auth contour. `/auth` теперь держит явный `mode=login|signup`, безопасно сохраняет `redirect`, после успешного входа или регистрации определяет следующий шаг через `redirect` или готовность core-profile, алиасы `/login` и `/signup` больше не теряют намерение пользователя, recovery flow ведет обратно в единый auth entry, а в `/account/settings` добавлена отдельная смена пароля для авторизованного пользователя вместо смешивания signed-in security и recovery-сценариев.
- 2026-03-28: `Today` signals выведены в общий personalization layer. Ответы `ritual feedback`, `mini decision` и `question of day` теперь сохраняются в `DayConnection`, учитываются в `tracking/fusion/{date}` как часть живого состояния дня, а weekly/monthly state map в `/tracking/calendar` и `/calendar/unified` показывает их отдельной строкой `Сигналы дня`, чтобы накопленное понимание пользователя строилось из реальных daily inputs, а не только из трекеров и дневника.
- 2026-03-28: `Today` начал учиться на вчерашнем отклике пользователя. Decision engine в `/morning-ritual/today` теперь читает последние `daily signals` из `DayConnection` и мягко адаптирует энергию, фокус, риск, действия и ограничения на следующий день: если вчера день не собрался, усиливается режим бережности и сужения фронта; если осталась неясность, следующий день сильнее предупреждает об ошибках и поспешных решениях.
- 2026-03-28: `Daily signals` подключены и к auto-insights. Инсайты теперь умеют замечать не только completion/mood-паттерны, но и повторяющуюся собранность дня, неясность решений и доминирующий фокус из `question of day`, поэтому слой `меня видят` начинает строиться из реального daily dialogue с пользователем, а не только из сервисных трекеров.
- 2026-03-28: `Profile` получил живой evolving layer поверх стабильной карты. В `core_profile` добавлен блок `living` с summary, signal profile, weekly state и recent insights, а на `/profile` появился отдельный слой накопленного понимания пользователя: как сейчас собирается день, растет ли ясность решений, какая тема всплывает чаще всего и что уже заметила система. Профиль теперь развивается не только через натал и числа, но и через проживаемый ритм пользователя.
- 2026-03-28: Начат user-level learning context поверх learning layer. `LearningService` теперь синтезирует общий контекст из feedback, JTBD route choices, diary topics и daily signals, а `core_profile.living` включает этот слой как `learning_context`. На `/profile` появился отдельный блок о том, как системе лучше говорить с пользователем, что ему сейчас помогает и какие темы у него повторяются чаще всего. Это ещё не финальный learning LLM, но уже общий psychotype foundation для web и iOS.
- 2026-03-28: Зафиксировано обязательное правило internal quality memory. Сервис должен помнить цепочку `сгенерированный ответ -> реакция пользователя -> downstream route/outcome` и на её основе различать сильные и слабые паттерны ответа. Этот learning contour остаётся внутренним: пользователь не должен видеть язык про “обучение машины” или “тренировку модели”, только более точные и уместные ответы.
- 2026-03-28: JTBD answer assembler начал учитывать живой learning context и quality memory. В `QuestionService` ответы и suggested-route теперь читают `core_profile.living.learning_context`: при необходимости усиливают ясность, сужение фронта и concrete-next-step tone, а money/future lanes больше не ведут пользователя в старые forecast-first корни, а синхронизированы с новым каноном `Today + Profile + Compatibility`.
- 2026-03-29: Learning context встроен и в `Today` decision engine. `/morning-ritual/today` теперь читает `core_profile.living.learning_context` как дополнительный deterministic-layer поверх транзитов, numerology, state, goals и yesterday signals: повторяющиеся темы пользователя, signal bias и preferred response style влияют на дневной focus, риск, действия и ограничения, а debug-сигналы decision engine уже несут этот learning slice как общий контракт для web и iOS.
- 2026-03-29 | Backend Astro | Снят частый 422 на `POST /chart` | DONE | В astro-сервисе `BirthData.location` по умолчанию пустая строка; парсер времени принимает `HH:MM:SS`; `AstroService.compute_chart` подставляет `lat,lon` в `location`, если город не передан; `user_context` всегда шлёт `location` в JSON.
- 2026-03-29 | Backend Today | Слой быстрой доставки для мобильного first paint | DONE | Добавлен `GET /today/opening` (DayConnection + флаги этапов); на `GET /today` — query `light=1` без трекеров дня, среза дневника, вечернего ritual payload и тяжёлого rewards snapshot (утро, core_profile и consistency сохраняются).
- 2026-03-29 | Backend Today | Полный набор progressive-слоёв под один экран Today | DONE | Добавлены `GET /today/checkin-prompt` (следующий чекин по DayConnection, RU/EN), `GET /today/core` (утро без списка сценариев), `GET /today/scenarios` (сценарии по сферам), `GET /today/state-map` (алиас fusion), `GET /today/evening` (вечерняя связка + ritual); общий хелпер `_fetch_morning_ritual_fast` + закрытие `AstroService`; полный `GET /today` использует тот же хелпер для утра.
- 2026-03-29 | Backend Today | Один проход core+scenarios + кеш утра | DONE | Добавлен `GET /today/bundle` и in-memory TTL-кеш (120s) на `(user_id, date, locale)` для `/today/core`, `/today/scenarios`, `bundle` и утренней части полного `GET /today`; при смене `morning_intention` в day-connection кеш сбрасывается.
- 2026-03-29 | Backend Push | Ритм дня и цель на день | DONE | Таблицы `push_devices`, `user_push_schedules`, `daily_goal_snapshots`, `push_dispatch_log` + миграция SQL; API `POST/DELETE /notifications/devices`, `GET/PUT /notifications/schedule`; крон-хук `POST /internal/push/run-due` с `X-Push-Dispatch-Secret`; сервис `push_delivery`: слоты morning/day/evening + goal midday/afternoon по локальному времени, мгновенный пуш при сохранении новой формулировки цели (`morning_intention`); опционально `FCM_SERVER_KEY` для legacy FCM HTTP.
- 2026-03-30 | Product Push | Матрица хуков и анти-спам | DONE | В `docs/status/IOS_TODAYFLOW_STATUS.md` зафиксированы: уже live-хуки, рекомендуемые следующие (streak, weekly focus, карта дня, привычки, re-engagement, transactional), глобальные лимиты/тихие часы/дедуп, категории для будущих тумблеров и технический backlog (`NotificationIntent`, расширение расписания, событийные точки в чекинах и активности).
- 2026-03-31 | Backend Push | Тихие часы, дневной лимит, категории | DONE | В `user_push_schedules`: `quiet_start`/`quiet_end`, `max_auto_per_day` (1–15), флаги `notify_rhythm_today`, `notify_goal_nudges`, `notify_goal_ack`, резервные `notify_streak_care` … `notify_comeback`; миграция `add_push_schedule_antispam.sql`; `run_due` учитывает тихие часы и лимит по `push_dispatch_log`; мгновенный `goal_saved` уважает `notify_goal_ack` и тихие часы; ответ крона расширен `blocked_quiet` / `blocked_cap`.
- 2026-04-26: Зафиксирован канон daily ritual UX и план развития — см. **§4.6** в этом трекере (паритет web/iOS, упаковка Today, очередь по narrative fusion и deep links).
- 2026-04-26: iOS — реализованы deep links чипов «Собрать день» в таб Flow (`pendingTrackerQuickCreate`, шиты цели/аскезы, скролл к новой привычке).
- 2026-04-26: iOS — цели: `week_start` как понедельник недели выбранного дня и якорь месяца `yyyy-MM-01`, лимит 3+3 как на вебе.
- 2026-05-03 | Product | Зафиксирована цель ветки «Today 100%» | IN_PROGRESS | Добавлен §6.2 DoD: ритуал, narrative, meaning parity web/iOS, обновление §4.7 и iOS status при закрытии; вне скоупа DE-10/11/13 и Phase 6 JTBD.
- 2026-05-03 | Frontend/Backend Today | Ритуал, копирайт, narrative cache, slim profile в guide | DONE | Герой без числа до шага числа; «Луна и фон дня» без profile_prism в первой строке; `day_narrative_brief_v0` с RU якорем mood/topic; кэш narrative по `prompt_label` + версия; `user_core` локализован, сырой `profile` убран из guide JSON для LLM.
- 2026-05-03 | Backend Today narrative | Семантическая дедупликация полей guide | DONE | `_dedupe_guide_payload_cross_fields` в `today_narrative` (паритет с веб-дедупом); на кэш-hit та же цепочка + `_normalize_guide_payload_for_tier`; pytest в `test_today_narrative_contract.py`.
- 2026-05-03 | Web + iOS Today | DE-7 UI: главный шаг ↔ fusion completions | DONE | Заголовок секции «Главный шаг на сегодня» (TODAY_WEB §4); строка «Сегодня в Flow уже отмечено: …» из `guide_meaning_completions_today`; тип `FusionResponse.activity_context` на вебе; `TodayRitualCopy.formatGuideMeaningCompletionsLine` на iOS.
- 2026-05-04 | Web + iOS Today | DE-7 UI v3: чипы и пустое состояние | DONE | `guideMeaningCompletionsEyebrow` / `guideMeaningCompletionsEmpty`; `guideMeaningCompletionChipItems` (TS) и `TodayRitualCopy.guideMeaningCompletionChipItems` + `GuideMeaningCompletionsFocusStrip` (Swift); dev `today-ritual-preview` с примером `activity_context`.
- 2026-05-04 | Product | Зафиксирован обязательный контур «умного сервиса» | DONE | §6 переписан: DayContext → narrative → UI → события/вечер → снова контекст; DE-8/DE-9 и §5.2 Learning Next — следующие обязательные инкременты; §5.3 п.8 уточнён (DE-10/11 отдельно, DE-13 эпик); §6.2: DE-7 в желательном заменён на backlog связки шага с событиями.
- 2026-05-04 | Web + iOS + Android scaffold | Ритуал: общий spine-reducer + аналитика из эффектов | DONE | Паритет фаз/переходов и `isSpineComplete`/`tarotContinueAck`; `analyticsHint` + единые исполнители событий; веб: `source: today_ritual` в payload `mood_selected`; Android: `ExecuteRitualSpineAnalytics.kt` + JUnit; см. §4.6 bullet «Ritual spine contract» и [TODAY_PERSONALIZATION_CORE.md](./TODAY_PERSONALIZATION_CORE.md) (payload ритуала).
- 2026-05-04 | Web + iOS Today | DE-9 v1.1: day_history у сфер | DONE | Компонент `TodayDayHistoryStrip`; повтор полоски в `#today-ritual-your-day`; iOS — `fusionDayHistoryStrip` в `spheresTriadBlock` (паритет).
- 2026-05-04 | Web + iOS Today | DE-9 v1.2: недельная сводка в полоске | DONE | `trailing_7d_summary` → вторая строка в `TodayDayHistoryStrip` / `fusionDayHistoryStrip`; Jest `formatFusionDayHistory.test.ts`; mock в `today-ritual-preview`.
- 2026-05-04 | Full-stack Today | DE-9 v1.3 + мета-срез guide | DONE | Нулевая дельта: `RITUAL_COPY.dayHistoryDeltaAllZeroTail` / EN + `formatFusionDayHistoryEn`; iOS `TodayRitualCopy` (RU/EN); `strip_llm_meta_commentary` + `strip_meta_from_guide_payload` в `ritual_cue_sanitize.py` → `_guide_apply_final_processing_pass`; pytest `test_ritual_cue_sanitize.py`; дорожная карта «Оркестратор O1–O12» в [TODAY_LANGUAGE_V1.md](today-language/TODAY_LANGUAGE_V1.md).
- 2026-05-04 | Backend + Web + iOS | §5.2 implicit: «Почему так?» в ритуале | DONE | `today_guide_why_opened` в `VALID_EVENT_TYPES`, вес Mind `0.03`; веб `TodayRitualFlow`, iOS `TodayRitualFlowView`; pytest `test_post_meaning_events_accepts_today_guide_why_opened`; [TODAY_PERSONALIZATION_CORE.md](./TODAY_PERSONALIZATION_CORE.md).
- 2026-05-04 | Web + iOS + Android scaffold | §5.2: generation_id на шагах хребта | DONE | При наличии guide — `number_selected` / `mood_selected` с `generation_id`: веб `executeRitualSpineAnalytics` + `narrativeGenerationIds.guide`, iOS `applySpineEffects` + `todayGuideNarrative.generationID`, Android параметр `guideGenerationId`; Jest `todayRitualSpineMachine.test.ts`; см. [TODAY_PERSONALIZATION_CORE.md](./TODAY_PERSONALIZATION_CORE.md) (ритуальная цепочка).
- 2026-05-04 | Web + iOS + Backend | §5.2: tarot + DE-9 visibility | DONE | `tarot_selected` с опциональным `generation_id` (веб/iOS); `today_day_history_first_visible` (`VALID_EVENT_TYPES`, Mind `0.025`), веб `TodayDayHistoryStrip` + IntersectionObserver, iOS `fusionDayHistoryStrip(placement:)` + `onAppear`; pytest `test_post_meaning_events_accepts_today_day_history_first_visible`.
- 2026-05-04 | Web + iOS | §5.3 UI garbage (канон копирайта) | DONE | `TodayResultView`: интро сфер из `RITUAL_COPY.areasIntroToday` (убран дубль захардкоженного текста); чипы «Собрать день» — `RITUAL_BUILD_DAY_QUICK_CHIPS` / `TodayRitualCopy.BuildDayQuickChips` (паритет [TODAY_SCREEN_V1_CANON.md](./TODAY_SCREEN_V1_CANON.md) §3–4).
- 2026-05-04 | Web + iOS Today | §5.3 UI garbage (оболочка `/today`) | DONE | `RITUAL_COPY`: загрузка/ошибки/фон, подписи шагов дня, тост и хром фокус-таймера, строки `TodayNarrativeDepthControl`; iOS — `TodayRitualCopy.TodayPageShell`, `NarrativeDepthControl`, `FocusTimerChrome` (в т.ч. «Собираю твой день…» / «Обновляю твой день…» вместо «Today»).
- 2026-05-04 | Web + iOS Today | §5.3 UI garbage (тосты и фолбэки `/today`) | DONE | `RITUAL_COPY`: тосты Guidance / DE-8 / сохранения дня и вечера / практики; фолбэки заголовка дня, числа, колец плана; `NUMEROLOGY_LUCKY_DAY_PRESETS`; iOS — `TodayPageToasts`, `NarrativeDepthToasts`, `NumerologyLuckyDayPresets`, `numerologyMeaningFallbackShort`, резерв заголовка дня в `dayTypeHeadline`.
- 2026-05-04 | Web + iOS Today | §5.3 UI garbage (`TodayRitualFlow` + связка карта/число) | DONE | `RITUAL_COPY` + хелперы: мост карта+число, кольцо «таро», риск/лучший ход, подсказка героя, таро без анимации, чек-ин, шит детали, закрытие/«Поняла»; iOS — те же формулы в `TodayRitualCopy`, `bridgeLine` = веб-фолбэк, `TodayGuideActionable` использует `heroRiskLabel` / `heroBestMoveLabel`.
- 2026-05-04 | Web + iOS Today | §5.3 UI garbage (`TodayResultView`) | DONE | `RITUAL_COPY`: `eveningHookBodyCompact`, `areasTriadModalDetailHint`, `sphereSheetNavTitle` (aria), `formatActionOptionEstimatedMinutesSuffix`; кнопка модалки сферы — `sheetCloseCta`; iOS — `eveningHookBodyCompact`, `areasTriadModalDetailHint` в каноне (UI треугольника без «окна» — строка не дублируется в разметке).
- 2026-05-04 | Web + iOS Today | §5.3 канон копирайта (Guide / Working / Quick actions) | DONE | Веб: `RITUAL_COPY` + хелперы в `todayRitualCopy.ts`; `TodayQuickActions`, `TodayGuideSection`, `TodayWorkingLayerSection` без захардкоженного русского; iOS — `TodayWebQuickActionsCopy`, `TodayWebGuideSectionCopy`, `TodayWebWorkingLayerCopy` в `TodayRitualCopy.swift` (дословный паритет для нативных экранов позже).
- 2026-05-04 | Web + iOS Today | §5.3 канон копирайта (сферы `/today` + хром секций) | DONE | `RITUAL_COPY`: блок сфер (`TodayLifeSpheresSection`), общие CTA «Свернуть»/«Развернуть»/«Открыть», подсказки `DaySectionHeader` (`TodaySectionPrimitives`); iOS — `TodayWebLifeSpheresCopy`, `TodayWebSectionChromeCopy`.
- 2026-05-04 | Web + iOS Today | §5.3 канон копирайта (этапы дня `/today`) | DONE | `RITUAL_COPY` + хелперы: `TodayDaySection`, `TodayMorningSection`, `TodayEveningSection`, `TodayFlowTabs`; вечерний outlook и связь с утром; iOS — `TodayWebDaySectionCopy`, `TodayWebMorningSectionCopy`, `TodayWebEveningSectionCopy`, `TodayWebFlowTabsCopy` (число/чек-ин — `TodayRitualCopy`).
- 2026-05-04 | Web + iOS Today | §5.3 канон: табы `/today` + уровни DE-8 | DONE | `TODAY_FLOW_TABS` из `RITUAL_COPY`; подписи «Короче/Обычно/Глубже» в `todayNarrativeDepthUi` + `TodayRitualCopy.NarrativeDepthControl.option*`; iOS `TodayView` / `ProfileView` без захардкоженных строк селекта; `TodayWebFlowTabsCopy` — подписи вкладок для паритета.
- 2026-05-04 | Web + iOS Today | §5.3 канон: прогрев `/today` + маршруты сфер | DONE | `thinkingMessages` и `getHoroscopeScenarioRoute` из `RITUAL_COPY`; iOS — `TodayWebPageShellCopy` (дословный паритет).
- 2026-05-04 | Web + iOS Today | §5.3 канон: данные дня в `todayPageUtils` | DONE | События для нарратива, подзаголовок входа в ритуал, тултипы ритма, награды/карточка rewards, персональный инсайт, следующее действие, дневной нудж, сводка энергии — в `RITUAL_COPY` + форматтеры в `todayRitualCopy.ts`; iOS — `TodayWebTodayPageDataCopy`.
- 2026-05-04 | Product | §5.3.1 SoT копирайта Today в трекере | DONE | Подпункт **5.3.1**: канон `todayRitualCopy.ts` ⇄ `TodayRitualCopy.swift`, связь с п.1 UI garbage; перенос «вопроса дня» — см. строку лога «§5.3.1: вопрос дня в каноне».
- 2026-05-04 | Web + iOS Today | §5.3 канон: фокус/риск/план/неделя/«сейчас»/ритм возврата | DONE | `buildDayFocusSummary`, `buildDayRiskSummary`, `buildTodayActionPlan`, `buildTodayCriticalLimits`, `buildWeeklyPatternMap`, `buildLifeNowSummary`, `buildDailyReturnCadence` → `RITUAL_COPY` + форматтеры; расширение `TodayWebTodayPageDataCopy`; без карточки «вопрос дня» (след. инкремент).
- 2026-05-04 | Web + iOS Today | DE-8 v3: глубина narrative на Today | DONE | Веб: `TodayNarrativeDepthControl`, `narrativeDepthSeq` → повторный `postTodayNarrative(guide)`; iOS: `TodayNarrativeDepthInlineBar`, `patchTodayNarrativeDepthLevel`, `preloadAllNarratives(force:)`; якорь настроек `#today-narrative-depth-settings`.
- 2026-05-04 | Backend + Web + iOS | DE-8 v4: learning-сигнал смены глубины | DONE | `today_narrative_depth_changed` в `VALID_EVENT_TYPES`, вес в Mind; клиенты шлют событие после успешного сохранения; pytest `test_post_meaning_events_accepts_narrative_depth_changed`; §4.7 DE-8 → **DONE**.
- 2026-05-04 | Web + iOS | DE-8 v4.1: событие и из формы настроек | DONE | Веб `/account/settings`: `trackMeaningEvent` при фактической смене `today_narrative_depth_level`; iOS `ProfileSettingsView`: `trackTodaySurfaceEvent` + `serverSyncedNarrativeDepth`; `payload.source` `account_settings` / `profile_settings` в [TODAY_PERSONALIZATION_CORE.md](./TODAY_PERSONALIZATION_CORE.md).
- 2026-05-04 | Web + Backend + i18n | OAuth redirect callbacks | DONE | `POST /oauth/google/code`, `GET /oauth/providers.code_exchange_enabled`, колбэки Next `/auth/google/callback`, POST Apple `/auth/apple/callback`; `OAuthButtons` через `getJson`, `state` + i18n `auth.oauth.callback.*`; `.env.example`; pytest в `test_auth.py`; дорожная карта #26.
- 2026-05-04 | Web + iOS | §5.3.1: «вопрос дня» в каноне | DONE | `RITUAL_QUESTION_OF_DAY_*` + `buildRitualQuestionOfDayDefaultCards` в `todayRitualCopy.ts`; `buildQuestionOfDay` — только выбор по дате/энергии/фокусу; `TodayWebQuestionOfDayCopy` в `TodayRitualCopy.swift`; §5.3.1 трекера без остатка по этому пункту.
- 2026-05-04 | iOS | RU/EN аудит (инкремент) | IN_PROGRESS → частично | `AuthView` + `PasswordRecoveryView`: `AuthScreenChrome` по той же схеме, что `CompatibilityScreenChrome`; `ProfileSettingsScreenChrome` — подпись пикера «ты»; `ExploreHubView` — ru/en заголовки и подзаголовки карточек; см. дорожную карту #30. Остаток аудита: онбординг, демо-лейауты, отдельные экраны.
- 2026-05-04 | Web + iOS Today | §5.3 канон: баннеры быстрого ответа / вопроса дня (iOS) | DONE | `RITUAL_COPY` + `TodayWebWorkingLayerCopy`: префиксы баннеров и подпись кнопки сохранения в компактном блоке `TodayView`; паритет формулировок с веб-каноном на будущее.
- 2026-05-04 | Web + iOS Today | §5.3 канон: компактный «быстрый ответ» iOS (полный блок) | DONE | `workingLayerCompactQuickAnswer*` в `todayRitualCopy.ts` и `TodayWebWorkingLayerCopy`; `TodayQuickAnswerSection` без захардкоженного русского.
- 2026-05-04 | Web + iOS Today | §5.3.1: нативные композеры `TodayView` (утро/чек-ин/дневник/вечер) | DONE | `todayView*` + `dayJournalPrompt*` + форматтеры в `todayRitualCopy.ts`; `TodayWebTodayViewComposerCopy` и промпты в `TodayWebDaySectionCopy`; чек-ин — шкалы из `TodayWebEveningSectionCopy`; правка синтаксиса `ringHint*` в `TodayExperienceLayout.swift` (`static var`).
- 2026-05-04 | Web + iOS Today | §5.3.1: `TodayView` герой + панели + таро/fusion | DONE | `TODAY_SHELL_COPY.shell*` + `formatShell*` в `todayRitualCopy.ts`; расширение `TodayShellCopy` и замена литералов в `TodayView.swift`; RU-фолбэки цикла действий вместо EN; подсказки цели (`shellGoalHint*`).
- 2026-05-04 | Web + iOS Today | §5.3.1: четыре сферы + `TodayRitualFlowView` | DONE | `fourArea*` + `ritualFlow*` + `formatFourArea*` / `formatRitualFlow*` в `todayRitualCopy.ts`; `todayFourAreas.ts` на каноне; зеркало в `TodayRitualCopy.swift`; `TodayRitualFlowView` + `RitualFourAreaBuilder` без захардкоженного RU в перечисленных блоках; риск энергии унифицирован с вебом («Напряжение редко…»); настроение `driven` — тот же суффикс, что у мотивации.
- 2026-05-04 | Web + iOS Today | §5.3.1: `TodayExperienceLayout` chrome RU/EN | DONE | `TODAY_EXPERIENCE_CHROME_RU` / `EN` + хелперы в `todayRitualCopy.ts`; `TodayExperienceChromeCopy.swift` + файл в таргете Xcode; `TodayExperienceLayout` без локального `TodayExpChrome`.
- 2026-05-04 | Web + iOS | §5.3.1: Flow / Практики / главный TabView chrome | DONE | TS `flowPracticesMainTabChrome.ts` (+ реэкспорт из `todayRitualCopy.ts`); iOS `FlowPracticesMainTabChromeCopy.swift`, `FlowTrackerChrome.swift` как `typealias`; подписи табов в `ContentView` через `TodayMainTabCopy`.
- 2026-05-04 | Web + iOS | §5.3.1: веб `/tracking/calendar` hero → канон Flow | DONE | `trackingCalendarPage*` в `flowPracticesMainTabChrome.ts` / `FlowTrackerChromeCopy`; страница через `flowTrackerChromeBundle(getLocale())`.
- 2026-05-04 | Web + iOS | §5.3.1: веб `/tracking/progress` хаб → канон Flow | DONE | `trackingProgress*` карточки/футер/логин в `flowPracticesMainTabChrome.ts` + `FlowTrackerChromeCopy`; `progress/page.tsx` на `flowTrackerChromeBundle`.
- 2026-05-04 | Web + iOS | §5.3.1: веб heatmap календаря → канон Flow | DONE | `heatmap*` в `FlowTrackerChromeCopy` / TS; вкладка «Практики» — `practicesExperienceChromeBundle().navPractices`; `CalendarHeatmap.tsx` + `weekdayFallback`; легенда — `heatmapLegend*` (см. также удаление `HEATMAP_LABEL` в трекере 2026-05-04).
- 2026-05-04 | Web + iOS | §5.3.1: heatmap drill + инсайт под картой + сводка категорий | DONE | `heatmapDrillDayCaption*`, `heatmapUnderMapInsight*`, `trackingCatSummary*` в `flowPracticesMainTabChrome.ts` / `FlowTrackerChromeCopy`; `calendarHeatmapModel.ts` + `entityTrackerCompute.categorySummaryLines` принимают `fc`; placeholder сущности в `CalendarHeatmap` из канона.
- 2026-05-04 | Web | `trackingRhythm` — только используемое API | DONE | Оставлены `lineDone` + `computeMarks` + типы; удалены неимпортируемые `buildWhatsHappening`, `computeRhythmBand`, `habitStabilityLabel`, `asceticHoldPhrase`, `practiceAttentionPhrase`.
- 2026-05-04 | Web + iOS | Веб `/habits` — карта привычек → канон Flow | DONE | `habitsMap*` в `flowPracticesMainTabChrome.ts` / `FlowTrackerChromeCopy`; страница на `flowTrackerChromeBundle` + `getLocale()`; тултипы heatmap — `ru-RU`/`en-US`; CTA логина — `trackingProgressHubLoginCta`.
- 2026-05-04 | Web | Мастер сущностей: шаблоны из канона RU/EN | DONE | `trackerEntityCatalog.ts` — типы + `filterAsceticismsByCategory`; данные в `components/today/trackerEntityTemplateCatalog.ts` (`getGoalTemplateGroups` / `getHabitTemplateGroups` / `getAsceticCategoryFilters`); фильтры аскез — объединённые RU+EN `keywords`; `EntityCreateWizard` по `getLocale()`. iOS/Android: при нативном мастере — паритет с этим TS-файлом.
- 2026-05-04 | Web + iOS | §5.3.1: `buildAttentionItems` / `buildBestItems` + heatmap tokens | DONE | `trackingAttention*` / `trackingBest*` в каноне; `entityTrackerCompute` принимает `fc`; удалён неиспользуемый `HEATMAP_LABEL` из `heatmapTokens.ts` (легенда только `heatmapLegend*`).
- 2026-05-04 | Web + iOS | §5.3.1: веб `/tracking/insights` + `/tracking/diary` → канон Flow | DONE | `trackingInsights*`, `trackingInsight*`, `trackingDiary*`, `trackingFormDateLabel`, `diary*Placeholder`, `insightsGeneratingShort`, `saveDiarySaving`, `insightsGenerateErrorFallback`; страницы на `flowTrackerChromeBundle(getLocale())`; даты — `ru-RU`/`en-US`; iOS — `trackingAutoInsightTypeLabel(for:)` + зеркальные строки в `FlowTrackerChromeCopy` (`insightsEmpty`/`insightsIntro` для `RitualsView` без изменения смысла).
- 2026-05-04 | Web + iOS | §5.3.1: веб `/tracking/calendar` page toasts + empty/login | DONE | `trackingCalendarEmptyState`, `trackingCalendarLoginPrompt`, `trackingToast*` в `flowPracticesMainTabChrome.ts` + `FlowTrackerChromeCopy`; `calendar/page.tsx` на `flowTrackerChromeBundle`.
- 2026-05-04 | Web + iOS | §5.3.1: веб `TrackerView` + `EntityCreateWizard` → канон Flow | DONE | `actionSave`/`actionCancel`, `habitSheetTitle`, `trackingEntityWizard*`, `trackingView*`; `practicesExperienceChromeBundle` для `navPractices`; даты полосы дней — `ru-RU`/`en-US`; зеркало в `FlowTrackerChromeCopy`.
- 2026-05-04 | Web + iOS | §5.3.1: веб `/affirmations` → канон Flow | DONE | `affirmations*` в `flowPracticesMainTabChrome.ts` / `FlowTrackerChromeCopy` (герой, фильтры, фокусы, каталог, CTA, `detectFocus` + EN-регэкспы); страница на `flowTrackerChromeBundle(getLocale())`.
- 2026-05-04 | Web + iOS | §5.3.1: веб `/affirmations/tracker` → канон Flow | DONE | `affirmationsTracker*` + реюз `trackingFormDateLabel`, `trackingDiaryEntriesHeading`, `actionSave`, `saveDiarySaving`, `trackingDiarySaveError`, `trackingProgressHubLoginCta`, `affirmationsLibraryLinkTracker`; даты `ru-RU`/`en-US`; зеркало в `FlowTrackerChromeCopy`.
- 2026-05-04 | Web + iOS | §5.3.1: веб `/practices` каталог (мастер) | DONE | `practicesCatalog*` в `PRACTICES_EXPERIENCE_CHROME_*` / `PracticesExperienceChromeCopy`; цели и направления + ключевые слова фильтра в `practicesCatalogContent.ts` (RU-ключи направлений для матчинга API); страница на `practicesExperienceChromeBundle(getLocale())`; `inferPracticeDefaultsFromJTBD` типизирует `PracticeCatalogDirectionKey`.
- 2026-05-04 | Web + iOS | §5.3.1: веб `/practices/[id]` карточка практики | DONE | `practiceDetail*` + `practicePatternAxisA1`–`A7` в `PRACTICES_EXPERIENCE_CHROME_*` / `PracticesExperienceChromeCopy`; реюз `stepsDoneLabel`, `practicesCatalogDifficulty*`; убран неиспользуемый `useRouter`/`PatternLink`/`currentStepNumber`.
- 2026-05-04 | Web + iOS | §5.3.1: веб `/practices/history` | DONE | `practicesHistory*` + реюз `historyProgressTitle`, `statistics`, `stat*`, `completedPractices`, `navHistory`, `repeatCta`, `practiceDetailBackLink`; даты `ru-RU`/`en-US`; зеркало в `PracticesExperienceChromeCopy`.
- 2026-05-04 | Web + iOS | Веб `/guidance/history` | DONE | Канон `guidanceHistoryChrome.ts` ⇄ `GuidanceHistoryChromeCopy` + `typealias GuidanceHistoryChrome`; страница без `t()`; `guidance.history.filtersAria` в `app.ru.json`/`app.en.json` (паритет с каноном).
- 2026-05-04 | Web | Guidance history: один вход по локали | DONE | `guidanceHistoryPageBundle.ts` — `guidanceHistoryPageBundle(locale)` = `chrome` + `catalogLocale` + `formatHistoryDate` (`ru-RU`/`en-US`); `/guidance/history/page.tsx` собирает хром и каталог из одного бандла (паритет с `guidanceHubPageBundle`).
- 2026-05-04 | Web + iOS | Веб `/guidance` (хаб расклада) | DONE | Канон `guidanceHubChrome.ts` ⇄ `GuidanceHubChromeCopy` + `typealias GuidanceHubChrome`; `guidanceHubInterpolate` для `{startOver}` / `{question}` / `{spreadTitle}`; страница на `guidanceHubChromeBundle`; `auth.login.title` остаётся в `t()`; строки = `nav.guidance.hub` + `guidance.page.*` в JSON.
- 2026-05-04 | Web + iOS | Веб `/tarot/result` — канон строк | DONE | `tarotSpreadResultChrome.ts` ⇄ `TarotSpreadResultChromeCopy.swift` + `typealias TarotSpreadResultChrome`; ключи `tarot.spreadResult.*` в `app.ru.json`/`app.en.json`; страница на `tarotSpreadResultChromeBundle` + `tarotSpreadResultResolvePositionLabel` (позиции past…outcome).
- 2026-05-04 | Web + iOS | Guidance: результат разбора + полоса карт + `GuidanceResultCard` | DONE | `guidanceResultChrome.ts` ⇄ `GuidanceResultChromeCopy.swift` + `typealias GuidanceResultChrome`; ключи `guidance.result.*`, `guidance.strip.*`, `guidance.resultCard.*` в `app.ru.json`/`app.en.json`; `stripTarotAppendFromExplanation` (RU+EN); подсказка совместимости по EN-регэкспу для `relationships`.
- 2026-05-04 | Web + iOS | Guidance: безопасность вопроса + подпись селекта расклада | DONE | `guidanceSafetyKeywords` — RU + EN (фразы + `\brape\b`); зеркало `GuidanceSafetyKeywords.swift`; `guidanceHubSpreadField` в `guidanceHubChrome.ts` ⇄ `GuidanceHubChromeCopy` (паритет `guidance.catalog.spreadField`).
- 2026-05-04 | Web + iOS + Android | Guidance: эвристики вынесены из UI | DONE | `guidanceResultLoveQuestionHeuristic` / `guidanceResultShowCompatHint` в `guidanceResultChrome.ts`; зеркало `GuidanceResultChromeCopy`; Android `GuidanceQuestionHeuristics.kt` (`GuidanceSafetyKeywords`, `GuidanceCompatHint`) — паритет с вебом/iOS (в репо нет `gradlew`; проверка `:app:compileDebugKotlin` — при настроенном Gradle).
- 2026-05-04 | Web + iOS | Guidance hub: группы раскладов в каноне хаба | DONE | `guidanceHubCatalogSectionQuick|Medium|Deep` + `guidanceHubSpreadSectionLabelsFromBundle` в `guidanceHubChrome.ts`; `/guidance` на этом каноне; удалён неиспользуемый `localizedGuidanceSectionLabels` из `catalog.ts`; iOS `GuidanceHubChromeCopy` + реюз в `GuidanceViewChrome.spreadSection*`.
- 2026-05-04 | Web | Guidance hub: единый бандл каталога мастера | DONE | `guidanceHubWizardCatalog.ts` — `guidanceHubWizardCatalogBundle(locale)` (расклады, темы, исходы, уточнение, роли, intimacy); `/guidance/page.tsx` один `useMemo` вместо шести; строки по-прежнему из `catalog.ts` / `guidance.catalog.*`.
- 2026-05-04 | Web | Guidance hub: один вход по локали | DONE | `guidanceHubPageBundle.ts` — `guidanceHubPageBundle(locale)` = `chrome` + `wizardCatalog` + `spreadSectionLabels`; `/guidance/page.tsx` один `useMemo` на страницу для хаба.
- 2026-05-04 | Web + iOS | §5.3.1: сводка трекера (`entityTrackerSpec` / `MARK_TODAY`) → канон | DONE | `trackingCategory*`, `trackingScreenHero*`, `trackingStatus*`, `trackingMarkToday*`, `trackingViewLimitsHint`, `trackingViewTodayLinkHint`; `entityTrackerSpec.ts` — только типы + `FREE_LIMITS`/`PRO_LIMITS`; `MARK_TODAY` убран из `trackerSpec.ts`.
- 2026-05-04 | Web | `trackerSpec` / `trackerCompute` — вырезан мёртвый слой | DONE | `trackerSpec.ts` — только `TrackerTier` + `DEFAULT_TRACKER_TIER`; из `trackerCompute.ts` оставлен `sliceLastNDaysSorted` (остальные вычисления и RU-строки нигде не импортировались). Новый UI-инсайт — через канон Flow, не через старые таблицы.
- 2026-05-04 | Tooling | iOS Xcode открытие проекта | DONE | Восстановлен `TodayFlow.xcodeproj/project.xcworkspace/contents.xcworkspacedata` (обязательный файл пакета).
- 2026-05-04 | Full-stack Today | O6: низкий ресурс настроения (tired/heavy/quiet_wish) | DONE | Промпт `LOW_RESOURCE` / `РЕЖИМ_НИЗКИЙ_РЕСУРС` + metadata `low_energy_ritual_mood`; веб/iOS — один шаг фокуса, меньше CTA, без недели в day history / без чипов build-day; Jest `isLowEnergyRitualMood`; pytest system prompt; [TODAY_LANGUAGE_V1.md](today-language/TODAY_LANGUAGE_V1.md) O6.
- 2026-05-04 | Backend Today narrative | O8: day_layer без «простыни» и дубля anchor | DONE | `_finalize_day_layer_payload_o8` после LLM и на cache hit; лимиты `nudge` / `personal_insight_*` / chips; снятие дословного префикса `anchor_summary`; доп. строки в `_DAY_SYS`; pytest `test_o8_finalize_day_layer_*`; [TODAY_LANGUAGE_V1.md](today-language/TODAY_LANGUAGE_V1.md) #35.
- 2026-05-04 | Web + iOS Today | O9: один канонический главный шаг + CTA «К шагу дня» | DONE | `guideCanonicalPrimaryStepLine` в `todayGuideActionable.ts` / Jest; `TodayGuideSection` + `RITUAL_COPY.guidePrimaryNavigateCta`; iOS `TodayGuideActionable.guideCanonicalPrimaryStepLine`, `TodayGuidePanel.guideExecutionDoItems`, `TodayWebGuideSectionCopy.guidePrimaryNavigateCta`; [TODAY_LANGUAGE_V1.md](today-language/TODAY_LANGUAGE_V1.md) #36 / O9.
- 2026-05-04 | Full-stack Today | O10: мета-комментарий LLM — расширение паттернов + day_layer | DONE | `ritual_cue_sanitize._LLM_META_NEEDLES`, `strip_meta_from_guide_payload` (доп. поля `core_message`); `_finalize_day_layer_payload_o8` + `strip_llm_meta_commentary`; паритет `ritualCueSanitizer.ts`, `TodayRitualCueSanitizer`, `RitualCueSanitizer.kt` + тесты; pytest / Jest / JUnit; дорожная карта #37 / O10.
- 2026-05-04 | Backend Today narrative | O1 (guide): дедуп hero vs тезис | DONE | `_dedupe_guide_payload_cross_fields`: очистка `headline`/`subline` при `_texts_semantically_redundant` с `core_message.body` и `anchor_summary`; subline при дубле headline; pytest `test_o1_top_level_hero_cleared_when_redundant_with_core_body_and_brief_anchor`, `test_o1_subline_cleared_when_redundant_with_headline_only`; дорожная карта #38 / O1.
- 2026-05-04 | Full-stack Today | O3: RU gate заголовка `day_layer` | DONE | `is_ru_abstract_topic_headline`, расширение `_TOPIC_LABELS_NOT_ACTIONS`; `_day_layer_payload_concrete` (мин. 12 символов для `personal_insight_title`); pytest `test_text_quality`, `test_ritual_cue_sanitize`; паритет `isRuAbstractTopicHeadline` / `TodayRitualCueSanitizer` / `RitualCueSanitizer.kt`; Jest `ritualCueSanitizer.test.ts`; дорожная карта #39 / O3.
- 2026-05-04 | Backend Today narrative | O4 + кэш guide / dedupe hero | DONE | При непустом `ritual_norm` RU — `_guide_payload_links_ritual_context` (иглы tarot/число/mood/head_topic/day_events); `_dedupe_guide_payload_cross_fields`: не снимать `headline` только из‑за `anchor_summary` (совместимо с `_guide_payload_concrete` и повторной валидацией кэша); EN — не обнулять `headline` при overlap с `core_message.body`; pytest `test_o4_*`, `test_guide_narrative_cache_hit_when_day_context_unchanged`, EN fallback; дорожная карта #40 / O4.
- 2026-05-04 | Full-stack Today | O5: кавычечные EN slug → RU подпись | DONE | `replace_quoted_en_slugs_for_ru_display` в `ritual_cue_sanitize` (spine + recommendations); паритет TS / Swift / Kotlin + `repairRitualDoNotEnterLine`; веб — `todayRitualSignals`, `todayPageUtils`; pytest / Jest / JUnit; дорожная карта O5.
- 2026-05-04 | Backend + Web + iOS Today | O7: «Ритм и вчера» без ложных баллов | DONE | `history_layer_v0`: `trailing_7d_summary_trustworthy`, `trailing_7d_flow_days`; при `fusion_score_delta_trustworthy=false` — одна строка без «Вчера: …», скрытие `trailing_7d` при нуле дней с Flow; веб `formatFusionDayHistory*`, `TodayDayHistoryStrip.footerHint`, `isFusionDayHistoryDeltaUntrustworthy`; iOS `FusionDayHistoryV0` + `fusionDayHistoryStrip`; pytest `test_history_layer_v0`, Jest `formatFusionDayHistory`; дорожная карта O7.
- 2026-05-04 | Backend + Web + iOS Today | O11: сферы и rhythm_context | DONE | `_rhythm_context_signal_categories`, `_spheres_payload_grounded_in_rhythm`, расширение `_SPHERES_SYS`; `_spheres_payload_concrete(..., rhythm_context)`; веб `computeSphereScoresProvisional`, `areasScoresProvisionalHint`, префикс `≈` у %; iOS `sphereScoresProvisional` + тот же копирайт; pytest `test_o11_spheres_rhythm_grounding.py`, Jest `todayFourAreas.test.ts`; дорожная карта O11.
- 2026-05-04 | Backend Today | O12: merge-pass в метаданных оркестратора | DONE | `ORCHESTRATOR_VERSION` 0.3.0, `MERGE_PASS_CONTRACT`, `narrative_merge_pass_plan`, поля `merge_pass_steps` / `primary_narrative_anchor` / стадия `merge_pass_documented` в `build_today_narrative_orchestration_meta`; pytest `test_generation_orchestrator.py`, расширение `test_today_narrative_contract`; дорожная карта O12.
- 2026-05-04 | Full-stack Today | O2: явный primary в payload guide | DONE | `narrative_hierarchy` (`narrative_hierarchy_v0`, `primary_anchor` = `day_engine_brief`) на cache hit и свежей генерации; `todayNarrativeApi` / `parseNarrativeHierarchyFromGuide` + Jest; iOS `TodayGuideActionable.narrativeHierarchyDisplay`; Android каркас `GuideNarrativeHierarchy.kt` + `GuideNarrativeHierarchyTest`; `DAY_CONTEXT_V0.md`; pytest `test_today_narrative_contract`, `test_today_narrative_day_layer_logs_day_context_hash`; дорожная карта O2 / #41.
- 2026-05-04 | Web + iOS | P1 RU: Guidance → «Разбор» в пользовательском тексте | DONE | `TODAY_MAIN_TAB_COPY_RU.guidance` = «Разбор» (`flowPracticesMainTabChrome.ts`); `GuidanceViewChrome` — заголовок «Центр разборов», фильтры/история/режимы без латиницы; `TodayExperienceChromeCopy` + `todayRitualCopy` (`TODAY_EXPERIENCE_CHROME_RU`, тост `todayToastGuidanceFollowup`); `ExploreHubView` секция; `CompatibilityView` CTA; кнопки ритуала → `TodayMainTabCopy.flow`; паритет TS ⇄ Swift.
- 2026-05-04 | Web | P1: `/guidance` и `/guidance/history` через `t()` + каталоги | DONE | Ключи `guidance.page.*`, `guidance.history.*` в `CONTENT/i18n/app.ru.json` / `app.en.json`; eyebrow = `nav.guidance.hub`; RU без латинского «Guidance» в UI; EN — полные строки; даты истории `ru-RU` / `en-US` по `getLocale()`.
- 2026-05-31 | Product / Economy | User Evolution + Gamification + Symbolic Commerce canons | DONE | [USER_MODEL_TARGET_STATE.md](pim/USER_MODEL_TARGET_STATE.md), [USER_MODEL_TARGET_STATE.md](pim/USER_MODEL_TARGET_STATE.md), [REFERENCE_LAYER_AND_BUILD_ORDER.md](./REFERENCE_LAYER_AND_BUILD_ORDER.md): Personal Path, PEG, cycles, stage→API, symbolic reference.
- 2026-05-31 | Product / Architecture | User Model Target State (north star) | DONE | [USER_MODEL_TARGET_STATE.md](pim/USER_MODEL_TARGET_STATE.md): 4 outputs, Compact User Model, uncertainty metric, UMTS filter, stop infinite layering.
- 2026-05-31 | Product / Architecture | Interpretation Layer & Reference canon | DONE | [INTERPRETATION_LAYER_AND_REFERENCE.md](explainability/INTERPRETATION_LAYER_AND_REFERENCE.md): Interpretation Reference, Engine, Instance, taxonomy×10, L1–L4, Signal→Interpretation→Knowledge.
- 2026-05-31 | Product / Architecture | Knowledge Acquisition & Signal Policy | DONE | [KNOWLEDGE_ACQUISITION_AND_SIGNAL_POLICY.md](./KNOWLEDGE_ACQUISITION_AND_SIGNAL_POLICY.md): channels A–I, trust T1–T5, fact/pattern/hypothesis, Event→Signal→Confirmation→Knowledge; UKM v1.1 fields.
- 2026-05-31 | Product / Architecture | User Knowledge Model canon | DONE | [USER_KNOWLEDGE_MODEL.md](pim/USER_KNOWLEDGE_MODEL.md): Knowledge Atoms, Events→Signals→Knowledge→Memory→Context; UKM before Gate; proto-code `meaning_surface_patterns_v0`.
- 2026-05-31 | Product / Architecture | API Memory & Learning Layer canon | DONE | [API_MEMORY_AND_LEARNING_LAYER.md](./API_MEMORY_AND_LEARNING_LAYER.md): LLM Call Gate, Request/Response/Reaction records, cache/reuse, Learning Signals, dataset status, token ROI; links PIL + generation_logs baseline.
- 2026-05-31 | Product / Architecture | PIL v2 — сквозной learning-aware канон | DONE | [PERSONAL_INTELLIGENCE_LAYER.md](pim/PERSONAL_INTELLIGENCE_LAYER.md) v2: Every feature must be learning-aware; два выхода; Global Build Order 1–12; Training Dataset; freeze без PIL; cursor rule `personal-intelligence-layer.mdc`.
- 2026-05-31 | Product / Architecture | Personal Intelligence Layer canon | DONE | [PERSONAL_INTELLIGENCE_LAYER.md](pim/PERSONAL_INTELLIGENCE_LAYER.md): events→memory→retrieval→prompt refinement→orchestrator→evaluation→feedback; maturity path to fine-tuning; LLM denylist; code baseline map.
- 2026-05-31 | Product / Architecture | Data ownership & consumption map | DONE | [DATA_OWNERSHIP_AND_CONSUMPTION_MAP.md](./DATA_OWNERSHIP_AND_CONSUMPTION_MAP.md): CD/DD/SN/RT, chain Reference→Behavior, CoreProfile/DayContext boundaries, API read model, LLM/UI policies.
- 2026-05-31 | Product / Architecture | Ontology & foundation phases canon | DONE | [ONTOLOGY_AND_FOUNDATION_PHASES.md](./ONTOLOGY_AND_FOUNDATION_PHASES.md): 5 phases (Knowledge→Rules→Intelligence→LLM→Own Model); current stage = world ontology; consumer/API/UI freeze; maps P0 + PIL to phases.
- 2026-05-31 | Product / Architecture | Data origination & lifecycle canon | DONE | [DATA_ORIGINATION_AND_LIFECYCLE.md](./DATA_ORIGINATION_AND_LIFECYCLE.md): six-level build order, creation methods, nine-field entity template, registry v1, filling policy, data-first freeze (no screen/API-first planning).
- 2026-06-01 | Product / Architecture | Branch B Evolution Engine — architecture closed at B1.5 | DONE | contracts CD only; B1.6 deferred; primary signal supplier = Branch C; [status/branch_b_evolution_engine.md](./status/branch_b_evolution_engine.md).
- 2026-06-01 | Product / Architecture | Branch D1.0 Symbolic Asset Ontology | DONE | Symbolic Asset ≠ Product; entities only; deps A/B/C/E ready; [SYMBOLIC_ASSET_ONTOLOGY.md](./SYMBOLIC_ASSET_ONTOLOGY.md); next D1.1.
- 2026-06-01 | Backend / Contract | Branch D1.1 Symbolic Asset Definition Registry | DONE | 40 canonical objects; no associations/commerce; validator+loader+11 tests; [SYMBOLIC_ASSET_REGISTRY.md](./SYMBOLIC_ASSET_REGISTRY.md); next D1.2.
- 2026-06-01 | Backend / Contract | Branch D1.2 Symbolic Asset Association Registry | DONE | 88 contextual links; cross-ref D1.1+B1.1+C1.1+C1.6+E1.5; no recommendations; [SYMBOLIC_ASSET_ASSOCIATION_REGISTRY.md](./SYMBOLIC_ASSET_ASSOCIATION_REGISTRY.md); next D1.3.
- 2026-06-01 | Backend / Contract | Branch D1.3 Symbolic Collection Registry | DONE | 16 curated collections; cross-ref D1.1+D1.2; no shop/commerce; [SYMBOLIC_ASSET_COLLECTION_REGISTRY.md](./SYMBOLIC_ASSET_COLLECTION_REGISTRY.md); next D1.4.
- 2026-06-01 | Backend / Contract | Branch D1.4 Symbolic Visibility Policy | DONE | B1.13+E1.7→D1.1/D1.3 caps; no recommendation/commerce activation; [SYMBOLIC_VISIBILITY_POLICY.md](./SYMBOLIC_VISIBILITY_POLICY.md); next D1.5.
- 2026-06-01 | Backend / Reference | Branch C1.8 Practice Selection Ranker | DONE | deterministic rank+trace; C1.7+B1.11; 12 tests; [PRACTICE_SELECTION_RANKER.md](./PRACTICE_SELECTION_RANKER.md); next FIRST_DAY_DOD_GAP_ANALYSIS.
- 2026-06-01 | Backend / Reference | Branch C1.7 Practice Context Association Registry | DONE | 120 context→practice edges; 5 negative; validator+loader+16 tests; [PRACTICE_CONTEXT_ASSOCIATION_REGISTRY.md](./PRACTICE_CONTEXT_ASSOCIATION_REGISTRY.md).
- 2026-06-01 | Product / Architecture | Generation order & budget canon | DONE | 7-step foundation path; 0–2 LLM/day Today; evening separate; cache horoscope/tarot/month; [API_MEMORY_AND_LEARNING_LAYER.md](./API_MEMORY_AND_LEARNING_LAYER.md).
- 2026-06-01 | Product / Architecture | Reference Inventory & Consumption Map | DONE | Per-domain CD counts, prod vs tests readers, Today wire constraints; [REFERENCE_INVENTORY_AND_CONSUMPTION_MAP.md](./REFERENCE_INVENTORY_AND_CONSUMPTION_MAP.md); wire paused → enrichment first.
- 2026-06-01 | Product / Architecture | System Map & Data Flow | DONE | Unified A–E+P map; runtime + LLM chains; Today slice; stop rules; freeze new branches; [DATA_OWNERSHIP_AND_CONSUMPTION_MAP.md](./DATA_OWNERSHIP_AND_CONSUMPTION_MAP.md); next Today vertical slice.
- 2026-06-01 | Product / Architecture | Surface Layer S1.1 Today Intelligence Read Model | DONE | Projection spec; builder + validator; no prod consumer yet; [SCREEN_CONTRACTS_V1.md](./SCREEN_CONTRACTS_V1.md).
- 2026-06-01 | Product / Architecture | Surface Layer S1.0 Read Model Ontology | DONE | Five read-only surfaces over A–E; policy stack; no commerce/LLM/mutations; [PRODUCT_SURFACE_READ_MODEL_ONTOLOGY.md](./PRODUCT_SURFACE_READ_MODEL_ONTOLOGY.md); next S1.1 Today.
- 2026-06-01 | Backend / Contract | Branch D1.5 Symbolic Commerce Separation | DONE | SKU→asset refs only; separation policy; Branch D complete; [SYMBOLIC_COMMERCE_SEPARATION_LAYER.md](./SYMBOLIC_COMMERCE_SEPARATION_LAYER.md).
- 2026-06-01 | Backend / Contract | Branch E1.7 Calendar Consumer Policies | DONE | B1.12→E visibility caps; redact/block artifacts; [CALENDAR_INTELLIGENCE_CONSUMER_POLICIES.md](./CALENDAR_INTELLIGENCE_CONSUMER_POLICIES.md); Branch E complete.
- 2026-06-01 | Backend / Contract | Branch E1.6 Calendar Knowledge/Evolution Bridge | DONE | pattern→knowledge candidate + progression context; no stage/profile/memory; [CALENDAR_KNOWLEDGE_EVOLUTION_BRIDGE.md](./CALENDAR_KNOWLEDGE_EVOLUTION_BRIDGE.md); next E1.7.
- 2026-06-01 | Backend / Contract | Branch E1.5 Rhythm Pattern Confirmation Gate | DONE | candidate→pattern gate; no insight/recommendation; [CALENDAR_RHYTHM_PATTERN_CONFIRMATION.md](./CALENDAR_RHYTHM_PATTERN_CONFIRMATION.md); next E1.6.
- 2026-06-01 | Backend / Contract | Branch E1.4 Rhythm Pattern Candidate | DONE | detect repetition signals; threshold gate; no confirmation/recommendation; [CALENDAR_RHYTHM_PATTERN_CANDIDATE_CONTRACT.md](./CALENDAR_RHYTHM_PATTERN_CANDIDATE_CONTRACT.md); next E1.5.
- 2026-06-01 | Backend / Contract | Branch E1.3 Calendar Month Map Contract | DONE | aggregate day records; no inference; [CALENDAR_MONTH_MAP_CONTRACT.md](./CALENDAR_MONTH_MAP_CONTRACT.md); next E1.4.
- 2026-06-01 | Backend / Contract | Branch E1.2 Calendar Signal Ingestion | DONE | verified artifacts → day record marks; idempotent; [CALENDAR_SIGNAL_INGESTION.md](./CALENDAR_SIGNAL_INGESTION.md); next E1.3.
- 2026-06-01 | Backend / Contract | Branch E1.1 Calendar Day Record Contract | DONE | user×date atom; refs/facts only; [CALENDAR_DAY_RECORD_CONTRACT.md](./CALENDAR_DAY_RECORD_CONTRACT.md); next E1.2.
- 2026-06-01 | Product / Architecture | Branch E1.0 Calendar Intelligence Ontology | DONE | archive + rhythm engine; entities only; [CALENDAR_INTELLIGENCE_ONTOLOGY.md](./CALENDAR_INTELLIGENCE_ONTOLOGY.md); next E1.1.
- 2026-06-01 | Backend / Contract | Branch B1.14 Evolution Consumer Metrics | DONE | read-only observability; all 6 consumers; [EVOLUTION_CONSUMER_METRICS.md](./EVOLUTION_CONSUMER_METRICS.md); Branch B wiring complete.
- 2026-06-01 | Backend / Contract | Branch B1.13 Evolution → Commerce Visibility Policy | DONE | visibility only; no targeting/recommendation; [EVOLUTION_COMMERCE_VISIBILITY_POLICY.md](./EVOLUTION_COMMERCE_VISIBILITY_POLICY.md); next B1.14.
- 2026-06-01 | Backend / Contract | Branch B1.12 Evolution → Calendar Runtime Policy | DONE | depth/visibility cap only; no insights; [EVOLUTION_CALENDAR_RUNTIME_POLICY.md](./EVOLUTION_CALENDAR_RUNTIME_POLICY.md); next B1.13.
- 2026-06-01 | Backend / Contract | Branch B1.11 Evolution → Practice Selector Filter | DONE | cap/filter only; no final selection; [EVOLUTION_PRACTICE_SELECTOR_FILTER.md](./EVOLUTION_PRACTICE_SELECTOR_FILTER.md); next B1.12.
- 2026-06-01 | Backend / Contract | Branch B1.10 Evolution Day Presentation Envelope | DONE | presentation envelope only; DayModel unchanged; [EVOLUTION_DAY_PRESENTATION_ENVELOPE.md](./EVOLUTION_DAY_PRESENTATION_ENVELOPE.md); next B1.11.
- 2026-06-01 | Backend / Contract | Branch B1.9 Evolution → Context Selector Wiring | DONE | cap-only AK/memory/context limits; no force-expand; [EVOLUTION_CONTEXT_SELECTOR_WIRING.md](./EVOLUTION_CONTEXT_SELECTOR_WIRING.md); next B1.10.
- 2026-06-01 | Backend / Contract | Branch B1.8 Evolution → LLM Gate Wiring | DONE | cap-only slice wire-in; no force-call; [EVOLUTION_LLM_GATE_WIRING.md](./EVOLUTION_LLM_GATE_WIRING.md); next B1.9.
- 2026-06-01 | Backend / Contract | Branch B1.7 Evolution Effect Consumer Map | DONE | six consumers; slice-only read; no full policy; [EVOLUTION_EFFECT_CONSUMER_MAP.md](./EVOLUTION_EFFECT_CONSUMER_MAP.md).
- 2026-06-01 | Backend / Contract | Branch B1.6 Evolution Effect Runtime Policy | DONE | B1.5→allowed/blocked effects; gate-gated unlocks; no promotion/commerce activation; [EVOLUTION_EFFECT_RUNTIME_POLICY.md](./EVOLUTION_EFFECT_RUNTIME_POLICY.md); next B1.7.
- 2026-06-01 | Backend / Contract | Branch C2.4 Runtime Signal Metrics | DONE | read-only counts/distributions; window-scoped; [PRACTICE_RUNTIME_SIGNAL_METRICS.md](./PRACTICE_RUNTIME_SIGNAL_METRICS.md); unblocks B1.6.
- 2026-06-01 | Backend / Contract | Branch C2.3 Practice Runtime Trace Map | DONE | audit layer event→ES; read-only; snapshot ref helpers; [PRACTICE_RUNTIME_TRACE_MAP.md](./PRACTICE_RUNTIME_TRACE_MAP.md); next C2.4.
- 2026-06-01 | Backend / Contract | Branch C2.2 Runtime Event→Emission Bridge | DONE | event→emission→B1.3; ascetic blocked; trace IDs; [PRACTICE_RUNTIME_EVENT_EMISSION_BRIDGE.md](./PRACTICE_RUNTIME_EVENT_EMISSION_BRIDGE.md); next C2.3.
- 2026-06-01 | Backend / Contract | Branch C2.1 Practice Runtime Event Contracts | DONE | six event kinds; validators; C2.0 path check; ascetic pending-only; [PRACTICE_RUNTIME_EVENT_CONTRACT.md](./PRACTICE_RUNTIME_EVENT_CONTRACT.md); next C2.2.
- 2026-06-01 | Backend / Contract | Branch C2.0 Practice Runtime Signal Emitter | DONE | CD→B1.3 bridge; no promotion/state/score; ascetic blocked; [PRACTICE_RUNTIME_SIGNAL_EMITTER_CONTRACT.md](./PRACTICE_RUNTIME_SIGNAL_EMITTER_CONTRACT.md); next C2.1.
- 2026-06-01 | Product / Architecture | Branch C Practice System — CD complete C1.0–C1.6 | DONE | all six entity registries; [status/branch_c_practice_system.md](./status/branch_c_practice_system.md); runtime emitters next.
- 2026-06-01 | Backend / Reference | Branch C1.6 Cycle Definition Registry | DONE | 8 temporal programs; components C1.1–C1.5; [CYCLE_REGISTRY.md](./CYCLE_REGISTRY.md).
- 2026-06-01 | Backend / Reference | Branch C1.5 Ritual Definition Registry | DONE | 8 containers; components → C1.1/C1.2/C1.4; [RITUAL_REGISTRY.md](./RITUAL_REGISTRY.md); next C1.6 Cycle.
- 2026-06-01 | Backend / Reference | Branch C1.4 Ascetic Definition Registry | DONE | 10 restrictions; produces_signals empty; safety rules; [ASCETIC_REGISTRY.md](./ASCETIC_REGISTRY.md); next C1.5 Ritual.
- 2026-06-01 | Backend / Reference | Branch C1.3 Goal Definition Registry | DONE | 10 outcomes; weekly/milestone/long_horizon; produces_signals → B1.3; [GOAL_REGISTRY.md](./GOAL_REGISTRY.md); next C1.4 Ascetic.
- 2026-06-01 | Backend / Reference | Branch C1.2 Habit Definition Registry | DONE | 10 habits → C1.1; produces_signals → B1.3; [HABIT_REGISTRY.md](./HABIT_REGISTRY.md); next C1.3 Goal.
- 2026-06-01 | Backend / Reference | Branch C1.1 Practice Definition Registry | DONE | 10 action types; produces_signals → B1.3; not content/variants; [PRACTICE_REGISTRY.md](./PRACTICE_REGISTRY.md); next C1.2 Habit.
- 2026-06-01 | Product / Architecture | Branch C1.0 Practice Ontology | DONE | Practice, Habit, Goal, Ascetic, Ritual, Cycle; signal map to B1.3; [PRACTICE_ONTOLOGY.md](./PRACTICE_ONTOLOGY.md); next C1.1.
- 2026-06-01 | Backend / Reference | Branch B1.5 Evolution Product Effects Registry | DONE | per-stage intelligence/engine/unlock/commerce effects; [EVOLUTION_PRODUCT_EFFECTS_REGISTRY.md](./EVOLUTION_PRODUCT_EFFECTS_REGISTRY.md); next Branch C.
- 2026-06-01 | Product | Phase 3 Core Loop Viability Test | ACTIVE | [CORE_LOOP_VIABILITY_TEST.md](./CORE_LOOP_VIABILITY_TEST.md): experiment not UI; Variant A/B; instrument=G1-surface; freeze enrichment until verdict.
- 2026-06-01 | Product / Web | G1-surface instrument | DONE | `/today?core_loop=1` / `?first=1`: Theme+Action+Progress без ritual gate; Test B rubric §6.3 + anti-cheat §4.
- 2026-06-01 | Product | Test B pulse 1 procedure | DONE | [CORE_LOOP_VIABILITY_TEST.md](./CORE_LOOP_VIABILITY_TEST.md) v1.2: 2–3 users; Q4 commit; S1–S4; F1–F4 breakpoints; no iOS/checklist before pulse 1.
- 2026-06-01 | Product | Profile serves Today canon | DONE | PROFILE_SCREEN_ARCHITECTURE §0.1; Identity=Operating Manual; exploration ≠ core.
- 2026-06-01 | Product | Phase 1 partial accept v0.2 | ACTIVE | Traits-first; 28 canon ✅; archetypes/formula ⬜; validation backlog.
- 2026-06-01 | Product | Profile cards 1–6 accept v1.11 | DONE | Card 6 portrait; all cards closed.
- 2026-06-01 | Product | Card 6 three axes v1.10 | DONE | superseded by v1.11 portrait UX.
- 2026-06-01 | Product | L1 Profile Cards spec v1.8 | DONE | review gate; engineering paused.
- 2026-06-01 | Product | Profile Data Inventory v1.0 | DONE | PROFILE_DATA_INVENTORY.md: 5 source layers; per-element table; before screen wire.
- 2026-06-01 | Product | Profile user cards v1.7 | DONE | 8 cards §3.1; screen canon parked until data inventory accepted.
- 2026-06-01 | Product | Explain Meaning v1.1 voice ban | DONE | EXPLAIN_MEANING_NOT_MECHANISM: four copy types; system/algorithm ban; Profile unveiling; gamification metaphors.
- 2026-06-01 | Product | Profile three-entity split | DONE | PROFILE_SCREEN_ARCHITECTURE §0.3; interest nav §4.1; GPS §0.1 two scales.
- 2026-06-01 | Product | SCREEN_BLOCK_DEFINITION v1.5 | ACTIVE | Interest tiles Day 1; I/R/D chips; system blocks ≠ layout.
- 2026-06-01 | Product | Profile Identity v1.4 | ACTIVE | Operating Manual question; Today-serving trait filter.
- 2026-06-01 | Product | Profile block definition v1.2 | DONE | Foundation→I/I/R/D Day 1; pipeline §2.1.
- 2026-06-01 | Product / Architecture | Profile Build Pipeline v1.1 | DONE | Predictability; canon matrix §6; LLM allow/deny.
- 2026-06-01 | Product | Minimal Cycle Viability gate | DONE | [MINIMAL_CYCLE_VIABILITY.md](./MINIMAL_CYCLE_VIABILITY.md) → pointer to Core Loop test.
- 2026-06-01 | Product / Architecture | Decision Source of Truth Map | DONE | [DECISION_PIL_MAP.md](./DECISION_PIL_MAP.md).
- 2026-06-01 | Product | Block Data Requirements | DONE | [BLOCK_DATA_REQUIREMENTS.md](./BLOCK_DATA_REQUIREMENTS.md): by user decision D1–D28; min/enrich/forbidden; Day1/7/30 maturity matrix.
- 2026-06-01 | Product | Screen Block Purposes | DONE | [SCREEN_BLOCK_PURPOSES.md](./SCREEN_BLOCK_PURPOSES.md): 52 sections → user decision; existence audit.
- 2026-06-01 | Product | Screen Content Map pass 1 | DONE | [SCREEN_CONTENT_MAP.md](./SCREEN_CONTENT_MAP.md): sections for all 9 screens; cross-screen index §10.
- 2026-06-01 | Product | TC-D Core Trait Definition | DONE | Admission criterion + Card 1 phrasing test; before TC0 catalog; [PROFILE_TODAY_DOMAIN_INVENTORY.md](./PROFILE_TODAY_DOMAIN_INVENTORY.md) v2.4.
- 2026-06-01 | Product | T0 Hybrid C accepted | DONE | Core/Love/Money/Operating as separate domains; not compromise; [PROFILE_TODAY_DOMAIN_INVENTORY.md](./PROFILE_TODAY_DOMAIN_INVENTORY.md) v2.3.
- 2026-06-01 | Product | TC0 Foundation Catalog №1 | DONE | 10S+5W Core; control→Love; 28-label routing locked; [DOMAIN_PHASE1](./DOMAIN_PHASE1_ARCHETYPES_AND_TRAITS.md) §4.
- 2026-06-01 | Product | TC2-A Output Model Variant B | DONE | CoreTraitProfile 15 scores; top-3 projection; [DOMAIN_PHASE1](./DOMAIN_PHASE1_ARCHETYPES_AND_TRAITS.md) §5.1.
- 2026-06-01 | Product | TC2-B scoring model v0.1 | ACTIVE | Rule-based additive; 5 rules; batches B1–B5; [DOMAIN_PHASE1](./DOMAIN_PHASE1_ARCHETYPES_AND_TRAITS.md) §5.2.
- 2026-06-01 | Product | TC2-B1 sign layer | DONE | Element+modality; Water empathy/depth +2; SIGN_LAYER_CAP=3; [DOMAIN_PHASE1](./DOMAIN_PHASE1_ARCHETYPES_AND_TRAITS.md) §5.2.1.
- 2026-06-01 | Product | Product Data Inventory v1.0 | SIGNED | Registry 87 rows; task closed; [PRODUCT_DATA_INVENTORY.md](./PRODUCT_DATA_INVENTORY.md).
- 2026-06-01 | Product | Profile Pass C Data Binding v0.2 | SIGNED | Seven CDs; gaps G1–G6 resolved; [PROFILE_DATA_BINDING.md](./PROFILE_DATA_BINDING.md).
- 2026-06-01 | Product | Profile Coherence Rule v0.1 | SIGNED | Card 1 identity source; 3/4/6 projections; Foundation→Projection→Narrative; [PROFILE_COHERENCE.md](./PROFILE_COHERENCE.md).
- 2026-06-01 | Design | TodayFlow Foundation UI | ACTIVE | [TODAYFLOW_FOUNDATION_UI.md](./TODAYFLOW_FOUNDATION_UI.md): Figma TODAYFLOW_FOUNDATION_UI — Hero L/M/S, Symbols, Geometry, Surfaces A-D, Typography, Colors; textless premium test; draft `todayflow-foundation.css` |
- 2026-06-01 | Product | Profile Screen Master | **ACTIVE** | Foundation code sign-off done; v0 Phase 2 entities + taxonomy audit remain · prod = Quick Map |
- 2026-06-01 | Product | Meta doc chain | PAUSED | No new product docs; Figma is deliverable |
- 2026-06-01 | Web | Profile sprint: Who scene + sphere objects | DONE | Who=L1 archetype+chips, expand=why only; Love/Money visual objects; desktop 2-col; scroll rhythm widths |
- 2026-06-01 | Product | Foundation Domain Registry | FROZEN | After data inventory; TC2-B/Love/domain priority paused.
- 2026-06-01 | Product | Foundation Domain Registry v2.0 | SUPERSEDED | by v2.1 DoD.
- 2026-06-01 | Product | Love Domain Card 3 scope | ACTIVE | LD-D→LD-2 before scoring; [LOVE_DOMAIN_CARD.md](./LOVE_DOMAIN_CARD.md).
- 2026-06-01 | Product | TC2-B scoring | PAUSED | Resume after Foundation map; B1 sign layer done.
- 2026-06-01 | Product | TC2-B2 Life path LP 1-3 | CANCELLED | Superseded by Foundation map pause.
- 2026-06-01 | Product | TC1.75 Trait Coverage PASS | DONE | 0 Unsupported; Weak confidence ceiling; [DOMAIN_PHASE1](./DOMAIN_PHASE1_ARCHETYPES_AND_TRAITS.md) §5.075.
- 2026-06-01 | Product | TC0 revision pass 2 | DONE | Core 10S+5W; superseded by TC0 sign-off.
- 2026-06-01 | Product | T0 hybrid domain model stop | DONE | Core vs Love/Money/Operating; before TC0; [PROFILE_TODAY_DOMAIN_INVENTORY.md](./PROFILE_TODAY_DOMAIN_INVENTORY.md) v2.2.
- 2026-06-01 | Product / Architecture | Profile Source of Truth Map | DONE | [PROFILE_PIL_MAP.md](./PROFILE_PIL_MAP.md): preserved; step 5 of screen-first canon.
- 2026-06-01 | Product / Architecture | Profile Readiness Audit | DONE | [PROFILE_READINESS_AUDIT.md](./PROFILE_READINESS_AUDIT.md): 7-block existence audit; Identity+Intent+Reality sufficient; empty blocks policy.
- 2026-06-02 | Product | Today Step B — ownership map | DONE | [TODAY_OWNERSHIP_MAP.md](./status/TODAY_OWNERSHIP_MAP.md) · DayModel vs User State vs Action Foundation; compass gaps → Today.
- 2026-06-02 | Product / Frontend | Today Step A — canon vs code diff | DONE | [TODAY_CANON_VS_CODE_DIFF.md](./status/TODAY_CANON_VS_CODE_DIFF.md) · ritual-first ≠ Theme→Action→Progress.
- 2026-06-02 | Product / Frontend | Profile v0 content-stable + visual QA | DONE | 29/31 unique · 2 compass gaps deferred · [PROFILE_V0_VISUAL_QA.md](./status/PROFILE_V0_VISUAL_QA.md) · UI audit tests.
- 2026-06-02 | Product / Frontend | Profile v0 taxonomy slots + Igor audit table | DONE | `buildProfileV0TaxonomySlots` · [PROFILE_V0_IGOR_TAXONOMY_AUDIT.md](./archive/PROFILE_V0_IGOR_TAXONOMY_AUDIT.md).
- 2026-06-01 | Product / Frontend | Profile v0 taxonomy gate (category ≠ count) | DONE | `profileInsightTaxonomy.ts` · superseded by slot pipeline.
- 2026-06-01 | Product / Frontend | Profile v0: Name killed, Social Mirror + insight budget 31 | DONE | Structural pass in web; taxonomy gate supersedes count-only QA.
- 2026-06-01 | Product / Architecture | Core User Loop canon | DONE | [CORE_USER_LOOP.md](./CORE_USER_LOOP.md): Theme→Action→Progress as main product object; domain matrix; branches A–E as loop feeders; pause enrichment until loop proof.
- 2026-06-01 | Product / Architecture | First Today Success Criteria v2 | DONE | [FIRST_DAY_EXPERIENCE.md](./FIRST_DAY_EXPERIENCE.md): action not feeling; one-sentence test; Test A/B; backend conditional pass / UX fail.
- 2026-06-01 | Product / Architecture | First Day execution lock P0.1–P0.3 | ACTIVE | Gap analysis v1.1; G5 Why deferred; freeze C1.7/registries.
- 2026-06-01 | Product / Architecture | First Day DoD gap analysis | DONE | [FIRST_DAY_EXPERIENCE.md](./FIRST_DAY_EXPERIENCE.md): model vs web/iOS/backend audit; P0 gaps G1–G5 mapped; three data kinds Foundation/Causal/Product.
- 2026-06-01 | Product / Architecture | First Day Experience + Today model v1.1 | DONE | [FIRST_DAY_EXPERIENCE.md](./FIRST_DAY_EXPERIENCE.md): 30s path Profile(1–3)→First Today→Daily Loop, MVP blocks without Knowledge/Evolution/Calendar/ME; [TODAY_PRODUCT_MODEL.md](./TODAY_PRODUCT_MODEL.md) v1.1: Progress mandatory in package, Why layer (selected/filtered/blocked); freeze C1.7/new registries/API until First Day DoD.
- 2026-06-01 | Product / Architecture | Profile + Today product models (воронки) | DONE | [PROFILE_PRODUCT_MODEL.md](./PROFILE_PRODUCT_MODEL.md): 4-layer profile funnel (Identity→Intent→Reality→Behavior), блоки экрана, обязательность; [TODAY_PRODUCT_MODEL.md](./TODAY_PRODUCT_MODEL.md): 6-stage day funnel, Today Package (Theme/Insight/Action/Reflection/Symbolic), UI↔data map, logical request sequence; no new API contracts.
- 2026-06-01 | Backend / Reference | Branch B1.4 Evolution Score / ECC Integration | DONE | read-only ES; B1.3→B1.2 path; no API/promotion; [EVOLUTION_SCORE_INTEGRATION.md](./EVOLUTION_SCORE_INTEGRATION.md); next B1.5.
- 2026-06-01 | Backend / Reference | Branch B1.3 Progression Signal Contract | DONE | registry + `progression_signal_v1`; eligibility aggregation; [PROGRESSION_SIGNAL_CONTRACT.md](./PROGRESSION_SIGNAL_CONTRACT.md); next B1.4 ECC.
- 2026-06-01 | Backend / Reference | Branch B1.2 Evolution User State Contract | DONE | `evolution_user_state_v1`; eligibility snapshot; no promotion; [EVOLUTION_USER_STATE_CONTRACT.md](./EVOLUTION_USER_STATE_CONTRACT.md); next B1.3 signals.
- 2026-06-01 | Backend / Reference | Branch B1.1 Evolution CD Reference Tables | DONE | 7 stages, 10 path themes, 6 stage gates; loader + validator; [EVOLUTION_CD_REFERENCE.md](./EVOLUTION_CD_REFERENCE.md); next B1.2 user state.
- 2026-06-01 | Product / Architecture | Branch B1.0.1 Evolution Hierarchy & Ownership | DONE | Stage primary axis; parallel paths; stage gates ≠ achievements; engine ownership; [EVOLUTION_HIERARCHY_AND_OWNERSHIP.md](./EVOLUTION_HIERARCHY_AND_OWNERSHIP.md); prerequisite for B1.1.
- 2026-06-01 | Product / Architecture | Branch B1.0 Evolution Entity Registry | DONE | stages, paths, cycles, milestones, gates, signals, unlocks; no UI/API; [EVOLUTION_ENTITY_REGISTRY.md](./EVOLUTION_ENTITY_REGISTRY.md); next B1.0.1 hierarchy.
- 2026-06-01 | Product / Architecture | Branch A Knowledge Usage Layer — architecture closed | ACTIVE | A1.1–A1.8; A1.8 partial until AK pool from promotion; log criteria — [status/branch_a_knowledge_usage_layer.md](./status/branch_a_knowledge_usage_layer.md); next Branch B.
- 2026-06-01 | Backend / Reference | Branch A1.8 Hot Path Wiring | DONE | `user_active_knowledge` DB; loader; `build_today_narrative` + metrics log; [KNOWLEDGE_HOT_PATH_WIRING.md](./KNOWLEDGE_HOT_PATH_WIRING.md); ops: promotion persist.
- 2026-05-31 | Backend / Reference | Branch A1.7 Knowledge Usage Metrics & Trace | DONE | `knowledge_usage_metrics_trace_v1`; DayContext + P1.9 enrich; 7 tests; [KNOWLEDGE_USAGE_METRICS.md](./KNOWLEDGE_USAGE_METRICS.md); next hot path.
- 2026-05-31 | Backend / Reference | Branch A1.5–A1.6 Personalization Usage Gate + P1.9 wire | DONE | `try_decide_personalization_usage_v1()`; `maybe_build_llm_context_slice_v1(..., day_context_layers=...)`; 12+4 tests; [PERSONALIZATION_USAGE_GATE.md](./PERSONALIZATION_USAGE_GATE.md); next A1.7 metrics.
- 2026-05-31 | Backend / Reference | Branch A1.4 Profile Knowledge Personalization | DONE | Context Slice → safe_personalization_summary; Profile Selector enrichment; DayContext hook; 12 tests; [PROFILE_KNOWLEDGE_PERSONALIZATION.md](./PROFILE_KNOWLEDGE_PERSONALIZATION.md); next A1.5 usage gate.
- 2026-05-31 | Backend / Reference | Branch A1.3 Day Engine Knowledge Wiring | DONE | `try_apply_day_engine_knowledge_v1()`; guide_decision knowledge_hints layer; DayContext opt-in; 13 tests; [status/knowledge_context_selection_a1_3.md](./status/knowledge_context_selection_a1_3.md); next A1.4 Profile Selector.
- 2026-05-31 | Backend / Reference | Branch A1.2 Day Engine Knowledge Integration | DONE | `try_build_day_engine_knowledge_input_v1()`; hint channels; advisory-only; 14 tests; [DAYENGINE_KNOWLEDGE_INTEGRATION.md](./DAYENGINE_KNOWLEDGE_INTEGRATION.md); next A1.3 Day Engine wiring.
- 2026-05-31 | Backend / Reference | Branch A1.1 Knowledge Context Selection | DONE | `select_knowledge_context_v1()`; freshness layer (`last_confirmed_at`); soft cap 3 / hard cap 5; conflict resolution; 10 tests; [status/knowledge_context_selection_a1_1.md](./status/knowledge_context_selection_a1_1.md); next A1.2 Profile Selector wire.
- 2026-05-31 | Product / Architecture | Branch A1.0 Knowledge Context Selection canon | DONE | [KNOWLEDGE_CONTEXT_SELECTION_SYSTEM.md](./KNOWLEDGE_CONTEXT_SELECTION_SYSTEM.md): Knowledge Selector → Context Selector → Slice; before Day Engine/LLM budget; next A1.1 builder.
- 2026-05-31 | Product / Architecture | Learning infrastructure scope freeze at P1.27 | ACTIVE | P1.28+ deferred; priority → Knowledge Usage, Evolution, Practice, Symbolic Assets, Calendar Intelligence; [API_MEMORY_AND_LEARNING_LAYER.md](./API_MEMORY_AND_LEARNING_LAYER.md).
- 2026-05-31 | Backend / Reference | P1.27 training dataset registry | DONE | `try_register_training_example_v1()`; scaffold frozen; next product branches A–E per freeze doc.
- 2026-05-31 | Backend / Reference | P1.26 dataset candidate promotion gate | DONE | `try_promote_dataset_candidate_v1()`; day_training_example_approval_v1; evidence/review gates; training_use_allowed=true only when approved; `test_day_model_v1_training_example_approval.py` (10); [DAYMODEL_TRAINING_EXAMPLE_APPROVAL.md](./DAYMODEL_TRAINING_EXAMPLE_APPROVAL.md); next P1.27 dataset registry.
- 2026-05-31 | Backend / Reference | P1.25 hint application dataset policy | DONE | `try_build_hint_application_dataset_policy_v1()`; candidate/runtime_trace_only/rejected; training_use_allowed=false; `test_day_model_v1_hint_application_dataset_policy.py` (10); [DAYMODEL_HINT_APPLICATION_DATASET_POLICY.md](./DAYMODEL_HINT_APPLICATION_DATASET_POLICY.md); next P1.26 promotion gate.
- 2026-05-31 | Backend / Reference | P1.24 hint package application contract | DONE | `try_apply_hint_package_v1()`; consumer compatibility; before/after trace; no mutation; `test_day_model_v1_hint_application.py` (11); [DAYMODEL_HINT_APPLICATION.md](./DAYMODEL_HINT_APPLICATION.md); next P1.25 application audit.
- 2026-05-31 | Backend / Reference | P1.23 active knowledge hint package | DONE | `try_build_active_knowledge_hint_package_v1()`; usage→hint_type mapping; applied=false; no application; `test_day_model_v1_active_knowledge_hint_package.py` (11); [DAYMODEL_ACTIVE_KNOWLEDGE_HINT_PACKAGE.md](./DAYMODEL_ACTIVE_KNOWLEDGE_HINT_PACKAGE.md); next P1.24 hint application.
- 2026-05-31 | Backend / Reference | P1.22 active knowledge runtime gate | DONE | `try_decide_active_knowledge_runtime_v1()`; surface compatibility; allow/deny only; `test_day_model_v1_active_knowledge_runtime_gate.py` (11); [DAYMODEL_ACTIVE_KNOWLEDGE_RUNTIME_GATE.md](./DAYMODEL_ACTIVE_KNOWLEDGE_RUNTIME_GATE.md); next P1.23 hint package.
- 2026-05-31 | Backend / Reference | P1.21 active knowledge usage policy | DONE | `try_build_active_knowledge_usage_policy_v1()`; allowed/forbidden usages; max influence low/medium; `test_day_model_v1_active_knowledge_usage_policy.py` (12); [DAYMODEL_ACTIVE_KNOWLEDGE_USAGE_POLICY.md](./DAYMODEL_ACTIVE_KNOWLEDGE_USAGE_POLICY.md); next P1.22 runtime gate.
- 2026-05-31 | Backend / Reference | P1.20 active knowledge confirmation gate | DONE | `try_activate_knowledge_from_candidate_v1()`; strict gate; Active Knowledge≠Profile; `test_day_model_v1_active_knowledge.py` (12); [DAYMODEL_ACTIVE_KNOWLEDGE.md](./DAYMODEL_ACTIVE_KNOWLEDGE.md); next P1.21 usage policy.
- 2026-05-31 | Backend / Reference | P1.19 knowledge candidate from pattern | DONE | `try_build_knowledge_candidate_from_pattern_v1()`; machine-readable claims; no active knowledge; `test_day_model_v1_knowledge_candidate.py` (10); [DAYMODEL_KNOWLEDGE_CANDIDATE.md](./DAYMODEL_KNOWLEDGE_CANDIDATE.md); next P1.20 confirmation gate.
- 2026-05-31 | Backend / Reference | P1.18 pattern confirmation gate | DONE | `try_confirm_pattern_from_candidate_v1()`; gate re-checks promotion_eligible; confirmed/not_ready/conflicted/rejected; `test_day_model_v1_confirmed_pattern.py` (11); [DAYMODEL_PATTERN_CONFIRMATION_GATE.md](./DAYMODEL_PATTERN_CONFIRMATION_GATE.md); next P1.19 knowledge candidate.
- 2026-05-31 | Product / Architecture | Knowledge Promotion Ladder canon | DONE | [USER_KNOWLEDGE_MODEL.md](pim/USER_KNOWLEDGE_MODEL.md): Signal→Candidate→Pattern→Knowledge→Profile; Pattern Candidate≠Pattern; no skip steps.
- 2026-05-31 | Backend / Reference | P1.17 pattern candidate aggregation | DONE | `try_aggregate_pattern_candidate_v1()`; promotion_eligible gate; no Pattern/memory/profile; `test_day_model_v1_pattern_candidate.py` (10); [DAYMODEL_PATTERN_CANDIDATE_AGGREGATION.md](./DAYMODEL_PATTERN_CANDIDATE_AGGREGATION.md).
- 2026-05-31 | Backend / Reference | P1.16 reaction → learning signal mapping | DONE | `build_day_surface_learning_signal_v1()`; all reaction types mapped; memory/ranking flags false; `test_day_model_v1_surface_learning_signal.py` (12); [DAYMODEL_LEARNING_SIGNAL_MAPPING.md](./DAYMODEL_LEARNING_SIGNAL_MAPPING.md); next P1.17 aggregation policy.
- 2026-05-31 | Backend / Reference | P1.15 user exposure & reaction contract | DONE | `build_day_surface_exposure_v1()` + `build_day_surface_reaction_v1()`; raw weights; audit→exposure→reaction; `test_day_model_v1_surface_exposure_reaction.py` (10); [DAYMODEL_USER_EXPOSURE_REACTION.md](./DAYMODEL_USER_EXPOSURE_REACTION.md); next P1.16 learning signal mapping.
- 2026-05-31 | Backend / Reference | P1.14 surface candidate audit record | DONE | `build_day_surface_candidate_audit_v1()`; hash/id derivation; [DAYMODEL_SURFACE_CANDIDATE_AUDIT.md](./DAYMODEL_SURFACE_CANDIDATE_AUDIT.md); next P1.15 exposure/reaction.
- 2026-05-31 | Backend / Reference | P1.13 surface candidate selection | DONE | `select_day_surface_candidate_v1()`; deterministic/llm/blocked; threshold 0.75; `test_day_model_v1_surface_candidate.py` (10); [DAYMODEL_SURFACE_CANDIDATE_SELECTION.md](./DAYMODEL_SURFACE_CANDIDATE_SELECTION.md); next P1.14 audit record.
- 2026-05-31 | Backend / Reference | P1.12 LLM response evaluation + post-call | DONE | `evaluate_day_llm_response_v1()`; post-call enrichment; used_in_ui=false; `test_day_model_v1_llm_response_evaluation.py` (10); [DAYMODEL_LLM_RESPONSE_EVALUATION.md](./DAYMODEL_LLM_RESPONSE_EVALUATION.md); next P1.13 surface selection.
- 2026-05-31 | Backend / Reference | P1.11 LLM response validator contract | DONE | `validate_day_llm_refinement_response_v1()`; valid/invalid + issues; `test_day_model_v1_llm_refinement_response.py` (12); [DAYMODEL_LLM_RESPONSE_CONTRACT.md](./DAYMODEL_LLM_RESPONSE_CONTRACT.md); next P1.12 post-call integration.
- 2026-05-31 | Backend / Reference | P1.10 LLM prompt template contract | DONE | registry + `build_day_llm_prompt_v1()`; refinement-only; `test_day_model_v1_llm_prompt.py` (10); [DAYMODEL_PROMPT_TEMPLATE_CONTRACT.md](./DAYMODEL_PROMPT_TEMPLATE_CONTRACT.md); next P1.11 Response Validator.
- 2026-05-31 | Backend / Reference | P1.9 LLM context slice contract | DONE | `build_llm_context_slice_v1()`; depth none/minimal/standard; no profile; `test_day_model_v1_llm_context_slice.py` (10); [DAYMODEL_CONTEXT_SLICE_CONTRACT.md](./DAYMODEL_CONTEXT_SLICE_CONTRACT.md); next P1.10 Prompt Template.
- 2026-05-31 | Backend / Reference | P1.8 LLM request record contract | DONE | pre/post-call builders; only on call_llm; evaluation hook fields; `test_day_model_v1_llm_request_record.py` (10); [DAYMODEL_LLM_REQUEST_RECORD.md](./DAYMODEL_LLM_REQUEST_RECORD.md); next P1.9 Context Slice.
- 2026-05-31 | Backend / Reference | P1.7 Day content LLM call gate | DONE | `decide_day_content_llm_call_v1()`; no_call/call_llm/blocked; policy meta only; `test_day_model_v1_llm_call_gate.py` (10); [DAYMODEL_LLM_CALL_GATE.md](./DAYMODEL_LLM_CALL_GATE.md); next P1.8 Request Record.
- 2026-05-31 | Backend / Reference | P1.6 Day content renderer contract | DONE | `render_day_content_package_v1()`; surfaces today_hero/guidance/risk/action/tempo/reflection; block→not renderable; `test_day_model_v1_content_renderer.py` (10); [DAYMODEL_RENDERER_CONTRACT.md](./DAYMODEL_RENDERER_CONTRACT.md); next P1.7 LLM Gate.
- 2026-05-31 | Backend / Reference | P1.5 Day content package evaluation | DONE | `evaluate_day_content_package_v1()`; completeness/confidence/conflict/repetition scores; recommendation use/caution/block; `test_day_model_v1_content_evaluation.py` (10); [DAYMODEL_PACKAGE_EVALUATION.md](./DAYMODEL_PACKAGE_EVALUATION.md); next P1.6 Renderer Contract.
- 2026-05-31 | Backend / Reference | P1.4 Day content assembly | DONE | `assemble_day_content_package_v1()`; slots headline/guidance/risk/action/tempo/reflection + metadata; `test_day_model_v1_content_assembly.py` (10); [DAYMODEL_INPUT_CONTRACT.md](./DAYMODEL_INPUT_CONTRACT.md); next P1.5 Evaluation.
- 2026-05-31 | Backend / Reference | P1.3 Day content seed texts | DONE | 37 keys `text_short`/`text_medium` locale en; validator + `resolve_content_entries_from_mapping()`; `test_day_model_v1_content_seed_texts.py` (13); [DAYMODEL_CONTENT_SEED_TEXTS.md](./DAYMODEL_CONTENT_SEED_TEXTS.md); next P1.4 Assembly.
- 2026-05-31 | Backend / Reference | P1.1 DayModel v1 interpretation rules | DONE | `interpret_day_model_v1()`; enums strategy/opportunity/risk/tempo/action/reflection/pressure; rule hits in `reasons`; `test_day_model_v1_interpretation.py` (12); [DAYMODEL_INTERPRETATION_RULES.md](./DAYMODEL_INTERPRETATION_RULES.md); next P1.2 Content Mapping.
- 2026-05-31 | Backend / Reference | P1.0 DayModel v1 multi-source aggregation | DONE | `aggregate_day_model_v1()`; vector 0.4/0.3/0.3; tempo 0.2/0.4/0.4; enum score maps; `test_day_model_v1_multisource.py` (15); [status](./status/day_model_v1_aggregation_p1_0.md); next P1.1 Interpretation Rules.
- 2026-05-31 | Backend / Reference | P0.8 Astrology atomic machine drafts | DONE | [ASTROLOGY_COMPOSITION_MODEL.md](./ASTROLOGY_COMPOSITION_MODEL.md) gate; 39 files; loader + validator; next P0.9.
- 2026-05-31 | Product / Architecture | Astrology Composition Model gate | DONE | [ASTROLOGY_COMPOSITION_MODEL.md](./ASTROLOGY_COMPOSITION_MODEL.md): primary vs derived; atomic-only P0.8; Composition Engine = phase 2.
- 2026-05-31 | Backend / Reference | P0.5 Numerology machine drafts | DONE | 39 files `DATA/reference/numerology/machine/`; loader + validator; next P0.7 AMC (not partial DayModel).
- 2026-05-31 | Backend / Reference | P0.4 DayModel v1 aggregation test (tarot-only) | DONE | `reference_machine_loader.py`, `day_model_v1_aggregator.py`, `test_day_model_v1_aggregation.py`; preview contract `day_model_v1_preview`; no UI/LLM/legacy migration; next P0.5 numerology machine drafts.
- 2026-05-31 | Reference / Tarot | P0.3 Tarot Major machine drafts (22 files) | DONE | `DATA/reference/tarot/machine/00_fool.json` … `21_world.json`; `status: draft`, `version: 0.1.0`; legacy `tarot_major_arcana.json` untouched; validator extended for 22-file gate; next P0.4 DayModel v1 aggregation test.
- 2026-05-31 | Product / Architecture | Reference Machine Contract JSON Schema v1 (P0.2) | DONE | `docs/schemas/reference_machine_contract_v1.schema.json`, fixtures, `scripts/validate_reference_machine_contract.py`, CI job `reference-machine-contract-schema`.
- 2026-05-31 | Product / Architecture | DayModel Input Contract (P0.1) | DONE | [DAYMODEL_INPUT_CONTRACT.md](./DAYMODEL_INPUT_CONTRACT.md): шкалы, Dependency Map, Machine fields per domain, gap vs `day_model_v0`; обновлены REFERENCE_LAYER freeze, README, tracker Phase 0.
- 2026-06-22 | Product / Architecture | Answer Contract v1 (Intent → Assembler) | DONE | [SCREEN_CONTRACTS_V1.md](./SCREEN_CONTRACTS_V1.md): Intent Registry, Answer Assembler role, Tier 1–2 mandatory answer elements; chain Reference → Profile → Question → Intent → Engines → Assembler → Surface; Phase 6 tracker + `CORE_PRODUCT_CANON` §6.1 cross-ref; next Question Registry v1.
- 2026-06-22 | Product / Architecture | Need-first stack (Need · Intent · Answer) | DONE | [INTENT_MODEL_V1.md](./INTENT_MODEL_V1.md) (28 needs, surface defaults, inference); [INTENT_REGISTRY_V1.md](./INTENT_REGISTRY_V1.md); [SCREEN_CONTRACTS_V1.md](./SCREEN_CONTRACTS_V1.md) v1.1 need-indexed; Question Registry demoted to Hub/AI; next Engine Projection Specs v1.
- 2026-06-22 | Product / Architecture | Daily Navigation Model (ICA kernel) | DONE | [DAILY_NAVIGATION_MODEL.md](./DAILY_NAVIGATION_MODEL.md): clarity+direction+reflection; Identity·Context·Guidance·Action; daily 4 opоры; screen map; Question Registry = chat periphery; `CORE_PRODUCT_CANON` §1 + JTBD Entry reframed.
- 2026-06-22 | Product / Architecture | Market attention + screen jobs | DONE | [MARKET_ATTENTION_AND_SCREEN_JOBS.md](./MARKET_ATTENTION_AND_SCREEN_JOBS.md): L1–L5 market tiers; 5 Today life domains; Today vs Tarot; Profile living KB; Calendar facts loop; retention Today→Calendar→Profile; `SCREEN_INVENTORY` §1 updated.
- 2026-06-22 | Product / Architecture | Screen Contracts v1 | DONE | [SCREEN_CONTRACTS_V1.md](./SCREEN_CONTRACTS_V1.md): mandatory slots per screen; Today domain status/opportunity/risk/action; Profile 8 elements; Compatibility 5; Tarot 4; Calendar 5; foundation-before Engine Projection Specs.
- 2026-06-22 | Product / Architecture | Today contract Model B ADR | DONE | [SCREEN_CONTRACTS_V1.md](./SCREEN_CONTRACTS_V1.md) v1.2: 3 DomainLens + global_context.period + personal_growth; unified status/opportunity/risk/action; отвергнуты 5-equal-domains и смешанная v1.1; до OpenAPI.
- 2026-06-22 | Product / Architecture | Today assembler mapping (legacy bridge) | DONE | [TODAY_CONTRACT_ASSEMBLER_MAPPING.md](./TODAY_CONTRACT_ASSEMBLER_MAPPING.md): source priority, slot rules, strict no-legacy-UI-bind, P0.1 acceptance; before OpenAPI.
- 2026-06-22 | Engineering | `assemble_today_contract_v1()` + fixtures | DONE | `services/today_contract_assembler_v1.py`; 3 fixture scenarios + `test_today_contract_assembler_v1.py` green; OpenAPI after wire.
- 2026-06-22 | Engineering | GET /today/contract wire | DONE | `today_contract_wire_v1.py` + `test_today_contract_endpoint.py`; legacy inputs server-side only.
- 2026-06-22 | Engineering | Web Today P0.1 contract render | DONE | `GET /today/contract` + `TodayContractSurface` / domain components; default Today path; ritual uses contract for domains.
- 2026-06-22 | Engineering | P0.1.1 Today text quality gate | DONE | `today_contract_text_quality_v1.py`; profile reject, imperative actions, family dedupe, short copy; tests green.
- 2026-06-22 | Engineering | P0.1.2 Today Text Quality v2 | DONE | Family profile leak blocked; Growth≠Period; cross-domain dedupe; domain-themed fallbacks; `family_profile_leak.json`; 22 contract tests green; web re-check before iOS.
- 2026-06-23 | Frontend / Onboarding P0.1 | Guest demo Today `/demo/today` | **DONE** | `GuestTodaySurface` + `buildGuestTodayPackage`; landing CTA → `/demo/today`; signup → `/onboarding/core`; tests `demoTodayPackage.test.ts`.
- 2026-06-23 | Frontend / Onboarding P0.2 + P0.4 | Core setup `/onboarding/core` | **DONE** | `CoreOnboardingFlow`, `useCoreSetupFlow`, `coreSetup.ts`; Profile ≠ onboarding host; `resolvePostAuthTarget`; legacy links migrated.
- 2026-06-23 | Frontend / Onboarding P0.3 | Intent + Reality chips | **DONE** | `IntentOnboardingFlow`, `RealityOnboardingFlow`, `onboardingContext.ts`; events `onboarding_intent_selected` / `onboarding_reality_selected`; backend + tests.
- 2026-06-23 | Frontend / Onboarding P0.5 | First Today `?first=1` | **DONE** | `FirstTodaySurface`, `buildFirstTodayPackage`; Theme→Progress→Insight→Action; deterministic, no LLM; tests.
- 2026-06-23 | Frontend / Onboarding P0.6 | Profile after First Today | **DONE** | `ProfileFirstDayTeaser`, `firstTodayState.ts`; journey redirects; `resolvePostCoreAuthTarget`.
- 2026-06-23 | Product / Onboarding | First Day & onboarding route contract v2 | **ACCEPTED** | [FIRST_DAY_EXPERIENCE.md](./FIRST_DAY_EXPERIENCE.md) v2: guest `/demo/today`, signup vs core split, `/onboarding/*`, Intent/Reality chips, Profile ≠ onboarding, PIM events, P0 backlog; [CORE_PRODUCT_CANON.md](archive/CORE_PRODUCT_CANON.md) §8.2; KASP channel A updated.
- 2026-06-23 | Product / Architecture | PIM v1.1 — Atom · Intent · DRE/LRE | **ACCEPTED** | PIM v1.1: Knowledge Atom unit; [INTENT_MODEL_V1.md](./INTENT_MODEL_V1.md); DRE/LRE split; UKM v1.3 provenance/decay; Today v2.5 C10–C12.
- 2026-06-23 | Product / Editorial | generation_logs export script | **DONE** | `export_today_generation_logs.py` → JSONL raw; corpus `--logs-dir`; PII mask; column introspection.
- 2026-06-23 | Product / Editorial | TL-0A/B language corpus | **DONE** | `today_language_corpus_v0.py` → 841 RU phrases + auto-tags; [TODAY_LANGUAGE_CORPUS_V0.json](./datasets/TODAY_LANGUAGE_CORPUS_V0.json).
- 2026-06-23 | Product / Editorial | TODAY_LANGUAGE + TL-0 | **IN_PROGRESS** | H4 SUPPORTED; H5 Self-Verification candidate; TL-1 blocked |
- 2026-06-23 | Product / Editorial | TODAY_LANGUAGE_V1 + RULE_001 (правило кино) | **ACCEPTED** | [TODAY_LANGUAGE_V1.md](today-language/TODAY_LANGUAGE_V1.md): ось банальность/небанальность; Today v2.7 R24.
- 2026-06-23 | Product / Architecture | PR2 Goal Loop PIM gate (C13) | **ACCEPTED** | Today v2.6 R23; A1–A6 acceptance; guidance-only = reject; [INTENT_MODEL_V1.md](./INTENT_MODEL_V1.md) §6.
- 2026-06-23 | Product / Architecture | Signal vs Interpretation (C14) | **ACCEPTED** | PIM v1.2; UKM `evidence_chain`; ILR §8.1; Today v2.7 R24.
- 2026-06-23 | Product / Architecture | Contradiction & Re-evaluation (C15) | **ACCEPTED** | [CONTRADICTION_AND_REEVALUATION_V1.md](./CONTRADICTION_AND_REEVALUATION_V1.md); PIM v1.3; Today v2.8 R25.
- 2026-06-23 | Product / Architecture | Temporal Identity (C16) | **ACCEPTED** | [TEMPORAL_IDENTITY_V1.md](./TEMPORAL_IDENTITY_V1.md); change_nature; UKM temporal fields; PIM v1.4; Today v2.9 R26.
- 2026-06-23 | Product / Architecture | Decision Relevance (C17) | **ACCEPTED** | [DECISION_RELEVANCE_V1.md](./DECISION_RELEVANCE_V1.md); PIM slice ranking; UKM v1.7; Today v3.0 R27.
- 2026-06-23 | Product / Architecture | PIM PR Gate v1 | **ACCEPTED** | [PIM_PR_GATE_V1.md](pim/PIM_PR_GATE_V1.md): 5 PR questions; PR1/PR2 stack verification; C18 freeze.
- 2026-06-23 | Product / Architecture | PIM PR Gate v1.1 ownership | **ACCEPTED** | «Today исчез» test; Intent Record / outcome owners; reject `day_goals` as SoT.
- 2026-06-23 | Product / Architecture | PIM PR Gate v1.2 PIM Diff | **ACCEPTED** | Experience vs PIM test; mandatory PIM Diff; «guidance → PIM unchanged» anti-pattern.
- 2026-06-23 | Product / Architecture | PIM PR Gate v1.3 Learning Δ | **ACCEPTED** | три acceptance-контура; Learning Delta Test; reject UI-only verification.
- 2026-06-23 | Product / Architecture | PIM Product North Star | **ACCEPTED** | [PIM_PRODUCT_NORTH_STAR.md](archive/PIM_PRODUCT_NORTH_STAR.md): актив = PIM; Learning Δ; PIM ROI.
- 2026-06-23 | Engineering | **PR1 pre-flight** | **DONE** | [PR1_PREFLIGHT.md](./archive/PR1_PREFLIGHT.md) §6–§10: S5 boundary, PIM audit, events chain, gate question. Шаблон PR: [PR1_GATE_SECTIONS.md](./archive/PR1_GATE_SECTIONS.md).
- 2026-06-23 | Engineering | **Gate 1 — PR1 в коде** | **READY FOR MERGE** | S0–S5, S5 sentence-filter, pim_read_audit. Evidence: [PR1_MERGE_VERIFICATION.md](./archive/PR1_MERGE_VERIFICATION.md) — live S5 (688/671/657) + gen log **692** + 6 events. → **PR2** (PIM write-path).
- 2026-06-23 | Product / Architecture | **Platform Layer Gate (C18+)** | **ACCEPTED** | Новый слой только при необходимости · gate question · [INTERNAL_PATTERNS](./TODAY_INTERNAL_PATTERNS_V0.md) v2.5 · [PIM_PR_GATE](pim/PIM_PR_GATE_V1.md) v1.5 · AR-010.
- 2026-06-23 | Product / Architecture | **Стоп-условие observable vs theory** | **ACCEPTED** | AP/SP · PIM · PR2 · IPL · Discovery — [INTERNAL_PATTERNS](./TODAY_INTERNAL_PATTERNS_V0.md) v2.3 §Стоп-условие · AR-010.
- 2026-06-23 | Product / Architecture | **AR-011 Phenomenon Before Analysis** | **ACCEPTED** | Два риска (wrong layer vs no data); pre-PR2 = phenomenon creation; IR lifecycle = canonical object — [INTERNAL_PATTERNS](./TODAY_INTERNAL_PATTERNS_V0.md) v2.6 §Стоп-условие · AR-011.
- 2026-06-23 | Engineering | **Day Continuity v0 (web)** | **PARTIAL UI VERIFIED** | Walkthrough run 2: close day + continuity line OK · onboarding→`/today` fix · [BEHAVIOR_CHANGE_TEST_V0.md](./status/BEHAVIOR_CHANGE_TEST_V0.md) § Walkthrough run 2.
- 2026-06-23 | Product | **Behavior Change Test (14d)** | **BLOCKED** | До ship gate; не тестировать S0–S5 фрагмент — [BEHAVIOR_CHANGE_TEST_V0.md](./status/BEHAVIOR_CHANGE_TEST_V0.md).
- 2026-06-23 | Product | **AR-012 freeze** | **ACTIVE** | No AR-013+; no field test on incomplete cycle.
- 2026-06-23 | Product / Architecture | **AR-012 Retention Before Instrumentation** | **ACCEPTED** | Продукт удержания первичен; IR = byproduct; instrumentation trap — [INTERNAL_PATTERNS](./TODAY_INTERNAL_PATTERNS_V0.md) v2.9 · PR2 §15 revised.
- 2026-06-23 | Product / Architecture | **Launch priority freeze** | **ACTIVE** | Retention-first order; gate «удержание в недели?» — AR-011/012 · [PR2_PREFLIGHT](./archive/PR2_PREFLIGHT.md) · [PIM_PR_GATE](pim/PIM_PR_GATE_V1.md) §5.
- 2026-06-23 | Product / Architecture | **PR2 Success Criterion (post-deploy)** | **REVISED** | Retention primary · IR secondary · reject IR-only success — [PR2_PREFLIGHT](./archive/PR2_PREFLIGHT.md) §15 · AR-012.
- 2026-06-23 | Product / Architecture | **Discovery fork** | **OPEN** | No Validation Protocol until prod Intent Records; post-PR2 **Watchlist** only — [INTERNAL_PATTERNS](./TODAY_INTERNAL_PATTERNS_V0.md) v2.2 · [PR2_PREFLIGHT](./archive/PR2_PREFLIGHT.md) §14.
- 2026-06-23 | Engineering | **PR2 pre-flight** | **DONE** | [PR2_PREFLIGHT.md](./archive/PR2_PREFLIGHT.md) — entity map; §2.1 birth moment; causal chain > atom; separate read/write audit; §14 Watchlist.
- 2026-06-23 | Docs | Legacy spec cleanup | DONE | Removed `spec/`, `REIMAGINING_PLAN.md`, PAUSED screen/visual docs, branch status snapshots, superseded Today web decisions; canon pointers → `TODAY_SCREEN_V1_CANON`, `PROFILE_SCREEN_MASTER`.
- 2026-06-23 | Docs | Aggressive canon prune | DONE | Removed 133 branch/registry/screen-pipeline docs; **37** canon files + schemas/i18n remain; `docs/README.md` rewritten as single index.
- 2026-06-23 | Docs | Single-canon rule | DONE | `.cursor/rules/docs-single-canon.mdc` + `docs/README.md` §Правило записи: search-before-create, no parallel specs; cross-ref in `workflow-incremental-docs.mdc`.
- 2026-07-01 | Docs | **Build Map v0.7.1 — Phase 1 screen gate table** | **ACTIVE** | launch remaining list · walkthrough after last ✅
- 2026-07-01 | Engineering | **Launch path wiring (web)** | **DONE** | Landing vitrine · demo redirect · FIRST_TODAY redirects · profile chart portal off
- 2026-07-01 | Engineering | **Landing v2 — outcome-first (web)** | **DONE** | Hero (map + copy) · 4 today cards · insight heatmap · final CTA · no feature menu
- 2026-07-01 | Engineering | **Maps seeds — Focus Map preview (Profile web)** | **DONE** | evening → dot seed · Profile preview · no Maps nav
- 2026-07-01 | Engineering | **Value-first onboarding P0.2 (web)** | **PARTIAL** | welcome → birth → preview → guest First Today → save · email-signup · claim → `/today?first=1` (not Profile skip)
- 2026-07-02 | Product / Architecture | **Maps — вторая половина TodayFlow (canon)** | **ACCEPTED** | §4.10 + §5.8 [TODAYFLOW_PRODUCT_MODEL.md](archive/TODAYFLOW_PRODUCT_MODEL.md) · §7 [PROFILE_SCREEN_MASTER.md](profile/PROFILE_SCREEN_MASTER.md) · §3.3 [PERSONAL_INTELLIGENCE_LAYER.md](pim/PERSONAL_INTELLIGENCE_LAYER.md) · backlog MP-1…MP-5
- 2026-07-02 | Engineering | **MP-2 Map language (web + iOS)** | **PARTIAL** | heatmap legend · calendar/ascetic/habits · nav · iOS sync notes
- 2026-07-03 | Engineering | **MP-2 Map language (web + iOS)** | **DONE** | weekly integration + WeeklyScreen story · ascetic/calendar/help/rings · `formatWeeklyRhythmStoryLine` · iOS chrome parity · legacy URL paths kept
- 2026-07-03 | Engineering | **Public launch path (web)** | **DONE** | docker stack · preview→First Today · guest claim on auth · nav cleanup · `/health` · `docker-compose.prod.yml`
- 2026-07-02 | Engineering | **MP-3 Mood Map v0 (web)** | **PARTIAL** | `/maps/mood` · heatmap · drill-down story · observation · Profile link
- 2026-07-02 | Engineering | **MP-3 Energy Map v0 (web)** | **PARTIAL** | `/maps/energy` · fusion API sync · mood fallback · Today persist · drill-down story · Profile link
- 2026-07-02 | Engineering | **MP-3 Habit Map v0 (web)** | **PARTIAL** | `/habits` · `habitMapModel` · 35-day 7×5 grid · day story · observation · mood/energy cross-links
- 2026-07-02 | Engineering | **MP-3 Promise Map v0 (web)** | **PARTIAL** | `/maps/promise` · `promiseMapModel` · evening close + open promises · drill-down · observation · Profile link
- 2026-07-03 | Engineering | **MP-3 Maps iOS parity v0** | **PARTIAL** | `TodayDayLocalStores` · Mood/Energy/Promise/Habit map views · Profile preview · mood→engagement sync · fusion persist
- 2026-07-03 | Engineering | **MP-3 Maps iOS gaps closed** | **DONE** | evening continuity writer · `/maps/*` + `/tracking/progress` deep links · `MapsHubView` · batch fusion sync for Energy Map
- 2026-07-03 | Engineering | **MP-1 Living Maps block v0** | **DONE** | section band · explore card grid + hub · local cross-map observation · heatmap/habit weave preview (web+iOS)
- 2026-07-03 | Engineering | **PS-1 Profile Selector v1** | **DONE** | `topic_sphere_excerpt` · day_history signals · `selector_eval.py` · DayContext wiring · slim LLM pack includes knowledge summary
- 2026-07-03 | Engineering | **DE-9 temporal context** | **DONE** | v1.5 `reflection_excerpt` · UI reflection line web+iOS · meaning signals · `day_model.temporal` |
- 2026-07-03 | Engineering | **DE-13 narrative funnel v1** | **IN_PROGRESS** | `day_history` in funnel step1/2 · step2 arg fix · temporal in funnel prompts |
- 2026-07-03 | Engineering | **DE-13 narrative funnel v2** | **IN_PROGRESS** | per-step cache reuse · `guide_funnel_step{1,2}_cache_hit` · `funnel_prompt_ver` in logs · pytest cache + cached_interpretation |
- 2026-07-03 | Engineering | **DE-13 narrative funnel v3** | **IN_PROGRESS** | child surfaces funnel chain · `funnel_interpretation` in user JSON · `guide_funnel_chain_used` · prompt v17 |
- 2026-07-03 | Engineering | **DE-13 narrative funnel v4** | **IN_PROGRESS** | step3 core_text_v0 LLM · guide_decision fallback · step3 cache/logs · step2 prompt v2 |
- 2026-07-03 | Engineering | **DE-13 guide_contract_v2** | **DONE** | HTTP envelope · guide_pipeline lineage · preserve funnel core · web/iOS/Android parsers · DE-13 epic closed |
- 2026-07-02 | Engineering | **Meaning-derived knowledge v0** | **PARTIAL** | `meaning_derived_knowledge_v0.py` · 3–6 → inferred hypothesis · 7+ → `day_active_knowledge_v1` · CUM sync · Today/Profile confirm
- 2026-07-02 | Engineering | **ILR engine v0 (BE)** | **PARTIAL** | JSON catalog `DATA/reference/interpretation/` + loader · compatibility rules · **gap:** migrate remaining triggers; editorial review queue
- 2026-07-02 | Engineering | **ILR confirm v0 (web + iOS + BE)** | **PARTIAL** | Today post-ritual chips · Profile atom confirm · inferred strip · iOS `PimInterpretationConfirmView` + CUM client · **gap:** Android
- 2026-07-02 | Engineering | **UKM explicit L1 promotion v0** | **PARTIAL** | mood/focus/promise/outcome/confirm/correction → `user_active_knowledge` · inferred verdict on `profile_atom_correction` · **gap:** full ILR ref expansion
- 2026-07-03 | Engineering | **UMTS-1 CUM schema v1** | **DONE** | [compact_user_model_v1.schema.json](./schemas/compact_user_model_v1.schema.json) · fixtures · CI `compact-user-model-schema` · v0 read slice unchanged
- 2026-07-06 | Product / Engineering | **Production pass · Landing #1 + guest limits** | **IN_PROGRESS** | Guest IA · `guestAccessStore` enforcement · **Tarot Figma pass (web):** hub 55:449 light shell · ritual+result 29:692 dark `ProductWebAppShell` · card images `contain` + portrait aspect · **gap:** iOS/Android parity
- 2026-07-03 | Design | **DS-FIGMA Foundation file v0** | **IN REVIEW** | [TODAYFLOW_FOUNDATION_UI](https://www.figma.com/design/pWdevqQqOi6wvoVc6hFWHa) · Cover premium textless · 8 pages · TF variables/styles · gate: «дорого/нет»
- 2026-07-03 | Design / Engineering | **Foundation sign-off — code-side (§9)** | **DONE** | Symbol grid + surfaces complete · Figma v0 built · formal Cover review open
- 2026-07-03 | Engineering | **DS-12 Archetype expansion 12/12 (web + iOS)** | **DONE** | seeker · mentor · guardian · visionary · catalyst · evolution aliases
- 2026-07-03 | Engineering | **DS-11 Element SVG assets (web + iOS)** | **DONE** | 4× elements SVG · `ElementIcon` · atmosphere pattern · `ElementSymbolView.swift`
- 2026-07-03 | Engineering | **DS-10 Typography bridge (`--tf-type-*`)** | **DONE** | `globals.css` orbit-text aliases · `profileV0.module.css` Foundation tokens
- 2026-07-03 | Engineering | **DS-9 Zodiac SVG assets (web + iOS)** | **DONE** | 12× zodiac SVG · mask tint `ZodiacIcon` · `ZodiacSymbolView.swift`
- 2026-07-03 | Engineering | **DS-8 Geometry System (web + iOS)** | **DONE** | G1–G5 · profile/today/portal presets · `SacredGeometryBackdrop` · portal deep · `FoundationGeometryView.swift`
- 2026-07-03 | Engineering | **DS-7 Planet SVG assets (web + iOS)** | **DONE** | 10× planets SVG · `PlanetIcon` · chart table · `PlanetSymbolView.swift`
- 2026-07-03 | Engineering | **DS-6 Foundation HeroSmall (web + iOS)** | **DONE** | Compatibility hub/exploration/dynamics headers · orbit symbol · compact score ring aside
- 2026-07-03 | Engineering | **DS-5 Foundation HeroMedium (web + iOS)** | **DONE** | `HeroMedium.tsx` · Today composition day-anchor · archetype/sun pillars · iOS `HeroMediumView.swift`
- 2026-07-03 | Design / Engineering | **Foundation sign-off — code-side QA (§9)** | **SUPERSEDED** | → **DONE** (2026-07-03 PM-QA) · Figma frames remain open
- 2026-07-03 | Engineering | **Phase 2 cleanup: ProfileLifeSection + legacy /natal-chart audit** | **DONE** | Quick Map `ProfileLifeSection` · `buildProfileLifeSpheresFromProfileData` · `?section=spheres` scroll · `/natal-chart` redirect only · href audit test
- 2026-07-03 | Engineering | **PM-1 backlog: sphere copy audit + ProfileV0 route** | **DONE** | `profileSphereCopy` canon · life sphere framing · `findLifeSphereHouseCopyOverlaps` · `/profile?view=v0` + `profileV0Route` chrome
- 2026-07-03 | Engineering | **DS-1 lite Archetype SVG assets (web + iOS)** | **DONE** | 8× `public/images/icons/archetypes/` · `VISUAL_ASSET_MODE=asset` · `ArchetypeSymbolView.swift`
- 2026-07-03 | Engineering | **DS-4 Profile motion kit (web + iOS)** | **DONE** | `--tf-motion-*` · `ProfileMotion.tsx` · HeroLarge/expand/portal/Quick Map · iOS `ProfileMotion.swift`
- 2026-07-03 | Engineering | **DS-3 Profile orbit-card purge (web)** | **DONE** | `ProfileSurface` tiles · legacy sections migrated · 0× `orbit-card` in `components/profile/`
- 2026-07-03 | Engineering | **DS-3 Profile route chrome (web)** | **DONE** | `SurfaceInsight` Surface B · `/profile` loading + notices без `orbit-card`
- 2026-07-03 | Engineering | **DS-2 Foundation HeroLarge (web + iOS)** | **DONE** | `HeroLarge.tsx` · Profile Quick Map / Editorial / FirstDayTeaser · iOS `HeroLargeView.swift` · symbol 120px · 88dvh canvas
- 2026-07-03 | Engineering | **UMTS-2 CUM v0.19** | **DONE** | Profile Quick Map UI: confidence %, delta_30d, 90d sparkline, primary + alternates · web+iOS
- 2026-07-02 | Engineering | **Today Day Dialogue v0 (web + iOS)** | **PARTIAL** | mood+focus + CUM merge · **inline ritual pick** (tarot grid + number flower, not modal gate) · post-ritual confirm · inferred strip · Tarot/Compat/Profile CUM · **gap:** Android · iOS pick parity audit
- 2026-07-02 | Engineering | **Compatibility PIM loop v0 (web + BE)** | **PARTIAL** | micro-echo · block_feedback → LLM · hub «Не сейчас» · **iOS:** `CompatibilityExplorationResultView` (ring hero, dimension cards, continuation) + analyze PIM · **gap:** pair profiles exploration · atom promotion
- 2026-07-02 | Product | **Today Screen v4.0 — Day Story Experience (canon §11)** | **ACCEPTED** | 17-block product spec → [TODAY_SCREEN_V1_CANON.md](./TODAY_SCREEN_V1_CANON.md) §11 · diff [TODAY_CANON_VS_CODE_DIFF.md](./status/TODAY_CANON_VS_CODE_DIFF.md) §Day Story v3
- 2026-07-02 | Engineering | **Meaning events batch dedup (web + BE)** | **DONE** | in-batch idempotency dedup · frontend outbox chunk dedup · fixes Today 500 spam
- 2026-07-02 | Engineering | **Value-first post-auth → First Today (web)** | **DONE** | `claimGuestProfile` no early `markFirstTodayCompleted` · save dev-token immediate redirect · demo → welcome
- 2026-07-01 | Engineering | **Onboarding preview · interpretation engine v1 (web)** | **DONE** | `frontend/src/lib/interpretation/*` — weighted candidates (sun + sign + life path + personal year/day) · mixed lenses · evidence gate · audit in guest draft · event `onboarding_recognition_shown`
- 2026-07-01 | Engineering | **First Result screen (web onboarding preview)** | **DONE** | Hero + key influences + dominant trait + mini-portrait + 6 dimension cards + surprise + «Почему?» · `FirstResultScreen` · engine-backed copy
- 2026-07-01 | Engineering | **First Result v2 — dedup + session (web)** | **DONE** | 4 visible cards + «ещё наблюдения» · dimension-specific «Почему?» · metadata sources (modality/ruler/season/weekday/chinese/personal year) · card types · RU polish · guest draft in `sessionStorage` · landing `?fresh=1`
- 2026-07-02 | Engineering | **Backend down / geocode+login fix** | **DONE** | `meaning.py` SyntaxError (frozenset `}`) crashed uvicorn · migration duplicate column tolerant · CityAutocomplete error surface
- 2026-07-02 | Engineering | **Onboarding chart path (web)** | **DONE** | name numerology on preview · single CTA → refine → email · welcome email + magic link · `/auth/magic` · profile prep on claim
- 2026-07-01 | Engineering | **Profile min — «Мои дни» (web)** | **DONE** | last 3 closed · focus + outcome · link Today · editorial + D1 teaser
- 2026-07-01 | Engineering | **Compatibility hook (Composition Explore)** | **DONE** | Card in Explore · CTA by saved person · `/compatibility` · D1 skip
- 2026-07-01 | Engineering | **Goal / Tracking teasers (Composition web)** | **DONE** | Growth zone slots 11–12 · default only · D1 skip
- 2026-07-01 | Engineering | **Composition polish (web)** | **DONE** | CSS module · loading skeletons · copy · evening hint · D2 continuity visual first · tests
- 2026-07-01 | Engineering | **First Today → Composition path (web)** | **DONE** | `?first=1` · `TodayCompositionSurface` variant `firstToday` · D1 zones
- 2026-07-01 | Engineering | **TodayCompositionSurface v1 (web)** | **PARTIAL** | Default `/today` · legacy `?experience=1`
- 2026-07-01 | Product | **Build Map v0.6.0 — wave 1 entities complete** | **ACTIVE** | `EveningClose` 🟢 · [TODAYFLOW_PRODUCT_BUILD_MAP.md](./TODAYFLOW_PRODUCT_BUILD_MAP.md)
- 2026-07-01 | Product | **Build Map v0.5.9 — `ContinuityRecall` spec 🟢** | **ACTIVE** | D2+ bridge
- 2026-07-01 | Product | **Positive Definition §2 CLOSED (canonical)** | **CLOSED** | Два базовых закона с §1
- 2026-07-01 | Product | **Positive Definition CLOSED** | **CLOSED** | §5.7 · Build Map E9 · spec · UX · empty states
- 2026-07-01 | Product | **Build Map v0.5.6 — `PracticeRecommendation` spec 🟢** | **ACTIVE** | One practice · [TODAYFLOW_PRODUCT_BUILD_MAP.md](./TODAYFLOW_PRODUCT_BUILD_MAP.md)
- 2026-07-27 | Profile / Architecture | **Applied houses emit all 12** | **LIVE** | Factor how+do for every house (domain+cusp+planet function); no empty non-angular omit · `character_engine_house_lines_v0.4`.
- 2026-07-28 | Today / Scenario | **Conflict short_name from day facts** | **LIVE** | Deterministic poles/stakes from ranked drivers (+natal) · family bank = fallback only · heal bank slogans on project · BE rebuilt
- 2026-07-28 | Today / UX | **Card+number stay readable after reveal** | **LIVE** | Live impacts in scenario «Карта и число» · symbol-impacts after reading · numberValue engagement · FE rebuilt
- 2026-07-28 | Today / UX | **Hide calendar DOY from day prose** | **LIVE** | `Календарный день … N-й день года` never in events_lead / opening / Сигналы — date stays in greeting chrome · heal pops calendar-only lead · BE+FE rebuilt
- 2026-07-28 | Today / UX | **Day reading open before ritual** | **DONE (code)** | Scenario chapters show when `day_scenario` ready · ritual = complement («Символы дня») not unlock · hero theme once · affirm title≠detail · **needs:** FE rebuild deploy
- 2026-07-28 | Today / Ops | **Deploy chrome+scene fixes to live compose** | **DONE** | Containers rebuilt · calendar mash sanitize · «Сигналы дня» · no theme in header
- 2026-07-27 | Today / Scenario | **Scene copy: no force-paste spam + name address** | **DONE (code)** | Deterministic scene beats per sphere (no «a»/«b» quote spam) · person_name vocative · FE drops template opp/trap under each sphere · heal on project for cached templates · needs reproject/refresh
- 2026-07-27 | Today / UI | **Today chrome dedupe (greeting/theme/appearance)** | **DONE (code)** | Remove depth promo · drop Appearance/Mood from Today (appearance → settings · mood system-only) · hero image full-bleed bg · one theme title · greeting+date only · no «Пульс дня» competing label
- 2026-07-27 | Today / Retention | **Cross-day habit architecture (day_hook)** | **BACKLOG** | Owner brief: Zeigarnik evening_payoff as open Q · persist day_hook → tomorrow inputs · practice.window push · evening yes/no tap → PIM · serial continuity · visible personalization growth · low-cost glance · share humor/color · **no** guilt streaks · curiosity+small benefit only · style calib necessary not sufficient
- 2026-07-27 | Today / Scenario | **Today screen P0: mash short_name + Firdaria leak** | **DONE (code)** | `short_name` = tension only · kitchen natal filtered · props shorter · FE sanitize · **follow-up:** card/number + sky cards no longer hide after personalize (`TodayCompositionSurface`) · **needs:** server deploy + reproject
- 2026-07-27 | Today / Scenario | **Style hook mechanics + igor contrast corpus** | **DONE (canon+pack)** | [DAY_SCENARIO_STYLE_HOOK_MECHANICS_V1.md](./audits/DAY_SCENARIO_STYLE_HOOK_MECHANICS_V1.md) · 8 BAD↔GOOD cases [day_scenario_style_calib_igor_v1/](./audits/day_scenario_style_calib_igor_v1/) · `owner_target` · **next:** SH-2 prompt few-shot · SH-3 props gate · SH-4 FE humor/evening_payoff · SH-5 human_consensus
- 2026-07-27 | Content / Voice | **LLM practitioner hard role (always)** | **DONE** | Voice Canon §1: always tarot+numerology+astro+psych+sexology+friend · `llm_practitioner_persona_v1.1` · wired Tarot/Compat/Profile/natal/day_scenario/CE stages/spheres + prior Today paths
- 2026-07-27 | Profile / Architecture | **Subscriber deep themes (L3 tips)** | **LIVE** | Selectable sex/money/love/work/body tips · Plus=1 Pro=2 · 7d change window · base spheres immutable · `character_engine_deep_themes_v0` · GET/PUT `/account/profile/deep-themes`.
- 2026-07-27 | Profile / Architecture | **Applied ASC & houses pass** | **LIVE** | ASC/MC + angular + occupied personal houses as `how`+`do` · omit empty filler · wire `character_engine_asc_v0` · canon scenario §опоры/дома · Swiss cusp/sign stay.
- 2026-07-26 | Profile / Architecture | **CE consumption restore** | **LIVE** | Backend CE env restored · compose PROFILE_CONSUMPTION default on · scrub thesis leak in Effort · [CHARACTER_ENGINE_CONSUMPTION_RESTORE_V0.md](audits/CHARACTER_ENGINE_CONSUMPTION_RESTORE_V0.md).
- 2026-07-26 | Profile / UI | **Profile visuals living pass** | **LIVE** | Portrait seed harden · atmosphere opacity · MotionDrift · sphere motifs · [PROFILE_VISUALS_LIVING_PASS_V0.md](audits/PROFILE_VISUALS_LIVING_PASS_V0.md).
- 2026-07-26 | Profile / Architecture | **CE readers pass 2** | **LIVE** | Drop life_areas primary (FE V0 taxonomy + iOS spheres/QuickMap) · Compat `person_sot`/`identity_line` · Tarot log soft SoT · helper `person_meaning_from_core_v0` · [CHARACTER_ENGINE_READERS_PASS2_V0.md](audits/CHARACTER_ENGINE_READERS_PASS2_V0.md).
- 2026-07-26 | Profile / Architecture | **CE post-cutover kill + readers** | **LIVE PARTIAL** | Personality/funnel hard-killed · CUM+iOS+FE V0 prefer contract/CE · [CHARACTER_ENGINE_POST_CUTOVER_READERS_V0.md](audits/CHARACTER_ENGINE_POST_CUTOVER_READERS_V0.md). **Next:** readers pass 2 (in progress) · file cleanup.
- 2026-07-26 | Profile / Architecture | **CE PUBLISH_READY cutover** | **LIVE** | Owner-approved · `character_engine_v1` = portrait SoT · personality/funnel/oneshot gated · [CHARACTER_ENGINE_PUBLISH_READY_CUTOVER_V0.md](audits/CHARACTER_ENGINE_PUBLISH_READY_CUTOVER_V0.md). Readers migration in progress.
- 2026-07-26 | Profile / Architecture | **CE envelope `character_engine_v1`** | **LIVE READY** | Nest composed from Stage 0–5 · cutover promotes `forming`→`ready` · [CHARACTER_ENGINE_ENVELOPE_V0.md](audits/CHARACTER_ENGINE_ENVELOPE_V0.md).
- 2026-07-29 | Profile / UI | **Act1 share-core + anti-dupe (#2+#6)** | **IN BRANCH** | Hero = name+line+visual only · no foundation/pills · Act2 owns facts · `journeyAntiDupe` · Act3 text draft [PROFILE_ACT3_NODE_DRAFT_V0.md](profile/PROFILE_ACT3_NODE_DRAFT_V0.md)
- 2026-07-30 | Profile / UI | **Natal chart object track closed** | **ACCEPTED** | Owner: карта ок · stop material/layout polish on wheel · 3D remains no-go · next Profile work = Motion B live accept (accents, not chart) or Acts 3–5 journey (content → then Visual Modes #4)
- 2026-07-30 | Profile / UI | **Natal 3D closed + no plate tilt** | **ACCEPTED** | Owner QA: chart reads as atmospheric object (starfield · focus chords · seal icons) — **WebGL/3D no-go** · remove pointer tilt/parallax · zodiac markers tint all four elements (jewel family), not fire-only
- 2026-07-30 | Profile / UI | **Why formation full-width 2-col** | **IN BRANCH** | Step 2 cards: drop desktop 4-col (left-clustered skinny cells) · 1 col mobile / 2 col desktop stretch scene width — same pattern as Effort spheres · odd/only orphan spans full row so selected/leftover cards are not left-guttered
- 2026-07-30 | Profile / UI | **Natal planet seal icons** | **IN BRANCH** | Heavier mask-optimized SVGs (`planets/*.svg` stroke 2.75 + filled cores) · inline/`PLANET_STROKE` parity · slightly larger disc glyph · iOS stroke weight · **3D closed** (see row above)
- 2026-07-30 | Profile / UI | **Effort spheres 2-col full width** | **IN BRANCH** | Step 5: drop desktop focus‖spheres split (looked like 3 skinny cols) · spheres grid = 1 col mobile / 2 col desktop, both stretch full scene width
- 2026-07-30 | Profile / UI | **Natal aspect chords outside hub** | **IN BRANCH** | Majors drawn disc↔disc across the plate (halo + legend color), not in the shrunk center well · painted web SoT = longitudes (10 planets), not sparse API BODY_PAIRS · legend counts from painted lines · hint copy updated
- 2026-07-29 | Profile / UI | **Natal wheel CSS material pass** | **IN BRANCH** | Lit planet discs + drop shadow · aspect weight hierarchy (`natalWheelMaterial`) · soft→strong paint order · light CSS plate tilt + layer parallax · `prefers-reduced-motion` off · no WebGL
- 2026-07-30 | Profile / UI | **Motion accents (B) regression audit** | **VERIFIED IN TESTS** | Checklist separate from chart polish: CTA breathe · pattern-sweep · aspect-wave retargeted to `natal-aspect-web` (was dead on layerMid after chords) · Act2 selectedOnceReveal · Sun/Moon/ASC/MC tap expand · reduced-motion + `profileMotionOnce` no replay · suite: DecodePanel / WhyScene.motion / NatalChartWheel.motion / profileMotionOnce (15 pass)
- 2026-07-29 | Profile / UI | **Profile motion accents (B)** | **IN BRANCH** | Decode CTA attention-breathe while unopened · one-shot pattern sweep + aspect wave on first grounded Decode · Act2 `selected_by` one-shot reveal · Sun/Moon/ASC/MC tap expand+shadow · `profileMotionOnce` localStorage · Act1 idle · 3D still go/no-go after live QA · see 2026-07-30 audit row
- 2026-07-29 | Profile / UI | **Natal wheel composition fix** | **IN BRANCH** | Compress dead center + vignette · stellium collision avoidance (`natalWheelLayout`) + leaders · warm/cool aspect colors (not thickness-only) · layer lightness · planet chip wrap/fade · stronger legend · 3D still deferred
- 2026-07-29 | Profile / UI | **Natal wheel full-bleed stage** | **IN BRANCH** | Atmospheric Decode stage (element tint) · dock controls on map · paper reading + full map below · larger plate / tighter SVG margins for stelliums · 3D-ready container
- 2026-07-29 | Profile / UI | **Natal stellium collision + house band** | **IN BRANCH** | Aggressive layout (spiral/fan) · house numbers off planet ring · leaders = belt whiskers not center spokes · center 0.28 + element label
- 2026-07-29 | Profile / UI | **Natal stellium pass 2** | **IN BRANCH** | Stronger spiral/fan · houses into zodiac ring · center 0.22 + element label · aspect donut-clip (no opposition spoke) · short solid leader stubs
- 2026-07-29 | Profile / UI | **Natal stage fill + clip** | **IN BRANCH** | Plate fills stage width · drop tall min-height · `natalScene` overflow:hidden with border-radius · stageAura inset 0 (no side bleed)
- 2026-07-29 | Profile / UI | **Natal hub + majors-only** | **IN BRANCH** | Element hub display type + icon · no mobile select stubs · Ptolemaic majors only in web/panel (sesqui filtered) · brand PlanetIcon on discs
- 2026-07-29 | Profile / UI | **Natal selection → aspect chords** | **IN BRANCH** | Select/hover lights major planet↔planet chords (legend colors) · dims unrelated discs · soft house spokes · hide leader ticks under focus
- 2026-07-29 | Profile / UI | **Natal stage starfield** | **IN BRANCH** | Decode stage background uses brand `/images/cosmic/stars.webp` under element washes (+ clipped aura pass)
- 2026-08-01 | Profile / UI | **Visual Modes #4 — Acts 3–5** | **IN BRANCH** | Act3 `insight-spine` · Act4 `effort-direction` · Act5 `bridge-portal` · glance @390 `/dev/profile-journey-preview` OK · decode blocked CTA dupe fixed · [PROFILE_VISUAL_MODES_V0.md](profile/PROFILE_VISUAL_MODES_V0.md) · human prod accept optional
- 2026-08-01 | Profile / Content | **Acts 3–5 scenarist prose QA (CE + guards)** | **IN BRANCH** | CE v0.8: Forms titles by living · preserve `living_evidence` · scrub «сегодня» from helps · effort_vector v0.2 action-start + no day agenda · bridge repeat without «сегодня» · FE drop duplicate insight eyebrow · optional essay voice polish remains
- 2026-07-30 | Profile / Content | **Act 4–5 form: swipe spheres + bridge** | **IN BRANCH** | Effort: horizontal snap cards + tap expand · [PROFILE_ACT4_EFFORT_DRAFT_V0.md](profile/PROFILE_ACT4_EFFORT_DRAFT_V0.md) · [PROFILE_ACT5_BRIDGE_DRAFT_V0.md](profile/PROFILE_ACT5_BRIDGE_DRAFT_V0.md)
- 2026-07-30 | Profile / Content | **Act 3 form align vs draft** | **IN BRANCH** | Vertical cascade · living honesty · hide warehouse triad · [PROFILE_ACT3_NODE_DRAFT_V0.md](profile/PROFILE_ACT3_NODE_DRAFT_V0.md)
- 2026-07-29 | Profile / Content | **Acts 3–5 scenario backlog** | **OPEN** | Form + prose guards wired · remaining = optional essay-bank voice vs Forms samples · then Visual Modes (#4)
- 2026-07-28 | Profile / UI | **Why formation with meaning** | **IN BRANCH** | Шаг 2: selected vs influenced blocks · each anchor fact+meaning · no decorative chips · `buildWhyFormationCards` · Forms/Surface
- 2026-07-28 | Profile / UI | **Essence foundation on Шаг 1** | **IN BRANCH** | Sun/Moon/ASC/MC/LP/PY move into «Твоя суть» with RU fact + meaning · Explore drops bare signature dump · Surface/Forms updated · `buildEssenceFoundationCards`
- 2026-07-27 | Profile / UI | **House theses not encyclopedia** | **IN BRANCH** | Web life map + full map never use natal `interpretations.houses` · short `HOUSE_FALLBACK` · iOS parity + decode CE `character_engine_house_lines_v0` on chart
- 2026-07-27 | Profile / UI | **Natal Decode FE CTA** | **LIVE** | `ProfileNatalDecodePanel` on Profile V2 · GET offer · POST generate · Deep Sources depth, not second portrait
- 2026-07-27 | Profile / Today | **CE day angle continuity v0** | **LIVE** | DayContext `character_continuity` · ExperienceSlice `primary_tension` · same hero + rotating `day_angle` · `character_engine_day_angle_v0` · Scenario §3.1 wire
- 2026-07-27 | Profile / Canon | **CE retention mechanics (§3.1)** | **ACTIVE** | From sealed golden 01–06: logline=mechanism · one tension=serial · day_hook=now · honest cost · Today=angle not new hero · Scenario **v1.1.3** · prompts stage2 **1.1.1** · natal_decode **1.0.1** · Content defects · Surface Шаг 5
- 2026-07-27 | Profile / Canon | **Natal Decode Depth v1** | **ACCEPTED + wire v0** | Opt-in depth поверх CE · explicit `POST /account/profile/natal-decode` · houses = theses · [PROFILE_NATAL_DECODE_DEPTH_V1.md](profile/PROFILE_NATAL_DECODE_DEPTH_V1.md) · Scenario v1.1.2 · **не** parallel personality root
- 2026-07-26 | Profile / Architecture | **CE Profile GET assemble-once** | **LIVE** | No CE LLM / no Stage recompute on GET when Stage 5 present · fill-once persisted · natal-chart style load.
- 2026-07-26 | Profile / Architecture | **CE Stage 5 assembly** | **LIVE SHADOW** | Deterministic Compass + adapters · no LLM · consumption v0.7 · [CHARACTER_ENGINE_STAGE5_ASSEMBLY_V0.md](audits/CHARACTER_ENGINE_STAGE5_ASSEMBLY_V0.md). Cutover supersedes «forming only».
- 2026-07-26 | Profile / Architecture | **CE Stage 4 life_bundle** | **LIVE SHADOW** | Prompt `stage4.v1` **1.0.0** · scenes/potential/blind_spots · [CHARACTER_ENGINE_STAGE4_LIFE_V0.md](audits/CHARACTER_ENGINE_STAGE4_LIFE_V0.md). Deployed with Stage 3.
- 2026-07-26 | Profile / Architecture | **CE Stage 3 Internal Engine** | **LIVE SHADOW** | Prompt `stage3.v1` **1.0.0** · [CHARACTER_ENGINE_STAGE3_INTERNAL_V0.md](audits/CHARACTER_ENGINE_STAGE3_INTERNAL_V0.md).
- 2026-07-26 | Profile / Architecture | **CE → Profile consumption slice v0** | **LIVE v0.7** | Stage 5 adapters preferred when grounded · Stage 3–4 fallback · Swiss natal facts kept · [CHARACTER_ENGINE_PROFILE_CONSUMPTION_V0.md](audits/CHARACTER_ENGINE_PROFILE_CONSUMPTION_V0.md).
- 2026-07-26 | Profile / Architecture | **CE Stage 2 live retest** | **HOLD superseded** | Owner override → Stage 3+. Diagnostics note: [CHARACTER_ENGINE_STAGE2_LIVE_RETEST_V0.md](audits/CHARACTER_ENGINE_STAGE2_LIVE_RETEST_V0.md).
- 2026-07-26 | Profile / Architecture | **CE Stage 2 staging eval** | **GATE PASS** | Prompt `stage2.v1` **1.1.0** · 15/16 grounded · [CHARACTER_ENGINE_STAGE2_STAGING_EVAL_V0.md](audits/CHARACTER_ENGINE_STAGE2_STAGING_EVAL_V0.md).
- 2026-07-26 | Profile / Architecture | **CE Stage 0–1 registry expansion v1** | **GATE PASS** | 13 rules · 16 fixtures · [CHARACTER_ENGINE_STAGE01_STAGING_EVAL_V0.md](audits/CHARACTER_ENGINE_STAGE01_STAGING_EVAL_V0.md).
- 2026-07-26 | Profile / Architecture | **CE Stage 2 live shadow** | **ON / REVIEWED** | `STAGE2_SHADOW=1` · [CHARACTER_ENGINE_STAGE2_LIVE_REVIEW_V0.md](audits/CHARACTER_ENGINE_STAGE2_LIVE_REVIEW_V0.md). Superseded for gate by live retest HOLD. **Next:** owner §1.4 skim · no Stage 3.
- 2026-07-25 | Profile / Architecture | **CE Stage 0–1 live review** | **CONDITIONAL GO** | [CHARACTER_ENGINE_STAGE01_LIVE_REVIEW_V0.md](audits/CHARACTER_ENGINE_STAGE01_LIVE_REVIEW_V0.md) · Stage 0 cache-shape fix · thin registry empty rate high.
- 2026-07-25 | Profile / Architecture | **CE Stage 2 Identity Core** | **IN_PROGRESS** | LLM-first prompt `profile.character_engine.stage2.v1` · structural/provenance gates only · **Baseline:** `5eb61c6`. **Exit criterion (canon §1.4):** Identity Core = sole SoT for Stage 3–5; later stages expand, never reinterpret. Gate to Stage 3: «This is a manifestation of the Identity Core because…» feels natural on most production-like packs. **Live:** Stage 2 shadow ON — see Stage 2 live review. Next: voice/exit review → Stage 3 only after criterion.
- 2026-07-25 | Profile / Architecture | **CE Stage 0–1 staging eval** | **GATE PASS** | Fixed fixtures · registry tightened · [CHARACTER_ENGINE_STAGE01_STAGING_EVAL_V0.md](audits/CHARACTER_ENGINE_STAGE01_STAGING_EVAL_V0.md). **Baseline:** `5eb61c6` — staging + Stage 2 results refer to this SHA, not branch tip. **Live recipe:** `STAGE01_SHADOW=1` · `STAGE2_SHADOW=1` · `STAGE*_ENABLED=0` · `PUBLISH_READY=0`.
- 2026-07-25 | Profile / Architecture | **CE Stage 0–1 shadow** | **LIVE** | Facts pack + evidence · diagnostics-only · funnel/`personality` remain publish SoT. **Next:** keep with Stage 2 shadow; expand registry only carefully after Stage 2 voice review.
- 2026-07-25 | Profile / Architecture | **CE Schema Contracts v0.2** | **DRAFT+validate** | Machine schema + local validation landed (`docs/schemas/character_engine_v1.schema.json` · fixtures · `character_engine_ids_v0` · pytest · `scripts/validate_character_engine_contract.py`). **CI job pending workflow-capable push** (local `ci.yml` patch not remote). **Next:** land CI when token has `workflow` scope.
- 2026-07-25 | Profile / Architecture | **CE Schema Contracts v0.1** | **SUPERSEDED → v0.2** | identity/provenance draft; see v0.2.
- 2026-07-25 | Profile / Architecture | **CE Architecture Impact D1–D4** | **ACCEPTED** | [CHARACTER_ENGINE_ARCHITECTURE_IMPACT_V1.md](audits/CHARACTER_ENGINE_ARCHITECTURE_IMPACT_V1.md): D1=`payload.character_engine_v1` · D2=Evidence Graph + Swiss authority · D3=stages 0–6 · D4=adapters + Shadow≠SoT. **Next:** schema track (in progress).
- 2026-07-25 | Profile / Canon | **CE Runtime Inventory v0** | **DONE** | [CHARACTER_ENGINE_RUNTIME_INVENTORY_V0.md](audits/CHARACTER_ENGINE_RUNTIME_INVENTORY_V0.md): preferred `personality` path vs live disclosure funnel/oneshot · Snapshot=`core_profile_snapshots` · kill list · D1–D4 closed via Impact doc.
- 2026-07-25 | Profile / Canon | **Character Engine Scenario v1.1.1 + matrix scrub** | **ACTIVE** | Header=1.1.1 · §8 wiring track · Availability Matrix dual roots scrubbed · `growth` deprecated as root. Residual: canon ≠ runtime until wiring.
- 2026-07-25 | Profile / Canon | **Character Engine Scenario v1.1** | **SUPERSEDED → v1.1.1** | См. строку выше.
- 2026-07-25 | Profile / Canon | **Profile Experience Scenario v1** | **SUPERSEDED → v1.1 Character Engine** | См. Character Engine v1.1.1.
- 2026-07-25 | Ops / Agents | **SoT stack clarified** | **ACTIVE** | Authority: **canon → backlog/tracker → server (live)**. Git = ledger only. Root `AGENTS.md` + `.cursor/rules/architecture-impact.mdc` updated.
- 2026-07-25 | Profile / UI | **Premium Profile pass · natal instrument + book scroll** | **ON SERVER** | Canon: Foundation UI «дорого без текста» · PROFILE_SCREEN_MASTER §0.2–0.3. Natal = one `instrument` bezel (plate+dial+selector) · planets angular fan inside rim · Journey/Bridge/Natal scenes stitched as chapters (hairline + air, no card stack). Today untouched. **Next:** owner mobile QA.
- 2026-07-25 | Today / Architecture | **day_thesis + evidence pack in DayContext** | **IN_PROGRESS** | Evidence + FE parity · formula bank + **SP links** + `vibe_strokes` · TL-1 blocked · next: TL-0C.3 editorial marking · linked: [TODAY_LANGUAGE_STRONG_PATTERNS_V0.md](./today-language/TODAY_LANGUAGE_STRONG_PATTERNS_V0.md)
- 2026-08-03 | Today / Ops | **DB pool starvation from sync prewarm** | **DONE** | Cron/GET no longer hold request session on LLM · enqueue `day_prewarm` ≤2 concurrent · pool_size 12 · FE: clear session only on `/auth/me` 401 · login claim fire-and-forget · `/auth/me` 10s abort
- 2026-08-03 | Today / Lifecycle | **ready_at 05:00 + catch-up/auth harden** | **DONE** | ready **05:00** · assemble **03–05** · candidates+=AstroProfile/activity · GET assembling→`day_prewarm` job · cron max-time 600 · guest-claim soft 401 no longer wipes JWT · login no longer awaits story refresh · canon [DAY_LIFECYCLE_V1.md](./audits/DAY_LIFECYCLE_V1.md)
- 2026-08-03 | Today / Lifecycle | **ready_at → 05:00** | **SUPERSEDED → row above** | Clock **03:00–05:00 assemble / ready 05:00** · push `morning_time`+`quiet_end` **05:00** · canon [DAY_LIFECYCLE_V1.md](./audits/DAY_LIFECYCLE_V1.md)
- 2026-07-26 | Today / Lifecycle | **Day Lifecycle V1 (assemble once)** | **DONE** | Clock was 05:00–07:00 / 08:30 → superseded by ready_at 05:00 row · GET never assembles · calm open from cache · pre-warm + catch-up · canon [DAY_LIFECYCLE_V1.md](./audits/DAY_LIFECYCLE_V1.md)
- 2026-07-26 | Today / Scenario | **Day Scenario Human Golden C3.6.2** | **DONE (pilot sealed)** | Batch [c362_blind_pilot_20260726](./audits/day_scenario_human_golden/batches/c362_blind_pilot_20260726/) · A+B agent blind · **7/7 sealed** (4 pass / 1 acceptable / 2 reject B5 clones) · evidence used by C3.6.3
- 2026-07-26 | Today / Scenario | **Day Scenario Gate Promotion C3.6.3** | **DONE** | Canon [DAY_SCENARIO_GATE_PROMOTION_C363.md](./audits/DAY_SCENARIO_GATE_PROMOTION_C363.md) · SCENE_CLONE/MISSING_EVERYDAY/ABSTRACT/ASTRO_JARGON_BARE → **blocking** (retry→unavailable) · SCENE_UNIVERSAL_ADVICE → candidate_blocking
- 2026-07-26 | Today / Scenario | **Day Scenario Human Golden EN expansion** | **DONE (20 EN sealed)** | Batch [c362_en_expansion_20260726](./audits/day_scenario_human_golden/batches/c362_en_expansion_20260726/) · curated EN · **20/20 sealed**
- 2026-07-27 | Today / Scenario | **Day Scenario Human Golden RU live → 40** | **DONE** | Batch [c362_ru_live_expansion_20260727](./audits/day_scenario_human_golden/batches/c362_ru_live_expansion_20260727/) · **13/13 sealed** · inventory **40/40** (20 RU · 20 EN)
- 2026-07-27 | Content / Voice | **LLM practitioner-friend persona** | **DONE** | Voice Canon §1 v1.7 · `llm_practitioner_persona_v1` wired into narrative / guide funnel / day_story · roles: tarot·numerology·astro·psych·sexology + friend
- 2026-07-27 | Today / Product | **Today Depth Layer voice (analytic)** | **DONE** | Deepen prompt = observation→mechanism→testable step · no faux solemnity · FE/CTA labels aligned · [TODAY_DEPTH_LAYER_V1.md](./TODAY_DEPTH_LAYER_V1.md) Voice
- 2026-07-27 | Today / Product | **Today Depth Layer step 3 (FE picker)** | **DONE** | `TodayDepthLayerSection` · chips from `contract.depth_layer` · Free CTA / Paid generate
- 2026-07-27 | Today / Product | **Today Depth Layer step 2 (contract offer)** | **DONE** | `GET /today/contract` → `depth_layer` menu + can_generate · SCREEN_CONTRACTS §3.3 · **next:** FE picker
- 2026-07-27 | Today / Product | **Today Depth Layer step 1 (gate)** | **DONE** | `today_depth_layer_v1` · topics + `intimacy` · Free deepen → CTA · Trial/Paid generate · [TODAY_DEPTH_LAYER_V1.md](./TODAY_DEPTH_LAYER_V1.md)
- 2026-07-27 | Today / Product | **Today Depth Layer (optional deepen)** | **ACCEPTED (canon)** | [TODAY_DEPTH_LAYER_V1.md](./TODAY_DEPTH_LAYER_V1.md) · Free+Paid = полный base day · Paid/Trial = выбор темы поверх · **запрет** прятать главы · Matrix §3.2 + Understanding Progress §4 · **next:** step 2 contract offer
- 2026-07-27 | Today / Scenario | **Day Scenario ASTRO_JARGON FP fix** | **DONE** | Lived-metaphor markers + echo-template guard · calib shadow false_blocks **0** (was 2) · ASTRO P 0.5→0.625 · **next:** UNIVERSAL_ADVICE recall
- 2026-07-27 | Today / Scenario | **Day Scenario Everyday specificity gap** | **DONE** | `SCENE_MISSING_EVERYDAY` lived-specificity (thin tip/template) · calib P=R=1.0 · shadow false cleared by jargon fix above
- 2026-07-27 | Today / Scenario | **Day Scenario Human Calibration C3.6.2** | **DONE** | Baseline [DAY_SCENARIO_HUMAN_CALIBRATION_BASELINE_C362.md](./audits/DAY_SCENARIO_HUMAN_CALIBRATION_BASELINE_C362.md) · 40 sealed · CHORUS_SEMANTIC_DUPLICATION → **candidate_blocking** · UNIVERSAL_ADVICE stays candidate
- 2026-07-26 | Today / Lifecycle | **Day Lifecycle V1 (assemble once)** | **SUPERSEDED → row above** | prior tracker wording before cron wiring
- 2026-07-26 | Today / Scenario | **Day Scenario SoT + product capture** | **IN_PROGRESS** | Canon [DAY_SCENARIO_V1.md](./DAY_SCENARIO_V1.md) · **B1–B5 + C1–C3.6.3 + C4 landed** · **next:** UNIVERSAL_ADVICE recall
- 2026-07-26 | Today / Scenario | **Day Scenario SoT + product capture** | **SUPERSEDED → C4 row** | C3.6.1 calibration (`c1c2b8d`); next was human golden then pipeline credibility.
- 2026-07-26 | Today / Scenario | **Day Scenario SoT + product capture** | **SUPERSEDED → C3.6.1 row** | C3.6 maturity runtime policy (`acbd06e`); next was calibration.
- 2026-07-26 | Today / Scenario | **Day Scenario SoT + product capture** | **SUPERSEDED → C3.6 row** | C3.5.1 eval hardening only (`c57f8e0`); superseded by Gate Maturity runtime policy.
- 2026-07-25 | Today / Scenario | **Day Scenario SoT + product capture** | **SUPERSEDED → 2026-07-26 C3.5.1 row** | C3.5.0 14d pack; see updated row above.
- 2026-07-01 | Product | **Build Map v0.5.5 — `DailySymbols` spec 🟢** | **ACTIVE** | Wave 1: color + stone · umbrella entity · [TODAYFLOW_PRODUCT_BUILD_MAP.md](./TODAYFLOW_PRODUCT_BUILD_MAP.md)
- 2026-07-01 | Product | **Invisible Mechanism CLOSED** | **CLOSED** | §5.6 · Build Map · dual Internal/External · 4 user knowledges — не revisiting
- 2026-07-01 | Product | **Build Map v0.2** | **REVOKED** | Component Catalog → Entity Catalog
- 2026-07-20 | Backend / LLM | **Quality-first Nebius + disclosure funnels** | **DONE** | `LLM_PROVIDER=nebius` · `LLM_QUALITY_MODE=rich` default · prompt registry · child surface 2-step funnels · profile 3-step portrait · [LLM_QUALITY_AND_PROMPT_EVOLUTION.md](./LLM_QUALITY_AND_PROMPT_EVOLUTION.md)
- 2026-07-20 | Profile / LLM | **profile-contract-v3 DoD hardening** | **IN_PROGRESS** | 4-step funnel · strict+quality validation · forming (no scaffold) · per-prompt versions in meta · hash lock/cache · pytest DoD green · FE no template spheres while forming · **next:** 20–30 live DeepSeek samples
- 2026-07-20 | Product / Audit | **User journey audit (guest→Today)** | **IN_PROGRESS** | Doc [USER_JOURNEY_AUDIT_2026-07-20.md](./audits/USER_JOURNEY_AUDIT_2026-07-20.md) · Tarot/Numerology module GET gated `not_selected` + reveal POSTs · hub no COD spoil · **open:** morning/Today redact pre-ritual · guest transfer · product decisions on pick vs reveal
- 2026-07-20 | Today / Reveal | **P0 day symbol SoT** | **DONE** | `day_symbol_states` · `/today/symbols/*` · morning redact · ritual FE reveal · guest claim · matrix pytest · canon [DAY_SYMBOL_REVEAL_CANON_V1.md](./audits/DAY_SYMBOL_REVEAL_CANON_V1.md) · **overlay-only** (no day reassemble on reveal) 2026-07-26
- 2026-07-20 | Today / Story | **day_story fingerprint rebuild** | **SUPERSEDED** | Was: reveal → `story_refresh_required`. **Now (2026-07-26):** fingerprint **excludes** card/number; reveal returns `symbol_overlay_only` + `story_refresh_required=false`; mood/goals may still invalidate · tests `test_day_story_rebuild_v1.py` · see DAY_LIFECYCLE_V1
- 2026-07-26 | Today / Lifecycle | **symbol overlay no-rebuild + number dash fix** | **DONE** | BE fingerprint/API · FE no `refreshTodayStory` on reveal · number resolve on pick · canon DAY_LIFECYCLE + DAY_SYMBOL_REVEAL
- 2026-07-20 | Auth / Guest | **full guest claim** | **DONE** | `guest_sessions` + `guest_day_snapshots` + claim token · `POST /today/guest/*` · atomic claim · conflict canon · FE sync/claim · tests `test_guest_claim_full_v1.py` · **next:** interpretation quality audit
- 2026-07-20 | Today / Quality | **interpretation quality audit** | **IN_PROGRESS** | Doc [INTERPRETATION_QUALITY_AUDIT_2026-07-20.md](./audits/INTERPRETATION_QUALITY_AUDIT_2026-07-20.md) · generation map · IQ-001/002 dual-influence fixes · `day-story-v1.1` · eval 100 + blind harness · pilot n=4 both schema OK (DeepSeek ~41s / Kimi ~22s, Kimi needs ≥4k tokens) · backend redeployed · **next:** human blind score 20→100 · EN/PL prompts · FE hardcode gates · consistency evaluator
- 2026-07-21 | Product / Canon | **Full user path canon v1** | **IN_PROGRESS** | Doc [FULL_USER_PATH_CANON_V1.md](./audits/FULL_USER_PATH_CANON_V1.md) · audit docs↔BE↔FE↔iOS · target journey landing→D30 · contradictions X1–X15 · generation registry · **no UI/code edits yet** · **next:** product accept X* → update FIRST_DAY / TODAY_SCREEN / blueprint → then implementation
- 2026-07-21 | Product / Canon | **§3 Canonical Personal Knowledge Principle** | **REVERTED** | Ошибочно поднят как новый закон; идея уже в Personal Model / PIL / DATA_OWNERSHIP · откат церемонии §3 · **вместо этого:** [PERSONAL_MODEL_CODE_COMPLIANCE_2026-07-21.md](./audits/PERSONAL_MODEL_CODE_COMPLIANCE_2026-07-21.md)
- 2026-07-21 | Eng / Audit | **Personal Model code compliance** | **IN_PROGRESS** | Doc [PERSONAL_MODEL_CODE_COMPLIANCE_2026-07-21.md](./audits/PERSONAL_MODEL_CODE_COMPLIANCE_2026-07-21.md) · **P0 DONE:** `build(publish_portrait=)` gate · GET no portrait LLM · `POST /account/core-profile/refresh` · Compat life_path from Snapshot/store · GenerationLog provenance · tests `test_core_profile_read_path_no_llm_v1.py` · **next P1:** Experiences consume CUM/contract slice · Compat profile_a/b = snapshot · **then C3** profile quality
- 2026-07-21 | Eng / Audit | **P1 Experience wiring** | **IN_PROGRESS** | Doc [PERSONAL_MODEL_EXPERIENCE_WIRING_P1_2026-07-21.md](./audits/PERSONAL_MODEL_EXPERIENCE_WIRING_P1_2026-07-21.md) · **SoI:** Formal single source without shared contract assembler → divergent understanding · target: Snapshot → **Experience Contract** → allowlist ExperienceSlice · Experience Consistency Tests (decision/conflict/communication/motivation/energy) · Tarot dead wiring · order P0→P1→C3→Telemetry · **next:** implement assembler_v0 + Consistency Tests · then C3
- 2026-07-21 | Content / C2 | **Compatibility content v1.1 production** | **DONE (guest+registered under flag)** | publish_gate in enrichment · Voice Canon architectural · prompt freeze until user data · **next:** telemetry; premium ≥5 real Q
- 2026-07-21 | Product / Metric | **Reference Rate (hardened)** | **RESERVED** | Prior knowledge impossible from current input alone · **in use** when comparable across modules (Today vs Tarot) and drives decisions · [PROFILE §7.2](profile/PROFILE_CONTENT_CANON_V1.md)
- 2026-07-21 | Product / Roadmap | **Longitudinal Validation** | **RESERVED (after C3, not C4)** | **Hypothesis:** model changes only with enough confirmed facts — not regen/prompt drift · [PROFILE §7.3](profile/PROFILE_CONTENT_CANON_V1.md) · exit criteria for C3/Telemetry in §7
- 2026-07-21 | Product / Roadmap | **Stage exit criteria (C3→Telemetry→RR→LV)** | **CANON** | Order frozen · C3: 4-step / unique knowledge / no section echo / prior as knowledge source · Telemetry: reads·confirm·regen·fallback·RR trend · [PROFILE §7](profile/PROFILE_CONTENT_CANON_V1.md)
- 2026-07-21 | Product / Roadmap | **Hypothesis falsifiers** | **RESERVED (after first real-user weeks)** | When to reject RR / Longitudinal / Consistency hypotheses · not engineering DoD · [PROFILE §7.4](profile/PROFILE_CONTENT_CANON_V1.md) · do not formalize yet
- 2026-07-01 | Product | **Launch Scope Freeze** | **ACTIVE** | Epic 1–4 only; Figma → code → 10×7d field; [WEB_LAUNCH_PRODUCT_BLUEPRINT.md](./status/WEB_LAUNCH_PRODUCT_BLUEPRINT.md)
- 2026-07-01 | Product | **TodayFlow Product Model v0.2** | **FROZEN** | Living model, Lifecycle, laws; doc №1 — no launch-scope edits until user test.
- 2026-06-22 | Engineering | P0.2 Today Experience (web) | PAUSED | Gate до ACCEPTED канона — снят 2026-06-23.
- 2026-06-22 | Engineering | P0.2.1 Unified day synthesis (web) | DONE | `todayUnifiedSynthesis.ts` + `todaySynthesisTextPolicy.ts`; one headline + paragraphs; RU tarot weave (Tower↔stability bridge); EN filter; thematic evening prompt; semantic cards deduped vs synthesis; tests green; iOS after web gate.
- 2026-06-22 | Engineering | P0.2.2 Ritual reveal gate (web) | DONE | `todayRevealGate.ts`; no card name / day number in UI before pick+reveal; experience starts at closed-card grid + symbol tiles; spine ribbon removed; synthesis gated until both ack; `TodayExperienceSurface` auto-opens day.
- 2026-06-22 | Product / Architecture | Today Experience Scenario v1 | ACTIVE | [TODAY_EXPERIENCE_SCENARIO_V1.md](./TODAY_EXPERIENCE_SCENARIO_V1.md): data vs narrative vs experience; phase machine; block registry; anti article-scroll; next after P0.1.3.
- 2026-06-22 | Engineering | P0.1.3 Today Narrative Layer + Growth skill | DONE | `todayNarrativeFromContract.ts` + `TodayNarrativeView`; growth observation reject; ritual/default Today unified story UI; before experience phases.
