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
