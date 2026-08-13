"""Publish the volatility forecast so the bot can read it without prices.

WHY THIS EXISTS. PythonAnywhere's free tier only permits outbound HTTP to
hosts on its allowlist. api.telegram.org and .githubusercontent.com are on
it; Yahoo Finance is not, and NSE — although allowlisted — blocks scripted
access (503, then 403 from a plain client, and a shared cloud IP fares
worse). So the bot cannot fetch prices itself.

GitHub Actions has unrestricted outbound access and already runs every
weekday morning. It therefore does the fetching, computes the FINISHED
forecast, and commits it here as JSON. The bot only reads and formats it —
it needs no price feed, no model and no numpy.

Refreshing once a day loses nothing worth having: the band is built from
63 sessions of high-low ranges, so one extra session moves it very little.
The published file carries `generated_at` and the bot always shows the
forecast's age, so a stale feed is visible rather than silently wrong.

Usage: python scripts/publish_forecast.py [out.json]
"""
import datetime
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app import quotes, volmodel                             # noqa: E402

DEFAULT_OUT = os.path.join(os.path.dirname(__file__), "..", "app",
                           "volforecast.json")
IST = datetime.timezone(datetime.timedelta(hours=5.5))


def build() -> dict | None:
    bars = quotes.recent_bars("nifty")
    if not bars or len(bars) < 10:
        return None
    i = len(bars)                    # the next, not-yet-traded session
    f = volmodel.forecast(bars, i)
    out = {
        "generated_at": datetime.datetime.now(IST).isoformat(timespec="seconds"),
        "last_bar": bars[-1]["date"],
        "reference_close": bars[-1]["close"],
        "p_wide": f["p_wide"],
        "band_label": f["band"],
        "oos_accuracy": f["oos_accuracy"],
        "history_bars": f["history_bars"],
        "intervals": {},
    }
    for conf in (0.80, 0.90, 0.95):
        iv = volmodel.interval(bars, i, conf)
        out["intervals"][f"{conf:.2f}"] = {
            "half_width_pct": iv["half_width_pct"],
            "half_width_points": iv["half_width_points"],
            "low": iv["low"], "high": iv["high"],
            "realised_coverage": iv["realised_coverage"],
        }
    return out


def main() -> None:
    out_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_OUT
    data = build()
    if data is None:
        # Not an error: leave whatever is already published in place rather
        # than overwriting a good forecast with an empty one.
        print("no price data — leaving the existing forecast untouched")
        return
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
    b = data["intervals"]["0.90"]
    print(f"wrote {out_path}")
    print(f"  last bar {data['last_bar']}  close {data['reference_close']:.0f}")
    print(f"  90% band +/-{b['half_width_points']} pts "
          f"({b['low']:.0f} - {b['high']:.0f})")


if __name__ == "__main__":
    main()
