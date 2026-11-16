import pytest

from tme.stats import t_ppf, t_cdf


@pytest.mark.parametrize("p,df,expected", [
    (0.975, 29, 2.0452),   # standard t-table values
    (0.995, 29, 2.7564),
    (0.975, 9, 2.2622),
    (0.975, 1000, 1.9623),
])
def test_t_quantiles_match_tables(p, df, expected):
    assert abs(t_ppf(p, df) - expected) < 1e-3


def test_cdf_symmetric():
    assert abs(t_cdf(0.0, 10) - 0.5) < 1e-12
    assert abs(t_cdf(1.3, 7) + t_cdf(-1.3, 7) - 1) < 1e-12
