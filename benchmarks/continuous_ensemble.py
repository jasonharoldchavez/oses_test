import numpy as np
from benchmarks.baselines import PersistenceModel, EWMAModel

class LinearModel:
    def predict(self, history):
        x = np.arange(len(history))
        slope, intercept = np.polyfit(x, history, 1)
        return (slope * len(history)) + intercept

class MeanRevModel:
    def predict(self, history):
        return np.mean(history)

class ContinuousEnsembleRouter:
    def __init__(self):
        self.models = {
            "LINEAR": LinearModel(),
            "MEAN_REV": MeanRevModel(),
            "PERSISTENCE": PersistenceModel(),
            "EWMA": EWMAModel(alpha=0.3)
        }
        
    def blend_and_forecast(self, history):
        preds = {name: mdl.predict(history) for name, mdl in self.models.items()}
        
        if len(history) <= 5:
            w_equal = 1.0 / len(self.models)
            return sum(p * w_equal for p in preds.values()), {n: w_equal for n in self.models}
            
        # 1. Structural Jump Detection
        diffs = np.diff(history)
        latest_jump = abs(history[-1] - history[-2])
        rolling_vol = np.std(diffs) if len(diffs) > 1 else 1.0
        
        # If latest delta exceeds 3.5 standard deviations of historical changes, route immediately to Persistence
        if latest_jump > 3.5 * rolling_vol:
            weights = {n: 0.0 for n in self.models}
            weights["PERSISTENCE"] = 1.0
            return preds["PERSISTENCE"], weights
            
        # 2. Contextual Trend Gating
        trend_score = np.std(history) / (rolling_vol + 1e-5)
        if trend_score > 8.0:
            weights = {n: 0.0 for n in self.models}
            weights["LINEAR"] = 1.0
            return preds["LINEAR"], weights
            
        # 3. Standard Continuous Inverse-Error Blending
        prev_window = history[:-1]
        actual_last = history[-1]
        
        inv_errors = {}
        for name, mdl in self.models.items():
            try:
                err = abs(mdl.predict(prev_window) - actual_last) + 1e-5
                inv_errors[name] = 1.0 / err
            except Exception:
                inv_errors[name] = 1e-5
                
        total_inv = sum(inv_errors.values())
        weights = {name: inv / total_inv for name, inv in inv_errors.items()}
        blended_forecast = sum(preds[name] * weights[name] for name in self.models)
        
        return blended_forecast, weights
