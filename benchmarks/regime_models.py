import numpy as np

class PersistenceModel:
    def predict(self, history):
        return history[-1] if len(history) > 0 else 0.0

class EWMAModel:
    def __init__(self, alpha=0.3):
        self.alpha = alpha
    def predict(self, history):
        if len(history) == 0: return 0.0
        val = 0.0
        weight = 1.0
        total_w = 0.0
        for x in reversed(history):
            val += x * weight
            total_w += weight
            weight *= (1.0 - self.alpha)
        return val / total_w

class AR1Model:
    def predict(self, history):
        if len(history) < 3:
            return history[-1] if len(history) > 0 else 0.0
        diffs = np.diff(history)
        if np.std(diffs[:-1]) == 0:
            return history[-1]
        r = np.corrcoef(diffs[:-1], diffs[1:]) [0, 1]
        if np.isnan(r): r = 0.0
        return history[-1] + r * (history[-1] - history[-2])

class LinearModel:
    def predict(self, history):
        if len(history) < 3:
            return history[-1] if len(history) > 0 else 0.0
        x = np.arange(len(history))
        slope, intercept = np.polyfit(x, history, 1)
        return (slope * len(history)) + intercept
