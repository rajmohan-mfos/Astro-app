# Nifty 50 backtest — 2021-08-10 → 2026-08-10 (1,235 trading days)

Re-run 2026-08-11 after the full rules rebuild (sunrise casting, degree
counting, upside-wise conflict rule, day-lord rule, guide thithi families,
complete 27-yoga classification, Class-10 x1/x2 splitting).

Method: each trading day's sunrise-cast segments are reduced to a
duration-weighted score (bullish +1 … bearish −1); predicted direction =
sign(score), compared against the session direction (close vs open).
Panchang tally = thithi + ½·yogam + karanam, each ±1. Per-day data in
`nifty_backtest.csv`.

| Test | n | Hit rate |
|---|---|---|
| Baseline: share of up days | 1235 | 48.3% |
| **Engine direction, all directional days** | 1085 | **48.3%** |
| Strong-signal days (\|score\| ≥ 0.5) | 468 | 46.4% |
| Days with a real move (\|ret\| ≥ 0.25%) | 725 | 48.7% |
| Thithi positive → up | 865 | 48.7% |
| Thithi negative → down | 291 | 51.9% |
| Yogam positive → up | 727 | 46.8% |
| Yogam negative → down | 375 | 49.3% |
| Yogam **very** negative → down | 133 | 49.6% |
| Panchang tally ≥ +0.5 → up | 1071 | 47.8% |
| Panchang tally ≤ −0.5 → down | 164 | 48.2% |
| **Chain AND panchang agree (confluence)** | 563 | **45.5%** |

Per-year: 41.4 / 54.3 / 45.2 / 49.8 / 48.4 / 44.6 (2021→2026).

## Slice by weekday (`scripts/slice_backtest.py`)

| Weekday | Engine hit | Actual up-rate |
|---|---|---|
| Monday | 45.3% (n=214) | 53.4% |
| Tuesday | 47.1% (n=225) | 44.8% |
| Wednesday | 44.1% (n=213) | 50.2% |
| Thursday | 51.6% (n=219) | 43.7% |
| Friday | 53.1% (n=213) | 49.8% |

Spread 44–53%, each n≈215 (95% CI ≈ ±6.7%) — all inside noise. Not an
artifact of a directional tilt: the engine calls bearish on 47.7% of
days overall and 45–52% within every weekday.

## Slice by Moon's nakshatra lord (n≈137/lord, 95% CI ≈ ±8pp)

| Lord | Days | Mean % | Up-rate | Taught |
|---|---|---|---|---|
| Sun | 136 | +0.0943 | **58.1%** | neutral |
| Rahu | 132 | +0.0399 | 57.6% | extreme either way |
| Mercury | 137 | +0.0057 | 51.8% | **maximum positive** ✓ |
| Moon | 140 | −0.0257 | 47.9% | positive ✗ |
| Venus | 132 | −0.0825 | 45.5% | positive ✗ |
| Saturn | 144 | −0.0362 | 45.1% | strongly bearish ✓ |
| Mars | 132 | −0.0704 | 44.7% | 60% bearish ✓ |
| Jupiter | 141 | −0.1385 | **42.6%** | amplifies/bullish ✗ |
| Ketu | 141 | −0.0863 | 42.6% | maximum negative ✓ |

Baseline up-rate 48.3%. The two best-performing lords (Sun, Rahu) are the
two the course does **not** grade bullish; Jupiter — a bullish planet — is
the single worst cell in the table. Grouping taught-positive lords
(Mercury/Venus/Moon/Jupiter, 47.0%) against taught-negative
(Saturn/Mars/Ketu, 44.1%) gives a 2.8pp gap in the right direction, but
that is 0.9σ — noise, and both groups sit below the base rate.

## Slice by thithi family (n≈247/family, 95% CI ≈ ±6pp)

| Family | Days | Mean % | Up-rate | Graded |
|---|---|---|---|---|
| Bhadra | 254 | −0.0438 | 51.6% | positive |
| Purna | 237 | +0.0288 | 51.1% | neutral |
| Nanda | 247 | +0.0029 | 49.0% | positive |
| Rikta | 251 | −0.0222 | 47.0% | negative ✓ (weak) |
| Jaya | 246 | −0.1327 | **43.1%** | **positive** ✗✗ |

**Jaya — "the good positive for the market" — is the worst family**
(43.1% up, mean −0.13%, ≈1.7σ below baseline). The neutral-graded Purna
family is second best.

**The sharpest claim in the course fails its direct test:** Rikta thithis
are taught as destructive gap-down days (1,000–2,000 points). Days falling
≥1% on Rikta thithis: **6.8%** — versus **7.9%** on all other days. Rikta
days were *less* crash-prone than ordinary days.

## Slice by horai — 4,334 hourly bars over 724 sessions

**Method note that dominates the interpretation:** a horai lord is a
deterministic function of (weekday, slot index), so "Monday Mercury
horai" and "Monday's ~12:00 hour" are *the same bars*. No amount of data
can separate a planetary effect from weekday × time-of-day seasonality
here — the horai layer is a relabeling of the clock.

Day-independent horai table (guide §7): mean move per bar

| Horai | Bars | Mean % | Up-rate | Taught |
|---|---|---|---|---|
| Mercury | 722 | −0.0233 | 51.1% | up ✗ |
| Mars | 722 | +0.0044 | 50.0% | down ✗ |
| Saturn | 579 | −0.0096 | 49.1% | down ✓ |
| Jupiter | 579 | +0.0146 | 50.8% | up ✓ |
| Sun | 578 | −0.0215 | 49.8% | down ✓ |

3 of 5 signs correct, but every magnitude is 0.004–0.023% — roughly
1–6 Nifty points against the taught 30–100.

Weekday golden rules, with the same clock hour on other weekdays as the
control:

| Rule | Result | Same hour, other weekdays |
|---|---|---|
| Mon Mercury → up | **62.0%** (n=142), +0.0158% | hour 12: 52.0% up |
| Wed Venus → up | 56.9% (n=144), +0.0084% | hour 12: 53.2% up |
| Tue Saturn → down | 51.7% (n=147), −0.0229% | hour 11: 47.7% down |
| Fri Mercury → up | 46.2% (n=143), −0.0103% | hour 14: 45.1% up |

Open-in-Saturn-horai → down: 51.7% (n=143), mean −0.0166%. (Sun horai at
the open never occurs on a trading day — n=1.)

## Conclusion

No predictive edge at any level tested — daily direction, weekday,
nakshatra lord, thithi family, or hourly horai window.

**The headline.** 48.3% on 1,085 directional days, identical to the 48.3%
base rate of up days, and *down* from the 50.0% the pre-rebuild engine
scored. Every correction made this session (sunrise casting, degree
counting, the upside-wise conflict rule, the day-lord rule, the guide's
thithi families, all 27 yogas) moved the number slightly worse. That is
the signature of noise: had the earlier version been mis-implementing a
real edge, fixing it would have raised the score.

**Conviction filters run backwards.** Stronger signals do worse (46.4%),
and confluence — chain and panchang agreeing — is the single worst cell
at 45.5%, exactly inverting the teaching that agreement means high
conviction.

**The sharpest, most falsifiable claims fail in the direction they
assert:**
- *Rikta thithis = 1,000–2,000-point gap-downs.* Days falling ≥1% on
  Rikta thithis: 6.8%, versus 7.9% on all other days — less crash-prone
  than ordinary days (n=251).
- *Jaya = "the good positive for the market".* Worst of the five
  families at 43.1% up, mean −0.13%.
- *Jupiter = bullish/amplifying.* Worst nakshatra lord in the table at
  42.6% up, mean −0.14%. The two best lords (Sun 58.1%, Rahu 57.6%) are
  the two the course does not grade bullish.
- *Horai golden rules worth 30–100 Nifty points.* Measured effects are
  0.004–0.023% per bar, i.e. 1–6 points, below round-trip costs.

**The horai layer carries no information beyond the clock.** A horai lord
is a deterministic function of (weekday, slot index), so "Monday Mercury
horai" and "Monday's ~12:00 hour" are the same bars — the two can never
be separated by data. The one nominally striking cell (Mon Mercury 62.0%,
n=142) is ~2.1σ against the same hour on other weekdays, about what
chance yields across the ~15 comparisons run here, and worth ~4 index
points. Friday Mercury is the clean counter-demonstration: the rule says
up, it delivers 46.2%, and the same 14:00 hour on other weekdays delivers
45.1% — the clock explains the result, including the failure.

**Statistics.** At n≈1,100 the 95% CI is ≈ ±3pp; per-lord and per-family
slices carry ±6–8pp. Across ~30 comparisons in this document the largest
deviation is ~2.3σ, which is the expected maximum under the null. Nothing
here survives correction for multiple testing — in either direction, so
neither the Sun star-lord nor the Monday Mercury hour should be read as a
real effect.

**Caveats.** Ground truth is close-vs-open, so intraday *shape* (half-day
splits, angle reversals) is still untested — though the horai slice does
test hourly windows directly on 4,334 bars. Chennai coordinates
throughout; 60-minute bars cover 724 sessions (~2 years) versus 5 years
of daily data. None of these plausibly conceal an edge at this sample
size.

**Bottom line.** The app is a faithful, source-traced, regression-tested
implementation of the GRAHA MARKETS method. The method itself does not
forecast Nifty. Use it as a study tool; do not trade it.

## KP vs Lahiri ayanamsa (`scripts/compare_ayanamsa.py`)

Run 2026-08-11, after the prediction path moved to KP. Same 1,235 days,
same rule stack, same sunrise cast — the ONLY difference is the 0.097°
(5.8 arcmin) zodiac offset. Per-day data in `ayanamsa_compare.csv`.

| Test | KP | Lahiri |
|---|---|---|
| Chain direction, all directional days | **48.3%** (526/1090) | **48.3%** (525/1087) |
| Strong days (\|score\| ≥ 0.5) | 46.1% (n=464) | 46.3% (n=467) |
| Panchang tally sign | 48.5% (n=1235) | 48.5% (n=1235) |

Per-year (KP / Lahiri): 42.0/42.0 · 54.3/54.3 · 45.4/45.2 · 49.6/49.8 ·
48.0/48.2 · 44.6/44.6.

**The two are the same predictor 98.9% of the time.** Over five years the
chain directions disagree on **12 days out of 1,086**. Overall hit rates
therefore cannot separate them — they are ~99% the same numbers by
construction, not by evidence. On the 12 discordant days the split is
**6–6**, exact McNemar two-sided *p* = 1.000. The panchang tallies
disagree on 2 days out of 1,235.

**The comparison is underpowered by design, and no amount of care fixes
that.** With 12 discordant days, one method would have had to win 10 of
them (83%) to reach *p* < 0.05. To detect a genuine but realistic edge at
80% power you would need:

| If one ayanamsa truly wins… | discordant days needed | ≈ years of Nifty |
|---|---|---|
| 60% of disagreements | 194 | ~70 |
| 65% | 85 | ~31 |
| 70% | 47 | ~17 |
| 75% | 29 | ~10 |

At the observed ~1.1% discordance rate, five years of data can only ever
detect an implausibly large effect. A tie here is the expected result
whether or not one ayanamsa is genuinely better.

**Bottom line.** Neither is better; this test cannot tell them apart, and
a longer one almost certainly could not either. The choice of KP for the
prediction path rests on source fidelity — the teacher's own Moon transit
table and horai timings reproduce under KP and not under Lahiri (see
RULES-SOURCES.md) — and NOT on predictive performance, of which there is
none to allocate. Both sit at 48.3% against a 48.3% base rate, and both
are beaten by the trivial rule "always predict down", which scores 51.7%
because that is simply how often Nifty closed below its open.

### Sliced by weekday and nakshatra lord (`scripts/slice_ayanamsa.py`)

**By weekday** — n≈247 per bucket:

| Weekday | KP hit | Lahiri hit | days they disagree | actual up-rate |
|---|---|---|---|---|
| Monday | 45.8% (n=214) | 45.3% (n=214) | 3 | 53.4% |
| Tuesday | 48.4% (n=225) | 47.1% (n=225) | 5 | 44.8% |
| Wednesday | 43.7% (n=215) | 44.1% (n=213) | 0 | 50.2% |
| Thursday | 51.1% (n=221) | 51.8% (n=220) | 2 | 43.7% |
| Friday | 51.9% (n=214) | 52.8% (n=214) | 2 | 49.8% |

**By nakshatra lord** (Moon's star lord at sunrise, bucketed by the KP
lord) — n≈137 per bucket:

| Lord | KP hit | Lahiri hit | disagree | up-rate |
|---|---|---|---|---|
| Sun | 53.7% (n=121) | 54.5% (n=121) | 3 | 58.1% |
| Moon | 44.2% (n=120) | 43.3% (n=120) | 1 | 47.5% |
| Mars | 57.0% (n=114) | 57.0% (n=114) | 2 | 43.8% |
| Mercury | 46.8% (n=126) | 47.2% (n=123) | 0 | 51.4% |
| Jupiter | 45.9% (n=122) | 46.7% (n=122) | 1 | 42.9% |
| Venus | 48.7% (n=117) | 48.7% (n=117) | 2 | 45.5% |
| Saturn | 47.7% (n=128) | 46.9% (n=128) | 1 | 45.1% |
| Rahu | 42.4% (n=118) | 42.4% (n=118) | 2 | 58.2% |
| Ketu | 48.4% (n=124) | 48.4% (n=124) | 0 | 42.9% |

**These slices cannot answer the ayanamsa question, and the disagree
column is why.** All 12 discordant days spread across 5 weekdays and 9
lords leaves 0–5 per bucket — Wednesday, Mercury and Ketu contain *zero*
days on which the two methods differ at all, so their rows compare a
method against itself. The largest KP-vs-Lahiri gap anywhere is 1.3pp
(Tuesday), resting on 5 days. What these tables actually measure is the
rule stack, not the zodiac: they reproduce the weekday and star-lord
slices earlier in this document, which is a useful check that the harness
is sound (the Lahiri weekday column matches the published figures to
within rounding) and nothing more.

The 12 discordant days in full, with the winner on each:

| Date | Weekday | KP lord | Lahiri lord | KP | Lahiri | ret% | Winner |
|---|---|---|---|---|---|---|---|
| 2021-09-27 | Monday | Moon | Moon | −0.01 | +0.17 | −0.43 | KP |
| 2021-10-07 | Thursday | Mars | Mars | +0.08 | −0.25 | −0.11 | Lahiri |
| 2023-02-21 | Tuesday | Rahu | Rahu | +0.28 | −0.56 | −0.44 | Lahiri |
| 2023-03-14 | Tuesday | Saturn | Saturn | −0.34 | +0.78 | −0.68 | KP |
| 2024-01-30 | Tuesday | Sun | Sun | −0.16 | +0.06 | −1.17 | KP |
| 2024-12-27 | Friday | Jupiter | Jupiter | −0.16 | +0.28 | +0.05 | Lahiri |
| 2025-02-06 | Thursday | Sun | Sun | +0.12 | −0.58 | −0.67 | Lahiri |
| 2025-04-01 | Tuesday | Venus | Venus | −0.34 | +0.13 | −0.75 | KP |
| 2025-07-11 | Friday | **Sun** | **Venus** | +0.28 | −0.16 | −0.42 | Lahiri |
| 2025-07-22 | Tuesday | Mars | Mars | −0.06 | +0.50 | −0.42 | KP |
| 2025-10-13 | Monday | Rahu | Rahu | +0.16 | −0.22 | +0.20 | KP |
| 2025-11-24 | Monday | Venus | Venus | +0.00 | −0.14 | −0.62 | Lahiri |

6–6, exact two-sided *p* = 1.000. Several are near-zero scores on both
sides (−0.01 vs +0.17; +0.00 vs −0.14) — days where the "disagreement"
is a sign flip on a number that rounds to nothing.

**The slice variable is itself ayanamsa-dependent.** The Moon's star lord
differs between the two zodiacs on 9 days (0.7%), so a day can fall in
different buckets depending on which method is asked. 2025-07-11 is both:
KP calls it a Sun-lord day, Lahiri a Venus-lord day, *and* they predict
opposite directions. Bucketing follows the KP lord throughout, since that
is the production method.

**Multiple testing.** These 14 comparisons join the ~30 already in this
document. At n≈120–225 the 95% CI is ±7–9pp per cell, and the spread seen
here (42.4%–57.0%) is the expected range under pure noise for 14 draws.
Mars 57.0% and Rahu 42.4% are identical under both ayanamsas, which
confirms they are properties of the rule stack rather than the zodiac —
and they were already inside the noise band in the star-lord slice above.

### Sliced by thithi family and horai (`scripts/slice_ayanamsa.py`)

**These two buckets are ayanamsa-invariant, unlike the nakshatra lord**,
and for a reason worth recording. Thithi and karanam derive from the
Moon−Sun *elongation*, so the ayanamsa cancels exactly in the
subtraction — measured over 366 days, the thithi number, thithi family
and karanam differ on **0** days. Yogam is a *sum* of the two longitudes,
so the offset doubles instead of cancelling: it differs on 6/366 (1.64%),
and that alone accounts for the 2 panchang-tally disagreements reported
above. Horai is invariant by construction — `horai_timeline` takes no
ayanamsa argument, depending only on sunrise/sunset and the weekday.

So both tables below compare the two zodiacs inside *identical* buckets.

**By thithi family** (n≈247 each):

| Family | KP hit | Lahiri hit | disagree | up-rate |
|---|---|---|---|---|
| Nanda | 47.8% (n=226) | 48.9% (n=225) | 4 | 48.6% |
| Bhadra | 48.1% (n=216) | 47.2% (n=216) | 4 | 50.4% |
| Jaya | 46.5% (n=230) | 46.5% (n=230) | 0 | 44.4% |
| Rikta | 50.7% (n=209) | 50.5% (n=208) | 4 | 46.1% |
| Purna | 48.3% (n=209) | 48.6% (n=208) | 0 | 52.5% |

Jaya and Purna contain no discordant days at all. Largest gap 1.1pp
(Nanda), on 4 days.

**By horai** — 4,334 hourly bars over 724 sessions, each bar scored
against the chain segment covering it. This is the fairest test available
to the two ayanamsas: the daily test collapses a session to one number,
so they can only differ when the whole day flips sign, whereas
segment-level scoring gives them many more chances to diverge. It also
tests intraday *shape*, which RESULTS.md notes elsewhere is otherwise
untested.

| Horai | bars | KP hit | Lahiri hit | disagree | up-rate |
|---|---|---|---|---|---|
| Sun | 578 | 46.7% (n=452) | 46.0% (n=450) | 3 | 49.7% |
| Moon | 579 | 47.9% (n=455) | 47.7% (n=453) | 1 | 50.8% |
| Mars | 722 | 48.9% (n=571) | 48.3% (n=571) | 4 | 50.1% |
| Mercury | 722 | 49.6% (n=568) | 49.8% (n=566) | 1 | 51.1% |
| Jupiter | 579 | 49.8% (n=462) | 49.8% (n=460) | 3 | 50.8% |
| Venus | 575 | 51.9% (n=445) | 51.8% (n=444) | 3 | 51.0% |
| Saturn | 579 | 49.7% (n=463) | 49.7% (n=459) | 1 | 48.9% |

Overall: **KP 49.2%** (1681/3416) vs **Lahiri 49.0%** (1668/3403). Even
at segment granularity the two agree on 99.6% of bars — they disagree on
16 of 4,334.

**The one asymmetry in the whole exercise, and why it is not one.** On
those 16 discordant bars KP is right 11 times to Lahiri's 5 (*p* = 0.210).
That is the largest gap anywhere in this comparison, and it does not
survive inspection:

- **The bars are not independent.** They fall on only **8 distinct
  sessions**. When a day's segment differs, consecutive bars inherit the
  same disagreement *and* largely the same market move, so 16 is not 16
  votes. One vote per session gives KP 6, Lahiri 2 — *p* = 0.289.
- **The moves are noise.** 10 of the 16 bars moved less than 0.1%. The
  "wins" are sign calls on essentially flat bars.
- **It is one of ~46 comparisons** in this document. A *p* = 0.21 among
  46 tests is entirely unremarkable; the expected number of sub-0.05
  results under the null alone is ~2, and this is not even one of them.

**Bottom line, unchanged.** Four cuts — weekday, nakshatra lord, thithi
family, horai — and 1,235 daily plus 4,334 hourly observations produce no
separation between the two ayanamsas. The daily split is 6–6, the
session-level intraday split 6–2 at *p* = 0.29. KP remains the right
choice for the prediction path on source-fidelity grounds alone.

## Location: the backtest is Chennai, the app now defaults to Mumbai

Every figure in this document was computed at **Chennai** (13.0827,
80.2707). The app's default cast location changed to **Mumbai** (19.076,
72.8777) on 2026-08-11, on the reasoning that the NSE is in Mumbai, so a
market chart belongs at the exchange.

Measured divergence over the same 1,235 days:

| | |
|---|---|
| Mumbai sunrise later than Chennai | **29.3 min** (range 18–41) |
| Chain (X / Y / first / second) differs | **25 days (2.0%)** |
| Day-score direction flips | **21 days (1.7%)** |

So the app's predictions now differ from the backtested configuration on
roughly one day in fifty. That is far smaller than the sunrise-vs-09:15
cast shift measured earlier (7–9%), because this is a ~30 minute move
rather than a ~3.5 hour one.

The backtest scripts deliberately still use Chennai, so re-running them
reproduces the numbers above rather than silently drifting. Nothing in the
conclusions turns on it: at a 48.3% hit rate against a 48.3% base rate, a
2% reshuffle cannot manufacture an edge. If the study is ever redone, it
should move to Mumbai for consistency with the app.

## Re-run at Mumbai (`scripts/backtest_nifty.py 5 mumbai`)

Run 2026-08-11 after the app's default cast location moved to Mumbai.
1,235 trading days, 2021-08-11 → 2026-08-11. Per-day data in
`nifty_backtest_mumbai.csv`; the Chennai run is untouched in
`nifty_backtest.csv`.

| Test | Chennai | Mumbai |
|---|---|---|
| Baseline: share of up days | 48.3% | 48.3% |
| **Engine direction, all directional days** | **48.3%** (n=1085) | **48.2%** (n=1086) |
| Strong-signal days (\|score\| ≥ 0.5) | 46.4% (n=468) | 46.6% (n=461) |
| Days with a real move (\|ret\| ≥ 0.25%) | 48.7% (n=725) | 49.0% (n=729) |
| Thithi positive → up | 48.7% | 48.6% |
| Thithi negative → down | 51.9% | 52.1% |
| Yogam positive → up | 46.8% | 46.8% |
| Yogam negative → down | 49.3% | 49.6% |
| Yogam **very** negative → down | 49.6% | 49.6% |
| Panchang tally ≥ +0.5 → up | 47.8% | 47.8% |
| Panchang tally ≤ −0.5 → down | 48.2% | 48.5% |
| **Chain AND panchang agree (confluence)** | **45.5%** | **45.3%** |

Per-year (Mumbai): 40.7 / 52.9 / 45.0 / 49.8 / 49.1 / 45.6 (2021→2026),
against Chennai's 41.4 / 54.3 / 45.2 / 49.8 / 48.4 / 44.6.

**Nothing moves.** Every cell lands within ~1pp of the Chennai run, well
inside the ±3pp confidence interval at this sample size — as expected,
since the two configurations differ on only 2.0% of days. The engine sits
at 48.2% against a 48.3% base rate, so it is still a coin flip that loses
to "always predict down" (51.7%), and confluence is still the single worst
cell in the study at 45.3%.

That the result is location-invariant is mildly useful in itself: the
finding is not an artifact of casting at Chennai, and moving the app to
the exchange's own city does not rescue it. The method still does not
forecast Nifty.

## BankNifty (`scripts/backtest_nifty.py 5 mumbai banknifty`)

Run 2026-08-11 at Mumbai. 1,234 trading days, 2021-08-11 → 2026-08-11.
Per-day data in `banknifty_backtest_mumbai.csv`. Worth testing separately
because several taught rules are BankNifty-specific (the Thursday
Sun + Karthigai rule, the "~100 BN minimum" magnitudes, the Nifty/BankNifty
divergence rule).

| Test | Nifty (Mumbai) | BankNifty (Mumbai) |
|---|---|---|
| Baseline: share of up days | 48.3% | 48.5% |
| **Engine direction, all directional days** | 48.2% (n=1086) | **51.0%** (n=1085) |
| Strong-signal days (\|score\| ≥ 0.5) | 46.6% | 50.1% |
| Days with a real move (\|ret\| ≥ 0.25%) | 49.0% | 49.4% |
| Thithi positive → up | 48.6% | 48.2% |
| Thithi negative → down | 52.1% | 51.0% |
| Yogam positive → up | 46.8% | 46.1% |
| Yogam negative → down | 49.6% | 46.3% |
| Yogam **very** negative → down | 49.6% | 52.6% |
| Panchang tally ≥ +0.5 → up | 47.8% | 48.1% |
| Panchang tally ≤ −0.5 → down | 48.5% | 48.5% |
| **Chain AND panchang agree (confluence)** | 45.3% | 48.5% |

Per-year: 41.9 / 52.0 / 51.4 / 52.5 / 51.6 / 50.9 (2021→2026) — five of
six years above 50%, and the first above-baseline headline in this whole
document.

**It is not a signal.** Three checks, all of which it fails:

1. **It loses to a constant.** BankNifty closed below its open on 51.5% of
   days, so "always predict down" scores **51.5%** — better than the
   engine's 51.0%. Same failure mode as Nifty, just at a different level.
2. **It is inside noise.** The engine calls UP on 52.3% of directional
   days. If its calls were independent of outcomes it would score 49.9% by
   arithmetic alone; it scores 51.0%, which is **z = +0.70**. Nothing at
   |z| < 1.96 is distinguishable from chance, and this is one cell among
   the ~60 now in this document.
3. **The edge is one-sided.** When it says DOWN it is 53.1% correct; when
   it says UP, 49.0%. A real directional signal helps in both directions.
   This asymmetry is just a mildly bearish predictor meeting a mildly
   falling market — the same coin landing tails slightly more often.

So BankNifty behaves exactly like Nifty once the baseline is set
correctly. The apparent improvement is the base rate moving, not the
method working. Both indices: no forecasting ability.
