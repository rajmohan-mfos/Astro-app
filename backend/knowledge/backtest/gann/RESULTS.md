# Gann cosmogram catalogue — backtest 2011-01-01 → 2026-08-28

Method: every exact event of every rule in `app/gann/calendar.py`
(tropical, `aspects.crossings`), mapped to the previous session when
the aspect day is closed (the course convention; the next-session
mapping is in results.json). Scored against the same statistic on
every other day. p = exact binomial vs base, or a random-subset
permutation for mean returns. Nothing was fitted.

## NIFTY — 3848 sessions; base: 5d mean +21 bp, 5d up 56.1%, 5d reverses 3d trend 49.2%, flip within ±2 days 88.4%, candle follow-through 57.5%

| rule (catalogue verdict) | events | +5d bp (p) | 5d up | reversal | flip ±2d | called direction | candle follow-through | months |
|---|---|---|---|---|---|---|---|---|
| Venus–Jupiter quadrature (paper-trade, reversal) | 31 (10 retro-excluded) | +36 (0.71) | 52% | 17/31 = 55% (p 0.59) | 90% | — (reversal rule) | 19/28 = 68% (p 0.34) | 1:2 2:4 3:3 4:1 5:2 6:3 7:1 8:5 9:2 10:2 11:4 12:2 |
| Mercury–Saturn conjunction (paper-trade, reversal) | 19 | +82 (0.24) | 74% | 11/19 = 58% (p 0.50) | 95% | — (reversal rule) | 11/18 = 61% (p 0.82) | 1:4 2:2 3:2 4:1 10:4 11:5 12:1 |
| Mars–Jupiter semisquare (lean, bullish) | 17 | +126 (0.07) | 71% | 8/17 = 47% (p 1.00) | 76% | 12/17 = 71% vs 56% (p 0.33) | 10/16 = 62% (p 0.80) | 1:2 2:1 3:2 4:1 5:3 7:3 8:1 9:1 10:1 11:1 12:1 |
| Mars–Neptune conjunction (lean, bearish) | 9 | +37 (0.83) | 56% | 6/9 = 67% (p 0.34) | 67% | 4/9 = 44% vs 44% (p 1.00) | 6/9 = 67% (p 0.74) | 1:2 2:2 4:2 5:1 6:1 12:1 |
| Venus–Saturn quadrature (null, reversal) | 35 | -40 (0.12) | 51% | 14/35 = 40% (p 0.31) | 91% | — (reversal rule) | 18/32 = 56% (p 1.00) | 1:3 2:2 3:4 4:4 5:2 6:2 7:3 8:5 9:3 10:3 11:2 12:2 |
| Jupiter–Uranus conjunction/opposition (rare, reversal) | 5 | -12 (0.74) | 80% | 3/5 = 60% (p 0.68) | 100% | — (reversal rule) | 5/5 = 100% (p 0.08) | 1:1 3:1 4:1 9:1 12:1 |
| Venus–natalVenus (null, reversal) | 100 (2 retro-excluded) | +13 (0.75) | 60% | 51/99 = 52% (p 0.69) | 91% | — (reversal rule) | 46/89 = 52% (p 0.28) | 1:10 2:8 3:14 4:8 5:6 6:4 7:6 8:14 9:14 10:10 11:4 12:2 |
| Mercury–Mars radix–transit conjunction (null, reversal) | 29 | -27 (0.26) | 45% | 9/29 = 31% (p 0.06) | 90% | — (reversal rule) | 13/26 = 50% (p 0.44) | 2:1 3:5 4:11 5:8 6:2 7:1 8:1 |
| Jupiter–natalJupiter opposition (rare, bullish) | 6 | +14 (0.93) | 67% | 2/6 = 33% (p 0.69) | 67% | 4/6 = 67% vs 56% (p 0.70) | 3/5 = 60% (p 1.00) | 1:1 4:1 5:1 8:1 9:1 12:1 |
| Venus station (null, reversal) | 18 | +148 (0.02) | 72% | 9/18 = 50% (p 1.00) | 94% | — (reversal rule) | 12/17 = 71% (p 0.33) | 1:1 2:1 3:2 4:2 5:2 6:2 7:2 9:2 10:1 11:1 12:2 |
| Sun–Uranus–Neptune triangle (calendar-trap, reversal) | 3 | -182 (0.11) | 33% | 1/3 = 33% (p 1.00) | 100% | — (reversal rule) | 2/3 = 67% (p 1.00) | 10:3 |

Catalogue evidence strings, for comparison:

- **Venus–Jupiter quadrature** — 54% win rate vs 43% base on 26 decided trades (14W/12L/10 undecided), +35 pts expectancy — the best rule in the catalogue, still not statistically significant. Claimed: >80%.
  dates: 2011-02-07, 2011-08-05, 2011-12-21, 2012-10-17, 2013-03-04, 2013-08-28, 2014-05-18, 2014-11-10, 2015-03-28, 2016-01-18, 2016-06-05, 2016-11-25, 2017-08-17, 2018-02-04, 2018-06-26, 2019-04-16, 2019-09-03, 2020-02-24, 2020-11-16, 2021-05-08, 2021-10-01, 2022-07-25, 2022-12-09, 2023-06-11, 2023-08-22, 2023-09-17, 2024-02-25, 2024-08-19, 2025-01-15, 2025-11-03, 2026-03-19
- **Mercury–Saturn conjunction** — Trend flipped 16/23 (70%) vs 49% base, p=0.038 — the strongest number in the project, but ~25 rules were tested so one such false positive is expected, and his own forward call (25 Feb 2025) failed.
  dates: 2011-10-07, 2012-10-05, 2013-10-09, 2013-10-30, 2013-11-26, 2014-11-26, 2015-11-25, 2016-11-24, 2017-11-28, 2017-12-06, 2018-01-13, 2019-01-13, 2020-01-12, 2021-01-10, 2022-03-03, 2023-03-02, 2024-02-28, 2025-02-25, 2026-04-20
- **Mars–Jupiter semisquare** — +1.4% Nifty / +1.9% BankNifty 5-day forward, p≈0.1 — directionally consistent on both indices, unproven.
  dates: 2011-02-08, 2011-07-24, 2013-04-21, 2013-10-24, 2015-07-06, 2016-01-18, 2017-09-23, 2018-03-31, 2019-12-17, 2020-05-31, 2022-03-06, 2022-08-09, 2024-05-18, 2024-11-18, 2025-01-14, 2025-05-04, 2026-07-29
- **Mars–Neptune conjunction** — −2.45% avg 5-day on Nifty at p=0.023 — but n=9, and one of 36 tests where two false positives are expected by chance.
  dates: 2011-02-21, 2013-02-05, 2015-01-20, 2017-01-01, 2018-12-07, 2020-06-13, 2022-05-18, 2024-04-29, 2026-04-13
- **Venus–Saturn quadrature** — 57% vs a 55% base across all 40 events since 2007, identical median excursions — and a ≥150-pt counter-move within 2 days happens on 39% of ALL days. Performs at the noise floor.
  dates: 2011-02-19, 2011-07-13, 2011-12-18, 2012-09-03, 2013-02-11, 2013-07-02, 2014-03-30, 2014-08-27, 2015-01-30, 2015-07-14, 2015-08-05, 2015-10-11, 2016-03-26, 2016-08-13, 2017-01-28, 2017-04-09, 2017-04-21, 2017-10-08, 2018-03-13, 2018-08-10, 2019-05-07, 2019-09-26, 2020-03-04, 2020-11-19, 2021-04-25, 2021-09-17, 2022-06-19, 2022-11-07, 2023-04-15, 2024-01-01, 2024-06-08, 2024-10-28, 2025-08-01, 2025-12-21, 2026-05-29
- **Jupiter–Uranus conjunction/opposition** — 7 exact passes since 2007, 1 produced the claimed reversal. Retrogradation makes each 'rare event' a triple pass over ~9 months — only the pass followed by a fall was shown.
  dates: 2011-01-04, 2016-12-27, 2017-03-03, 2017-09-28, 2024-04-21
- **Venus–natalVenus** — The flagship birth-chart rule: sextile scored 10/15 (67%) vs a 64% base — not the claimed 85%; quadrature and trine averaged −0.1% to +0.9%, all p>0.37. No edge at any of the three angles.
  dates: 2011-03-16, 2011-04-10, 2011-05-04, 2011-08-11, 2011-09-04, 2011-09-28, 2012-01-03, 2012-01-27, 2012-02-22, 2012-09-21, 2012-10-17, 2012-11-11, 2013-02-15, 2013-03-11, 2013-04-04, 2013-07-11, 2013-08-05, 2013-08-30, 2014-03-23, 2014-04-21, 2014-05-17, 2014-08-25, 2014-09-19, 2014-10-13, 2015-01-16, 2015-02-09, 2015-03-06, 2015-06-24, 2015-08-28, 2015-09-16, 2015-10-26, 2015-11-23, 2016-03-01, 2016-03-25, 2016-04-19, 2016-07-25, 2016-08-19, 2016-09-12, 2016-12-22, 2017-01-19 …
- **Mercury–Mars radix–transit conjunction** — Reversal at the exact date 5/13 (38%) — below the 49% random-day rate. With his ±2-day deflection it reads 85%… which is exactly the base rate of any random day. The window manufactures the accuracy.
  dates: 2011-03-25, 2011-04-06, 2011-05-09, 2011-06-10, 2012-05-04, 2013-04-27, 2013-05-21, 2014-04-19, 2015-04-11, 2015-05-01, 2016-04-02, 2017-03-26, 2017-04-10, 2018-05-08, 2019-03-20, 2019-05-02, 2020-04-24, 2021-02-19, 2021-04-15, 2022-04-07, 2022-08-08, 2023-03-30, 2024-03-24, 2024-04-12, 2024-05-08, 2024-07-10, 2025-05-05, 2026-04-29, 2026-06-18
- **Jupiter–natalJupiter opposition** — Once per ~11.9-year orbit, as a triple pass. The Aug 2025 pass ran +4.4% at three months (his first graded forward hit); the Feb 2026 pass of the same triple was followed by −5%. Too rare to establish.
  dates: 2013-09-23, 2013-12-22, 2014-05-16, 2025-08-29, 2026-01-31, 2026-04-19
- **Venus station** — All 22 stations 2007–2026: flip at the date 55% vs 49% base; within ±2 days 95% vs an 85% base. Mercury's 118 stations flip at the same 55% — the slow-planet accuracy claim isn't in the data.
  dates: 2012-05-16, 2012-06-28, 2013-12-22, 2014-02-01, 2015-07-26, 2015-09-07, 2017-03-05, 2017-04-16, 2018-10-06, 2018-11-17, 2020-05-14, 2020-06-26, 2021-12-20, 2022-01-30, 2023-07-23, 2023-09-04, 2025-03-02, 2025-04-13
- **Sun–Uranus–Neptune triangle** — Uranus–Neptune sit within 5° of sextile on 11% of all days — the Sun supplies all the timing, so the 'rare pattern' recurs every mid-to-late October. 1 of 3 windows produced a flip.
  dates: 2023-10-17, 2024-10-18, 2025-10-21

## BANKNIFTY — 3863 sessions; base: 5d mean +26 bp, 5d up 55.0%, 5d reverses 3d trend 50.2%, flip within ±2 days 89.9%, candle follow-through 54.9%

| rule (catalogue verdict) | events | +5d bp (p) | 5d up | reversal | flip ±2d | called direction | candle follow-through | months |
|---|---|---|---|---|---|---|---|---|
| Venus–Jupiter quadrature (paper-trade, reversal) | 31 (10 retro-excluded) | +51 (0.66) | 61% | 17/31 = 55% (p 0.72) | 90% | — (reversal rule) | 15/27 = 56% (p 1.00) | 1:2 2:4 3:3 4:1 5:2 6:3 7:1 8:5 9:2 10:2 11:4 12:2 |
| Mercury–Saturn conjunction (paper-trade, reversal) | 19 | +87 (0.40) | 63% | 12/19 = 63% (p 0.36) | 100% | — (reversal rule) | 7/17 = 41% (p 0.33) | 1:4 2:2 3:2 4:1 10:4 11:5 12:1 |
| Mars–Jupiter semisquare (lean, bullish) | 17 | +203 (0.03) | 76% | 4/17 = 24% (p 0.03) | 88% | 13/17 = 76% vs 55% (p 0.09) | 10/16 = 62% (p 0.62) | 1:2 2:1 3:2 4:1 5:3 7:3 8:1 9:1 10:1 11:1 12:1 |
| Mars–Neptune conjunction (lean, bearish) | 9 | +41 (0.89) | 67% | 5/9 = 56% (p 1.00) | 89% | 3/9 = 33% vs 45% (p 0.53) | 3/7 = 43% (p 0.71) | 1:2 2:2 4:2 5:1 6:1 12:1 |
| Venus–Saturn quadrature (null, reversal) | 35 | -50 (0.16) | 57% | 18/35 = 51% (p 1.00) | 91% | — (reversal rule) | 20/35 = 57% (p 0.87) | 1:3 2:2 3:4 4:4 5:2 6:2 7:3 8:5 9:3 10:3 11:2 12:2 |
| Jupiter–Uranus conjunction/opposition (rare, reversal) | 5 | -45 (0.61) | 80% | 4/5 = 80% (p 0.38) | 100% | — (reversal rule) | 5/5 = 100% (p 0.07) | 1:1 3:1 4:1 9:1 12:1 |
| Venus–natalVenus (null, reversal) | 100 (2 retro-excluded) | +22 (0.89) | 61% | 51/99 = 52% (p 0.84) | 96% | — (reversal rule) | 47/88 = 53% (p 0.83) | 1:10 2:8 3:14 4:8 5:6 6:4 7:6 8:14 9:14 10:10 11:4 12:2 |
| Mercury–Mars radix–transit conjunction (null, reversal) | 29 | -32 (0.34) | 52% | 10/29 = 34% (p 0.10) | 93% | — (reversal rule) | 15/26 = 58% (p 0.85) | 2:1 3:5 4:11 5:8 6:2 7:1 8:1 |
| Jupiter–natalJupiter opposition (rare, bullish) | 6 | -22 (0.70) | 67% | 2/6 = 33% (p 0.45) | 100% | 4/6 = 67% vs 55% (p 0.70) | 2/4 = 50% (p 1.00) | 1:1 4:1 5:1 8:1 9:1 12:1 |
| Venus station (null, reversal) | 18 | +164 (0.07) | 83% | 12/18 = 67% (p 0.24) | 100% | — (reversal rule) | 12/17 = 71% (p 0.23) | 1:1 2:1 3:2 4:2 5:2 6:2 7:2 9:2 10:1 11:1 12:2 |
| Sun–Uranus–Neptune triangle (calendar-trap, reversal) | 3 | -180 (0.23) | 33% | 1/3 = 33% (p 0.62) | 67% | — (reversal rule) | 2/3 = 67% (p 1.00) | 10:3 |

Catalogue evidence strings, for comparison:

- **Venus–Jupiter quadrature** — 54% win rate vs 43% base on 26 decided trades (14W/12L/10 undecided), +35 pts expectancy — the best rule in the catalogue, still not statistically significant. Claimed: >80%.
  dates: 2011-02-07, 2011-08-05, 2011-12-21, 2012-10-17, 2013-03-04, 2013-08-28, 2014-05-18, 2014-11-10, 2015-03-28, 2016-01-18, 2016-06-05, 2016-11-25, 2017-08-17, 2018-02-04, 2018-06-26, 2019-04-16, 2019-09-03, 2020-02-24, 2020-11-16, 2021-05-08, 2021-10-01, 2022-07-25, 2022-12-09, 2023-06-11, 2023-08-22, 2023-09-17, 2024-02-25, 2024-08-19, 2025-01-15, 2025-11-03, 2026-03-19
- **Mercury–Saturn conjunction** — Trend flipped 16/23 (70%) vs 49% base, p=0.038 — the strongest number in the project, but ~25 rules were tested so one such false positive is expected, and his own forward call (25 Feb 2025) failed.
  dates: 2011-10-07, 2012-10-05, 2013-10-09, 2013-10-30, 2013-11-26, 2014-11-26, 2015-11-25, 2016-11-24, 2017-11-28, 2017-12-06, 2018-01-13, 2019-01-13, 2020-01-12, 2021-01-10, 2022-03-03, 2023-03-02, 2024-02-28, 2025-02-25, 2026-04-20
- **Mars–Jupiter semisquare** — +1.4% Nifty / +1.9% BankNifty 5-day forward, p≈0.1 — directionally consistent on both indices, unproven.
  dates: 2011-02-08, 2011-07-24, 2013-04-21, 2013-10-24, 2015-07-06, 2016-01-18, 2017-09-23, 2018-03-31, 2019-12-17, 2020-05-31, 2022-03-06, 2022-08-09, 2024-05-18, 2024-11-18, 2025-01-14, 2025-05-04, 2026-07-29
- **Mars–Neptune conjunction** — −2.45% avg 5-day on Nifty at p=0.023 — but n=9, and one of 36 tests where two false positives are expected by chance.
  dates: 2011-02-21, 2013-02-05, 2015-01-20, 2017-01-01, 2018-12-07, 2020-06-13, 2022-05-18, 2024-04-29, 2026-04-13
- **Venus–Saturn quadrature** — 57% vs a 55% base across all 40 events since 2007, identical median excursions — and a ≥150-pt counter-move within 2 days happens on 39% of ALL days. Performs at the noise floor.
  dates: 2011-02-19, 2011-07-13, 2011-12-18, 2012-09-03, 2013-02-11, 2013-07-02, 2014-03-30, 2014-08-27, 2015-01-30, 2015-07-14, 2015-08-05, 2015-10-11, 2016-03-26, 2016-08-13, 2017-01-28, 2017-04-09, 2017-04-21, 2017-10-08, 2018-03-13, 2018-08-10, 2019-05-07, 2019-09-26, 2020-03-04, 2020-11-19, 2021-04-25, 2021-09-17, 2022-06-19, 2022-11-07, 2023-04-15, 2024-01-01, 2024-06-08, 2024-10-28, 2025-08-01, 2025-12-21, 2026-05-29
- **Jupiter–Uranus conjunction/opposition** — 7 exact passes since 2007, 1 produced the claimed reversal. Retrogradation makes each 'rare event' a triple pass over ~9 months — only the pass followed by a fall was shown.
  dates: 2011-01-04, 2016-12-27, 2017-03-03, 2017-09-28, 2024-04-21
- **Venus–natalVenus** — The flagship birth-chart rule: sextile scored 10/15 (67%) vs a 64% base — not the claimed 85%; quadrature and trine averaged −0.1% to +0.9%, all p>0.37. No edge at any of the three angles.
  dates: 2011-03-16, 2011-04-10, 2011-05-04, 2011-08-11, 2011-09-04, 2011-09-28, 2012-01-03, 2012-01-27, 2012-02-22, 2012-09-21, 2012-10-17, 2012-11-11, 2013-02-15, 2013-03-11, 2013-04-04, 2013-07-11, 2013-08-05, 2013-08-30, 2014-03-23, 2014-04-21, 2014-05-17, 2014-08-25, 2014-09-19, 2014-10-13, 2015-01-16, 2015-02-09, 2015-03-06, 2015-06-24, 2015-08-28, 2015-09-16, 2015-10-26, 2015-11-23, 2016-03-01, 2016-03-25, 2016-04-19, 2016-07-25, 2016-08-19, 2016-09-12, 2016-12-22, 2017-01-19 …
- **Mercury–Mars radix–transit conjunction** — Reversal at the exact date 5/13 (38%) — below the 49% random-day rate. With his ±2-day deflection it reads 85%… which is exactly the base rate of any random day. The window manufactures the accuracy.
  dates: 2011-03-25, 2011-04-06, 2011-05-09, 2011-06-10, 2012-05-04, 2013-04-27, 2013-05-21, 2014-04-19, 2015-04-11, 2015-05-01, 2016-04-02, 2017-03-26, 2017-04-10, 2018-05-08, 2019-03-20, 2019-05-02, 2020-04-24, 2021-02-19, 2021-04-15, 2022-04-07, 2022-08-08, 2023-03-30, 2024-03-24, 2024-04-12, 2024-05-08, 2024-07-10, 2025-05-05, 2026-04-29, 2026-06-18
- **Jupiter–natalJupiter opposition** — Once per ~11.9-year orbit, as a triple pass. The Aug 2025 pass ran +4.4% at three months (his first graded forward hit); the Feb 2026 pass of the same triple was followed by −5%. Too rare to establish.
  dates: 2013-09-23, 2013-12-22, 2014-05-16, 2025-08-29, 2026-01-31, 2026-04-19
- **Venus station** — All 22 stations 2007–2026: flip at the date 55% vs 49% base; within ±2 days 95% vs an 85% base. Mercury's 118 stations flip at the same 55% — the slow-planet accuracy claim isn't in the data.
  dates: 2012-05-16, 2012-06-28, 2013-12-22, 2014-02-01, 2015-07-26, 2015-09-07, 2017-03-05, 2017-04-16, 2018-10-06, 2018-11-17, 2020-05-14, 2020-06-26, 2021-12-20, 2022-01-30, 2023-07-23, 2023-09-04, 2025-03-02, 2025-04-13
- **Sun–Uranus–Neptune triangle** — Uranus–Neptune sit within 5° of sextile on 11% of all days — the Sun supplies all the timing, so the 'rare pattern' recurs every mid-to-late October. 1 of 3 windows produced a flip.
  dates: 2023-10-17, 2024-10-18, 2025-10-21
