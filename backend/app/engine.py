"""Layer A — astronomy engine (SPEC Section 5).

Sidereal (Lahiri) graha longitudes, lagna, panchang and the South Indian
chart token grid. Deterministic; Layer B (predict.py) is wired in main.py
so this module never depends on the prediction method.
"""
import datetime

import swisseph as swe

from .names import RASIS, RASIS_TA, GRAHA_TA
from .panchang import panchang

FLAGS = swe.FLG_MOSEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED

BODIES = [("Sun", swe.SUN), ("Moon", swe.MOON), ("Mars", swe.MARS),
          ("Mercury", swe.MERCURY), ("Jupiter", swe.JUPITER),
          ("Venus", swe.VENUS), ("Saturn", swe.SATURN)]

TOKENS = {"Sun": "Su", "Moon": "Mo", "Mars": "Ma", "Mercury": "Me",
          "Jupiter": "Ju", "Venus": "Ve", "Saturn": "Sa",
          "Rahu": "Ra", "Ketu": "Ke"}


def deg_in_sign(lon: float) -> str:
    total_min = round((lon % 30) * 60)
    return f"{total_min // 60}°{total_min % 60:02d}'"


def _graha(name: str, lon: float, retro: bool) -> dict:
    sign = int(lon // 30)
    return {"name": name, "name_ta": GRAHA_TA[name], "lon": round(lon, 4),
            "sign": sign, "rasi": RASIS[sign], "rasi_ta": RASIS_TA[sign],
            "deg_in_sign": deg_in_sign(lon), "retro": retro}


def compute(year: int, month: int, day: int, hour: int, minute: int,
            tz_offset: float, lat: float, lon: float) -> dict:
    datetime.date(year, month, day)  # raises ValueError on an invalid date

    ut_hour = hour + minute / 60 - tz_offset
    jd = swe.julday(year, month, day, ut_hour)

    swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
    ayanamsa = swe.get_ayanamsa_ut(jd)

    grahas = []
    for name, body in BODIES:
        pos = swe.calc_ut(jd, body, FLAGS)[0]
        retro = pos[3] < 0 and name not in ("Sun", "Moon")
        grahas.append(_graha(name, pos[0] % 360, retro))

    rahu = swe.calc_ut(jd, swe.MEAN_NODE, FLAGS)[0][0] % 360
    grahas.append(_graha("Rahu", rahu, True))
    grahas.append(_graha("Ketu", (rahu + 180) % 360, True))

    _, ascmc = swe.houses_ex(jd, lat, lon, b'W', swe.FLG_SIDEREAL)
    asc = ascmc[0] % 360
    asc_sign = int(asc // 30)

    sun_lon = grahas[0]["lon"]
    moon_lon = grahas[1]["lon"]

    chart: list[list[str]] = [[] for _ in range(12)]
    chart[asc_sign].append("La")
    for g in grahas:
        chart[g["sign"]].append(TOKENS[g["name"]] + ("(R)" if g["retro"] else ""))

    return {
        "input": {"date": f"{year:04d}-{month:02d}-{day:02d}",
                  "time": f"{hour:02d}:{minute:02d}",
                  "tz_offset": tz_offset, "lat": lat, "lon": lon},
        "ayanamsa": round(ayanamsa, 4),
        "lagna": {"lon": round(asc, 4), "sign": asc_sign,
                  "rasi": RASIS[asc_sign], "rasi_ta": RASIS_TA[asc_sign],
                  "deg_in_sign": deg_in_sign(asc)},
        "grahas": grahas,
        "chart": chart,
        "panchang": panchang(sun_lon, moon_lon, year, month, day),
    }
