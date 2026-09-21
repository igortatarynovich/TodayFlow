# X4/X5 honest reveal copy — CLOSED / PASS

**Date:** 2026-09-21  
**Branch:** `cursor/x4-x5-honest-reveal-copy`  
**Base:** `14a739b0` (X4/X5 selection on `cursor/x3-theme-focus-step`)  
**Pass bound:** **X4/X5: CLOSED / PASS** (one joint gate). Locked T2-gate card chrome is a reveal, not a pick. Locked T2-gate number chrome is the calendar day number, not «своё». TIC remains **CLOSED / PASS**. N = 20. X3 remains **CLOSED / PASS**.

Not two trains. Not TIC-K21. Not landing. Not X11 leftover. Do not rebuild server until asked.

---

## 0. Decision (locked)

X4 and X5 close **together**. Live locked `T2-gate.card_*` no longer paints a prebaked card as a user choice. Live locked `T2-gate.number_*` no longer paints YYYYMMDD as a personal number. Overlay gesture was already honest and stays theater. Mechanic (DAY_SYMBOL prebake + POST reveal + YYYYMMDD) unchanged.

Selected next product remainder: Full User Path **X14**. Closing X4/X5 does not implement or close that gate. **X11 leftover narrative is CLOSED / PASS** on `cursor/x11-leftover-narrative`.

---

## 1. Live defects proven (then painted)

| Clause | Locked slot | Live before | Live after |
|--------|-------------|-------------|------------|
| **X4** | `T2-gate.card_body` (`DsRitualGate` body) | «Выбери ту, к которой тянет» | «Открой карту» |
| **X4 leftover** | unused `ritualTarotPickCta` | «Выбрать карту» | «Открыть карту» |
| **X5** | `T2-gate.number_title` (`DsRitualGate` title) | «Открой своё число дня» | «Открыть число дня» |
| **X5 leftover** | unused `ritualNumberPickCta` | «Выбрать число» | «Открыть число дня» |

Already honest, not this paint: overlay CTA «Открыть карту»; number ring `aria-label` «Открыть число дня»; §2 state A «Открой свою карту дня» (reveal of the day-card, not a pick). Out of gate: `todayRitualCopy` / `?full=1` / `?experience=1` = X11.

---

## 2. What passed

- Same 4-surface order. Card then number (A→B).
- No new Inventory slot. No new TIC-K. No producer change. No ScreenFlow reorder. No mechanic change.
- X3 lens copy still holds (card/number do not define the day or action timing).

Gate: `todayX4X5HonestReveal.test.tsx` · `todayX4X5GateCopy.test.ts`. X3 gates unchanged. TIC close-out unchanged PASS.

---

## 3. Do not

- Split X4 from X5 after this freeze.
- Invent TIC-K21 or resume TIC hops.
- Rebuild server. Merge/deploy only if asked.
- Start later Today remainder (**X14**) from this freeze. X11 leftover narrative is a separate closed gate.
- Reopen Glance as a fifth act. Resume PIC / IL / Compatibility IC.
