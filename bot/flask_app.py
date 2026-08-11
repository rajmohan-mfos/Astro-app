"""Telegram webhook for PythonAnywhere. Transport and auth only —
all command logic lives in handler.py.

A webhook URL is public: anyone who guesses it can POST to it. Two gates,
both required:

1. Telegram's own `secret_token`, set when the webhook is registered and
   returned on every request as X-Telegram-Bot-Api-Secret-Token. A
   request without it is not from Telegram.
2. An allowlist of chat ids. Even a genuine Telegram update is ignored
   unless it comes from TELEGRAM_CHAT_ID, so a stranger who finds the bot
   cannot make it work — or run up compute on your account.

Environment (set in the PythonAnywhere Web tab, not in code):
  TELEGRAM_BOT_TOKEN
  TELEGRAM_CHAT_ID          the only chat allowed to use the bot
  TELEGRAM_WEBHOOK_SECRET   any random string; must match setwebhook.py
"""
import json
import os
import urllib.parse
import urllib.request

from flask import Flask, request

from handler import handle

app = Flask(__name__)
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


@app.route("/", methods=["GET"])
def health():
    return "astro-app bot is up", 200


@app.route("/webhook", methods=["POST"])
def webhook():
    secret = os.environ.get("TELEGRAM_WEBHOOK_SECRET")
    if secret and request.headers.get(
            "X-Telegram-Bot-Api-Secret-Token") != secret:
        return "", 403

    update = request.get_json(silent=True) or {}
    msg = update.get("message") or update.get("edited_message") or {}
    chat_id = str((msg.get("chat") or {}).get("id", ""))
    text = msg.get("text") or ""
    if not chat_id:
        return "", 200                      # nothing to reply to

    allowed = os.environ.get("TELEGRAM_CHAT_ID", "")
    if allowed and chat_id != allowed:
        # answer once so it is not a silent black hole, then ignore
        _send(chat_id, "This bot is private.")
        return "", 200

    try:
        _send(chat_id, handle(text))
    except Exception:
        # always 200: a non-200 makes Telegram retry the same update
        # repeatedly, which turns one bad message into a loop
        pass
    return "", 200
