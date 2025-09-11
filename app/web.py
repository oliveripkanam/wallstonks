#!/usr/bin/env python
# -*- coding: utf-8 -*-

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

app = FastAPI(title="WallStonks Web", version="2.0.0")

static_dir = Path(__file__).parent / "static"
static_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/", response_class=HTMLResponse)
async def index(_: Request):
    index_path = static_dir / "index.html"
    if not index_path.exists():
        return HTMLResponse("<h1>WallStonks</h1>")
    return HTMLResponse(index_path.read_text(encoding="utf-8"))


@app.get("/api/glossary", response_class=JSONResponse)
async def glossary():
    # Pull latest snapshot for "latest" values
    from app.features.aggregate import latest_snapshot
    snap = latest_snapshot()
    items = [
        {
            "key": "cpi",
            "name": "Consumer Price Index (CPI)",
            "category": "Inflation",
            "source": "BLS",
            "definition": "Measures average change over time in prices paid by consumers.",
            "latest": snap.get("cpi"),
            "calculation": "z = (actual - trailing_mean_k) / trailing_std_k",
        },
        {
            "key": "nfp",
            "name": "Nonfarm Payrolls (NFP)",
            "category": "Labor",
            "source": "BLS",
            "definition": "Change in the number of employed during the previous month, excluding farming.",
            "latest": snap.get("nfp"),
            "calculation": "z = (actual - trailing_mean_k) / trailing_std_k",
        },
        {
            "key": "reddit_sentiment",
            "name": "Reddit Sentiment",
            "category": "Social",
            "source": "Reddit RSS",
            "definition": "Net sentiment from selected subreddits' titles, time-decayed and weighted.",
            "latest": snap.get("reddit_sentiment"),
            "calculation": "score = sentiment * source_weight * time_decay",
        },
        {
            "key": "trends",
            "name": "Google Trends (Macro Terms)",
            "category": "Trends",
            "source": "Google Trends",
            "definition": "Week-over-week standardized change in search interest for macro terms.",
            "latest": snap.get("trends"),
            "calculation": "z = (term_value - mean) / std",
        },
    ]
    return JSONResponse({"items": items, "as_of": snap.get("as_of")})


