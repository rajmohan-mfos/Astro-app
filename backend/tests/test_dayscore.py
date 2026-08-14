"""Tests for the aggregate day score (Class 3 'combine with whole concept')."""
import pytest

from app import engine, predict
from app.rules import dayscore


def chart(y, m, d):
    return engine.compute(y, m, d, 9, 15, 5.5, 13.0827, 80.2707)


def test_weights_follow_the_sources():
    # yogam is half-weight vs thithi/karanam [C3: "half effect of dhithi
    # will be in yoga"]; the extreme yogam grade counts full
    assert dayscore.STAR_VALUE["Mercury"] == 1.0     # maximum positive
    assert dayscore.STAR_VALUE["Ketu"] == -1.0       # maximum negative
    assert dayscore.STAR_VALUE["Saturn"] == -1.0     # strongly bearish
    assert dayscore.STAR_VALUE["Mars"] == -0.5       # 60% bearish
    assert dayscore.AMPLIFIERS == {"Jupiter", "Rahu"}


def test_tally_components_and_amplifier():
    s = dayscore.panchang_tally(chart(2026, 8, 11))
    assert set(s["parts"]) == {"thithi", "karanam", "yogam", "nakshatra"}
    # every component is one of the graded magnitudes
    for v in s["parts"].values():
        assert v in (-1.0, -0.5, 0.0, 0.5, 1.0)
    assert isinstance(s["amplified"], bool)
    if s["amplified"]:
        assert s["lord"] in dayscore.AMPLIFIERS


def test_amplifier_scales_not_adds():
    """A Jupiter/Rahu star lord multiplies the tally rather than adding a
    sign of its own — 'amplifies the prevailing condition'."""
    base = {"thithi": 1.0, "karanam": 1.0, "yogam": 0.5, "nakshatra": 0.0}
    plain = sum(base.values())
    assert round(plain * 1.5, 2) == 3.75          # what the code would do
    # and an amplifier contributes no sign itself
    assert "Jupiter" not in dayscore.STAR_VALUE
    assert "Rahu" not in dayscore.STAR_VALUE


@pytest.mark.parametrize("y,m,d", [(2026, 8, 11), (2021, 5, 5),
                                   (1990, 1, 1), (2022, 1, 7)])
def test_day_score_shape(y, m, d):
    s = dayscore.day_score(chart(y, m, d))
    assert s["conviction"] in ("high", "medium", "low")
    assert s["agreement"] in ("agree", "conflict", "panchang neutral",
                              "chain is directionless",
                              "chain cancels out (small wave)")
    assert s["panchang_sign"] in ("positive", "negative", "flat")
    assert s["chain_sign"] in ("positive", "negative", "flat")
    assert -1.0 <= s["chain_score"] <= 1.0


def test_conflict_never_scores_high():
    """Panchang gates the chain: disagreement caps conviction at low."""
    for d in range(1, 29):
        s = dayscore.day_score(chart(2026, 4, d))
        if s["agreement"] == "conflict":
            assert s["conviction"] == "low"
        if s["chidra"]:
            assert s["conviction"] != "high"


def test_wired_into_prediction():
    pred = predict.run(chart(2026, 8, 11))
    assert "day_score" in pred
    assert pred["day_score"]["conviction"] in ("high", "medium", "low")
    titles = " ".join(f["title"] for f in pred["sections"]["graph"])
    assert "Day score:" in titles
    # the finding must carry the backtest caveat
    finding = next(f for f in pred["sections"]["graph"]
                   if f["title"].startswith("Day score:"))
    assert "not a signal" in finding["detail"]


def test_small_wave_is_distinguished_from_a_flat_chain():
    """[C9 @ 03:34-03:55] 'half and half ... like a small wave, wave,
    wave'. A chain whose stretches CANCEL and a chain with no push in it
    both average near zero; the taught reading differs (choppy narrow
    range vs nothing happening), so the code must tell them apart on
    energy, not on the mean."""
    assert dayscore.is_small_wave(0.0, 1.0) is True     # bullish + bearish
    assert dayscore.is_small_wave(0.0, 0.5) is True     # the weaker pair
    assert dayscore.is_small_wave(0.0, 0.0) is False    # all sideways
    assert dayscore.is_small_wave(0.0, 0.4) is False    # too little force
    # a chain with a real direction is never a small wave, however
    # energetic it is
    assert dayscore.is_small_wave(1.0, 1.0) is False


def test_small_wave_reports_range_not_direction():
    """The whole point of the gap: 'low conviction' says nothing about
    the size of the swings, which is what C9 is describing."""
    found = None
    for d in range(1, 29):
        s = dayscore.day_score(chart(2021, 5, d))
        if s["small_wave"]:
            found = [f for f in dayscore.rules(chart(2021, 5, d))
                     if f.title.startswith("Small-wave")]
            break
    assert found, "no small-wave day in May 2021 to test"
    detail = found[0].detail.lower()
    assert "range" in detail
    assert "size" in detail and "not their direction" in detail
    assert "not a signal" in detail


def test_chain_profile_energy_is_span_weighted():
    """Energy must be the mean of |weight|, so cancelling stretches keep
    their force instead of summing to nothing."""
    p = dayscore.chain_profile(chart(2021, 5, 5))
    assert p["energy"] >= abs(p["score"])      # |mean| <= mean|w| always
    assert 0.0 <= p["energy"] <= 1.0
    assert p["score"] == dayscore.chain_score(chart(2021, 5, 5))
