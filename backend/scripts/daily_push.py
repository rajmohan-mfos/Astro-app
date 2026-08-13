"""Send the day's prediction to Telegram. Driven by GitHub Actions cron.

Environment:
  TELEGRAM_BOT_TOKEN   from @BotFather
  TELEGRAM_CHAT_ID     your own chat id (see the workflow file for how)
  ASTRO_LAT/ASTRO_LON  optional, default Mumbai (the NSE's location)
  ASTRO_DATE           optional. YYYY-MM-DD, or the keywords `today`
                       / `tomorrow` / `+N` (N days ahead). Blank = today.
                       Keywords exist so the date can be typed on a phone
                       when triggering the workflow by hand.
  ASTRO_DRY_RUN        set to 1 to print the message instead of sending
  ASTRO_DIAGNOSE       set to 1 to check the token and list the chat ids
                       the bot can see, instead of sending. Use this when
                       Telegram answers "chat not found".

Nothing here stores a phone number: Telegram addresses a chat id, so the
number never enters the repository or its logs.

Usage: python scripts/daily_push.py
"""
import datetime
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app import engine, predict, quotes, volmodel          # noqa: E402

LAT = float(os.environ.get("ASTRO_LAT", 19.076))
LON = float(os.environ.get("ASTRO_LON", 72.8777))
TZ = 5.5
IST = datetime.timezone(datetime.timedelta(hours=5.5))

# NSE weekly holidays are handled by the cron (Mon-Fri only). Trading
# holidays are NOT: the job will still fire on them, since a holiday
# calendar would need maintaining every year. A message on a closed day
# is harmless noise.


def build_message(d: datetime.date) -> str:
    chart = engine.compute(d.year, d.month, d.day, 9, 0, TZ, LAT, LON)
    p = predict.run(chart)
    pan = chart["panchang"]

    def hhmm(h: float) -> str:
        return f"{int(h):02d}:{round((h % 1) * 60):02d}"

    L = [f"📈 Astro-app — {d.strftime('%a %d %b %Y')}",
         "",
         f"Panchang: {pan['vaara']['en']} · {pan['thithi']['name']} "
         f"({pan['thithi']['paksha']}) · {pan['natchathiram']['name']} "
         f"· {pan['yogam']['name']} · {pan['karanam']['name']}"]

    score = p.get("day_score")
    if score:
        L += ["", f"Day score: {score['conviction'].upper()} conviction — "
                  f"panchang {score['panchang_sign']} "
                  f"({score['panchang_total']:+g}), chain "
                  f"{score['chain_sign']} ({score['chain_score']:+g}), "
                  f"{score['agreement']}"]

    chain = p.get("chain")
    if chain:
        parts = [f"X={chain['x']['planet']}({chain['x']['count']})"
                 if chain.get("x") else "",
                 f"X1={chain['x1']['planet']}({chain['x1']['count']})"
                 if chain.get("x1") else "",
                 f"Y={chain['y']['planet']}({chain['y']['count']})"
                 if chain.get("y") else "",
                 f"Y1={chain['y1']['planet']}({chain['y1']['count']})"
                 if chain.get("y1") else ""]
        L += ["", "Chain: " + "  ".join(x for x in parts if x),
              f"Using {chain['first']} (first half) / {chain['second']} "
              f"(second half)"]

    segs = p.get("graph_segments") or []
    if segs:
        L += ["", "Intraday:"]
        L += [f"  {hhmm(s['start'])}–{hhmm(s['end'])}  "
              f"{s['planet']}({s['count']})  {s['bias']}" for s in segs]

    horai = [f for f in (p["sections"].get("graph") or [])
             if f["title"].startswith(("Horai", "Confluence", "Market opens"))]
    if horai:
        L += ["", "Horai notes:"]
        L += [f"  • {f['title']}" for f in horai[:4]]

    fit = (score or {}).get("fitted")
    if fit:
        L += ["", f"Fitted tables ({fit['in_sample_rate']:g}% in-sample / "
                  f"{fit['out_of_sample_rate']:g}% out-of-sample):",
              f"  {fit['call'].upper()}  (score {fit['total']:+g}, "
              f"threshold ±{fit['threshold']:g})",
              "  Tuned on the same history it is scored against — the "
              "first number describes the past, the second is what to "
              "expect."]

    vol = volatility_lines(d)
    if vol:
        L += vol

    L += ["",
          "⚠️ Study aid reproducing a taught method — NOT financial "
          "advice and not a signal. A 5-year backtest over Nifty, "
          "BankNifty, Metal, Pharma and a Defence proxy found no "
          "forecasting ability on any of them: the engine loses to "
          "\"always predict down\" on every index. Do not trade this."]
    return "\n".join(L)


def volatility_lines(d: datetime.date) -> list:
    """The one part of this message with measured predictive value.

    Deliberately separated from everything above it: this block contains
    no astrology at all. It is a 6-feature logistic regression on recent
    high-low ranges, ~60% out-of-sample on session WIDTH, and it says
    nothing whatever about direction.

    Returns [] if prices cannot be fetched — PythonAnywhere's free tier
    may not allow Yahoo, and a missing volatility line must never break
    the push.
    """
    bars = quotes.recent_bars("nifty")
    if not bars or len(bars) < 10:
        return []
    # score the next not-yet-traded session when d is past the last bar
    i = len(bars) if d.isoformat() > bars[-1]["date"] else len(bars) - 1
    try:
        f = volmodel.forecast(bars, i, date=d.isoformat())
    except (ValueError, KeyError, OSError):
        return []
    return ["", f"Volatility (no astrology, {f['oos_accuracy']}% "
            f"out-of-sample):",
            f"  {f['band'].upper()} session — P(wider than usual) = "
            f"{f['p_wide'] * 100:.0f}%",
            f"  expected range ≈ {f['expected_range_points']} pts "
            f"({f['expected_range_pct']:.2f}%)",
            "  Width only — says nothing about up or down."]


def send(text: str) -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat:
        raise SystemExit("TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be "
                         "set (repository secrets)")
    data = urllib.parse.urlencode({
        "chat_id": chat, "text": text,
        "disable_web_page_preview": "true"}).encode()
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/sendMessage", data=data)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            body = json.load(r)
    except urllib.error.HTTPError as e:
        # never echo the token; the URL contains it
        raise SystemExit(f"Telegram rejected the send: HTTP {e.code} "
                         f"{e.read().decode()[:200]}")
    if not body.get("ok"):
        raise SystemExit(f"Telegram returned not-ok: {body}")
    print("sent")


def _api(token: str, method: str) -> dict:
    with urllib.request.urlopen(
            f"https://api.telegram.org/bot{token}/{method}", timeout=30) as r:
        return json.load(r)


def diagnose() -> None:
    """Work out why a send failed, without ever printing the token.

    Prints chat ids and names only — never message text, since this lands
    in the Actions log.
    """
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat = os.environ.get("TELEGRAM_CHAT_ID")
    if not token:
        raise SystemExit("TELEGRAM_BOT_TOKEN is not set")
    print(f"TELEGRAM_CHAT_ID is {'set' if chat else 'NOT SET'}"
          + (f" ({len(chat)} chars, "
             f"{'numeric' if chat.lstrip('-').isdigit() else 'NOT NUMERIC'})"
             if chat else ""))
    if chat and chat != chat.strip():
        print("  WARNING: it has leading/trailing whitespace — that alone "
              "causes 'chat not found'")

    try:
        me = _api(token, "getMe")
    except urllib.error.HTTPError as e:
        raise SystemExit(f"token rejected: HTTP {e.code} — regenerate it "
                         f"with @BotFather")
    print(f"token OK — bot is @{me['result'].get('username')}")

    ups = _api(token, "getUpdates")
    chats = {}
    for u in ups.get("result", []):
        m = u.get("message") or u.get("channel_post") or {}
        c = m.get("chat")
        if c:
            chats[c["id"]] = (c.get("type"), c.get("first_name")
                              or c.get("title") or c.get("username"))
    if not chats:
        print("\nThe bot has received NO messages, so it cannot know your "
              "chat id.\nOpen Telegram, find the bot by the @username "
              "above, press Start,\nsend it any message, then run this "
              "again.")
        return
    print("\nchat ids this bot can message:")
    for cid, (kind, who) in chats.items():
        mark = "  <-- matches your secret" if str(cid) == (chat or "") else ""
        print(f"  {cid}   ({kind}, {who}){mark}")
    if chat and str(chat) not in {str(c) for c in chats}:
        print("\nYour TELEGRAM_CHAT_ID matches none of these. Set it to one "
              "of the ids above.")


def resolve_date(raw: str | None) -> datetime.date:
    """Blank / today / tomorrow / +N / YYYY-MM-DD, relative to IST.

    'Today' has to be IST, not the runner's UTC: at 02:45 UTC it is
    already 08:15 the same day in India, but a UTC-based `today` would
    still be correct there — whereas an evening run would not be. Using
    IST throughout removes the class of bug rather than one instance.
    """
    today = datetime.datetime.now(IST).date()
    s = (raw or "").strip().lower()
    if not s or s == "today":
        return today
    if s == "tomorrow":
        return today + datetime.timedelta(days=1)
    if s.startswith("+") and s[1:].isdigit():
        return today + datetime.timedelta(days=int(s[1:]))
    try:
        return datetime.date.fromisoformat(s)
    except ValueError:
        raise SystemExit(
            f"could not read date {raw!r} — use YYYY-MM-DD, or "
            f"today / tomorrow / +N")


def main() -> None:
    if os.environ.get("ASTRO_DIAGNOSE") == "1":
        diagnose()
        return
    d = resolve_date(os.environ.get("ASTRO_DATE"))
    text = build_message(d)
    if os.environ.get("ASTRO_DRY_RUN") == "1":
        print(text)
        return
    send(text)


if __name__ == "__main__":
    main()
