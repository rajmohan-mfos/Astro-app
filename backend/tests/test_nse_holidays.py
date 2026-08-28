"""The push must stay silent on NSE holidays and weekends, and the
calendar must not rot silently when a new year arrives."""
import datetime
import os
import subprocess
import sys

from app import nse_holidays

HERE = os.path.dirname(__file__)
PUSH = os.path.join(HERE, "..", "scripts", "daily_push.py")


def test_2026_list_is_the_published_one():
    days = nse_holidays.HOLIDAYS[2026]
    assert len(days) == 16
    # every listed date is a weekday — a weekend entry is a typo
    assert all(d.weekday() < 5 for d in days)
    assert days[datetime.date(2026, 9, 14)] == "Ganesh Chaturthi"


def test_closed_reason():
    assert nse_holidays.closed_reason(datetime.date(2026, 8, 28)) is None
    assert nse_holidays.closed_reason(datetime.date(2026, 8, 29)) == "Saturday"
    assert nse_holidays.closed_reason(datetime.date(2026, 10, 2)) \
        == "Mahatma Gandhi Jayanti"
    assert nse_holidays.is_trading_day(datetime.date(2026, 8, 28))
    assert not nse_holidays.is_trading_day(datetime.date(2026, 12, 25))


def test_unknown_year_is_treated_as_open():
    assert nse_holidays.is_trading_day(datetime.date(2031, 1, 27))
    assert not nse_holidays.calendar_known(datetime.date(2031, 1, 27))


def _run(**env):
    e = {**os.environ, "ASTRO_DRY_RUN": "1", "PYTHONIOENCODING": "utf-8",
         **env}
    return subprocess.run([sys.executable, PUSH], env=e, capture_output=True,
                          text=True, encoding="utf-8", timeout=120).stdout


def test_push_skips_a_holiday_but_force_overrides():
    out = _run(ASTRO_DATE="2026-09-14")
    assert out.startswith("skipped: NSE closed on 2026-09-14")
    assert "Astro-app" not in out
    out = _run(ASTRO_DATE="2026-09-14", ASTRO_FORCE="1")
    assert "Astro-app" in out
    assert "NSE closed — Ganesh Chaturthi" in out


def test_push_sends_on_a_trading_day():
    out = _run(ASTRO_DATE="2026-08-28")
    assert out.startswith("📈 Astro-app")
    assert "NSE closed" not in out
    assert "No NSE holiday list" not in out


def test_message_warns_when_the_year_is_missing():
    out = _run(ASTRO_DATE="2031-01-27")
    assert "No NSE holiday list for 2031" in out
