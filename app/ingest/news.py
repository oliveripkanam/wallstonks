#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass
from typing import List, Tuple, Union
from datetime import datetime
import math
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from app.ingest.rss import fetch_headlines, Headline


@dataclass
class NewsSentiment:
    key: str
    label: str
    score: float
    n_titles: int
    as_of: datetime


def aggregate_news_sentiment(
    feeds: List[Union[Tuple[str, str], Tuple[str, str, float]]],
    half_life_hours: float = 6.0,
) -> NewsSentiment:
    """
    Compute weighted VADER compound sentiment across recent headlines from the given feeds.
    - feeds: list of (source_name, feed_url[, source_weight])
    - weights: source_weight * time_decay(age_hours, half_life)
    """
    analyzer = SentimentIntensityAnalyzer()
    log2 = math.log(2.0)
    weighted_sum = 0.0
    weight_total = 0.0
    n = 0

    for entry in feeds:
        if len(entry) == 3:
            source_name, url, src_w = entry  # type: ignore[misc]
        else:
            source_name, url = entry  # type: ignore[misc]
            src_w = 1.0

        headlines = fetch_headlines(url, source_name)[:30]
        for h in headlines:
            title = h.title
            if not title:
                continue
            score = analyzer.polarity_scores(title)["compound"]
            # Age-based decay
            if isinstance(h.published_at, datetime):
                age_hours = max(0.0, (datetime.utcnow() - h.published_at).total_seconds() / 3600.0)
            else:
                age_hours = half_life_hours  # neutral penalty if unknown time
            decay = math.exp(-log2 * (age_hours / max(1e-6, half_life_hours)))
            w = max(0.0, float(src_w)) * decay
            weighted_sum += w * score
            weight_total += w
            n += 1

    if weight_total <= 0.0 or n == 0:
        return NewsSentiment(
            key="news_sentiment",
            label="News Sentiment",
            score=0.0,
            n_titles=0,
            as_of=datetime.utcnow(),
        )

    avg = weighted_sum / weight_total
    return NewsSentiment(
        key="news_sentiment",
        label="News Sentiment",
        score=avg,
        n_titles=n,
        as_of=datetime.utcnow(),
    )


