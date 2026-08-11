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
