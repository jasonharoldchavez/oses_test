import time
import sys
import numpy as np
from abc import ABC, abstractmethod

# =====================================================================
# 1. CORE FRAMEWORK INTERFACES (Stable Blueprints)
# =====================================================================

class AbstractMeasurementLayer(ABC):
    @abstractmethod
    def fetch_raw_data(self):
        pass

class AbstractFeatureLayer(ABC):
    @abstractmethod
    def transform(self, raw_telemetry):
        pass

class AbstractDecisionLayer(ABC):
    @abstractmethod
    def update(self, isolated_signal):
        pass

class PassThroughFeature(AbstractFeatureLayer):
    def transform(self, raw_telemetry):
        return raw_telemetry

# =====================================================================
# 2. THE SELF-CORRECTING ADAPTIVE DETECTION ENGINE
# =====================================================================

class AdaptiveCUSUMDetector(AbstractDecisionLayer):
    """
    A self-correcting CUSUM engine that automatically updates its own 
    noise floor based on rolling background statistics, eliminating the 
    need for pre-calibrated baseline knowledge.
    """
    def __init__(self, burn_in=30):
        self.burn_in = burn_in
        self.history = []
        self.tracker = 0.0
        self.floor = 0.0
        self.h = 4.605 
        self.step = 0

    def update(self, signal):
        self.step += 1
        self.history.append(signal)
        
        # Burn-in phase: Collect baseline data to self-calibrate
        if self.step <= self.burn_in:
            if self.step == self.burn_in:
                self.floor = np.mean(self.history) + (0.5 * np.std(self.history))
            return False, 0.0
        
        # Self-correction: Slowly adapt the floor if no anomaly is accumulating
        if self.tracker == 0.0:
            recent_window = self.history[-15:]
            self.floor = (0.95 * self.floor) + (0.05 * (np.mean(recent_window) + 0.5 * np.std(recent_window)))

        # Run sequential accumulation with the self-corrected baseline
        increment = signal - self.floor
        self.tracker = max(0.0, self.tracker + increment)
        
        return self.tracker > self.h, self.tracker

# =====================================================================
# 3. EVALUATION TEST ENGINE MAIN LOOP (HIGH FIDELITY + ADAPTIVE)
# =====================================================================
if __name__ == "__main__":
    from detectors.models import CUSUMDecisionEngine, SimpleMovingAverageDetector, EWMADetector
    from scenarios.generators import DynamicSensor

    print("=" * 85)
    print("      RUNNING UNIFIED SELF-CORRECTING HIGH-FIDELITY BENCHMARK (1,000 TRIALS)")
    print("=" * 85)

    # The comprehensive benchmarking gauntlet
    scenarios = [
        {"name": "Standard Creeping Drift (Baseline)", "scale": 0.4, "drift": 0.10, "type": "gradual"},
        {"name": "High Noise / Slow Leak", "scale": 0.8, "drift": 0.05, "type": "gradual"},
        {"name": "Extreme Volatility / Sudden Shift", "scale": 1.2, "drift": 2.0, "type": "step"}
    ]

    num_trials = 1000  # Massive statistical population for absolute certainty

    for sc in scenarios:
        print(f"\n>>> Scenario: {sc['name']}")
        print(f"    [Stress Level -> Volatility: {sc['scale']}, Drift Speed: {sc['drift']}]")
        print("-" * 85)

        # Track results for all four competitors
        engine_keys = ["cusum", "adaptive_cusum", "sma", "ewma"]
        results = {k: {"delays": [], "fa_count": 0, "detections": 0} for k in engine_keys}

        for t in range(num_trials):
            sensor = DynamicSensor(scale=sc["scale"], drift=sc["drift"], drift_type=sc["type"])
            feature = PassThroughFeature()

            # Initialize detectors side-by-side
            engines = {
                "cusum": CUSUMDecisionEngine(threshold_h=4.605, noise_floor=10.8),
                "adaptive_cusum": AdaptiveCUSUMDetector(burn_in=30),
                "sma": SimpleMovingAverageDetector(window_size=15, threshold_multiplier=2.5),
                "ewma": EWMADetector(alpha=0.15, threshold_multiplier=2.5)
            }

            alarm_steps = {k: -1 for k in engine_keys}
            fa_counts = {k: 0 for k in engine_keys}
            ground_truth_step = 50

            for step in range(1, 120):
                raw_signal = sensor.fetch_raw_data()
                signal = feature.transform(raw_signal)

                for name, engine in engines.items():
                    is_alarm, _ = engine.update(signal)
                    if is_alarm and alarm_steps[name] == -1:
                        if step < ground_truth_step:
                            fa_counts[name] += 1
                        else:
                            alarm_steps[name] = step

            for name in engine_keys:
                if alarm_steps[name] != -1:
                    results[name]["detections"] += 1
                    results[name]["delays"].append(alarm_steps[name] - ground_truth_step)
                results[name]["fa_count"] += fa_counts[name]

        # Calculate and print rigorous 95% Confidence Intervals
        for name in engine_keys:
            delays = results[name]["delays"]
            avg_delay = np.mean(delays) if delays else float('nan')
            std_delay = np.std(delays) if len(delays) > 1 else 0.0
            margin_of_error = 1.96 * (std_delay / np.sqrt(len(delays))) if delays else 0.0
            
            recall = (results[name]["detections"] / num_trials) * 100.0
            total_predicted = results[name]["detections"] + results[name]["fa_count"]
            precision = (results[name]["detections"] / total_predicted * 100.0) if total_predicted > 0 else 0.0
            f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

            if name == "cusum":
                display_name = "SEQUENTIAL CUSUM"
            elif name == "adaptive_cusum":
                display_name = "SELF-CORRECTING CUSUM"
            else:
                display_name = name.upper()

            print(f"  • [{display_name:<21}] F1: {f1:>5.1f}% | Recall: {recall:>5.1f}% | Precision: {precision:>5.1f}% | Delay: {avg_delay:.2f} ± {margin_of_error:.2f} steps")
    print("=" * 85)
