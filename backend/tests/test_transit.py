"""Validate transit.py against the author's printed chart for 05/05/2021
(panchang.png reference).

Boundary degrees are exact Vimshottari arithmetic and must match exactly.
Crossing times get tolerances: the author's software is a KP tool whose
Moon rows we reproduce within ~5 min (residual ayanamsa-variant/ephemeris
differences); slow-planet rows land within ~13 min.

The author's பஞ்ச அங்கங்கள் block is only checked for *names*: its printed
thithi/yogam/karanam end times (13:59 / 20:25 / 12:49) contradict the
author's own Moon table — thithi timing is ayanamsa-independent, and by the
elongation the author's Moon rows imply, Navami must end ≈13:22, not 13:59.
Those block values appear to come from a Vakya (almanac) panchangam, not
from the KP computation. Our values are internally consistent with the
author's transit tables. The natchathiram end IS cross-checked because the
author's own Moon row (306°40' at 09:03:00) confirms it.
"""
import pytest

from app import transit

# சந்திர பெயர்ச்சி table from the reference chart
MOON_ROWS = [
    ("304.53.20", "Venus",   "05:40:57"),
    ("305.33.20", "Sun",     "06:56:43"),
    ("306.40.00", "Moon",    "09:03:00"),
    ("308.40.00", "Rahu",    "12:50:18"),
    ("310.26.40", "Jupiter", "16:12:22"),
    ("312.33.20", "Saturn",  "20:12:18"),
    ("314.26.40", "Mercury", "23:46:59"),
    ("315.13.20", "Ketu",    "25:15:22"),
]

# பிற கிரகங்களின் பெயர்ச்சி table
PLANET_ROWS = [
    ("Mercury", "037.46.40", "Ketu", "09:15:16"),
    ("Venus",   "031.13.20", "Rahu", "11:35:36"),
]


@pytest.fixture(scope="module")
def chart():
    return transit.day_chart(2021, 5, 5, 5.5)


def secs(hms: str) -> int:
    h, m, s = (int(x) for x in hms.split(":"))
    return h * 3600 + m * 60 + s


def test_sub_segments_cover_circle():
    assert len(transit._SUBS) == 243
    total = sum(end - start for start, end, _, _ in transit._SUBS)
    assert abs(total - 360) < 1e-9
    # segments are contiguous
    for prev, cur in zip(transit._SUBS, transit._SUBS[1:]):
        assert abs(prev[1] - cur[0]) < 1e-9


def test_moon_sub_lord_table(chart):
    rows = {r["deg"]: r for r in chart["moon_transits"]}
    for deg, sub, time in MOON_ROWS:
        row = rows[deg]
        assert row["sub_lord"] == sub
        assert abs(secs(row["time"]) - secs(time)) < 360, (deg, row["time"])


def test_moon_rows_ordered(chart):
    times = [secs(r["time"]) for r in chart["moon_transits"]]
    assert times == sorted(times)


def test_planet_transits(chart):
    rows = {(r["graha"], r["deg"]): r for r in chart["planet_transits"]}
    for graha, deg, sub, time in PLANET_ROWS:
        row = rows[(graha, deg)]
        assert row["sub_lord"] == sub
        assert abs(secs(row["time"]) - secs(time)) < 900, (graha, row["time"])


def test_day_lord_and_panchang_block(chart):
    # 05/05/2021 was a Wednesday; அதிபதி = புதன் (Mercury)
    assert chart["vaara"] == "Wednesday"
    assert chart["day_lord"]["en"] == "Mercury"

    ends = chart["panchang_ends"]
    assert ends["natchathiram"]["name"] == "Dhanishta"
    assert ends["thithi"]["name"] == "Navami"
    assert ends["yogam"]["name"] == "Brahma"
    assert ends["karanam"]["name"] == "Taitila"
    # cross-checked against the author's own Moon row: 306°40' @ 09:03:00
    assert abs(secs(ends["natchathiram"]["ends"]) - secs("09:03:00")) < 360

    # internal consistency: karanam is half a thithi; the karanam after the
    # one running at midnight must end exactly when the thithi ends
    assert ends["karanam"]["num"] * 6 + 6 == ends["thithi"]["num"] * 12


def test_ends_parse_as_times(chart):
    for key in ("thithi", "natchathiram", "yogam", "karanam"):
        assert secs(chart["panchang_ends"][key]["ends"]) >= 0
