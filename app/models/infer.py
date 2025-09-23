#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Dict, Any, Tuple
from datetime import datetime
import json
from pathlib import Path


def _sigmoid(x: float) -> float:
    import math
    try:
        return 1.0 / (1.0 + math.exp(-x))
    except OverflowError:
        return 0.0 if x < 0 else 1.0


def _score_artifact(features: Dict[str, Any], artifact: Dict[str, Any]) -> Tuple[float, float, Dict[str, Any]]:
    """
    Return (prob_up, expected_move_pct, meta) using a JSON artifact.
    Missing features are treated as 0.0.
    """
    feats = artifact.get("features", [])
    dir_spec = artifact.get("direction", {})
    mag_spec = artifact.get("magnitude", {})

    # Direction (logistic)
    db = float(dir_spec.get("bias", 0.0))
    dw = {k: float(v) for k, v in dir_spec.get("weights", {}).items()}
    s_dir = db
    for f in feats:
        x = features.get(f)
        xv = 0.0 if x is None else float(x)
        s_dir += dw.get(f, 0.0) * xv
    prob_up = _sigmoid(s_dir)

    # Magnitude (linear)
    mb = float(mag_spec.get("bias", 0.0))
    mw = {k: float(v) for k, v in mag_spec.get("weights", {}).items()}
    y = mb
    for f in feats:
        x = features.get(f)
        xv = 0.0 if x is None else float(x)
        y += mw.get(f, 0.0) * xv
    clip = mag_spec.get("clip_pct")
    if clip is not None:
        try:
            c = float(clip)
            if c > 0:
                y = max(-c, min(c, y))
        except Exception:
            pass

    meta = {"model": "artifact_v1"}
    return prob_up, y, meta


def _fallback_stub(features: Dict[str, Any]) -> Tuple[float, float, Dict[str, Any]]:
    s_reddit = float(features.get("reddit_sentiment") or 0.0)
    s_trends = float(features.get("trends_inflation_z") or 0.0)
    pmi = features.get("ism_pmi_dev_from_50")
    s_pmi = 0.0 if pmi is None else max(-1.0, min(1.0, float(pmi) / 10.0))
    w_reddit, w_trends, w_pmi = 0.4, 0.35, 0.25
    composite = (w_reddit * s_reddit) + (w_trends * s_trends) + (w_pmi * s_pmi)
    composite = max(-1.0, min(1.0, composite))
    prob_up = 0.5 * (composite + 1.0)
    expected_move = 0.55 * composite
    return prob_up, expected_move, {"model": "stub_model_v0"}


def forecast_from_features(features: Dict[str, Any]) -> Dict[str, Any]:
    """
    Inference that prefers a JSON artifact if present; otherwise falls back
    to a simple heuristic mapping.
    """
    # Try artifact first
    artifact_path = Path(__file__).resolve().parent / "artifacts" / "model.json"
    prob_up: float
    expected_move: float
    meta: Dict[str, Any]
    if artifact_path.exists():
        try:
            art = json.loads(artifact_path.read_text(encoding="utf-8"))
            prob_up, expected_move, meta = _score_artifact(features, art)
        except Exception:
            prob_up, expected_move, meta = _fallback_stub(features)
    else:
        prob_up, expected_move, meta = _fallback_stub(features)

    # Intervals (keep simple symmetric bands)
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
        "meta": meta,
    }
    return out


