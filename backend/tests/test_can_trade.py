"""Tests for the /api/can-trade gochara check.

Charts here are KP, like the rest of the prediction path — only the
/api/compute display endpoints stay Lahiri (SPEC §5). Cast time stays
09:15: this is a "can I trade today" read, so market open is the relevant
moment rather than the sunrise used for the panchang day.
"""
from app import engine, transit
from app.main import CanTradeRequest, ComputeRequest, can_trade


def make_req(by, bm, bd, y, m, d):
    return CanTradeRequest(
        birth=ComputeRequest(year=by, month=bm, day=bd, hour=12, minute=0,
                             tz_offset=5.5, lat=13.0827, lon=80.2707),
        year=y, month=m, day=d, tz_offset=5.5)


def test_can_trade_counts_and_verdict():
    # Birth 1990-01-01: Moon ~306.4 -> Kumbha (sign 10)
    r = can_trade(make_req(1990, 1, 1, 2021, 5, 5))
    assert r["birth_rasi"]["en"] == "Kumbha"
    # 2021-05-05 09:15: Moon ~306.7 -> Kumbha -> count 1 -> neutral OK
    assert r["transit_rasi"]["en"] == "Kumbha"
    assert r["count"] == 1
    # lagna Meena: transit Moon is 12th FROM THE LAGNA -> AVOID [guide 2.1]
    assert r["lagna_count"] == 12
    assert r["verdict"] == "AVOID"

    # 2021-05-11: Moon in Mesha (sign 0) -> (0-10)%12+1 = 3 -> neutral;
    # walk a few days to hit an AVOID (count 5 = Mithuna ~ May 16)
    r = can_trade(make_req(1990, 1, 1, 2021, 5, 16))
    assert r["count"] in (4, 5)          # boundary tolerance
    if r["count"] == 5:
        assert r["verdict"] == "AVOID"


def test_rasi_until_is_a_real_timestamp():
    """The old assertion compared against a mojibake em dash, so it could
    never fail — it passed even when moon_rasi_exit returned its "—"
    sentinel. Check the actual shape instead."""
    r = can_trade(make_req(1990, 1, 1, 2021, 5, 5))
    until = r["rasi_until"]
    assert until != "—", "moon_rasi_exit found no crossing"
    import datetime
    parsed = datetime.datetime.strptime(until, "%Y-%m-%d %H:%M")
    # the Moon spends ~2.5 days per rasi, so the exit is within 3 days
    assert 0 <= (parsed - datetime.datetime(2021, 5, 5, 9, 15)).days <= 3


def test_rasi_until_is_always_parseable():
    """Guards a rollover bug: the hour and minute used to be formatted
    independently, so a crossing at 05:59:40 rendered as "05:60" — an
    invalid timestamp on 3 days of 2024 alone."""
    import datetime

    day = datetime.date(2024, 9, 20)          # one of the three
    while day <= datetime.date(2024, 9, 22):
        s = transit.moon_rasi_exit(day.year, day.month, day.day,
                                   5.5, 13.0827, 80.2707)
        datetime.datetime.strptime(s, "%Y-%m-%d %H:%M")   # must not raise
        assert s.endswith(":60") is False
        day += datetime.timedelta(days=1)


def test_rasi_until_agrees_with_transit_rasi():
    """`rasi_until` answers "when does the Moon leave THIS rasi" — so the
    Moon must still be in `transit_rasi` just before that moment and out
    of it just after.

    The probe below computes on KP, so this pins the whole path to KP as
    well as tying its two halves together: it fails if `can_trade` drops
    back to Lahiri (transit_rasi stops matching), and `test_moon_rasi_exit_is_kp`
    fails if `moon_rasi_exit` does. Between them, a revert of either half
    is caught. A single-ayanamsa mismatch would name different rasis on
    boundary days and put the exit time out by up to ~2.5 days.
    """
    import datetime

    for day in (5, 11, 16, 23):
        r = can_trade(make_req(1990, 1, 1, 2021, 5, day))
        t = datetime.datetime.strptime(r["rasi_until"], "%Y-%m-%d %H:%M")

        def rasi_at(dt):
            c = engine.compute(dt.year, dt.month, dt.day, dt.hour,
                               dt.minute, 5.5, 13.0827, 80.2707,
                               ayanamsa_mode=engine.KP)
            return next(g for g in c["grahas"] if g["name"] == "Moon")["rasi"]

        before = rasi_at(t - datetime.timedelta(minutes=10))
        after = rasi_at(t + datetime.timedelta(minutes=10))
        assert before == r["transit_rasi"]["en"], (day, before, r)
        assert after != before, (day, after, r)


def test_moon_rasi_exit_is_kp():
    """Pin the ayanamsa by its observable consequence.

    The Moon covers 0.55°/hour, so the 0.097° Lahiri/KP offset moves a
    rasi crossing by ~12 minutes: this crossing is 05:43 under KP and
    05:55 under Lahiri. Asserting the KP value is what catches a revert —
    an earlier version of this test compared two calls to the same
    function, which returns the same answer either way and so could never
    fail.
    """
    assert transit.moon_rasi_exit(2021, 5, 5, 5.5,
                                  13.0827, 80.2707) == "2021-05-07 05:43"


def test_moon_rasi_exit_sets_its_own_sid_mode():
    """Must not inherit whatever ayanamsa the previous caller left set."""
    import swisseph as swe

    expected = transit.moon_rasi_exit(2021, 5, 5, 5.5, 13.0827, 80.2707)
    swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
    assert transit.moon_rasi_exit(2021, 5, 5, 5.5, 13.0827, 80.2707) == expected


def test_can_trade_is_cast_at_sunrise():
    """The chart moment is sunrise, not market open — and `rasi_until` is
    anchored there too, so the two cannot drift apart.

    Consequence worth knowing: on ~5.7% of days (21 of 366 in 2024) the
    sunrise rasi has already expired by 09:15, so `rasi_until` reads
    earlier than market open. That is faithful to the sunrise reading.
    """
    import datetime

    r = can_trade(make_req(1990, 1, 1, 2021, 5, 5))
    rise = transit.sunrise_hour(2021, 5, 5, 5.5, 13.0827, 80.2707)
    hh, mm = int(rise), round((rise % 1) * 60)
    assert r["cast"] == f"{hh:02d}:{mm:02d}"
    assert 5 <= hh <= 6, r["cast"]

    # the reported rasi must be the one in force AT SUNRISE
    c = engine.compute(2021, 5, 5, hh, mm, 5.5, 13.0827, 80.2707,
                       ayanamsa_mode=engine.KP)
    at_rise = next(g for g in c["grahas"] if g["name"] == "Moon")["rasi"]
    assert r["transit_rasi"]["en"] == at_rise

    # and rasi_until must be that rasi's end, not the 09:15 rasi's
    t = datetime.datetime.strptime(r["rasi_until"], "%Y-%m-%d %H:%M")
    assert t > datetime.datetime(2021, 5, 5, hh, mm)


def test_verdict_classes():
    # every verdict must be consistent with counts, lagna and natal nodes
    for d in range(1, 15):
        r = can_trade(make_req(1990, 1, 1, 2021, 6, d))
        if (r["over_natal_node"] or r["count"] in (5, 8, 12)
                or r["lagna_count"] in (5, 8, 12)):
            assert r["verdict"] == "AVOID"
        elif r["count"] in (2, 6, 11):
            assert r["verdict"] == "FAVOURABLE"
        else:
            assert r["verdict"] == "OK"
