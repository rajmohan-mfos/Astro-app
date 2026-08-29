"""Week-ahead Nifty / Gold / Silver outlook in the Saptarsh Insight style.

Reproduces, day by day, the components of Saptarsh's daily bulletins —
the Telegram "Saptarsh Insight" posts (Nifty) and the "Gold & Silver
Premium Report" images on X (@sonisunil59, Sunil J. Soni, Gujarat):

  * Moon sign + nakshatra during the session, with change times
  * panchang end-times; Vishti karana, Vaidhriti / Vyatipata yoga
  * Vaar-Tithi yoga (weekday x tithi, classical tables)
  * Rahu Kaal, Yamaganda, Gulika Kaal, Abhijit from sunrise-sunset
  * exact-time aspects at 0/45/60/90/120/135/150/180 between Sun, Moon,
    Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto, Rahu
  * lunar / solar eclipse on the date
  * a Nifty, Gold and Silver call built from those, NSE session windows
    for Nifty and 03:30-27:30 IST (Globex) windows with ET for metals
  * a slow-moving "regime" block: Jupiter's sidereal sign, Sun+Ketu,
    and the conjunction calendar (planets sharing a sign, entry/exit)

Every label carries a `source`: "observed" means the channel wrote that
exact call in its Jul-Aug 2026 posts; "extrapolated" means it comes
from the simple rule below (nakshatra lord / aspect family) and has NOT
been seen in their output. Nothing here is backtested.

Sidereal Lahiri like engine.py (the channel's tables imply it). Aspect
separations are ayanamsa-free.
"""
import datetime

import swisseph as swe

from . import nse_holidays
from .engine import FLAGS
from .names import NAKSHATRAS, RASIS, THITHIS
from .transit import DASHA_LORDS, SEG, _next_cross, _panchang_ends

TZ = 5.5
IST = datetime.timezone(datetime.timedelta(hours=TZ))
OPEN_H, CLOSE_H = 9.25, 15.5           # NSE 09:15 - 15:30
METAL_OPEN_H, METAL_CLOSE_H = 3.5, 27.5  # the report's Globex day, IST

BODIES = [("Sun", swe.SUN), ("Moon", swe.MOON), ("Mercury", swe.MERCURY),
          ("Venus", swe.VENUS), ("Mars", swe.MARS), ("Jupiter", swe.JUPITER),
          ("Saturn", swe.SATURN), ("Uranus", swe.URANUS),
          ("Neptune", swe.NEPTUNE), ("Pluto", swe.PLUTO),
          ("Rahu", swe.MEAN_NODE)]          # the channel's "Mn Node"
ANGLES = [0, 45, 60, 72, 90, 120, 135, 144, 150, 180]
ASPECT_NAMES = {0: "conjunction", 45: "semi-square", 60: "sextile",
                72: "quintile", 90: "square", 120: "trine",
                135: "sesquiquadrate", 144: "biquintile", 150: "quincunx",
                180: "opposition"}
INGRESS_BODIES = [("Sun", swe.SUN), ("Mercury", swe.MERCURY),
                  ("Venus", swe.VENUS), ("Mars", swe.MARS),
                  ("Jupiter", swe.JUPITER), ("Saturn", swe.SATURN),
                  ("Uranus", swe.URANUS)]     # 16 Dec 2024: "Uranus enters Aries at 11:24"
SIGN_EN = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra",
           "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

# 1-based segment (of 8 between sunrise and sunset) per weekday Mon..Sun.
RAHU_SEG = [2, 7, 5, 6, 4, 3, 8]
YAMA_SEG = [4, 3, 2, 1, 7, 6, 5]
GULIKA_SEG = [6, 5, 4, 3, 2, 1, 7]

# ---------------------------------------------------------- rule tables
# (a, b, angle) -> tone, exactly as the channel labelled them. Pairs are
# stored in BODIES order (Sun before Moon before Mercury ...).
OBSERVED_ASPECTS: dict[tuple[str, str, int], str] = {
    ("Sun", "Moon", 135): "bull",
    ("Sun", "Mercury", 0): "bull",
    ("Sun", "Neptune", 150): "bull",
    ("Sun", "Pluto", 150): "bear",
    ("Moon", "Mercury", 135): "bull",
    ("Moon", "Mercury", 180): "neutral",
    ("Moon", "Venus", 90): "bear",
    ("Moon", "Venus", 120): "bull",
    ("Moon", "Mars", 135): "bull",
    ("Moon", "Mars", 150): "bull",
    ("Moon", "Jupiter", 150): "bull",
    ("Moon", "Jupiter", 180): "bear",
    ("Moon", "Saturn", 45): "bear",
    ("Moon", "Saturn", 60): "bull",
    ("Moon", "Saturn", 90): "bear",
    ("Moon", "Uranus", 90): "bear",
    ("Moon", "Uranus", 120): "bull",
    ("Moon", "Uranus", 135): "vol",
    ("Moon", "Neptune", 45): "bear",
    ("Moon", "Rahu", 0): "bear",
    ("Moon", "Rahu", 45): "bear",
    ("Mercury", "Neptune", 150): "vol",
    ("Mercury", "Pluto", 150): "vol",
    ("Mercury", "Rahu", 180): "vol",
    # X premium reports (metals), Jul-Aug 2026
    ("Sun", "Jupiter", 120): "bull",        # 27 Jul "Sun-Jupiter become bullish"
    ("Moon", "Pluto", 0): "bull",           # 2 Jul
    ("Venus", "Rahu", 150): "vol",          # 29 Jul "will affect silver"
    # X premium reports, May-Jun 2026 (the earlier prose format)
    ("Sun", "Moon", 72): "bear",            # 10 Jun "strong bearish"
    ("Sun", "Moon", 120): "bear",           # 26 May
    ("Sun", "Saturn", 60): "bear",          # 3 Jun
    ("Moon", "Venus", 0): "bear",           # 19 May "bearish for 1-2 hours"
    ("Moon", "Mars", 0): "bull",            # 15 May "bullish for few hours"
    ("Moon", "Jupiter", 0): "bear",         # 20 May "bearish for few hrs"
    ("Moon", "Saturn", 0): "bull",          # 10 Jun "strong bullish"
    ("Moon", "Saturn", 180): "bull",        # 26 May
    ("Moon", "Uranus", 60): "bear",         # 9 Jun
    ("Moon", "Neptune", 0): "bear",         # 9 Jun
    ("Moon", "Rahu", 60): "bear",           # 2 Jun
    ("Mercury", "Saturn", 90): "vol",       # 10 Jun "high volatile"
    ("Venus", "Jupiter", 0): "bear",        # 10 Jun "strong bearish for the day"
    ("Venus", "Uranus", 45): "vol",         # 2 Jun
    ("Mars", "Pluto", 90): "vol",           # 26 May
    # X posts, Nov 2025 - Jan 2026
    ("Sun", "Pluto", 0): "bear",            # 20 Jan "Sun and Pluto at 0° this week … many times tops"
    ("Moon", "Rahu", 180): "bull",          # 14 Nov "Moon-Ketu at 0° … is bullish" (Ketu = Rahu+180)
    # X posts, Jul-Oct 2025
    ("Mars", "Jupiter", 120): "bear",       # 27-28 Oct "Mars 120° Jupiter is bearish" (a soft angle!)
    # X week notes, Apr-May 2025 (the earliest reports)
    ("Sun", "Mars", 90): "bear",            # 21 Apr 2025 "IMP … very scary correction" (gold -7% in 2 days)
    ("Venus", "Rahu", 0): "bear",           # 20 Apr 2025 "IMP", same note
    ("Venus", "Uranus", 60): "vol",         # 20 Apr 2025 "IMP"
    ("Sun", "Saturn", 45): "bear",          # 2 May 2025 "can affect the stock market, little impact on metals"
    ("Mars", "Jupiter", 45): "bull",        # 2 May 2025 "bullish for precious metals"
    ("Mercury", "Jupiter", 60): "vol",      # 2 May 2025 "little volatility"
    ("Jupiter", "Rahu", 90): "vol",         # 16 May 2025 "Volatility"
    ("Sun", "Venus", 45): "bull",           # 16 May 2025 "Bullish … can pull the market any side"
    # X Nifty / metals reports, Jan-Mar 2025
    ("Sun", "Rahu", 45): "bear",            # 3 Feb 2025 "negative and high volatility is expected"
    ("Sun", "Saturn", 0): "bear",           # 27 Feb 2025 "bearish for whole metal sector including copper"
    # X posts, Nov-Dec 2024 (the launch)
    ("Moon", "Uranus", 0): "vol",           # 13 Dec 2024 "Moon-Uranus conjunction will create volatility"
    ("Venus", "Neptune", 45): "vol",        # 16 Dec 2024 week note "very important, can turn the market one way"
    ("Sun", "Neptune", 90): "vol",          # same note
    ("Venus", "Jupiter", 120): "bear",      # same note: "Friday aspects are bearish"
    ("Sun", "Mars", 144): "bear",           # same note
    # X posts, Feb-May 2024 (the origins)
    ("Mars", "Saturn", 0): "vol",           # 8 Apr 2024 "Mars 0 Sat, Sun 0 Mer are trend changer. Must watch for commodities"
    ("Jupiter", "Uranus", 0): "vol",        # 21 Apr 2024 "potential to change the direction in all markets. Uranus is unpredictable"
    # (Sun 0 Mercury: "triggering a market drop … 2nd event of bearish
    # trend" on 28 Feb 2024, "trend changer" 8 Apr 2024, yet "Bullish"
    # in the 27 Aug 2026 table — kept as his latest label, bullish)
    # X posts, May-Oct 2024 (before the launch)
    ("Sun", "Pluto", 180): "bear",          # 23 Jul 2024 "responsible for huge drop in gold and silver"
    ("Sun", "Saturn", 120): "bull",         # 17 Jul 2024 "bullish yog involving the Sun and Saturn is ending"
    ("Sun", "Saturn", 90): "bear",          # 30 May 2024 colour-coded list: red
    ("Sun", "Pluto", 135): "bear",          # same list: orange
    ("Sun", "Neptune", 72): "bull",         # same list: green
    ("Sun", "Rahu", 60): "bull",            # same list: green (Sun 60 Mn Node)
    ("Jupiter", "Pluto", 120): "bull",      # same list: green
    # (the same note lists "Venus 90 Uranus" on 26 Jun — the sky had
    # Venus 45 Uranus at 00:31; that pair is already observed above)
    ("Mercury", "Saturn", 120): "vol",      # 23 Jun 2024 week note "sudden change … high volatility"
    ("Mercury", "Jupiter", 45): "vol",      # same note
}

# Sign / nakshatra ingresses the reports commented on: (planet, kind, to)
# -> (tone, their words). Anything else is listed as "watch".
INGRESS_NOTES: dict[tuple[str, str, str], tuple[str, str]] = {
    ("Jupiter", "sign", "Kataka"): ("bear", "16 Oct 2025: \"Sidereal Jupiter enters Cancer, its exalted sign. Major change in markets\"; 2 Jun: \"can affect the market heavily for long term … bearish last Oct, careful for few days\""),
    ("Mars", "nakshatra", "Swati"): ("bear", "23 Sep 2025: \"Mars enters in Swati nakshatra … This is bearish\""),
    ("Mars", "sign", "Vrischika"): ("bear", "27 Oct 2025: \"strong bearish for precious metals for 1-2 days … MARS AT TRANSITION POINT … MAY DOMINATE all bullish yog\""),
    ("Sun", "sign", "Kanya"): ("bull", "15 Sep 2025: \"Sun ingress Virgo, conjunct with Mercury. This is powerful combination for stock market. BANKNIFTY may outperform\""),
    ("Jupiter", "nakshatra", "Ashlesha"): ("bull", "19 Aug: \"considered bullish for stock markets\""),
    ("Venus", "nakshatra", "Ardra"): ("bear", "20 May: \"bearish for Silver\""),
    ("Venus", "nakshatra", "Bharani"): ("bear", "6 Apr: \"this is bearish\""),
    ("Mars", "nakshatra", "Uttara Bhadrapada"): ("bull", "6 Apr: \"bullish for gold and silver\""),
    ("Venus", "sign", "Kataka"): ("bull", "8 Jun: \"bullish for Silver but not immediately\""),
    ("Mercury", "nakshatra", "Ardra"): ("bear", "2 Jun: \"slightly bearish\""),
    ("Mercury", "nakshatra", "Rohini"): ("neutral", "19 May: \"not much significant for precious metal market\""),
    ("Sun", "nakshatra", "Pushya"): ("bull", "20 Jul: \"slightly bullish\""),
    ("Sun", "nakshatra", "Anuradha"): ("bull", "19 Nov 2025: \"this is bullish\""),
    ("Venus", "nakshatra", "Vishakha"): ("bear", "18 Nov 2025: \"slightly bearish for silver\""),
    ("Mars", "nakshatra", "Shravana"): ("bull", "26 Jan 2026: \"also bullish for silver\""),
    ("Jupiter", "sign", "Mithuna"): ("vol", "16 May 2025: \"favourable for stock markets and slightly bearish for precious metals\"; 5 Dec 2025: \"enters Mercury's sign, difficult to predict. Something big in Banking sector\""),
    ("Sun", "sign", "Kataka"): ("bull", "16 Jul 2025: \"Sun changes sign and enters in Cancer and conjunct with Mercury. This is trend changing event … We may start upward journey\""),
    ("Mercury", "sign", "Mesha"): ("vol", "6 May 2025: \"Mercury is changing sign and entering in Aries and conjunct with the Sun. This is significant event and there may reversal in many markets\""),
    ("Mercury", "sign", "Mithuna"): ("vol", "5 Jun 2025: \"Mercury enters in Gemini, its own sign … conjunct with Jupiter. In past it created high volatility. Max 8% up from low and down from high\""),
    ("Saturn", "sign", "Meena"): ("bear", "28 Mar 2025: \"Sun eclipse on 29 March and Saturn also change sign. This may be last phase of bullish trend\""),
    ("Venus", "sign", "Meena"): ("bear", "28 Jan 2025: \"Venus is enters in Pisces, this is slightly bearish\" (metals)"),
    ("Uranus", "sign", "Mesha"): ("vol", "16 Dec 2024: \"Nifty made day's low at 10:45 IST while Uranus enters in Aries at 11:24 IST. We should believe that today's volatility was only due to the Uranus\""),
    ("Mercury", "sign", "Meena"): ("bear", "27 Feb 2025: \"Mercury enters in Pisces, this is not favorable\" (metals)"),
    ("Sun", "sign", "Vrishabha"): ("neutral", "16 May 2025: \"favourable for stock markets and slightly bearish for precious metals\"; 15 May 2026: \"trend changer but not for metals\""),
    ("Mercury", "sign", "Vrishabha"): ("neutral", "15 May: \"trend changer but not for metals\""),
}
BENEFIC = {"Venus", "Jupiter", "Mercury", "Sun", "Moon"}
HEAVY = {"Saturn", "Rahu", "Pluto"}
OUTER = {"Uranus", "Neptune", "Pluto"}


def aspect_tone(a: str, b: str, angle: int) -> tuple[str, str]:
    """(tone, source) for a pair at an angle."""
    if (a, b, angle) in OBSERVED_ASPECTS:
        return OBSERVED_ASPECTS[(a, b, angle)], "observed"
    other = b if a in ("Sun", "Moon") else a
    if angle in (60, 120):
        return "bull", "extrapolated"
    if angle == 0:
        if other in HEAVY:
            return "bear", "extrapolated"
        if other in OUTER or other == "Mars":
            return "vol", "extrapolated"
        return "bull", "extrapolated"
    if angle in (45, 90, 180):
        return ("vol" if {a, b} & {"Mercury"} and other in OUTER
                else "bear"), "extrapolated"
    if angle in (72, 144):
        # quintile family: seen once (Sun 72 Moon, bearish); no rule
        return "neutral", "extrapolated"
    # 135 / 150
    if other in HEAVY:
        return "bear", "extrapolated"
    if other in OUTER:
        return "vol", "extrapolated"
    return "bull", "extrapolated"


# Moon nakshatra -> (nifty, metals) as the channel called it. None means
# no clean base call was seen for that instrument. Nifty column from the
# Telegram posts (19-28 Aug); metals column from the X premium reports
# (2 Jul - 19 Aug) plus the Telegram Gold/Silver lines.
OBSERVED_NAK: dict[str, tuple[str | None, str | None]] = {
    "Ashwini": ("bear", "bull"),            # Nifty "not favourable, bearish effects" 13 Mar 2024; metals 15 May, 8-9 Jul
    "Bharani": ("bear", "bear"),            # Nifty "not favourable" 14 Mar 2024; metals 15 May, 9 Jul
    "Krittika": ("neutral", "bull"),        # Nifty "neutral to slightly positive" 10 Jan 2025; metals 4 Dec 2025
    "Rohini": ("bull", "bear"),             # Nifty "supportive" 10 Jan, 7 Feb 2025; metals bearish 10 Jan, 4 Dec 2025, 10 Aug
    "Mrigashira": ("bull", "bull"),         # Nifty "supportive for higher prices" 7 Jun 2024; metals 19 May
    "Ardra": (None, "bear"),                # 19-20 May, 10 Aug
    "Punarvasu": ("bull", "bear"),          # Nifty "favourable for stocks" 19 Mar 2024; metals 20 May, 14 Jul
    "Pushya": ("bull", "bull"),             # Nifty "supportive" 20 Mar 2024; metals bullish 23 Apr, 21 May; bearish 15 Jul (2 of 3)
    "Ashlesha": ("bull", "neutral"),        # Dow "favourable for stocks" 17 Apr 2024; metals 15 Jul
    "Magha": ("bear", None),                # Nifty "not supportive … consider it as a bearish" 16 May 2024; Dow "unpredictable" 20 Dec 2024
    "Uttara Phalguni": (None, "bull"),      # 14 Nov 2025
    "Hasta": ("bull", "bear"),              # Nifty "favourable / supportive" 23-24 Dec 2024; metals 26 May, 20 Jul
    "Chitra": ("bull", "bull"),             # Nifty supportive 24 Dec 2024, 17 Feb 2025; neutral 27 Nov 2024 (2 of 3); metals 20 Jul
    "Swati": ("bear", "bear"),              # Nifty 18 Feb 2025, 18 Aug; metals bearish 18-19 Nov 2025, both sides 18 Aug
    "Vishakha": ("vol", "vol"),             # Nifty "not supportive" 20 Feb 2025 vs "slightly positive" 19 Aug; metals mixed
    "Anuradha": ("neutral", "bull"),        # Nifty: not supportive 20 Feb 2025 & 20 Aug, supportive 21 Feb 2025 & 21 Aug (2-2);
                                            # metals bullish 6 Apr, 4 May; both sides 21 Aug
    "Jyeshtha": ("bull", "vol"),            # bearish 4 May; both sides 21 Aug
    "Mula": ("bear", "bull"),               # Nifty: "not favourable" 5 Mar & 1 Apr 2024, "bearish" 5 Nov 2024, "not supportive" 30 Dec 2024, "high volatility" 9 Jul 2025;
                                            # metals bullish 5 Nov 2024, 27 Oct 2025, 8 Apr, 2 Jun; bearish 27 Jul (4 of 5)
    "Purva Ashadha": ("bull", "bear"),      # Nifty favourable 29 Apr 2024, 6 Nov 2024, 24 Aug 2026; metals 6 Nov 2024, 2-3 Jun, 28 Jul
    "Uttara Ashadha": ("bull", "bull"),     # Nifty "supportive for stocks" 1 Jan 2025; metals 9 Jun, 2 Jul, 28-29 Jul, 25 Aug (once "not much supportive", 28 Jan 2025)
    "Shravana": ("neutral", "bear"),        # 26 Aug / 2 Jul, 29 Jul
    "Dhanishta": ("bull", "bull"),
    "Shatabhisha": ("bear", "bear"),        # 8 Jun, 28 Aug
    "Purva Bhadrapada": ("bull", "bear"),   # Nifty "bullish for stocks" 11 Nov 2024; metals bearish 11 Nov 2024, 21 May 2025, 11 Aug 2025; bullish 8 Jun 2026 (3 of 4)
    "Uttara Bhadrapada": ("neutral", "bull"),  # Nifty "not favourable" 11 Mar 2024, "neutral" 28 Jun 2024; metals 16 Apr, 10 Jun, 7 Jul
    "Revati": ("neutral", "bear"),          # Nifty "little favourable" 12 Mar 2024, "neutral" 3 Feb 2025; metals 10 Jun, 7-8 Jul; "neutral" 16 Apr
}
# Moon SIGN -> metals bias, only where the report printed one next to
# the sign itself (used when the nakshatra is unobserved). Kumbha was
# "bearish" on 6 Jul and "slight bullish" on 8 Jun — the two-vote side.
OBSERVED_SIGN_METALS = {"Makara": "bull", "Kumbha": "bear", "Meena": "bear",
                        "Kataka": "bear", "Mithuna": "neutral",
                        "Dhanu": "bear", "Kanya": "neutral"}

# Vaar-Nakshatra yoga ("combination of Nakshatra and Vaar", 21 May):
# classical Sarvartha Siddhi / Amrita Siddhi (auspicious) and
# Yamaghanta / Mrityu (inauspicious) tables, weekday Mon=0 .. Sun=6.
SARVARTHA = {
    6: {"Hasta", "Mula", "Uttara Phalguni", "Uttara Ashadha", "Uttara Bhadrapada", "Pushya", "Ashwini"},
    0: {"Shravana", "Rohini", "Mrigashira", "Pushya", "Anuradha"},
    1: {"Ashwini", "Uttara Bhadrapada", "Krittika", "Ashlesha"},
    2: {"Rohini", "Anuradha", "Hasta", "Krittika", "Mrigashira"},
    3: {"Revati", "Anuradha", "Ashwini", "Punarvasu", "Pushya"},
    4: {"Revati", "Anuradha", "Ashwini", "Punarvasu", "Shravana"},
    5: {"Shravana", "Rohini", "Swati"},
}
AMRITA = {6: "Hasta", 0: "Mrigashira", 1: "Ashwini", 2: "Anuradha",
          3: "Pushya", 4: "Revati", 5: "Rohini"}
YAMAGHANTA = {6: "Magha", 0: "Vishakha", 1: "Ardra", 2: "Mula",
              3: "Krittika", 4: "Rohini", 5: "Hasta"}
MRITYU_NAK = {6: "Anuradha", 0: "Uttara Ashadha", 1: "Shatabhisha",
              2: "Ashwini", 3: "Mrigashira", 4: "Ashlesha", 5: "Hasta"}


# (weekday, nakshatra) he called explicitly where the classical tables
# are silent or disagree: 12 Dec 2024 (Thu, Ashwini->Bharani at 09:53)
# "Vaar-Nakshatra yog is bearish" — classical has Thu+Ashwini auspicious.
OBSERVED_VAAR_NAK = {(3, "Bharani"): "bear", (3, "Ashwini"): "bear"}


def vaar_nakshatra_yoga(weekday: int, nak: str) -> dict | None:
    if (weekday, nak) in OBSERVED_VAAR_NAK:
        return {"names": ["Vaar-Nakshatra"], "tone": OBSERVED_VAAR_NAK[(weekday, nak)],
                "source": "observed"}
    hits = []
    if nak in SARVARTHA.get(weekday, ()):
        hits.append(("Sarvartha Siddhi", "bull"))
    if AMRITA.get(weekday) == nak:
        hits.append(("Amrita Siddhi", "bull"))
    if YAMAGHANTA.get(weekday) == nak:
        hits.append(("Yamaghanta", "bear"))
    if MRITYU_NAK.get(weekday) == nak:
        hits.append(("Mrityu", "bear"))
    if not hits:
        return None
    return {"names": [h[0] for h in hits],
            "tone": "bear" if any(h[1] == "bear" for h in hits) else "bull",
            "source": "classical"}
LORD_TONE = {"Venus": "bull", "Jupiter": "bull", "Mercury": "bull",
             "Mars": "bull", "Moon": "neutral", "Sun": "neutral",
             "Saturn": "bear", "Rahu": "bear", "Ketu": "bear"}
TONE_WORD = {"bull": "bullish", "bear": "bearish", "vol": "volatile",
             "neutral": "neutral"}


def nak_tone(nak: str, sign: str, instrument: str) -> tuple[str, str]:
    idx = NAKSHATRAS.index(nak)
    obs = OBSERVED_NAK.get(nak)
    col = 0 if instrument == "nifty" else 1
    if obs and obs[col]:
        return obs[col], "observed"
    if instrument != "nifty" and sign in OBSERVED_SIGN_METALS:
        return OBSERVED_SIGN_METALS[sign], "observed"
    return LORD_TONE[DASHA_LORDS[idx % 9]], "extrapolated"


# Vaar-Tithi yoga: weekday x tithi (1-15 within the paksha), from the
# classical muhurta tables. The channel prints "Vaar-Tithi yog is
# bullish / bearish" without publishing its table, so these are the
# standard ones, labelled classical. Weekday index Mon=0 .. Sun=6.
NANDA, BHADRA, JAYA, RIKTA, PURNA = {1, 6, 11}, {2, 7, 12}, {3, 8, 13}, {4, 9, 14}, {5, 10, 15}
SIDDHA = {4: NANDA, 2: BHADRA, 1: JAYA, 5: RIKTA, 3: PURNA}
MRITYU = {6: NANDA, 1: NANDA, 0: BHADRA, 4: BHADRA, 2: JAYA, 3: RIKTA, 5: PURNA}
DAGDHA = {6: 12, 0: 11, 1: 5, 2: 3, 3: 6, 4: 8, 5: 9}
VISHA = {6: 4, 0: 6, 1: 7, 2: 2, 3: 8, 4: 9, 5: 7}
HUTASANA = {6: 12, 0: 6, 1: 7, 2: 8, 3: 9, 4: 10, 5: 11}


# (weekday, tithi 1-30) the reports called explicitly. The classical
# tables agree where they speak (Tue+3 Siddha = "bullish" 19 May; Wed+3
# Mrityu/Dagdha = "bearish" 3 Jun; Thu+15 Siddha = "bullish" 4 Dec;
# Fri+12 Mrityu = "bearish" 30 Jan) and are silent on these. Keyed by the
# FULL tithi because his table distinguishes paksha: Tuesday + Shukla 14
# was "bullish" (28 Jul) and Tuesday + Krishna 14 "bearish" (18 Nov).
OBSERVED_VAAR_TITHI = {(4, 29): "bear",     # Fri 15 May "Vaar-Tithi yog is bearish"
                       (0, 13): "bear",     # Mon 27 Jul
                       (1, 14): "bull",     # Tue 28 Jul
                       (1, 29): "bear",     # Tue 18 Nov 2025
                       (1, 7): "bull",      # Tue 28 Oct 2025 (classical says Visha/Hutasana)
                       (1, 13): "bear",     # Tue 8 Jul 2025 (classical says Siddha)
                       (2, 9): "bear",      # Wed 8 Jan 2025
                       (4, 11): "bear",     # Fri 10 Jan 2025 (classical says Siddha)
                       (2, 22): "bear",     # Wed 19 Feb 2025 (classical says Siddha)
                       (1, 4): "bull",      # Tue 5 Nov 2024 "Tithi and Vaar combination is bullish"
                       (2, 11): "bear",     # Wed 11 Dec 2024
                       (4, 13): "bear"}     # Fri 13 Dec 2024
# Scorecard of the classical tables against his dated calls: 19 May, 3
# Jun, 4 Dec, 30 Jan, 10 Sep 2025, 30 Sep 2025 agree; 28 Oct 2025, 8 Jul
# 2025, 10 Jan 2025 and 19 Feb 2025 do not (6 of 10). His table is his
# own; the observed overrides above take precedence wherever he spoke.


def vaar_tithi_yoga(weekday: int, tithi_num: int) -> dict | None:
    t = (tithi_num - 1) % 15 + 1
    if (weekday, tithi_num) in OBSERVED_VAAR_TITHI:
        return {"names": ["Vaar-Tithi"],
                "tone": OBSERVED_VAAR_TITHI[(weekday, tithi_num)],
                "source": "observed"}
    hits = []
    if t in SIDDHA.get(weekday, ()):
        hits.append(("Siddha", "bull"))
    if t in MRITYU.get(weekday, ()):
        hits.append(("Mrityu", "bear"))
    if DAGDHA.get(weekday) == t:
        hits.append(("Dagdha", "bear"))
    if VISHA.get(weekday) == t:
        hits.append(("Visha", "bear"))
    if HUTASANA.get(weekday) == t:
        hits.append(("Hutasana", "bear"))
    if not hits:
        return None
    return {"names": [h[0] for h in hits],
            "tone": "bear" if any(h[1] == "bear" for h in hits) else "bull",
            "source": "classical"}


# ---------------------------------------------------------- ephemeris

def _jd_local(d: datetime.date, hour: float) -> float:
    return swe.julday(d.year, d.month, d.day, hour - TZ)


def _hhmm(jd: float, jd0: float) -> str:
    """Clock time on the civil day of jd0; '+1' suffix past midnight."""
    total = round((jd - jd0) * 1440)
    day, rem = divmod(total, 1440)
    h, m = divmod(rem, 60)
    return f"{h:02d}:{m:02d}" + (f" (+{day})" if day else "")


def _hhmm24(jd: float, jd0: float) -> str:
    """The report's Vedic-day clock: hours run past 24 (27:30)."""
    total = round((jd - jd0) * 1440)
    return f"{total // 60:02d}:{total % 60:02d}"


def _us_dst(dt_utc: datetime.datetime) -> bool:
    """US daylight time: 2nd Sunday of March 07:00 UTC .. 1st Sunday of
    November 06:00 UTC (the 02:00 local switch expressed in UTC)."""
    y = dt_utc.year
    mar = datetime.datetime(y, 3, 1, 7, tzinfo=datetime.timezone.utc)
    mar += datetime.timedelta(days=(6 - mar.weekday()) % 7 + 7)
    nov = datetime.datetime(y, 11, 1, 6, tzinfo=datetime.timezone.utc)
    nov += datetime.timedelta(days=(6 - nov.weekday()) % 7)
    return mar <= dt_utc < nov


def _et(jd: float) -> str:
    """Clock time in US Eastern (the report prints IST / ET side by side)."""
    y, m, d, h = swe.revjul(jd)
    # round to the minute as one quantity — 13:04:59.98 must print 13:05
    utc = datetime.datetime(y, m, d, tzinfo=datetime.timezone.utc) \
        + datetime.timedelta(minutes=round(h * 60))
    off = -4 if _us_dst(utc) else -5
    loc = utc + datetime.timedelta(hours=off)
    return f"{loc.hour:02d}:{loc.minute:02d}"


def _lon(body: int, jd: float) -> float:
    return swe.calc_ut(jd, body, FLAGS)[0][0] % 360


def _wrap(x: float) -> float:
    return -((-x + 180) % 360 - 180)


def _rise_set(d: datetime.date, lat: float, lon: float) -> tuple[float, float]:
    jd_mid = _jd_local(d, 0)
    geo = (lon, lat, 0)
    r = swe.rise_trans(jd_mid, swe.SUN, swe.CALC_RISE, geo, 0, 0, swe.FLG_MOSEPH)
    s = swe.rise_trans(jd_mid, swe.SUN, swe.CALC_SET, geo, 0, 0, swe.FLG_MOSEPH)
    if r[0] != 0 or s[0] != 0:
        raise ValueError("sunrise/sunset not found")
    return r[1][0], s[1][0]


def kaal_windows(d: datetime.date, lat: float, lon: float) -> dict:
    jd0 = _jd_local(d, 0)
    rise, sset = _rise_set(d, lat, lon)
    seg = (sset - rise) / 8
    w = d.weekday()

    def win(n: int) -> list[str]:
        return [_hhmm(rise + (n - 1) * seg, jd0), _hhmm(rise + n * seg, jd0)]

    muh = (sset - rise) / 15
    return {
        "sunrise": _hhmm(rise, jd0), "sunset": _hhmm(sset, jd0),
        "rahu_kaal": win(RAHU_SEG[w]), "yamaganda": win(YAMA_SEG[w]),
        "gulika_kaal": win(GULIKA_SEG[w]),
        "abhijit": [_hhmm(rise + 7 * muh, jd0), _hhmm(rise + 8 * muh, jd0)],
        "_rahu_jd": (rise + (RAHU_SEG[w] - 1) * seg, rise + RAHU_SEG[w] * seg),
    }


def moon_path(d: datetime.date) -> dict:
    """Sign / nakshatra at the open and any change before the close."""
    jd0 = _jd_local(d, 0)
    jd_open, jd_close = _jd_local(d, OPEN_H), _jd_local(d, CLOSE_H)
    moon = lambda j: _lon(swe.MOON, j)         # noqa: E731
    lon_open = moon(jd_open)
    sign_i, nak_i = int(lon_open // 30), int(lon_open // SEG)
    out = {"sign": RASIS[sign_i], "sign_en": SIGN_EN[sign_i],
           "nakshatra": NAKSHATRAS[nak_i],
           "pada": int((lon_open % SEG) // (SEG / 4)) + 1,
           "sign_change": None, "nakshatra_change": None, "_events": []}
    c = _next_cross(moon, ((sign_i + 1) * 30) % 360, jd_open, jd_close, 1 / 24)
    if c is not None:
        out["sign_change"] = {"time": _hhmm(c, jd0),
                              "to": RASIS[(sign_i + 1) % 12]}
        out["_events"].append((c, f"Moon enters {RASIS[(sign_i + 1) % 12]}"))
    c = _next_cross(moon, ((nak_i + 1) * SEG) % 360, jd_open, jd_close, 1 / 24)
    if c is not None:
        out["nakshatra_change"] = {"time": _hhmm(c, jd0),
                                   "to": NAKSHATRAS[(nak_i + 1) % 27]}
        out["_events"].append((c, f"Moon enters {NAKSHATRAS[(nak_i + 1) % 27]}"))
    return out


def day_aspects(d: datetime.date) -> list[dict]:
    """Exact aspects between 00:00 and 24:00 IST on d, with clock times."""
    jd0, jd1 = _jd_local(d, 0), _jd_local(d, 24)
    step = 1 / 48
    n = int(round((jd1 - jd0) / step))
    grid = [jd0 + i * step for i in range(n + 1)]
    pos = {name: [_lon(b, j) for j in grid] for name, b in BODIES}
    found = []
    for i, (a, ba) in enumerate(BODIES):
        for b, bb in BODIES[i + 1:]:
            diffs = [_wrap(x - y) for x, y in zip(pos[a], pos[b])]
            for ang in ANGLES:
                for t in {_wrap(ang), _wrap(-ang)}:
                    g = [_wrap(x - t) for x in diffs]
                    for k in range(1, len(g)):
                        if g[k - 1] * g[k] <= 0 and g[k - 1] != g[k] \
                                and abs(g[k] - g[k - 1]) < 180:
                            def f(j, t=t):
                                return _wrap(_lon(ba, j) - _lon(bb, j) - t)
                            lo, hi = grid[k - 1], grid[k]
                            flo = f(lo)
                            for _ in range(30):
                                mid = (lo + hi) / 2
                                if (f(mid) < 0) == (flo < 0):
                                    lo, flo = mid, f(mid)
                                else:
                                    hi = mid
                            jd = (lo + hi) / 2
                            tone, src = aspect_tone(a, b, ang)
                            found.append({
                                "_jd": jd, "time": _hhmm(jd, jd0),
                                "et": _et(jd),
                                "a": a, "angle": ang, "b": b,
                                "name": ASPECT_NAMES[ang],
                                "tone": tone, "source": src,
                                "in_session": OPEN_H <= (jd - jd0) * 24 <= CLOSE_H,
                            })
    found.sort(key=lambda x: x["_jd"])
    # a 0°/180° hit can register on both signed targets — keep one
    dedup, last = [], None
    for x in found:
        key = (x["a"], x["b"], x["angle"], round(x["_jd"] * 24))
        if key != last:
            dedup.append(x)
        last = key
    return dedup


def day_ingresses(d: datetime.date) -> list[dict]:
    """Sign and nakshatra changes of Sun..Saturn between 00:00 and 24:00
    IST — the reports list these under "Important Astro. Event"."""
    jd0, jd1 = _jd_local(d, 0), _jd_local(d, 24)
    out = []
    for name, body in INGRESS_BODIES:
        fn = lambda j, b=body: _lon(b, j)          # noqa: E731
        lon0 = fn(jd0)
        retro = swe.calc_ut(jd0, body, FLAGS)[0][3] < 0
        for kind, size, names in (("sign", 30.0, RASIS),
                                  ("nakshatra", SEG, NAKSHATRAS)):
            i = int(lon0 // size)
            n = len(names)
            if retro:
                target, to = (i * size) % 360, names[(i - 1) % n]
            else:
                target, to = ((i + 1) * size) % 360, names[(i + 1) % n]
            c = _next_cross(fn, target, jd0, jd1, 1 / 24, decreasing=retro)
            if c is None:
                continue
            tone, note = INGRESS_NOTES.get((name, kind, to), (None, None))
            out.append({"_jd": c, "time": _hhmm(c, jd0), "et": _et(c),
                        "planet": name, "kind": kind, "to": to,
                        "tone": tone or "neutral",
                        "source": "observed" if note else "extrapolated",
                        "note": note or ("a slow planet changing sign is a "
                                         "'trend changer' in their reading — watch"
                                         if kind == "sign" and name in
                                         ("Jupiter", "Saturn", "Mars")
                                         else "listed, no reading given")})
    # "out of bound of the Sun": a planet leaving the combustion orb.
    # 11 Mar 2024: "Mercury is out of bound of the Sun. This may turn
    # negative for medium term"; 19 Mar 2024: "Saturn is moving out of
    # bound. This can be trend changer specially in metals and crude oil".
    # Classical orbs: Mercury 12 (14 retro), Venus 10 (8), Mars 17,
    # Jupiter 11, Saturn 15.
    sun0, sun1 = _lon(swe.SUN, jd0), _lon(swe.SUN, jd1)
    for name, body, orb in (("Mercury", swe.MERCURY, 12), ("Venus", swe.VENUS, 10),
                            ("Mars", swe.MARS, 17), ("Jupiter", swe.JUPITER, 11),
                            ("Saturn", swe.SATURN, 15)):
        def gap(j, b=body):
            x = abs(_lon(b, j) - _lon(swe.SUN, j)) % 360
            return min(x, 360 - x)
        g0, g1 = gap(jd0), gap(jd1)
        if (g0 < orb) != (g1 < orb):
            lo, hi = jd0, jd1
            for _ in range(30):
                mid = (lo + hi) / 2
                if (gap(mid) < orb) == (g0 < orb):
                    lo = mid
                else:
                    hi = mid
            c = (lo + hi) / 2
            leaving = g1 >= orb
            note = {
                ("Mercury", True): "11 Mar 2024: \"Mercury is out of bound of the Sun. This may turn negative for medium term so wait before taking risk\"",
                ("Saturn", True): "19 Mar 2024: \"Major astronomical event, Saturn is moving out of bound. This can be trend changer specially in metals and crude oil\"",
            }.get((name, leaving))
            out.append({"_jd": c, "time": _hhmm(c, jd0), "et": _et(c),
                        "planet": name, "kind": "combust",
                        "to": "out of bound" if leaving else "combust",
                        "tone": "vol" if note else "neutral",
                        "source": "observed" if note else "extrapolated",
                        "note": note or (f"{name} {'leaves' if leaving else 'enters'} "
                                         f"the {orb}° combustion orb — unremarked by him")})

    # stations: "Mercury is reducing its speed and going to retrograde on
    # Sunday night. BankNifty may get affected more" (6 Nov 2025)
    for name, body in INGRESS_BODIES:
        if name == "Sun":
            continue
        s0 = swe.calc_ut(jd0, body, FLAGS)[0][3]
        s1 = swe.calc_ut(jd1, body, FLAGS)[0][3]
        if s0 * s1 < 0:
            lo, hi = jd0, jd1
            for _ in range(30):
                mid = (lo + hi) / 2
                if swe.calc_ut(mid, body, FLAGS)[0][3] * s0 > 0:
                    lo = mid
                else:
                    hi = mid
            c = (lo + hi) / 2
            label = "retrograde" if s1 < 0 else "direct"
            out.append({"_jd": c, "time": _hhmm(c, jd0), "et": _et(c),
                        "planet": name, "kind": "station", "to": label,
                        "tone": "vol",
                        "source": "observed" if name in ("Mercury", "Mars", "Saturn") else "extrapolated",
                        "note": (("6 Nov 2025: \"Mercury … going to retrograde … "
                                  "sudden drop is possible. BankNifty may get "
                                  "affected more\"" if label == "retrograde" else
                                  "9 Aug 2025: \"Mercury turning direct … the "
                                  "stars point to a possible reversal in the "
                                  "Indian stock market\"; 11 Aug: \"may change "
                                  "the trend but you have to watch first\"")
                                 if name == "Mercury"
                                 else ("23 Feb 2025: \"Mars turning direct, this may "
                                       "impact the current trend in metal sector. Gold, "
                                       "Silver and copper may affected. Chemical sector "
                                       "will also affected\"" if name == "Mars"
                                       else ("15 Nov 2024: \"Saturn is turning to direct "
                                             "motion. Retrograde Saturn was one of many "
                                             "factors of bullish phase in all commodities "
                                             "and stock markets. Watch for trend now\""
                                             if name == "Saturn"
                                             else "a station — treated like Mercury's, unseen")))})
    out.sort(key=lambda x: x["_jd"])
    return out


def mercury_retro_midpoint(d: datetime.date) -> bool:
    """6 Dec 2024: 'Retrograde Mercury is at halfway mark of its entire
    journey. This is considered as a peak of its energy. Some changes are
    possible in all financial markets.' True on the day nearest the
    midpoint of the current retrograde span."""
    jd = _jd_local(d, OPEN_H)

    def speed(j):
        return swe.calc_ut(j, swe.MERCURY, FLAGS)[0][3]

    if speed(jd) >= 0:
        return False

    def station(step):
        """Exact instant the speed crosses zero, scanning day by day
        in `step` direction from jd, then bisecting that day."""
        a = jd
        for _ in range(40):
            if speed(a + step) >= 0:
                break
            a += step
        lo, hi = (a, a + step) if step > 0 else (a + step, a)
        for _ in range(30):
            mid = (lo + hi) / 2
            if (speed(mid) < 0) == (step > 0):
                lo = mid
            else:
                hi = mid
        return (lo + hi) / 2

    mid = (station(-1) + station(+1)) / 2
    y, m, dd, _ = swe.revjul(mid + TZ / 24)
    return datetime.date(y, m, dd) == d


def mercury_state(d: datetime.date) -> dict:
    """Retrograde and combustion of Mercury (and Venus's combustion).

    28 Aug 2024: "Mercury is unpredictable planet during retrograde. This
    is second time I am experiencing almost all predictions went wrong.
    Now decided to avoid making prediction during retro Mercury."
    29 Jun 2024: he disputes a site's combustion dates, showing the
    Sun-Mercury distance was 23° on the day it claimed combustion ended.
    Classical orbs: Mercury 12° (14° when retrograde), Venus 10° (8°).
    """
    jd = _jd_local(d, OPEN_H)
    sun = _lon(swe.SUN, jd)
    merc = swe.calc_ut(jd, swe.MERCURY, FLAGS)[0]
    ven = swe.calc_ut(jd, swe.VENUS, FLAGS)[0]

    def dist(lon):
        x = abs(lon % 360 - sun) % 360
        return min(x, 360 - x)

    m_retro = merc[3] < 0
    return {
        "retrograde": m_retro,
        "sun_distance": round(dist(merc[0]), 1),
        "combust": dist(merc[0]) < (14 if m_retro else 12),
        "venus_combust": dist(ven[0]) < (8 if ven[3] < 0 else 10),
    }


def eclipse_on(d: datetime.date) -> str | None:
    jd0, jd1 = _jd_local(d, 0), _jd_local(d, 24)
    try:
        r = swe.lun_eclipse_when(jd0 - 1, swe.FLG_MOSEPH, 0)
        if jd0 <= r[1][0] < jd1:
            return f"lunar eclipse {_hhmm(r[1][0], jd0)}"
        r = swe.sol_eclipse_when_glob(jd0 - 1, swe.FLG_MOSEPH, 0)
        if jd0 <= r[1][0] < jd1:
            return f"solar eclipse {_hhmm(r[1][0], jd0)}"
    except swe.Error:
        return None
    return None


# ---------------------------------------------------------- regime

def _sign_span(body: int, jd: float, ketu: bool = False) -> tuple[str, str]:
    """(entry date, exit date) of the sign the body occupies at jd, by a
    daily scan up to 400 days either way (retrograde re-entries count as
    the nearest boundary, which is what a calendar reader wants)."""
    def sign_at(j):
        lon = _lon(body, j)
        if ketu:
            lon = (lon + 180) % 360
        return int(lon // 30)

    s0 = sign_at(jd)
    back, back_clipped = jd, True
    for _ in range(400):
        if sign_at(back - 1) != s0:
            back_clipped = False
            break
        back -= 1
    fwd, fwd_clipped = jd, True
    for _ in range(400):
        if sign_at(fwd + 1) != s0:
            fwd_clipped = False
            break
        fwd += 1

    def iso(j, clipped, mark):
        y, m, d, _ = swe.revjul(j + TZ / 24)
        # a slow body (Ketu, Neptune) can sit in a sign longer than the
        # scan; say so instead of printing the scan edge as a date
        return (mark if clipped else "") + f"{y:04d}-{m:02d}-{d:02d}"
    return iso(back, back_clipped, "before "), iso(fwd, fwd_clipped, "after ")


JUPITER_CANCER_HISTORY = [
    ("07 Aug 1978", "29 Aug 1979", 387, 55.2, 69.45),
    ("20 Jul 1990", "14 Aug 1991", 390, 0.3, -19.18),
    ("05 Jul 2002", "30 Jul 2003", 390, 14.85, 3.66),
    ("19 Jun 2014", "14 Jul 2015", 390, -9.52, -2.0),
    ("20 Oct 2025", "05 Dec 2025", 46, -1.17, 13.2),
]


def regime(d: datetime.date) -> dict:
    """Slow-moving context the X account posts as calendars."""
    swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
    jd = _jd_local(d, OPEN_H)
    bodies = [(n, b) for n, b in BODIES if n != "Moon"]
    pos = {n: _lon(b, jd) for n, b in bodies}
    pos["Ketu"] = (pos["Rahu"] + 180) % 360
    ids = dict(bodies)
    signs = {n: int(l // 30) for n, l in pos.items()}

    groups: dict[int, list[str]] = {}
    for n, s in signs.items():
        groups.setdefault(s, []).append(n)
    notes: list[str] = []
    conj = []
    for s, members in sorted(groups.items()):
        if len(members) < 2:
            continue
        rows = []
        for n in members:
            body = ids["Rahu"] if n == "Ketu" else ids[n]
            entry, exit_ = _sign_span(body, jd, ketu=(n == "Ketu"))
            rows.append({"planet": n, "entry": entry, "exit": exit_})
        conj.append({"sign": RASIS[s], "sign_en": SIGN_EN[s],
                     "planets": [r["planet"] for r in rows], "members": rows,
                     "until": min(r["exit"] for r in rows)})
        # "March end, Sun+Saturn+Rahu+Mercury+Venus in Pisces. Very
        # critical time for global markets. Make or break" (14 Feb 2025)
        if len(members) >= 4:
            notes.append(f"{len(members)} bodies in {SIGN_EN[s]} "
                         f"({', '.join(members)}) — a sign stellium: \"very "
                         "critical time for global markets. Make or break for "
                         "all financial markets\" was their reading of the "
                         "five-body Pisces stellium of Mar 2025.")

    jup_sign = signs["Jupiter"]
    jup_entry, jup_exit = _sign_span(swe.JUPITER, jd)

    # "Four planets in Shravana nakshatra … bullish with high volatility.
    # Very large gap up or gap down is possible" (26 Jan 2026 note)
    naks: dict[int, list[str]] = {}
    for n, l in pos.items():
        if n in ("Rahu", "Ketu"):          # points, not planets — his count
            continue                        # was Sun, Mercury, Venus, Mars
        naks.setdefault(int(l // SEG), []).append(n)
    stellia = [{"nakshatra": NAKSHATRAS[k], "planets": v}
               for k, v in naks.items() if len(v) >= 3]
    for s in stellia:
        notes.append(f"{len(s['planets'])} planets in {s['nakshatra']} "
                     f"({', '.join(s['planets'])}) — a nakshatra stellium: "
                     "\"bullish with high volatility … very large gap up or "
                     "gap down is possible\" (their 26 Jan 2026 note).")

    # "Many planets today are below 10 degrees. This is unusual … all
    # financial markets are showing extreme" (21 Jan 2026: 8 of 12)
    early = [n for n, l in pos.items() if l % 30 < 10]
    if len(early) >= 6:
        notes.append(f"{len(early)} bodies in the first 10° of their signs "
                     f"({', '.join(early)}) — they flagged this as unusual "
                     "and linked it to extremes across markets (21 Jan 2026).")

    # "The Grand Trine — Mars, Jupiter and Saturn forming grand trine from
    # Monday. One way …" (26 Oct 2025). Any three of Sun..Saturn mutually
    # ~120° apart, 6° orb.
    trine_bodies = ["Sun", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]
    grand_trines = []
    for i, a in enumerate(trine_bodies):
        for j, b in enumerate(trine_bodies[i + 1:], i + 1):
            for c in trine_bodies[j + 1:]:
                def sep(x, y):
                    dd = abs(pos[x] - pos[y]) % 360
                    return min(dd, 360 - dd)
                if all(abs(sep(x, y) - 120) <= 6 for x, y in
                       ((a, b), (b, c), (a, c))):
                    grand_trines.append([a, b, c])
    for t in grand_trines:
        notes.append(f"Grand trine {' – '.join(t)} — \"one way\" move in "
                     "their 26 Oct 2025 reading (Mars–Jupiter–Saturn then; "
                     "gold and silver fell hard the next two days).")

    # Kaal Sarp yog: every classical planet on one side of the Rahu-Ketu
    # axis. "From Monday, Kaal sarp yog is going to break. Mars is moving
    # away from Ketu and leaving Leo. Major change in Geopolitical
    # situations are coming" (25 Jul 2025).
    ks_bodies = ["Sun", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]
    side = [((pos[n] - pos["Rahu"]) % 360) < 180 for n in ks_bodies]
    kaal_sarp = all(side) or not any(side)
    if kaal_sarp:
        # the planet nearest the axis is the one whose move will break it
        gaps = {n: min((pos[n] - pos["Rahu"]) % 360, (pos[n] - pos["Ketu"]) % 360,
                       (pos["Rahu"] - pos[n]) % 360, (pos["Ketu"] - pos[n]) % 360)
                for n in ks_bodies}
        nearest = min(gaps, key=gaps.get)
        notes.append(f"Kaal Sarp yog — Sun to Saturn all on one side of the "
                     f"Rahu–Ketu axis ({nearest} is nearest the axis, "
                     f"{gaps[nearest]:.1f}° away, and will break it). Their "
                     "reading when it broke on 28 Jul 2025: \"major change in "
                     "geopolitical situations are coming.\"")

    # Rahu-Ketu on the Leo-Aquarius axis: their gold history (6 Jan 2026)
    if {signs["Rahu"], signs["Ketu"]} == {4, 10}:
        which = "Rahu in Leo / Ketu in Aquarius" if signs["Rahu"] == 4 \
            else "Rahu in Aquarius / Ketu in Leo"
        notes.append(f"{which} — their table: 1979-80 and 2016-17 (Rahu Leo) "
                     "= explosive top then heavy correction; 1997-99 and "
                     "2006-08 (Rahu Aquarius) = sharp sell-off / weakness "
                     "then breakout. \"Vulnerable to sharp corrections after "
                     "reaching key resistance zones.\"")
    if SIGN_EN[jup_sign] == "Cancer":
        notes.append("Jupiter in sidereal Cancer — the X account's table of "
                     "every Cancer transit since 1978 shows silver weak in 3 "
                     "of 5 (their claim: 'not a supportive phase for "
                     "sustained bullish trends in Silver').")
    if signs["Sun"] == signs["Ketu"]:
        notes.append(f"Sun + Ketu together in {SIGN_EN[signs['Sun']]} — the "
                     "analog they flagged for the Aug 2025 metals rally "
                     "('almost same chart').")
    return {
        "as_of": d.isoformat(),
        "jupiter": {"sign": RASIS[jup_sign], "sign_en": SIGN_EN[jup_sign],
                    "entry": jup_entry, "exit": jup_exit,
                    "nakshatra": NAKSHATRAS[int(pos["Jupiter"] // SEG)]},
        "sun_ketu_same_sign": signs["Sun"] == signs["Ketu"],
        "nakshatra_stellia": stellia,
        "early_degree_bodies": early,
        "grand_trines": grand_trines,
        "kaal_sarp": kaal_sarp,
        "conjunctions": conj,
        "notes": notes,
        "jupiter_cancer_history": [
            {"entry": a, "exit": b, "days": n, "gold_pct": g, "silver_pct": s}
            for a, b, n, g, s in JUPITER_CANCER_HISTORY],
    }


# ---------------------------------------------------------- one day

def _karanas_in_session(jd0: float) -> list[dict]:
    """Karana running at the open, and the next if it ends before close."""
    sun = lambda j: _lon(swe.SUN, j)          # noqa: E731
    moon = lambda j: _lon(swe.MOON, j)        # noqa: E731

    def elong(j):
        return (moon(j) - sun(j)) % 360

    from .panchang import karana_name
    out, jd = [], jd0 + OPEN_H / 24
    close = jd0 + CLOSE_H / 24
    for _ in range(3):
        k = int(elong(jd) // 6)
        c = _next_cross(elong, ((k + 1) * 6) % 360, jd, jd0 + 2, 1 / 24)
        out.append({"name": karana_name(k), "ends": _hhmm(c, jd0) if c else None,
                    "_end": c})
        if c is None or c > close:
            break
        jd = c + 1 / 1440
    return out


def _call(instrument: str, moon: dict, flags: list[str], karanas: list[dict],
          yoga: str, vt: dict | None, tithi_num: int,
          vn: dict | None = None) -> dict:
    nak = moon["nakshatra"]
    tone, src = nak_tone(nak, moon["sign"], instrument)
    why = [f"Moon in {moon['sign']} / {nak} — {TONE_WORD[tone]} ({src})"]
    if moon["sign"] == "Vrischika" and instrument == "nifty":
        # Nifty only: the 20 Aug Telegram post read the debilitated Moon
        # as bearish for Nifty, but the metals reports of 6 Apr and 4 May
        # call Anuradha (entirely inside Scorpio) bullish for gold/silver.
        tone = "bear"
        why.append("Moon debilitated in Scorpio — bearish (their 20 Aug reading)")
    elif moon["sign"] == "Vrishabha" and tone != "bear":
        tone = "bull"
        why.append("Moon exalted in Taurus")
    if instrument != "nifty" and tithi_num == 30:
        if tone != "bull":
            tone = "bull" if tone == "neutral" else "vol"
        why.append("Amavasya — \"considered bullish for gold and silver\" (14 Jul)")
    if any(f.startswith("Kshaya tithi") for f in flags):
        # "believed bearish for all markets" (Nifty, 5 Mar 2024); "considered
        # as bearish for commodities" (19 May 2025)
        if tone == "bull":
            tone = "vol"
        elif tone == "neutral":
            tone = "bear"
        why.append("Kshaya tithi — \"believed bearish for all markets\" (5 Mar 2024; "
                   "19 May 2025 for commodities)")
    if any(k["name"] == "Vishti" for k in karanas):
        if tone == "bull":
            tone = "vol"
        elif tone == "neutral":
            tone = "bear"
        why.append("Vishti karana in session — \"be very careful following "
                   "a bullish trend\"")
    if yoga == "Vaidhriti":
        if instrument == "nifty":
            # 23 Jun 2024 week note: "Vaidhruti yog is running from
            # 11:52 IST, this is considered as a bearish" (Nifty)
            tone = "bear" if tone != "bull" else "vol"
            why.append("Vaidhriti yog — \"considered as a bearish\" for Nifty (23 Jun 2024)")
        else:
            tone = "vol"
            why.append("Vaidhriti yog — \"volatility with bullish bias\" (27 Jul, 2 Jul)")
    elif yoga == "Vyatipata":
        if instrument == "nifty":
            tone = "vol" if tone != "bear" else "bear"
            why.append("Vyatipata yoga — classically inauspicious; no Nifty "
                       "reading seen, treat as volatile")
        else:
            tone = "bull" if tone != "bear" else "vol"
            why.append("Vyatipat Mahapat yog — \"this is also bullish\" for "
                       "metals (21 May)")
    if vt:
        why.append(f"Vaar-Tithi yog {'/'.join(vt['names'])} — "
                   f"{TONE_WORD[vt['tone']]} ({vt['source']})")
        if vt["source"] == "observed":
            if vt["tone"] == "bull" and tone == "neutral":
                tone = "bull"
            elif vt["tone"] == "bear" and tone in ("neutral", "bull"):
                tone = "vol" if tone == "bull" else "bear"
    if vn:
        why.append(f"Nakshatra + Vaar {'/'.join(vn['names'])} — "
                   f"{TONE_WORD[vn['tone']]} (classical; their 21 May "
                   "\"combination of Nakshatra and Vaar is bullish\")")
        if vn["tone"] == "bull" and tone == "neutral":
            tone = "bull"
        elif vn["tone"] == "bear" and tone == "neutral":
            tone = "bear"
    return {"tone": tone, "source": src, "why": why, "caution": list(flags)}


def _prose(inst: str, call: dict, moon: dict, aspects: list[dict],
           kaal: dict) -> str:
    name = {"nifty": "Nifty", "gold": "gold", "silver": "silver"}[inst]
    s = [f"The Moon is in {moon['sign']}"]
    if moon["sign_change"]:
        s[0] += (f" till {moon['sign_change']['time']} IST then enters "
                 f"{moon['sign_change']['to']}")
    s[0] += f" and stays in {moon['nakshatra']} nakshatra"
    if moon["nakshatra_change"]:
        s[0] += (f" till {moon['nakshatra_change']['time']} IST then "
                 f"{moon['nakshatra_change']['to']}")
    s[0] += f". This is {TONE_WORD[call['tone']]} for {name}."
    live = [a for a in aspects if a["in_session"] and "Moon" in (a["a"], a["b"])]
    if live:
        s.append("Intraday: " + "; ".join(
            f"{a['a']} {a['angle']} {a['b']} at {a['time']} ({TONE_WORD[a['tone']]})"
            for a in live[:4]) + ".")
    s.append(f"Rahu Kaal {kaal['rahu_kaal'][0]}–{kaal['rahu_kaal'][1]}.")
    if call["caution"]:
        s.append(" ".join(call["caution"]) + " Be careful.")
    return " ".join(s)


def _tile(events: list, start: float, end: float, tone: str, driver: str,
          jd0: float, clock=_hhmm, with_et: bool = False) -> list[dict]:
    """Split [start, end] at each event; the lean carries forward."""
    windows = []
    for jd, label, t in sorted(e for e in events if start < e[0] < end):
        if jd - start > 20 / 1440:           # swallow sub-20-minute slivers
            w = {"start": clock(start, jd0), "end": clock(jd, jd0),
                 "tone": tone, "driver": driver}
            if with_et:
                w["start_et"], w["end_et"] = _et(start), _et(jd)
            windows.append(w)
            start = jd
        driver = label
        if t:
            tone = t
    w = {"start": clock(start, jd0), "end": clock(end, jd0),
         "tone": tone, "driver": driver}
    if with_et:
        w["start_et"], w["end_et"] = _et(start), _et(end)
    windows.append(w)
    # merge neighbours that share a tone — the report prints 3-4 windows
    merged: list[dict] = []
    for w in windows:
        if merged and merged[-1]["tone"] == w["tone"]:
            merged[-1]["end"] = w["end"]
            if with_et:
                merged[-1]["end_et"] = w["end_et"]
        else:
            merged.append(w)
    return merged


def day(d: datetime.date, lat: float = 19.076, lon: float = 72.8777) -> dict:
    # swisseph's process-wide default sidereal mode is Fagan-Bradley
    # (+0.88° on Lahiri in 2026 — enough to move a Moon sign change by
    # ~1h40). The channel's tables imply Lahiri (24.23° on 27 Aug 2026).
    swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
    jd0 = _jd_local(d, 0)
    closed = nse_holidays.closed_reason(d)
    moon = moon_path(d)
    pe = _panchang_ends(_jd_local(d, OPEN_H), jd0)
    karanas = _karanas_in_session(jd0)
    kaal = kaal_windows(d, lat, lon)
    aspects = day_aspects(d)
    # the metals day runs to 03:30 next morning — pull tomorrow's early hours
    nxt = day_aspects(d + datetime.timedelta(days=1))
    for a in nxt:
        a["time"] = _hhmm(a["_jd"], jd0)
        a["in_session"] = False
    ecl = eclipse_on(d)
    ingresses = day_ingresses(d)
    tithi = pe["thithi"]
    vt = vaar_tithi_yoga(d.weekday(), tithi["num"])
    vn = vaar_nakshatra_yoga(d.weekday(), moon["nakshatra"])
    # a tithi lasts 20-26 h, so one that begins after the open and ends
    # before tomorrow's open would never be sampled at 09:15 — look at
    # the close as well. Purnima / Amavasya must not slip through.
    elong_close = (_lon(swe.MOON, _jd_local(d, CLOSE_H))
                   - _lon(swe.SUN, _jd_local(d, CLOSE_H))) % 360
    tithis_in_session = sorted({tithi["num"], int(elong_close // 12) + 1})

    # Kshaya tithi: a tithi that begins after today's sunrise and ends
    # before tomorrow's, so the panchang skips it. "Today is Kshay tithi
    # which is considered as bearish for commodities" (19 May 2025).
    rise0, _ = _rise_set(d, lat, lon)
    rise1, _ = _rise_set(d + datetime.timedelta(days=1), lat, lon)
    t0 = int(((_lon(swe.MOON, rise0) - _lon(swe.SUN, rise0)) % 360) // 12)
    t1 = int(((_lon(swe.MOON, rise1) - _lon(swe.SUN, rise1)) % 360) // 12)
    kshaya = THITHIS[(t0 + 1) % 15] if (t1 - t0) % 30 >= 2 else None

    flags: list[str] = []
    merc = mercury_state(d)
    if merc["retrograde"]:
        flags.append("Mercury retrograde — his own moratorium (28 Aug 2024): "
                     "\"almost all predictions went wrong … decided to avoid "
                     "making prediction during retro Mercury.\" Treat every "
                     "call below as lower confidence.")
    if merc["combust"]:
        flags.append(f"Mercury combust ({merc['sun_distance']}° from the Sun) "
                     "— marked [C] in his tables.")
    retro_mid = mercury_retro_midpoint(d)
    if retro_mid:
        flags.append("Retrograde Mercury at the halfway mark of its journey — "
                     "\"considered as a peak of its energy. Some changes are "
                     "possible in all financial markets\" (6 Dec 2024).")
    if kshaya:
        flags.append(f"Kshaya tithi ({kshaya} is skipped between today's and "
                     "tomorrow's sunrise) — \"considered as bearish for "
                     "commodities\" (19 May 2025).")
    if 15 in tithis_in_session:
        flags.append("Purnima — Full Moon: a potential turning point; "
                     "\"Full Moon can be trigger and form bottom\" (29 Jul).")
    elif 30 in tithis_in_session:
        flags.append("Amavasya — New Moon: turning-point watch; bullish for "
                     "metals in their reading (14 Jul).")
    if ecl:
        flags.append(f"{ecl[0].upper() + ecl[1:]} today — many astro events on "
                     "the same day, confidence is low.")
    for a in aspects:
        if a["a"] == "Mercury" and a["b"] == "Rahu" and a["angle"] == 180:
            flags.append("Mercury 180 Rahu — unclear trend, traders may get confused.")
        if a["a"] == "Mars" and a["b"] == "Rahu":
            flags.append(f"Mars {a['angle']} Rahu — \"neutral, confusing price "
                         "action\" (18 Aug).")
        if a["a"] == "Venus" and a["b"] == "Rahu":
            flags.append(f"Venus {a['angle']} Rahu — \"will affect silver "
                         "significantly\" (29 Jul).")
        if a["a"] == "Sun" and a["b"] == "Jupiter":
            flags.append(f"Sun {a['angle']} Jupiter — they read Sun–Jupiter "
                         "contacts on metals both ways (bullish 27 Jul, "
                         "bearish 10 Aug / 15 Jul); watch, don't assume.")

    for ing in ingresses:
        if ing["source"] == "observed":
            flags.append(f"{ing['planet']} enters {ing['to']} at {ing['time']} — "
                         f"{ing['note']}.")
    calls = {inst: _call(inst, moon, flags, karanas, pe["yogam"]["name"], vt,
                         30 if 30 in tithis_in_session else tithi["num"], vn)
             for inst in ("nifty", "gold", "silver")}
    if moon["sign"] == "Kumbha" and ecl:
        calls["silver"]["why"].append(
            "Eclipse in Aquarius / Shatabhisha — the channel flags this as "
            "relevant to white metals")

    # Nifty session windows: split at in-session events, lean carries
    events = [(e[0], e[1], None) for e in moon["_events"]]
    events += [(a["_jd"], f"{a['a']} {a['angle']} {a['b']}", a["tone"])
               for a in aspects if a["in_session"]]
    r0, r1 = kaal["_rahu_jd"]
    events += [(r0, "Rahu Kaal begins", "bear"),
               (r1, "Rahu Kaal ends", calls["nifty"]["tone"])]
    for k in karanas:
        if k["_end"] and jd0 + OPEN_H / 24 < k["_end"] < jd0 + CLOSE_H / 24:
            events.append((k["_end"], f"{k['name']} karana ends",
                           calls["nifty"]["tone"]))
    windows = _tile(events, jd0 + OPEN_H / 24, jd0 + CLOSE_H / 24,
                    calls["nifty"]["tone"], "Moon nakshatra", jd0)

    # Metals windows: the report's 03:30 -> 27:30 IST day, IST / ET,
    # split at every exact aspect (Globex trades through the night)
    m_events = [(a["_jd"], f"{a['a']} {a['angle']} {a['b']}", a["tone"])
                for a in aspects + nxt]
    m_events += [(e[0], e[1], None) for e in moon["_events"]]
    m_events += [(i["_jd"], f"{i['planet']} enters {i['to']}",
                  i["tone"] if i["source"] == "observed" else None)
                 for i in ingresses]
    metal_windows = _tile(m_events, jd0 + METAL_OPEN_H / 24,
                          jd0 + METAL_CLOSE_H / 24, calls["gold"]["tone"],
                          "Moon nakshatra", jd0, clock=_hhmm24, with_et=True)

    for inst in calls:
        calls[inst]["text"] = _prose(inst, calls[inst], moon, aspects, kaal)

    all_aspects = aspects + [a for a in nxt
                             if (a["_jd"] - jd0) * 24 <= METAL_CLOSE_H]
    # "Active planets are Venus, Jupiter, Saturn" — the bodies making an
    # exact aspect that day, in their words
    active = sorted({a["a"] for a in aspects} | {a["b"] for a in aspects},
                    key=lambda n: [b[0] for b in BODIES].index(n))
    for a in all_aspects:
        a.pop("_jd", None)
    for i in ingresses:
        i.pop("_jd", None)
    for k in karanas:
        k.pop("_end", None)
    moon.pop("_events", None)
    kaal.pop("_rahu_jd", None)

    return {
        "date": d.isoformat(), "weekday": d.strftime("%A"),
        "closed": closed,
        "moon": moon,
        "panchang": {
            "tithi": f"{THITHIS[(tithi['num'] - 1) % 15]} "
                     f"({'Shukla' if tithi['num'] <= 15 else 'Krishna'})",
            "tithi_num": tithi["num"],
            "tithis_in_session": tithis_in_session,
            "kshaya_tithi": kshaya,
            "tithi_ends": _strip(pe["thithi"]["ends"]),
            "nakshatra_ends": _strip(pe["natchathiram"]["ends"]),
            "yoga": pe["yogam"]["name"], "yoga_ends": _strip(pe["yogam"]["ends"]),
            "karanas": karanas,
            "vaar_tithi": vt,
            "vaar_nakshatra": vn,
        },
        "kaal": kaal,
        "aspects": all_aspects,
        "ingresses": ingresses,
        "active_planets": active,
        "mercury_retro_midpoint": retro_mid,
        "mercury": merc,
        "eclipse": ecl,
        "flags": flags,
        "calls": calls,
        "windows": windows,
        "metal_windows": metal_windows,
    }


def _strip(clock: str | None) -> str | None:
    """'HH:MM:SS' (hours may pass 24) -> 'HH:MM' with a (+1) marker."""
    if not clock:
        return None
    h, m, _ = clock.split(":")
    h = int(h)
    return f"{h % 24:02d}:{m}" + (f" (+{h // 24})" if h >= 24 else "")


def week(start: datetime.date, days: int = 7,
         lat: float = 19.076, lon: float = 72.8777) -> dict:
    out = [day(start + datetime.timedelta(days=i), lat, lon)
           for i in range(days)]
    return {
        "start": start.isoformat(),
        "end": (start + datetime.timedelta(days=days - 1)).isoformat(),
        "days": out,
        "regime": regime(start),
        "note": ("Saptarsh-style reconstruction. 'observed' = the channel "
                 "wrote this exact call in Jul-Aug 2026; 'extrapolated' = "
                 "filled in by nakshatra-lord / aspect-family rules never "
                 "seen in their output; 'classical' = a standard muhurta "
                 "table standing in for their unpublished one. Not "
                 "backtested, not advice."),
    }
