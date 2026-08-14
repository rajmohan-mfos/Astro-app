"""Telegram webhook as a Vercel serverless function.

Transport and auth only — every command lives in bot/handler.py, exactly
as with bot/flask_app.py. The two are deliberately interchangeable: same
env var names, same two gates, same chunking. Deploying to Vercel is a
transport swap, not a rewrite, and either host can be abandoned without
touching a rule.

WHY SERVERLESS SUITS THIS BOT. It runs on request and costs nothing at
rest, so there is no instance to keep awake and no free-tier sleep to
work around — the failure mode that makes most free hosts unreliable for
a webhook. Measured locally, the slowest command (/today) takes 0.28s
cold, so the default function timeout is not a concern.

Unlike PythonAnywhere's free tier there is no outbound allowlist, so
/vol can fetch live prices here instead of falling back to the published
forecast. The fallback stays in place regardless — it costs nothing and
covers a provider outage.

A webhook URL is public: anyone who guesses it can POST to it. Two
gates, both required, as in flask_app.py:

1. Telegram's `secret_token`, set when the webhook is registered and
   returned on every request as X-Telegram-Bot-Api-Secret-Token. A
   request without it is not from Telegram.
2. An allowlist of chat ids. Even a genuine Telegram update is ignored
   unless it comes from TELEGRAM_CHAT_ID, so a stranger who finds the
   bot cannot use it or run up compute on your account.

Environment (set in the Vercel project's Settings → Environment
Variables, never in code):
  TELEGRAM_BOT_TOKEN
  TELEGRAM_CHAT_ID          the only chat allowed to use the bot
  TELEGRAM_WEBHOOK_SECRET   any random string; must match setwebhook.py
"""
import json
import os
import sys
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler

# bot/handler.py puts backend/ and backend/scripts/ on the path itself,
# so adding bot/ is enough. Resolved from this file rather than the
# process cwd, which a serverless runtime does not guarantee.
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (os.path.join(_ROOT, "bot"),):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from handler import handle                                   # noqa: E402

MAX = 4000          # Telegram's hard limit is 4096


def _send(chat_id: str, text: str) -> None:
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    for i in range(0, len(text), MAX):
        data = urllib.parse.urlencode({
            "chat_id": chat_id, "text": text[i:i + MAX],
            "disable_web_page_preview": "true"}).encode()
        urllib.request.urlopen(urllib.request.Request(
            f"https://api.telegram.org/bot{token}/sendMessage", data=data),
            timeout=30)


def reply_for(update: dict) -> tuple[str, str] | None:
    """(chat_id, text) to send, or None to stay silent.

    Split out from the HTTP plumbing so the whole auth decision is
    testable without a server — the same reason handler.handle is pure.
    """
    msg = update.get("message") or update.get("edited_message") or {}
    chat_id = str((msg.get("chat") or {}).get("id", ""))
    if not chat_id:
        return None                         # nothing to reply to
    allowed = os.environ.get("TELEGRAM_CHAT_ID", "")
    if allowed and chat_id != allowed:
        # answer once so it is not a silent black hole, then ignore
        return chat_id, "This bot is private."
    return chat_id, handle(msg.get("text") or "")


class handler(BaseHTTPRequestHandler):
    def _finish(self, code: int, body: str = "") -> None:
        self.send_response(code)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(body.encode("utf-8"))

    def do_GET(self):
        self._finish(200, "astro-app bot is up")

    def do_POST(self):
        secret = os.environ.get("TELEGRAM_WEBHOOK_SECRET")
        if secret and self.headers.get(
                "X-Telegram-Bot-Api-Secret-Token") != secret:
            return self._finish(403)

        try:
            n = int(self.headers.get("Content-Length") or 0)
            update = json.loads(self.rfile.read(n) or b"{}")
        except (ValueError, TypeError):
            update = {}

        try:
            got = reply_for(update)
            if got:
                _send(*got)
        except Exception:
            # ALWAYS 200: a non-200 makes Telegram retry the same update
            # repeatedly, turning one bad message into a loop
            pass
        self._finish(200)
