#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


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


