#!/usr/bin/env python3
"""Run v2 (pre-registered in PREREGISTRATION-v2.md), plus its dt/2 check.

    python run_v2.py --name v2
    python run_v2.py --quick        # tiny smoke run
"""

import argparse
import dataclasses
import json
from pathlib import Path

from tme.analysis_v2 import summary_markdown
from tme.v2 import ConfigV2, run_v2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", default="v2")
    ap.add_argument("--quick", action="store_true")
    args = ap.parse_args()
    cfg = ConfigV2()
    if args.quick:
        cfg = dataclasses.replace(cfg, seeds=3, burn_steps=500, run_steps=2000)
    res = run_v2(cfg)
    # dt check: same physics at half the step, fresh noise, same seeds and projections
    half = dataclasses.replace(cfg, dt=cfg.dt / 2, burn_steps=2 * cfg.burn_steps,
                               run_steps=2 * cfg.run_steps, check_every=2 * cfg.check_every)
    res_half = run_v2(half)
    out = Path("results") / ("quick-v2" if args.quick else args.name)
    out.mkdir(parents=True, exist_ok=True)
    (out / "results.json").write_text(json.dumps({"main": res, "dt_half": res_half}))
    md = summary_markdown(res, res_half)
    (out / "summary.md").write_text(md)
    print(md)


if __name__ == "__main__":
    main()
