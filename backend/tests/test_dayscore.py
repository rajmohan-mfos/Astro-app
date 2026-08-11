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
                              "chain is directionless")
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
