from tme.analysis import primary_verdicts, summary_markdown, compare
from tme.experiment import Config, run_grid


def test_grid_has_all_8_arms_and_verdicts():
    cfg = Config(L=4, steps=40, check_every=10, seeds=3, ref_factor=2, lyapunov=False)
    res = run_grid(cfg, progress=lambda *_: None)
    arms = {(a["topology"], a["integrator"], a["projection"]) for a in res["arms"]}
    assert len(arms) == 8
    v = primary_verdicts(res)
    assert len(v) == 4
    assert "Primary test" in summary_markdown(res)


def test_compare_verdicts():
    assert compare([10, 11, 12], [1, 2, 3])["verdict"] == "structured better"
    assert compare([1, 2, 3], [10, 11, 12])["verdict"] == "shuffled better"
    assert compare([1, 5, 9], [2, 5, 8])["verdict"] == "null"


def test_v1_pipeline_runs_and_v0_preset_unchanged():
    from tme.experiment import PRESETS
    from tme.analysis import summary_v1_markdown, gates
    import dataclasses
    assert PRESETS["v0"] == Config()
    cfg = dataclasses.replace(PRESETS["v1"], L=4, steps=40, check_every=10, seeds=3, ref_factor=2)
    res = run_grid(cfg, progress=lambda *_: None)
    md = summary_v1_markdown(res)
    assert "Primary test" in md
    assert gates(res)["torus"]["max_edge_phase_diff"] < 1.0  # starts near sync


def test_locked_init_is_near_sync():
    import dataclasses
    import numpy as np
    from tme.experiment import PRESETS, initial_state
    th, p, _ = initial_state(dataclasses.replace(PRESETS["v1"], seeds=5))
    assert np.abs(th).max() < 0.6 and abs(th.mean()) < 1e-12 and abs(p.mean()) < 1e-12


def test_prediction_outcomes():
    from tme.analysis import prediction_outcome
    r = lambda lo, hi: {"lo": lo, "hi": hi}
    assert prediction_outcome(r(0.97, 1.03), (0.95, 1.05)) == "confirmed"
    assert prediction_outcome(r(0.9, 1.1), (0.95, 1.05)) == "consistent"
    assert prediction_outcome(r(0.7, 0.9), (0.95, 1.05)) == "ruled out"
    assert prediction_outcome(r(0.77, 0.83), (0.75, 0.85), True) == "confirmed"
    assert prediction_outcome(r(0.8, 0.95), (0.75, 0.85), True) == "consistent"
    assert prediction_outcome(r(0.8, 1.1), (0.75, 0.85), True).startswith("consistent, but")
    assert prediction_outcome(r(0.9, 1.1), (0.75, 0.85), True) == "ruled out"
