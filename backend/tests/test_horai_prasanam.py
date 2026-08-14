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
    # rules read the SUNRISE-cast panchang (KP), not the display chart:
    # 1990-01-01 is thithi #5 at noon but #4 at sunrise, and 4 is chidra
    chart = engine.compute(1990, 1, 1, 12, 0, 5.5, 13.0827, 80.2707)
    from app.rules import graph
    n = graph.cast_chart(chart)["panchang"]["thithi"]["num"]
    in_paksha = (n - 1) % 15 + 1
    titles = " ".join(f.title for f in panchang_rules.rules(chart))
    assert ("Paksha Chidra" in titles) == (in_paksha in panchang_rules.PAKSHA_CHIDRA)
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




def test_class8_horai_corrections():
    from app.rules import horai
    # divergence rule is standalone and day-independent, not buried in a
    # weekday string, and points the right way (trade Nifty on divergence)
    chart = engine.compute(2026, 8, 11, 9, 15, 5.5, 13.0827, 80.2707)
    titles = [f.title for f in horai.rules(chart)]
    assert any("Index selection" in t for t in titles)
    idx = next(f for f in horai.rules(chart) if "Index selection" in f.title)
    assert "NIFTY only" in idx.detail and "diverge" in idx.detail
    for day in horai.DAY_RULES.values():
        for _, detail in day.values():
            assert "diverge" not in detail

    # every quoted figure is framed as a minimum, with the 45-min window
    assert "45 minutes" in horai.WINDOW_NOTE and "minimums" in horai.WINDOW_NOTE
    assert "before" in horai.WINDOW_NOTE.lower()

    # Uthiradam mega-crash tier carries its own magnitudes
    assert horai.UTHIRADAM_TIER[0] == "Uttara Ashadha"
    assert "300" in horai.UTHIRADAM_TIER[1] and "100" in horai.UTHIRADAM_TIER[1]

    # Venus horai is a reversal on ANY day, not Monday-only
    assert "REVERSAL" in horai.HORAI_EFFECT["Venus"]
    assert "Venus" not in horai.DAY_RULES.get("Monday", {})

    # the day-independent timeline is emitted
    assert any("Horai timeline" in t for t in titles)


def test_class9_saturn_horai_is_a_reversal():
    from app.rules import horai
    # [C9] "Next is Saturn Horai... That is vice versa. Vice versa means
    # it will be opposite to what happened before."
    assert "REVERSAL" in horai.HORAI_EFFECT["Saturn"]
    assert "vice versa" in horai.HORAI_EFFECT["Saturn"]
    # [C9] "Venus is the sign of unexpected things" - stated with no day
    assert "REVERSAL" in horai.HORAI_EFFECT["Venus"]
    # [C9] "Mercury Horai... I have given it as little up"
    assert horai.HORAI_EFFECT["Mercury"] == "up"
    # [C9] "It will rise up to half" - the half/45-min window
    assert "45 minutes" in horai.WINDOW_NOTE


def test_class10_confluence_and_gap_rules():
    from app.rules import horai, prasanam
    # confluence minimums fire only when horai and chain agree
    found = False
    for d in range(1, 29):
        c = engine.compute(2021, 6, d, 9, 15, 5.5, 13.0827, 80.2707)
        for f in horai.rules(c):
            if f.title.startswith("Confluence"):
                assert "30 points Nifty" in f.detail
                assert "60 points BankNifty" in f.detail
                found = True
    assert found, "confluence rule never fired in a month of sessions"

    # gap up/down is routed to prasanam, with no invented direction mapping
    c = engine.compute(2026, 8, 11, 9, 15, 5.5, 13.0827, 80.2707)
    gap = next(f for f in prasanam.rules(c) if "Gap up" in f.title)
    assert "prasanam" in gap.detail.lower()
    assert "garbled" in gap.detail


def test_example_chart_negative_yogam_overrides_horai():
    """[EX] 07/01/2022 Friday: Vyatipata (disease) day - the Friday
    Mercury UP rule is overridden and the market went down."""
    import datetime
    from app.rules import horai
    from app.rules.panchang_rules import yogam_bias
    c = engine.compute(2022, 1, 7, 9, 15, 5.5, 13.0827, 80.2707)
    assert c['panchang']['yogam']['name'] == 'Vyatipata'
    ups = [f for f in horai.rules(c) if '(Mercury)' in f.title]
    for f in ups:
        assert 'OVERRIDDEN' in f.title
        assert 'Vyatipata' in f.detail

    # on a clean-yogam Friday the rule stands unmodified
    for d in range(1, 90):
        day = datetime.date(2022, 1, 1) + datetime.timedelta(days=d)
        if day.weekday() != 4:
            continue
        c2 = engine.compute(day.year, day.month, day.day, 9, 15, 5.5,
                            13.0827, 80.2707)
        if yogam_bias(c2['panchang']['yogam']['name'])[0] == 'positive':
            for f in horai.rules(c2):
                if '(Mercury)' in f.title:
                    assert 'OVERRIDDEN' not in f.title
            break


def test_example_chart_saturn_horai_timing_exact():
    """The teacher's Saturn horai on 07/01/2022 runs 09:24-10:21; the
    proportional model must reproduce both endpoints."""
    slots = transit.horai_timeline(2022, 1, 7, 5.5, 13.0827, 80.2707)
    sat = next(s for s in slots
               if s['lord'] == 'Saturn' and 9 < s['start'] < 11)
    assert abs(sat['start'] - (9 + 24 / 60)) < 0.02
    assert abs(sat['end'] - (10 + 21 / 60)) < 0.02


def test_moon_is_the_question_planet():
    """[LT2] 'The moon is the question... the star in the moon is the
    question. The Buddha is an answer.' The question planet is the Moon's
    star lord; the answer is that planet's own star lord."""
    from app import transit
    from app.rules.graph import nak_lord_of
    import swisseph as swe
    c = transit.prasanam_chain(2021, 5, 5, 11, 58, 5.5, 13.0827, 80.2707)

    swe.set_sid_mode(swe.SIDM_KRISHNAMURTI, 0, 0)
    jd = swe.julday(2021, 5, 5, 11 + 58 / 60 - 5.5)
    moon = swe.calc_ut(jd, swe.MOON, transit.FLAGS)[0][0] % 360
    assert c['question'] == transit.lords_of(moon)['nak_lord']
    # and it is NOT simply the lagna sub-lord any more
    assert 'lagna_sub_lord' in c
    # answer chains one more star level down from the question planet
    assert c['answer'] in transit.DASHA_LORDS


def test_rahu_ketu_flags_unreliable_via_lagna_sub_lord():
    """[C3] 'if Raghukethu comes... there is a chance to make it 100%
    opposite... it can even lie' - tied to the lagna sub-lord, not the
    question planet. Downgraded from a hard CANCEL per P1's
    counter-evidence: 57 of the 249 seed numbers carry a Rahu/Ketu lagna
    sub-lord (23% of the input space, fixed by the KP table) and the old
    gate refused every one that reached it. The verdict is now computed
    by houses and flagged UNRELIABLE instead."""
    import datetime
    from app import engine
    from app.rules import prasanam
    found = False
    for d in range(1, 40):
        day = datetime.date(2021, 5, 1) + datetime.timedelta(days=d)
        c = engine.compute(day.year, day.month, day.day, 11, 58, 5.5,
                           13.0827, 80.2707)
        chain = __import__('app.transit', fromlist=['x']).prasanam_chain(
            day.year, day.month, day.day, 11, 58, 5.5, 13.0827, 80.2707)
        if chain['lagna_sub_lord'] in ('Rahu', 'Ketu') and \
                chain['moon_house'] not in prasanam.LOSS_HOUSES:
            verdict = next(f for f in prasanam.rules(c)
                           if f.title.startswith('Verdict'))
            assert 'UNRELIABLE' in verdict.title
            # the underlying houses judgment is still present...
            assert any(v in verdict.title for v in
                       ('YES', 'NO', 'UNCLEAR', 'INVALID'))
            # ...alongside the C3 warning
            assert 'opposite' in verdict.detail
            found = True
            break
    assert found, 'no Rahu/Ketu lagna-sub-lord day found to test'


def test_prasanam_gate_marks_sections():
    """[P2] 'if you open the gate you can enter, then you can put a
    graph' - a non-YES substitute prasanam prepends a study-only notice
    to the graph/weekly/long-term sections; a YES leaves them clean."""
    from app import engine, predict
    chart = engine.compute(2021, 5, 5, 11, 58, 5.5, 13.0827, 80.2707)
    pred = predict.run(chart)
    gate = pred['prasanam_gate']
    assert set(gate) >= {'verdict', 'open', 'reason', 'substitute'}
    assert gate['open'] == (gate['verdict'] == 'YES')
    for sec in ('graph', 'weekly', 'monthly', 'long_term'):
        has_notice = pred['sections'][sec][0]['title'].startswith(
            'Prasanam gate NOT open')
        assert has_notice == (not gate['open']), (sec, gate)


def test_rahu_ketu_share_of_the_seed_numbers_is_57():
    """The count RULES-SOURCES.md cites to justify the downgrade. It is
    a fixed property of the KP 249 table (number -> ascendant sub-lord),
    so it must not move with the date — if this fails, the doc's '23% of
    the input space' argument no longer holds."""
    from app import transit

    n = sum(transit.horary_chart(i, 2026, 8, 14, 10, 30, 5.5,
                                 13.0827, 80.2707)['lagna_sub_lord']
            in ('Rahu', 'Ketu') for i in range(1, 250))
    assert n == 57


def test_unreliable_yes_does_not_open_the_gate():
    """A reading flagged do-not-act must not be what authorises a graph,
    so the gate tests for a bare 'YES', not a substring."""
    from app.rules import prasanam

    assert prasanam.gate_state('YES', '')['open'] is True
    assert prasanam.gate_state('UNRELIABLE (YES)', '')['open'] is False


def test_significator_sets_structure():
    """[P1] planets signify SETS of houses - 'the star is the question,
    4, 9, 10, 11 are there; Rahu is here, 4, 10, 12 are there'."""
    from app import transit
    c = transit.prasanam_chain(2021, 5, 5, 11, 58, 5.5, 13.0827, 80.2707)
    for key in ('question_houses', 'answer_houses', 'moon_houses'):
        hs = c[key]
        assert isinstance(hs, list) and hs == sorted(hs)
        assert all(1 <= h <= 12 for h in hs)
        assert len(hs) >= 2, (key, hs)     # occupied + owned at minimum
    # the occupied house is always inside the significator set
    assert c['question_house'] in c['question_houses']
    assert c['answer_house'] in c['answer_houses']


def test_p1_worked_example_verdict():
    """[P1] question signifies 4,9,10,11; answer (Rahu) signifies
    4,10,12 - the 12 makes it a NO, and the market fell."""
    from app.rules.prasanam import judge_sets
    verdict, reason = judge_sets({4, 9, 10, 11}, {4, 10, 12})
    assert verdict == 'NO'
    assert '12' in reason


def test_poison_rule_on_sets():
    from app.rules.prasanam import judge_sets
    # a loss house spoils an otherwise profitable answer
    assert judge_sets({2}, {11, 8})[0] == 'NO'
    assert judge_sets({2}, {2, 6, 11})[0] == 'YES'
    # 3 + 11 = profit but delayed
    v, r = judge_sets({2}, {3, 11})
    assert v == 'YES' and 'delayed' in r
    # 1/4/10 satisfaction axis is reported either way
    assert 'satisfaction' in judge_sets({2}, {11, 4})[1]
    assert 'unsatisfying' in judge_sets({2}, {11})[1]


def test_int_judge_still_backward_compatible():
    from app.rules.prasanam import judge
    assert judge(4, 8)[0] == 'NO'
    assert judge(4, 11)[0] == 'YES'
    assert judge(5, 11)[0] == 'NO'
    assert judge(1, 4)[0] == 'UNCLEAR'
