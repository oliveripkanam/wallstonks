#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Minimal training CLI to produce a JSON artifact for inference.

Usage:
  python -m app.models.train path/to/data.csv

CSV schema (columns):
  date, reddit_sentiment, trends_inflation_z, ism_pmi_dev_from_50, consumer_confidence, direction, move_pct

Notes:
  - Logistic regression for direction is implemented via simple gradient descent.
  - Linear regression for move_pct uses normal equations with ridge regularization.
  - This is intentionally lightweight; for richer models, consider scikit-learn.
"""

from __future__ import annotations

import sys
import json
from pathlib import Path
from typing import List

import math
import numpy as np
import pandas as pd


FEATURES: List[str] = [
    "reddit_sentiment",
    "trends_inflation_z",
    "ism_pmi_dev_from_50",
    "consumer_confidence",
]


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-x))


def fit_logistic(X: np.ndarray, y: np.ndarray, lr: float = 0.1, epochs: int = 300, l2: float = 0.0):
    n, d = X.shape
    w = np.zeros(d)
    b = 0.0
    for _ in range(epochs):
        z = X @ w + b
        p = sigmoid(z)
        grad_w = (X.T @ (p - y)) / n + l2 * w
        grad_b = float(np.sum(p - y) / n)
        w -= lr * grad_w
        b -= lr * grad_b
    return w, b


def fit_linear_ridge(X: np.ndarray, y: np.ndarray, l2: float = 1e-3):
    d = X.shape[1]
    A = X.T @ X + l2 * np.eye(d)
    b = X.T @ y
    w = np.linalg.solve(A, b)
    # intercept via centering trick
    y_mean = float(np.mean(y))
    X_mean = np.mean(X, axis=0)
    b0 = y_mean - float(X_mean @ w)
    return w, b0


def main():
    if len(sys.argv) < 2:
        print("Usage: python -m app.models.train path/to/data.csv")
        sys.exit(1)
    csv_path = Path(sys.argv[1]).resolve()
    if not csv_path.exists():
        print(f"File not found: {csv_path}")
        sys.exit(1)

    df = pd.read_csv(csv_path)
    for f in FEATURES + ["direction", "move_pct"]:
        if f not in df.columns:
            print(f"Missing column: {f}")
            sys.exit(1)

    # Prepare X, y
    X = df[FEATURES].astype(float).fillna(0.0).to_numpy()
    y_dir = df["direction"].astype(float).to_numpy()
    y_mag = df["move_pct"].astype(float).to_numpy()

    # Fit models
    w_dir, b_dir = fit_logistic(X, y_dir, lr=0.2, epochs=600, l2=0.001)
    w_mag, b_mag = fit_linear_ridge(X, y_mag, l2=1e-3)

    # Build artifact
    artifact = {
        "version": 1,
        "features": FEATURES,
        "direction": {
            "type": "logistic",
            "weights": {f: float(w_dir[i]) for i, f in enumerate(FEATURES)},
            "bias": float(b_dir),
        },
        "magnitude": {
            "type": "linear",
            "weights": {f: float(w_mag[i]) for i, f in enumerate(FEATURES)},
            "bias": float(b_mag),
            "clip_pct": 1.0,
        },
    }

    out_dir = Path(__file__).resolve().parent / "artifacts"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "model.json").write_text(json.dumps(artifact, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote model artifact to {out_dir / 'model.json'}")


if __name__ == "__main__":
    main()


