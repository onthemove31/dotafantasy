from __future__ import annotations

import argparse
from pathlib import Path
import json

from app.jobs.build_hero_patch_stats import compute_hero_patch_stats
from app.jobs.build_player_patch_stats import compute_player_patch_stats


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--window", type=int, default=60)
    parser.add_argument("--patch", type=str, required=True)
    parser.add_argument("--include-prev-minor", action="store_true")
    args = parser.parse_args()

    out_dir = Path(__file__).resolve().parents[2] / "artifacts"
    out_dir.mkdir(parents=True, exist_ok=True)

    hero_stats = [s.__dict__ for s in compute_hero_patch_stats(args.patch, args.window)]
    player_stats = [s.__dict__ for s in compute_player_patch_stats(args.patch, args.window)]

    (out_dir / f"hero_stats_{args.patch}.json").write_text(json.dumps(hero_stats, indent=2))
    (out_dir / f"player_stats_{args.patch}.json").write_text(json.dumps(player_stats, indent=2))
    print(f"Wrote hero and player stats to {out_dir}")


if __name__ == "__main__":
    main()
