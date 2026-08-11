"""Tests for the KP horary seed-number prasanam (1–249).

The 249 table is validated against facts that hold independently of any
worked example: the canonical per-sign counts, the first and last
divisions, and the round-trip invariant that a cast chart's lagna sub lord
must equal the sub lord the number selected.

NOT validated here: that the cusp derivation matches AstroSage. PRASANAM
VIDEO 1 quotes number 88 with significators {4,9,10,11}/{4,10,12} but
gives no DATE, so the planets cannot be reproduced. See the docstring on
transit.horary_chart.
"""
import pytest

from app import transit
from app.main import PrasanamRequest, prasanam
from app.rules import prasanam as prasanam_rules

CHENNAI = (5.5, 13.0827, 80.2707)


def test_table_has_249_entries():
    assert len(transit.KP_HORARY) == 249


def test_canonical_per_sign_counts():
    """The KP horary table splits 243 subs at rasi cusps, giving the
    standard 22/19/21/21 pattern repeating four times."""
    per = [0] * 12
    for start, _e, _n, _l in transit.KP_HORARY:
        per[int(start // 30)] += 1
    assert per == [22, 19, 21, 21] * 3
    assert sum(per) == 249


def test_first_and_last_divisions():
    first = transit.horary_ascendant(1)
    assert first["rasi"] == "Mesha"
    assert first["sub_lord"] == "Ketu"
    assert first["start"] == pytest.approx(0.0)
    assert first["end"] == pytest.approx(0.7777778, abs=1e-6)   # 0°46'40"
    assert transit.KP_HORARY[248][1] == pytest.approx(360.0)


def test_number_out_of_range_rejected():
    for n in (0, 250, -1):
        with pytest.raises(ValueError):
            transit.horary_ascendant(n)


def test_every_number_round_trips():
    """The cast chart's lagna sub lord must be the one the number picked.

    This is what caught the original bug: targeting the division's exact
    START put the ascendant on a knife-edge, and the solver landed
    fractions of an arcsecond below it, flipping number 45 from Sun to
    Venus. The ascendant is now taken at the division midpoint.
    """
    tz, lat, lon = CHENNAI
    for n in range(1, 250):
        c = transit.horary_chart(n, 2026, 8, 11, 11, 58, tz, lat, lon)
        assert c["lagna_sub_lord"] == transit.horary_ascendant(n)["sub_lord"], n


def test_ascendant_lands_inside_its_span():
    tz, lat, lon = CHENNAI
    for n in (1, 45, 88, 150, 249):
        c = transit.horary_chart(n, 2026, 8, 11, 11, 58, tz, lat, lon)
        s, e = transit.KP_HORARY[n - 1][0] % 360, transit.KP_HORARY[n - 1][1]
        e = 360.0 if abs(e - 360) < 1e-9 else e % 360
        a = c["asc"]
        assert (s <= a <= e) if s <= e else (a >= s or a <= e), (n, s, a, e)


def test_the_number_actually_changes_the_reading():
    """If the number did not move the significators it would be decorative."""
    tz, lat, lon = CHENNAI
    pairs = set()
    for n in range(1, 250, 17):
        c = transit.horary_chart(n, 2026, 8, 11, 11, 58, tz, lat, lon)
        pairs.add((c["question"], tuple(c["question_houses"]),
                   c["answer"], tuple(c["answer_houses"])))
    assert len(pairs) > 5, pairs


def test_question_planet_is_the_lagna_sub_lord():
    """[P1] 'Lakkana Upanachathram is the question' — and the number is
    exactly what selects the lagna, so the two agree under this method."""
    tz, lat, lon = CHENNAI
    for n in (7, 63, 88, 200):
        c = transit.horary_chart(n, 2026, 8, 11, 11, 58, tz, lat, lon)
        assert c["question"] == c["seed"]["sub_lord"]


def test_endpoint_returns_findings_and_rejects_bad_numbers():
    r = prasanam(PrasanamRequest(number=88, year=2026, month=8, day=11,
                                 hour=11, minute=58, tz_offset=5.5,
                                 lat=13.0827, lon=80.2707))
    assert r["number"] == 88
    assert r["seed"]["rasi"] == "Simha"
    titles = " ".join(f["title"] for f in r["findings"])
    assert "Horary number 88" in titles
    assert "Verdict" in titles
    assert "not financial advice" in r["note"]

    with pytest.raises(Exception):        # pydantic rejects ge/le violations
        PrasanamRequest(number=250, year=2026, month=8, day=11, hour=11,
                        minute=58, tz_offset=5.5, lat=13.0827, lon=80.2707)


def test_auto_path_is_labelled_as_a_substitute():
    """The user's objection was that the no-number reading was presented as
    the taught method. It must now say so itself."""
    from app import engine
    chart = engine.compute(2026, 8, 11, 11, 58, 5.5, 13.0827, 80.2707)
    titles = " ".join(f.title for f in prasanam_rules.rules(chart))
    assert "SUBSTITUTE" in titles
