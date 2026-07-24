/**
 * Legacy global CSS modules (split from `app/globals.css`, phase 6).
 *
 * Cascade rule: import order in `app/globals.css` must stay exactly as listed.
 * Reordering files changes specificity conflicts and visual regressions.
 *
 * Regression check (manual, after any edit here):
 * - `/` landing (hero, return reasons, footer)
 * - `/today` (guest gate or ritual + day-phase atmosphere)
 * - `/profile` (guest gate or journey shell)
 * - `/tarot` (void atmosphere / product shell)
 *
 * Machine check: `npm test -- --testPathPattern=globalsCssSplit`
 * Fixture: `pre-split-body.fixture.css` (concat of module bodies without file headers).
 */
