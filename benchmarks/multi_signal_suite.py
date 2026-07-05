import numpy as np
from benchmarks.continuous_ensemble import ContinuousEnsembleRouter

def generate_composite_gauntlet():
    np.random.seed(42)
    t1 = np.linspace(0, 10, 50)
    phase1 = (t1 * 1.5 + 10.0 + np.random.normal(0, 0.05, 50)).tolist()
    phase2 = ([phase1[-1] + 15.0]*25 + [phase1[-1] + 5.0]*25 + np.random.normal(0, 0.05, 50)).tolist()
    rw = np.cumsum(np.random.normal(0, 0.4, 50)).tolist()
    phase3 = [val + phase2[-1] for val in rw]
    t4 = np.linspace(0, 15, 50)
    phase4 = (np.sin(t4) * 4.0 + phase3[-1] + np.random.normal(0, 0.05, 50)).tolist()
    return phase1 + phase2 + phase3 + phase4

def run_bayesian_trace():
    stream = generate_composite_gauntlet()
    # Configure the adaptive routing engine
    router = ContinuousEnsembleRouter(hazard_rate=0.12, process_sigma=0.5)
    selection_counts = {k: 0 for k in router.models.keys()}
    
    print("=" * 115)
    print("   OMNIGNITION BAYESIAN ROUTER REAL-TIME POSTERIOR PROBABILITY TRACE LOG")
    print("=" * 115)
    
    for i in range(10, len(stream)):
        window = stream[:i]
        target = stream[i]
        pred, weights = router.blend_and_forecast(window)
        active_expert = max(weights, key=weights.get)
        selection_counts[active_expert] += 1
        
        # Monitor exact transitional regime handoff indices
        if i in [25, 49, 51, 74, 76, 110, 135, 160, 185]:
            w_str = ", ".join([f"{k}:{v:.2f}" for k, v in weights.items() if v > 0.01])
            print(f"Step {i:<3} | Value: {target:<6.2f} | Dominant Expert: {active_expert:<12} | Posteriors -> {w_str}")
            
    print("=" * 115)
    print("AGGREGATE SUITE REVALUATION FREQUENCIES:", selection_counts)
    print("=" * 115)

if __name__ == "__main__":
    run_bayesian_trace()
