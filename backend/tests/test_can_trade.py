"""Tests for the /api/can-trade gochara check."""
from app.main import CanTradeRequest, ComputeRequest, can_trade


def make_req(by, bm, bd, y, m, d):
    return CanTradeRequest(
        birth=ComputeRequest(year=by, month=bm, day=bd, hour=12, minute=0,
                             tz_offset=5.5, lat=13.0827, lon=80.2707),
        year=y, month=m, day=d, tz_offset=5.5)


def test_can_trade_counts_and_verdict():
    # Birth 1990-01-01: Moon 306.465 â†’ Kumbha (sign 10)
    r = can_trade(make_req(1990, 1, 1, 2021, 5, 5))
    assert r["birth_rasi"]["en"] == "Kumbha"
    # 2021-05-05 09:15: Moon â‰ˆ 306.8 â†’ Kumbha â†’ count 1 â†’ neutral OK
    assert r["transit_rasi"]["en"] == "Kumbha"
    assert r["count"] == 1
    # lagna Meena: transit Moon is 12th FROM THE LAGNA -> AVOID [guide 2.1]
    assert r["lagna_count"] == 12
    assert r["verdict"] == "AVOID"
    assert r["rasi_until"] != "â€”"

    # 2021-05-11: Moon in Mesha (sign 0) â†’ (0-10)%12+1 = 3 â†’ neutral;
    # walk a few days to hit an AVOID (count 5 = Mithuna â‰ˆ May 16)
    r = can_trade(make_req(1990, 1, 1, 2021, 5, 16))
    assert r["count"] in (4, 5)          # boundary tolerance
    if r["count"] == 5:
        assert r["verdict"] == "AVOID"


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
