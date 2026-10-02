from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class CompareResult:
    value: float
    tier: Optional[str]
    z: Optional[float]
    percentile_approx: Optional[float]

def _approx_percentile_from_z(z: float) -> float:
    # Fast approximation (error acceptable for UI). No SciPy needed.
    # Abramowitz & Stegun-ish approximation for normal CDF.
    import math
    t = 1.0 / (1.0 + 0.2316419 * abs(z))
    d = 0.3989423 * math.exp(-z*z/2)
    prob = d*t*(0.3193815 + t*(-0.3565638 + t*(1.781478 + t*(-1.821256 + t*1.330274))))
    cdf = 1 - prob
    if z < 0:
        cdf = 1 - cdf
    return float(cdf * 100.0)

def compare_to_baseline(value: float, baseline_mean: float, baseline_std: float, tier: str) -> CompareResult:
    if baseline_std <= 1e-9:
        return CompareResult(value=value, tier=tier, z=None, percentile_approx=None)
    z = (value - baseline_mean) / baseline_std
    pct = _approx_percentile_from_z(z)
    return CompareResult(value=value, tier=tier, z=float(z), percentile_approx=float(pct))
