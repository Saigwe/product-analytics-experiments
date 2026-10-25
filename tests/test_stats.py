import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from experiments.stats import cuped, diff_in_means, guardrail, sample_size_per_arm, srm_check  # noqa: E402


def test_sample_size_matches_the_textbook_value():
    # 10% baseline, +10% relative (10% -> 11%), alpha 0.05, power 0.8: about 14,750 per arm
    n = sample_size_per_arm(0.10, 0.10)
    assert 14_600 <= n <= 14_900


def test_sample_size_grows_with_smaller_effects():
    assert sample_size_per_arm(0.05, 0.05) > 3 * sample_size_per_arm(0.05, 0.10)


def test_srm_flags_a_52_48_split_at_scale_but_not_a_fair_one():
    assert srm_check([52_000, 48_000])["mismatch"]
    assert not srm_check([50_120, 49_880])["mismatch"]


def test_cuped_keeps_the_effect_and_cuts_variance_when_covariate_is_predictive():
    rng = np.random.default_rng(0)
    n = 20_000
    x = rng.normal(10, 3, n)
    arm = rng.random(n) < 0.5
    y = 0.8 * x + rng.normal(0, 1, n) + 0.5 * arm      # true effect 0.5
    adj, theta = cuped(y, x)
    raw = diff_in_means(y[~arm], y[arm])
    adjusted = diff_in_means(adj[~arm], adj[arm])
    assert abs(theta - 0.8) < 0.05
    assert abs(adjusted.diff - 0.5) < 0.05
    assert (adjusted.ci_high - adjusted.ci_low) < 0.5 * (raw.ci_high - raw.ci_low)


def test_diff_in_means_interval_covers_known_effect():
    rng = np.random.default_rng(1)
    c = rng.random(50_000) < 0.10
    t = rng.random(50_000) < 0.11
    e = diff_in_means(c, t)
    assert e.ci_low < 0.01 < e.ci_high and e.significant


def test_guardrail_passes_a_flat_metric_and_fails_a_clear_drop():
    rng = np.random.default_rng(2)
    c = rng.normal(100, 10, 20_000)
    assert guardrail(c, rng.normal(100, 10, 20_000))["pass"]
    assert not guardrail(c, rng.normal(95, 10, 20_000))["pass"]
