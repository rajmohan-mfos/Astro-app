"""Send the day's prediction to Telegram. Driven by GitHub Actions cron.

Environment:
  TELEGRAM_BOT_TOKEN   from @BotFather
  TELEGRAM_CHAT_ID     your own chat id (see the workflow file for how)
  ASTRO_LAT/ASTRO_LON  optional, default Mumbai (the NSE's location)
  ASTRO_DATE           optional YYYY-MM-DD, for testing a specific day
  ASTRO_DRY_RUN        set to 1 to print the message instead of sending

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
from app import engine, predict                            # noqa: E402

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

    L += ["",
          "⚠️ Study aid reproducing a taught method — NOT financial "
          "advice and not a signal. A 5-year backtest over Nifty, "
          "BankNifty, Metal, Pharma and a Defence proxy found no "
          "forecasting ability on any of them: the engine loses to "
          "\"always predict down\" on every index. Do not trade this."]
    return "\n".join(L)


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


def main() -> None:
    raw = os.environ.get("ASTRO_DATE")
    d = (datetime.date.fromisoformat(raw) if raw
         else datetime.datetime.now(IST).date())
    text = build_message(d)
    if os.environ.get("ASTRO_DRY_RUN") == "1":
        print(text)
        return
    send(text)


if __name__ == "__main__":
    main()
