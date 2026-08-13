"""Tests for the data-fitted tables.

These values are tuned on the same 15 years they are scored against, so
the danger is not that they are wrong — it is that the flattering
in-sample number gets read as a forecast. Most of what is pinned here is
therefore about the number never travelling without its companion.
"""
import importlib
import json
import os

import pytest

from app import engine
from app.rules import dayscore

FITTED = os.path.join(os.path.dirname(__file__), "..", "app", "rules",
                      "fitted_tables.json")
needs_fit = pytest.mark.skipif(not os.path.exists(FITTED),
                               reason="tables have not been fitted")


@pytest.fixture
def fitted_mode(monkeypatch):
    monkeypatch.setattr(dayscore, "MODE", "fitted")
    yield


def _chart():
    return engine.compute(2026, 8, 14, 9, 0, 5.5, 19.076, 72.8777)


# ------------------------------------------------- provenance protection
def test_taught_tables_are_untouched_by_fitting():
    """The course's own numbers are the app's provenance. A fitting run
    must never edit them — only add an alternative set."""
    assert dayscore.TAUGHT_STAR_VALUE["Mercury"] == 1.0
    assert dayscore.TAUGHT_STAR_VALUE["Saturn"] == -1.0
    assert dayscore.TAUGHT_STAR_VALUE["Ketu"] == -1.0
    assert dayscore.TAUGHT_CHAIN_WEIGHTS["bullish"] == 1.0
    assert dayscore.TAUGHT_CHAIN_WEIGHTS["bearish"] == -1.0
    # the public names still point at the taught values
    assert dayscore.STAR_VALUE is dayscore.TAUGHT_STAR_VALUE
    assert dayscore.CHAIN_WEIGHTS is dayscore.TAUGHT_CHAIN_WEIGHTS


def test_default_mode_is_taught(monkeypatch):
    """Fitted numbers must be opt-in. A fresh checkout with no environment
    set reproduces the course method, not a curve fit."""
    monkeypatch.delenv("ASTRO_SCORE_MODE", raising=False)
    try:
        mod = importlib.reload(dayscore)
        assert mod.MODE == "taught"
        assert mod.active_mode() == "taught"
    finally:
        importlib.reload(dayscore)


def test_taught_mode_emits_no_fitted_call(monkeypatch):
    monkeypatch.setattr(dayscore, "MODE", "taught")
    s = dayscore.day_score(_chart())
    assert s["mode"] == "taught"
    assert "call" not in s


# ------------------------------------------------------- fitted mechanics
@needs_fit
def test_fitted_tables_cover_the_five_taught_tables():
    f = dayscore.fitted()
    for name in ("star_value", "chain_weights", "thithi", "yogam",
                 "karanam"):
        assert name in f["tables"], f"missing fitted table {name}"
        assert f["tables"][name], f"fitted table {name} is empty"
    assert set(f["component_weights"]) == {
        "star_value", "chain_weights", "thithi", "yogam", "karanam"}
    assert f["threshold"] >= 0


@needs_fit
def test_fitted_score_is_deterministic_and_bounded(fitted_mode):
    c = _chart()
    a, b = dayscore.fitted_score(c), dayscore.fitted_score(c)
    assert a == b
    assert a["call"] in ("up", "down", "no call")
    assert abs(a["total"]) < 50


@needs_fit
def test_fitted_mode_sets_the_call(fitted_mode):
    s = dayscore.day_score(_chart())
    assert s["mode"] == "fitted"
    assert s["call"] in ("up", "down", "no call")
    assert "fitted" in s["call_source"]


@needs_fit
def test_fitted_mode_does_not_overwrite_the_taught_reading(fitted_mode):
    """Both readings must survive side by side — the fit is an addition,
    not a replacement, or the course reading becomes unverifiable."""
    taught = dayscore.day_score(_chart())
    with pytest.MonkeyPatch.context() as m:
        m.setattr(dayscore, "MODE", "taught")
        plain = dayscore.day_score(_chart())
    for k in ("panchang_total", "chain_score", "panchang_sign",
              "chain_sign", "conviction", "agreement", "parts"):
        assert taught[k] == plain[k], f"fitted mode altered {k}"


# --------------------------------------------------- the honesty guards
@needs_fit
def test_in_sample_rate_never_appears_without_out_of_sample(fitted_mode):
    """The one number a reader will latch onto is the in-sample rate.
    It must never be shown alone."""
    s = dayscore.day_score(_chart())
    f = s["fitted"]
    assert "in_sample_rate" in f and "out_of_sample_rate" in f
    finding = dayscore.fitted_finding(s)
    assert str(f["in_sample_rate"]) in finding.detail
    assert str(f["out_of_sample_rate"]) in finding.detail
    assert "not a forecast" in finding.detail.lower()


@needs_fit
def test_the_fit_is_labelled_as_fitted_not_predicted(fitted_mode):
    finding = dayscore.fitted_finding(dayscore.day_score(_chart()))
    text = (finding.title + " " + finding.detail).lower()
    assert "fitted" in text
    assert "same history" in text or "in-sample" in text


@needs_fit
def test_the_stored_warning_states_the_out_of_sample_reality():
    with open(FITTED, encoding="utf-8") as fh:
        payload = json.load(fh)
    assert "not a forecast" in payload["warning"].lower()
    oos = payload["out_of_sample"]
    ins = payload["in_sample"]
    # the whole point: the fit flatters, and the file records by how much
    assert ins["rate"] > oos["rate"], \
        "in-sample should exceed out-of-sample; if not, re-check the fit"


@needs_fit
def test_fitted_engine_does_not_claim_a_significant_edge():
    """A guard against a future re-fit quietly shipping an overstated
    claim: if the out-of-sample edge ever looks large, that is a signal to
    re-examine the method, not to celebrate."""
    payload = dayscore.fitted()
    assert payload["out_of_sample"]["edge_pp"] < 10.0
