#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


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


