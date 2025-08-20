from __future__ import annotations

import json
from pathlib import Path
import numpy as np

from app.ml.features import build_player_fantasy_regression_dataset


def train(output_dir: Path | None = None, patch: str = "7.37b", seed: int = 42) -> dict:
    np.random.seed(seed)
    ds = build_player_fantasy_regression_dataset(patch)
    # Fallback simple linear regression using numpy (xgboost may not be available in CI)
    X = ds.X
    y = ds.y
    X1 = np.concatenate([X, np.ones((X.shape[0], 1))], axis=1)
    coef, *_ = np.linalg.lstsq(X1, y, rcond=None)
    pred = X1 @ coef
    mae = float(np.mean(np.abs(pred - y)))
    r2 = float(1 - np.sum((y - pred) ** 2) / np.sum((y - y.mean()) ** 2 + 1e-8))

    out = {
        "patch": patch,
        "feature_names": ds.feature_names,
        "coef": coef.tolist(),
        "metrics": {"MAE": mae, "R2": r2},
        "seed": seed,
    }
    if output_dir is None:
        output_dir = Path(__file__).resolve().parent / "artifacts" / "player"
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "model.json").write_text(json.dumps(out, indent=2))
    return out


if __name__ == "__main__":
    print(train())
