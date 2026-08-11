"""Prasanam (KP horary) rules — GRAHA MARKETS method.

Sources: PRASANAM VIDEO 1 (cWhvsCFCtCE), prasanam 2 (Hzvl4LKxy1s),
LT part 2 (ka0QwvUnJx0). The teacher's procedure: hold the question in
mind, cast a KP chart (he uses AstroSage "KP Murai", old KP method, with a
1–249 seed number; casting at the question moment is the same mechanism).
Read the lagna's SUB lord as the QUESTION planet and that planet's
nakshatra lord as the ANSWER planet [P1 @ 09:56–11:09]; judge by their
houses: 2/6/11 = profit, 5/8/12 = loss [P1 @ 10:09–10:27], with 6 median /
11 heavy profit and 5/12 median / 8 heavy loss [LT2 @ 05:16–05:48].

This module casts at the chart moment. The 1–249 seed-number variant needs
a UI input and is not implemented yet.
"""
from .. import transit
from .base import Finding

SECTION = "prasanam"

PROFIT_HOUSES = {2, 6, 11}
LOSS_HOUSES = {5, 8, 12}

HOUSE_GRADE = {2: "profit", 6: "median profit", 11: "heavy profit",
               5: "median loss", 12: "median loss", 8: "heavy loss"}


def judge(question_house: int, answer_house: int) -> tuple[str, str]:
    """(verdict, reason) — the answer planet's house carries the verdict;
    the question planet's house supports it.

    Poison rule first: "even one drop spoils the milk" — any 5/8/12 in the
    picture kills a profit answer, even alongside a 2/6/11 [P2, LT2, guide
    §8]. (With single houses per planet this is the faithful analogue of
    the significator-set contamination test; see the deferred TODO.)
    """
    a, q = answer_house, question_house
    if a in PROFIT_HOUSES and q in LOSS_HOUSES:
        return "NO", (f"answer planet in house {a} ({HOUSE_GRADE[a]}) but "
                      f"the question planet sits in house {q} "
                      f"({HOUSE_GRADE[q]}) — mixed, treat as spoiled")
    if a in LOSS_HOUSES:
        return "NO", (f"answer planet sits in house {a} "
                      f"({HOUSE_GRADE[a]}) — unfavourable")
    if a in PROFIT_HOUSES:
        return "YES", (f"answer planet sits in house {a} "
                       f"({HOUSE_GRADE[a]}) — favourable")
    if q in LOSS_HOUSES:
        return "NO", (f"answer house {a} is neutral but the question "
                      f"planet sits in house {q} ({HOUSE_GRADE[q]})")
    if q in PROFIT_HOUSES:
        return "YES", (f"answer house {a} is neutral but the question "
                       f"planet sits in house {q} ({HOUSE_GRADE[q]})")
    return "UNCLEAR", (f"neither planet touches 2/6/11 or 5/8/12 (houses "
                       f"{q} and {a}) — re-ask after 1–2 hours")


def rules(chart: dict) -> list[Finding]:
    inp = chart["input"]
    year, month, day = (int(v) for v in inp["date"].split("-"))
    hour, minute = (int(v) for v in inp["time"].split(":"))

    c = transit.prasanam_chain(year, month, day, hour, minute,
                               inp["tz_offset"], inp["lat"], inp["lon"])
    if c["moon_house"] in LOSS_HOUSES:
        # [P2-Buzz] "In 5, 8, 12, when your chart has the Moon, you should
        # not put the prasanam at all" — do not cast, ask another time
        verdict, reason = "CANCEL", (
            f"the Moon sits in house {c['moon_house']} (5/8/12) — do not "
            f"cast a prasanam at this time; ask later")
    elif c["question"] in ("Rahu", "Ketu"):
        # [guide §2.3] Rahu/Ketu as lagna sub-lord → deceptive, inverted
        # outcomes — cancel the trade outright
        verdict, reason = "CANCEL", (
            f"the lagna sub-lord is {c['question']} — Rahu/Ketu horary "
            f"charts give deceptive answers; cancel the trade")
    elif c["question_house"] not in PROFIT_HOUSES | LOSS_HOUSES:
        # [LT2-Buzz] the QUESTION planet must connect to 2/6/11 or 5/8/12
        # else "the question doesn't connect to the universe"
        verdict, reason = "INVALID", (
            f"the question planet sits in house {c['question_house']} — "
            f"no connection to 2/6/11 or 5/8/12; the question is not "
            f"validated, re-ask after 2–3 hours")
    else:
        verdict, reason = judge(c["question_house"], c["answer_house"])

    return [
        Finding(
            SECTION,
            f"Question planet: {c['question']} (house {c['question_house']})",
            f"The lagna's sub lord at this moment is {c['question']} — it "
            f"represents the question itself.",
            "Prasanam video 1 @ 09:56–11:09"),
        Finding(
            SECTION,
            f"Answer planet: {c['answer']} (house {c['answer_house']})",
            f"The nakshatra lord of {c['question']}'s position — it carries "
            f"the answer.",
            "Prasanam video 1 @ 07:47–08:04"),
        Finding(
            SECTION,
            f"Verdict for a question asked at this moment: {verdict}",
            f"{reason}. Judgment scale: 2/6/11 profit (6 median, 11 heavy); "
            f"5/12 median loss, 8 heavy loss. Treat the chart time as the "
            f"question time; the 1–249 seed-number variant is a future "
            f"input. Never re-ask the same question immediately.",
            "Prasanam video 1 @ 10:09 + LT part 2 @ 03:32–05:48"),
    ]
