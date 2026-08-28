"""NSE trading-holiday calendar.

Hand-maintained: NSE publishes next year's list each December at
https://www.nseindia.com/resources/exchange-communication-holidays and
occasionally adds a date mid-year by circular (2026-01-15 was one).
Add each new year here; the morning push warns when the year is missing
rather than silently guessing.

Equity (Capital Market) segment only. Weekends are handled by weekday().
"""
import datetime

HOLIDAYS = {
    2026: {
        datetime.date(2026, 1, 15): "Maharashtra municipal elections",
        datetime.date(2026, 1, 26): "Republic Day",
        datetime.date(2026, 3, 3): "Holi",
        datetime.date(2026, 3, 26): "Shri Ram Navami",
        datetime.date(2026, 3, 31): "Shri Mahavir Jayanti",
        datetime.date(2026, 4, 3): "Good Friday",
        datetime.date(2026, 4, 14): "Dr. Baba Saheb Ambedkar Jayanti",
        datetime.date(2026, 5, 1): "Maharashtra Day",
        datetime.date(2026, 5, 28): "Bakri Id",
        datetime.date(2026, 6, 26): "Muharram",
        datetime.date(2026, 9, 14): "Ganesh Chaturthi",
        datetime.date(2026, 10, 2): "Mahatma Gandhi Jayanti",
        datetime.date(2026, 10, 20): "Dussehra",
        datetime.date(2026, 11, 10): "Diwali - Balipratipada",
        datetime.date(2026, 11, 24): "Prakash Gurpurb Sri Guru Nanak Dev",
        datetime.date(2026, 12, 25): "Christmas",
    },
}


def calendar_known(d: datetime.date) -> bool:
    return d.year in HOLIDAYS


def closed_reason(d: datetime.date) -> str | None:
    """Why the NSE is shut on `d`, or None if it is a trading day.

    An unknown year is treated as open: better a message on a holiday
    than silence for a year.
    """
    if d.weekday() >= 5:
        return d.strftime("%A")
    return HOLIDAYS.get(d.year, {}).get(d)


def is_trading_day(d: datetime.date) -> bool:
    return closed_reason(d) is None
