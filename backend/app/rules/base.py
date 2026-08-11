"""Shared rule-finding schema (SPEC Section 8)."""
from dataclasses import dataclass


@dataclass
class Finding:
    section: str        # "graph" | "weekly" | "monthly" | "long_term" | "prasanam"
    title: str
    detail: str
    source: str         # exact lesson / document the rule came from
