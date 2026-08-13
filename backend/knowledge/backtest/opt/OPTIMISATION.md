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

## 10. Conclusion

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
