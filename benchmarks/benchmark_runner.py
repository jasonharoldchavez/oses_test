"""Reproducible scenario benchmark with explicitly defined metric units."""
import time
import numpy as np
from streaming_guardian.detectors.framework_core import AdaptiveCUSUMDetector
from benchmarks.metrics import summarize_trials, wilson_interval, classify_first_alarms


def run_statistical_audit(num_trials=1000, stream_length=120, change_point=50, seed=42):
    if isinstance(num_trials, bool) or not isinstance(num_trials, int) or num_trials < 1:
        raise ValueError("num_trials must be a positive integer.")
    if isinstance(stream_length, bool) or not isinstance(stream_length, int) or stream_length < 3:
        raise ValueError("stream_length must be an integer >= 3.")
    if isinstance(change_point, bool) or not isinstance(change_point, int) or not 2 <= change_point < stream_length:
        raise ValueError("change_point must be an integer in [2, stream_length).")

    regimes = [
        {"name": "Standard Creeping Drift", "noise_scale": 0.4, "drift_slope": 0.10},
        {"name": "High Ambient Noise / Slow Leak", "noise_scale": 0.8, "drift_slope": 0.05},
        {"name": "Extreme Volatility / Sudden Jump", "noise_scale": 1.2, "drift_slope": 2.0},
    ]
    rng = np.random.default_rng(seed)
    print("ADVERSARIAL STATISTICAL AUDIT")
    print(f"seed={seed}, trials={num_trials}, stream_length={stream_length}, change_point={change_point}")
    print("No-change false-alarm probability is estimated from independent baseline-only trials.")

    for regime in regimes:
        false_alarm_counts = []
        first_alarm_indices = []
        no_change_alarm_counts = []
        start_time = time.perf_counter()

        # Trials containing a known change.
        for _ in range(num_trials):
            noise = rng.normal(loc=10.0, scale=regime["noise_scale"], size=stream_length)
            drift = np.zeros(stream_length)
            for idx in range(change_point, stream_length):
                offset = idx - change_point
                drift[idx] = regime["drift_slope"] if regime["drift_slope"] > 1.0 else offset * regime["drift_slope"]
            stream = noise + drift
            detector = AdaptiveCUSUMDetector(burn_in=min(30, change_point))
            pre_alarm_count = 0
            first_alarm_index = None

            for idx, value in enumerate(stream):
                alarm, _ = detector.update(float(value))
                if alarm:
                    if first_alarm_index is None:
                        first_alarm_index = idx
                    if idx < change_point:
                        pre_alarm_count += 1

            false_alarm_counts.append(pre_alarm_count)
            first_alarm_indices.append(first_alarm_index)

        # Independent baseline-only trials estimate false-alarm probability
        # over the full horizon, without mixing false alarms with detections.
        for _ in range(num_trials):
            baseline = rng.normal(loc=10.0, scale=regime["noise_scale"], size=stream_length)
            detector = AdaptiveCUSUMDetector(burn_in=min(30, change_point))
            alarm_samples = 0
            for value in baseline:
                alarm, _ = detector.update(float(value))
                alarm_samples += int(alarm)
            no_change_alarm_counts.append(alarm_samples)

        elapsed_ms = (time.perf_counter() - start_time) * 1000
        alarm_classification = classify_first_alarms(first_alarm_indices, change_point, stream_length)
        delays = alarm_classification["detection_delays"]
        metrics = summarize_trials(num_trials, change_point, false_alarm_counts, delays)
        no_change_alarm_trials = sum(count > 0 for count in no_change_alarm_counts)
        no_change_alarm_samples = sum(no_change_alarm_counts)
        no_change_probability = no_change_alarm_trials / num_trials
        no_change_ci = wilson_interval(no_change_alarm_trials, num_trials)
        pre_change_ci = wilson_interval(metrics["false_alarm_trials"], num_trials)
        detection_ci = wilson_interval(metrics["detected_trials"], num_trials)

        print(f"
Scenario: {regime['name']}")
        print(f"  Pre-change alarm-trial probability:        {metrics['false_alarm_trial_probability']:.4f} ({metrics['false_alarm_trials']}/{num_trials}); Wilson 95% CI [{pre_change_ci[0]:.4f}, {pre_change_ci[1]:.4f}]")
        print(f"  Pre-change alarm-sample rate:              {metrics['false_alarm_sample_rate']:.6f} ({metrics['false_alarm_samples']}/{metrics['pre_change_samples']})")
        print(f"  Post-change detection probability:         {metrics['detection_probability']:.4f} ({metrics['detected_trials']}/{num_trials}); Wilson 95% CI [{detection_ci[0]:.4f}, {detection_ci[1]:.4f}]")
        print(f"  No-change false-alarm probability:         {no_change_probability:.4f} ({no_change_alarm_trials}/{num_trials}); Wilson 95% CI [{no_change_ci[0]:.4f}, {no_change_ci[1]:.4f}]")
        print(f"  No-change alarm-sample rate:               {no_change_alarm_samples / (num_trials * stream_length):.6f} ({no_change_alarm_samples}/{num_trials * stream_length})")
        print(f"  Mean delay, conditional on detection:      {metrics['mean_delay_given_detection']:.2f} samples")
        print(f"  Runtime:                                   {elapsed_ms:.2f} ms")
    print("
Empirical results only; they are not universal performance guarantees.")


if __name__ == "__main__":
    run_statistical_audit()
