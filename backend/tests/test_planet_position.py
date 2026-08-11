"""Validate the KP planet-position sheet against the author's printed
chart for 06-01-2022 09:00 (planets degree.png reference).

Author's rows: Sun 261:37:26 (12, Jup/Ven/Jup), Moo 307:44:46 (01,
Sat/Rah/Rah), Mar 232:36:48 (10, Mar/Mer/Moo), Mer 280:44:11 (12,
Sat/Moo/Moo), Jup 307:25:08 (01, Sat/Rah/Rah), Ven# 266:19:09 (12,
Jup/Ven/Ket), Sat 288:18:55 (12, Sat/Moo/Mer), Rah 035:06:19 (04,
Ven/Sun/Sat), Ket 215:06:19 (10, Mar/Sat/Sat). Chain: "Star lord of Moon
is Rah / Star lord of Rah is Sun"; Day Lord Jupiter.

The author's exact location is unknown (Chennai assumed), so degrees get a
0.15° tolerance and only planets sitting safely inside a house get exact
house asserts; near-cusp planets are allowed one house of slack.
"""
import pytest

from app import transit

AUTHOR = {
    "Sun": (261 + 37 / 60 + 26 / 3600, {11, 12}, "Jup", "Ven"),
    "Moo": (307 + 44 / 60 + 46 / 3600, {1}, "Sat", "Rah"),
    "Mar": (232 + 36 / 60 + 48 / 3600, {10}, "Mar", "Mer"),
    "Mer": (280 + 44 / 60 + 11 / 3600, {11, 12}, "Sat", "Moo"),
    "Jup": (307 + 25 / 60 + 8 / 3600, {1}, "Sat", "Rah"),
    "Ven": (266 + 19 / 60 + 9 / 3600, {11, 12}, "Jup", "Ven"),
    "Sat": (288 + 18 / 60 + 55 / 3600, {11, 12}, "Sat", "Moo"),
    # Rahu sits on the 3rd/4th Placidus cusp — house depends on the exact
    # cast minute/location, so both are accepted
    "Rah": (35 + 6 / 60 + 19 / 3600, {3, 4}, "Ven", "Sun"),
    "Ket": (215 + 6 / 60 + 19 / 3600, {9, 10}, "Mar", "Sat"),
}

LORD_ABBREV = {"Sun": "Sun", "Moon": "Moo", "Mars": "Mar", "Mercury": "Mer",
               "Jupiter": "Jup", "Venus": "Ven", "Saturn": "Sat",
               "Rahu": "Rah", "Ketu": "Ket"}


@pytest.fixture(scope="module")
def sheet():
    return transit.planet_position(2022, 1, 6, 9, 0, 5.5, 13.0827, 80.2707)


def to_deg(dms: str) -> float:
    d, m, s = (int(x) for x in dms.split(":"))
    return d + m / 60 + s / 3600


def test_rows_match_author(sheet):
    rows = {r["planet"]: r for r in sheet["rows"]}
    for name, (deg, houses, sign_l, star_l) in AUTHOR.items():
        r = rows[name]
        assert abs(to_deg(r["deg"]) - deg) < 0.15, (name, r["deg"])
        assert r["house"] in houses, (name, r["house"])
        assert LORD_ABBREV[r["rasi_lord"]] == sign_l, name
        assert LORD_ABBREV[r["nak_lord"]] == star_l, name


def test_venus_marked_retro(sheet):
    rows = {r["planet"]: r for r in sheet["rows"]}
    assert rows["Ven"]["retro"] is True          # author prints "Ven#"
    assert rows["Rah"]["retro"] and rows["Ket"]["retro"]
    assert not rows["Sun"]["retro"]


def test_ruling_chain_and_day_lord(sheet):
    # planet_position's own chain reflects its cast moment (09:00 here) —
    # Moon 307.75 in Shatabhisha, matching the author's 06-01 sheet
    assert sheet["chain"] == {"x": "Rahu", "y": "Sun"}
    assert sheet["day_lord"]["en"] == "Jupiter"   # 06-01-2022 was Thursday


def test_sunrise_ruling_chain_matches_example_video():
    # The author's 07-01-2022 sheet: "Star lord of Moon is Jup / Star lord
    # of Jup is Rah". Our sunrise-cast chain reproduces it (the API always
    # serves this sunrise chain regardless of the displayed time).
    rc = transit.ruling_chain(2022, 1, 7, 5.5, 13.0827, 80.2707)
    assert rc["x"] == "Jupiter" and rc["y"] == "Rahu"
    assert rc["chain_text"] == ["Star lord of Moon is Jupiter",
                                "Star lord of Jupiter is Rahu"]
    assert "sunrise" in rc["cast"]


def test_lagna_row_first(sheet):
    assert sheet["rows"][0]["planet"] == "Lag"
    assert sheet["rows"][0]["house"] == 1
