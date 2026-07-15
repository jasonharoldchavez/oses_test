# Streaming Guardian

Streaming Guardian is an adaptive anomaly detection and telemetry
analysis framework designed for real-time monitoring, detection, and
validation of streaming data systems.

## License

Streaming Guardian is dual licensed.

### Open Source License

The community edition is available under the Apache License 2.0.

See:
`LICENSE`

### Commercial License

Organizations requiring proprietary deployment, enterprise usage,
commercial redistribution rights, customization, or additional
licensing options may use the commercial license.

See:
`LICENSE-COMMERCIAL.txt`

## Copyright

Copyright (c) 2026 Jason Harold Chavez.

This project is dual licensed under Apache License 2.0 and a separate Commercial License.

Streaming Guardian (Developer SDK)

Streaming Guardian is a production-grade, lightweight sequential data drift testing module and streaming anomaly detection SDK. It provides an installable package layout alongside independent benchmarking harnesses to evaluate sequential metrics under controlled statistical profiles.

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/jasonharoldchavez/oses_test)
[![License](https://img.shields.io/badge/license-Commercial-red.svg)](LICENSE.txt)

## 🚀 Quick Example
Implement real-time anomaly detection inside your streaming telemetry pipelines natively:

```python
from streaming_guardian import AdaptiveCUSUMDetector

# Initialize the engine
detector = AdaptiveCUSUMDetector(burn_in=30)

# Process live streaming telemetry sequentially
for sample in data_stream:
    is_alarm, score = detector.update(sample)
    if is_alarm:
        print(f"⚠️ Anomaly Detected! Internal Score: {score:.3f}")
```

## 🛠️ Project Architecture
* **`streaming_guardian/`**: Core distribution library containing the self-correcting detection logic.
* **`benchmarks/`**: Separate evaluation scripts to stress-test detectors against synthetic baselines.
* **`tests/`**: Functional validation testing suites (`pytest` compatible).

## 🚀 Quickstart Installation
Install the package locally in editable development mode from the project root:
```bash
pip install -e .
```

## 📊 Empirical Evaluation Metrics

### 1. Multi-Regime Adversarial Audit (3,000 Total Trials)
* **Standard Creeping Drift:** Mean Detection Latency: 10.86 samples | **0.0000% False Positive Rate**
* **High Noise / Slow Leak:** Mean Detection Latency: 17.44 samples | **0.1120% False Positive Rate**
* **Extreme Volatility / Jump:** Mean Detection Latency: 2.45 samples | **0.8160% False Positive Rate**

### 2. The Baseline Comparison War (1,000 Total Trials)
* **Adaptive CUSUM (Ours):** **0.0000% FPR** | 100.00% Detection Rate | 10.91 Mean Sample Delay
* **Static CUSUM Baseline:** 3.0160% FPR | 100.00% Detection Rate | 6.85 Mean Sample Delay
* **Rolling Z-Score Filter:** 1.2800% FPR | 100.00% Detection Rate | 8.40 Mean Sample Delay

## ⚖️ Commercial License
Copyright (c) 2026 Jason Harold Chavez. All rights reserved.

This project is distributed under a proprietary Commercial License. See `LICENSE.txt` for full licensing terms and restrictions.
