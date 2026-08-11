"""Panchang helpers (SPEC Sections 5.4–5.5).

All longitudes are sidereal (Lahiri), degrees [0, 360).
"""
import datetime
from math import floor

from .names import (THITHIS, NAKSHATRAS, NAKSHATRAS_TA, YOGAS,
                    KARANA_MOVABLE, WEEKDAYS, WEEKDAYS_TA)

SEG = 360 / 27


def karana_name(k: int) -> str:
    if k == 0:
        return "Kimstughna"
    if k >= 57:
        return ["Shakuni", "Chatushpada", "Naga"][k - 57]
    return KARANA_MOVABLE[(k - 1) % 7]


def panchang(sun: float, moon: float, year: int, month: int, day: int) -> dict:
    elongation = (moon - sun) % 360

    thithi_idx = floor(elongation / 12)                 # 0..29
    paksha = "Shukla" if thithi_idx < 15 else "Krishna"

    nak_idx = floor(moon / SEG)                         # 0..26
    pada = floor((moon % SEG) / (SEG / 4)) + 1          # 1..4

    yoga_idx = floor(((sun + moon) % 360) / SEG)        # 0..26

    k = floor(elongation / 6)                           # 0..59

    # Civil-local date, NOT swe.day_of_week: the UT day rolls back for
    # early-morning IST times and returns the wrong weekday (SPEC 5.5).
    w = datetime.date(year, month, day).weekday()       # Mon=0 .. Sun=6

    return {
        "vaara": {"en": WEEKDAYS[w], "ta": WEEKDAYS_TA[w]},
        "thithi": {"num": thithi_idx + 1, "name": THITHIS[thithi_idx % 15],
                   "paksha": paksha},
        "natchathiram": {"num": nak_idx + 1, "name": NAKSHATRAS[nak_idx],
                         "name_ta": NAKSHATRAS_TA[nak_idx], "pada": pada},
        "yogam": {"num": yoga_idx + 1, "name": YOGAS[yoga_idx]},
        "karanam": {"num": k + 1, "name": karana_name(k)},
    }
