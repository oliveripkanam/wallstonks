### Sentiment & Macro News Aggregator — Essentials Build Plan

Goal: Daily, pre-open forecast of SPY/DIA direction and expected move using public news, official macro releases, Reddit sentiment, and Google Trends. One interactive page explains terms, shows latest values, and documents calculations.

## 1) Sources (public-only)
- News (RSS): Reuters Business/Markets, AP Top/Business, CNBC Markets
- Macro releases: BLS (CPI/PPI/Employment), BEA (GDP/PCE), ISM (PMIs), Census (Retail/Durable), Conference Board (Confidence), Fed (FOMC statements/minutes/speeches)
- Social: Reddit RSS (r/wallstreetbets, r/investing, r/stocks, r/economy)
- Trends: Google Trends via pytrends (inflation, recession, rate cut, layoffs, CPI, FOMC)

## 2) Minimal Pipeline (phased)
- P1 Fetch: Stateless connectors with retries/backoff, per-source rate limits, dedup by URL/title hash; simple disk cache
- P2 Normalize: Common schema {id, source, published_at_utc, title, snippet, url, language, meta}
- P3 NLP: Sentiment (FinBERT; fallback VADER), Topics (zero‑shot into: inflation, labor, growth, policy/Fed, credit/banks, geopolitics, energy/commodities, big tech, China/EU)
- P4 Macro Parse: For official releases, extract direction words and compute standardized surprise vs trailing baseline
- P5 Aggregate: Time-decay weights (news ~6h half-life, social ~2h); source weights; per-topic indices and momentum; social score; trends z-scores
- P6 Model: 
  - Direction: logistic/GBDT with probability calibration
  - Magnitude: quantile regression (25/50/75%) → expected move and intervals
  - Cutoff: features as of 9:25 ET; time-series CV with purge
- P7 Output: CLI report + JSON; generate single-page HTML “Glossary & Methods” with latest values and formula explainers

## 3) Features (used by model)
- Per-item score: sentiment × source_weight × time_decay × topic_relevance
- Topic indices (level, 6h vs 24h momentum)
- Macro event surprise z-scores per category (e.g., inflation, labor)
- Social bullish/bearish ratio (time-decayed, capped)
- Google Trends WoW z-scores for macro terms

## 4) Single Interactive Page (Glossary & Methods)
- One page with expandable terms covering: CPI/Core CPI, PPI/Core PPI, PCE/Core PCE, NFP, Unemployment, AHE, JOLTS, GDP, Retail Sales, Durable Goods, ISM Mfg/Services, Consumer Confidence, Fed Statement/Minutes/Speeches, Reddit Sentiment, Google Trends
- Each term: definition, source link, release cadence/next date, latest value/state, “How we calculate” (formulas), optional recent inputs (headlines/excerpts)
- Implementation: static HTML generated daily; native <details>/<summary> accordions; small JS for search/filter; embed JSON payload for values

## 5) Scheduling & Ops
- Pre-open job at 09:20–09:25 ET (Windows Task Scheduler or cron)
- Config in JSON/YAML (sources, topic labels, weights, decay half-lives, trends terms)
- Logging to files; cached raws under data/ (gitignored); resilience with retries/backoff

## 6) Minimal Folder Layout
- app/
  - ingest/ (rss.py, macro.py, reddit.py, trends.py, gdelt.py optional)
  - nlp/ (sentiment.py, topics.py)
  - features/ (aggregate.py)
  - models/ (train.py, infer.py)
  - report/ (build_glossary_page.py)
  - config/ (defaults.json)
- data/, logs/, reports/ (gitignored)

## 7) Milestones
- M1: Connectors + cache + dedup → sample JSON
- M2: Sentiment & topics operational → per-item features stored
- M3: Daily feature vector by 9:25 ET → JSON/CLI report
- M4: Baseline models trained & calibrated → expected move + intervals
- M5: Glossary page generated daily with latest values and formulas

## 8) Dependencies (add as needed)
- requests, feedparser, pandas, numpy, python-dateutil, pytz
- transformers, torch (CPU), vaderSentiment, langdetect
- pytrends, beautifulsoup4 (if parsing), tenacity
- scikit-learn, lightgbm or xgboost

Notes: Public-only inputs, no price-based features. On CPI/NFP/FOMC days prioritize macro event scores; shrink to zero on sparse-news days.


