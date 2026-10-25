"""Statistics for online experiments.

- sample_size_per_arm : users needed per arm to detect a relative lift in a conversion rate
- srm_check           : sample-ratio mismatch (chi-square goodness of fit on assignment counts)
- cuped               : variance reduction with a pre-period covariate (Deng et al., 2013)
- diff_in_means       : difference with a Welch 95% interval and p-value (works for 0/1 and continuous)
- guardrail           : non-inferiority check: is the worst plausible change within the allowed margin?
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy import stats


def sample_size_per_arm(baseline_rate: float, relative_mde: float, alpha: float = 0.05, power: float = 0.8) -> int:
    """Users per arm for a two-sided two-proportion z-test detecting baseline x (1 + relative_mde)."""
    p1, p2 = baseline_rate, baseline_rate * (1 + relative_mde)
    z_a, z_b = stats.norm.ppf(1 - alpha / 2), stats.norm.ppf(power)
    p_bar = (p1 + p2) / 2
    n = ((z_a * np.sqrt(2 * p_bar * (1 - p_bar)) + z_b * np.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2) / (p2 - p1) ** 2
    return int(np.ceil(n))


def srm_check(observed: list[int], expected_share: list[float] | None = None, threshold: float = 0.001) -> dict:
    """Chi-square test that assignment counts match the intended split. p < threshold means stop and investigate."""
    observed = np.asarray(observed, dtype=float)
    share = np.full(len(observed), 1 / len(observed)) if expected_share is None else np.asarray(expected_share)
    chi2, p = stats.chisquare(observed, f_exp=observed.sum() * share)
    return {"chi2": float(chi2), "p_value": float(p), "mismatch": bool(p < threshold)}


def cuped(y: np.ndarray, x: np.ndarray) -> tuple[np.ndarray, float]:
    """Adjusted outcome y - theta * (x - mean(x)), theta = cov(y, x) / var(x), pooled across arms.
    Unbiased for the treatment effect (x is measured before assignment); variance shrinks by corr(y, x)^2."""
    y, x = np.asarray(y, float), np.asarray(x, float)
    vx = x.var()
    theta = 0.0 if vx == 0 else float(np.cov(y, x, bias=True)[0, 1] / vx)
    return y - theta * (x - x.mean()), theta


@dataclass
class Effect:
    control_mean: float
    treatment_mean: float
    diff: float
    ci_low: float
    ci_high: float
    p_value: float
    relative_lift: float

    @property
    def significant(self) -> bool:
        return self.p_value < 0.05


def diff_in_means(control: np.ndarray, treatment: np.ndarray, alpha: float = 0.05) -> Effect:
    """Treatment minus control with a Welch interval (normal approximation; fine at experiment sample sizes)."""
    c, t = np.asarray(control, float), np.asarray(treatment, float)
    diff = t.mean() - c.mean()
    se = np.sqrt(t.var(ddof=1) / len(t) + c.var(ddof=1) / len(c))
    z = stats.norm.ppf(1 - alpha / 2)
    p = 2 * (1 - stats.norm.cdf(abs(diff) / se)) if se > 0 else 1.0
    rel = diff / c.mean() if c.mean() else float("nan")
    return Effect(float(c.mean()), float(t.mean()), float(diff), float(diff - z * se), float(diff + z * se), float(p), float(rel))


def guardrail(control: np.ndarray, treatment: np.ndarray, max_relative_drop: float = 0.02,
              higher_is_better: bool = True) -> dict:
    """Pass if the worst end of the 95% interval is no worse than `max_relative_drop` of the control mean."""
    e = diff_in_means(control, treatment)
    margin = max_relative_drop * abs(e.control_mean)
    worst = e.ci_low if higher_is_better else -e.ci_high
    return {"diff": e.diff, "worst_plausible": worst, "allowed": -margin, "pass": bool(worst >= -margin)}
