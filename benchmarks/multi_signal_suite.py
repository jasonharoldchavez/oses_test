import numpy as np
from benchmarks.continuous_ensemble import ContinuousEnsembleRouter, LinearModel, MeanRevModel
from benchmarks.baselines import PersistenceModel, EWMAModel, AR1Model

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

def run_diagnostic_trace():
    stream = generate_composite_gauntlet()
    router = ContinuousEnsembleRouter(use_jump_gate=True, use_trend_gate=True)
    
    selection_counts = {k: 0 for k in router.models.keys()}
    gate_activations = {"JUMP_GATE": 0, "TREND_GATE": 0, "HEDGE_BLEND": 0}

    print("=" * 105)
    print("REAL-TIME MOE ROUTING TRACE LOG (SAMPLED KEY REGIME TRANSITIONS)")
    print("=" * 105)
    print(f"Step  | True Value | Active Expert | Routing Mode     | Selected Expert Weight Distribution")
    print("-" * 105)
    
    for i in range(15, len(stream)):
        window = stream[:i]
        target = stream[i]

        pred, weights = router.blend_and_forecast(window)
        active_expert = max(weights, key=weights.get)
        selection_counts[active_expert] += 1
        
        diffs = np.diff(window)
        latest_jump = abs(window[-1] - window[-2])
        rolling_vol = np.std(diffs) if len(diffs) > 1 else 1.0
        
        x_idx = np.arange(len(window))
        corr_matrix = np.corrcoef(x_idx, window)
        trend_strength = abs(corr_matrix[0, 1]) if not np.isnan(corr_matrix[0, 1]) else 0.0
        
        if latest_jump > 4.0 * rolling_vol:
            mode = "JUMP OVERRIDE "
            gate_activations["JUMP_GATE"] += 1
        elif trend_strength > 0.98 and len(window) > 10:
            mode = "TREND OVERRIDE"
            gate_activations["TREND_GATE"] += 1
        else:
            mode = "HEDGE BLEND   "
            gate_activations["HEDGE_BLEND"] += 1
            
        if i in [25, 51, 52, 76, 110, 135, 160, 185]:
            w_str = ", ".join([f"{k}:{v:.2f}" for k, v in weights.items() if v > 0.02])
            print(f"{i:<5} | {target:<10.2f} | {active_expert:<13} | {mode} | {w_str}")
            
    print("=" * 105)
    print("AGGREGATE SUITE DIAGNOSTICS")
    print("=" * 105)
    print("Model Selection Frequencies: ", dict(selection_counts))
    print("Routing Gate Allocations:     ", dict(gate_activations))
    print("=" * 105)

if __name__ == '__main__':
    run_diagnostic_trace()
