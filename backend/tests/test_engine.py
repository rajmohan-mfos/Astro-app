"""Validation fixtures from SPEC Section 5.7.

Longitudes within 0.02°; ayanamsa exact to 3 dp; panchang numbers and
vaara exact. Case 4 (03:15 IST) guards the civil-date vaara rule of §5.5.
"""
import pytest

from app import engine

# (year, month, day, hour, minute, lat, lon,
#  ayanamsa, lagna_lon, vaara, thithi, nak, pada, yoga, karana)
FIXTURES = [
    (1990, 1, 1, 12, 0, 13.0827, 80.2707,
     23.7174, 346.468, "Monday", 5, 23, 4, 16, 9),
    (1985, 6, 15, 7, 30, 13.0827, 80.2707,
     23.6539, 83.918, "Saturday", 27, 2, 3, 7, 54),
    (2001, 11, 23, 18, 45, 12.9716, 77.5946,
     23.8836, 51.791, "Friday", 9, 24, 3, 13, 17),
    (1975, 3, 9, 3, 15, 19.0760, 72.8777,
     23.5104, 262.013, "Sunday", 27, 21, 4, 19, 53),
]

CASE1_GRAHAS = {"Sun": 256.860, "Moon": 306.465, "Mars": 226.118,
                "Mercury": 272.014, "Jupiter": 71.459, "Venus": 282.530,
                "Saturn": 261.910, "Rahu": 294.726, "Ketu": 114.726}


def angle_diff(a: float, b: float) -> float:
    return abs((a - b + 180) % 360 - 180)


@pytest.mark.parametrize(
    "year,month,day,hour,minute,lat,lon,ayanamsa,lagna,vaara,thithi,nak,pada,yoga,karana",
    FIXTURES)
def test_fixture(year, month, day, hour, minute, lat, lon,
                 ayanamsa, lagna, vaara, thithi, nak, pada, yoga, karana):
    r = engine.compute(year, month, day, hour, minute, 5.5, lat, lon)

    assert round(r["ayanamsa"], 3) == round(ayanamsa, 3)
    assert angle_diff(r["lagna"]["lon"], lagna) < 0.02

    pan = r["panchang"]
    assert pan["vaara"]["en"] == vaara
    assert pan["thithi"]["num"] == thithi
    assert pan["natchathiram"]["num"] == nak
    assert pan["natchathiram"]["pada"] == pada
    assert pan["yogam"]["num"] == yoga
    assert pan["karanam"]["num"] == karana


def test_case1_graha_longitudes():
    r = engine.compute(1990, 1, 1, 12, 0, 5.5, 13.0827, 80.2707)
    lons = {g["name"]: g["lon"] for g in r["grahas"]}
    for name, expected in CASE1_GRAHAS.items():
        assert angle_diff(lons[name], expected) < 0.02, name


def test_case1_response_shape():
    r = engine.compute(1990, 1, 1, 12, 0, 5.5, 13.0827, 80.2707)

    assert r["lagna"]["rasi"] == "Meena"
    assert r["lagna"]["deg_in_sign"] == "16°28'"
    assert [g["name"] for g in r["grahas"]] == [
        "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn",
        "Rahu", "Ketu"]

    # Rahu/Ketu always retrograde; Sun/Moon never
    retro = {g["name"]: g["retro"] for g in r["grahas"]}
    assert retro["Rahu"] and retro["Ketu"]
    assert not retro["Sun"] and not retro["Moon"]

    # chart grid: 12 cells, La in the lagna sign, every graha token placed once
    assert len(r["chart"]) == 12
    assert "La" in r["chart"][r["lagna"]["sign"]]
    tokens = [t for cell in r["chart"] for t in cell]
    assert len(tokens) == 10  # La + 9 grahas
    assert "Ra(R)" in tokens and "Ke(R)" in tokens

    pan = r["panchang"]
    assert pan["thithi"]["name"] == "Panchami"
    assert pan["thithi"]["paksha"] == "Shukla"
    assert pan["natchathiram"]["name"] == "Dhanishta"
    assert pan["yogam"]["name"] == "Siddhi"
    assert pan["karanam"]["name"] == "Bava"


def test_invalid_date_raises():
    with pytest.raises(ValueError):
        engine.compute(1990, 2, 30, 12, 0, 5.5, 13.0827, 80.2707)
