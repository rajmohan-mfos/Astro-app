"""Core factors — GRAHA MARKETS Astro Classes 2 & 3.

[C3 @ 02:03–03:47]: when the transit Moon "goes on Raghukethu" (moves
over the nodes), the day is treated with great caution — "see Raghukethu
very carefully… if Raghukethu comes, avoid it". Codified as: Moon in the
same rasi as Rahu or Ketu at the sunrise cast → avoid/volatile warning.
[C3 @ 05:22] also restates the panchang structure (thithi/karanam/yogam
relations) already codified elsewhere.
"""
from .base import Finding

SECTION = "graph"


def rules(chart: dict) -> list[Finding]:
    grahas = {g["name"]: g for g in chart["grahas"]}
    moon_sign = grahas["Moon"]["sign"]
    over = [n for n in ("Rahu", "Ketu") if grahas[n]["sign"] == moon_sign]
    if not over:
        return []
    return [Finding(
        SECTION,
        f"Moon over {'/'.join(over)} — trade with caution",
        "The transit Moon shares a rasi with the node today; the teacher "
        "says to watch Rahu/Ketu days very carefully and avoid entries "
        "when they interfere.",
        "Astro Class 3 @ 02:03–03:47")]
