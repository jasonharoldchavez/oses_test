# Streaming Guardian (Developer SDK)

Streaming Guardian is a lightweight sequential data drift testing module and streaming anomaly detection SDK. It provides an installable package layout alongside independent benchmarking harnesses to evaluate sequential metrics under controlled statistical profiles.

## 🛠️ Project Architecture
* streaming_guardian/: Core distribution library containing the self-correcting detection logic.
* benchmarks/: Separate evaluation scripts to stress-test detectors against synthetic baselines.
* tests/: Functional validation testing suites.

---

## 🚀 Quickstart Installation
Install the package locally in editable development mode from the project root:
$ pip install -e .

## 📊 Empirical Evaluation Metrics
### 1. Multi-Regime Adversarial Audit (3,000 Total Trials)
* Standard Creeping Drift: 10.86 Packet Latency | 0.0000% False Positive Rate
* High Noise / Slow Leak: 17.44 Packet Latency | 0.1120% False Positive Rate
* Extreme Volatility / Jump: 2.45 Packet Latency | 0.8160% False Positive Rate

### 2. The Baseline Comparison War (1,000 Total Trials)
* Adaptive CUSUM (Ours): 0.0000% FPR | 100.00% Detection Rate | 10.91 Mean Delay
* Static CUSUM Baseline: 3.0160% FPR | 100.00% Detection Rate | 6.85 Mean Delay
* Rolling Z-Score Filter: 1.2800% FPR | 100.00% Detection Rate | 8.40 Mean Delay

## ⚖️ License
This project is licensed under the MIT License.
