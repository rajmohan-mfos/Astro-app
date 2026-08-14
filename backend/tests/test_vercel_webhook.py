"""Tests for the Vercel serverless webhook (api/telegram.py).

The auth decision is the part worth testing: a webhook URL is public, so
the two gates (Telegram's secret header and the chat-id allowlist) are
all that stand between a stranger and free compute on the account. Both
are pure functions of the request, so no server is needed.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "api"))
import telegram as fn                                        # noqa: E402

OWNER = "1184293568"


def _update(chat_id, text, key="message"):
    return {key: {"chat": {"id": chat_id}, "text": text}}


@pytest.fixture(autouse=True)
def _owner_only(monkeypatch):
    monkeypatch.setenv("TELEGRAM_CHAT_ID", OWNER)


def test_owner_gets_the_real_answer():
    chat, text = fn.reply_for(_update(int(OWNER), "/today"))
    assert chat == OWNER
    assert "Astro-app" in text
    assert "not financial advice" in text.lower()


def test_a_stranger_is_refused_but_not_ignored_silently():
    """A silent black hole looks like a broken bot; one flat refusal is
    kinder and still runs no rules for them."""
    chat, text = fn.reply_for(_update(999999, "/today"))
    assert chat == "999999"
    assert text == "This bot is private."


def test_a_stranger_never_reaches_the_rules():
    """The refusal must not be produced by running the command first."""
    called = []
    original = fn.handle
    fn.handle = lambda t: called.append(t) or "should not happen"
    try:
        fn.reply_for(_update(999999, "/today"))
    finally:
        fn.handle = original
    assert not called


def test_updates_without_a_chat_are_dropped():
    assert fn.reply_for({}) is None
    assert fn.reply_for({"message": {}}) is None
    assert fn.reply_for({"my_chat_member": {"chat": {"id": 1}}}) is None


def test_edited_messages_are_answered_too():
    chat, text = fn.reply_for(_update(int(OWNER), "/help", "edited_message"))
    assert chat == OWNER and "/tomorrow" in text


def test_no_allowlist_means_open_but_still_functional(monkeypatch):
    """If TELEGRAM_CHAT_ID is unset the bot answers anyone — deliberate,
    so a misconfigured deploy is debuggable rather than mutely dead."""
    monkeypatch.delenv("TELEGRAM_CHAT_ID", raising=False)
    chat, text = fn.reply_for(_update(4242, "/help"))
    assert chat == "4242" and "/tomorrow" in text


def test_chat_id_is_compared_as_a_string():
    """Telegram sends the id as a JSON number; the env var is a string.
    Comparing them raw would refuse the owner on every request."""
    chat, text = fn.reply_for(_update(int(OWNER), "/help"))
    assert text != "This bot is private."


def test_handler_exposes_both_verbs():
    """GET is the health check people hit in a browser; POST is Telegram."""
    assert hasattr(fn.handler, "do_GET")
    assert hasattr(fn.handler, "do_POST")


def test_chunk_size_stays_under_the_telegram_limit():
    assert fn.MAX < 4096
