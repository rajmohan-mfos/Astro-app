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
lagna sub-lord is still returned as `lagna_sub_lord`; when it is Rahu or
Ketu the verdict is flagged UNRELIABLE [C3 "100% opposite… it can even
lie"] rather than cancelled (see verdict_for).

Judge by houses: 2/6/11 = profit, 5/8/12 = loss [P1 @ 10:09–10:27], with
2/6 median and 11 heavy profit, 5/12 median and 8 heavy loss [LT2].

Two paths: `horary_rules` is the taught method (a 1–249 seed number picks
the ascendant — POST /api/prasanam); `rules` is the no-number SUBSTITUTE
that casts at the chart moment instead.
"""
from .. import transit
from .base import Finding
from .bhavam import BHAVAM

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


def _bhavam_finding(c: dict) -> Finding | None:
    """Gloss the houses the question/answer significators land in, from
    the 12 BHAVAM EXPLANATION table — context for reading the verdict
    (e.g. 5 = speculation/stock exchange, 11 = gains without investment).
    """
    houses = sorted(set(c["question_houses"]) | set(c["answer_houses"]))
    lines = [f"{h}: {BHAVAM[h]}" for h in houses if h in BHAVAM]
    if not lines:
        return None
    return Finding(
        SECTION,
        "What those houses signify (12 bhavam)",
        "; ".join(lines) + ".",
        "12 Bhavam Explanation video")


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


NATAL_AVOID = {5, 8, 12}


def natal_moon_gate(birth_chart: dict, now_chart: dict) -> dict:
    """The TAUGHT do-not-cast gate: transit Moon from the natal frame.

    [P2 @ 03:06–03:26] "For a day Chandran will go in a tie for 2.5
    hours … when he is going in 8 you should not give him the present.
    In 5-8-12 … in your [birth chart] … when Chandran goes from Lakkanam
    to Rasi, you should not give the present." Counted from BOTH the
    janma rasi and the lagna — [12-Bhavam @ 10:32–10:40] "you can see it
    from your Rasi, you can see it from your Lakanam".

    Same arithmetic as /api/can-trade, which has had this rule all along
    while the prasanam path could not reach it.
    """
    def moon(ch):
        return next(g for g in ch["grahas"] if g["name"] == "Moon")
    t_moon = moon(now_chart)
    rasi_count = (t_moon["sign"] - moon(birth_chart)["sign"]) % 12 + 1
    lagna_count = (t_moon["sign"] - birth_chart["lagna"]["sign"]) % 12 + 1
    blocked = [f"{n} from your {frame}"
               for n, frame in ((rasi_count, "janma rasi"),
                                (lagna_count, "lagna"))
               if n in NATAL_AVOID]
    return {"rasi_count": rasi_count, "lagna_count": lagna_count,
            "cast": not blocked, "blocked_by": blocked}


def verdict_for(c: dict) -> tuple[str, str]:
    """Verdict gates, shared by the seed-number and no-number paths.

    The Moon gate says "do not cast at all"; INVALID says "you cast, but
    the question did not connect"; a Rahu/Ketu lagna sub-lord no longer
    cancels — the verdict is computed and flagged UNRELIABLE instead.
    """
    if c["moon_house"] in LOSS_HOUSES:
        # STAND-IN — and the comment here used to overstate it. The taught
        # gate is NATAL: [P2 @ 03:06–03:26] "in 5-8-12 … in your [birth
        # chart] … when Chandran goes from Lakkanam to Rasi, you should
        # not give the present", i.e. the TRANSIT Moon counted from your
        # own janma rasi AND lagna. That is what natal_moon_gate()
        # computes when birth data is supplied. Without birth data there
        # is no natal frame to count from, so the Moon's house in the
        # HORARY chart stands in. It is a different measurement, and the
        # reason string now says so rather than implying fidelity.
        return "CANCEL", (
            f"the Moon sits in house {c['moon_house']} (5/8/12) of the "
            f"horary chart — do not cast a prasanam at this time; ask "
            f"later. Stand-in gate: the taught rule counts the transit "
            f"Moon from YOUR birth rasi and lagna, which needs birth "
            f"data (send `birth` to /api/prasanam, or use /api/can-trade)")
    if not set(c["question_houses"]) & (PROFIT_HOUSES | LOSS_HOUSES):
        verdict, reason = "INVALID", (
            f"the question signifies {c['question_houses']} — no "
            f"connection to 2/6/11 or 5/8/12; you asked from the upper "
            f"mind, not the subconscious. Discard and re-ask after 2–3 "
            f"hours")
    else:
        verdict, reason = judge_sets(c["question_houses"],
                                     c["answer_houses"])
    if c["lagna_sub_lord"] in ("Rahu", "Ketu"):
        # [C3 @ 03:38–04:16] "if Raghukethu comes … there is a chance to
        # make it 100% opposite … it can even lie." Downgraded from a
        # hard CANCEL (2026-08-14): 57 of the 249 seed numbers (Rahu 30 +
        # Ketu 27) carry a Rahu/Ketu lagna sub-lord — 23% of the input
        # space, fixed by the KP table — and the old gate refused every
        # one that reached it (42 on a 2026-08-14 cast; the rest were
        # already Moon-cancelled above, a split that varies by date).
        # Meanwhile [P1]'s own worked example reads Rahu normally by
        # houses as the ANSWER planet. C3's words are a reliability
        # warning ("a chance"), so the judgment is computed and flagged,
        # not refused.
        return f"UNRELIABLE ({verdict})", (
            f"{reason}. WARNING: the lagna sub-lord is "
            f"{c['lagna_sub_lord']} — a Rahu/Ketu horary can come out "
            f"100% opposite, 'it can even lie' [C3]; do not act on this "
            f"reading — re-ask with a fresh number after 2–3 hours")
    return verdict, reason


def horary_rules(number: int, year: int, month: int, day: int, hour: int,
                 minute: int, tz_offset: float, lat: float,
                 lon: float, birth: dict | None = None) -> list[Finding]:
    """The taught prasanam: a seed number 1–249 chooses the chart.

    [P1 @ 04:31–05:32] AstroSage → KP Murai → KP OLD method → "KP Hora
    Ennai" → think of a number 1–249. The number fixes the ascendant, so
    the QUESTION planet is the lagna's sub lord — which is exactly what
    the number selects. This is P1's "Lakkana Upanachathram is the
    question", and under the seed-number method it stops conflicting with
    LT2's Moon phrasing: LT2 describes reading the Moon off a chart the
    number already chose.

    `birth` is an optional Layer-A birth chart. When given, the TAUGHT
    natal do-not-cast gate is applied ([P2] transit Moon in 5/8/12 from
    your janma rasi or lagna) instead of the horary-chart stand-in.
    """
    c = transit.horary_chart(number, year, month, day, hour, minute,
                             tz_offset, lat, lon)
    seed = c["seed"]
    natal = None
    if birth:
        from .. import engine
        now_chart = engine.compute(year, month, day, hour, minute,
                                   tz_offset, lat, lon,
                                   ayanamsa_mode=engine.KP)
        natal = natal_moon_gate(birth, now_chart)
    if natal and not natal["cast"]:
        verdict, reason = "CANCEL", (
            f"the transit Moon is {' and '.join(natal['blocked_by'])} — "
            f"[P2] 'in 5-8-12 … you should not give the present'. This is "
            f"the taught natal gate, counted from your own birth chart; "
            f"do not cast now, ask later")
    else:
        verdict, reason = verdict_for(c)
        if natal:
            reason += (f" (natal gate clear: Moon {natal['rasi_count']} "
                       f"from your janma rasi, {natal['lagna_count']} from "
                       f"your lagna)")
    return [
        Finding(
            SECTION,
            f"Horary number {number} → lagna {seed['rasi']} "
            f"({seed['sub_lord']} sub)",
            f"Number {number} of 249 selects {seed['rasi']} "
            f"{seed['start'] % 30:.2f}°–{seed['end'] % 30 or 30:.2f}°, "
            f"{seed['nakshatra']} ({seed['star_lord']}'s star), "
            f"{seed['sub_lord']} sub. The number chooses the ascendant; "
            f"the other 11 cusps follow by Placidus and the planets are "
            f"placed for the moment you asked.",
            "Prasanam video 1 @ 04:31–05:32 (AstroSage KP old method)"),
        Finding(
            SECTION,
            f"Question planet: {c['question']} — signifies houses "
            f"{c['question_houses']}",
            f"The lagna's sub lord, which the number selected. "
            f"Significators = houses it occupies and owns, plus its star "
            f"lord's. (Occupied house {c['question_house']}.)",
            "Prasanam video 1 @ 09:56–10:08 'Lakkana Upanachathram'"),
        Finding(
            SECTION,
            f"Answer planet: {c['answer']} — signifies houses "
            f"{c['answer_houses']}",
            f"The star lord of {c['question']}'s position — 'the star of "
            f"the star' — it carries the verdict. (Occupied house "
            f"{c['answer_house']}.)",
            "Prasanam video 1 @ 07:47–08:04"),
        *([f] if (f := _bhavam_finding(c)) else []),
        Finding(
            SECTION,
            f"Verdict: {verdict}",
            f"{reason}. Judgment scale: 2/6 median profit, 11 heavy "
            f"profit; 5/12 median loss, 8 heavy loss. Ask one exact "
            f"question — one instrument, one direction, an explicit "
            f"target and horizon — and do not re-ask it for 2–3 hours. "
            f"Study aid, not financial advice.",
            "Prasanam video 1 @ 10:09 + LT part 2 @ 03:32–05:48"),
    ]


def gate_state(verdict: str, reason: str) -> dict:
    """[P2 @ 279–299] "Present is the gateway… if you open the gate you
    can enter, then you can put a graph" — prasanam is taught as a GATE
    on the graph methods, not a peer reading. predict.run uses this to
    mark the graph/weekly/long-term sections when the gate is not open.

    Only a bare "YES" opens the gate — so "UNRELIABLE (YES)" does not.
    That is intended, not an accident of the equality test: a reading
    flagged do-not-act must not be what authorises a graph.

    This is read from the SUBSTITUTE
    prasanam (cast at the chart moment, no seed number); the taught gate
    is a seed-number prasanam on your actual question (/api/prasanam).
    """
    return {
        "verdict": verdict,
        "open": verdict == "YES",
        "reason": reason,
        "substitute": True,
    }


def report(chart: dict) -> tuple[list[Finding], dict]:
    """Findings for the substitute prasanam plus the gate state."""
    inp = chart["input"]
    year, month, day = (int(v) for v in inp["date"].split("-"))
    hour, minute = (int(v) for v in inp["time"].split(":"))

    c = transit.prasanam_chain(year, month, day, hour, minute,
                               inp["tz_offset"], inp["lat"], inp["lon"])
    verdict, reason = verdict_for(c)
    return _findings(c, verdict, reason), gate_state(verdict, reason)


def rules(chart: dict) -> list[Finding]:
    return report(chart)[0]


def _findings(c: dict, verdict: str, reason: str) -> list[Finding]:
    return [
        Finding(
            SECTION,
            "No horary number given — this is the SUBSTITUTE reading",
            "The taught prasanam is driven by a seed number 1–249 that you "
            "think of while holding the question in mind; that number "
            "chooses the ascendant. Nothing below used a number — it reads "
            "the chart cast at this page's date and time instead, which is "
            "a stand-in, not the method. Enter a number in the Prasanam "
            "tab to cast the real thing.",
            "Prasanam video 1 @ 04:51–05:32"),
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
        *([f] if (f := _bhavam_finding(c)) else []),
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
            f"as the question time; enter a 1–249 number in the Prasanam "
            f"tab for the taught method.",
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
