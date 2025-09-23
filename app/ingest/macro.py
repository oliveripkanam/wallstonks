#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass
from typing import Optional
from datetime import datetime
import os
from .fred import get_fred_api_key, latest_value


@dataclass
class MacroValue:
    key: str
    label: str
    value: Optional[float]
    unit: str
    period: Optional[str]
    as_of: datetime


def fetch_cpi_stub() -> MacroValue:
    # Stubbed CPI YoY example
    return MacroValue(
        key="cpi",
        label="CPI YoY",
        value=3.2,
        unit="%",
        period="Aug 2025",
        as_of=datetime.utcnow(),
    )


def fetch_nfp_stub() -> MacroValue:
    # Stubbed NFP example
    return MacroValue(
        key="nfp",
        label="Nonfarm Payrolls",
        value=168000,
        unit="jobs",
        period="Aug 2025",
        as_of=datetime.utcnow(),
    )


def fetch_ism_pmi_stub() -> MacroValue:
    # Stubbed ISM Manufacturing PMI
    return MacroValue(
        key="ism_pmi",
        label="ISM Manufacturing PMI",
        value=48.6,
        unit="index",
        period="Aug 2025",
        as_of=datetime.utcnow(),
    )


def fetch_confidence_stub() -> MacroValue:
    # Stubbed Conference Board Consumer Confidence
    return MacroValue(
        key="confidence",
        label="Consumer Confidence (Conference Board)",
        value=104.2,
        unit="index",
        period="Aug 2025",
        as_of=datetime.utcnow(),
    )


# --- Live fetchers via FRED (fallback to stubs if unavailable) ---

def fetch_cpi_yoy_live() -> MacroValue:
    """
    CPI YoY (%): compute from FRED CPIAUCSL (CPI All Urban Consumers, Index 1982-84=100),
    YoY = ((level / level_12m_ago) - 1) * 100.
    """
    api_key = get_fred_api_key()
    if not api_key:
        return fetch_cpi_stub()
    try:
        from .fred import latest_and_lag
        pair = latest_and_lag("CPIAUCSL", api_key, months_back=12)
        if not pair:
            return fetch_cpi_stub()
        (dt_now, now_val), (_, prev_val) = pair
        yoy = ((now_val / prev_val) - 1.0) * 100.0 if prev_val else None
        return MacroValue(
            key="cpi",
            label="CPI YoY",
            value=round(yoy, 2) if yoy is not None else None,
            unit="%",
            period=dt_now.strftime("%b %Y"),
            as_of=datetime.utcnow(),
        )
    except Exception:
        return fetch_cpi_stub()


def fetch_nfp_live() -> MacroValue:
    """
    NFP (Nonfarm Payrolls, level, jobs): use PAYEMS series from FRED.
    Return the monthly change (Δ) vs previous month to match the usual NFP headline.
    """
    api_key = get_fred_api_key()
    if not api_key:
        return fetch_nfp_stub()
    try:
        from .fred import latest_and_prev
        pair = latest_and_prev("PAYEMS", api_key)
        if not pair:
            return fetch_nfp_stub()
        (dt_now, now_val), (_, prev_val) = pair
        delta = now_val - prev_val
        return MacroValue(
            key="nfp",
            label="Nonfarm Payrolls",
            value=int(round(delta)) if delta is not None else None,
            unit="jobs",
            period=dt_now.strftime("%b %Y"),
            as_of=datetime.utcnow(),
        )
    except Exception:
        return fetch_nfp_stub()


def fetch_ism_pmi_live() -> MacroValue:
    """
    ISM Manufacturing PMI: use FRED series NAPM (ISM Manufacturing: PMI Composite Index).
    """
    api_key = get_fred_api_key()
    if not api_key:
        return fetch_ism_pmi_stub()
    try:
        # Primary: PMI composite
        lv = latest_value("NAPM", api_key)
        if lv:
            dt_now, val = lv
            return MacroValue(
                key="ism_pmi",
                label="ISM Manufacturing PMI",
                value=round(val, 1),
                unit="index",
                period=dt_now.strftime("%b %Y"),
                as_of=datetime.utcnow(),
            )
        # Fallback: ISM New Orders Index as proxy directionally
        lv_alt = latest_value("NAPMNOI", api_key)
        if lv_alt:
            dt_now, val = lv_alt
            return MacroValue(
                key="ism_pmi",
                label="ISM New Orders Index (proxy PMI)",
                value=round(val, 1),
                unit="index",
                period=dt_now.strftime("%b %Y"),
                as_of=datetime.utcnow(),
            )
        return fetch_ism_pmi_stub()
    except Exception:
        return fetch_ism_pmi_stub()


def fetch_confidence_live() -> MacroValue:
    """
    Consumer Confidence (Conference Board): proxy via FRED series CONCCONF.
    Note: FRED provides a Conference Board index historical series identified as CONCCONF.
    """
    api_key = get_fred_api_key()
    if not api_key:
        return fetch_confidence_stub()
    try:
        # Primary: Conference Board (may be unavailable on FRED)
        lv = latest_value("CONCCONF", api_key)
        if lv:
            dt_now, val = lv
            return MacroValue(
                key="confidence",
                label="Consumer Confidence (Conference Board)",
                value=round(val, 1),
                unit="index",
                period=dt_now.strftime("%b %Y"),
                as_of=datetime.utcnow(),
            )
        # Fallback: University of Michigan Consumer Sentiment (UMCSENT)
        lv_alt = latest_value("UMCSENT", api_key)
        if lv_alt:
            dt_now, val = lv_alt
            return MacroValue(
                key="confidence",
                label="Consumer Sentiment (U. Michigan)",
                value=round(val, 1),
                unit="index",
                period=dt_now.strftime("%b %Y"),
                as_of=datetime.utcnow(),
            )
        return fetch_confidence_stub()
    except Exception:
        return fetch_confidence_stub()


