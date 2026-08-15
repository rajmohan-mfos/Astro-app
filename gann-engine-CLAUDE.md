# Implementing the Gann Cosmogram rules inside Astro-app

A build brief for `rajmohan-mfos/Astro-app`, written against the repo as it stands.
Companion docs: `Gann_Trading_Course.md` (rule specs), `Bjybnf_Gann_Aspect_Master_Table.xlsx` (call archive + prior backtests).

---

## The headline: don't build a new engine

Astro-app already contains almost everything a Gann rule engine needs, and its statistical layer is stronger than most quant hobby projects:

| Need | Already in the repo |
|---|---|
| Ephemeris | `backend/app/engine.py` — swisseph, `FLG_MOSEPH \| FLG_SIDEREAL \| FLG_SPEED` |
| Rule plugin shape | `backend/app/rules/base.py` — the `Finding` dataclass with its `source` field |
| Price data | `backend/scripts/opt/prices.py` — absolute-window, disk-cached, **nifty + banknifty already wired** |
| Out-of-sample discipline | `backend/scripts/opt/walkforward.py` — nested vs best-of protocols, leakage assertion |
| Multiple-testing control | `backend/scripts/opt/permutation_null.py` — block-shuffled null, exactly the tool for this |
| Test convention | `backend/tests/test_*.py` |

So the work is **four additions**, not a new project. Note especially that `permutation_null.py` solves the biggest open problem from the manual analysis: ~25 Gann rules have been tested by hand, so roughly one spurious p<0.05 is expected by chance. The block-shuffled null measures that inflation directly instead of hand-waving at it.

---

## Addition 1 — extend the body list

`engine.py` currently has the classical seven (`BODIES`) plus Rahu/Ketu tokens. The Gann rules need the moderns:

```python
("Uranus", swe.URANUS), ("Neptune", swe.NEPTUNE)
```

Required by Venus–Neptune opposition, Uranus–Uranus trine, Mars–Uranus sesquisquare/trine, Mars–Neptune conjunction, Saturn–Uranus sextile, and the Sun/Uranus/Neptune pattern. Keep them out of the chart-token grid and panchang paths — they belong to the Gann layer only, so add them as a separate `GANN_BODIES` list rather than widening `BODIES` and disturbing existing chart tests.

---

## Addition 2 — `backend/app/gann/` (the mechanics)

```
backend/app/gann/
  aspects.py     # separation, exact-crossing detection, orb handling
  natal.py       # radix chart + transit-to-natal aspects
  sq9.py         # Square of 9: classic + modified increment
  fan.py         # Gann fan coordinates, sqrt-price scaling
  solar.py       # solar static/dynamic date windows
```

**Verified formulas** (regression-test these; they are checked against Swiss Ephemeris and NSE closes):

- Angular separation: `d = abs(a - b) % 360; sep = min(d, 360 - d)`
- Exact crossing: sign change of `wrap180(sep - target)` **with an `abs(diff) < 180` guard** — without it every 359°→1° step is a false hit
- Square of 9 next level: `(sqrt(price) + n * 0.25) ** 2`, n = 1 per 45° (n=4 → 180°, n=8 → full cycle)
- Modified Sq9 increment: `((major_high - major_low) / N) * 4`, N = candles between, **N > 150**. (The source video's wording implies `/(N*4)`; its own arithmetic gives the parenthesised form: (20222−18837)/183×4 = 30.27.)
- Solar date conversion: `days = degrees * 1.0146` (= 365.25/360)
- Fan sqrt scaling: from anchor `(bar B1, price P1)`, second point `(B1 + N, P1 ± N*sqrt(P1))` — plus from a low, minus from a high
- Daily snapshot hour: **09:15 IST = 3.75 UT**

---

## ⚠️ Addition 2a — the sidereal gotcha (read before writing `natal.py`)

The engine runs **sidereal (Lahiri)**. All the Gann analysis so far was tropical. This matters in exactly one place:

- **Transit-to-transit aspects are identical in both zodiacs.** The ayanamsa cancels in a difference taken at one instant — verified: Venus–Saturn separation on 15 Aug 2026 is 173.8013° in both. Every transit-only rule (Venus–Saturn quadrature, Venus–Jupiter quadrature, Mercury–Saturn conjunction, Mars–Jupiter semisquare …) can use the existing sidereal engine unchanged.
- **Transit-to-natal aspects are NOT.** Ayanamsa drifts ~50″/year, so between a 1996 radix and a 2026 transit it grows by **0.42°** (23.8055° → 24.2290°). A transit–natal separation that reads 112.062° tropical reads 111.637° sidereal. With orbs of 1–5° the aspect still fires, but **exact-crossing dates shift by roughly a third of a day for Venus**, and the "orb 0" rules are the ones that care.

**Decision to make explicitly** (and record in the module docstring): compute Gann transit-to-natal aspects **tropically** — i.e. call swisseph without `FLG_SIDEREAL` in `gann/natal.py` only — because that is the zodiac GannZilla uses and the zodiac all published rules were derived in. Keep the sidereal engine untouched for panchang/jothidam. Two zodiacs in one codebase is fine as long as each module states which it uses and a test asserts it.

**Natal fixtures (tropical, Nifty first trade 22 Apr 1996, `swe.julday(1996,4,22,6.5)`):**

| Body | Longitude |
|---|---|
| Mercury | 52.4° |
| Mars | 22.1° |
| Venus | 76.17° |
| Jupiter | 287.4° |
| Uranus | 304.5° |

---

## Addition 3 — `backend/app/rules/gann.py`

One function per rule, each returning `Finding` objects with `source` set to the course lesson, matching the existing convention in `graph.py` / `weekly.py`:

```python
Finding(section="graph",
        title="Venus–Jupiter quadrature",
        detail="Reversal expected; target 275 / SL 215 (54% hit vs 43% base, n=26, not significant)",
        source="Gann_Trading_Course.md Lesson 10")
```

**Carry the evidence in `detail`.** The whole point of the audit was that these rules are mostly at the noise floor — a rule that surfaces in the UI without its hit-rate-vs-base-rate attached will quietly become a belief.

Priority order (best-evidenced first): Venus–Jupiter quadrature (L10), Mercury–Saturn conjunction (L12), then the Sq9 and fan level tools (L3/L14/L15 — these make no accuracy claim and are useful regardless), then the rest as clearly-labelled null results.

---

## Addition 4 — wire into the existing study harness

Add the Gann event dates as features in `scripts/opt/features.py`, then run the rules through the harness that already exists:

1. `walkforward.py` — **nested** protocol only for any headline number. Best-of is not a performance estimate.
2. `permutation_null.py` — run the identical rule search against block-shuffled outcomes. If the real Gann result sits inside the null's distribution, that is the answer, and it should be published in the repo rather than buried.
3. Reserve the last 3 years as untouched holdout.

**Base rates every Gann rule must beat** (Nifty 2007–2026, already measured):

| Metric | Nifty | Bank Nifty |
|---|---|---|
| Mean 5-day forward return | +0.22% | +0.41% |
| 5-day forward positive | 56% | 55% |
| Trend flip on any day | 49% | — |
| **Trend flip within ±2 days of any day** | **85%** | — |
| ≥150pt counter-move within 2 days (2020–24) | 39% | — |

The 85% is the single most important number: any rule graded as "reversal within ±2 days, either direction" is measuring the calendar, not the sky.

---

## Pitfalls specific to this codebase

1. **Retrograde** is already available (`FLG_SPEED`, tuple index 3, `speed < 0`). Several rules *exclude* retrograde events — that filter is part of the spec.
2. **Multi-pass events.** Jupiter–Uranus and Jupiter–natalJupiter resolve as *three* exact passes over ~9 months. Group them; never let a rule score only the pass that worked.
3. **Aspect date ≠ trading date.** Map to a real session. The source's holiday convention is the **previous** session; implement it as a flag since forward-mapping gives different results.
4. **No lookahead.** Entry at the close of the mapped session.
5. **Calendar traps.** Any pattern combining Sun/Moon with slow outer planets recurs in the same calendar week yearly (the Sun–Uranus–Neptune pattern is an October date in disguise). Have the report print a month histogram of each rule's event dates automatically.
6. **Don't disturb Layer A.** Panchang and chart tests are green; the Gann layer is additive and must not change `BODIES`, `FLAGS`, or `panchang()`.

---

## Suggested Claude Code session plan

1. `/init` is already satisfied — instead, drop this file plus the two course docs into the repo and reference them by path in prompts.
2. Plan mode for `gann/aspects.py` + `gann/natal.py` (the zodiac decision above is the thing to get right once).
3. Then rule-by-rule: *"Read Lesson 10 in docs/Gann_Trading_Course.md. Implement `venus_jupiter_quadrature` in rules/gann.py, plus its scorecard test using the opt/ harness."*
4. Add a hook running `pytest backend/tests/test_gann_golden.py` on every edit — the natal fixtures and Sq9 formula are exactly what a refactor breaks silently.
5. Keep `rules_tested.json` as a running count for the FDR correction.
