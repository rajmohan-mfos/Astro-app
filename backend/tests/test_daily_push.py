"""Tests for the daily Telegram message.

This file exists because its absence hid a real fault: build_message
hand-picks what to show from predict.run's output, so a finding can be
computed correctly and still never reach the reader. The prasanam gate
was computed for a full day before anyone noticed the morning push was
printing "HIGH conviction" without it.

The push is the surface actually read every day, so what it OMITS is as
much a correctness question as what it prints.
"""
import datetime
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from daily_push import LAT, LON, TZ, build_message      # noqa: E402

from app import engine, predict                          # noqa: E402

DAYS = [datetime.date(2026, 8, 15), datetime.date(2026, 8, 18),
        datetime.date(2021, 1, 22), datetime.date(2021, 5, 5)]


def _prediction(d):
    return predict.run(engine.compute(d.year, d.month, d.day, 9, 0,
                                      TZ, LAT, LON))


@pytest.mark.parametrize("d", DAYS)
def test_message_always_carries_the_disclaimer(d):
    m = build_message(d)
    assert "NOT financial advice" in m
    assert "Do not trade this" in m


@pytest.mark.parametrize("d", DAYS)
def test_message_fits_a_telegram_send(d):
    """Telegram rejects messages over 4096 characters outright."""
    assert len(build_message(d)) < 4096


@pytest.mark.parametrize("d", DAYS)
def test_gate_state_reaches_the_reader(d):
    """[P2] the gate qualifies the whole reading, so a push that shows a
    conviction without it misrepresents the method."""
    m = build_message(d)
    gate = _prediction(d)["prasanam_gate"]
    if gate["open"]:
        assert "Prasanam gate open" in m
    else:
        assert "Prasanam gate NOT open" in m
        assert gate["verdict"] in m
        assert "study material, not an entry" in m


@pytest.mark.parametrize("d", DAYS)
def test_gate_appears_above_the_day_score(d):
    """Ordering is the point: a qualifier printed after the thing it
    qualifies has already been read as unqualified."""
    m = build_message(d)
    if "Prasanam gate" in m and "Day score:" in m:
        assert m.index("Prasanam gate") < m.index("Day score:")


@pytest.mark.parametrize("d", DAYS)
def test_gate_reason_is_never_truncated_mid_word(d):
    """The reason is trimmed to its first sentence rather than cut at a
    character count, which used to end lines like '...counts the tra'."""
    for line in build_message(d).splitlines():
        s = line.strip()
        if s.startswith("the ") and s.endswith("."):
            assert not s.endswith(" .")


def test_small_wave_reaches_the_reader_when_it_fires():
    """[C9] the range characterisation is the whole point of gap 4; it
    must not stop at the API boundary."""
    d = datetime.date(2021, 1, 1)
    while d < datetime.date(2021, 4, 1):
        if _prediction(d)["day_score"]["small_wave"]:
            assert "Small-wave day" in build_message(d)
            return
        d += datetime.timedelta(days=1)
    pytest.skip("no small-wave day in the window")


def test_trade_expression_reaches_the_reader_and_stays_disowned():
    """It only fires with the gate open AND agreement, so it is rare -
    and when it does appear it must still say it is not a recommendation.
    """
    d = datetime.date(2021, 1, 1)
    while d < datetime.date(2021, 7, 1):
        p = _prediction(d)
        if any(f["title"].startswith("How the course expresses")
               for f in p["sections"].get("graph", [])):
            m = build_message(d)
            assert "How the course expresses" in m
            assert "NOT a recommendation" in m
            return
        d += datetime.timedelta(days=1)
    pytest.skip("no gate-open agreeing day in the window")
