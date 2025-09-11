#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass
from typing import Optional
from datetime import datetime
try:
    from pytrends.request import TrendReq  # type: ignore
except Exception:
    TrendReq = None  # graceful fallback


@dataclass
class TrendsScore:
    key: str
    label: str
    zscore: float
    term: str
    as_of: datetime
    note: Optional[str] = None


def fetch_trends_stub(term: str = "inflation") -> TrendsScore:
    # Stubbed WoW z-score example
    return TrendsScore(
        key="trends",
        label="Google Trends (WoW z-score)",
        zscore=0.8,
        term=term,
        as_of=datetime.utcnow(),
        note="elevated interest",
    )


def fetch_trends(term: str = "inflation") -> TrendsScore:
    if TrendReq is None:
        return fetch_trends_stub(term)
    try:
        py = TrendReq(hl='en-US', tz=360)
        py.build_payload([term], timeframe='now 7-d', geo='US')
        df = py.interest_over_time()
        if df is None or df.empty:
            return fetch_trends_stub(term)
        series = df[term].dropna()
        if len(series) < 10:
            return fetch_trends_stub(term)
        # compute WoW z-score using last 7d vs prior values
        current = float(series.iloc[-1])
        mean = float(series.iloc[:-1].mean()) if len(series) > 1 else current
        std = float(series.iloc[:-1].std()) if len(series) > 2 else 1.0
        z = 0.0 if std == 0 else (current - mean) / std
        return TrendsScore(
            key="trends",
            label="Google Trends (WoW z-score)",
            zscore=z,
            term=term,
            as_of=datetime.utcnow(),
            note="computed from last 7d",
        )
    except Exception:
        return fetch_trends_stub(term)


