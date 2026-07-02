import numpy as np
from benchmarks.baselines import PersistenceModel, EWMAModel, AR1Model

class LinearModel:
    def predict(self, history):
        if len(history) < 2:
            return history[-1] if len(history) == 1 else 0.0
        x = np.arange(len(history))
        slope, intercept = np.polyfit(x, history, 1)
        return (slope * len(history)) + intercept

class MeanRevModel:
    def predict(self, history):
        return np.mean(history) if len(history) > 0 else 0.0

class ContinuousEnsembleRouter:
    def __init__(self, learning_rate=0.4, gamma=0.85, use_jump_gate=True, use_trend_gate=True):
        self.models = {
            "LINEAR": LinearModel(),
            "MEAN_REV": MeanRevModel(),
            "PERSISTENCE": PersistenceModel(),
            "EWMA": EWMAModel(alpha=0.3),
            "AR1": AR1Model()
        }
        self.learning_rate = learning_rate
        self.gamma = gamma
        self.use_jump_gate = use_jump_gate
        self.use_trend_gate = use_trend_gate
        self.cumulative_losses = {name: 0.0 for name in self.models}

    def blend_and_forecast(self, history):
        preds = {name: mdl.predict(history) for name, mdl in self.models.items()}
        
        if len(history) <= 5:
            w_equal = 1.0 / len(self.models)
            return sum(p * w_equal for p in preds.values()), {n: w_equal for n in self.models}

        diffs = np.diff(history)
        latest_jump = abs(history[-1] - history[-2])
        rolling_vol = np.std(diffs) if len(diffs) > 1 else 1.0

        x_idx = np.arange(len(history))
        with np.errstate(divide="ignore", invalid="ignore"):
            corr_matrix = np.corrcoef(x_idx, history)
            trend_strength = abs(corr_matrix[0, 1]) if not np.isnan(corr_matrix[0, 1]) else 0.0

        if self.use_jump_gate and latest_jump > 4.0 * rolling_vol:
            weights = {n: 0.0 for n in self.models}
            weights["PERSISTENCE"] = 1.0
            return preds["PERSISTENCE"], weights

        if self.use_trend_gate and trend_strength > 0.98 and len(history) > 10:
            weights = {n: 0.0 for n in self.models}
            weights["LINEAR"] = 1.0
            return preds["LINEAR"], weights

        prev_window = history[:-1]
        actual_last = history[-1]

        for name, mdl in self.models.items():
            try:
                instant_loss = abs(mdl.predict(prev_window) - actual_last)
                self.cumulative_losses[name] = (self.gamma * self.cumulative_losses[name]) + instant_loss
            except Exception:
                self.cumulative_losses[name] = (self.gamma * self.cumulative_losses[name]) + 1.0

        min_loss = min(self.cumulative_losses.values())
        raw_weights = {}
        for name in self.models:
            scaled_loss = self.cumulative_losses[name] - min_loss
            raw_weights[name] = np.exp(-self.learning_rate * scaled_loss)

        total_weight = sum(raw_weights.values()) + 1e-11
        normalized_weights = {k: v / total_weight for k, v in raw_weights.items()}
        
        blended_pred = sum(preds[name] * normalized_weights[name] for name in self.models)
        return blended_pred, normalized_weights
