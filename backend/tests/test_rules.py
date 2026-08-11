"""Tests for rules/graph.py â€” the intraday X/Y/X1/Y1 method.

The bias-table cases marked [C5] reproduce judgements the teacher makes
explicitly in the Class 5 video; the fixture-1 chain values were derived by
hand from the engine's validated longitudes and the Vimshottari star table.
"""
from app import engine, predict
from app.rules import graph


def chart_fixture1():
    return engine.compute(1990, 1, 1, 12, 0, 5.5, 13.0827, 80.2707)


def test_bias_table():
    # [C5 @ 05:27] Jupiter at count 1 â†’ bullish
    assert graph.bias(1, "Jupiter", False)[0] == "bullish"
    # [C5 @ 05:35] Rahu at count 4 â†’ sideways
    assert graph.bias(4, "Rahu", False)[0] == "sideways"
    # [C5 @ 10:41] count 9 â†’ angle
    assert graph.bias(9, "Jupiter", False)[0] == "angle"
    # [C6-Buzz] bearish planet at bullish count 10 → upside-wise
    assert graph.bias(10, "Saturn", False)[0] == "sideways-bullish"
    # [NOTES] à®…à®ªà®œà¯†à®¯ house with a bearish planet â†’ bearish
    assert graph.bias(12, "Saturn", False)[0] == "bearish"
    # [NOTES] retro planet counts as bearish: retro Mercury at count 10
    assert graph.bias(10, "Mercury", True)[0] == "sideways-bullish"
    # [C4 @ 07:54] sideways planet on a median-loss count â†’ drift down
    assert graph.bias(12, "Sun", False)[0] == "sideways-bearish"
    # [S3 Sun(10)] sideways planet on a bullish count
    assert graph.bias(10, "Mercury", False)[0] == "sideways-bullish"
    # Rahu keeps its bullish nature (exempt from retroâ†’bearish) but its
    # permanent retro softens outcomes: [S2] count 3 â†’ sideways-bullish,
    # and at median-loss 12 â†’ sideways-bearish
    assert graph.planet_nature("Rahu", True) == "bullish"
    assert graph.bias(3, "Rahu", True)[0] == "sideways-bullish"
    assert graph.bias(12, "Rahu", True)[0] == "sideways-bearish"
    # [S1 Venus(8)] the heavy-loss house dominates any planet
    assert graph.bias(8, "Venus", False)[0] == "bearish"


def test_nak_lord_cycle():
    assert graph.nak_lord_of(0.0) == "Ketu"          # Ashwini
    assert graph.nak_lord_of(306.0) == "Mars"        # Dhanishta
    assert graph.nak_lord_of(307.0) == "Rahu"        # Shatabhisha


def test_degree_house():
    # [C4 @ 05:23] Moon 29Â° in its sign, Sun 27Â° in the previous... same
    # sign region â€” 2Â° behind the Moon is the 12th degree-house
    assert graph.degree_house(29.0, 27.0) == 12
    assert graph.degree_house(29.0, 29.0) == 1
    assert graph.degree_house(29.0, 58.9) == 1     # "29* to next 29* - 1 house"
    assert graph.degree_house(29.0, 59.1) == 2


def make_chart(lons: dict, retro=("Rahu", "Ketu")) -> dict:
    """Synthetic engine-output chart for rule tests."""
    grahas = [{"name": n, "lon": lon, "sign": int(lon // 30),
               "retro": n in retro} for n, lon in lons.items()]
    return {"grahas": grahas}


def test_class4_full_day_example():
    # [C4] Moon 29Â° Krittika region... Moon at 29.0 (Krittika, lord Sun),
    # Sun at 27.0 (also Krittika â€” its own star), nothing else in Sun's
    # stars â†’ X=Y=Sun, both count 12 â†’ full-day sideways-bearish
    chart = make_chart({
        "Sun": 27.0, "Moon": 29.0, "Mars": 100.0, "Mercury": 50.0,
        "Jupiter": 200.0, "Venus": 130.0, "Saturn": 310.0,
        "Rahu": 220.0, "Ketu": 45.0,
    })
    p = graph._pick(chart)
    assert p["x"] == "Sun" and p["y"] == "Sun"
    assert p["x1"] is None and p["y1"] is None
    assert p["first_count"] == 12 and p["second_count"] == 12

    findings = graph.rules(chart)
    titles = " ".join(f.title for f in findings)
    assert "Full-day market: SIDEWAYS-BEARISH" in titles


def test_fixture1_chain():
    # Moon 306.465 â†’ Dhanishta â†’ X = Mars
    # Mars 226.118 â†’ Anuradha (Saturn's star) â†’ Y = Saturn
    # Rahu 294.726 sits in Dhanishta (Mars's star) â†’ X1 = Rahu
    # Mars defines Y so it is excluded from Y-occupants â†’ Y1 = none
    p = graph._pick(chart_fixture1())
    assert p["x"] == "Mars"
    assert p["y"] == "Saturn"
    assert p["x1"] == "Rahu"
    assert p["y1"] is None
    assert p["first"] == "Rahu" and p["second"] == "Saturn"
    # Rahu is an occupant â†’ reverse count (306.465-294.726 â†’ 1);
    # Saturn is the bare Y â†’ forward count from the Moon â†’ 11
    assert p["first_count"] == 1
    assert p["second_count"] == 11


def test_findings_and_prediction_shape():
    chart = chart_fixture1()
    findings = graph.rules(chart)
    assert all(f.section == "graph" for f in findings)
    assert all(f.source for f in findings)
    titles = " ".join(f.title for f in findings)
    assert "09:15" in titles and "15:30" in titles

    pred = predict.run(chart)
    assert pred["status"] == "v1"
    assert pred["sections"]["graph"]
    assert pred["note"]



def test_nakshatra_lords_match_course_chart():
    """The Kaala Purusha Chakram sheet prints each lord's three stars;
    the engine derives them from the Vimshottari cycle. They must agree
    for all 27 — this validates every star-lord the app ever reports."""
    from app.names import NAKSHATRAS
    from app.rules.reference import NAKSHATRAS_BY_LORD

    derived = {}
    for i, name in enumerate(NAKSHATRAS):
        lord = graph.NAK_LORDS[i % 9]
        derived.setdefault(lord, []).append(name)

    assert derived == NAKSHATRAS_BY_LORD
    assert sum(len(v) for v in derived.values()) == 27
    # spot-checks straight off the sheet
    assert graph.nak_lord_of(0.0) == "Ketu"            # Ashwini
    assert graph.nak_lord_of(26.7) == "Sun"            # Krittika
    assert graph.nak_lord_of(359.0) == "Mercury"       # Revati


def test_rasi_attributes_table():
    from app.rules.reference import RASI_ATTRS
    assert len(RASI_ATTRS) == 12
    assert RASI_ATTRS[0] == ("Mars", "movable", "fire", "east", "male")
    assert RASI_ATTRS[9][0] == "Saturn"                # Makara
    # the four elements repeat in order across the wheel
    assert [a[2] for a in RASI_ATTRS[:4]] == ["fire", "earth", "air", "water"]
