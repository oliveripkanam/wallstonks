#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class SocialSentiment:
    key: str
    label: str
    score: float  # [-1, 1]
    as_of: datetime
    note: Optional[str] = None


def fetch_reddit_sentiment_stub() -> SocialSentiment:
    # Stubbed net sentiment example
    return SocialSentiment(
        key="reddit_sentiment",
        label="Reddit Net Sentiment",
        score=-0.12,
        as_of=datetime.utcnow(),
        note="WSB/downbeat; investing neutral",
    )


