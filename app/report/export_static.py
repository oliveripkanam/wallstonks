#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Static exporter for GitHub Pages.

Generates:
- docs/data/glossary.json
- docs/data/features.json
- docs/data/forecast.json
- docs/data/forecast_model.json
- docs/data/health.json
- docs/index.html (rewrites CSS link to relative styles.css)
- docs/styles.css (copied if available)
"""

from pathlib import Path
import json
import shutil

from app.features.aggregate import latest_snapshot, features_snapshot


def build_glossary_payload():
    snap = latest_snapshot()
    items = [
        {
            "key": "news_sentiment",
            "name": "News Sentiment",
            "category": "News",
            "source": "RSS (Reuters, CNBC, etc.)",
            "definition": "Weighted, time-decayed VADER compound across curated headlines.",
            "latest": snap.get("news_sentiment"),
            "calculation": "weighted_avg(VADER_compound(headlines)) with time_decay",
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
            "definition": "Average sentiment from selected subreddits' recent post titles.",
            "latest": snap.get("reddit_sentiment"),
            "calculation": "avg(VADER_compound(titles))",
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
    return {"items": items, "as_of": snap.get("as_of"), "meta": {"error": None}}


def build_health_payload():
    from datetime import datetime
    from app.ingest.fred import get_fred_api_key, latest_value
    from app.ingest.trends import fetch_trends, TrendReq
    from app.ingest.reddit import fetch_reddit_sentiment
    from app.ingest.news import aggregate_news_sentiment
    import json as _json
    from pathlib import Path as _Path

    status = {"as_of": datetime.utcnow().isoformat() + "Z"}
    # FRED
    try:
        api_key = get_fred_api_key()
        latest_dates = {}
        fred_ok = False
        if api_key:
            for sid in ("CPIAUCSL", "PAYEMS", "NAPM", "NAPMNOI", "CONCCONF", "UMCSENT"):
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

    # Trends
    try:
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
        subs = []
        try:
            cfg_path = _Path(__file__).parents[2] / "app" / "config" / "defaults.json"
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

    # News
    try:
        feeds = []
        half_life = 6.0
        try:
            cfg_path = _Path(__file__).parents[2] / "app" / "config" / "defaults.json"
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

    status["live"] = any([
        status.get("fred", {}).get("ok"),
        status.get("trends", {}).get("ok"),
        status.get("reddit", {}).get("ok"),
        status.get("news", {}).get("ok"),
    ])
    return status


def export_docs():
    root = Path(__file__).resolve().parents[2]
    docs = root / "docs"
    data_dir = docs / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    # Write JSON payloads
    glossary = build_glossary_payload()
    (data_dir / "glossary.json").write_text(json.dumps(glossary, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    features = features_snapshot()
    (data_dir / "features.json").write_text(json.dumps(features, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    # Forecast
    from app.features.aggregate import daily_forecast_heuristic
    forecast = daily_forecast_heuristic()
    (data_dir / "forecast.json").write_text(json.dumps(forecast, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    # Model forecast (stub)
    try:
        from app.models.infer import forecast_from_features
        mf = forecast_from_features(features)
        (data_dir / "forecast_model.json").write_text(json.dumps(mf, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    except Exception:
        pass

    # Health snapshot for Pages
    try:
        health = build_health_payload()
        (data_dir / "health.json").write_text(json.dumps(health, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    except Exception:
        pass

    # Copy styles.css if present
    styles_src = root / "app" / "static" / "styles.css"
    if styles_src.exists():
        shutil.copyfile(styles_src, docs / "styles.css")

    # Copy index.html adjusting the CSS href to relative path
    index_src = root / "app" / "static" / "index.html"
    html = index_src.read_text(encoding="utf-8") if index_src.exists() else "<h1>WallStonks</h1>"
    html = html.replace("/static/styles.css", "styles.css")
    (docs / "index.html").write_text(html, encoding="utf-8")


def main():
    export_docs()


if __name__ == "__main__":
    main()


