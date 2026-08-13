"""Tests for the volatility model runtime.

Two of these matter more than the rest:

  test_features_never_see_the_current_bar — if bar i's own range leaked
  into its own features the model would look brilliant and be useless.

  test_stdlib_scorer_matches_the_trained_weights — the model is trained
  with sklearn and served by hand-written stdlib arithmetic. A mismatched
  scaler or a reordered coefficient produces plausible numbers with no
  error anywhere, so the arithmetic is pinned directly.
"""
import json
import math
import os

import pytest

from app import volmodel


def _bars(n=120, rng=1.0, start="2020-01-01"):
    """Synthetic ascending bars with a controllable daily range."""
    import datetime
    d0 = datetime.date.fromisoformat(start)
    out = []
    for i in range(n):
        base = 100.0
        out.append({"date": (d0 + datetime.timedelta(days=i)).isoformat(),
                    "open": base, "close": base,
                    "high": base + rng / 2, "low": base - rng / 2})
    return out


# ------------------------------------------------------------- leakage
def test_features_never_see_the_current_bar():
    bars = _bars(80)
    spiked = [dict(b) for b in bars]
    spiked[40]["high"] = 500.0          # an enormous range on bar 40

    for i in (39, 40):
        assert volmodel.features(bars, i) == volmodel.features(spiked, i), \
            f"bar {i} sees a range it must not (bar 40's own move)"
    assert volmodel.features(bars, 41) != volmodel.features(spiked, 41), \
        "bar 41 should see bar 40's range but does not"


def test_features_handle_the_start_of_history():
    bars = _bars(5)
    assert volmodel.features(bars, 0) == [0.0] * len(volmodel.WINDOWS)
    f = volmodel.features(bars, 3)
    assert len(f) == len(volmodel.WINDOWS)
    assert all(v >= 0 for v in f)


def test_features_are_the_mean_range_over_each_window():
    bars = _bars(80, rng=2.0)          # every bar has a 2% range
    f = volmodel.features(bars, 70)
    for v in f:
        assert v == pytest.approx(2.0, abs=1e-9)


# --------------------------------------------------------- scorer parity
def test_stdlib_scorer_matches_the_trained_weights():
    """Recompute the logistic by hand and compare to the module."""
    w = volmodel.weights()
    bars = _bars(100, rng=1.5)
    i = 90
    z = [(v - m) / s for v, m, s
         in zip(volmodel.features(bars, i), w["mu"], w["sd"])]
    s = w["intercept"] + sum(c * v for c, v in zip(w["coef"], z))
    assert volmodel.probability_wide(bars, i) == pytest.approx(
        1 / (1 + math.exp(-s)), abs=1e-12)


def test_weights_file_is_complete_and_self_describing():
    w = volmodel.weights()
    for k in ("mu", "sd", "coef", "intercept", "range_coef",
              "range_intercept", "median_abs_ret_pct", "trained_through",
              "windows", "oos"):
        assert k in w, f"weights file is missing {k}"
    n = len(volmodel.WINDOWS)
    assert len(w["mu"]) == len(w["sd"]) == len(w["coef"]) == n
    assert tuple(w["windows"]) == volmodel.WINDOWS
    assert 0 < w["median_abs_ret_pct"] < 5


def test_no_astro_feature_reached_the_model():
    """The astro block measured -5pp on this target; it must not be here."""
    w = volmodel.weights()
    blob = json.dumps(w).lower()
    for word in ("thithi", "yogam", "karanam", "nakshatra", "rahu",
                 "paksha", "lagna"):
        assert word not in blob


# --------------------------------------------------------------- output
def test_higher_recent_range_raises_the_probability():
    calm = _bars(100, rng=0.3)
    wild = _bars(100, rng=3.0)
    assert volmodel.probability_wide(wild, 90) > \
        volmodel.probability_wide(calm, 90)


def test_band_labels_are_ordered():
    assert volmodel.band(0.9) == "wide"
    assert volmodel.band(0.60) == "leaning wide"
    assert volmodel.band(0.50) == "typical"
    assert volmodel.band(0.40) == "leaning narrow"
    assert volmodel.band(0.1) == "narrow"


def test_forecast_shape_and_disclaimer():
    bars = _bars(100, rng=1.2)
    f = volmodel.forecast(bars)
    assert 0.0 <= f["p_wide"] <= 1.0
    assert f["expected_range_points"] >= 0
    assert f["band"] in ("wide", "leaning wide", "typical",
                         "leaning narrow", "narrow")
    # the number is easy to over-read; the disclaimer travels with it
    assert "direction" in f["note"].lower()
    assert "not a trading signal" in f["note"].lower()


def test_forecast_needs_prior_history():
    with pytest.raises(ValueError):
        volmodel.forecast(_bars(1))


def test_missing_high_low_does_not_crash():
    bars = _bars(80)
    for b in bars[:10]:
        b["high"] = None
        b["low"] = None
    assert 0.0 <= volmodel.probability_wide(bars, 70) <= 1.0


# ----------------------------------------------------------- band forecast
def test_interval_widens_with_confidence():
    bars = _bars(100, rng=1.2)
    w = [volmodel.interval(bars, 90, c)["half_width_pct"]
         for c in (0.80, 0.90, 0.95)]
    assert w[0] < w[1] < w[2]


def test_interval_adapts_to_recent_volatility():
    """The whole justification for the band: it must tighten when recent
    sessions were calm and widen when they were wild. A band that does
    not do this is just a constant."""
    calm = volmodel.interval(_bars(100, rng=0.3), 90)["half_width_pct"]
    wild = volmodel.interval(_bars(100, rng=3.0), 90)["half_width_pct"]
    assert wild > calm * 1.5, \
        f"band barely adapts: calm ±{calm:.3f}% vs wild ±{wild:.3f}%"


def test_interval_is_symmetric_around_the_reference_close():
    bars = _bars(100, rng=1.0)
    iv = volmodel.interval(bars, 90)
    mid = (iv["low"] + iv["high"]) / 2
    assert mid == pytest.approx(iv["reference_close"], rel=1e-6)
    assert iv["low"] < iv["reference_close"] < iv["high"]


def test_interval_reports_realised_not_just_target_coverage():
    """The stated confidence is a target; what it actually achieved
    out-of-sample is the number a reader should act on, so it travels
    with every band."""
    iv = volmodel.interval(_bars(100, rng=1.0), 90, 0.90)
    assert iv["realised_coverage"] is not None
    assert 80.0 < iv["realised_coverage"] < 99.0
    assert iv["confidence"] == 0.90


def test_interval_rejects_a_confidence_it_was_not_calibrated_for():
    with pytest.raises(ValueError):
        volmodel.interval(_bars(100), 90, 0.99)


def test_interval_disowns_direction():
    iv = volmodel.interval(_bars(100, rng=1.0), 90)
    assert "direction" in iv["note"].lower()
    assert "not a trading signal" in iv["note"].lower()


def test_forecast_carries_the_band():
    f = volmodel.forecast(_bars(100, rng=1.0))
    assert f["band90"]["confidence"] == 0.90
    assert f["band90"]["half_width_points"] > 0


@pytest.mark.skipif(
    not os.path.exists(os.path.join(
        os.path.dirname(__file__), "..", "knowledge", "backtest", "opt",
        "cache", "nifty_2011-01-01_2026-08-13.csv")),
    reason="price cache not present")
def test_on_real_bars_the_model_is_not_degenerate():
    """Against the real series it must actually discriminate, not just
    emit one constant probability."""
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..",
                                    "scripts", "opt"))
    import prices

    bars = prices.load("nifty")
    ps = [volmodel.probability_wide(bars, i)
          for i in range(200, len(bars), 25)]
    assert min(ps) < 0.45 and max(ps) > 0.55, \
        "model emits a near-constant probability"
