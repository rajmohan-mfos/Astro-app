# Which method to actually use — the four-way comparison

Four astrological methods live in this app, and all four have now been
backtested on the same instrument with the same discipline: score the call
against the realised move, compare with the trivial benchmark on the *same
days*, and correct for how many rules were tried.

| | **Options Mersal** (GRAHA MARKETS course — Prediction tab) | **Gann cosmogram** (Gann tab) | **Saptarsh Insight** (Saptarsh tab) | **Vikas dates** (Vikas tab) |
|---|---|---|---|---|
| What it predicts | Nifty session direction, from the sunrise chain (X/X1/Y/Y1), panchang tally, horai | Trend reversals / swings on dated planetary aspects and stations | Nifty session direction; gold & silver daily direction; intraday windows | **Dates, not direction**: planetary events → the date candle's high/low as breakout levels; a day-lord direction rule; Mars-vs-Saturn metal-sector rules |
| Test window | Nifty 2011–2026 (15 yr, 3,830 bars), walk-forward; BankNifty as a second index | Nifty and Bank Nifty 2011–2026 (3,848 / 3,863 sessions), every exact event of the 11 catalogued rules (`scripts/backtest_gann.py`) | Nifty, COMEX gold & silver 2016–2026 (≈2,650 days each) | Nifty 2011–2026 (3,848 bars); Bank Nifty; Nifty Metal; COMEX gold & silver 2016–2026 |
| Benchmark it must beat | Always-down on its own traded days (53.0%) | The same statistic on every other day: 5-day reversal of the 3-day trend 49.2%, flip within ±2 days 88.4%, 5-day up 56.1%, candle follow-through 57.5% | Always-majority-side on its own traded days (Nifty 52.3%, gold 54.6%, silver 52.5%) | The same statistic on every other day: candle-breakout follow-through 57.5%, week-holds-the-low 31%, majority side 54.6% |
| Headline result | Engine as shipped **48.9%** (−4.4 pp, z = −4.2 — worse than always-down); day-score confluence 45.8%; nested walk-forward **53.95%** (z = +0.52) | Mercury–Saturn conjunction reverses the trend **11/19 = 58% vs 49%** (p 0.50 — the archive's 70% does not replicate); Venus–Jupiter square 17/31 = 55% (p 0.59); "flip within ±2 days" 90–100% for every rule, against an 88% base; best row Mars–Jupiter semisquare +126 bp Nifty (p 0.07) / +203 bp Bank Nifty (p 0.03) on 17 events — one of 22 tests | Nifty **51.6% vs 52.3%** (n = 1,959, perm-p 0.11); gold **48.8% vs 54.6%**; silver **49.7% vs 52.5%** | Day-lord rule **49.8%** (n = 2,808); carry-over 47.3% (n = 423); Saturn→Mercury half-retrace 70.6% vs 68.8% for any down day; his date candles follow through **52–60% vs 57.5%** for any candle, across 25 date families |
| Rules that survive multiple-comparison correction | **0** of 6,912 variants (best-of search p = 0.045, but the shuffled null's own maximum beats the real data) | **0** of 11 on either index (best uncorrected p 0.03 among 22 rule × index tests) | **0** of 32 rules on any instrument | **0** of ~45 daily / candle tests; **1** transit rule — Mars vs Saturn's sign — at p ≈ 0.01 on n = 11 spans |
| Second-instrument check | BankNifty: **47.1%** (z = −2.85) — the Nifty "winner" vanishes | Bank Nifty agrees: Mercury–Saturn 12/19 = 63% (p 0.36), Venus station +164 bp (p 0.07) after +148 bp (p 0.02) on Nifty — chance-sized both times | Gold and silver both below benchmark; "observed" calls no better than extrapolated | Mars-vs-Saturn repeats on Nifty Metal (−4.0% / +8.2%) and in both halves of the window; Sun→Uttarashadha week (his "95%") holds the low **6 of 16** years; Mercury→Aries low holds 60 sessions 4 of 18 |
| Its own volatility claims | Amavasai / Pournami "volatile": +0.00 pp excess, null | — | "Volatile" calls: |move| above median 47–50% of the time (coin) | — (he makes none) |
| Verdict | **No directional edge.** Ceiling ≈ the always-down base rate. | **No rule clears a fair bar**, and the archive's two "paper-trade" numbers do not replicate on the repo's own data. | **No directional edge** on Nifty, gold or silver. | **No edge in the daily or date-candle rules.** One positional transit lead (n = 11) worth a forward ledger. |

Full write-ups: `backend/knowledge/backtest/opt/OPTIMISATION.md` (Mersal),
`backend/knowledge/backtest/gann/RESULTS.md` (Gann — the repo's own
measurement; `app/gann/calendar.py` still carries the course archive's
evidence strings), `backend/knowledge/backtest/saptarsh/RESULTS.md` (Saptarsh),
`backend/knowledge/backtest/vikas/RESULTS.md` and `backend/knowledge/vikas/NOTES.md`
(Vikas).

## The one thing that measurably works — and it isn't astrology

The **volatility model** (`backend/app/volmodel.py`): a six-feature logistic
regression on recent high–low ranges. Out-of-sample 2016–2026 it calls
whether the Nifty session will be *wider or narrower than its median move*
**about 60% of the time**, and its 90% band on the close holds **~91%** of
the time. It says nothing about direction. Adding any panchang or chain
feature made it significantly **worse** (−5.05 pp Nifty, −4.09 pp BankNifty,
both p < 0.001).

That is the only component in the app with a measured, replicated edge, and
it is a *sizing* tool, not a *direction* tool.

## What survives as "leads" — watch, don't trade

Across the four methods, uncorrected p < 0.05 turned up about fifteen rows,
which is roughly what chance produces in ~200 tests. A split-sample check
(first half vs second half of each window) sorts them:

| Lead | Method | Whole window | 1st half | 2nd half | Reading |
|---|---|---|---|---|---|
| **Mars enters Saturn's sign → Nifty up** over the transit | Vikas (his metals rule, Class 4) | +7.5% mean, **11 of 11** spans up vs 65% base, p = 0.01 | +8.6% | +6.7% | **Holds in both halves and on Nifty Metal (+8.2%, 8/11).** n = 11, one span every ~18 months; median +5.0% vs +1.7% for any Mars sign transit. |
| **Mars in the sign before Saturn's → Nifty down** | Vikas | −5.2% mean, **8 of 11** down vs 35% base, p = 0.02 | +0.9% | −10.3% | Median −3.4%; Saturn in an even sign −10.8% vs odd +1.4% — the split he teaches. The mean is the 2020 span; gold does not show it (+2.3%). |
| Moon in **Mula → gold up** | Saptarsh (his 4-of-5 call) | 66.7% up, n = 102, p = 0.010 | 66.0% (z +1.85) | 67.3% (z +1.82) | **Holds in both halves.** The best-supported rule of his — still uncorrected. |
| Moon in **Jyeshtha → gold down** | Saptarsh (he calls it "volatile") | 36.0% up, n = 100, p = 0.0004 | 32.0% (z −2.97) | 40.0% (z −2.09) | Holds in both halves and clears correction — but it is not a direction he gave. |
| **Vishti karana → Nifty down** | Saptarsh (2026 headline rule) | 41.5% up, n = 537, p = 0.014 | 43.8% (z −0.38) | 39.5% (z −3.07) | Only the second half. Unstable. |
| **Amavasya → silver up** | Saptarsh | 66.4% up, n = 107, p = 0.005 | 77.4% (z +3.70) | 55.6% (z +0.39) | Decays to nothing after 2020. |
| **Saturn-star days close down** | Vikas (his rule says *up*) | 58.4% down, n = 406, p = 0.001 | 57.6% | 59.1% | One of nine lords tested; the opposite of his reading and in line with the classical one. Study, not a rule. |
| Moon at 45/135/225/315° (tropical) at the open → breakout follows through | Vikas | 64% vs 57.5%, n = 281, p = 0.03 | — | — | One of ~25 candle families; the sidereal version scores 55%. Chance. |
| Mars–Jupiter semisquare → up 5 days | Gann (catalogue "lean") | Nifty +126 bp (p 0.07), 71% up; Bank Nifty +203 bp (p 0.03), 76% up; n = 17 | — | — | One of 22 rule × index tests; 17 events. Watch. |
| Venus station → up 5 days | Gann (catalogue "null") | Nifty +148 bp (p 0.02); Bank Nifty +164 bp (p 0.07); n = 18 | — | — | Same caveat; he does not even call it directional. |
| Mercury–Saturn conjunction flip | Gann | archive 70% vs 49% (n = 23); **repo measurement 58% vs 49%, n = 19, p 0.50** | — | — | Does not replicate; his own forward call failed. |
| `nak_lord + paksha` variant | Mersal best-of-6,912 | +4.9 pp, p = 0.045 | negative in 3 of 11 years | | +0.5 pp on BankNifty. Search artefact. |

None of these is a strategy. The two Saptarsh leads that replicate (Mula /
Jyeshtha for gold) are ~100-day samples on one instrument; the Vikas
Mars–Saturn pair is eleven spans. A real test is the *next* two years,
recorded in advance.

## The combined recipe — how to use the app from tomorrow

This is the only honest way to "use the best of all four":

1. **Size with the volatility model, never direct with astrology.**
   Read the day's band (Strategy tab, `/vol` in the bot, or the morning
   push). A LEANING WIDE day is a day to reduce size or widen stops; a
   NARROW day is a day not to expect a trend. Direction comes from your
   technical levels, as every one of the four sources itself insists.

2. **Treat every directional call in the app as study material.** The
   Prediction, Gann, Saptarsh and Vikas tabs all say so, and the numbers
   above are why. If you want one astrological input at all, restrict it
   to the two replicated gold leads — Moon in Mula (lean long gold) and
   Moon in Jyeshtha (lean short gold) — and only as a tie-breaker on top
   of a technical setup, with a stop.

3. **Use Vikas's dates for *where to look*, not *which way*.** His
   calendar tells you which candle to mark (star dates, ingress dates,
   Moon-45° days); the backtest says that candle breaks out and follows
   through no more often than any other candle. So: a date is a reason to
   have levels ready, never a reason to take a trade the chart has not
   given.

4. **One positional lean to ledger, not to trade yet:** Mars entering
   Saturn's sign → Nifty and the metal index up for the transit (11 of 11
   since 2011); Mars in the sign before Saturn's → down (8 of 11, worse
   when Saturn is in an even sign). The engine flags both on the Strategy
   and Vikas tabs. Eleven spans is too few — record the next two before
   sizing anything on it.

5. **Ignore the rest of the flags for trading; keep them for study.**
   Vishti, Amavasya, Mercury retrograde, Rahu Kaal, stellia, grand
   trines, Kaal Sarp, day-lords, carry-overs, Saturn→Mercury retraces —
   none survived, and the split test shows the ones that looked best are
   regime-dependent.

6. **Keep the ledger.** Every call the app makes is dated. Score the two
   gold leads, the Mars–Saturn lean and the volatility band forward for
   a year before believing any of them. The Saptarsh tab's calls logs show
   what happens when a method is judged only by its reposted hits.

## Why the four agree

They start from the same sky and the same panchang; they differ only in
the interpretive layer (chain-counting, transit-to-natal aspects,
Moon-nakshatra + timed aspects, event dates + day-lords). The backtests
found the same thing four times: the layer adds nothing that a coin — or
the majority side, or any other candle — does not already give. The
market's own recent volatility, with no astrology, is the one input that
carried information.
