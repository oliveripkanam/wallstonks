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
import math


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


def _tanh_scale(x: float, denom: float = 2.0) -> float:
    try:
        return math.tanh(x / denom)
    except Exception:
        return 0.0


def daily_forecast_heuristic() -> Dict[str, Any]:
    """
    Produce a simple daily forecast for SPY/DIA from public signals.
    Returns fields:
      - direction_prob_up (0..1)
      - expected_move_pct (signed, e.g., +0.28)
      - interval_pct {p50_low, p50_high, p80_low, p80_high}
      - drivers: ordered list of {name, contribution}
    """
    # Config and inputs
    cfg = {}
    try:
        cfg_path = Path(__file__).parents[1] / "config" / "defaults.json"
        cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    except Exception:
        pass

    # Reddit
    reddit = fetch_reddit_sentiment_stub()
    try:
        subs = cfg.get("sources", {}).get("reddit", {}).get("subreddits", [])
        if subs:
            reddit = fetch_reddit_sentiment(subs)
    except Exception:
        pass
    s_reddit = max(-1.0, min(1.0, float(reddit.score)))

    # Trends (inflation)
    try:
        tr = fetch_trends("inflation")
    except Exception:
        tr = fetch_trends_stub("inflation")
    s_trends = _tanh_scale(float(tr.zscore))  # ~[-1,1]

    # PMI deviation from neutral 50
    pmi = fetch_ism_pmi_stub()
    s_pmi = 0.0 if pmi.value is None else max(-1.0, min(1.0, (float(pmi.value) - 50.0) / 10.0))

    # News sentiment
    s_news = 0.0
    try:
        feeds = []
        news_cfg = cfg.get("sources", {}).get("news", [])
        for entry in news_cfg:
            feeds.append((entry.get('name', 'News'), entry.get('url', '')))
        if feeds:
            ns = aggregate_news_sentiment(feeds)
            s_news = max(-1.0, min(1.0, float(ns.score)))
    except Exception:
        s_news = 0.0

    # Weighted composite
    w_news, w_reddit, w_trends, w_pmi = 0.35, 0.25, 0.20, 0.20
    composite = (w_news * s_news) + (w_reddit * s_reddit) + (w_trends * s_trends) + (w_pmi * s_pmi)
    composite = max(-1.0, min(1.0, composite))

    # Direction probability and expected move (heuristic)
    prob_up = 0.5 * (composite + 1.0)
    # Expected signed move in percent; scale up to ~0.6% at |composite|=1
    expected_move = 0.6 * composite  # percent

    # Simple symmetric intervals
    p50_halfwidth = 0.35
    p80_halfwidth = 0.80
    p50 = {"p50_low": expected_move - p50_halfwidth, "p50_high": expected_move + p50_halfwidth}
    p80 = {"p80_low": expected_move - p80_halfwidth, "p80_high": expected_move + p80_halfwidth}

    drivers = [
        {"name": "News", "contribution": round(w_news * s_news, 3)},
        {"name": "Reddit", "contribution": round(w_reddit * s_reddit, 3)},
        {"name": "Trends (inflation)", "contribution": round(w_trends * s_trends, 3)},
        {"name": "PMI", "contribution": round(w_pmi * s_pmi, 3)},
    ]
    drivers.sort(key=lambda d: d["contribution"], reverse=True)

    payload = {
        "as_of": datetime.utcnow().isoformat() + "Z",
        "indices": {
            "SPY": {
                "direction_prob_up": round(prob_up, 3),
                "expected_move_pct": round(expected_move, 3),
                "interval_pct": {**p50, **p80},
                "drivers": drivers,
            },
            "DIA": {
                "direction_prob_up": round(prob_up, 3),
                "expected_move_pct": round(expected_move, 3),
                "interval_pct": {**p50, **p80},
                "drivers": drivers,
            },
        },
        "meta": {"model": "heuristic_v1", "notes": "Public-signal composite; no prices used."}
    }
    return payload

