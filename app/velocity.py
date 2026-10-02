"""Optional shop velocity via publicrecords/etsy-shop-velocity (off by default)."""
from __future__ import annotations

import os
from typing import Any

def shop_velocity(shop_names: list[str]) -> dict[str, dict]:
    """Return {shop: velocity fields} or {} when disabled/no token.

    Live Actor fields (confirmed run Y4DLGuoWhmkhSvIa3): shop, delta_28d,
    sales_per_day, breakout, history_days, sales_precision, … Shops not in
    the panel are omitted by the Actor (treated here as no_coverage).
    """
    if os.environ.get("NICHESCOPE_VELOCITY") != "1" or not os.environ.get("APIFY_TOKEN"):
        return {}
    if not shop_names:
        return {}
    try:
        from apify_client import ApifyClient
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("apify-client is required when NICHESCOPE_VELOCITY=1") from exc

    client = ApifyClient(os.environ["APIFY_TOKEN"])
    run = client.actor("publicrecords/etsy-shop-velocity").call(
        run_input={"shops": shop_names}
    )
    out: dict[str, dict] = {}
    seen: set[str] = set()
    for r in client.dataset(run["defaultDatasetId"]).iterate_items():
        shop = r.get("shop")
        if not shop:
            continue
        seen.add(shop)
        out[shop] = {
            # live names
            "delta_28d": r.get("delta_28d"),
            "sales_per_day": r.get("sales_per_day"),
            "breakout": r.get("breakout"),
            "history_days": r.get("history_days"),
            "sales_precision": r.get("sales_precision"),
            # aliases matching earlier kit docs
            "sales_30d": r.get("delta_28d"),
            "rate_per_day": r.get("sales_per_day"),
            "readings": r.get("history_days"),
            "fidelity": r.get("sales_precision"),
            "status": "ok",
        }
    for name in shop_names:
        if name not in seen:
            out[name] = {
                "delta_28d": None,
                "sales_per_day": None,
                "breakout": None,
                "history_days": 0,
                "sales_precision": None,
                "sales_30d": None,
                "rate_per_day": None,
                "readings": 0,
                "fidelity": None,
                "status": "no_coverage",
            }
    return out


def shops_from_listings(listings: list[dict[str, Any]]) -> list[str]:
    names: set[str] = set()
    for listing in listings:
        shop = listing.get("shop") if isinstance(listing.get("shop"), dict) else None
        for candidate in (
            listing.get("shop_name"),
            (shop or {}).get("shop_name"),
            (shop or {}).get("name"),
            listing.get("login_name"),
        ):
            if isinstance(candidate, str) and candidate.strip():
                names.add(candidate.strip())
                break
    return sorted(names)
