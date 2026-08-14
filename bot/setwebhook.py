"""Register (or inspect, or remove) the Telegram webhook.

Run from anywhere with the bot token in the environment:

  TELEGRAM_BOT_TOKEN=... TELEGRAM_WEBHOOK_SECRET=... \
      python bot/setwebhook.py https://PROJECT.vercel.app/api/telegram

  python bot/setwebhook.py --info      show the current registration
  python bot/setwebhook.py --delete    unregister (falls back to polling)

Note the path differs by host: Vercel serves the function at the file's
own route, /api/telegram, while the Flask app (bot/flask_app.py) serves
/webhook. Both implement the same two gates, so only the URL changes.

The secret is what the webhook checks on every request, so the same
value must be set as an environment variable on the host — Vercel:
Settings → Environment Variables; PythonAnywhere: the Web tab.
"""
import json
import os
import sys
import urllib.parse
import urllib.request


def api(method: str, **params) -> dict:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise SystemExit("TELEGRAM_BOT_TOKEN is not set")
    data = urllib.parse.urlencode(params).encode() if params else None
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/{method}", data=data)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def main() -> None:
    args = sys.argv[1:]
    if args and args[0] == "--info":
        info = api("getWebhookInfo")["result"]
        for k in ("url", "has_custom_certificate", "pending_update_count",
                  "last_error_date", "last_error_message",
                  "max_connections"):
            if k in info:
                print(f"  {k}: {info[k]}")
        if not info.get("url"):
            print("  (no webhook registered — the bot is in polling mode)")
        return
    if args and args[0] == "--delete":
        print(api("deleteWebhook", drop_pending_updates="true"))
        return
    if not args:
        raise SystemExit(__doc__)

    url = args[0]
    if not url.startswith("https://"):
        raise SystemExit("Telegram requires an https:// webhook URL")
    params = {"url": url, "drop_pending_updates": "true",
              "allowed_updates": json.dumps(["message", "edited_message"])}
    secret = os.environ.get("TELEGRAM_WEBHOOK_SECRET")
    if secret:
        params["secret_token"] = secret
    else:
        print("WARNING: no TELEGRAM_WEBHOOK_SECRET set — the endpoint will "
              "accept any POST that reaches it")
    print(api("setWebhook", **params))
    print("\nRegistered. Verify with:  python bot/setwebhook.py --info")


if __name__ == "__main__":
    main()
