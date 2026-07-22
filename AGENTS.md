# AGENTS — TodayFlow

Scope: **this repository only** (`TodayFlow`).

## Read order

1. [docs/README.md](./docs/README.md) — sole documentation entry point
2. The section for the screen/topic you touch (Product Map · Technical Architecture · Generation Registry · Implementation Status · Screen Maps)
3. Code paths named there (or found by search)

Documentation work rules: [`.cursor/rules/docs-single-canon.mdc`](./.cursor/rules/docs-single-canon.mdc).

## Hard rules

1. **Find first.** Search code and `docs/` before inventing a contract, map, registry, passport, or principle.
2. **No new SoT.** Do not introduce a second source of truth for an existing topic.
3. **Extend, don’t spawn.** Prefer updating an existing document over creating a new one.
4. **Code before docs.** Implement or verify against working code/API first; then update the existing canon. Do not write architecture docs ahead of a real runtime path.

## Default analysis shape

1. What already exists  
2. What is broken  
3. What is truly missing  
4. Minimal change  

If a change needs a new `*MAP*` / `*REGISTRY*` / `*PASSPORT*` / `*CANON*` file, follow `docs-single-canon.mdc` (justify in the PR why an existing doc could not be extended).
