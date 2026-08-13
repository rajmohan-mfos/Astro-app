# Can the engine be tuned toward 100%? — a walk-forward ceiling study

**Question asked:** set a target, loop — write code, measure against 15 years
of Nifty, change strategy, repeat — until accuracy approaches 100%.

**Answer: no, and the ceiling is about 53%.** That is not a statement about
how hard we tried. It is a measured property of the data, and this document
is the measurement.

Reproduce with `python scripts/opt/run_study.py` (needs
`requirements-research.txt`). Everything reads a cached price series and a
prebuilt feature table, so the numbers do not drift with the run date.

---

## 1. What "success" actually has to beat

Nifty closes below its open on **53.04%** of the 2,615 out-of-sample bars
(mean intraday move −0.06%). So a strategy that says "down" every single
morning, using no astrology and no data at all, scores 53.04%.

That — not 50% — is the bar. Everything below is measured against it.

| Baseline (Nifty, 2016–2026 out-of-sample) | Rate | Edge vs same-day always-down |
|---|---|---|
| **always-down** | **53.04%** | — |
| always-up | 46.96% | −6.08pp |
| previous-day momentum | 48.49% | −4.55pp |
| previous-day contrarian | 51.51% | −1.53pp |
| **the engine as shipped** (sign of chain score) | **48.89%** | **−4.39pp** (z = −4.22) |
| **the engine's day_score** (chain + panchang agreeing) | **45.82%** | **−8.75pp** (z = −4.86) |

The shipped engine is not merely unhelpful; it is **4σ worse than a coin that
always says down**. The day_score confluence rule is worse still, which
matches the earlier finding that HIGH-conviction days were the least reliable
cell in the 5-year study.

## 2. Method

15 years, 2011-01-03 → 2026-08-13, 3,830 bars, cast at Mumbai in KP at
sunrise — the app's own path, not the old backtest's (which read panchang
from a *different* chart: Lahiri at 09:15; see `features.py`).

- **Walk-forward, expanding.** Fit on 2011..Y, test on Y+1, never look back.
  11 untouched out-of-sample years, 2,615 bars.
- **Variant budget declared in advance: 6,912.** 576 feature-group subsets
  (all 1-, 2- and 3-way combinations of 15 groups, plus the all-groups model)
  × 4 shrinkage levels × 3 decision thresholds. Groups: thithi, thithi-in-
  paksha, thithi family, karanam, yogam, nakshatra, nakshatra lord, weekday,
  paksha, chain bucket, panchang bucket, X planet, X count, Y planet, first
  segment bias.
- Each group contributes an additive log-odds term fitted **inside the
  training window only**, shrunk toward the training base rate.

`tests/test_walkforward.py::test_folds_never_leak` asserts no training window
ever contains a bar from its own test year or later. A leak there would look
exactly like success, and nothing else in the study would catch it.

## 3. The trap, and the metric that avoids it

The best of 6,912 variants scores **59.14%** out-of-sample. That looks like a
decisive win over 53.04%, and it is the number a "loop until the target is
hit" procedure would have reported as success.

It is an artifact, for two independent reasons.

**First — it trades only the days it likes.** That variant makes a call on
509 of 2,615 days (19.5%), and *those 509 days are 57.96% down*. Always-down,
on the variant's own chosen days, scores 57.96%. The variant scores 59.14%.
The actual forecasting skill is **+1.18pp, z = +0.54** — nothing.

Comparing a selective strategy against the all-days base rate credits it with
five points it never earned. Every number below therefore uses **edge**:

> edge = hit rate − always-down **on that same strategy's own traded days**

**Second — it is the maximum of 6,912 tries.** Even with the day-selection
effect removed, picking the best of thousands of variants is biased upward.
Section 5 measures by how much.

## 4. The honest number: nested walk-forward

The protocol that answers "what would I actually have traded, knowing only
the past": inside each training window, hold out the most recent year, pick
the single best variant on it, refit, and apply that one variant to the
untouched test year.

**Nifty: 430/797 = 53.95%**, 95% CI [50.48, 57.39], vs 53.04% — **z = +0.52**.
Not significant.

The per-year detail is the most informative table in this study:

| Test year | Variant selected | Score on inner validation | Score out-of-sample |
|---|---|---|---|
| 2016 | karanam+weekday+panchang | 57.8% | 58.1% |
| 2017 | paksha+panchang | 63.0% | 50.8% |
| 2018 | thithi_paksha+nakshatra+first_seg | 62.6% | 50.0% |
| 2019 | thithi_paksha+chain+y_planet | 64.6% | 52.5% |
| 2020 | y_planet | 70.2% | 61.3% |
| 2021 | karanam+chain | 70.8% | 61.4% |
| 2022 | karanam+weekday+paksha | 69.6% | 52.2% |
| 2023 | thithi+nak_lord+panchang | 64.6% | 51.6% |
| 2024 | thithi_family+karanam | 63.3% | 61.2% |
| 2025 | thithi_family+karanam+panchang | 65.0% | 55.1% |
| 2026 | thithi_family+nak_lord+paksha | 69.8% | 50.9% |

Two things to read here. **A different variant wins every single year** — no
combination is stable, which is what noise looks like. And the selection score
(58–71%, mean ~65%) has **no relationship** to the out-of-sample score
(50–61%, mean 54%). That ~11-point collapse, repeated 11 times, *is* the
overfitting, measured directly rather than argued about.

This is precisely what the requested loop would have produced: a sequence of
rules each looking 65% right when chosen, each landing near 53% in reality.

## 5. Permutation null — how good does luck get?

Re-run the identical search — same 6,912 variants, same folds — against
outcomes block-shuffled in 21-bar blocks (blocks preserve volatility
clustering; an i.i.d. shuffle would make the null too easy and overstate
significance). 200 permutations. This measures how large a best-of-6,912 edge
appears when there is provably nothing to find.

| | Edge (best of 6,912) |
|---|---|
| **real data** | **+4.92pp** |
| null mean | +2.26pp |
| null median | +2.12pp |
| null 95th percentile | +4.63pp |
| **null maximum** | **+6.43pp** |
| p-value | **0.045** |

Read that carefully before celebrating it.

The real result clears the 95th percentile — by 0.29pp, p = 0.045, a hair
under the conventional line. But **the null's own maximum, +6.43pp, is higher
than the real data's +4.92pp**: in at least one of 200 runs on outcomes that
were provably meaningless, this exact search produced a *better* answer than
it produced on the real market. And searching 6,912 variants on noise still
yields +2.26pp on average — so more than half the apparent edge of any winner
is manufactured by the search itself.

The winning variant here is `[nak_lord+paksha] m=50 t=0.15`: 56.46% raw on 712
calls, against 51.54% always-down on those same days, z = +2.62 taken in
isolation. That z is exactly the trap. It is the maximum of 6,912 tries, and
the null is what converts it from "significant" to "marginal at best".

Section 6 then removes the ambiguity entirely.



## 6. Second instrument: BankNifty

A real effect should not care which index it is measured on.

| | Nifty | BankNifty |
|---|---|---|
| always-down | 53.04% | 52.33% |
| engine as shipped | 48.89% (−4.39pp) | 50.39% (−2.26pp) |
| **nested walk-forward** | **53.95% (z = +0.52)** | **47.11% (z = −2.85)** |

On BankNifty the same procedure lands **significantly worse than always-down**.

The two variants that won on Nifty were then run unchanged on BankNifty:

| Variant | Nifty edge | BankNifty edge |
|---|---|---|
| `karanam` (best raw rate) | +1.18pp (z=+0.54) | **−5.41pp** (z=−1.47) |
| `nak_lord+paksha` (best edge, p=0.045) | +4.92pp (z=+2.62) | **+0.49pp** (z=+0.24) |

The variant that marginally cleared the permutation null on Nifty carries
essentially zero edge on BankNifty. Its Nifty per-year edges are also unstable
— negative in 3 of 11 years (−5, −3, −4pp) and +18pp in one. A lunar-calendar
effect on Indian equities that appears in the Nifty and vanishes in the
BankNifty, drawn from the same sessions and largely the same constituents, is
not an effect. It is the 1-in-20 that p = 0.045 explicitly predicts.

Best-of search on BankNifty independently confirms this: best edge only
+2.66pp, **median variant edge −2.63pp**.

## 7. Tier 2 — the ceiling with a modern classifier

Tier 1 re-fits the taught structure. This asks whether *any* model can do
better: regularised logistic regression and gradient boosting over the full
one-hot feature set — every panchang field, the chain planets and counts, the
segment bias shares, and Moon/Sun angles as sin/cos.

| Model (Nifty, walk-forward) | Rate | z vs always-down |
|---|---|---|
| logistic C=0.01 | 53.23% | +0.20 |
| logistic C=0.1 | 53.80% | +0.78 |
| logistic C=1 | 53.65% | +0.63 |
| gradient boosting | 52.93% | −0.12 |
| gradient boosting, deep | 53.61% | +0.59 |
| logistic C=0.01, top/bottom decile only | 55.73% | +1.23 |
| gradient boosting deep, top/bottom decile | 55.92% | +1.32 |

Every one is inside ±1.4σ. At the 0.5 threshold the models converge on
53.0–53.8% — they have learned "predict down", and essentially nothing else.

This is the part that generalises past the course's own tables. These models
are strictly more expressive than an additive tally of hand-assigned biases,
so the conclusion is not "the weights were set wrong". **The features do not
carry the information.** No amount of retuning `STAR_VALUE`, `CHAIN_WEIGHTS`
or the thithi/yogam/karanam tables can recover a signal that is not there.

## 8. Calibration — one thing that IS wrong and fixable

Separate from the search, with a reason independent of the target: the
panchang tally is structurally biased bullish. The course tables grade far
more days auspicious than inauspicious, so the engine can barely emit a
strong bearish call — 138 of 152 HIGH-conviction days in the 5-year study
were bullish, against a market that falls 53% of the time.

| Nifty, walk-forward | Rate | Bullish calls | z vs always-down |
|---|---|---|---|
| panchang as shipped | 47.86% | 80.7% | −5.17 |
| recentred on training mean | 49.25% | 62.0% | −3.88 |
| quantile-matched cut | 49.87% | 41.2% | −3.25 |

(The market itself rises on 47.0% of days.)

Recentring **does** fix the tilt — 80.7% bullish calls down to 41.2%, close to
the market's own mix — and gains about 2 points. But it never approaches
53.04%; it stays 3.3σ below.

That separates the two possible diagnoses cleanly. The threshold **was**
misplaced, and that part is real and fixable. But fixing it does not make the
engine predictive, because the underlying signal is empty. A miscalibrated
pointer at nothing still points at nothing.

## 9. Volatility instead of direction

Direction is close to a fair coin. Volatility is not — `|ret|` has
autocorrelation **+0.215 at lag 1** and is still +0.146 at lag 10, the
clustering every GARCH model exploits. So this target is genuinely
predictable, and the benchmark changes completely: a model must beat *lagged
volatility*, not the base rate.

**A lagged-volatility model is already good.** Logistic regression on
strictly-lagged rolling means of `|ret|` (windows 1/3/5/10/21), prior return,
trailing dispersion, and NSE expiry flags (Thursday, last Thursday, expiry
neighbourhood):

| Model, walk-forward, median-split target | Nifty | BankNifty |
|---|---|---|
| **A — lagged volatility + expiry only** | **59.96%** | **63.56%** |
| **B — A plus every astro feature** | 54.91% | 59.47% |
| **delta (astro's contribution)** | **−5.05pp** | **−4.09pp** |
| 95% CI on the delta (block bootstrap) | [−7.38, −2.87] | [−6.30, −1.83] |
| exact McNemar | p < 0.001 | p < 0.001 |

Both models are fitted on identical folds and identical rows, differing only
in the astro columns, so the delta is the whole story. Expiry is deliberately
in the *baseline*: it is a large calendar-driven volatility source, and
leaving it out would let the astro block take credit for finding the
calendar.

The astro features do not merely fail to help — they **actively degrade a
working model**, significantly, on both indices. Giving them their best shot
across regularisation strengths does not rescue it:

| Model B regularisation | C=0.003 | 0.01 | 0.03 | 0.1 | 0.3 | 1.0 |
|---|---|---|---|---|---|---|
| delta vs Model A | −3.13pp | −4.05pp | −4.85pp | −5.05pp | −5.24pp | −5.81pp |

The delta worsens monotonically as the astro block gets more weight — the
signature of noise being fitted. (At C=0.003 the penalty also shrinks the
useful volatility features, so −3.13pp is a floor artifact, not astro
approaching neutrality.)

### Pre-registered hypotheses

Because the course makes *specific* volatility claims, these were declared
before running and tested exactly as declared — five tests, Bonferroni
α = 0.010 — rather than searched. Each compares mean `|ret|` in the category
against all other days, measured as **excess over the day's own trailing
21-day level**, so "these days are volatile" cannot be satisfied merely by
landing inside an already-volatile stretch. p-values from 2,000 block
permutations.

| Claim | n | Excess diff (Nifty) | p | BankNifty p |
|---|---|---|---|---|
| Amavasai (new moon) → volatile | 135 | −0.0315pp | 0.537 | 0.254 |
| Pournami (full moon) → volatile | 112 | +0.0015pp | 0.975 | 0.636 |
| New **or** full moon | 247 | −0.0170pp | 0.665 | 0.604 |
| Extreme yogas (Vyaghata/Vyatipata/Vaidhriti) — the course's explicit "crash-risk day" | 422 | +0.0115pp | 0.689 | 0.696 |
| Rikta thithis 4/9/14 — "sharp gap-downs, 1000–2000 point drops" | 751 | +0.0005pp | 0.983 | 0.456 |

**None survives, on either index.** Not one is even close — the smallest
p-value across ten tests is 0.25.

The Rikta result deserves a line of its own. The course sheet describes those
days as producing sharp gap-downs of 1,000–2,000 points. Across 751 of them
over 15 years, the measured excess volatility is **+0.0005 percentage points,
p = 0.983** — indistinguishable from exactly nothing.

So volatility is the better question, and it has a better answer: it *is*
predictable, to about 60% on Nifty and 64% on BankNifty. Just not by
astrology. The lunar and panchang features contribute nothing to it, and
including them costs about five points.

## 10. The one thing that works: `app/volmodel.py`

Section 9 established that volatility is predictable and astrology does not
help predict it. The volatility part is worth keeping on its own, so it is
now a shipped module — trained by `scripts/opt/train_volmodel.py`, served by
`app/volmodel.py`.

**Six features**: mean daily high-low range over the previous 1, 3, 5, 10, 21
and 63 sessions. Nothing else. No astrology.

Range rather than `|ret|` was chosen **before** any accuracy was computed, on
the grounds that a range uses the whole session instead of two points of it:
it correlates **+0.314** with tomorrow's `|ret|` against **+0.215** for `|ret|`
itself. The accuracy comparison, run afterwards on identical folds, agreed:

| Paired comparison (Nifty, walk-forward) | Delta | 95% CI | McNemar |
|---|---|---|---|
| range vs `\|ret\|`-only | **+1.38pp** | [+0.30, +2.55] | p = 0.030 |
| adding `\|ret\|` back on top of range | +0.46pp | [−0.53, +1.41] | p = 0.356 |

So range earns its place and `|ret|` does not — the shipped model is the
parsimonious 6-feature one.

**Out-of-sample, 2016–2026:**

| | Nifty | BankNifty |
|---|---|---|
| accuracy (median split of `\|ret\|`) | 60.34% | 64.17% |
| Brier score | 0.2355 | 0.2244 |
| Brier skill vs base rate | **+4.2%** | **+7.5%** |

Accuracy alone would be the wrong thing to report for a "how wide will today
be" tool, so calibration matters more:

| Stated probability | n | Mean stated | Actually wide |
|---|---|---|---|
| 0.00–0.35 | 180 | 33.9% | 26.7% |
| 0.35–0.45 | 1226 | 40.0% | 36.7% |
| 0.45–0.55 | 821 | 49.1% | 49.8% |
| 0.55–0.65 | 287 | 58.8% | 55.7% |
| 0.65–1.01 | 101 | 82.7% | **71.3%** |

The middle bins track well. **The top bin is overconfident** — a stated 83%
resolves at 71%. That is why the module reports a coarse band rather than a
bare probability: at the `p ≥ 0.65` cut the realised rate is 71.3% wide, and
at `p ≤ 0.35` it is 73.3% narrow, both of which the label honestly supports.
Per-year accuracy ranges 54–76% with no downward trend.

### What it is not

60% on a two-way split of session width is **ordinary**. Volatility clustering
is one of the oldest known properties of markets and every GARCH textbook
exploits it; this model is a plain-vanilla instance of that, not an edge.
It says **nothing about direction** — a wide day is equally likely to be wide
up or wide down, and section 1 showed no method of calling that better than a
coin. It is context for reading a session, and it is not wired to anything
that places an order.

### Architecture

sklearn is study-only (`requirements-research.txt`). Training happens offline
and exports `app/volmodel_weights.json`; the runtime is pure stdlib, so the
API and the PythonAnywhere bot stay dependency-light — the deploy zip goes
from 25 files / 55 KB to 28 / 61 KB and still carries no course material.
`train_volmodel.py` asserts the stdlib scorer reproduces sklearn's
`predict_proba` (observed max difference 2.2e-16); a silently mismatched
scaler would otherwise produce plausible garbage with no error.

Surfaced in the daily Telegram push as its own block, and as `/vol` in the
bot. Both degrade to a plain message if prices cannot be fetched, since
PythonAnywhere's free tier may not reach the quote provider.

## 11. Re-fitting the engine's own tables

Requested directly: replace the course's hand-assigned numbers with numbers
learned from the market, in the engine's own five tables, tuned as hard as
the data allows. `scripts/opt/fit_tables.py` does exactly that and writes
`app/rules/fitted_tables.json`; `ASTRO_SCORE_MODE=fitted` makes the engine
use them.

The taught tables are **not** edited — they are the app's provenance, still
pinned by tests. Fitted mode adds a second reading beside the first.

### The two numbers

| | Rate |
|---|---|
| **In-sample**, all days | 55.98% |
| **In-sample**, selective calls (\|score\| > 0.40, 11% of days) | **65.53%** |
| **Out-of-sample**, identical procedure re-fitted per fold | 56.18% |
| always-down on those same out-of-sample days | 54.18% |
| **edge** | **+1.99pp, z = +0.90** |

65.53% is the number that looks like success, and it is the one to distrust:
it is fitted and scored on the same 15 years. Run the identical procedure
honestly — re-fitting inside each expanding window and scoring the year it
has never seen — and it gives +1.99pp over doing nothing, z = +0.90, not
significant.

### What the data says about the course's tables

This is the genuinely interesting output. Fitted values are log-odds of an up
day relative to the base rate.

**Star lords** — 6 of 7 agree in *sign* with the course:

| Lord | Course | Data | |
|---|---|---|---|
| Mercury | +1.0 | +0.046 | agrees |
| Moon | +0.5 | +0.081 | agrees |
| Mars | −0.5 | −0.031 | agrees |
| Saturn | −1.0 | −0.119 | agrees |
| Ketu | −1.0 | −0.097 | agrees |
| **Venus** | **+0.5** | **−0.141** | **opposite** |
| Sun | 0.0 (neutral) | **+0.321** | strongest positive of all |
| Jupiter | amplifier | −0.221 | |
| Rahu | amplifier | +0.166 | |

**Chain weights** — the two labels the whole engine is built on come out
near zero and *reversed*:

| Label | Course | Data |
|---|---|---|
| **bullish** | **+1.0** | **−0.014** |
| **bearish** | **−1.0** | **+0.045** |
| sideways-bullish | +0.5 | +0.041 |
| sideways-bearish | −0.5 | −0.171 |

**Yogam** — the 16/8/3 classification is *inverted*:

| Course class | n | Mean fitted |
|---|---|---|
| very negative (அதித அசுபம்) | 3 | **+0.118** |
| negative | 11 | +0.072 |
| positive | 16 | **−0.048** |

**Thithi families** — 4 of 5 agree in sign (Jaya is the exception), but every
magnitude is under 0.14.

### How to read all that

Two temptations, both wrong.

The first is to see "6 of 7 star lords agree" as vindication. Under random
signs, 6-or-better out of 7 happens 6% of the time, this was checked after
the fact rather than predicted, and — decisively — **the magnitudes are
tiny**. A fitted log-odds of +0.046 for Mercury is a rounding error on a
coin flip, not the "maximum positive" the course describes. The signs agree
about noise.

The second is to see the yogam inversion as a discovery — that you should
trade *against* the classification. The same objection applies with the same
force: mean +0.118 versus −0.048 on 27 categories is well inside what
resampling produces, and section 5 already showed what happens to findings
of this size.

The honest summary is the one the magnitudes give: **re-fitting drives nearly
every weight to approximately zero**, because there is nearly nothing to fit.
That is the same conclusion as sections 1–7, arrived at from the opposite
direction — and it is why the fitted engine gains +1.99pp out-of-sample
instead of the +12 that its in-sample number implies.

### What shipped

- `ASTRO_SCORE_MODE=fitted` switches the engine; **default stays `taught`**,
  so a fresh checkout still reproduces the course method.
- The fitted call appears in the API, the rule findings and the daily
  Telegram push — always with both rates side by side. A test
  (`test_in_sample_rate_never_appears_without_out_of_sample`) enforces that
  the flattering number can never be displayed alone.
- The taught reading is left completely intact in fitted mode, so the two can
  be compared rather than one silently replacing the other.

## 12. Conclusion

- The measured ceiling on daily direction is **≈53%**, which is the base rate.
  Nothing in 6,912 rule variants, two classifier families, or 15 years of data
  beat it out-of-sample on both instruments.
- **One candidate cleared the permutation null at p = 0.045 and is reported
  here rather than buried** — `nak_lord+paksha`, +4.92pp on Nifty. It is not
  an edge: it is the maximum of 6,912 tries, the null's own maximum beat it,
  it is unstable across years, and it evaporates to +0.49pp on BankNifty. It
  is what a false positive looks like, which is why the study was built to
  produce one and then identify it as such.
- The engine **as shipped is worse than useless** for direction: 4σ below
  always-down. If it were inverted it would still not be a strategy, because
  the day-selection effect explains the difference.
- 100% is not approachable, and no loop can get there. Daily index direction
  is close to a fair coin; the honest target was never a number but the
  question "is there anything here?", and the answer is no.
- The one genuine defect found — the bullish calibration tilt — is worth
  knowing about but does not change the conclusion.
- **Volatility is the better target and gives a cleaner answer.** It is
  genuinely predictable (60% Nifty, 64% BankNifty from lagged volatility and
  expiry alone), and adding the astro features makes it significantly
  *worse* on both indices. Five pre-registered course claims — new moon, full
  moon, the extreme yogas, the Rikta "1000–2000 point drop" thithis — all
  fail, none close.

**Nothing in `backend/app/` was modified.** The app's own disclaimers already
describe it as a study aid rather than a signal, and this study is the
strongest evidence yet that they are correct and should stay.
