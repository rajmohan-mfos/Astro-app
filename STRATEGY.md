# Which method to actually use — the three-way comparison

Three astrological methods live in this app, and all three have now been
backtested on the same instrument with the same discipline: score the call
against the realised move, compare with the trivial benchmark on the *same
days*, and correct for how many rules were tried.

| | **Options Mersal** (GRAHA MARKETS course — Prediction tab) | **Gann cosmogram** (Gann tab) | **Saptarsh Insight** (Saptarsh tab) |
|---|---|---|---|
| What it predicts | Nifty session direction, from the sunrise chain (X/X1/Y/Y1), panchang tally, horai | Trend reversals / swings on dated planetary aspects and stations | Nifty session direction; gold & silver daily direction; intraday windows |
| Test window | Nifty 2011–2026 (15 yr, 3,830 bars), walk-forward; BankNifty as a second index | Nifty 2007–2026, every exact event of 11 catalogued rules | Nifty, COMEX gold & silver 2016–2026 (≈2,650 days each) |
| Benchmark it must beat | Always-down on its own traded days (53.0%) | Base rate of a trend flip on any day (49%); within ±2 days (85%) | Always-majority-side on its own traded days (Nifty 52.3%, gold 54.6%, silver 52.5%) |
| Headline result | Engine as shipped **48.9%** (−4.4 pp, z = −4.2 — worse than always-down); day-score confluence 45.8%; nested walk-forward **53.95%** (z = +0.52) | Best rule Venus–Jupiter square **54% vs 43% base on 26 trades** (n.s.); Mercury–Saturn conjunction 70% flips vs 49% (p = 0.038, one of ~25 tests); everything else null / rare / calendar trap | Nifty **51.6% vs 52.3%** (n = 1,959, perm-p 0.11); gold **48.8% vs 54.6%**; silver **49.7% vs 52.5%** |
| Rules that survive multiple-comparison correction | **0** of 6,912 variants (best-of search p = 0.045, but the shuffled null's own maximum beats the real data) | **0** of 11 (two "paper-trade", none significant) | **0** of 32 rules on any instrument |
| Second-instrument check | BankNifty: **47.1%** (z = −2.85) — the Nifty "winner" vanishes | — | Gold and silver both below benchmark; "observed" calls no better than extrapolated |
| Its own volatility claims | Amavasai / Pournami "volatile": +0.00 pp excess, null | — | "Volatile" calls: |move| above median 47–50% of the time (coin) |
| Verdict | **No directional edge.** Ceiling ≈ the always-down base rate. | **No rule clears a fair bar.** | **No directional edge** on Nifty, gold or silver. |

Full write-ups: `backend/knowledge/backtest/opt/OPTIMISATION.md` (Mersal),
`backend/app/gann/calendar.py` evidence strings and `gann-engine-CLAUDE.md`
(Gann), `backend/knowledge/backtest/saptarsh/RESULTS.md` (Saptarsh).

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

Across the three methods, uncorrected p < 0.05 turned up about a dozen rows,
which is roughly what chance produces in ~150 tests. A split-sample check
(2016–2020 vs 2021–2026) sorts them:

| Lead | Method | Whole window | 2016–2020 | 2021–2026 | Reading |
|---|---|---|---|---|---|
| Moon in **Mula → gold up** | Saptarsh (his 4-of-5 call) | 66.7% up, n = 102, p = 0.010 | 66.0% (z +1.85) | 67.3% (z +1.82) | **Holds in both halves.** The best-supported rule of his — still uncorrected. |
| Moon in **Jyeshtha → gold down** | Saptarsh (he calls it "volatile") | 36.0% up, n = 100, p = 0.0004 | 32.0% (z −2.97) | 40.0% (z −2.09) | Holds in both halves and clears correction — but it is not a direction he gave. |
| **Vishti karana → Nifty down** | Saptarsh (2026 headline rule) | 41.5% up, n = 537, p = 0.014 | 43.8% (z −0.38) | 39.5% (z −3.07) | Only the second half. Unstable. |
| **Amavasya → silver up** | Saptarsh | 66.4% up, n = 107, p = 0.005 | 77.4% (z +3.70) | 55.6% (z +0.39) | Decays to nothing after 2020. |
| Venus–Jupiter square swing | Gann | 54% vs 43%, n = 26 | — | — | Too few trades to say anything. |
| Mercury–Saturn conjunction flip | Gann | 70% vs 49%, n = 23, p = 0.038 | — | — | One expected false positive in 25; his own forward call failed. |
| `nak_lord + paksha` variant | Mersal best-of-6,912 | +4.9 pp, p = 0.045 | negative in 3 of 11 years | | +0.5 pp on BankNifty. Search artefact. |

None of these is a strategy. The two that replicate (Mula / Jyeshtha for
gold) are ~100-day samples on one instrument; a real test is the *next*
two years, recorded in advance.

## The combined recipe — how to use the app from tomorrow

This is the only honest way to "use the best of all three":

1. **Size with the volatility model, never direct with astrology.**
   Read the day's band (Strategy tab, `/vol` in the bot, or the morning
   push). A LEANING WIDE day is a day to reduce size or widen stops; a
   NARROW day is a day not to expect a trend. Direction comes from your
   technical levels, as every one of the three sources itself insists.

2. **Treat every directional call in the app as study material.** The
   Prediction, Gann and Saptarsh tabs all say so, and the numbers above
   are why. If you want one astrological input at all, restrict it to the
   two replicated gold leads — Moon in Mula (lean long gold) and Moon in
   Jyeshtha (lean short gold) — and only as a tie-breaker on top of a
   technical setup, with a stop.

3. **Ignore the rest of the flags for trading; keep them for study.**
   Vishti, Amavasya, Mercury retrograde, Rahu Kaal, stellia, grand
   trines, Kaal Sarp — none survived, and the split test shows the two
   that looked best are regime-dependent.

4. **Keep the ledger.** Every call the app makes is dated. Score the two
   gold leads and the volatility band forward for a year before believing
   either. The Saptarsh tab's calls logs show what happens when a method
   is judged only by its reposted hits.

## Why the three agree

They start from the same sky and the same panchang; they differ only in
the interpretive layer (chain-counting, transit-to-natal aspects,
Moon-nakshatra + timed aspects). The backtests found the same thing three
times: the layer adds nothing that a coin — or the majority side — does
not already give. The market's own recent volatility, with no astrology,
is the one input that carried information.
