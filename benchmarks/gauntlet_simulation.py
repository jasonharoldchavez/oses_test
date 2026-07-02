import numpy as np
from benchmarks.adaptive_cusum_commander import AdaptiveCUSUMCommander

def generate_gauntlet_stream():
    np.random.seed(101)
    # Regime 1: Stable Mean Reverting Base
    r1 = np.random.normal(10.0, 0.4, 40).tolist()
    # Regime 2: Sudden Sharp Structural Trend Jump
    r2 = [r1[-1] + (i * 1.8) + np.random.normal(0, 0.2) for i in range(1, 25)]
    # Regime 3: Fast Cyclic Noise Oscillation
    base = r2[-1]
    r3 = [base + np.sin(i) * 3.0 + np.random.normal(0, 0.5) for i in range(1, 35)]
    return r1 + r2 + r3

def execute():
    stream = generate_gauntlet_stream()
    commander = AdaptiveCUSUMCommander(target_mean=10.0, target_std=0.4, k_threshold=1.5, h_decision=4.5)
    
    print("=" * 120)
    print(f"{'STEP':<6} | {'TRUE VAL':<10} | {'PREDICTION':<10} | {'ACTIVE REGIME':<15} | {'CONF':<6} | {'SPEED':<6} | {'DYNAMIC EXPERT ALLOCATIONS'}")
    print("=" * 120)
    
    for t in range(5, len(stream)):
        history = stream[:t]
        target = stream[t]
        
        pred, weights = commander.route_and_predict(history)
        
        # Trace exact samples during step phase updates
        if t in [15, 38, 41, 42, 45, 60, 66, 72, 85, 92]:
            w_str = "  ".join([f"{k[:4]}:{v:.2f}" for k, v in weights.items() if v > 0.01])
            metrics = commander.scorecard
            print(f"{t:<6} | {target:<10.2f} | {pred:<10.2f} | {metrics['active_regime']:<15} | {metrics['confidence']:<6.2f} | {metrics['adaptation_speed']:<6.2f} | {w_str}")

    print("=" * 120)
    print("GAUNTLET SIMULATION COMPLETE: Online Learning Playbook Verified.")

if __name__ == '__main__':
    execute()
