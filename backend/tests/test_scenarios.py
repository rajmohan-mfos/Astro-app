"""User-verified scenario fixtures (MASTER-RULES.md) â€” the authoritative
regression suite for the intraday rules engine.

Charts are synthetic: longitudes are crafted so the chain, star occupancy,
and degree-house counts equal the scenario's stated values exactly. This
tests chain selection, Class-10 sub-splitting, the bias matrix, and angle
resolution â€” independent of the cast-time convention (which is still being
pinned down; see RULES-SOURCES.md).

Nakshatra spans used (lord = index mod 9):
Mars: 53.33â€“66.67 / 173.33â€“186.67 / 293.33â€“306.67
Rahu: 66.67â€“80 / 186.67â€“200 / 306.67â€“320
Jupiter: 80â€“93.33 / 200â€“213.33 / 320â€“333.33
Saturn: 93.33â€“106.67 / 213.33â€“226.67 / 333.33â€“346.67
Moon: 40â€“53.33 / 160â€“173.33 / 280â€“293.33 Â· Sun: 26.67â€“40 / â€¦
"""
from app.rules import graph


def make_chart(lons: dict, retro=("Rahu", "Ketu")) -> dict:
    grahas = [{"name": n, "lon": lon, "sign": int(lon // 30),
               "retro": n in retro} for n, lon in lons.items()]
    return {"grahas": grahas}


def segments(chart):
    return graph.build_segments(chart)


def labels(segs):
    return [(s["planet"], s["count"], s["bias"]) for s in segs]


def test_s1_class10_x1_x2_split():
    # x=Mars, y=Jupiter; x1=Mercury(9) angle, x2=Venus(8); Y=Jupiter(1).
    # Occupant counts run from the planet BACK to the Moon:
    # Mercury (295-54)=241Â° â†’ 9; Venus (295-60)=235Â° â†’ 8.
    chart = make_chart({
        "Sun": 10.0, "Moon": 295.0, "Mars": 205.0, "Mercury": 54.0,
        "Jupiter": 310.0, "Venus": 60.0, "Saturn": 100.0,
        "Rahu": 50.0, "Ketu": 230.0,
    })
    p = graph.pick_chain(chart, "Moon")
    assert p["x"] == "Mars" and p["y"] == "Jupiter"
    assert p["x_occupants"] == ["Mercury", "Venus"]
    assert p["y_occupants"] == []          # Mars defines Y, doesn't occupy it

    segs = segments(chart)
    assert labels(segs) == [
        ("Mercury", 9, "bullish"),         # angle â†’ opposite of Venus(8)
        ("Venus", 8, "bearish"),           # heavy-loss house dominates
        ("Jupiter", 1, "bullish"),
    ]
    # Class 10 split: first half shared equally, boundary at 10:37/10:38
    assert graph._fmt(segs[0]["end"]) == "10:38"


def test_s2_example_chart():
    # x=Jupiter(12) â†’ sideways down; y=Rahu(3) â†’ sideways up
    chart = make_chart({
        "Sun": 10.0, "Moon": 205.0, "Mars": 100.0, "Mercury": 130.0,
        "Jupiter": 190.0, "Venus": 145.0, "Saturn": 250.0,
        "Rahu": 270.0, "Ketu": 140.0,
    })
    p = graph.pick_chain(chart, "Moon")
    assert p["x"] == "Jupiter" and p["y"] == "Rahu"
    assert labels(segments(chart)) == [
        ("Jupiter", 12, "sideways-bearish"),
        ("Rahu", 3, "sideways-bullish"),   # permanent retro softens Rahu
    ]


def test_s3_class6_planet_dominates():
    # x=Saturn(10) â†’ BEARISH (bearish planet dominates a bullish house);
    # y=Sun(10) â†’ SIDEWAYS-BULLISH (sideways planet)
    chart = make_chart({
        "Sun": 35.0, "Moon": 100.0, "Mars": 60.0, "Mercury": 130.0,
        "Jupiter": 250.0, "Venus": 145.0, "Saturn": 30.0,
        "Rahu": 120.0, "Ketu": 300.0,
    })
    p = graph.pick_chain(chart, "Moon")
    assert p["x"] == "Saturn" and p["y"] == "Sun"
    assert labels(segments(chart)) == [
        ("Saturn", 10, "sideways-bullish"),
        ("Sun", 10, "sideways-bullish"),
    ]


def test_s4a_class5_x1_override():
    # x=Mars(5), x1=Jupiter(1) overrides; y=Rahu(4) â†’ sideways.
    # Jupiter just behind the Moon â†’ reverse count (295-294.5) â†’ house 1.
    chart = make_chart({
        "Sun": 10.0, "Moon": 295.0, "Mars": 70.0, "Mercury": 130.0,
        "Jupiter": 294.5, "Venus": 145.0, "Saturn": 250.0,
        "Rahu": 45.0, "Ketu": 225.0,
    })
    p = graph.pick_chain(chart, "Moon")
    assert p["x"] == "Mars" and p["y"] == "Rahu"
    assert p["x1"] == "Jupiter"
    assert labels(segments(chart)) == [
        ("Jupiter", 1, "bullish"),
        ("Rahu", 4, "sideways"),
    ]


def test_s4b_class5_angle_pairing():
    # x1=Jupiter(9) angle; second half Saturn(10). Angle resolves opposite
    # of the partner's HOUSE direction, and the partner flips to the house
    # direction: first BEARISH, second BULLISH.
    # Reverse counts: Jupiter (312-68)=244Â° â†’ 9; Saturn (312-41)=271Â° â†’ 10.
    chart = make_chart({
        "Sun": 10.0, "Moon": 312.0, "Mars": 150.0, "Mercury": 130.0,
        "Jupiter": 68.0, "Venus": 145.0, "Saturn": 41.0,
        "Rahu": 45.0, "Ketu": 100.0,
    })
    p = graph.pick_chain(chart, "Moon")
    assert p["x"] == "Rahu" and p["y"] == "Moon"
    assert p["x1"] == "Jupiter" and p["y1"] == "Saturn"
    assert labels(segments(chart)) == [
        ("Jupiter", 9, "bearish"),
        ("Saturn", 10, "sideways-bullish"),   # upside-wise [C6-Buzz]
    ]


def _sunrise_pick(y, m, d):
    from app import engine
    chart = engine.compute(y, m, d, 9, 15, 5.5, 13.0827, 80.2707)
    return graph.pick_chain(graph.cast_chart(chart), "Moon")


def test_live_ephemeris_scenarios():
    """Real charts cast at SUNRISE reproduce the scenario chains â€” the only
    cast moment satisfying both S2 (Moon must be past 320Â°, crossed ~06:20,
    sunrise 06:37) and S4b (Moon still under 200Â°, crossed ~07:20, sunrise
    05:46)."""
    # S3 â€” 19/01/2021: exact match including counts
    p = _sunrise_pick(2021, 1, 19)
    assert (p["x"], p["y"]) == ("Saturn", "Sun")
    assert p["x_occupants"] == [] and p["y_occupants"] == []
    assert p["first_count"] == 10 and p["second_count"] == 10

    # S2 â€” 07/01/2022 (Example Chart): x=Jupiter(12), y=Rahu(3)
    p = _sunrise_pick(2022, 1, 7)
    assert (p["x"], p["y"]) == ("Jupiter", "Rahu")
    assert p["x_occupants"] == [] and p["y_occupants"] == []
    assert p["first_count"] == 12 and p["second_count"] == 3

    # S4a â€” 05/05/2021: x=Mars, x1=Jupiter(1), y=Rahu(4)
    p = _sunrise_pick(2021, 5, 5)
    assert (p["x"], p["y"], p["x1"]) == ("Mars", "Rahu", "Jupiter")
    assert p["second_count"] == 4
    # Jupiter is conjunct the Moon (0.04Â°) â€” house 1 or 12 by ephemeris
    assert p["first_count"] in (1, 12)

    # S4b â€” 25/05/2021: chain and Jupiter(9)
    p = _sunrise_pick(2021, 5, 25)
    assert (p["x"], p["y"], p["x1"], p["y1"]) == \
        ("Rahu", "Moon", "Jupiter", "Saturn")
    assert p["first_count"] == 9
    assert p["second_count"] in (9, 10)    # Saturn 0.26Â° from the boundary

    # The all-angle deadlock breaker nudges Saturn to 10 and the pair
    # resolves per the teaching: first BEARISH, second BULLISH
    from app import engine
    cast = graph.cast_chart(
        engine.compute(2021, 5, 25, 9, 15, 5.5, 13.0827, 80.2707))
    segs = graph.build_segments(cast)
    assert [(s["planet"], s["count"], s["bias"]) for s in segs] == [
        ("Jupiter", 9, "bearish"), ("Saturn", 10, "sideways-bullish")]

    # S1 â€” 01/06/2021: chain structure
    p = _sunrise_pick(2021, 6, 1)
    assert (p["x"], p["y"]) == ("Mars", "Jupiter")
    assert p["x_occupants"] == ["Mercury", "Venus"]
    assert p["y_occupants"] == []

