"""NicheScope — Etsy keyword/niche research tool (FastAPI + Jinja2).

Public API only: given a keyword, sample active listings and report
competition, price distribution, favorites, and the tags that dominate.
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app import analysis, etsy, mock, velocity

BASE = Path(__file__).parent
app = FastAPI(title="NicheScope")
app.mount("/static", StaticFiles(directory=BASE / "static"), name="static")
templates = Jinja2Templates(directory=BASE / "templates")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html", {"request": request, "demo": not etsy.has_api_key()}
    )


@app.get("/api/analyze")
async def analyze(keyword: str = ""):
    keyword = keyword.strip()
    if not keyword:
        return JSONResponse({"error": "Enter a keyword to analyze."}, status_code=400)
    try:
        if etsy.has_api_key():
            listings = await etsy.search_active(keyword, limit=100)
            total = len(listings)  # count is returned per page; sample size is fine here
            report = analysis.analyze(keyword, listings, total)
        else:
            listings, total = mock.mock_search(keyword, limit=100)
            report = analysis.analyze(keyword, listings, total)
        report["demo"] = not etsy.has_api_key()
        # Optional hosted shop-velocity column (off unless NICHESCOPE_VELOCITY=1)
        shops = velocity.shops_from_listings(listings)
        vel = velocity.shop_velocity(shops)
        report["velocity_enabled"] = bool(vel) or (
            __import__("os").environ.get("NICHESCOPE_VELOCITY") == "1"
            and bool(__import__("os").environ.get("APIFY_TOKEN"))
        )
        report["shop_velocity"] = vel
        return report
    except Exception as exc:  # noqa: BLE001 — surface any API error to the UI
        return JSONResponse({"error": str(exc)}, status_code=500)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=int(os.getenv("PORT", "8000")))
