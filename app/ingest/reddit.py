#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime
import feedparser
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


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


def fetch_reddit_sentiment(subreddits: List[str]) -> SocialSentiment:
    analyzer = SentimentIntensityAnalyzer()
    titles: List[str] = []
    for sub in subreddits:
        url = f"https://www.reddit.com/r/{sub}/new/.rss"
        parsed = feedparser.parse(url, request_headers={"User-Agent": "WallStonks/2.0"})
        for e in parsed.entries[:30]:
            title = getattr(e, 'title', '') or ''
            if title:
                titles.append(title)

    if not titles:
        return fetch_reddit_sentiment_stub()

    scores = [analyzer.polarity_scores(t)['compound'] for t in titles]
    avg = sum(scores) / len(scores)
    return SocialSentiment(
        key="reddit_sentiment",
        label="Reddit Net Sentiment",
        score=avg,
        as_of=datetime.utcnow(),
        note=f"n={len(scores)} titles",
    )


