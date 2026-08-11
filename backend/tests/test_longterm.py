"""Tests for rules/longterm.py and the Jupiter-nakshatra window.

The window test reproduces the teacher's own Class 11 example: in July 2021
Jupiter slid RETROGRADE into Dhanishta (Mars's star) around July 22 and the
teacher confirms the star holds "for the next 6 months". Date bounds are
loose to absorb ayanamsa/ephemeris differences.
"""
from app import engine, predict, transit
from app.rules import longterm


def test_jupiter_window_teacher_example():
    w = transit.jupiter_nak_window(2021, 8, 15, 5.5)
    assert w["nak"] == "Dhanishta"
    assert w["lord"] == "Mars"
    # retro ingress around 2021-07-22
    assert "2021-07-15" <= w["start"] <= "2021-07-31"
    # direct exit around the new year (teacher's "6 months" is approximate)
    assert "2021-12-20" <= w["end"] <= "2022-02-15"
    assert w["days"] > 140


def test_longterm_chain_teacher_example():
    # Jupiter in Dhanishta → X = Mars, exactly as the teacher reads it
    chart = engine.compute(2021, 8, 15, 9, 15, 5.5, 13.0827, 80.2707)
    p = longterm.pick_chain(chart, "Jupiter")
    assert p["x"] == "Mars"


def test_longterm_findings_shape():
    chart = engine.compute(2021, 8, 15, 9, 15, 5.5, 13.0827, 80.2707)
    findings = longterm.rules(chart)
    assert all(f.section == "long_term" for f in findings)
    titles = " ".join(f.title for f in findings)
    assert "Window: Jupiter in Dhanishta" in titles
    assert "First half" in titles and "Second half" in titles
    assert "checklist" in titles.lower()


def test_prediction_has_all_sections():
    chart = engine.compute(2021, 8, 15, 9, 15, 5.5, 13.0827, 80.2707)
    pred = predict.run(chart)
    for section in ("graph", "weekly", "monthly", "long_term"):
        assert pred["sections"][section], section
