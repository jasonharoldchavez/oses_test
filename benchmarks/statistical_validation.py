import numpy as np
from streaming_guardian.detectors.framework_core import AdaptiveCUSUMDetector
from streaming_guardian.detectors.models import CUSUMDecisionEngine
from scenarios.generators import DynamicSensor

def run_permutation_test(group_a, group_b, num_resamples=5000):
    observed_diff = np.mean(group_b) - np.mean(group_a)
    combined = np.concatenate([group_a, group_b])
    n_a = len(group_a)
    
    count = 0
    for _ in range(num_resamples):
        shuffled = np.random.permutation(combined)
        sim_diff = np.mean(shuffled[n_a:]) - np.mean(shuffled[:n_a])
        if sim_diff >= observed_diff:
            count += 1
            
    return count / num_resamples

if __name__ == "__main__":
    print("=" * 80)
    print("   ADVANCED STATISTICAL SIGNIFICANCE MATRIX (NON-PARAMETRIC RESAMPLING)   ")
    print("=" * 80)
    
    np.random.seed(42)
    num_trials = 250
    ground_truth_step = 50
    
    sensor_args = {"scale": 0.8, "drift": 0.05, "drift_type": "gradual"}
    
    delays_standard = []
    delays_adaptive = []
    
    for _ in range(num_trials):
        sensor = DynamicSensor(**sensor_args)
        std_engine = CUSUMDecisionEngine(threshold_h=4.605, noise_floor=10.8)
        adp_engine = AdaptiveCUSUMDetector(burn_in=30)
        
        alarm_std = -1
        alarm_adp = -1
        
        for step in range(1, 120):
            signal = sensor.fetch_raw_data()
            
            is_alarm_std, _ = std_engine.update(signal)
            if is_alarm_std and alarm_std == -1 and step >= ground_truth_step:
                alarm_std = step
                
            is_alarm_adp, _ = adp_engine.update(signal)
            if is_alarm_adp and alarm_adp == -1 and step >= ground_truth_step:
                alarm_adp = step
        
        if alarm_std != -1: delays_standard.append(alarm_std - ground_truth_step)
        if alarm_adp != -1: delays_adaptive.append(alarm_adp - ground_truth_step)
        
    p_val = run_permutation_test(delays_adaptive, delays_standard)
    
    print(f"Scenario Baseline Evaluation : High Noise / Slow Leak")
    print(f"  • Standard CUSUM Sample Mean Delay   : {np.mean(delays_standard):.2f} steps (N={len(delays_standard)})")
    print(f"  • Adaptive CUSUM Sample Mean Delay   : {np.mean(delays_adaptive):.2f} steps (N={len(delays_adaptive)})")
    print(f"  • Empirical Delta Optimization       : -{np.mean(delays_standard) - np.mean(delays_adaptive):.2f} steps")
    print(f"  • Non-Parametric Permutation P-Value : {p_val:.4f}")
    
    if p_val < 0.01:
        print("Conclusion: The speed advantage of the Adaptive Floor is highly statistically significant (p < 0.01).")
    else:
        print("Conclusion: Optimization delta cannot rule out stochastic noise bounds.")
    print("=" * 80)
