"""Etsy Open API v3 client — public listing search only (x-api-key auth)."""
from __future__ import annotations

import os
import httpx

API_BASE = "https://api.etsy.com/v3/application"
API_KEY = os.getenv("ETSY_API_KEY", "")


def has_api_key() -> bool:
    return bool(API_KEY) and API_KEY != "your_etsy_keystring_here"


async def _get(path: str, params: dict) -> dict:
    params = {k: v for k, v in params.items() if v not in (None, "")}
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.get(
            API_BASE + path,
            params=params,
            headers={"x-api-key": API_KEY},
        )
        r.raise_for_status()
        return r.json()


async def search_active(keywords: str, limit: int = 100) -> list[dict]:
    """Fetch up to `limit` active listings for a keyword (paged by 100)."""
    out: list[dict] = []
    offset = 0
    # When shop velocity is enabled, ask Etsy for Shop so we have shop names.
    include_shop = os.getenv("NICHESCOPE_VELOCITY") == "1"
    while len(out) < limit:
        params = {"keywords": keywords, "limit": min(100, limit - len(out)), "offset": offset}
        if include_shop:
            params["includes"] = "Shop"
        page = await _get("/listings/active", params)
        results = page.get("results", [])
        out.extend(results)
        total = page.get("count", 0)
        offset += len(results)
        if not results or offset >= total:
            break
    return out
