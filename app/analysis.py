"""Turn a bag of raw Etsy listings into niche metrics."""
from __future__ import annotations

import re
from collections import Counter
from statistics import median

_WORD = re.compile(r"[a-z0-9]+")
_STOP = {
    "the", "and", "for", "with", "a", "an", "of", "to", "in", "on", "by",
    "handmade", "gift", "gifts", "custom", "personalized", "set", "new",
}


def _price(listing: dict) -> float | None:
    p = listing.get("price")
    if not isinstance(p, dict):
        return None
    amount = p.get("amount")
    divisor = p.get("divisor") or 100
    return round(amount / divisor, 2) if amount is not None else None


def analyze(keyword: str, listings: list[dict], total_count: int) -> dict:
    prices = [p for p in (_price(l) for l in listings) if p is not None]
    favs = [l.get("num_favorers", 0) or 0 for l in listings]

    # keyword frequency across titles + tags — the "what sells here" signal
    words: Counter[str] = Counter()
    for l in listings:
        text = (l.get("title") or "") + " " + " ".join(l.get("tags") or [])
        for w in _WORD.findall(text.lower()):
            if len(w) > 2 and w not in _STOP:
                words[w] += 1

    # price histogram (8 buckets across observed range)
    histogram: list[dict] = []
    if prices:
        lo, hi = min(prices), max(prices)
        span = (hi - lo) or 1
        buckets = 8
        counts = [0] * buckets
        for p in prices:
            idx = min(buckets - 1, int((p - lo) / span * buckets))
            counts[idx] += 1
        step = span / buckets
        histogram = [
            {"label": f"${lo + i * step:.0f}", "count": c}
            for i, c in enumerate(counts)
        ]

    def avg(xs):
        return round(sum(xs) / len(xs), 2) if xs else 0

    # crude competition read: many results + high avg favorites = crowded
    if total_count > 20000:
        competition = "High"
    elif total_count > 3000:
        competition = "Medium"
    else:
        competition = "Low"

    return {
        "keyword": keyword,
        "total_count": total_count,
        "sampled": len(listings),
        "competition": competition,
        "price": {
            "min": min(prices) if prices else 0,
            "max": max(prices) if prices else 0,
            "avg": avg(prices),
            "median": round(median(prices), 2) if prices else 0,
        },
        "favorites": {"avg": avg(favs), "max": max(favs) if favs else 0},
        "histogram": histogram,
        "top_tags": [{"tag": t, "count": c} for t, c in words.most_common(20)],
    }
