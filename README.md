# Streaming Guardian

Streaming Guardian is a Python toolkit for experimenting with sequential
change detection and telemetry monitoring. Its adaptive CUSUM-style detector
is a heuristic; it is not a calibrated probabilistic model, and its thresholds
must be evaluated against the intended data and operating conditions.

## Current scope

- `streaming_guardian/`: detector implementation.
- `benchmarks/benchmark_runner.py`: reproducible, synthetic scenario audit
  for the adaptive detector, including independent no-change trials.
- `benchmarks/metrics.py`: metric summaries and Wilson score intervals for
  trial-level binomial proportions.
- `tests/`: regression tests for input validation and benchmark metrics.

## Install for development

From the repository root:

```bash
python -m pip install -e .
```

The core runtime dependency is NumPy. The GitHub Actions workflow installs
pytest for the test suite.

## Run tests

```bash
python -m pytest -q
```

The repository's CI currently runs the detector, benchmark-metric,
certificate, and benchmark-configuration regression tests on Python 3.10,
3.11, 3.12, and 3.13. A passing test suite establishes only the tested
software behaviors; it does not establish operational performance.

## Run the synthetic benchmark

```bash
python -m benchmarks.benchmark_runner
```

The default run uses 1,000 trials per scenario, a stream length of 120, and a
change point at sample 50. It reports:

- pre-change false-alarm trial probability;
- pre-change false-alarm sample rate;
- post-change detection probability;
- no-change false-alarm probability from separate baseline-only trials;
- no-change alarm-sample rate;
- mean detection delay conditional on detection; and
- runtime.

The benchmark uses seeded synthetic data and reports Wilson 95% confidence
intervals for selected trial-level probabilities. These intervals describe
sampling uncertainty under the benchmark's assumptions; they do not establish
performance on unseen real-world streams. The no-change false-alarm estimate
also depends on the chosen stream length. Results must be reported with the
scenario parameters, detector configuration, seed, and source revision.

The current default statistical runner evaluates the adaptive detector only.
A separate comparison loop exists in `streaming_guardian/detectors/framework_core.py`,
but its results should not be presented as a validated head-to-head benchmark
until its scenario generation, alarm handling, and metrics are independently
reviewed and covered by tests.

## Example

```python
from streaming_guardian import AdaptiveCUSUMDetector

detector = AdaptiveCUSUMDetector(burn_in=30)

for sample in data_stream:
    alarm, score = detector.update(sample)
    if alarm:
        print(f"Detector alarm; internal score={score:.3f}")
```

An alarm means the detector's configured rule fired. It is not, by itself,
proof that the data point is erroneous or that a real-world fault occurred.

## Evidence and release status

The checked-in tests and synthetic benchmark are engineering tools, not a
production-readiness certificate. Before deployment, evaluate the detector on
representative historical and live-like data, define acceptable false-alarm
and missed-detection costs, measure resource use, and establish monitoring and
rollback procedures.

## License review required

The repository's license references currently need reconciliation before a
release or commercial distribution decision:

- `pyproject.toml` points to `LICENSE.txt`.
- The README previously linked `LICENSE` and `LICENSE-COMMERCIAL.txt`, but
  those paths are not present on the default branch.
- `LICENSE.txt` contains Apache License 2.0 text followed by additional
  commercial-license terms.

This README does not resolve the legal effect of that combined file. Confirm
the intended licensing model and make the license files, package metadata,
README, and distribution artifacts consistent before publishing a release.
