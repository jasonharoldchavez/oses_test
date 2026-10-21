"""Generate an explicitly scoped empirical behavior report, not a guarantee."""
import datetime
import math
import subprocess
import sys
import numpy as np
from streaming_guardian import AdaptiveCUSUMDetector


def get_git_commit():
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], stderr=subprocess.DEVNULL
        ).decode("utf-8").strip()
    except Exception:
        return "unavailable"


def generate_certificate():
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    rng = np.random.default_rng(42)

    detector_drift = AdaptiveCUSUMDetector(burn_in=30)
    drift_lag = -1
    for i in range(100):
        value = 10.0 + rng.normal(0, 0.2) + max(0, i - 30) * 0.05
        alarm, _ = detector_drift.update(float(value))
        if alarm and drift_lag == -1:
            drift_lag = i - 30
            break

    detector_noise = AdaptiveCUSUMDetector(burn_in=30)
    false_alarm_samples = 0
    total_noise_samples = 100
    for _ in range(total_noise_samples):
        alarm, _ = detector_noise.update(float(10.0 + rng.normal(0, 2.5)))
        false_alarm_samples += int(alarm)

    detector_shock = AdaptiveCUSUMDetector(burn_in=30)
    shock_lag = -1
    for i in range(50):
        value = 10.0 + rng.normal(0, 0.2) if i < 35 else 25.0
        alarm, _ = detector_shock.update(float(value))
        if i >= 35 and alarm and shock_lag == -1:
            shock_lag = i - 35

    invalid_values = [None, "CORRUPT_SIGNAL", float("nan"), float("inf"), True]
    rejected = 0
    validation_errors = []
    for bad_value in invalid_values:
        candidate = AdaptiveCUSUMDetector(burn_in=10)
        before = (candidate.step, len(candidate.history), candidate.tracker, candidate.floor)
        try:
            candidate.update(bad_value)
            validation_errors.append(f"{type(bad_value).__name__} was accepted")
        except (ValueError, TypeError):
            rejected += 1
        after = (candidate.step, len(candidate.history), candidate.tracker, candidate.floor)
        if before != after:
            validation_errors.append(f"state mutated for {type(bad_value).__name__}")

    malformed_status = "PASSED" if rejected == len(invalid_values) and not validation_errors else "FAILED"
    rng_repeat = np.random.default_rng(42).normal(size=8)
    rng_repeat_2 = np.random.default_rng(42).normal(size=8)
    reproducibility_status = "PASSED" if np.array_equal(rng_repeat, rng_repeat_2) else "FAILED"

    report = f"""======================================================================
STREAMING GUARDIAN - EMPIRICAL BEHAVIOR REPORT
======================================================================
Generated At: {timestamp}
Package Name: streaming_guardian
Git Commit Reference: {get_git_commit()}
Python Version: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}
Random Generator: numpy.default_rng(42)

SCOPED OBSERVATIONS (single deterministic smoke scenarios; not guarantees)
----------------------------------------------------------------------
Creeping-drift first alarm lag: {drift_lag} samples (-1 means no alarm)
Noise scenario alarm-sample count: {false_alarm_samples}/{total_noise_samples}
Sudden-shock first alarm lag: {shock_lag} samples (-1 means no alarm)
Malformed-input rejection: {malformed_status} ({rejected}/{len(invalid_values)} rejected)
Seeded generator reproducibility smoke check: {reproducibility_status}

Malformed-input test errors:
{chr(10).join(validation_errors) if validation_errors else "None"}

LIMITATIONS
----------------------------------------------------------------------
These smoke scenarios do not establish a calibrated false-alarm probability,
general detection guarantee, or performance across all noise regimes. The
noise count above is a sample count from one stream, not a trial-level FPR.
Run benchmarks/benchmark_runner.py for separately reported empirical
pre-change trial probability, pre-change sample rate, detection probability,
and conditional detection delay. Results depend on scenario and parameters.
======================================================================
"""
    with open("MODEL_BEHAVIOR_CERTIFICATE.txt", "w", encoding="utf-8") as handle:
        handle.write(report)
    if malformed_status != "PASSED" or reproducibility_status != "PASSED":
        raise SystemExit("Behavior report checks failed; inspect the generated report.")
    print("Empirical behavior report generated; it does not certify universal performance.")


if __name__ == "__main__":
    generate_certificate()
