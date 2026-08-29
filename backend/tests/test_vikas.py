"""Pins the Vikas engine to dates he cites in the classes (see
knowledge/vikas/NOTES.md for the timestamps)."""
import datetime

import pytest

from app import vikas


def labels(d: str) -> list[str]:
    return [e["label"] for e in vikas.events_between(datetime.date.fromisoformat(d))]


def keys(d: str) -> dict:
    return {e["label"]: e["key"] for e in vikas.events_between(datetime.date.fromisoformat(d))}


@pytest.mark.parametrize("iso, label", [
    ("2024-05-13", "Jupiter 30° Mercury"),          # [V1 @ 01:09] the May 2024 bottom
    ("2024-02-06", "Mars enters Makara"),           # [V4 @ 05:44] "6th February 24, metal sector"
    ("2024-03-07", "Mars enters Dhanishta"),        # [V4 @ 21:53]
    ("2025-01-11", "Sun enters Uttara Ashadha"),    # [V1 @ 29:02; VD2]
    ("2024-09-27", "Sun enters Hasta"),             # [V1 @ 46:04] the ATH date
    ("2025-05-07", "Mercury enters Mesha"),         # [V1] the big date of May 2025
    ("2020-03-22", "Mars enters Makara"),           # [V4 @ 14:03] "22nd March … 22 was holiday, 23 was bottom"
])
def test_cited_event_dates(iso, label):
    assert label in labels(iso)


def test_class2_families():
    # [V2 @ 01:05:39–01:09:14] Venus–Uranus 8° "16th/17th April 2021 … Monday is important"
    assert "Venus within 8° of Uranus" in labels("2021-04-16")
    # [V2 @ 32:29–36:30] Moon in Mesha 3–4 Mar 2025 bottom (both days), with Mercury–Rahu 0°
    for iso in ("2025-03-03", "2025-03-04"):
        r = vikas.day(datetime.date.fromisoformat(iso))
        assert "Moon in Mesha" in [e["label"] for e in r["events"]]
    assert "Mercury conjunct Rahu" in labels("2025-03-02") + labels("2025-03-03")


def test_mars_saturn_keys():
    # Saturn in Kumbha (11th sign, odd) in Feb 2024 → small fall
    assert keys("2024-02-06")["Mars enters Makara"] == "12th_from_saturn_odd"
    # Saturn in Makara (10th sign, even) in Feb 2020 → big fall; Mars joins it 23 Mar
    assert keys("2020-02-08")["Mars enters Dhanu"] == "12th_from_saturn_even"
    assert keys("2020-03-22")["Mars enters Makara"] == "with_saturn"


def test_moon_45_is_tropical():
    # [V4 @ 29:53] "18-8-2022 … nearly 45 at market opening" — and 14 Mar 2024 [V4 @ 42:33]
    for iso in ("2022-08-18", "2024-03-14"):
        fams = [e["family"] for e in vikas.moon_angle_date(datetime.date.fromisoformat(iso))]
        assert "moon45_trop" in fams


def test_session_star_split():
    # [V5 @ 47:05–48:11] Anuradha (Saturn) 13 May 2025 fell, Jyeshtha (Mercury) reversed 14 May
    s13 = vikas.session_star(datetime.date(2025, 5, 13))
    assert s13["nakshatra"] == "Anuradha" and s13["lord"] == "Saturn"
    assert s13["full_session"] and s13["clean"] and s13["nature"] == "malefic"
    s14 = vikas.session_star(datetime.date(2025, 5, 14))
    assert s14["open_nakshatra"] == "Anuradha" and s14["open_ends"] == "11:47"
    assert s14["nakshatra"] == "Jyeshtha" and s14["lord"] == "Mercury"
    assert not s14["clean"]                      # under 4 h of the session


def test_session_star_class5_examples():
    # [V5 @ 36:03] 9 Jun 2025 Vishakha (Jupiter) → Bank Nifty date; 10 Jun Anuradha (Saturn)
    s9 = vikas.session_star(datetime.date(2025, 6, 9))
    assert (s9["nakshatra"], s9["lord"], s9["nature"]) == ("Vishakha", "Jupiter", "benefic")
    s10 = vikas.session_star(datetime.date(2025, 6, 10))
    assert (s10["nakshatra"], s10["lord"]) == ("Anuradha", "Saturn") and s10["full_session"]


def test_moon_nature_follows_tithi():
    # Moon is benefic only from Shukla Dashami (10) to Krishna Panchami (20)
    assert vikas._nature("Moon", 12) == "benefic"
    assert vikas._nature("Moon", 3) == "malefic"
    assert vikas._nature("Moon", 25) == "malefic"
    assert vikas._nature("Saturn", 12) == "malefic"
    assert vikas._nature("Venus", 25) == "benefic"


def test_week_shape_and_shift():
    w = vikas.week(datetime.date(2026, 8, 28), 10)
    assert [r["weekday"] for r in w["days"][:3]] == ["Fri", "Sat", "Sun"]
    sat = w["days"][1]
    assert not sat["trading"] and sat["shifted_to"] == "2026-08-31"
    assert sat["star_date"] is None                 # closed day is never a star date
    for r in w["days"]:
        assert set(r) >= {"date", "star", "events", "star_date", "carry_over", "shifted_to"}
    # 2 Sep 2026: Venus (benefic) after Ketu (malefic), same Moon sign → setup reported
    d2 = next(r for r in w["days"] if r["date"] == "2026-09-02")
    assert d2["carry_over"] and d2["carry_over"]["setup"]


def test_friday_is_not_a_star_date():
    # Saturn star on a Friday is skipped ("no Friday dates" [V3])
    d = datetime.date(2026, 9, 4)                   # Rohini (Moon) — not lorded anyway
    r = vikas.day(d)
    assert r["star_date"] is None
