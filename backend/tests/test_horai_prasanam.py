"""Tests for the horai timeline/rules and the prasanam chain."""
from app import engine, predict, transit
from app.rules import horai, prasanam


def test_horai_timeline_wednesday():
    # 2021-05-05 (the author's chart date) was a Wednesday, Chennai
    slots = transit.horai_timeline(2021, 5, 5, 5.5, 13.0827, 80.2707)
    assert len(slots) == 24
    # first horai belongs to the day lord (Mercury on Wednesday)
    assert slots[0]["lord"] == "Mercury"
    # sunrise â‰ˆ 05:46 local
    assert 5.5 < slots[0]["start"] < 6.2
    # Chaldean sequence: Mercury â†’ Moon â†’ Saturn â†’ Jupiter â†’ Mars â†’ Sun â†’ Venus
    assert [s["lord"] for s in slots[:7]] == [
        "Mercury", "Moon", "Saturn", "Jupiter", "Mars", "Sun", "Venus"]
    # 24h later the cycle lands on Thursday's day lord (Jupiter)
    assert transit.HORAI_SEQ[(transit.HORAI_SEQ.index("Mercury") + 24) % 7] \
        == "Jupiter"


def test_horai_rules_wednesday_venus_window():
    chart = engine.compute(2021, 5, 5, 9, 15, 5.5, 13.0827, 80.2707)
    findings = horai.rules(chart)
    venus = [f for f in findings if "(Venus): UP" in f.title]
    # proportional horai put the Venus slot ~12:11â€“13:15, inside the session
    assert venus, [f.title for f in findings]


def test_proportional_horai_match_example_video():
    # [EX @ 04:29] Friday 07/01/2022: the teacher's Saturn horai runs
    # 09:24â€“10:29. Proportional daylight twelfths reproduce it closely.
    slots = transit.horai_timeline(2022, 1, 7, 5.5, 13.0827, 80.2707)
    assert slots[0]["lord"] == "Venus"          # Friday day lord
    saturn = slots[3]
    assert saturn["lord"] == "Saturn"
    assert 9.3 < saturn["start"] < 9.6          # teacher: 09:24
    assert 10.3 < saturn["end"] < 10.6          # teacher: 10:29
    # daylight slots are shorter than 1h in January
    assert (saturn["end"] - saturn["start"]) < 1.0


def test_prasanam_chain_and_judgment():
    c = transit.prasanam_chain(2021, 5, 5, 11, 58, 5.5, 13.0827, 80.2707)
    assert c["question"] in transit.DASHA_LORDS
    assert c["answer"] in transit.DASHA_LORDS
    assert 1 <= c["question_house"] <= 12
    assert 1 <= c["answer_house"] <= 12

    # judgment table
    assert prasanam.judge(4, 8)[0] == "NO"       # heavy loss dominates
    assert prasanam.judge(4, 11)[0] == "YES"     # heavy profit
    assert prasanam.judge(5, 4)[0] == "NO"       # question planet in loss
    assert prasanam.judge(1, 4)[0] == "UNCLEAR"  # both neutral
    # poison rule: a profit answer is spoiled by a loss-house question
    assert prasanam.judge(5, 11)[0] == "NO"
    assert prasanam.judge(8, 2)[0] == "NO"


def test_thithi_bias_table():
    from app.rules.panchang_rules import thithi_bias
    assert thithi_bias(3)[0] == "positive"      # Jaya (Tritiyai)
    assert thithi_bias(23)[0] == "positive"     # Jaya in Krishna paksha
    assert thithi_bias(4)[0] == "negative"      # Rikta
    assert thithi_bias(29)[0] == "negative"     # Rikta (Krishna Chaturdasi)
    assert thithi_bias(15)[0] == "positive"     # Pournami
    assert thithi_bias(30)[0] == "negative"     # Amavasai
    # guide §4A five families (user-adjudicated)
    assert thithi_bias(6)[0] == "positive"      # Nanda (Shashti)
    assert thithi_bias(1)[0] == "positive"      # Nanda (Prathamai)
    assert thithi_bias(11)[0] == "positive"     # Nanda (Ekadasi)
    assert thithi_bias(2)[0] == "positive"      # Bhadra (Dwitiyai)
    assert thithi_bias(12)[0] == "positive"     # Bhadra (Dwadasi)
    assert thithi_bias(5)[0] == "positive"      # Panchami [EX-Buzz]
    assert thithi_bias(10)[0] == "neutral"      # Purna — consolidation
    assert "Rikta" in thithi_bias(4)[1] and "Nanda" in thithi_bias(1)[1]


def test_yogam_classification_complete():
    from app.names import YOGAS
    from app.rules.panchang_rules import (NEGATIVE_YOGAS, POSITIVE_YOGAS,
                                          VERY_NEGATIVE_YOGAS, yogam_bias)
    # all 27 yogas classified, none left neutral
    assert len(NEGATIVE_YOGAS | POSITIVE_YOGAS) == 27
    assert not (NEGATIVE_YOGAS & POSITIVE_YOGAS)
    for name in YOGAS:
        assert yogam_bias(name)[0] != "neutral", name
    assert VERY_NEGATIVE_YOGAS == {"Vyaghata", "Vyatipata", "Vaidhriti"}
    # this system marks several classically-benign yogas inauspicious
    for n in ("Dhriti", "Dhruva", "Siddhi"):
        assert yogam_bias(n)[0] == "negative", n
    assert yogam_bias("Priti")[0] == "positive"
    assert yogam_bias("Vaidhriti")[0] == "very negative"


def test_paksha_chidra_and_thakka_yoga():
    from app import engine
    from app.rules import panchang_rules
    # 1990-01-01 is Shukla Panchami (#5) on a Monday: not chidra, and
    # Ekadasi/Monday is the Monday thakka pair, so no thakka finding here
    chart = engine.compute(1990, 1, 1, 12, 0, 5.5, 13.0827, 80.2707)
    titles = " ".join(f.title for f in panchang_rules.rules(chart))
    assert "Paksha Chidra" not in titles
    assert panchang_rules.PAKSHA_CHIDRA == {4, 6, 8, 12, 14}
    assert (11, 0) in panchang_rules.THAKKA_YOGA      # Ekadasi + Monday
    assert (9, 5) in panchang_rules.THAKKA_YOGA       # Navami + Saturday


def test_karanam_bias_table():
    from app.rules.panchang_rules import karanam_bias
    # [C7 @ 11:25] movable positive, the four fixed negative
    assert karanam_bias("Bava")[0] == "positive"
    assert karanam_bias("Vishti")[0] == "positive"
    assert karanam_bias("Shakuni")[0] == "negative"
    assert karanam_bias("Kimstughna")[0] == "negative"
    assert karanam_bias("Naga")[0] == "negative"


def test_day_lord_rule_bare_xy_only():
    from tests.test_scenarios import make_chart
    from app.rules import graph
    # S3-style chart (bare X=Saturn, bare Y=Sun) dated on a SUNDAY â†’
    # Sun is the day lord and Y=Sun flips to bullish; X is unaffected.
    chart = make_chart({
        "Sun": 35.0, "Moon": 100.0, "Mars": 60.0, "Mercury": 130.0,
        "Jupiter": 250.0, "Venus": 145.0, "Saturn": 30.0,
        "Rahu": 120.0, "Ketu": 300.0,
    })
    chart["input"] = {"date": "2021-01-17", "time": "06:00",
                      "tz_offset": 5.5, "lat": 13.0827, "lon": 80.2707}
    segs = graph.build_segments(chart)
    assert segs[0]["bias"] == "sideways-bullish"  # Saturn(10) upside-wise
    assert segs[1]["bias"] == "bullish"          # Sun = Sunday's day lord
    assert "day-lord" in segs[1]["reason"]


def test_prediction_has_prasanam_section():
    chart = engine.compute(2021, 5, 5, 11, 58, 5.5, 13.0827, 80.2707)
    pred = predict.run(chart)
    for section in ("graph", "weekly", "monthly", "long_term", "prasanam"):
        assert pred["sections"][section], section
    titles = " ".join(f["title"] for f in pred["sections"]["prasanam"])
    assert "Verdict" in titles


def test_stock_mapping():
    from app.rules.stocks import STOCKS, stocks_of
    assert len(STOCKS) == 50
    # video cross-checks: C4 Reliance=Sun (pure), Cipla=Rahu+Sun (mixed);
    # C6 Coal India=Saturn; C11 Grasim=Venus+Moon
    assert stocks_of("Sun", pure=True) == ["RELIANCE"]
    # purity counts only the nine grahas: TATASTEEL (Saturn+Uranus) and
    # ASIANPAINTS (Mars+Neptune) stay eligible — the latter is the
    # teacher's own flagship Mars long-term trade
    assert set(stocks_of("Saturn", pure=True)) == {"COALINDIA", "VEDL",
                                                   "TATASTEEL"}
    assert "ASIANPAINTS" in stocks_of("Mars", pure=True)
    assert "CIPLA" in stocks_of("Rahu") and "CIPLA" not in stocks_of("Rahu", pure=True)
    assert STOCKS["GRASIM"] == ["Venus", "Moon"]
    assert set(stocks_of("Ketu")) == {"GAIL", "ONGC"}


def test_stock_findings_in_prediction():
    chart = engine.compute(2022, 1, 7, 9, 15, 5.5, 13.0827, 80.2707)
    pred = predict.run(chart)
    titles = " ".join(f["title"] for f in pred["sections"]["graph"])
    assert "Stocks for the" in titles


