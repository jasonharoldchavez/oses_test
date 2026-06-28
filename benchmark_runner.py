import numpy as np
import time
from framework_core import AdaptiveCUSUMDetector

def run_statistical_audit():
    print("=====================================================================")
    print("     ADVERSARIAL STATISTICAL AUDIT: MULTI-REGIME EVALUATION          ")
    print("=====================================================================")

    # Define 3 distinct environmental regimes (Adversarial Stress Testing)
    regimes = [
        {"name": "Standard Creeping Drift", "noise_scale": 0.4, "drift_slope": 0.10},
        {"name": "High Ambient Noise / Slow Leak", "noise_scale": 0.8, "drift_slope": 0.05},
        {"name": "Extreme Volatility / Sudden Jump", "noise_scale": 1.2, "drift_slope": 2.0}
    ]

    num_trials = 1000  # Large population sample size
    stream_length = 120
    change_point = 50   # Ground truth intervention boundary

    np.random.seed(42)  # For global envelope reproducibility

    for regime in regimes:
        print(f"\n📈 Testing Regime: {regime['name'].upper()}")
        print(f"   [Parameters -> Noise Sigma: {regime['noise_scale']}, Drift Slope: {regime['drift_slope']}]")
        print("-" * 69)

        delays = []
        false_alarms = 0
        total_pre_change_packets = change_point * num_trials
        
        start_time = time.perf_counter()

        for trial in range(num_trials):
            # Re-initialize clean detector per trial (Zero memory leakage)
            detector = AdaptiveCUSUMDetector(burn_in=30)
            
            # Generate stream dynamically based on regime definitions
            noise = np.random.normal(loc=10.0, scale=regime['noise_scale'], size=stream_length)
            drift = np.zeros(stream_length)
            
            # Inject anomaly past the horizon
            for i in range(change_point, stream_length):
                if regime['drift_slope'] > 1.0: # Step change
                    drift[i] = regime['drift_slope']
                else: # Gradual drift
                    drift[i] = (i - change_point) * regime['drift_slope']
            
            stream = noise + drift
            alarm_triggered = False

            for idx, val in enumerate(stream):
                is_alarm, tracker = detector.update(val)
                
                if is_alarm:
                    if idx < change_point:
                        false_alarms += 1
                    elif not alarm_triggered:
                        delays.append(idx - change_point)
                        alarm_triggered = True
                        # We don't break, allowing system to continue processing

        elapsed_ms = (time.perf_counter() - start_time) * 1000
        
        # Calculate true empirical distributions
        empirical_fpr = (false_alarms / total_pre_change_packets) * 100
        mean_delay = np.mean(delays) if delays else float('nan')
        std_delay = np.std(delays) if delays else float('nan')
        detection_rate = (len(delays) / num_trials) * 100

        print(f"  • Empirical False Positive Rate (FPR) : {empirical_fpr:.4f}%")
        print(f"  • True Positive Detection Rate        : {detection_rate:.2f}%")
        print(rf"  • Mean Detection Latency ($\mu_\Delta$)      : {mean_delay:.2f} packets")
        print(rf"  • Latency Variance ($\sigma_\Delta$)         : {std_delay:.2f} packets")
        print(f"  • Compute Footprint (1k Trials)       : {elapsed_ms:.2f} ms")

    print("\n✅ Multi-regime audit complete. Empirical distributions locked.")

if __name__ == "__main__":
    run_statistical_audit()
