import time
import sys
import math
from numbers import Integral, Real
import numpy as np
from abc import ABC, abstractmethod

class AbstractMeasurementLayer(ABC):
    @abstractmethod
    def fetch_raw_data(self):
        raise NotImplementedError

class AbstractFeatureLayer(ABC):
    @abstractmethod
    def transform(self, raw_telemetry):
        raise NotImplementedError

class AbstractDecisionLayer(ABC):
    @abstractmethod
    def update(self, isolated_signal):
        raise NotImplementedError

class PassThroughFeature(AbstractFeatureLayer):
    def transform(self, raw_telemetry):
        return raw_telemetry

class AdaptiveCUSUMDetector(AbstractDecisionLayer):
    """Adaptive one-sided CUSUM-style detector for finite scalar samples.

    This heuristic detector is not a calibrated probabilistic model. Its
    adaptive floor and threshold require scenario-specific evaluation before
    any false-alarm or detection guarantee is claimed.
    """
    def __init__(self, burn_in=30):
        if isinstance(burn_in, bool) or not isinstance(burn_in, Integral) or burn_in < 2:
            raise ValueError("burn_in must be an integer >= 2.")
        self.burn_in = int(burn_in)
        self.history = []
        self.tracker = 0.0
        self.floor = 0.0
        self.h = 4.605
        self.step = 0

    @staticmethod
    def _validate_signal(signal):
        if isinstance(signal, (bool, np.bool_)) or not isinstance(signal, Real):
            raise ValueError("signal must be a finite real scalar.")
        value = float(signal)
        if not math.isfinite(value):
            raise ValueError("signal must be a finite real scalar.")
        return value

    def update(self, signal):
        # Validate before mutating detector state.
        signal = self._validate_signal(signal)
        self.step += 1
        self.history.append(signal)
        if self.step <= self.burn_in:
            if self.step == self.burn_in:
                self.floor = float(np.mean(self.history) + 0.5 * np.std(self.history))
            return False, 0.0

        if self.tracker == 0.0:
            recent_window = self.history[-15:]
            self.floor = 0.95 * self.floor + 0.05 * (np.mean(recent_window) + 0.5 * np.std(recent_window))

        self.tracker = max(0.0, self.tracker + signal - self.floor)
        return self.tracker > self.h, self.tracker

if __name__ == "__main__":
    from .models import CUSUMDecisionEngine, SimpleMovingAverageDetector, EWMADetector
    from scenarios.generators import DynamicSensor

    print("=" * 85)
    print("      RUNNING UNIFIED SELF-CORRECTING HIGH-FIDELITY BENCHMARK")
    print("=" * 85)
    scenarios = [
        {"name": "Standard Creeping Drift (Baseline)", "scale": 0.4, "drift": 0.10, "type": "gradual"},
        {"name": "High Noise / Slow Leak", "scale": 0.8, "drift": 0.05, "type": "gradual"},
        {"name": "Extreme Volatility / Sudden Shift", "scale": 1.2, "drift": 2.0, "type": "step"}
    ]
    num_trials = 1000
    for sc in scenarios:
        print(f"\n>>> Scenario: {sc['name']}")
        engine_keys = ["cusum", "adaptive_cusum", "sma", "ewma"]
        results = {k: {"delays": [], "false_alarm_trials": 0, "false_alarm_samples": 0, "detections": 0} for k in engine_keys}
        change_step = 50
        stream_length = 120
        for _ in range(num_trials):
            sensor = DynamicSensor(scale=sc["scale"], drift=sc["drift"], drift_type=sc["type"])
            engines = {
                "cusum": CUSUMDecisionEngine(threshold_h=4.605, noise_floor=10.8),
                "adaptive_cusum": AdaptiveCUSUMDetector(burn_in=30),
                "sma": SimpleMovingAverageDetector(window_size=15, threshold_multiplier=2.5),
                "ewma": EWMADetector(alpha=0.15, threshold_multiplier=2.5)
            }
            first_alarm = {key: None for key in engine_keys}
            pre_change_alarm_count = {key: 0 for key in engine_keys}
            for step in range(stream_length):
                signal = sensor.fetch_raw_data()
                for name, engine in engines.items():
                    is_alarm, _ = engine.update(signal)
                    if is_alarm:
                        if first_alarm[name] is None:
                            first_alarm[name] = step
                        if step < change_step:
                            pre_change_alarm_count[name] += 1
            for name in engine_keys:
                results[name]["false_alarm_samples"] += pre_change_alarm_count[name]
                if pre_change_alarm_count[name] > 0:
                    results[name]["false_alarm_trials"] += 1
                alarm_step = first_alarm[name]
                if alarm_step is not None and alarm_step >= change_step:
                    results[name]["detections"] += 1
                    results[name]["delays"].append(alarm_step - change_step)

        for name in engine_keys:
            delays = results[name]["delays"]
            avg_delay = float(np.mean(delays)) if delays else float("nan")
            detection_probability = results[name]["detections"] / num_trials
            pre_trial_probability = results[name]["false_alarm_trials"] / num_trials
            pre_sample_rate = results[name]["false_alarm_samples"] / (num_trials * change_step)
            display_name = {"cusum": "SEQUENTIAL CUSUM", "adaptive_cusum": "SELF-CORRECTING CUSUM"}.get(name, name.upper())
            print(
                f"[{display_name}] pre-change alarm-trial probability={pre_trial_probability:.4f}; "
                f"pre-change alarm-sample rate={pre_sample_rate:.4f}; "
                f"post-change detection probability={detection_probability:.4f}; "
                f"conditional delay={avg_delay:.2f} samples"
            )
    print("These are empirical scenario results, not universal performance guarantees.")
