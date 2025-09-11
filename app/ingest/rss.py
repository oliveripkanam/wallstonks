#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
import feedparser


@dataclass
class Headline:
    source: str
    title: str
    link: str
    published_at: Optional[datetime]


def parse_time(entry):
    try:
        if 'published_parsed' in entry and entry.published_parsed:
            return datetime(*entry.published_parsed[:6])
    except Exception:
        pass
    return None


def fetch_headlines(feed_url: str, source_name: str) -> List[Headline]:
    parsed = feedparser.parse(feed_url, request_headers={"User-Agent": "WallStonks/2.0"})
    items: List[Headline] = []
    for e in parsed.entries[:25]:  # cap per feed
        items.append(Headline(
            source=source_name,
            title=getattr(e, 'title', '') or '',
            link=getattr(e, 'link', '') or '',
            published_at=parse_time(e),
        ))
    return items


