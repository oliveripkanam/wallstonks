# WallStonks — Public Sentiment & Macro Forecast

Single‑page site that aggregates public news, macro releases, Reddit sentiment, and Google Trends to explain and forecast the same‑day move of major indices (SPY/DIA). Built for GitHub Pages (static) and FastAPI (local dev).

## What this is
- A public‑data dashboard with an interactive Glossary & Methods page
- A “Daily Features” snapshot (Reddit, Trends, PMI, Confidence)
- A simple “Daily Forecast” (probability up, expected move, ranges, drivers)

## What we track
- News (RSS): Reuters Business/Markets, CNBC Markets
- Social: Reddit RSS — r/wallstreetbets, r/investing, r/stocks, r/economy
- Trends: Google Trends (inflation, recession, rate cut, layoffs, CPI, FOMC)
- Macro: CPI/NFP (stubs for now), ISM Manufacturing PMI, Consumer Confidence

## How we calculate (concise)
- News sentiment: VADER on recent headlines → average; source‑weighted, time‑decay planned
- Reddit sentiment: VADER on post titles → average
- Trends: WoW z‑score of term interest (pytrends)
- Macro: PMI deviation from neutral 50; other releases to use surprise vs trailing baseline
- Forecast (heuristic v1): weighted composite of News/Reddit/Trends/PMI →
  - direction_prob_up = (composite + 1) / 2
  - expected_move_pct = scale × composite (±~0.6% at full tilt)
  - intervals: rough 50% and 80% symmetric bands

## Run locally (dev)
```bash
python -m venv .venv && .\.venv\Scripts\activate
pip install -r requirements.txt
npm install && npm run build:css
python run.py  # http://localhost:8000
```

## Static preview (like GitHub Pages)
```bash
npm run build:css
python -m app.report.export_static
cd docs && python -m http.server 8080  # http://localhost:8080
```

## Deploy to GitHub Pages
1) Settings → Pages → Source: “Deploy from a branch”; Branch: `main`; Folder: `/docs`
2) A nightly GitHub Actions workflow regenerates `docs/` automatically

## Update frequency
- Local dev: computed on request; cached for 3 minutes (see `app/features/aggregate.py`)
- GitHub Pages: refreshed nightly at 02:15 UTC (see `.github/workflows/publish.yml`)

## Notes
- Public‑only inputs; no price‑based predictive features
- Future work: FinBERT, zero‑shot topics, macro surprise parsing, trained models


