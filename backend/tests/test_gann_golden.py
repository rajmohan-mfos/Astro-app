"""Golden fixtures for the Gann layer (gann-engine-CLAUDE.md).

The natal longitudes and the crossing guard are exactly what a refactor
breaks silently; the event-date cases pin the scan to dates the course
verified against the ephemeris and NSE closes.
"""
import datetime

import pytest

from app.gann import aspects, calendar, natal


# --- natal fixtures (tropical, 22 Apr 1996, julday(...,6.5)) ----------

@pytest.mark.parametrize("body,lon", [
    ("Mercury", 52.4), ("Mars", 22.1), ("Venus", 76.17),
    ("Jupiter", 287.4), ("Uranus", 304.5),
])
def test_radix_fixture(body, lon):
    assert natal.radix()[body] == pytest.approx(lon, abs=0.1)


# --- formula mechanics -------------------------------------------------

def test_separation_folds_over_180():
    assert aspects.separation(350, 10) == 20
    assert aspects.separation(0, 180) == 180
    assert aspects.separation(90, 45) == 45


def test_crossing_wrap_guard():
    """A 359°→1° lap must not fire aspects it never crossed."""
    dates = [datetime.date(2026, 1, 1) + datetime.timedelta(days=i)
             for i in range(3)]
    # a sweeps past b=180 → diff wraps 179 → -179: only the
    # conjunction-with-180-offset (opposition) is real, 90 is not
    assert aspects.crossings(dates, [358, 0, 2], [178, 178, 178], 90) == []
    assert aspects.crossings(dates, [358, 0, 2], [178, 178, 178], 180) != []


def test_crossing_detects_conjunction_zero():
    """Target 0 has no sign change in unsigned separation — the signed
    implementation must still catch it."""
    dates = [datetime.date(2026, 1, 1) + datetime.timedelta(days=i)
             for i in range(3)]
    assert aspects.crossings(dates, [178, 180.5, 183], [179, 179, 179],
                             0) != []


# --- event dates verified in the course --------------------------------

def _scan(center, back=5, ahead=5):
    return calendar.scan(datetime.date.fromisoformat(center), back, ahead)


def _dates(result, rule_id):
    return [e["date"] for e in result["events"] if e["rule_id"] == rule_id]


def test_venus_saturn_quadrature_jun_2024():
    # Lesson 7 ledger: aspect on 8 Jun 2024 (closed day → 7 Jun session)
    ds = _dates(_scan("2024-06-08"), "venus_saturn_quadrature")
    assert any("2024-06-06" <= d <= "2024-06-09" for d in ds)


def test_mercury_saturn_conjunction_feb_2025():
    # Lesson 12: his forward call, 25 Feb 2025
    ds = _dates(_scan("2025-02-25"), "mercury_saturn_conjunction")
    assert any("2025-02-23" <= d <= "2025-02-27" for d in ds)


def test_venus_natal_venus_quadrature_feb_2026():
    # Venus–Venus quadrature call for 23 Feb 2026 (90.3° that day)
    ds = _dates(_scan("2026-02-23"), "venus_natal_venus")
    assert any("2026-02-21" <= d <= "2026-02-25" for d in ds)


def test_mercury_mars_radix_may_2025():
    # Lesson 6 ledger: 06 May 2025, tMerc × nMars
    ds = _dates(_scan("2025-05-06"), "mercury_mars_radix")
    assert any("2025-05-04" <= d <= "2025-05-08" for d in ds)


def test_venus_station_jul_2023_and_retro_exclusion():
    # Lesson 9: Rx begins 21 Jul 2023 — and Lesson 8: the 21 Aug 2023
    # Venus–natalVenus sextile falls inside it and must be flagged
    # excluded by the taught retrograde filter.
    r = _scan("2023-08-05", back=20, ahead=25)
    stations = [e for e in r["events"] if e["rule_id"] == "venus_station"]
    assert any("2023-07-20" <= e["date"] <= "2023-07-24"
               and "begins" in e["detail"] for e in stations)
    sextiles = [e for e in r["events"] if e["rule_id"] == "venus_natal_venus"
                and e["angle"] == 60]
    assert sextiles and all(e["excluded"] for e in sextiles)


def test_october_pattern_is_octoberish():
    # Lesson 11: the Sun–Uranus–Neptune triangle exists only as a
    # mid-to-late October window (21–25 Oct 2025 is the third one).
    oct_ = _scan("2025-10-20", back=15, ahead=15)
    assert _dates(oct_, "sun_uranus_neptune")
    mar = _scan("2025-03-15", back=15, ahead=15)
    assert not _dates(mar, "sun_uranus_neptune")


def test_events_carry_their_evidence():
    r = _scan("2026-02-23")
    for e in r["events"]:
        assert e["evidence"] and e["verdict"] and e["source"]
