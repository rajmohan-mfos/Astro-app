"""Minimal daily OHLC fetch — stdlib only, so it ships in the deploy zip.

scripts/opt/prices.py is the study's fetcher and is deliberately NOT part
of the deployed set (bot/package_for_deploy.py ships app/, daily_push.py
and bot/ only). volmodel needs a short price history at inference time on
both the GitHub Actions path and the PythonAnywhere path, so the runtime
gets its own tiny fetcher here.

NETWORK NOTE. GitHub Actions has unrestricted outbound access, so the
daily push can always fetch. PythonAnywhere's free tier only permits hosts
on its proxy allowlist; api.telegram.org is on it, but Yahoo Finance is
not guaranteed to be. Every caller must therefore treat a fetch failure as
normal and degrade to "no price data" rather than raising — see
recent_bars() returning None.
"""
import datetime
import json
import os
import urllib.error
import urllib.request

IST = datetime.timezone(datetime.timedelta(hours=5.5))
SYMBOLS = {"nifty": "%5ENSEI", "banknifty": "%5ENSEBANK"}


def recent_bars(index: str = "nifty", days: int = 130,
                timeout: int = 20) -> list | None:
    """Last `days` calendar days of daily OHLC, oldest first.

    Returns None on any network or parse failure — callers are expected to
    carry on without the volatility line rather than fail the whole push.
    """
    symbol = SYMBOLS.get(index)
    if not symbol:
        return None
    end = datetime.datetime.now(IST)
    start = end - datetime.timedelta(days=days)
    url = (f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
           f"?period1={int(start.timestamp())}"
           f"&period2={int(end.timestamp()) + 86400}&interval=1d")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = json.load(r)
        res = data["chart"]["result"][0]
        q = res["indicators"]["quote"][0]
        bars = []
        for t, o, c, h, lo in zip(res["timestamp"], q["open"], q["close"],
                                  q["high"], q["low"]):
            if not o or c is None:
                continue
            bars.append({
                "date": datetime.datetime.fromtimestamp(t, IST)
                .date().isoformat(),
                "open": o, "close": c, "high": h, "low": lo})
        return bars or None
    except (urllib.error.URLError, urllib.error.HTTPError, KeyError,
            ValueError, TypeError, OSError):
        return None


# ------------------------------------------------------ published feed
# The fallback for hosts that cannot reach a quote provider. Measured
# against PythonAnywhere's free-tier allowlist: api.telegram.org and
# .githubusercontent.com are permitted, Yahoo is not, and .nseindia.com is
# permitted but blocks scripted clients. So the forecast is computed by
# GitHub Actions (unrestricted network) and read back from GitHub here.
GITHUB_REPO = os.environ.get("ASTRO_GITHUB_REPO", "rajmohan-mfos/Astro-app")
FORECAST_PATH = "backend/app/volforecast.json"
_LOCAL = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                      "volforecast.json")


def published_forecast(timeout: int = 20) -> dict | None:
    """The last forecast published by the daily workflow.

    Tries the local copy first — it ships in the deploy zip, so a fresh
    deploy answers instantly and works even with no network at all. Then
    GitHub, for a copy newer than the deploy.

    Returns None rather than raising; callers show "no forecast" instead
    of failing.
    """
    best = None
    try:
        with open(_LOCAL, encoding="utf-8") as f:
            best = json.load(f)
    except (OSError, ValueError):
        pass

    remote = _fetch_published(timeout)
    if remote and (not best or remote.get("generated_at", "") >
                   best.get("generated_at", "")):
        best = remote
    return best


def _fetch_published(timeout: int) -> dict | None:
    token = os.environ.get("ASTRO_GITHUB_TOKEN")
    if not token:
        return None            # private repo: without a token, skip quietly
    url = (f"https://api.github.com/repos/{GITHUB_REPO}/contents/"
           f"{FORECAST_PATH}")
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.raw+json",
        "User-Agent": "astro-app-bot"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.load(r)
    except (urllib.error.URLError, urllib.error.HTTPError, KeyError,
            ValueError, TypeError, OSError):
        return None


def forecast_age_hours(data: dict) -> float | None:
    """How old a published forecast is, so staleness is visible."""
    try:
        t = datetime.datetime.fromisoformat(data["generated_at"])
    except (KeyError, ValueError, TypeError):
        return None
    return (datetime.datetime.now(IST) - t).total_seconds() / 3600
