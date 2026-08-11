"""Shared rule-finding schema (SPEC Section 8) and helpers."""
import datetime
from dataclasses import dataclass


def date_slice(start: str, end: str, i: int, n: int) -> tuple[str, str]:
    """Equal i-th slice of the [start, end] date span, as ISO dates.

    Used to share a prediction window among the occupants of a star —
    [C11] "one and a half month is Venus and one and a half month is
    Moon"; the intraday equivalent is Class 10's x1/x2 split.
    """
    a = datetime.date.fromisoformat(start)
    b = datetime.date.fromisoformat(end)
    total = (b - a).days
    return (str(a + datetime.timedelta(days=total * i // n)),
            str(a + datetime.timedelta(days=total * (i + 1) // n)))


@dataclass
class Finding:
    section: str        # "graph" | "weekly" | "monthly" | "long_term" | "prasanam"
    title: str
    detail: str
    source: str         # exact lesson / document the rule came from
