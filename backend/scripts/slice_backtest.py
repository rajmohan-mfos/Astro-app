"""Slice the Nifty backtest by weekday and by horai window.

Weekday slice uses the daily CSV written by backtest_nifty.py.
Horai slice fetches 60-minute bars (Yahoo allows ~730 days at 60m) and
assigns each bar to the horai lord covering its midpoint, so the taught
hourly rules are tested against actual intraday moves rather than a
daily proxy.

Usage: python scripts/slice_backtest.py
"""
import csv
import datetime
import json
import os
import sys
import urllib.request
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app import transit                                   # noqa: E402

LAT, LON, TZ = 13.0827, 80.2707, 5.5
IST = datetime.timezone(datetime.timedelta(hours=5.5))
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
            "Saturday", "Sunday"]
SESSION = (9.25, 15.5)

# taught golden rules: (weekday, horai lord) -> expected direction
GOLDEN = {
    ("Monday", "Mercury"): "up",
    ("Tuesday", "Saturn"): "down",
    ("Wednesday", "Venus"): "up",
    ("Friday", "Mercury"): "up",
}
# day-independent horai table from the course guide §7
GENERIC = {"Sun": "down", "Saturn": "down", "Mars": "down",
           "Mercury": "up", "Jupiter": "up"}


def pct(hits, n):
    return f"{hits:5d}/{n:5d} = {hits / n * 100:5.1f}%" if n else "      —"


def weekday_slice():
    path = os.path.join(os.path.dirname(__file__), "..", "knowledge",
                        "backtest", "nifty_backtest.csv")
    rows = list(csv.DictReader(open(path, encoding="utf-8")))
    by_day = defaultdict(list)
    for r in rows:
        d = datetime.date.fromisoformat(r["date"])
        by_day[WEEKDAYS[d.weekday()]].append(r)

    print("=== Engine direction by weekday " + "=" * 34)
    print(f"{'weekday':12s} {'engine hit':>22s} {'actual up-rate':>22s}")
    for wd in WEEKDAYS[:5]:
        rs = by_day.get(wd, [])
        dirs = [r for r in rs if float(r["score"]) != 0]
        hits = sum(1 for r in dirs
                   if (float(r["score"]) > 0) == (float(r["ret_pct"]) > 0))
        ups = sum(1 for r in rs if float(r["ret_pct"]) > 0)
        print(f"{wd:12s} {pct(hits, len(dirs)):>22s} {pct(ups, len(rs)):>22s}")


def fetch_intraday(days=730):
    url = (f"https://query1.finance.yahoo.com/v8/finance/chart/%5ENSEI"
           f"?range={days}d&interval=60m")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=90) as r:
        data = json.load(r)
    res = data["chart"]["result"][0]
    q = res["indicators"]["quote"][0]
    bars = []
    for t, o, c in zip(res["timestamp"], q["open"], q["close"]):
        if o is None or c is None or o == 0:
            continue
        dt = datetime.datetime.fromtimestamp(t, IST)
        bars.append((dt, (c - o) / o * 100))
    return bars


def horai_slice(bars):
    cache = {}
    tagged = []
    for dt, ret in bars:
        d = dt.date()
        mid = dt.hour + dt.minute / 60 + 0.5          # bar midpoint
        if not (SESSION[0] <= mid <= SESSION[1]):
            continue
        if d not in cache:
            try:
                cache[d] = transit.horai_timeline(d.year, d.month, d.day,
                                                  TZ, LAT, LON)
            except Exception:
                cache[d] = None
        slots = cache[d]
        if not slots:
            continue
        lord = next((s["lord"] for s in slots
                     if s["start"] <= mid < s["end"]), None)
        if lord:
            tagged.append((WEEKDAYS[d.weekday()], lord, ret))

    print(f"\n=== Horai windows, {len(tagged)} hourly bars "
          f"({len(cache)} sessions) " + "=" * 12)

    print("\n-- every horai lord, all weekdays (mean move, % up) --")
    by_lord = defaultdict(list)
    for _, lord, ret in tagged:
        by_lord[lord].append(ret)
    print(f"{'horai':10s} {'bars':>6s} {'mean %':>9s} {'up-rate':>9s}  taught")
    for lord in sorted(by_lord, key=lambda k: -len(by_lord[k])):
        rs = by_lord[lord]
        up = sum(1 for r in rs if r > 0) / len(rs) * 100
        taught = GENERIC.get(lord, "—")
        print(f"{lord:10s} {len(rs):6d} {sum(rs) / len(rs):+9.4f} "
              f"{up:8.1f}%  {taught}")

    print("\n-- the taught weekday golden rules --")
    for (wd, lord), want in GOLDEN.items():
        rs = [r for w, l, r in tagged if w == wd and l == lord]
        if not rs:
            print(f"{wd} {lord} horai: no data")
            continue
        hits = sum(1 for r in rs if (r > 0) == (want == "up"))
        mean = sum(rs) / len(rs)
        print(f"{wd:10s} {lord:8s} horai → {want:4s}  "
              f"{pct(hits, len(rs))}  mean {mean:+.4f}%")

    # A horai lord is a deterministic function of (weekday, slot index), so
    # "Monday Mercury horai" and "Monday's ~7th daylight hour" are the same
    # bars. Separate the planet from the clock: compare each golden-rule
    # window against the SAME clock hour on other weekdays (different lord).
    print("\n-- planet or just time-of-day? same clock hour, other days --")
    hours = defaultdict(list)          # (weekday, hour) -> returns
    for dt, ret in bars:
        mid = dt.hour + dt.minute / 60 + 0.5
        if SESSION[0] <= mid <= SESSION[1]:
            hours[(WEEKDAYS[dt.date().weekday()], dt.hour)].append(ret)
    for (wd, lord), want in GOLDEN.items():
        # the clock hours this rule's window actually occupies
        occupied = set()
        for dt, _ in bars:
            mid = dt.hour + dt.minute / 60 + 0.5
            if (WEEKDAYS[dt.date().weekday()] != wd
                    or not SESSION[0] <= mid <= SESSION[1]):
                continue
            slots = cache.get(dt.date())
            if slots and next((s["lord"] for s in slots
                               if s["start"] <= mid < s["end"]), None) == lord:
                occupied.add(dt.hour)
        same_hour_other = [r for (w, h), rs in hours.items()
                           if w != wd and h in occupied for r in rs]
        if same_hour_other:
            up = sum(1 for r in same_hour_other if r > 0)
            print(f"{wd:10s} {lord:8s} hours {sorted(occupied)} on OTHER "
                  f"weekdays: {pct(up, len(same_hour_other))} up")

    print("\n-- opening bar when the session opens in a Saturn/Sun horai --")
    for lord in ("Saturn", "Sun"):
        rs = [r for w, l, r in tagged if l == lord]
        opens = []
        for dt, ret in bars:
            mid = dt.hour + dt.minute / 60 + 0.5
            if not (SESSION[0] <= mid < SESSION[0] + 1):
                continue
            slots = cache.get(dt.date())
            if slots and next((s["lord"] for s in slots
                               if s["start"] <= mid < s["end"]), None) == lord:
                opens.append(ret)
        if opens:
            down = sum(1 for r in opens if r < 0)
            print(f"open in {lord:7s} horai → down  {pct(down, len(opens))}"
                  f"  mean {sum(opens) / len(opens):+.4f}%")


def panchang_slice():
    """Slice the daily results by the Moon's nakshatra lord and by thithi
    family — the two panchang classifications the course grades."""
    from app import engine
    from app.rules import graph, panchang_rules

    path = os.path.join(os.path.dirname(__file__), "..", "knowledge",
                        "backtest", "nifty_backtest.csv")
    rows = list(csv.DictReader(open(path, encoding="utf-8")))

    # course star-lord temperament (guide §2 / slide 8)
    STAR = {"Mercury": "max positive", "Venus": "positive",
            "Moon": "positive", "Jupiter": "amplifies", "Sun": "neutral",
            "Mars": "60% negative", "Saturn": "strongly bearish",
            "Ketu": "max negative", "Rahu": "extreme either way"}

    by_lord, by_family = defaultdict(list), defaultdict(list)
    for r in rows:
        d = datetime.date.fromisoformat(r["date"])
        chart = engine.compute(d.year, d.month, d.day, 9, 15, TZ, LAT, LON)
        cast = graph.cast_chart(chart)
        moon = next(g for g in cast["grahas"] if g["name"] == "Moon")
        by_lord[graph.nak_lord_of(moon["lon"])].append(float(r["ret_pct"]))

        num = chart["panchang"]["thithi"]["num"]
        in_paksha = (num - 1) % 15 + 1
        fam = next((f for f, members, _, _ in panchang_rules.THITHI_FAMILIES
                    if in_paksha in members), "?")
        by_family[fam].append(float(r["ret_pct"]))

    print("\n=== Moon's nakshatra lord " + "=" * 40)
    print(f"{'lord':10s} {'days':>5s} {'mean %':>9s} {'up-rate':>9s}  taught")
    for lord in sorted(by_lord, key=lambda k: -len(by_lord[k])):
        rs = by_lord[lord]
        up = sum(1 for x in rs if x > 0) / len(rs) * 100
        print(f"{lord:10s} {len(rs):5d} {sum(rs) / len(rs):+9.4f} "
              f"{up:8.1f}%  {STAR.get(lord, '—')}")

    print("\n=== Thithi family " + "=" * 47)
    print(f"{'family':10s} {'days':>5s} {'mean %':>9s} {'up-rate':>9s}  graded")
    graded = {f: b for f, _, b, _ in panchang_rules.THITHI_FAMILIES}
    for fam in ("Nanda", "Bhadra", "Jaya", "Rikta", "Purna"):
        rs = by_family.get(fam, [])
        if not rs:
            continue
        up = sum(1 for x in rs if x > 0) / len(rs) * 100
        print(f"{fam:10s} {len(rs):5d} {sum(rs) / len(rs):+9.4f} "
              f"{up:8.1f}%  {graded.get(fam, '—')}")

    # the sharpest claim in the course: Rikta = 1000-2000 point gap-downs
    rikta = by_family.get("Rikta", [])
    other = [x for f, rs in by_family.items() if f != "Rikta" for x in rs]
    if rikta and other:
        big = sum(1 for x in rikta if x <= -1.0) / len(rikta) * 100
        big_o = sum(1 for x in other if x <= -1.0) / len(other) * 100
        print(f"\nRikta days falling >=1%: {big:.1f}%  "
              f"(all other days: {big_o:.1f}%)")


if __name__ == "__main__":
    weekday_slice()
    panchang_slice()
    horai_slice(fetch_intraday())
