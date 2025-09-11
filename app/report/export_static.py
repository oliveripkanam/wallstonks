#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Static exporter for GitHub Pages.

Generates:
- docs/data/glossary.json
- docs/data/features.json
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
    return {"items": items, "as_of": snap.get("as_of"), "meta": {"error": None}}


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


