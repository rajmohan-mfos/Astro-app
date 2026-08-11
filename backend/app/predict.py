"""Layer B — GRAHA MARKETS prediction rules (SPEC Section 8, Appendix C).

Aggregates findings from the rules/ modules: graph (intraday), horai,
panchang_rules, stocks, weekly, longterm and prasanam.
"""
from dataclasses import asdict

from .rules import (dayscore, graph, horai, longterm, panchang_rules,
                    prasanam, stocks, weekly)

DISCLAIMER = (
    "Educational study aid reproducing the GRAHA MARKETS teaching "
    "(@GRAHAMARKETS, YouTube). Not financial advice and not from a "
    "SEBI-registered advisor. Astrology-based market forecasting has no "
    "demonstrated predictive edge; never treat output as a trading signal."
)

# basics.py retired from the pipeline: [C3-Buzz] shows the node rule is
# about the Moon over NATAL Rahu/Ketu — implemented in /api/can-trade
RULE_MODULES = [graph.rules, horai.rules, panchang_rules.rules,
                dayscore.rules, stocks.rules, weekly.rules, longterm.rules,
                prasanam.rules]


def run(chart: dict) -> dict:
    """chart = Layer A engine output. Returns the `prediction` response section."""
    findings = []
    for mod in RULE_MODULES:
        findings.extend(mod(chart))

    sections: dict[str, list[dict]] = {}
    for f in findings:
        sections.setdefault(f.section, []).append(asdict(f))

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
        "sections": sections,
        "graph_segments": segments,
        "chain": chain,
        "day_score": dayscore.day_score(chart),
        "note": DISCLAIMER,
    }
