#!/usr/bin/env python3
"""Run the 8-arm control grid and write results/<name>/{results.json,summary.md}.

    python run_grid.py                       # default grid
    python run_grid.py --quick               # small smoke run
    python run_grid.py --steps 20000 --seeds 20 --name long
"""

import argparse
import dataclasses
import json
from pathlib import Path

from tme.analysis import summary_markdown
from tme.experiment import Config, run_grid


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    for f in dataclasses.fields(Config):
        if f.type in (int, float, "int", "float"):
            ap.add_argument(f"--{f.name.replace('_', '-')}", type=type(f.default), default=None)
    ap.add_argument("--no-lyapunov", action="store_true")
    ap.add_argument("--quick", action="store_true", help="tiny run for smoke tests")
    ap.add_argument("--name", default=None, help="output folder under results/")
    args = ap.parse_args()

    cfg = Config()
    if args.quick:
        cfg = dataclasses.replace(cfg, L=4, steps=200, seeds=3, ref_factor=4, check_every=10)
    overrides = {f.name: getattr(args, f.name) for f in dataclasses.fields(Config)
                 if getattr(args, f.name, None) is not None}
    if args.no_lyapunov:
        overrides["lyapunov"] = False
    cfg = dataclasses.replace(cfg, **overrides)

    results = run_grid(cfg)
    out = Path("results") / (args.name or ("quick" if args.quick else "default"))
    out.mkdir(parents=True, exist_ok=True)
    (out / "results.json").write_text(json.dumps(results))
    summary = summary_markdown(results)
    (out / "summary.md").write_text(summary)
    print(summary)
    print(f"Wrote {out}/results.json and {out}/summary.md")


if __name__ == "__main__":
    main()
