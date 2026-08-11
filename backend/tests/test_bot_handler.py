"""Tests for the Telegram bot's command handling.

handle() is pure text-in / text-out, so the whole command surface is
testable without Flask, a webhook, or a network call.
"""
import datetime
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "bot"))
from handler import handle                                    # noqa: E402

IST = datetime.timezone(datetime.timedelta(hours=5.5))


def test_help_and_start_explain_the_bot():
    for cmd in ("/start", "/help", "", "   "):
        r = handle(cmd)
        assert "/tomorrow" in r and "/prasanam" in r


def test_today_and_tomorrow_are_different_days():
    a, b = handle("/today"), handle("/tomorrow")
    today = datetime.datetime.now(IST).date()
    assert today.strftime("%d %b %Y") in a
    assert (today + datetime.timedelta(days=1)).strftime("%d %b %Y") in b
    assert a != b


def test_date_accepts_iso_and_offsets():
    r = handle("/date 2026-09-15")
    assert "15 Sep 2026" in r
    today = datetime.datetime.now(IST).date()
    assert (today + datetime.timedelta(days=3)).strftime("%d %b %Y") \
        in handle("/d +3")


def test_date_without_argument_asks_for_one():
    assert "Give a date" in handle("/date")


def test_bad_date_is_rejected_not_silently_defaulted():
    r = handle("/date nextweek")
    assert "could not read date" in r.lower()
    # and it must NOT have quietly answered for today
    assert "Panchang:" not in r


def test_group_style_mentions_are_stripped():
    """In a group Telegram sends '/today@BotName'."""
    assert handle("/today@DailyIntradayPredictionKPbot") == handle("/today")


def test_prasanam_needs_a_number_in_range():
    assert "1–249" in handle("/prasanam")
    assert "out of range" in handle("/prasanam 250")
    assert "out of range" in handle("/prasanam 0")


def test_prasanam_casts_from_the_seed():
    r = handle("/prasanam 88")
    assert "number 88" in r
    assert "Verdict" in r


def test_chart_lists_bodies_with_lords():
    r = handle("/chart 2022-01-07")
    assert "07 Jan 2022" in r
    assert "Lahiri" in r          # the chart is Lahiri, not KP
    assert "star lord" in r
    for body in ("Nept", "Plut", "Uran", "Lag"):
        assert body in r          # outer planets + lagna are included


def test_unknown_command_falls_back_to_help():
    r = handle("/wibble")
    assert "Unknown command" in r and "/tomorrow" in r


def test_every_reply_carries_a_disclaimer_or_is_help():
    """A push that looks like a signal must say it is not one."""
    for cmd in ("/today", "/tomorrow", "/date +2"):
        assert "not financial advice" in handle(cmd).lower()


def test_handler_never_raises():
    """The webhook returns 200 regardless; the handler must not be the
    thing that breaks it."""
    for junk in ("/date ../../etc/passwd", "/prasanam abc", "/chart zzz",
                 "\x00\x01", "/" + "x" * 5000, "hello there"):
        assert isinstance(handle(junk), str)
