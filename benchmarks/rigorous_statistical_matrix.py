import numpy as np
from streaming_guardian.detectors.framework_core import AdaptiveCUSUMDetector
from streaming_guardian.detectors.models import CUSUMDecisionEngine
from scenarios.generators import DynamicSensor

def compute_cliffs_delta(group_a, group_b):
    """
    Computes Cliff's Delta effect size for non-parametric data.
    Quantifies how often values in group_a are lower than group_b.
    Returns value in [-1, 1], where positive implies group_a has lower delays.
    """
    mat = np.expand_dims(group_a, axis=1) < np.expand_dims(group_b, axis=0)
    mat_rev = np.expand_dims(group_a, axis=1) > np.expand_dims(group_b, axis=0)
    return (np.sum(mat) - np.sum(mat_rev)) / (len(group_a) * len(group_b))

def bootstrap_mean_difference_ci(group_a, group_b, num_bootstraps=2000, alpha=0.05):
    """
    Generates a 95% confidence interval for the mean difference (Mean(B) - Mean(A))
    using percentile bootstrapping.
    """
    diffs = []
    arr_a = np.array(group_a)
    arr_b = np.array(group_b)
    
    for _ in range(num_bootstraps):
        boot_a = np.random.choice(arr_a, size=len(arr_a), replace=True)
        boot_b = np.random.choice(arr_b, size=len(arr_b), replace=True)
        diffs.append(np.mean(boot_b) - np.mean(boot_a))
        
    low_pct = 100 * (alpha / 2)
    high_pct = 100 * (1.0 - alpha / 2)
    return np.percentile(diffs, low_pct), np.percentile(diffs, high_pct)

def run_permutation_test(group_a, group_b, num_resamples=3000):
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
    print("=" * 95)
    print("         HIGH-FIDELITY MATRIX: MULTI-SCENARIO NON-PARAMETRIC VALIDATION ENGINE")
    print("=" * 95)
    
    np.random.seed(42)
    num_trials = 200
    ground_truth_step = 50
    
    scenarios = [
        {"name": "Standard Creeping Drift ", "scale": 0.4, "drift": 0.10, "type": "gradual"},
        {"name": "High Noise / Slow Leak   ", "scale": 0.8, "drift": 0.05, "type": "gradual"},
        {"name": "Extreme Volatility Shock ", "scale": 1.2, "drift": 2.0, "type": "step"}
    ]
    
    for sc in scenarios:
        print(f"\n>>> EVALUATING ENVIRONMENT REGIME: {sc['name']}")
        print(f"    Params -> Volatility (Sigma): {sc['scale']}, Drift Velocity: {sc['drift']}")
        print("-" * 95)
        
        delays_standard = []
        delays_adaptive = []
        
        for _ in range(num_trials):
            sensor = DynamicSensor(scale=sc["scale"], drift=sc["drift"], drift_type=sc["type"])
            std_engine = CUSUMDecisionEngine(threshold_h=4.605, noise_floor=10.8)
            adp_engine = AdaptiveCUSUMDetector(burn_in=30)
            
            alarm_std, alarm_adp = -1, -1
            
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
            
        # Core Statistical Reductions
        mean_std = np.mean(delays_standard) if delays_standard else float('nan')
        mean_adp = np.mean(delays_adaptive) if delays_adaptive else float('nan')
        delta_opt = mean_std - mean_adp
        
        p_val = run_permutation_test(delays_adaptive, delays_standard)
        cliffs_d = compute_cliffs_delta(delays_adaptive, delays_standard)
        ci_low, ci_high = bootstrap_mean_difference_ci(delays_adaptive, delays_standard)
        
        # Interpret effect size magnitude
        abs_d = abs(cliffs_d)
        effect_magnitude = "Negligible"
        if abs_d >= 0.474: effect_magnitude = "Large"
        elif abs_d >= 0.330: effect_magnitude = "Medium"
        elif abs_d >= 0.147: effect_magnitude = "Small"

        print(f"  • Standard CUSUM Mean Delay   : {mean_std:.2f} steps")
        print(f"  • Self-Correcting CUSUM Mean  : {mean_adp:.2f} steps")
        print(f"  • Empirical Delay Reduction   : -{delta_opt:.2f} steps")
        print(f"  • 95% Bootstrap CI on Delta   : [{ci_low:.3f}, {ci_high:.3f}] steps absolute")
        print(f"  • Cliff's Delta Effect Size  : {cliffs_d:+.4f} ({effect_magnitude} Dominance Bound)")
        print(f"  • Permutation Resample P-Val  : {p_val:.4f}")
        
    print("=" * 95)
