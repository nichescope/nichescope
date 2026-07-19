"""Deterministic demo listings so NicheScope runs without an API key."""
from __future__ import annotations

_ADJ = ["Personalized", "Minimalist", "Vintage", "Boho", "Rustic", "Modern",
        "Hand-painted", "Engraved", "Custom", "Dainty"]
_MAT = ["Ceramic", "Brass", "Linen", "Walnut", "Silver", "Glass", "Leather", "Wool"]
_ITEM = ["Necklace", "Mug", "Print", "Earrings", "Candle", "Pillow", "Sign", "Keychain"]


def _rng(seed: int):
    s = seed or 1
    def nxt():
        nonlocal s
        s = (s * 16807) % 2147483647
        return s / 2147483647
    return nxt


def mock_search(keyword: str, limit: int = 100):
    seed = sum(ord(c) for c in keyword) or 7
    rnd = _rng(seed)
    kw_words = [w for w in keyword.lower().split() if w]
    listings = []
    for i in range(limit):
        adj = _ADJ[int(rnd() * len(_ADJ))]
        mat = _MAT[int(rnd() * len(_MAT))]
        item = _ITEM[int(rnd() * len(_ITEM))]
        title = f"{adj} {mat} {item}"
        # weave the searched keyword into most titles/tags so metrics reflect it
        tags = [adj.lower(), mat.lower(), item.lower()] + kw_words
        if rnd() < 0.8 and kw_words:
            title = f"{adj} {kw_words[0].title()} {item}"
        listings.append({
            "listing_id": 9_000_000 + i,
            "title": title,
            "tags": tags,
            "num_favorers": int(rnd() * 800),
            "price": {"amount": int((6 + rnd() * 90) * 100), "divisor": 100,
                      "currency_code": "USD"},
        })
    # fake a plausible total from the keyword length
    total = 500 + (seed % 40) * 900
    return listings, total
