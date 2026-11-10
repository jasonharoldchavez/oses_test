"""Fixed-reference, two-sided standardized CUSUM detector.

The reference distribution is estimated only during burn-in and is then
frozen. This avoids allowing a detected shift to move its own baseline.
Thresholds are empirical tuning parameters, not universal error guarantees.
"""
from __future__ import annotations
import math
from numbers import Integral, Real

class StandardizedCUSUMDetector:
    """Two-sided CUSUM over observations standardized by a frozen baseline."""
    def __init__(self, burn_in=30, k=0.5, h=5.0, min_std=1e-9):
        if isinstance(burn_in, bool) or not isinstance(burn_in, Integral) or burn_in < 2:
            raise ValueError("burn_in must be an integer >= 2.")
        self.burn_in = int(burn_in)
        self.k = self._nonnegative(k, "k")
        self.h = self._positive(h, "h")
        self.min_std = self._positive(min_std, "min_std")
        self.reset()

    @staticmethod
    def _finite(value, name):
        if isinstance(value, bool) or not isinstance(value, Real):
            raise ValueError(f"{name} must be a finite real scalar.")
        value = float(value)
        if not math.isfinite(value):
            raise ValueError(f"{name} must be a finite real scalar.")
        return value

    @classmethod
    def _positive(cls, value, name):
        value = cls._finite(value, name)
        if value <= 0:
            raise ValueError(f"{name} must be > 0.")
        return value

    @classmethod
    def _nonnegative(cls, value, name):
        value = cls._finite(value, name)
        if value < 0:
            raise ValueError(f"{name} must be >= 0.")
        return value

    def reset(self):
        """Reset both calibration and accumulated detector state."""
        self.count = 0
        self._mean = 0.0
        self._m2 = 0.0
        self.baseline_mean = None
        self.baseline_std = None
        self.positive_sum = 0.0
        self.negative_sum = 0.0
        self.alarm_count = 0

    @property
    def ready(self):
        return self.baseline_mean is not None

    def update(self, value):
        value = self._finite(value, "value")
        if not self.ready:
            self.count += 1
            delta = value - self._mean
            self._mean += delta / self.count
            self._m2 += delta * (value - self._mean)
            if self.count == self.burn_in:
                variance = self._m2 / (self.count - 1)
                self.baseline_mean = self._mean
                self.baseline_std = max(math.sqrt(max(0.0, variance)), self.min_std)
            return False, 0.0

        z = (value - self.baseline_mean) / self.baseline_std
        self.positive_sum = max(0.0, self.positive_sum + z - self.k)
        self.negative_sum = max(0.0, self.negative_sum - z - self.k)
        score = max(self.positive_sum, self.negative_sum)
        alarm = score >= self.h
        if alarm:
            self.alarm_count += 1
            self.positive_sum = 0.0
            self.negative_sum = 0.0
        return alarm, float(score)