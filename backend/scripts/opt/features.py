"""Per-bar astro feature table — computed once, reused by every variant.

Everything downstream (the walk-forward search, the permutation null) is
arithmetic over this table. That is what makes a large search affordable:
casting a chart is ~0.2 ms, but re-casting 3,800 of them for each of
thousands of variants is not.

TWO CORRECTNESS NOTES, both found by reading the existing code:

1. scripts/backtest_nifty.py reads its panchang from a DIFFERENT chart than
   the app does. It computes at 09:15 in Lahiri (engine.compute's default)
   and reads chart["panchang"], while dayscore.panchang_tally reads from
   cast_chart() — KP, at sunrise. Thithi and karanam are elongation-based
   and so ayanamsa-invariant, but yogam and nakshatra are not. This module
   uses the APP's path (KP at sunrise) throughout, so the study measures
   the thing the app actually ships.

2. The features stored are the RAW INGREDIENTS, not the derived labels.
   For each segment we keep (planet, nature, count, retro), not just the
   "bullish"/"bearish" string, so a variant can re-derive the label under a
   different 3x4 cell table without re-casting the chart.
"""
import csv
import datetime
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)

from app import engine                                       # noqa: E402
from app.rules import graph, panchang_rules                  # noqa: E402
import prices                                                # noqa: E402

OUT_DIR = os.path.join(HERE, "..", "..", "knowledge", "backtest", "opt")
SESSION_START, SESSION_END = 9.25, 15.5
MUMBAI = (19.076, 72.8777)
TZ = 5.5

FIELDS = [
    "date", "open", "close", "ret_pct", "up", "year", "weekday",
    "thithi_num", "thithi_in_paksha", "paksha", "thithi_family",
    "karanam", "yogam", "nakshatra", "nak_lord",
    "moon_lon", "sun_lon", "lagna_lon",
    "x_planet", "x_count", "x1_planet", "x1_count",
    "y_planet", "y_count", "y1_planet", "y1_count",
    "first", "second",
    "segments",          # JSON: [{planet, nature, count, retro, start, end}]
    "chain_score", "panchang_total",   # the CURRENT engine's own numbers
    "prev_ret",
]


def _family(in_paksha: int) -> str:
    for name, members, _bias, _gloss in panchang_rules.THITHI_FAMILIES:
        if in_paksha in members:
            return name
    return "?"


def features_for(d: datetime.date, lat: float, lon: float) -> dict:
    """One day's raw astro ingredients, from the app's own cast path."""
    chart = engine.compute(d.year, d.month, d.day, 9, 0, TZ, lat, lon)
    cast = graph.cast_chart(chart)          # KP, at sunrise
    pick = graph.pick_chain(cast, "Moon")
    segs = graph.build_segments(cast, pick)

    pan = cast["panchang"]
    grahas = {g["name"]: g for g in cast["grahas"]}
    moon_lon = grahas["Moon"]["lon"]
    in_paksha = (pan["thithi"]["num"] - 1) % 15 + 1

    def var(planet, reverse):
        if planet is None:
            return None, ""
        count = (graph.degree_house(grahas[planet]["lon"], moon_lon)
                 if reverse else
                 graph.degree_house(moon_lon, grahas[planet]["lon"]))
        return planet, count

    xp, xc = var(pick["x"], False)
    x1p, x1c = var(pick["x1"], True)
    yp, yc = var(pick["y"], False)
    y1p, y1c = var(pick["y1"], True)

    seg_rows = []
    for s in segs:
        g = grahas.get(s["planet"], {})
        seg_rows.append({
            "planet": s["planet"],
            "nature": graph.planet_nature(s["planet"], g.get("retro", False)),
            "count": s["count"],
            "retro": bool(g.get("retro", False)),
            "start": round(s["start"], 4),
            "end": round(s["end"], 4),
            "bias": s["bias"],
        })

    span = sum(s["end"] - s["start"] for s in segs) or 1.0
    chain = sum((s["end"] - s["start"])
                * {"bullish": 1.0, "sideways-bullish": 0.5, "sideways": 0.0,
                   "angle": 0.0, "sideways-bearish": -0.5,
                   "bearish": -1.0}.get(s["bias"], 0.0)
                for s in segs) / span

    val = {"positive": 1.0, "negative": -1.0}
    t_bias = panchang_rules.thithi_bias(pan["thithi"]["num"])[0]
    k_bias = panchang_rules.karanam_bias(pan["karanam"]["name"])[0]
    y_bias = panchang_rules.yogam_bias(pan["yogam"]["name"])[0]
    lord = graph.nak_lord_of(moon_lon)
    pan_total = (val.get(t_bias, 0.0) + val.get(k_bias, 0.0)
                 + {"positive": 0.5, "negative": -0.5,
                    "very negative": -1.0}.get(y_bias, 0.0)
                 + {"Mercury": 1.0, "Venus": 0.5, "Moon": 0.5, "Sun": 0.0,
                    "Mars": -0.5, "Saturn": -1.0, "Ketu": -1.0}.get(lord, 0.0))
    if lord in ("Jupiter", "Rahu"):
        pan_total *= 1.5

    return {
        "year": d.year, "weekday": d.weekday(),
        "thithi_num": pan["thithi"]["num"], "thithi_in_paksha": in_paksha,
        "paksha": pan["thithi"]["paksha"], "thithi_family": _family(in_paksha),
        "karanam": pan["karanam"]["name"], "yogam": pan["yogam"]["name"],
        "nakshatra": pan["natchathiram"]["name"], "nak_lord": lord,
        "moon_lon": round(moon_lon, 4),
        "sun_lon": round(grahas["Sun"]["lon"], 4),
        "lagna_lon": round(cast["lagna"]["lon"], 4),
        "x_planet": xp or "", "x_count": xc,
        "x1_planet": x1p or "", "x1_count": x1c,
        "y_planet": yp or "", "y_count": yc,
        "y1_planet": y1p or "", "y1_count": y1c,
        "first": pick["first"] or "", "second": pick["second"] or "",
        "segments": json.dumps(seg_rows, separators=(",", ":")),
        "chain_score": round(chain, 4),
        "panchang_total": round(pan_total, 4),
    }


def build(index: str = "nifty", lat: float = MUMBAI[0],
          lon: float = MUMBAI[1],
          start=datetime.date(2011, 1, 1),
          end=datetime.date(2026, 8, 13)) -> str:
    bars = prices.load(index, start, end)
    rows, prev_ret, skipped = [], 0.0, 0
    for b in bars:
        d = datetime.date.fromisoformat(b["date"])
        ret = (b["close"] - b["open"]) / b["open"] * 100
        try:
            f = features_for(d, lat, lon)
        except Exception as e:                        # noqa: BLE001
            skipped += 1
            print(f"  skip {d}: {type(e).__name__}: {e}")
            continue
        f.update({"date": b["date"], "open": round(b["open"], 2),
                  "close": round(b["close"], 2), "ret_pct": round(ret, 4),
                  "up": int(ret > 0), "prev_ret": round(prev_ret, 4)})
        rows.append(f)
        prev_ret = ret

    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, f"features_{index}.csv")
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {path} — {len(rows)} rows"
          + (f", {skipped} skipped" if skipped else ""))
    return path


def load(index: str = "nifty") -> list[dict]:
    path = os.path.join(OUT_DIR, f"features_{index}.csv")
    with open(path, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    for r in rows:
        r["up"] = int(r["up"])
        r["year"] = int(r["year"])
        r["weekday"] = int(r["weekday"])
        r["thithi_num"] = int(r["thithi_num"])
        r["thithi_in_paksha"] = int(r["thithi_in_paksha"])
        r["segments"] = json.loads(r["segments"])
        for k in ("ret_pct", "chain_score", "panchang_total", "prev_ret",
                  "moon_lon", "sun_lon", "lagna_lon"):
            r[k] = float(r[k])
    return rows


if __name__ == "__main__":
    idx = sys.argv[1] if len(sys.argv) > 1 else "nifty"
    build(idx)
