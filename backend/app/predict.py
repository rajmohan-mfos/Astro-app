"""Layer B — GRAHA MARKETS prediction rules (SPEC Section 8, Appendix C).

Aggregates findings from the rules/ modules: graph (intraday), horai,
panchang_rules, stocks, weekly, longterm and prasanam.
"""
from dataclasses import asdict

from .rules import (dayscore, graph, horai, longterm, panchang_rules,
                    prasanam, stocks, weekly)
from .rules.base import Finding

DISCLAIMER = (
    "Educational study aid reproducing the GRAHA MARKETS teaching "
    "(@GRAHAMARKETS, YouTube). Not financial advice and not from a "
    "SEBI-registered advisor. Astrology-based market forecasting has no "
    "demonstrated predictive edge; never treat output as a trading signal."
)

# basics.py retired from the pipeline: [C3-Buzz] shows the node rule is
# about the Moon over NATAL Rahu/Ketu — implemented in /api/can-trade
# prasanam runs separately (via report) so its verdict can gate the rest.
RULE_MODULES = [graph.rules, horai.rules, panchang_rules.rules,
                dayscore.rules, stocks.rules, weekly.rules, longterm.rules]

# [P2 @ 279–299] "Present is the gateway… if you open the gate you can
# enter, then you can put a graph" — the sections a non-open prasanam gate
# demotes to study-only output
GATED_SECTIONS = ("graph", "weekly", "monthly", "long_term")

# [C4 @ 22:54–23:26] the taught way to EXPRESS a finished reading. Note
# the order on the tape: "You are putting the present [prasanam] … now in
# Bank Nifty, is it profitable to buy put option? … yeah, you get profit"
# and, for a stock, "In Reliance, if I sell the future, I will get
# profit". The instrument follows a prasanam confirmation — it is not a
# property of the day score — which is why this lives here, behind the
# same gate, rather than in dayscore.rules().
_EXPRESSION = {
    "positive": ("call options on the index, or buying the future in a "
                 "stock of the stretch's planet"),
    "negative": ("put options on the index, or selling the future in a "
                 "stock of the stretch's planet"),
}


def _expression_finding(chart: dict, gate: dict) -> Finding | None:
    """How the course expresses a CONFIRMED reading as an instrument.

    Emitted only when the prasanam gate is open AND the day's panchang
    and chain agree. Reported as what the course teaches, never as an
    instruction — the app is a study aid, and this is the point in the
    method where a reader is most likely to forget that.
    """
    if not gate["open"]:
        return None
    s = dayscore.day_score(chart)
    if s["agreement"] != "agree":
        return None
    how = _EXPRESSION.get(s["panchang_sign"])
    if not how:
        return None
    return Finding(
        "graph",
        f"How the course expresses this: {s['panchang_sign']} day → {how}",
        f"[C4] After the prasanam confirms, the teacher names the "
        f"instrument directly — 'is it profitable to buy put option? … "
        f"you get profit', and for a stock 'if I sell the future, I will "
        f"get profit'. Reproduced here because it is part of the taught "
        f"method, and shown only on a day whose panchang and chain agree "
        f"({s['conviction']} conviction) with the gate open, which is the "
        f"only state he applies it in. It is a description of his "
        f"teaching, NOT a recommendation: the 5-year backtest found this "
        f"engine no better than a coin flip, and options lose money "
        f"quickly when the reading is wrong. Not financial advice.",
        "Astro Class 4 @ 22:54–23:26")


def run(chart: dict) -> dict:
    """chart = Layer A engine output. Returns the `prediction` response section."""
    findings = []
    for mod in RULE_MODULES:
        findings.extend(mod(chart))

    prasanam_findings, gate = prasanam.report(chart)
    findings.extend(prasanam_findings)

    expr = _expression_finding(chart, gate)
    if expr:
        findings.append(expr)

    sections: dict[str, list[dict]] = {}
    for f in findings:
        sections.setdefault(f.section, []).append(asdict(f))

    if not gate["open"]:
        for sec in GATED_SECTIONS:
            if sec in sections:
                sections[sec].insert(0, asdict(Finding(
                    sec,
                    f"Prasanam gate NOT open ({gate['verdict']}) — "
                    f"study only",
                    "[P2] 'Present is the gateway… if you open the gate "
                    "you can enter, then you can put a graph.' The "
                    "substitute prasanam at this chart moment did not "
                    "answer a plain YES, so treat this section as study "
                    "output, not an entry signal, until a seed-number "
                    "prasanam on your actual question opens the gate "
                    "(Prasanam tab / POST /api/prasanam).",
                    "prasanam 2 — the gateway rule")))

    cast = graph.cast_chart(chart)
    p = graph.pick_chain(cast, "Moon")
    segments = [
        {"start": s["start"], "end": s["end"], "planet": s["planet"],
         "count": s["count"], "bias": s["bias"]}
        for s in graph.build_segments(cast, p)]

    grahas = p["grahas"]
    moon_lon = grahas["Moon"]["lon"]

    def var(planet, reverse):
        if planet is None:
            return None
        count = (graph.degree_house(grahas[planet]["lon"], moon_lon)
                 if reverse else
                 graph.degree_house(moon_lon, grahas[planet]["lon"]))
        return {"planet": planet, "count": count}

    chain = {
        "x": var(p["x"], False),
        "x1": var(p["x1"], True),
        "y": var(p["y"], False),
        "y1": var(p["y1"], True),
        "first": p["first"], "second": p["second"],
        "cast_time": cast.get("input", {}).get("time"),
    }

    summary = [f.title for f in findings]
    return {
        "status": "v1" if findings else "stub",
        "summary": summary,
        "prasanam_gate": gate,
        "sections": sections,
        "graph_segments": segments,
        "chain": chain,
        "day_score": dayscore.day_score(chart),
        "note": DISCLAIMER,
    }
