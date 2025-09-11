#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Dict, Any
from datetime import datetime


def forecast_from_features(features: Dict[str, Any]) -> Dict[str, Any]:
    """
    Placeholder model inference using features snapshot.
    For now, delegate to a simple mapping similar to the heuristic.
    """
    s_reddit = float(features.get("reddit_sentiment") or 0.0)
    s_trends = float(features.get("trends_inflation_z") or 0.0)
    pmi = features.get("ism_pmi_dev_from_50")
    s_pmi = 0.0 if pmi is None else max(-1.0, min(1.0, float(pmi) / 10.0))

    # weights (tunable)
    w_reddit, w_trends, w_pmi = 0.4, 0.35, 0.25
    composite = (w_reddit * s_reddit) + (w_trends * s_trends) + (w_pmi * s_pmi)
    composite = max(-1.0, min(1.0, composite))
    prob_up = 0.5 * (composite + 1.0)
    expected_move = 0.55 * composite

    p50_halfwidth = 0.33
    p80_halfwidth = 0.78
    p50 = {"p50_low": expected_move - p50_halfwidth, "p50_high": expected_move + p50_halfwidth}
    p80 = {"p80_low": expected_move - p80_halfwidth, "p80_high": expected_move + p80_halfwidth}

    out = {
        "as_of": datetime.utcnow().isoformat() + "Z",
        "indices": {
            "SPY": {
                "direction_prob_up": round(prob_up, 3),
                "expected_move_pct": round(expected_move, 3),
                "interval_pct": {**p50, **p80},
            },
            "DIA": {
                "direction_prob_up": round(prob_up, 3),
                "expected_move_pct": round(expected_move, 3),
                "interval_pct": {**p50, **p80},
            },
        },
        "meta": {"model": "stub_model_v0"}
    }
    return out


