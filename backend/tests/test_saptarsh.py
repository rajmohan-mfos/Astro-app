"""The week-ahead reconstruction is checked against numbers the Saptarsh
Insight channel actually published (Aug 2026 posts), so a drift in
ayanamsa, node type or the kaal arithmetic shows up as a failed test
rather than a silently different outlook."""
import datetime

from app import saptarsh
from app import main


def _mins(hhmm: str) -> int:
    h, m = hhmm.split(" ")[0].split(":")
    return int(h) * 60 + int(m)


def _aspect(d: dict, a: str, angle: int, b: str) -> dict:
    hits = [x for x in d["aspects"]
            if x["a"] == a and x["b"] == b and x["angle"] == angle]
    assert hits, f"{a} {angle} {b} not found on {d['date']}"
    return hits[0]


def test_aspect_times_match_the_channel_27_aug():
    d = saptarsh.day(datetime.date(2026, 8, 27))
    published = [("Sun", 150, "Pluto", "01:41"), ("Moon", 45, "Neptune", "03:11"),
                 ("Moon", 120, "Venus", "03:31"), ("Sun", 150, "Neptune", "06:02"),
                 ("Mercury", 150, "Pluto", "12:13"),
                 ("Mercury", 150, "Neptune", "14:21"),
                 ("Moon", 135, "Mars", "16:00"), ("Moon", 45, "Saturn", "22:31"),
                 ("Sun", 0, "Mercury", "22:35"), ("Moon", 0, "Rahu", "23:41")]
    for a, ang, b, t in published:
        got = _aspect(d, a, ang, b)
        assert abs(_mins(got["time"]) - _mins(t)) <= 3, (a, ang, b, got["time"], t)
        assert got["source"] == "observed"


def test_moon_sign_change_uses_lahiri():
    """Channel: 'Moon in Capricorn till 13:36 IST then enters Aquarius'.
    Under swisseph's default Fagan-Bradley mode this lands at 15:17."""
    d = saptarsh.day(datetime.date(2026, 8, 27))
    assert d["moon"]["sign"] == "Makara"
    assert d["moon"]["nakshatra"] == "Dhanishta"
    assert d["moon"]["sign_change"]["to"] == "Kumbha"
    assert abs(_mins(d["moon"]["sign_change"]["time"]) - _mins("13:36")) <= 8


def test_kaal_windows_thursday_20_aug():
    """Channel panchang for 20 Aug: Rahu 14:20-15:55, Yamaganda
    06:23-07:59, Gulika 09:34-11:09, Abhijit 12:19-13:10. Their sunrise
    is 2 min later than swisseph's upper-limb value, so ±4 min."""
    k = saptarsh.day(datetime.date(2026, 8, 20))["kaal"]
    for got, want in [(k["rahu_kaal"], ("14:20", "15:55")),
                      (k["yamaganda"], ("06:23", "07:59")),
                      (k["gulika_kaal"], ("09:34", "11:09")),
                      (k["abhijit"], ("12:19", "13:10"))]:
        assert abs(_mins(got[0]) - _mins(want[0])) <= 4, (got, want)
        assert abs(_mins(got[1]) - _mins(want[1])) <= 4, (got, want)


def test_28_aug_is_purnima_eclipse_and_bearish_shatabhisha():
    d = saptarsh.day(datetime.date(2026, 8, 28))
    assert d["panchang"]["tithi"].startswith("Pournami")
    assert abs(_mins(d["panchang"]["tithi_ends"]) - _mins("09:49")) <= 3
    assert d["eclipse"] and d["eclipse"].startswith("lunar eclipse")
    assert d["moon"]["nakshatra"] == "Shatabhisha"
    assert d["calls"]["nifty"]["tone"] == "bear"
    assert d["calls"]["nifty"]["source"] == "observed"
    assert d["calls"]["gold"]["tone"] == "bear"
    assert any("Eclipse in Aquarius" in w for w in d["calls"]["silver"]["why"])
    assert "confidence is low" in d["calls"]["nifty"]["text"]


def test_vishti_downgrades_a_bullish_moon():
    d = saptarsh.day(datetime.date(2026, 8, 27))
    assert d["panchang"]["karanas"][0]["name"] == "Vishti"
    assert d["calls"]["nifty"]["tone"] == "vol"
    assert any("Vishti" in w for w in d["calls"]["nifty"]["why"])


def test_moon_exalted_in_taurus_lifts_a_neutral_star():
    """3 Sep 2026: Moon in Vrishabha / Krittika (Sun-lorded, neutral).
    Exaltation lifts it to bullish; Vishti in session then softens the
    bullish call to volatile — the channel's own 27 Aug pattern."""
    d = saptarsh.day(datetime.date(2026, 9, 3))
    assert d["moon"]["sign"] == "Vrishabha"
    assert any("exalted" in w for w in d["calls"]["nifty"]["why"])
    assert d["calls"]["nifty"]["tone"] == "vol"


def test_extrapolated_calls_are_labelled():
    d = saptarsh.day(datetime.date(2026, 9, 3))     # Moon far from Aug stars
    assert all(c["source"] in ("observed", "extrapolated")
               for c in d["calls"].values())
    assert all(a["source"] in ("observed", "extrapolated") for a in d["aspects"])


def test_windows_tile_the_session():
    d = saptarsh.day(datetime.date(2026, 8, 28))
    w = d["windows"]
    assert w[0]["start"] == "09:15" and w[-1]["end"] == "15:30"
    for a, b in zip(w, w[1:]):
        assert a["end"] == b["start"]


def test_week_endpoint():
    # called as a plain function: the repo's test env has no httpx, so
    # no TestClient — the routing itself is FastAPI's job, not ours
    body = main.saptarsh_week(date="2026-08-28", days=7)
    assert body["start"] == "2026-08-28" and body["end"] == "2026-09-03"
    assert len(body["days"]) == 7
    sat = body["days"][1]
    assert sat["weekday"] == "Saturday" and sat["closed"] == "Saturday"
    assert set(body["days"][0]["calls"]) == {"nifty", "gold", "silver"}
    assert len(main.saptarsh_week(days=99)["days"]) == 14      # capped
    assert main.saptarsh_week(date="nope").status_code == 400
