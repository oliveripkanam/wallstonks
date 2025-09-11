#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Dict, Any
from datetime import datetime

from app.ingest.macro import fetch_cpi_stub, fetch_nfp_stub, fetch_ism_pmi_stub, fetch_confidence_stub
from app.ingest.reddit import fetch_reddit_sentiment_stub, fetch_reddit_sentiment
from app.ingest.trends import fetch_trends_stub, fetch_trends
from app.ingest.news import aggregate_news_sentiment
import json
from pathlib import Path


def latest_snapshot() -> Dict[str, Any]:
    """Return a minimal snapshot for the glossary page."""
    cpi = fetch_cpi_stub()
    nfp = fetch_nfp_stub()
    pmi = fetch_ism_pmi_stub()
    conf = fetch_confidence_stub()
    # Load config for reddit subs
    reddit = fetch_reddit_sentiment_stub()
    try:
        cfg_path = Path(__file__).parents[1] / "config" / "defaults.json"
        cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
        subs = cfg.get("sources", {}).get("reddit", {}).get("subreddits", [])
        if subs:
            reddit = fetch_reddit_sentiment(subs)
    except Exception:
        pass
    # trends (real with fallback)
    trends = fetch_trends_stub("inflation")
    try:
        trends = fetch_trends("inflation")
    except Exception:
        pass

    # news sentiment (RSS + VADER)
    news = None
    try:
        feeds = []
        news_cfg = cfg.get("sources", {}).get("news", []) if 'cfg' in locals() else []
        for entry in news_cfg:
            feeds.append((entry.get('name', 'News'), entry.get('url', '')))
        if feeds:
            news = aggregate_news_sentiment(feeds)
    except Exception:
        news = None

    return {
        "as_of": datetime.utcnow().isoformat() + "Z",
        "cpi": {
            "value": cpi.value,
            "unit": cpi.unit,
            "period": cpi.period,
        },
        "nfp": {
            "value": nfp.value,
            "unit": nfp.unit,
            "period": nfp.period,
        },
        "ism_pmi": {
            "value": pmi.value,
            "unit": pmi.unit,
            "period": pmi.period,
        },
        "confidence": {
            "value": conf.value,
            "unit": conf.unit,
            "period": conf.period,
        },
        "reddit_sentiment": {
            "score": reddit.score,
            "note": reddit.note,
        },
        "trends": {
            "term": trends.term,
            "zscore": trends.zscore,
            "note": trends.note,
        },
        "news_sentiment": ({
            "score": news.score,
            "n": news.n_titles,
        } if news else None),
    }


def features_snapshot() -> Dict[str, Any]:
    """Return a minimal composite feature set for the day."""
    # Load config
    cfg = {}
    try:
        cfg_path = Path(__file__).parents[1] / "config" / "defaults.json"
        cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    except Exception:
        pass

    # Reddit sentiment
    reddit = fetch_reddit_sentiment_stub()
    try:
        subs = cfg.get("sources", {}).get("reddit", {}).get("subreddits", [])
        if subs:
            reddit = fetch_reddit_sentiment(subs)
    except Exception:
        pass

    # Trends (inflation term as example)
    try:
        tr = fetch_trends("inflation")
    except Exception:
        tr = fetch_trends_stub("inflation")

    # Macro levels (use stubs for now)
    pmi = fetch_ism_pmi_stub()
    conf = fetch_confidence_stub()

    features: Dict[str, Any] = {
        "as_of": datetime.utcnow().isoformat() + "Z",
        "reddit_sentiment": reddit.score,
        "trends_inflation_z": tr.zscore,
        "ism_pmi_dev_from_50": (pmi.value - 50.0) if pmi.value is not None else None,
        "consumer_confidence": conf.value,
    }
    return features

