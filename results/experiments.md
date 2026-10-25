# Experiment toolkit validated on real visitors

Units: 269,683 visitors active in the last 28 days (bots excluded); baseline conversion 0.78%; mean views 1.71. Correlation with pre-period: conversion 0.06, views 0.58. 500 simulations per row.

## 1. A/A tests (no real effect)

| Metric | False positive rate (target 5%) |
|---|---|
| conversion | 2.8% |
| views | 5.0% |
| views (CUPED) | 6.8% |
| SRM false alarms (threshold p < 0.001) | 0.0% |

## 2. Planted lifts

| Metric | True lift | Mean estimated lift | 95% CI covers truth | Power (raw) | Power (CUPED) | CI width reduction (CUPED) |
|---|---|---|---|---|---|---|
| Conversion | +2% | +2.1% | 97% | 5% | 5% | 0% |
| Conversion | +5% | +4.7% | 93% | 20% | 20% | 0% |
| Conversion | +10% | +10.0% | 96% | 60% | 61% | 0% |
| Views per visitor | +2% | +2.0% | 95% | 24% | 31% | 18% |
| Views per visitor | +5% | +5.0% | 95% | 85% | 96% | 18% |
| Views per visitor | +10% | +10.1% | 96% | 100% | 100% | 18% |

## 3. Sample-ratio mismatch drill

Treatment loses 2% of its units (a logging bug): control 135,121 vs treatment 131,830. SRM p-value 1.9e-10: **flagged**. Guardrail on views with no change applied: fail (worst plausible change -0.064 views vs allowed -0.034).

## 4. Sample size at this conversion rate

| Relative lift to detect | Users per arm needed | Available per arm (28 days) | Feasible |
|---|---|---|---|
| +2% | 5,064,733 | 134,841 | no |
| +5% | 822,295 | 134,841 | no |
| +10% | 210,546 | 134,841 | no |
| +20% | 55,121 | 134,841 | yes |

Run time 82s.
