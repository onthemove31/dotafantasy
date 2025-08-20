from __future__ import annotations

import json
from pathlib import Path
import numpy as np

from app.ml.features import build_team_win_classification_dataset


def train(output_dir: Path | None = None, patch: str = "7.37b", seed: int = 42) -> dict:
    np.random.seed(seed)
    ds = build_team_win_classification_dataset(patch)
    X = ds.X
    y = ds.y
    # Fallback logistic regression via gradient descent
    X1 = np.concatenate([X, np.ones((X.shape[0], 1))], axis=1)
    w = np.zeros(X1.shape[1])
    lr = 0.01
    for _ in range(1000):
        z = X1 @ w
        p = 1 / (1 + np.exp(-z))
        grad = X1.T @ (p - y) / len(y)
        w -= lr * grad
    logloss = float(-np.mean(y * np.log(p + 1e-8) + (1 - y) * np.log(1 - p + 1e-8)))

    out = {
        "patch": patch,
        "feature_names": ds.feature_names,
        "weights": w.tolist(),
        "metrics": {"LogLoss": logloss},
        "seed": seed,
    }
    if output_dir is None:
        output_dir = Path(__file__).resolve().parent / "artifacts" / "team"
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "model.json").write_text(json.dumps(out, indent=2))
    return out


if __name__ == "__main__":
    print(train())
