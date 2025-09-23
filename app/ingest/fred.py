#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Minimal FRED client helpers for fetching recent observations for a given series.

Environment:
  - FRED_API_KEY: required for live requests. If missing, callers should fallback.

Notes:
  - We keep dependencies minimal and use `requests` directly.
  - We request roughly the last 3 years of data to compute deltas/YoY.
"""

from __future__ import annotations

from typing import List, Tuple
from datetime import datetime, timedelta
import os
import requests

FRED_BASE = "https://api.stlouisfed.org/fred/series/observations"


def get_fred_api_key() -> str | None:
    return os.environ.get("FRED_API_KEY")


def _to_iso(d: datetime) -> str:
    return d.strftime("%Y-%m-%d")


def fetch_series_observations(series_id: str, api_key: str, start: datetime | None = None) -> List[Tuple[datetime, float]]:
    """
    Fetch observations for a FRED series starting from `start` (default: ~3 years ago).
    Returns a list of (date, value) sorted ascending by date.
    Filters out missing values ('.').
    """
    if start is None:
        start = datetime.utcnow() - timedelta(days=365 * 3)

    params = {
        "series_id": series_id,
        "api_key": api_key,
        "file_type": "json",
        "observation_start": _to_iso(start),
    }
    r = requests.get(FRED_BASE, params=params, timeout=15)
    r.raise_for_status()
    data = r.json()
    obs = data.get("observations", [])
    out: List[Tuple[datetime, float]] = []
    for o in obs:
        v = o.get("value")
        if not v or v == ".":
            continue
        try:
            dt = datetime.strptime(o.get("date"), "%Y-%m-%d")
            out.append((dt, float(v)))
        except Exception:
            continue
    out.sort(key=lambda x: x[0])
    return out


def latest_value(series_id: str, api_key: str) -> Tuple[datetime, float] | None:
    obs = fetch_series_observations(series_id, api_key)
    if not obs:
        return None
    return obs[-1]


def latest_and_prev(series_id: str, api_key: str) -> Tuple[Tuple[datetime, float], Tuple[datetime, float]] | None:
    obs = fetch_series_observations(series_id, api_key)
    if not obs or len(obs) < 2:
        return None
    return obs[-1], obs[-2]


def latest_and_lag(series_id: str, api_key: str, months_back: int) -> Tuple[Tuple[datetime, float], Tuple[datetime, float]] | None:
    """Return (latest, lagged_by_months) if available."""
    obs = fetch_series_observations(series_id, api_key)
    if not obs or len(obs) <= months_back:
        return None
    return obs[-1], obs[-1 - months_back]
