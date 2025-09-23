#!/usr/bin/env python
# -*- coding: utf-8 -*-

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from datetime import datetime

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
    # Pull latest snapshot for "latest" values with robust fallbacks
    try:
        from app.features.aggregate import latest_snapshot
        snap = latest_snapshot()
    except Exception as e:
        snap = {"as_of": None, "_error": f"aggregation_failed: {e}"}
    items = [
        {
            "key": "news_sentiment",
            "name": "News Sentiment",
            "category": "News",
            "source": "RSS (Reuters, CNBC, etc.)",
            "definition": "Average VADER compound sentiment across recent curated headlines.",
            "latest": snap.get("news_sentiment"),
            "calculation": "avg(VADER_compound(headlines))",
        },
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
            "key": "ism_pmi",
            "name": "ISM Manufacturing PMI",
            "category": "Activity/PMI",
            "source": "ISM",
            "definition": "Diffusion index summarizing manufacturing activity; 50=neutral.",
            "latest": snap.get("ism_pmi"),
            "calculation": "level vs 50 and vs trailing mean",
        },
        {
            "key": "confidence",
            "name": "Consumer Confidence (Conference Board)",
            "category": "Confidence",
            "source": "Conference Board",
            "definition": "Survey-based index of consumer sentiment toward the economy.",
            "latest": snap.get("confidence"),
            "calculation": "standardized vs trailing mean",
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
    return JSONResponse({"items": items, "as_of": snap.get("as_of"), "meta": {"error": snap.get("_error")}})


@app.get("/api/features", response_class=JSONResponse)
async def features():
    try:
        from app.features.aggregate import features_snapshot
        data = features_snapshot()
        return JSONResponse(data)
    except Exception as e:
        return JSONResponse({"error": f"features_failed: {e}"}, status_code=500)


@app.get("/api/forecast", response_class=JSONResponse)
async def forecast():
    try:
        from app.features.aggregate import daily_forecast_heuristic
        data = daily_forecast_heuristic()
        return JSONResponse(data)
    except Exception as e:
        return JSONResponse({"error": f"forecast_failed: {e}"}, status_code=500)


@app.get("/api/forecast_model", response_class=JSONResponse)
async def forecast_model():
    try:
        from app.features.aggregate import features_snapshot
        from app.models.infer import forecast_from_features
        feats = features_snapshot()
        data = forecast_from_features(feats)
        return JSONResponse(data)
    except Exception as e:
        return JSONResponse({"error": f"forecast_model_failed: {e}"}, status_code=500)


@app.get("/api/health", response_class=JSONResponse)
async def health():
    """Quick liveness diagnostics for data sources.
    Returns which sources are reachable/live vs falling back.
    """
    status = {"as_of": datetime.utcnow().isoformat() + "Z"}
    # FRED
    try:
        from app.ingest.fred import get_fred_api_key, latest_value
        api_key = get_fred_api_key()
        fred_ok = False
        latest_dates = {}
        if api_key:
            for sid in ("CPIAUCSL", "PAYEMS", "NAPM", "CONCCONF"):
                try:
                    lv = latest_value(sid, api_key)
                    if lv:
                        dt, _ = lv
                        latest_dates[sid] = dt.strftime("%Y-%m-%d")
                except Exception:
                    latest_dates[sid] = None
            fred_ok = any(v is not None for v in latest_dates.values())
        status["fred"] = {"api_key": bool(api_key), "ok": fred_ok, "latest": latest_dates}
    except Exception as e:
        status["fred"] = {"api_key": False, "ok": False, "error": str(e)}

    # Google Trends
    try:
        from app.ingest.trends import fetch_trends, TrendReq
        trends_available = TrendReq is not None
        tr_ok = False
        note = None
        if trends_available:
            tr = fetch_trends("inflation")
            tr_ok = tr is not None and getattr(tr, "note", "").lower().startswith("computed")
            note = getattr(tr, "note", None)
        status["trends"] = {"available": trends_available, "ok": tr_ok, "note": note}
    except Exception as e:
        status["trends"] = {"available": False, "ok": False, "error": str(e)}

    # Reddit
    try:
        import json as _json
        from pathlib import Path as _Path
        from app.ingest.reddit import fetch_reddit_sentiment
        subs = []
        try:
            cfg_path = _Path(__file__).parents[1] / "config" / "defaults.json"
            cfg = _json.loads(cfg_path.read_text(encoding="utf-8"))
            subs = cfg.get("sources", {}).get("reddit", {}).get("subreddits", [])
        except Exception:
            subs = []
        red_ok = False
        n_titles = 0
        if subs:
            red = fetch_reddit_sentiment(subs)
            note = getattr(red, "note", "") or ""
            if note.startswith("n="):
                try:
                    n_titles = int(note.split("=", 1)[1].split()[0])
                except Exception:
                    n_titles = 0
            red_ok = n_titles > 0
        status["reddit"] = {"configured": bool(subs), "ok": red_ok, "n_titles": n_titles}
    except Exception as e:
        status["reddit"] = {"configured": False, "ok": False, "error": str(e)}

    # News (RSS)
    try:
        import json as _json
        from pathlib import Path as _Path
        from app.ingest.news import aggregate_news_sentiment
        feeds = []
        half_life = 6.0
        try:
            cfg_path = _Path(__file__).parents[1] / "config" / "defaults.json"
            cfg = _json.loads(cfg_path.read_text(encoding="utf-8"))
            news_cfg = cfg.get("sources", {}).get("news", [])
            half_life = float(cfg.get("nlp", {}).get("decay", {}).get("news_half_life_hours", 6))
            for entry in news_cfg:
                feeds.append((entry.get('name', 'News'), entry.get('url', ''), float(entry.get('weight', 1.0))))
        except Exception:
            feeds = []
        ns_ok = False
        n = 0
        if feeds:
            ns = aggregate_news_sentiment(feeds, half_life_hours=half_life)
            n = int(getattr(ns, "n_titles", 0) or 0)
            ns_ok = n > 0
        status["news"] = {"configured": bool(feeds), "ok": ns_ok, "n_titles": n}
    except Exception as e:
        status["news"] = {"configured": False, "ok": False, "error": str(e)}

    # Overall
    status["live"] = any([
        status.get("fred", {}).get("ok"),
        status.get("trends", {}).get("ok"),
        status.get("reddit", {}).get("ok"),
        status.get("news", {}).get("ok"),
    ])
    return JSONResponse(status)


