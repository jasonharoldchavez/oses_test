import numpy as np
import time
from streaming_guardian.detectors.framework_core import AdaptiveCUSUMDetector

# --- Baseline 1: Standard Static CUSUM (Requires a pre-calibrated mean) ---
class StaticCUSUMDetector:
    def __init__(self, target_mean=10.0, threshold_h=4.605):
        self.target_mean = target_mean
        self.h = threshold_h
        self.tracker = 0.0

    def update(self, signal):
        # Static baseline subtraction
        increment = signal - self.target_mean
        self.tracker = max(0.0, self.tracker + increment)
        return self.tracker > self.h, self.tracker

# --- Baseline 2: Simple Moving Average Z-Score Detector ---
class RollingZScoreDetector:
    def __init__(self, window_size=15, z_threshold=2.5):
        self.window_size = window_size
        self.z_threshold = z_threshold
        self.history = []

    def update(self, signal):
        self.history.append(signal)
        if len(self.history) < self.window_size:
            return False, 0.0
        
        window = self.history[-self.window_size:]
        mean = np.mean(window[:-1])
        std = np.std(window[:-1]) + 1e-6
        
        z_score = (signal - mean) / std
        return z_score > self.z_threshold, z_score

# --- The Evaluation Gauntlet ---
def execute_baseline_war():
    print("=====================================================================")
    print("                    THE UNIFIED BASELINE WAR                         ")
    print("=====================================================================")

    regimes = [
        {"name": "Standard Creeping Drift", "noise_scale": 0.4, "drift_slope": 0.10},
        {"name": "High Ambient Noise / Slow Leak", "noise_scale": 0.8, "drift_slope": 0.05}
    ]

    num_trials = 500  # Streamlined for rapid, statistically sound cross-evaluation
    stream_length = 120
    change_point = 50

    np.random.seed(42)

    for regime in regimes:
        print(f"\n⚔️  REGIME: {regime['name'].upper()}")
        print(f"   [Noise: {regime['noise_scale']}, Drift Slope: {regime['drift_slope']}]")
        print("-" * 69)

        # Initialize tracking matrices for all competitors
        competitors = ["Adaptive CUSUM (Ours)", "Static CUSUM Baseline", "Rolling Z-Score"]
        metrics = {c: {"false_alarms": 0, "delays": [], "detections": 0} for c in competitors}
        
        total_pre_change_packets = change_point * num_trials

        for trial in range(num_trials):
            # Generate identical data stream per trial for absolute parity
            noise = np.random.normal(loc=10.0, scale=regime['noise_scale'], size=stream_length)
            drift = np.zeros(stream_length)
            for i in range(change_point, stream_length):
                drift[i] = (i - change_point) * regime['drift_slope']
            stream = noise + drift

            # Instantiate detectors side-by-side
            engines = {
                "Adaptive CUSUM (Ours)": AdaptiveCUSUMDetector(burn_in=30),
                "Static CUSUM Baseline": StaticCUSUMDetector(target_mean=10.0, threshold_h=4.605),
                "Rolling Z-Score": RollingZScoreDetector(window_size=15, z_threshold=2.5)
            }

            triggered = {c: False for c in competitors}

            for idx, val in enumerate(stream):
                for name, engine in engines.items():
                    is_alarm, _ = engine.update(val)
                    
                    if is_alarm:
                        if idx < change_point:
                            metrics[name]["false_alarms"] += 1
                        elif not triggered[name]:
                            metrics[name]["delays"].append(idx - change_point)
                            metrics[name]["detections"] += 1
                            triggered[name] = True

        # Print unified landscape results
        print(f"{'Detector Model':<25} | {'Empirical FPR':<15} | {'Detection Rate':<15} | {'Mean Delay':<12}")
        print("-" * 69)
        for name in competitors:
            fpr = (metrics[name]["false_alarms"] / total_pre_change_packets) * 100
            det_rate = (metrics[name]["detections"] / num_trials) * 100
            mean_delay = np.mean(metrics[name]["delays"]) if metrics[name]["delays"] else float('nan')
            print(f"{name:<25} | {fpr:>13.4f}% | {det_rate:>13.2f}% | {mean_delay:>10.2f}")

if __name__ == "__main__":
    execute_baseline_war()
