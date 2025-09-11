#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Dict, Any
from datetime import datetime

from app.ingest.macro import fetch_cpi_stub, fetch_nfp_stub
from app.ingest.reddit import fetch_reddit_sentiment_stub
from app.ingest.trends import fetch_trends_stub


def latest_snapshot() -> Dict[str, Any]:
    """Return a minimal snapshot for the glossary page."""
    cpi = fetch_cpi_stub()
    nfp = fetch_nfp_stub()
    reddit = fetch_reddit_sentiment_stub()
    trends = fetch_trends_stub("inflation")

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
        "reddit_sentiment": {
            "score": reddit.score,
            "note": reddit.note,
        },
        "trends": {
            "term": trends.term,
            "zscore": trends.zscore,
            "note": trends.note,
        },
    }


