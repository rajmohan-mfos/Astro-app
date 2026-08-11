"""Prasanam (KP horary) rules — GRAHA MARKETS method.

Sources: PRASANAM VIDEO 1 (cWhvsCFCtCE), prasanam 2 (Hzvl4LKxy1s),
LT part 2 (ka0QwvUnJx0). The teacher's procedure: hold the question in
mind, cast a KP chart (he uses AstroSage "KP Murai", old KP method, with a
1–249 seed number; casting at the question moment is the same mechanism).

QUESTION planet = the Moon's nakshatra lord; ANSWER planet = that
planet's own star lord [LT2: "the moon is the question… the Buddha is an
answer"]. NOTE: P1 instead phrases the question planet as the lagna's
sub-lord ("Lakhna Upanachathram"). The two transcripts genuinely
disagree; the Moon reading is used per user adjudication (2026-08-11)
because LT2 states it repeatedly and works a full example with it. The
lagna sub-lord is still returned as `lagna_sub_lord` and still triggers
the Rahu/Ketu cancel.

Judge by houses: 2/6/11 = profit, 5/8/12 = loss [P1 @ 10:09–10:27], with
2/6 median and 11 heavy profit, 5/12 median and 8 heavy loss [LT2].

This module casts at the chart moment. The 1–249 seed-number variant needs
a UI input and is not implemented yet.
"""
from .. import transit
from .base import Finding

SECTION = "prasanam"

PROFIT_HOUSES = {2, 6, 11}
LOSS_HOUSES = {5, 8, 12}

# [LT2] "5 to 12 is the medium loss, 8 is the heavy loss, 2, 6 is the
# medium profit, 11 is the heavy profit"
HOUSE_GRADE = {2: "median profit", 6: "median profit", 11: "heavy profit",
               5: "median loss", 12: "median loss", 8: "heavy loss"}


DELAY_HOUSE = 3            # [LT2] "if it goes in 2, 6, 11, or 3, 11"
SATISFACTION = {1, 4, 10}  # [P2] "whoever is satisfied have 1, 4, 10"


def _as_set(v) -> set:
    return set(v) if isinstance(v, (set, list, tuple)) else {v}


def judge_sets(question, answer) -> tuple[str, str]:
    """Judge KP significator SETS [P1: 'the star is the question - 4, 9,
    10, 11 are there; Rahu is here - 4, 10, 12'].

    Poison rule first: any 5/8/12 among the answer's significators spoils
    it, even alongside a 2/6/11 — "one drop of poison in a tumbler of
    milk". His own example answers 4/10/12 and the 12 makes it a NO.
    """
    q, a = _as_set(question), _as_set(answer)
    a_loss, a_profit = a & LOSS_HOUSES, a & PROFIT_HOUSES

    def grade(hs):
        return ", ".join(f"{h} ({HOUSE_GRADE[h]})" for h in sorted(hs))

    extra = ""
    if a & SATISFACTION:
        extra = (f" Touches {sorted(a & SATISFACTION)} — the satisfaction "
                 f"houses; the size of the gain should feel worthwhile.")
    else:
        extra = (" No 1/4/10 connection — any profit may feel unsatisfying "
                 "in size.")

    if a_loss:
        return "NO", (f"the answer signifies {grade(a_loss)}"
                      + (f" alongside {grade(a_profit)} — mixed, and one "
                         f"drop of poison spoils it" if a_profit else
                         " — unfavourable"))
    if a_profit:
        if q & LOSS_HOUSES:
            return "NO", (f"the answer signifies {grade(a_profit)} but the "
                          f"question carries {grade(q & LOSS_HOUSES)} — "
                          f"mixed, treat as spoiled")
        if DELAY_HOUSE in a and 11 in a:
            return "YES", (f"the answer signifies {grade(a_profit)} with "
                           f"house 3 — profit, but delayed: expect a dip "
                           f"and a late recovery, so do not exit early."
                           + extra)
        return "YES", f"the answer signifies {grade(a_profit)}.{extra}"
    if q & LOSS_HOUSES:
        return "NO", (f"the answer is neutral but the question carries "
                      f"{grade(q & LOSS_HOUSES)}")
    if q & PROFIT_HOUSES:
        return "YES", (f"the answer is neutral but the question carries "
                       f"{grade(q & PROFIT_HOUSES)}.{extra}")
    return "UNCLEAR", ("neither the question nor the answer touches "
                       "2/6/11 or 5/8/12 — re-ask after 2–3 hours")


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
    elif c["lagna_sub_lord"] in ("Rahu", "Ketu"):
        # [C3] "if Raghukethu comes as Lakhanam's Upanachathram… avoid" —
        # tied to the LAGNA's sub-lord specifically, not the question
        # planet; "there is a chance you will be 100% opposite"
        verdict, reason = "CANCEL", (
            f"the lagna sub-lord is {c['lagna_sub_lord']} — Rahu/Ketu "
            f"horary charts can invert the answer completely; cancel")
    elif not set(c["question_houses"]) & (PROFIT_HOUSES | LOSS_HOUSES):
        # [LT2/P1] the QUESTION must connect to 2/6/11 or 5/8/12, else
        # "you asked in the upper mind" — discard without predicting
        verdict, reason = "INVALID", (
            f"the question signifies {c['question_houses']} — no "
            f"connection to 2/6/11 or 5/8/12; you asked from the upper "
            f"mind, not the subconscious. Discard and re-ask after 2–3 "
            f"hours")
    else:
        verdict, reason = judge_sets(c["question_houses"],
                                     c["answer_houses"])

    return [
        Finding(
            SECTION,
            f"Question planet: {c['question']} — signifies houses "
            f"{c['question_houses']}",
            f"The Moon's nakshatra lord at this moment is {c['question']} — "
            f"'the moon is the question'. Significators = houses it "
            f"occupies and owns, plus its star lord's. (Occupied house "
            f"{c['question_house']}; lagna sub-lord {c['lagna_sub_lord']}.)",
            "LT part 2 + Prasanam video 1 significator sets"),
        Finding(
            SECTION,
            f"Answer planet: {c['answer']} — signifies houses "
            f"{c['answer_houses']}",
            f"The star lord of {c['question']}'s position — 'the star of "
            f"the star' — it carries the verdict. (Occupied house "
            f"{c['answer_house']}.)",
            "LT part 2 + Prasanam video 1 @ 07:47–08:04"),
        Finding(
            SECTION,
            "Gap up / gap down is a prasanam question, not a graph read",
            "[C10] The overnight gap is not taken from the chart — cast a "
            "prasanam on the specific trade ('will I profit buying puts at "
            "the open?') the evening before. The transcript's yes/no→"
            "direction mapping is garbled, so no automatic mapping is "
            "applied here: ask the question in the form you will trade.",
            "Astro Class 10"),
        Finding(
            SECTION,
            f"Verdict for a question asked at this moment: {verdict}",
            f"{reason}. Judgment scale: 2/6 median profit, 11 heavy "
            f"profit; 5/12 median loss, 8 heavy loss. Treat the chart time "
            f"as the question time; the 1–249 seed-number variant is a "
            f"future input.",
            "Prasanam video 1 @ 10:09 + LT part 2 @ 03:32–05:48"),
        Finding(
            SECTION,
            "The three rules for a valid question [LT2]",
            "(1) Right timing — cast on a clean day (your Moon not in "
            "5/8/12, not over natal Rahu/Ketu). (2) The question must be "
            "exact — one instrument, one direction, an explicit target and "
            "horizon ('will Reliance exceed 4000 in 2 years?'). (3) The "
            "question planet must connect to 2/6/11 or 5/8/12, else it "
            "'doesn't connect to the universe' — discard it.",
            "LT part 2 — 'you should not forget these 3 rules'"),
        Finding(
            SECTION,
            "Re-asking etiquette and horizon [LT2]",
            "Do not re-ask the same question for 2–3 hours, and leave the "
            "same stock 1–2 weeks before asking again; batch a basket over "
            "several sittings rather than in one go. On a NO, lower the "
            "target and re-ask ('above 3000 or 3500?') to find the level "
            "the chart will grant. Prasanam answers out to ~5 years — "
            "further than the Jupiter graph method, which he limits to "
            "about a year.",
            "LT part 2 — re-ask intervals, target laddering, 5-year scope"),
    ]
