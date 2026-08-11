"""Tests for rules/weekly.py and the Sun-nakshatra window.

The window test uses the teacher's own example month (a February): the Sun
sits in Dhanishta (Mars's star) from ~Feb 5–7 to ~Feb 18–20, then enters
Shatabhisha (Rahu's star) — "on 20th, Ragh is coming" [W @ 05:28]. Solar
dates drift by at most ~a day between years, so the bounds are loose.
"""
from app import engine, predict, transit
from app.rules import weekly


def test_degree_house():
    from app.rules.graph import degree_house
    assert degree_house(294.0, 294.0) == 1
    assert degree_house(294.0, 323.9) == 1     # within 30°
    assert degree_house(294.0, 324.1) == 2     # just past 30°
    assert degree_house(294.0, 264.5) == 12    # 29.5° behind → 12th
    # [W @ 04:06] "Sun is in 24 degree… then it is the second house":
    # anchor 18°, planet ~54° → house 2
    assert degree_house(18.0, 54.0) == 2


def test_sun_nak_window_teacher_example():
    w = transit.sun_nak_window(2022, 2, 10, 5.5)
    assert w["nak"] == "Dhanishta"
    assert w["lord"] == "Mars"
    assert w["next_lord"] == "Rahu"
    assert w["start"].startswith("2022-02-0")          # Feb 4–7
    assert w["end"] in ("2022-02-18", "2022-02-19", "2022-02-20")
    assert w["start"] < w["mid"] < w["end"]


def test_window_is_consistent_across_the_period():
    # any date inside the window must return the same window
    a = transit.sun_nak_window(2022, 2, 8, 5.5)
    b = transit.sun_nak_window(2022, 2, 16, 5.5)
    assert a == b


def test_weekly_findings_shape():
    chart = engine.compute(2022, 2, 10, 9, 15, 5.5, 13.0827, 80.2707)
    findings = weekly.rules(chart)
    sections = {f.section for f in findings}
    assert "weekly" in sections and "monthly" in sections
    titles = " ".join(f.title for f in findings)
    assert "Window: Sun in Dhanishta" in titles
    assert "First half" in titles and "Second half" in titles
    assert "prasanam" in titles.lower()
    assert all(f.source for f in findings)


def test_prediction_includes_weekly_sections():
    chart = engine.compute(2022, 2, 10, 9, 15, 5.5, 13.0827, 80.2707)
    pred = predict.run(chart)
    assert pred["status"] == "v1"
    assert pred["sections"]["graph"]
    assert pred["sections"]["weekly"]
    assert pred["sections"]["monthly"]
