"""Tests for the optimisation harness.

The single most important test here is test_folds_never_leak. A walk-
forward harness that lets one future bar into a training window produces
numbers that look like success and are worthless, and nothing else in the
study would catch it. Everything else is secondary.

These tests need numpy and the prebuilt feature table; both are study-only
(requirements-research.txt), so they skip rather than fail when the app is
installed without them.
"""
import os
import random
import sys

import pytest

OPT = os.path.join(os.path.dirname(__file__), "..", "scripts", "opt")
sys.path.insert(0, OPT)

pytest.importorskip("numpy")

import stats                                                 # noqa: E402

FEATURES = os.path.join(os.path.dirname(__file__), "..", "knowledge",
                        "backtest", "opt", "features_nifty.csv")
needs_features = pytest.mark.skipif(
    not os.path.exists(FEATURES), reason="feature table not built")


# --------------------------------------------------------------- leakage
@needs_features
def test_folds_never_leak():
    """No training window may contain a bar from its own test year, or
    from any later year. This is the test the whole study rests on."""
    import features as feat
    import walkforward as wf

    rows = feat.load()
    seen_years = []
    for y, train, test in wf.folds(rows):
        assert train, f"fold {y} has an empty training window"
        assert max(r["year"] for r in train) < y
        assert {r["year"] for r in test} == {y}
        assert max(r["date"] for r in train) < min(r["date"] for r in test)
        seen_years.append(y)
    assert seen_years == sorted(seen_years)
    assert len(seen_years) >= 10


@needs_features
def test_contribution_matrix_is_fitted_on_train_only():
    """Corrupting the test fold's labels must not change the fitted
    contributions — if it does, the test labels are leaking into the fit."""
    import features as feat
    import walkforward as wf

    rows = feat.load()
    _y, train, test = next(iter(wf.folds(rows)))
    before = wf.contribution_matrix(train, test, 20.0)
    flipped = [dict(r, up=1 - r["up"]) for r in test]
    after = wf.contribution_matrix(train, flipped, 20.0)
    assert (before == after).all()


def test_fit_group_shrinks_rare_levels_toward_base():
    """Two levels with the SAME empirical rate must not carry the same
    weight — the one backed by fewer observations has to be pulled harder
    toward the base rate. Without this, a level seen 3 times at 100% up
    dominates the tally and the search overfits on sample noise."""
    import walkforward as wf

    rows = [{"up": i % 2, "k": "filler"} for i in range(400)]   # base 50%
    rows += [{"up": 1, "k": "rare"}] * 5                        # 100%, n=5
    rows += [{"up": 1, "k": "frequent"}] * 200                  # 100%, n=200
    table = wf.fit_group(rows, lambda r: r["k"], smoothing=20.0)

    assert table["rare"] > 0 and table["frequent"] > 0
    assert table["rare"] < table["frequent"]
    # and heavier smoothing must shrink both further
    heavy = wf.fit_group(rows, lambda r: r["k"], smoothing=200.0)
    assert heavy["rare"] < table["rare"]


# ------------------------------------------------------------- shuffling
def test_block_shuffle_preserves_the_multiset():
    rng = random.Random(1)
    vals = list(range(100))
    out = stats.block_shuffle(vals, 7, rng)
    assert sorted(out) == sorted(vals)
    assert len(out) == len(vals)


def test_block_shuffle_keeps_runs_together():
    """Blocks must stay contiguous, otherwise the null destroys the serial
    correlation in returns and becomes too easy to beat."""
    rng = random.Random(2)
    vals = list(range(60))
    out = stats.block_shuffle(vals, 10, rng)
    # every value should still sit next to at least one original neighbour
    adjacent = sum(1 for i in range(len(out) - 1)
                   if abs(out[i] - out[i + 1]) == 1)
    assert adjacent >= len(out) * 0.7


def test_block_shuffle_of_one_is_a_plain_shuffle():
    rng = random.Random(3)
    vals = list(range(50))
    assert sorted(stats.block_shuffle(vals, 1, rng)) == vals


# ----------------------------------------------------------------- stats
def test_wilson_brackets_the_point_estimate():
    lo, hi = stats.wilson(50, 100)
    assert lo < 50.0 < hi
    wide, narrow = stats.wilson(5, 10), stats.wilson(500, 1000)
    assert (wide[1] - wide[0]) > (narrow[1] - narrow[0])


def test_prop_z_signs_correctly():
    assert stats.prop_z(600, 1000, 0.5) > 0
    assert stats.prop_z(400, 1000, 0.5) < 0
    assert abs(stats.prop_z(530, 1000, 0.53)) < 0.1


def test_binom_two_sided_is_a_probability():
    for k, n in ((5, 10), (0, 10), (10, 10), (37, 50)):
        assert 0.0 <= stats.binom_two_sided(k, n) <= 1.0
    assert stats.binom_two_sided(5, 10) > stats.binom_two_sided(10, 10)


# ------------------------------------------------------- engine fidelity
@needs_features
def test_feature_table_reproduces_the_published_backtest():
    """The features must describe the engine the app actually ships.
    RESULTS.md reports 48.3% on 2021-08-10..2026-08-10; if this drifts,
    the study is measuring something else."""
    import features as feat

    rows = feat.load()
    window = [r for r in rows if "2021-08-10" <= r["date"] <= "2026-08-10"]
    assert 1200 < len(window) < 1270
    directional = [r for r in window if r["chain_score"] != 0]
    hits = sum(1 for r in directional
               if (r["chain_score"] > 0) == (r["up"] == 1))
    assert 47.0 < hits / len(directional) * 100 < 49.5


@needs_features
def test_baselines_are_computed_on_directional_calls_only():
    import features as feat
    import walkforward as wf

    rows = feat.load()[:500]
    preds = wf.baseline_preds(rows, "current_engine")
    h, n = wf.score(preds, rows)
    assert n == sum(1 for r in rows if r["chain_score"] != 0)
    assert 0 <= h <= n
