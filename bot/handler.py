"""Command handling for the Telegram bot — pure text in, text out.

Deliberately free of Flask, HTTP and Telegram types so the whole command
surface can be tested by calling handle("/tomorrow"). The web layer in
flask_app.py does transport and auth only.

Commands:
  /start /help          what the bot does
  /today /tomorrow      the day's reading
  /date YYYY-MM-DD      a specific day  (also /d +3, /d tomorrow)
  /prasanam <1-249>     KP horary from a seed number
  /chart                the panchang chart as text
"""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
for _p in (os.path.join(_HERE, "..", "backend"),
           os.path.join(_HERE, "..", "backend", "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from daily_push import LAT, LON, TZ, build_message, resolve_date  # noqa: E402
from app import engine, quotes, transit, volmodel                 # noqa: E402
from app.rules import prasanam as prasanam_rules                  # noqa: E402

HELP = """Astro-app bot — the GRAHA MARKETS method, as a study aid.

/today        today's reading
/tomorrow     tomorrow's reading
/date <when>  a specific day: /date 2026-09-15, /date +3
/prasanam <n> KP horary from a seed number 1-249
/chart        panchang chart (planets, degrees, star/sub lords)
/vol          volatility outlook — the ONE part with measured skill,
              and it contains no astrology
/help         this message

Not financial advice. A 5-year backtest over Nifty, BankNifty, Metal,
Pharma and a Defence proxy found no forecasting ability on any of them."""

DISCLAIMER = ("\n\n⚠️ Study aid, not a signal — backtested at no better "
              "than a coin flip.")


def _chart_text(d) -> str:
    cells = transit.chart_cells(d.year, d.month, d.day, 9, 0, TZ, LAT, LON)
    out = [f"Panchang chart — {d:%a %d %b %Y} 09:00, Lahiri", ""]
    for c in cells:
        if not c["items"]:
            continue
        out.append(c["rasi"])
        for it in c["items"]:
            out.append(f"  {it['short']:<5s} {it['deg']:>6s}"
                       f"{' (R)' if it['retro'] else '   '}"
                       f"  ★{it['star_short']} ·{it['sub_short']}")
    out.append("\n★ = star lord, · = sub lord")
    return "\n".join(out)


def _prasanam_text(arg: str, d) -> str:
    try:
        n = int(arg)
    except (TypeError, ValueError):
        return ("Give a number 1–249, e.g. /prasanam 88\n\n"
                "Hold your question in mind — one instrument, one "
                "direction, an explicit target and horizon — then pick "
                "the number without deliberating.")
    if not 1 <= n <= 249:
        return f"{n} is out of range — the KP horary numbers are 1 to 249."
    now = __import__("datetime").datetime.now(
        __import__("datetime").timezone(
            __import__("datetime").timedelta(hours=5.5)))
    findings = prasanam_rules.horary_rules(
        n, now.year, now.month, now.day, now.hour, now.minute,
        TZ, LAT, LON)
    out = [f"Prasanam — number {n}, asked {now:%d %b %H:%M} IST", ""]
    for f in findings:
        out.append(f"• {f.title}")
        out.append(f"  {f.detail}")
        out.append("")
    return "\n".join(out).strip()


def _vol_text() -> str:
    """The volatility model, on its own.

    Kept separate from every other command because it is a different kind
    of thing: no astrology in it, and unlike the rest of this bot it has
    measurable out-of-sample skill. It still only calls session WIDTH.
    """
    bars = quotes.recent_bars("nifty")
    if bars and len(bars) >= 10:
        f = volmodel.forecast(bars, len(bars))
        rows = [(c, volmodel.interval(bars, len(bars), c))
                for c in (0.80, 0.90, 0.95)]
        rows = [(c, iv["half_width_points"], iv["low"], iv["high"],
                 iv["realised_coverage"]) for c, iv in rows]
        p_wide, label = f["p_wide"], f["band"]
        hist, age = f["history_bars"], None
    else:
        # This host cannot reach a quote provider — the expected case on a
        # free tier with an outbound allowlist. Fall back to the forecast
        # the daily workflow published.
        d = quotes.published_forecast()
        if not d:
            return ("No forecast available yet. This host cannot reach a "
                    "quote provider, and no published forecast was found "
                    "— it is written each weekday morning by the daily "
                    "workflow.")
        rows = [(float(k), v["half_width_points"], v["low"], v["high"],
                 v["realised_coverage"])
                for k, v in sorted(d["intervals"].items())]
        p_wide, label = d["p_wide"], d["band_label"]
        hist, age = d["history_bars"], quotes.forecast_age_hours(d)

    lines = ["Nifty — next session\n"]
    for conf, pts, lo, hi, cov in rows:
        lines.append(f"  {conf:.0%} band  ±{pts:>4d} pts   "
                     f"{lo:.0f} – {hi:.0f}   (holds {cov:.0f}%)")
    stale = ""
    if age is not None:
        stale = (f"\nForecast published {age:.0f}h ago by the daily "
                 f"workflow — this host cannot fetch live prices.")
    return ("\n".join(lines) + "\n\n"
            f"  {label.upper()} session — P(wider than usual) = "
            f"{p_wide * 100:.0f}%\n"
            + stale + "\n\n"
            f"Bands adapt to the last {hist} sessions' high-low ranges, so "
            f"they tighten when the market is calm. 'Holds' is measured "
            f"out-of-sample 2016–2026, not assumed.\n"
            f"No astrology in these numbers — the panchang features were "
            f"measured to make them worse.\n\n"
            f"SIZE ONLY. Says nothing about up or down, and is not a "
            f"trading signal.")


def handle(text: str) -> str:
    """Map one message to one reply. Unknown input gets the help text."""
    raw = (text or "").strip()
    if not raw:
        return HELP
    parts = raw.split()
    cmd = parts[0].lower().lstrip("/")
    cmd = cmd.split("@")[0]           # /today@MyBot in groups
    arg = parts[1] if len(parts) > 1 else ""

    try:
        if cmd in ("start", "help"):
            return HELP
        if cmd in ("today", "tomorrow"):
            return build_message(resolve_date(cmd))
        if cmd in ("date", "d"):
            if not arg:
                return "Give a date: /date 2026-09-15, /date +3, /date tomorrow"
            return build_message(resolve_date(arg))
        if cmd == "prasanam":
            return _prasanam_text(arg, resolve_date("today"))
        if cmd == "chart":
            return _chart_text(resolve_date(arg or "today"))
        if cmd in ("vol", "volatility"):
            return _vol_text()
    except SystemExit as e:                 # resolve_date's rejection
        return str(e)
    except Exception as e:                  # never leak a stack trace
        return f"Could not compute that: {type(e).__name__}"

    return f"Unknown command: {parts[0]}\n\n{HELP}"
