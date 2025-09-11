#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass
from typing import List, Tuple
from datetime import datetime
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from app.ingest.rss import fetch_headlines, Headline


@dataclass
class NewsSentiment:
    key: str
    label: str
    score: float
    n_titles: int
    as_of: datetime


def aggregate_news_sentiment(feeds: List[Tuple[str, str]]) -> NewsSentiment:
    """
    Compute average VADER compound sentiment across recent headlines from the given feeds.
    feeds: list of (source_name, feed_url)
    """
    analyzer = SentimentIntensityAnalyzer()
    titles: List[str] = []
    for source_name, url in feeds:
        for h in fetch_headlines(url, source_name)[:30]:
            if h.title:
                titles.append(h.title)

    if not titles:
        return NewsSentiment(
            key="news_sentiment",
            label="News Sentiment",
            score=0.0,
            n_titles=0,
            as_of=datetime.utcnow(),
        )

    scores = [analyzer.polarity_scores(t)["compound"] for t in titles]
    avg = sum(scores) / len(scores)
    return NewsSentiment(
        key="news_sentiment",
        label="News Sentiment",
        score=avg,
        n_titles=len(scores),
        as_of=datetime.utcnow(),
    )


