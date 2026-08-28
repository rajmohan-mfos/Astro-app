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


# ---- second learning pass: the X account (@sonisunil59) ----

def test_vaar_tithi_classical_tables():
    assert saptarsh.vaar_tithi_yoga(4, 1)["names"] == ["Siddha"]      # Fri + Nanda
    assert saptarsh.vaar_tithi_yoga(4, 1)["tone"] == "bull"
    assert saptarsh.vaar_tithi_yoga(6, 4)["names"] == ["Visha"]       # Sun + 4
    assert saptarsh.vaar_tithi_yoga(3, 6)["names"] == ["Dagdha"]      # Thu + 6
    assert saptarsh.vaar_tithi_yoga(6, 16)["names"] == ["Mrityu"]     # Sun + Krishna 1
    assert saptarsh.vaar_tithi_yoga(0, 3) is None                     # Mon + 3


def test_metal_windows_cover_the_globex_day_with_et():
    """The premium report's windows run 03:30 -> 27:30 IST with ET
    alongside; Aug is US daylight time so ET = IST - 9.5 h."""
    d = saptarsh.day(datetime.date(2026, 8, 28))
    w = d["metal_windows"]
    assert w[0]["start"] == "03:30" and w[-1]["end"] == "27:30"
    assert w[0]["start_et"] == "18:00" and w[-1]["end_et"] == "18:00"
    for a, b in zip(w, w[1:]):
        assert a["end"] == b["start"]
        assert a["tone"] != b["tone"]          # neighbours merged


def test_et_conversion_handles_us_dst():
    aug = saptarsh._jd_local(datetime.date(2026, 8, 27), 22 + 35 / 60)
    assert saptarsh._et(aug) == "13:05"                    # EDT, -9.5 h
    jan = saptarsh._jd_local(datetime.date(2026, 1, 15), 22 + 30 / 60)
    assert saptarsh._et(jan) == "12:00"                    # EST, -10.5 h


def test_regime_matches_the_posted_conjunction_calendar():
    """X, 26 Aug: Leo holds Sun, Mercury, Ketu from 22-Aug to 07-Sep;
    Jupiter sits in Cancer (their table: JUP CAN 106.29 on 17 Aug)."""
    r = saptarsh.regime(datetime.date(2026, 8, 28))
    assert r["jupiter"]["sign_en"] == "Cancer"
    assert any("Cancer" in n for n in r["notes"])
    leo = [c for c in r["conjunctions"] if c["sign_en"] == "Leo"]
    assert leo and {"Sun", "Mercury", "Ketu"} <= set(leo[0]["planets"])
    assert leo[0]["until"] in ("2026-09-06", "2026-09-07", "2026-09-08")
    assert r["sun_ketu_same_sign"]
    assert len(r["jupiter_cancer_history"]) == 5


def test_amavasya_is_read_bullish_for_metals():
    d = datetime.date(2026, 8, 28)
    for _ in range(40):
        x = saptarsh.day(d)
        if 30 in x["panchang"]["tithis_in_session"]:
            assert any("Amavasya" in w for w in x["calls"]["gold"]["why"])
            assert x["calls"]["gold"]["tone"] in ("bull", "vol")
            assert not any("Amavasya" in w for w in x["calls"]["nifty"]["why"])
            return
        d += datetime.timedelta(days=1)
    raise AssertionError("no Amavasya in 40 days?")


def test_metals_nakshatra_calls_from_the_x_reports():
    assert saptarsh.nak_tone("Pushya", "Kataka", "gold") == ("bear", "observed")
    assert saptarsh.nak_tone("Chitra", "Kanya", "silver") == ("bull", "observed")
    assert saptarsh.nak_tone("Pushya", "Kataka", "nifty")[1] == "extrapolated"
    # sign-level fallback only for metals, only where the report printed it
    assert saptarsh.nak_tone("Purva Bhadrapada", "Kumbha", "gold") == ("bear", "observed")
    assert saptarsh.nak_tone("Purva Bhadrapada", "Kumbha", "nifty")[1] == "extrapolated"
