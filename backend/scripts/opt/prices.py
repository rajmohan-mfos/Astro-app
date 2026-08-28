"""Reproducible index price series, cached to disk.

The existing scripts/backtest_nifty.py fetches with `range={years}y`, which
is anchored to the wall-clock run date. That is why nifty_backtest.csv and
nifty_backtest_mumbai.csv cover different windows: the same nominal five
years, run a day apart. Two sweeps run on different days are not
comparable, which is fatal for a walk-forward study.

So this module fetches an ABSOLUTE window (period1/period2 unix seconds)
and caches the parsed bars to disk. Re-running on any later day returns the
identical series, byte for byte.
"""
import csv
import datetime
import json
import os
import urllib.request

IST = datetime.timezone(datetime.timedelta(hours=5.5))
CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "..", "..", "knowledge", "backtest", "opt", "cache")

SYMBOLS = {
    "nifty": "%5ENSEI",
    "banknifty": "%5ENSEBANK",
    "metal": "%5ECNXMETAL",
    "pharma": "%5ECNXPHARMA",
    # COMEX front-month futures — the Globex day Saptarsh's metals
    # report is written for (bars are dated in New York time)
    "gold": "GC%3DF",
    "silver": "SI%3DF",
}


def _cache_path(index: str, start: datetime.date, end: datetime.date) -> str:
    return os.path.join(CACHE_DIR, f"{index}_{start}_{end}.csv")


def _fetch(symbol: str, start: datetime.date, end: datetime.date):
    p1 = int(datetime.datetime.combine(
        start, datetime.time(0, 0), IST).timestamp())
    p2 = int(datetime.datetime.combine(
        end + datetime.timedelta(days=1), datetime.time(0, 0),
        IST).timestamp())
    url = (f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
           f"?period1={p1}&period2={p2}&interval=1d")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = json.load(r)
    res = data["chart"]["result"][0]
    q = res["indicators"]["quote"][0]
    bars = []
    for t, o, c, h, lo in zip(res["timestamp"], q["open"], q["close"],
                              q["high"], q["low"]):
        # backtest_nifty.py guards None but not a zero open, which then
        # divides by zero outside its try/except and kills the whole run.
        if not o or c is None:
            continue
        d = datetime.datetime.fromtimestamp(t, IST).date()
        bars.append({"date": d.isoformat(), "open": o, "close": c,
                     "high": h, "low": lo})
    return bars


def load(index: str = "nifty",
         start: datetime.date = datetime.date(2011, 1, 1),
         end: datetime.date = datetime.date(2026, 8, 13),
         refresh: bool = False) -> list[dict]:
    """Bars for an absolute window, from cache unless refresh=True."""
    if index not in SYMBOLS:
        raise SystemExit(f"index must be one of {sorted(SYMBOLS)}")
    path = _cache_path(index, start, end)
    if os.path.exists(path) and not refresh:
        with open(path, newline="", encoding="utf-8") as f:
            return [{"date": r["date"], "open": float(r["open"]),
                     "close": float(r["close"]),
                     "high": float(r["high"]) if r["high"] else None,
                     "low": float(r["low"]) if r["low"] else None}
                    for r in csv.DictReader(f)]

    bars = _fetch(SYMBOLS[index], start, end)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["date", "open", "close",
                                          "high", "low"])
        w.writeheader()
        w.writerows(bars)
    return bars


if __name__ == "__main__":
    b = load()
    print(f"{len(b)} bars  {b[0]['date']} -> {b[-1]['date']}")
    up = sum(1 for r in b if r["close"] > r["open"])
    print(f"up {up}/{len(b)} = {up / len(b) * 100:.2f}%  "
          f"always-down = {(len(b) - up) / len(b) * 100:.2f}%")
