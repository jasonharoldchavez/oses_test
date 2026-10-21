"""Reproducible scenario benchmark with explicitly defined metric units."""
import time
import numpy as np
from streaming_guardian.detectors.framework_core import AdaptiveCUSUMDetector


def run_statistical_audit(num_trials=1000, stream_length=120, change_point=50, seed=42):
    if not isinstance(num_trials, int) or num_trials < 1:
        raise ValueError("num_trials must be a positive integer.")
    if not isinstance(stream_length, int) or stream_length < 2:
        raise ValueError("stream_length must be an integer >= 2.")
    if not isinstance(change_point, int) or not 1 <= change_point < stream_length:
        raise ValueError("change_point must lie inside the stream.")

    regimes = [
        {"name": "Standard Creeping Drift", "noise_scale": 0.4, "drift_slope": 0.10},
        {"name": "High Ambient Noise / Slow Leak", "noise_scale": 0.8, "drift_slope": 0.05},
        {"name": "Extreme Volatility / Sudden Jump", "noise_scale": 1.2, "drift_slope": 2.0},
    ]
    rng = np.random.default_rng(seed)
    print("ADVERSARIAL STATISTICAL AUDIT")
    print(f"seed={seed}, trials={num_trials}, stream_length={stream_length}, change_point={change_point}")
    print("False-alarm trial probability and alarm-sample rate are reported separately.")

    for regime in regimes:
        false_alarm_trials = 0
        false_alarm_samples = 0
        detection_trials = 0
        delays = []
        start_time = time.perf_counter()

        for _ in range(num_trials):
            noise = rng.normal(loc=10.0, scale=regime["noise_scale"], size=stream_length)
            drift = np.zeros(stream_length)
            for idx in range(change_point, stream_length):
                offset = idx - change_point
                drift[idx] = regime["drift_slope"] if regime["drift_slope"] > 1.0 else offset * regime["drift_slope"]
            stream = noise + drift
            detector = AdaptiveCUSUMDetector(burn_in=min(30, max(2, change_point)))
            pre_alarm_count = 0
            first_post_alarm = None

            for idx, value in enumerate(stream):
                alarm, _ = detector.update(float(value))
                if alarm and idx < change_point:
                    pre_alarm_count += 1
                elif alarm and idx >= change_point and first_post_alarm is None:
                    first_post_alarm = idx

            if pre_alarm_count:
                false_alarm_trials += 1
                false_alarm_samples += pre_alarm_count
            if first_post_alarm is not None:
                detection_trials += 1
                delays.append(first_post_alarm - change_point)

        elapsed_ms = (time.perf_counter() - start_time) * 1000
        pre_samples = num_trials * change_point
        trial_probability = false_alarm_trials / num_trials
        sample_rate = false_alarm_samples / pre_samples
        detection_probability = detection_trials / num_trials
        mean_delay = float(np.mean(delays)) if delays else float("nan")
        print(f"\nScenario: {regime['name']}")
        print(f"  Pre-change false-alarm trial probability: {trial_probability:.4f} ({false_alarm_trials}/{num_trials})")
        print(f"  Pre-change false-alarm sample rate:       {sample_rate:.6f} ({false_alarm_samples}/{pre_samples})")
        print(f"  Post-change detection probability:        {detection_probability:.4f} ({detection_trials}/{num_trials})")
        print(f"  Mean delay, conditional on detection:     {mean_delay:.2f} samples")
        print(f"  Runtime:                                  {elapsed_ms:.2f} ms")
    print("\nEmpirical results only; they are not universal performance guarantees.")


if __name__ == "__main__":
    run_statistical_audit()
