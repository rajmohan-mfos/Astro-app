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
    assert saptarsh.nak_tone("Pushya", "Kataka", "gold") == ("bull", "observed")  # 2 of 3 reports
    assert saptarsh.nak_tone("Chitra", "Kanya", "silver") == ("bull", "observed")
    assert saptarsh.nak_tone("Pushya", "Kataka", "nifty")[1] == "extrapolated"
    # sign-level fallback only for metals, only where the report printed it
    assert saptarsh.nak_tone("Purva Bhadrapada", "Kumbha", "gold") == ("bear", "observed")  # 2 of 3 bearish
    # every Virgo star is observed by now, so exercise the sign fallback
    # with a star the metals table has never seen (nak_tone does not
    # check that the star lies in the sign)
    assert saptarsh.nak_tone("Magha", "Kanya", "gold") == ("neutral", "observed")  # Virgo, 26 May
    assert saptarsh.nak_tone("Magha", "Kanya", "nifty")[1] == "extrapolated"


# ---- third learning pass: X posts of Apr-Jun 2026 (may.mp4) ----

def test_ingresses_match_the_2_jun_report():
    """2 Jun report: 'Jupiter enters in Cancer at 01:49 IST', 'Mercury
    enters in Adra nakshatra at 06:13 IST'."""
    d = saptarsh.day(datetime.date(2026, 6, 2))
    jup = [i for i in d["ingresses"] if i["planet"] == "Jupiter" and i["kind"] == "sign"]
    assert jup and jup[0]["to"] == "Kataka"
    assert abs(_mins(jup[0]["time"]) - _mins("01:49")) <= 5
    assert jup[0]["source"] == "observed" and jup[0]["tone"] == "bear"
    mer = [i for i in d["ingresses"] if i["planet"] == "Mercury" and i["kind"] == "nakshatra"]
    assert mer and mer[0]["to"] == "Ardra"
    assert abs(_mins(mer[0]["time"]) - _mins("06:13")) <= 5
    assert any("Jupiter enters Kataka" in f for f in d["flags"])


def test_quintile_and_moon_saturn_conjunction_10_jun():
    """10 Jun report: Sun 72 Moon 02:36 'strong bearish'; Moon 00 Saturn
    13:01 'strong bullish'; Venus 00 Jupiter 01:30 'strong bearish';
    Mercury 90 Saturn 11:10 'high volatile'."""
    d = saptarsh.day(datetime.date(2026, 6, 10))
    for a, ang, b, t, tone in [("Sun", 72, "Moon", "02:36", "bear"),
                               ("Moon", 0, "Saturn", "13:01", "bull"),
                               ("Venus", 0, "Jupiter", "01:30", "bear"),
                               ("Mercury", 90, "Saturn", "11:10", "vol")]:
        got = _aspect(d, a, ang, b)
        assert abs(_mins(got["time"]) - _mins(t)) <= 4, (a, ang, b, got["time"])
        assert got["tone"] == tone and got["source"] == "observed"
    assert {"Venus", "Jupiter", "Saturn"} <= set(d["active_planets"])


def test_vaar_nakshatra_thursday_pushya_is_auspicious():
    """21 May (Thu, Pushya): 'Combination of Nakshatra and Vaar is
    bullish' — classical Sarvartha Siddhi + Amrita Siddhi."""
    vn = saptarsh.vaar_nakshatra_yoga(3, "Pushya")
    assert vn["tone"] == "bull" and "Amrita Siddhi" in vn["names"]
    assert saptarsh.vaar_nakshatra_yoga(1, "Ardra")["names"] == ["Yamaghanta"]
    assert saptarsh.vaar_nakshatra_yoga(0, "Bharani") is None
    d = saptarsh.day(datetime.date(2026, 5, 21))
    assert d["moon"]["nakshatra"] == "Pushya"
    assert d["panchang"]["vaar_nakshatra"]["tone"] == "bull"


def test_observed_vaar_tithi_overrides_the_classical_table():
    assert saptarsh.vaar_tithi_yoga(4, 29) == {"names": ["Vaar-Tithi"], "tone": "bear",
                                               "source": "observed"}      # Fri 15 May
    assert saptarsh.vaar_tithi_yoga(1, 3)["source"] == "classical"        # Tue 19 May
    d = saptarsh.day(datetime.date(2026, 5, 15))
    assert d["panchang"]["vaar_tithi"]["source"] == "observed"
    assert d["panchang"]["vaar_tithi"]["tone"] == "bear"


def test_vyatipata_is_bullish_for_metals_but_not_nifty():
    moon = {"sign": "Kataka", "nakshatra": "Ashlesha", "sign_change": None,
            "nakshatra_change": None}
    gold = saptarsh._call("gold", moon, [], [], "Vyatipata", None, 6)
    nifty = saptarsh._call("nifty", moon, [], [], "Vyatipata", None, 6)
    assert gold["tone"] == "bull" and any("Mahapat" in w for w in gold["why"])
    assert nifty["tone"] == "vol"


# ---- fourth learning pass: X posts of Apr 2026 (April.mp4) ----

def test_6_apr_report_ingresses_and_anuradha():
    """6 Apr: 'Venus enters in Bharani nakshatra from 01:00 IST, this is
    bearish and Mars enters in Uttarbhadra, this is bullish'; Moon in
    Anuradha 'considered bullish for precious metals'."""
    d = saptarsh.day(datetime.date(2026, 4, 6))
    assert d["moon"]["nakshatra"] == "Anuradha"
    assert d["calls"]["gold"]["tone"] in ("bull", "vol")
    assert d["calls"]["gold"]["source"] == "observed"
    ven = [i for i in d["ingresses"] if i["planet"] == "Venus" and i["to"] == "Bharani"]
    assert ven and abs(_mins(ven[0]["time"]) - _mins("01:00")) <= 10
    assert ven[0]["tone"] == "bear" and ven[0]["source"] == "observed"
    mars = [i for i in d["ingresses"] if i["planet"] == "Mars" and i["to"] == "Uttara Bhadrapada"]
    assert mars and mars[0]["tone"] == "bull"


def test_16_apr_moon_mars_and_moon_saturn_conjunctions():
    """16 Apr: 'Moon-Mars at 0° at 03:40 IST and Moon-Saturn at 08:09 IST
    are strong bullish'."""
    d = saptarsh.day(datetime.date(2026, 4, 16))
    for b, t in (("Mars", "03:40"), ("Saturn", "08:09")):
        got = _aspect(d, "Moon", 0, b)
        assert abs(_mins(got["time"]) - _mins(t)) <= 5, (b, got["time"])
        assert got["tone"] == "bull"


def test_17_apr_amavasya_new_moon_time():
    """17 Apr: 'TODAY IS AMAVSHYA … MOON-SUN AT 0° AT 17:32 IST' and Moon
    Pisces/Revati till 12:30 then Aries/Ashwini."""
    d = saptarsh.day(datetime.date(2026, 4, 17))
    assert 30 in d["panchang"]["tithis_in_session"]
    got = _aspect(d, "Sun", 0, "Moon")
    # the astronomical new moon is 11:52 UTC = 17:22 IST; their 17:32 is
    # the one published time in these reports that is 10 min off
    assert abs(_mins(got["time"]) - _mins("17:32")) <= 12
    assert d["moon"]["sign_change"]["to"] == "Mesha"
    # April reports were cast with a coarser ephemeris than the August
    # ones (which match to 1-2 min): Moon->Aries 12:02 vs their 12:30
    assert abs(_mins(d["moon"]["sign_change"]["time"]) - _mins("12:30")) <= 30
    assert any("Amavasya" in w for w in d["calls"]["silver"]["why"])


# ---- fifth learning pass: X posts of Nov 2025 - Jan 2026 (Nov 2025.mp4) ----

def test_vaar_tithi_distinguishes_paksha():
    """Tue + Shukla 14 'bullish' (28 Jul); Tue + Krishna 14 'bearish'
    (18 Nov 2025). Thu + 15 and Fri + Krishna 12 fall to the classical
    table, which agrees with his calls of 4 Dec and 30 Jan."""
    assert saptarsh.vaar_tithi_yoga(1, 14)["tone"] == "bull"
    assert saptarsh.vaar_tithi_yoga(1, 29)["tone"] == "bear"
    assert saptarsh.vaar_tithi_yoga(3, 15) == {"names": ["Siddha"], "tone": "bull",
                                               "source": "classical"}
    assert saptarsh.vaar_tithi_yoga(4, 12)["names"] == ["Mrityu"]
    d = saptarsh.day(datetime.date(2025, 11, 18))
    assert d["panchang"]["vaar_tithi"] == {"names": ["Vaar-Tithi"], "tone": "bear",
                                           "source": "observed"}


def test_regime_stellium_cluster_and_nodal_axis():
    """26 Jan 2026 note: four planets in Shravana from 29 Jan. 21 Jan:
    'many planets today are below 10 degrees'. 6 Jan: Rahu in Aquarius,
    Ketu in Leo."""
    r = saptarsh.regime(datetime.date(2026, 1, 29))
    st = [s for s in r["nakshatra_stellia"] if s["nakshatra"] == "Shravana"]
    assert st and {"Sun", "Mercury", "Venus", "Mars"} <= set(st[0]["planets"])
    assert any("stellium" in n for n in r["notes"])
    r21 = saptarsh.regime(datetime.date(2026, 1, 21))
    assert len(r21["early_degree_bodies"]) >= 7
    assert any("first 10°" in n for n in r21["notes"])
    assert any("Rahu in Aquarius / Ketu in Leo" in n for n in r21["notes"])
    # and none of those fire on an ordinary day
    r_aug = saptarsh.regime(datetime.date(2026, 8, 28))
    assert not any("stellium" in n or "first 10°" in n for n in r_aug["notes"])


def test_14_nov_moon_ketu_and_mercury_station():
    """14 Nov 2025: 'Moon-Ketu at 0° at 09:22 IST is bullish' — Ketu is
    Rahu + 180, so this is Moon 180 Rahu. 6 Nov: Mercury 'going to
    retrograde on Sunday night' — the station is early on Mon 10 Nov."""
    d = saptarsh.day(datetime.date(2025, 11, 14))
    got = _aspect(d, "Moon", 180, "Rahu")
    assert abs(_mins(got["time"]) - _mins("09:22")) <= 4
    assert got["tone"] == "bull" and got["source"] == "observed"
    st = [i for i in saptarsh.day(datetime.date(2025, 11, 10))["ingresses"]
          if i["kind"] == "station"]
    assert st and st[0]["planet"] == "Mercury" and st[0]["to"] == "retrograde"
    assert st[0]["source"] == "observed"


def test_nov_ingress_readings_and_amavasya():
    d = saptarsh.day(datetime.date(2025, 11, 18))
    ven = [i for i in d["ingresses"] if i["planet"] == "Venus" and i["to"] == "Vishakha"]
    assert ven and abs(_mins(ven[0]["time"]) - _mins("12:20")) <= 4
    assert ven[0]["tone"] == "bear"
    d = saptarsh.day(datetime.date(2025, 11, 19))
    assert 30 in d["panchang"]["tithis_in_session"]
    sun = [i for i in d["ingresses"] if i["planet"] == "Sun" and i["to"] == "Anuradha"]
    assert sun and sun[0]["tone"] == "bull"
    assert saptarsh.nak_tone("Swati", "Tula", "gold") == ("bear", "observed")
    assert saptarsh.nak_tone("Krittika", "Vrishabha", "gold") == ("bull", "observed")
    assert saptarsh.aspect_tone("Sun", "Pluto", 0) == ("bear", "observed")


# ---- sixth learning pass: X posts of Jul - Oct 2025 (August 2025.mp4) ----

def test_grand_trine_27_oct_2025():
    """26 Oct 2025: 'Mars, Jupiter and Saturn forming grand trine from
    Monday' — separations 119.3 / 122.0 / 118.7 on the 27th."""
    r = saptarsh.regime(datetime.date(2025, 10, 27))
    assert ["Mars", "Jupiter", "Saturn"] in r["grand_trines"]
    assert any("Grand trine" in n for n in r["notes"])
    assert saptarsh.regime(datetime.date(2026, 8, 28))["grand_trines"] == []


def test_mars_jupiter_trine_is_bearish_28_oct():
    d = saptarsh.day(datetime.date(2025, 10, 28))
    got = _aspect(d, "Mars", 120, "Jupiter")
    assert got["tone"] == "bear" and got["source"] == "observed"
    assert d["moon"]["nakshatra"] == "Purva Ashadha"
    assert d["panchang"]["vaar_tithi"]["tone"] == "bull"          # Tue + 7, observed
    assert d["panchang"]["vaar_tithi"]["source"] == "observed"


def test_ingress_readings_sep_oct_2025():
    """23 Sep: 'Mars enters in Swati nakshatra at 20:57 IST. This is
    bearish'. 27 Oct: Mars enters Scorpio (he printed 13:28 — the Moon's
    nakshatra-change time — the ingress is 15:43). 15 Sep: Sun ingress
    Virgo conjunct Mercury 'powerful combination for stock market'."""
    d = saptarsh.day(datetime.date(2025, 9, 23))
    m = [i for i in d["ingresses"] if i["planet"] == "Mars" and i["to"] == "Swati"]
    assert m and abs(_mins(m[0]["time"]) - _mins("20:57")) <= 3 and m[0]["tone"] == "bear"
    d = saptarsh.day(datetime.date(2025, 10, 27))
    m = [i for i in d["ingresses"] if i["planet"] == "Mars" and i["to"] == "Vrischika"]
    assert m and m[0]["tone"] == "bear" and "TRANSITION POINT" in m[0]["note"]
    assert abs(_mins(d["moon"]["nakshatra_change"]["time"]) - _mins("13:28")) <= 3
    d = saptarsh.day(datetime.date(2025, 9, 17))
    s = [i for i in d["ingresses"] if i["planet"] == "Sun" and i["to"] == "Kanya"]
    assert s and s[0]["tone"] == "bull"


def test_mercury_direct_station_11_aug_2025():
    d = saptarsh.day(datetime.date(2025, 8, 11))
    st = [i for i in d["ingresses"] if i["kind"] == "station"]
    assert st and st[0]["planet"] == "Mercury" and st[0]["to"] == "direct"
    assert "reversal" in st[0]["note"]
    assert abs(_mins(d["moon"]["nakshatra_change"]["time"]) - _mins("13:01")) <= 3
    got = _aspect(d, "Moon", 0, "Rahu")
    assert got["tone"] == "bear"
    assert saptarsh.nak_tone("Purva Bhadrapada", "Kumbha", "gold") == ("bear", "observed")


def test_classical_vaar_tithi_scorecard():
    """Six of seven dated calls agree with the classical tables."""
    agree = [(2, 18, "bear"), (1, 8, "bull"), (1, 3, "bull"), (3, 15, "bull"),
             (4, 12, "bear")]
    for wd, t, tone in agree:
        vt = saptarsh.vaar_tithi_yoga(wd, t)
        assert vt and vt["tone"] == tone and vt["source"] == "classical", (wd, t)


# ---- seventh learning pass: X posts of Mar - Jul 2025 (April 2025.mp4) ----

def test_kaal_sarp_july_2025():
    """25 Jul 2025: 'From Monday, Kaal sarp yog is going to break. Mars is
    moving away from Ketu.' Degree-based: all of Sun..Saturn on one side
    of the nodal axis on 21 Jul; Mars past Ketu by early August."""
    assert saptarsh.regime(datetime.date(2025, 7, 21))["kaal_sarp"]
    assert any("Kaal Sarp" in n and "Mars" in n
               for n in saptarsh.regime(datetime.date(2025, 7, 21))["notes"])
    assert not saptarsh.regime(datetime.date(2025, 8, 5))["kaal_sarp"]
    assert not saptarsh.regime(datetime.date(2026, 8, 28))["kaal_sarp"]


def test_kshaya_tithi_19_may_2025():
    """19 May 2025: 'Today is Kshay tithi which is considered as bearish
    for commodities' — Krishna Saptami begins after sunrise and ends
    before the next."""
    d = saptarsh.day(datetime.date(2025, 5, 19))
    assert d["panchang"]["kshaya_tithi"] == "Saptami"
    assert any("Kshaya" in f for f in d["flags"])
    assert any("Kshaya" in w for w in d["calls"]["gold"]["why"])
    assert not any("Kshaya" in w for w in d["calls"]["nifty"]["why"])
    assert saptarsh.day(datetime.date(2025, 5, 18))["panchang"]["kshaya_tithi"] is None


def test_imp_aspects_of_the_april_2025_gold_crash():
    """20-21 Apr 2025 week note: Venus 000 Mn Node 19:09 IMP, Sun 090 Mars
    07:05 IMP -> 'very scary correction' -> gold $3,500 -> $3,263."""
    d = saptarsh.day(datetime.date(2025, 4, 20))
    got = _aspect(d, "Venus", 0, "Rahu")
    assert abs(_mins(got["time"]) - _mins("19:09")) <= 3 and got["tone"] == "bear"
    d = saptarsh.day(datetime.date(2025, 4, 21))
    got = _aspect(d, "Sun", 90, "Mars")
    assert abs(_mins(got["time"]) - _mins("07:05")) <= 3 and got["tone"] == "bear"
    d = saptarsh.day(datetime.date(2025, 5, 15))
    got = _aspect(d, "Jupiter", 90, "Rahu")
    assert abs(_mins(got["time"]) - _mins("17:07")) <= 3 and got["tone"] == "vol"
    d = saptarsh.day(datetime.date(2025, 5, 17))
    got = _aspect(d, "Sun", 45, "Venus")
    assert abs(_mins(got["time"]) - _mins("22:37")) <= 3 and got["tone"] == "bull"


def test_ingress_readings_of_2025():
    for ds, planet, to, tone in [("2025-03-29", "Saturn", "Meena", "bear"),
                                 ("2025-05-14", "Jupiter", "Mithuna", "vol"),
                                 ("2025-06-06", "Mercury", "Mithuna", "vol"),
                                 ("2025-07-16", "Sun", "Kataka", "bull")]:
        d = saptarsh.day(datetime.date.fromisoformat(ds))
        hits = [i for i in d["ingresses"] if i["planet"] == planet and i["to"] == to]
        assert hits and hits[0]["tone"] == tone and hits[0]["source"] == "observed", ds


def test_vaar_tithi_8_jul_2025_override_and_nakshatra_updates():
    d = saptarsh.day(datetime.date(2025, 7, 8))
    assert d["panchang"]["vaar_tithi"] == {"names": ["Vaar-Tithi"], "tone": "bear",
                                           "source": "observed"}
    assert saptarsh.nak_tone("Purva Bhadrapada", "Kumbha", "gold") == ("bear", "observed")
    assert saptarsh.nak_tone("Mula", "Dhanu", "nifty") == ("vol", "observed")
    assert saptarsh.nak_tone("Mula", "Dhanu", "silver") == ("bull", "observed")
