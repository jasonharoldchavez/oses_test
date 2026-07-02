import numpy as np
import time
from benchmarks.adaptive_cusum_commander import AdaptiveCUSUMCommander
from benchmarks.regime_models import PersistenceModel, EWMAModel, AR1Model, LinearModel

def run_comprehensive_benchmark(num_simulations=500, series_length=100):
    print("=" * 125)
    print(f"LAUNCHING RIGOROUS COMPARATIVE BENCHMARK SUITE ({num_simulations} ITERATIONS)")
    print("=" * 125)

    methods = ["Persistence", "EWMA", "AR(1)", "Linear", "Static Ensemble", "CUSUM Commander"]
    metrics = {m: {"mae": [], "rmse": [], "max_err": []} for m in methods}
    detection_delays = []
    
    baselines = {
        "Persistence": PersistenceModel(),
        "EWMA": EWMAModel(alpha=0.4),
        "AR(1)": AR1Model(),
        "Linear": LinearModel()
    }

    for sim in range(num_simulations):
        np.random.seed(42 + sim)
        
        regime_change_point = 40
        r1 = np.random.normal(10.0, 0.4, regime_change_point).tolist()
        r2 = [r1[-1] + (i * 1.5) + np.random.normal(0, 0.3) for i in range(1, series_length - regime_change_point + 1)]
        stream = r1 + r2
        
        commander = AdaptiveCUSUMCommander(target_mean=10.0, target_std=0.4, k_threshold=1.5, h_decision=4.5)
        
        sim_errors = {m: [] for m in methods}
        detected_at = None
        
        for t in range(5, len(stream)):
            history = stream[:t]
            target = stream[t]
            
            preds = {}
            for name, model in baselines.items():
                preds[name] = model.predict(history)
                sim_errors[name].append(abs(preds[name] - target))
                
            preds["Static Ensemble"] = np.mean([preds[n] for n in baselines])
            sim_errors["Static Ensemble"].append(abs(preds["Static Ensemble"] - target))
            
            preds["CUSUM Commander"], _ = commander.route_and_predict(history)
            sim_errors["CUSUM Commander"].append(abs(preds["CUSUM Commander"] - target))
            
            if t >= regime_change_point and detected_at is None:
                if commander.scorecard["active_regime"] in ["BREAKOUT_UP", "BREAKOUT_DOWN"]:
                    detected_at = t

        for m in methods:
            errs = np.array(sim_errors[m])
            metrics[m]["mae"].append(np.mean(errs))
            metrics[m]["rmse"].append(np.sqrt(np.mean(errs**2)))
            metrics[m]["max_err"].append(np.max(errs))
            
        if detected_at is not None:
            detection_delays.append(detected_at - regime_change_point)
        else:
            detection_delays.append(series_length - regime_change_point)

    mean_maes = {m: np.mean(metrics[m]["mae"]) for m in methods}
    commander_mae = mean_maes["CUSUM Commander"]

    print(f"{'METHOD':<20} | {'MAE (Mean ± STD)':<22} | {'RMSE':<10} | {'MAX ERROR':<12} | {'VS COMMANDER':<14} | {'DETECTION DELAY':<15}")
    print("-" * 125)
    
    for m in methods:
        mae_m = mean_maes[m]
        mae_s = np.std(metrics[m]["mae"])
        rmse_m = np.mean(metrics[m]["rmse"])
        max_m = np.mean(metrics[m]["max_err"])
        
        if m == "CUSUM Commander":
            vs_str = "Baseline"
            delay_str = f"{np.mean(detection_delays):.2f} steps"
        else:
            pct_diff = ((commander_mae - mae_m) / mae_m) * 100.0
            vs_str = f"{pct_diff:+.1f}%"
            delay_str = "N/A"
            
        print(f"{m:<20} | {mae_m:<7.4f} ± {mae_s:<10.4f} | {rmse_m:<10.4f} | {max_m:<12.4f} | {vs_str:<14} | {delay_str:<15}")
        
    print("=" * 125)
    print("VALIDATION MATRIX GENERATION COMPLETE. READY FOR BENCHMARK CHOP REPORT.")

if __name__ == '__main__':
    run_comprehensive_benchmark()
